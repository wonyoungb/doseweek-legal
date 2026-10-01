#!/usr/bin/env python3
"""Stage the 1.0.6 legal integration with the existing page renderers.

The output is a local review directory, never the public checkout. Canonical sources/pages
remain historical. No date, credential, remote request or deployed behavior is inferred.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
import json
import shutil
from pathlib import Path
from urllib.parse import urlencode
import account_sync_candidate
import legal_release
import locale_pages
import render_ios
import render_android
import render_terms

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('privacy/', 'support/', 'android/privacy/', 'android/support/', 'terms/', 'account/delete/')

def sections(entry):
    return {s['id']: s for s in entry['sections']}

def integrated_sources(candidate=None):
    c = candidate or account_sync_candidate.load()
    ios = json.loads((ROOT / 'docs/ios-content.json').read_text())
    android = json.loads((ROOT / 'docs/android-content.candidate.json').read_text())
    terms = json.loads((ROOT / 'docs/terms-content.json').read_text())
    # Validate original contracts before altering the bounded fields below.
    render_ios.validate(ios)
    render_android.validate_catalog(android)
    render_terms.validate(terms, ios)
    originals = copy.deepcopy((ios, android, terms))
    ios['bundleVersion'] = android['versionName'] = c['plannedVersion']
    ios['effectiveDate'] = android['effectiveDate'] = terms['effectiveDate'] = None
    for loc, text in c['locales'].items():
        i, a, t = ios['locales'][loc], android['locales'][loc], terms['locales'][loc]
        ip, ap, tp = sections(i['privacy']), sections(a['privacy']), sections(t)
        join = lambda *keys: '\n\n'.join(text[k] for k in keys)
        i['privacy']['intro'] = text['releaseStatus'] + '\n\n' + i['privacy']['intro']
        i['privacy']['effectiveDate'] = text['releaseStatus']
        i['support']['labels']['lead'] = join('releaseStatus', 'account')
        ip['storage']['paragraphs'][0] = join('releaseStatus', 'account', 'sync', 'analytics', 'notice')
        ip['backups']['paragraphs'][0] = text['manualBackupScope'] + '\n\n' + ip['backups']['paragraphs'][0] + '\n\n' + text['sync']
        ip['deletion']['paragraphs'][0] += '\n\n' + join('retention', 'webDeletion')
        purchase = ip['purchases']['paragraphs'][0].split('\n\n')
        assert len(purchase) == 7, (loc, 'ios purchase paragraph boundary changed')
        placeholders = [x for x in legal_release.RELEASE_PLACEHOLDERS if x in purchase[1]]
        assert len(placeholders) == 2, (loc, 'purchase placeholders')
        # The 1.0.6 purchase text describes the account/sync server, so its location, operator,
        # processors and retention replace the two "listed before release" placeholders.
        purchase[1] = join('account', 'sync', 'processors')
        # Legacy file backup exclusions stay scoped to that file format; account settings
        # sync is a distinct path. Keep the complete existing offline/cache/tool behavior.
        purchase[3] = text['manualBackupScope'] + '\n\n' + purchase[3] + '\n\n' + text['sync']
        purchase[5] = join('legacyRights', 'priorBuyerClaimPrivacy')
        ip['purchases']['paragraphs'][0] = '\n\n'.join(purchase)
        for group, key in [('released', 'backup'), ('secondRelease', 'backup')]:
            i['support'][group][key]['answers'][0] = text['manualBackupScope'] + '\n\n' + i['support'][group][key]['answers'][0]
            i['support'][group][key]['answers'][-1] += '\n\n' + text['sync']
        i['support']['released']['deletion']['answers'][-1] += '\n\n' + join('retention', 'webDeletion')
        i['support']['plus']['features']['answers'][0] += '\n\n' + join('account', 'sync')
        i['support']['plus']['manage']['answers'][-1] += '\n\n' + join('account', 'retention')
        i['support']['plus']['earlier']['answers'] = [join('legacyRights', 'priorBuyerClaimHelp'), text['releaseStatus']]
        a['privacy']['scope'] = text['releaseStatus'] + '\n\n' + a['privacy']['scope'].replace('1.0.5', '1.0.6')
        a['home']['featureBadges'][1] = text['account']
        ap['no-collection']['paragraphs'][0] = ap['no-collection']['paragraphs'][0].replace('1.0.5', '1.0.6')
        a['support']['intro'] = join('releaseStatus', 'account', 'analytics')
        ap['scope']['paragraphs'][1] = join('account', 'sync', 'notice')
        a['home']['versionScope'] = a['home']['versionScope'].replace('1.0.5', '1.0.6')
        for item in a['support']['faq']:
            if item['id'] in ('ai-health', 'notifications'):
                item['answers'] = [x.replace('1.0.5', '1.0.6') for x in item['answers']]
        # Preserve the actual analytics/transfer paragraphs after replacing only their
        # previous local-only scope paragraph; analytics remains independent.
        analytics = ap['no-collection']['paragraphs'][1].split('\n\n')
        ap['no-collection']['paragraphs'][1] = join('releaseStatus', 'account', 'sync', 'analytics', 'notice') + '\n\n' + '\n\n'.join(analytics[1:])
        ap['no-collection']['items'][0] = text['sync']
        ap['no-collection']['items'][1] = text['account']
        for index in (0, 2):
            ap['backup']['paragraphs'][index] = text['manualBackupScope'] + '\n\n' + ap['backup']['paragraphs'][index]
        ap['backup']['paragraphs'][-1] += '\n\n' + text['sync']
        ap['purchases']['paragraphs'][1] = join('account', 'sync')
        ap['purchases']['paragraphs'][2] = join('sync', 'processors')
        ap['purchases']['paragraphs'][4] = text['manualBackupScope'] + '\n\n' + ap['purchases']['paragraphs'][4] + '\n\n' + text['sync']
        faq = {f['id']: f for f in a['support']['faq']}
        ap['purchases']['paragraphs'][5] = '\n\n'.join(faq['plus-cancel']['answers']) + '\n\n' + join('legacyRights', 'priorBuyerClaimPrivacy')
        ap['retention']['paragraphs'][0] = join('retention', 'webDeletion')
        ap['security']['paragraphs'][0] = text['sync']
        faq['accounts']['answers'] = [join('releaseStatus', 'account', 'sync', 'analytics', 'notice')]
        faq['backup']['answers'][0] = text['manualBackupScope'] + '\n\n' + faq['backup']['answers'][0]
        faq['backup']['answers'][1] += '\n\n' + text['sync']
        faq['deletion']['answers'][0] += '\n\n' + join('retention', 'webDeletion')
        faq['recovery']['answers'] = [text['sync']]
        faq['plus-features']['answers'][0] += '\n\n' + join('account', 'sync')
        faq['plus-restore']['answers'][1] = join('account', 'sync')
        faq['plus-earlier']['answers'] = [join('legacyRights', 'priorBuyerClaimHelp'), text['releaseStatus']]
        t['intro'] = text['releaseStatus'] + '\n\n' + t['intro']
        tp['free-plus']['paragraphs'][1] = text['legacyRights']
        tp['free-plus']['paragraphs'][0] += '\n\n' + text['account']
        tp['billing']['paragraphs'][1] = join('account', 'retention')
        tp['records']['paragraphs'][0] = join('sync', 'retention', 'webDeletion', 'notice', 'analytics')
    render_ios.validate(ios)
    render_android.validate_catalog(android)
    render_terms.validate(terms, ios)
    for loc in c['localeOrder']:
        # Medical and source attributions must remain verbatim; analytics consent transfer
        # and all reward-pass disclosures remain in their original sections.
        assert ios['locales'][loc]['privacy']['medicalDisclaimer'] == originals[0]['locales'][loc]['privacy']['medicalDisclaimer']
        assert sections(ios['locales'][loc]['privacy'])['tracking'] == sections(originals[0]['locales'][loc]['privacy'])['tracking']
        assert sections(android['locales'][loc]['privacy'])['ads'] == sections(originals[1]['locales'][loc]['privacy'])['ads']
        assert sections(terms['locales'][loc])['ad-free-pass'] == sections(originals[2]['locales'][loc])['ad-free-pass']
    return {'ios-content.json': ios, 'android-content.candidate.json': android, 'terms-content.json': terms}

def deletion_panel(c, loc):
    text = c['locales'][loc]
    title = html.escape(text['deletionTitle'])
    mailto = 'mailto:' + c['deletionRequest']['supportEmail'] + '?' + urlencode({'subject': 'DoseWeek account deletion request'})
    paragraphs = ''.join('<p>' + html.escape(text[k]) + '</p>' for k in ('releaseStatus', 'webDeletion', 'retention', 'account', 'analytics'))
    return f'<article id="{loc}" class="language-panel" lang="{loc}" dir="{locale_pages.direction(loc)}" data-language="{loc}" data-document-title="{title} — DoseWeek" aria-labelledby="{loc}-content"><header class="hero"><h1 id="{loc}-content">{title}</h1></header><div class="policy-card">{paragraphs}<a class="button primary" href="{html.escape(mailto, quote=True)}">{html.escape(text["requestLabel"])}</a><p><a href="{html.escape(mailto, quote=True)}">wonyoung@wonyoungchoi.dev</a></p></div></article>'

def rendered_pages(sources, candidate=None):
    c = candidate or account_sync_candidate.load()
    i, a, t = (sources[k] for k in ('ios-content.json', 'android-content.candidate.json', 'terms-content.json'))
    pages = {render_ios.PAGE_PATH: render_ios.rendered(i), render_ios.SUPPORT_PATH: render_ios.rendered_support(i), **render_ios.rendered_locale_pages(i)}
    pages.update({p: s for p,s in {**render_android.rendered_pages(a), **render_android.rendered_locale_pages(a)}.items() if p.relative_to(ROOT).as_posix().endswith(('privacy/index.html','support/index.html'))})
    pages.update(render_terms.rendered_pages(t, i))
    for path, markup in list(pages.items()):
        relative = path.relative_to(ROOT)
        locale = relative.parts[0] if relative.parts[0] in c['localeOrder'] else None
        prefix = '../' * (len(relative.parts)-1)
        def link(loc):
            return f'<a class="page-link" href="{prefix}account/delete/#{loc}">{html.escape(c["locales"][loc]["deletionTitle"])}</a>'
        if locale:
            markup = markup.replace('</article>', link(locale) + '</article>')
        else:
            for loc in c['localeOrder']:
                # Each language panel has exactly one closing article; attach the matching link.
                import re
                pattern = rf'(<article id="{loc}".*?)(</article>)'
                markup, count = re.subn(pattern, lambda m: m[1]+link(loc)+m[2], markup, count=1, flags=re.S)
                assert count == 1, (relative, loc)
        pages[path] = markup.replace('<head>', '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    # Register the new route only inside this staging process, leaving the public sitemap
    # and routes untouched until publication is separately authorized.
    old_routes = locale_pages.ROUTES
    locale_pages.ROUTES = (*old_routes, 'account/delete/')
    try:
        names = {loc: entry['languageName'] for loc,entry in i['locales'].items()}
        panels = '\n'.join(deletion_panel(c,loc) for loc in c['localeOrder'])
        shell = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>DoseWeek account deletion request</title><link rel="canonical" href="{c["plannedDeletionPage"]}">{locale_pages.alternate_links("account/delete/")}<link rel="stylesheet" href="../../{__import__("site_assets").stylesheet_path()}"><script src="../../{__import__("site_assets").script_path("language.js")}" defer></script></head><body><nav>'+''.join(f'<a class="language-link" data-language-link="{loc}" href="#{loc}">{html.escape(names[loc])}</a> ' for loc in c['localeOrder'])+f'</nav><main id="main" class="site-shell"><div class="language-stack">{panels}</div></main></body></html>'
        pages[ROOT/'account/delete/index.html'] = shell
        for loc in c['localeOrder']:
            pages[locale_pages.page_path('account/delete/',loc)] = locale_pages.locale_page(route='account/delete/', locale=loc, names=names, description=c['locales'][loc]['deletionTitle'], panel=deletion_panel(c,loc), icon='assets/app-icon.png', social_image=render_ios.SOCIAL_IMAGE, image_alt='DoseWeek app icon', brand_href='../../', brand_aria='DoseWeek', brand_label='DoseWeek', skip_label=i['locales'][loc]['common']['skipToContent'], skip_target=f'{loc}-content', footer='<footer>DoseWeek · 1.0.6 · unpublished</footer>', body_attributes=' data-page="account-delete"').replace('<head>', '<head>\n<meta name="robots" content="noindex,nofollow">',1)
    finally:
        locale_pages.ROUTES = old_routes
    assert len(pages) == 108
    return pages

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True, help='Local review directory outside this public checkout')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output != ROOT and not output.is_relative_to(ROOT), 'Never render staged pages into the public checkout'
    sources = integrated_sources()
    pages = rendered_pages(sources)
    output.mkdir(parents=True,exist_ok=True)
    # Supporting static pages/assets use the preserved baseline, not a new full-site render.
    for p in sorted(ROOT.rglob('index.html')):
        if '.git' not in p.parts:
            dest=output/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    shutil.copytree(ROOT/'assets',output/'assets',dirs_exist_ok=True)
    for name, source in sources.items():
        dest=output/'sources'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
    for path, markup in pages.items():
        dest=output/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(markup)
    receipt={'status':'unpublished-local-candidate','version':'1.0.6','effectiveDate':None,'routes':list(ROUTES),'locales':list(account_sync_candidate.LOCALES),'affectedPages':{p.relative_to(ROOT).as_posix():hashlib.sha256(s.encode()).hexdigest() for p,s in sorted(pages.items())},'sources':{n:hashlib.sha256((output/'sources'/n).read_bytes()).hexdigest() for n in sources},'runtime':'no-network-no-device'}
    (output/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'OK: staged {len(pages)} pages, 6 routes x 18 (hash + 17 locales), with null effective date; {output}')

if __name__=='__main__':main()
