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
import re
import shutil
from pathlib import Path
from urllib.parse import urlencode
import account_sync_candidate
import legal_release
import locale_pages
import render_ios
import render_android
import render_terms
import render_us_health

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('privacy/', 'support/', 'android/privacy/', 'android/support/', 'terms/', 'account/delete/', 'us-health/')
CJK = ('ja', 'zh-Hans', 'zh-Hant')

# Keep cross-store purchase verification/deletion disclosures in iOS copy using neutral
# store names. Context-specific substitutions preserve grammar and every retention bound.
IOS_RETENTION_STORE_LABELS = {'ko': [{'old': 'Google Play', 'new': '다른 지원 스토어'}],
 'en': [{'old': 'Google Play', 'new': 'another supported store'}],
 'ja': [{'old': 'Google Play', 'new': '対応する他のストア'}],
 'de': [{'old': 'bei Google Play', 'new': 'bei einem anderen unterstützten Store'},
        {'old': 'über Google Play', 'new': 'über einen anderen unterstützten Store'}],
 'fr': [{'old': 'de Google Play', 'new': 'd’un autre store pris en charge'},
        {'old': 'sur Google Play', 'new': 'sur un autre store pris en charge'}],
 'es': [{'old': 'Google Play', 'new': 'otra tienda compatible'}],
 'it': [{'old': 'Google Play', 'new': 'un altro store supportato'}],
 'nl': [{'old': 'Google Play', 'new': 'een andere ondersteunde store'}],
 'pt-PT': [{'old': 'do Google Play', 'new': 'de outra loja compatível'},
           {'old': 'no Google Play', 'new': 'em outra loja compatível'}],
 'pl': [{'old': 'Google Play', 'new': 'innym obsługiwanym sklepie'}],
 'sv': [{'old': 'Google Play', 'new': 'en annan stödd butik'}],
 'hi': [{'old': 'Google Play', 'new': 'किसी अन्य समर्थित स्टोर'}],
 'pt-BR': [{'old': 'no Google Play', 'new': 'em outra loja compatível'},
           {'old': 'o Google Play', 'new': 'outra loja compatível'}],
 'ar': [{'old': 'Google Play', 'new': 'متجر آخر مدعوم'}],
 'zh-Hans': [{'old': 'Google Play', 'new': '其他受支持的商店'}],
 'zh-Hant': [{'old': 'Google Play', 'new': '其他支援的商店'}],
 'tr': [{'old': "Google Play'den", 'new': 'desteklenen başka bir mağazadan'}]}

def sections(entry):
    return {s['id']: s for s in entry['sections']}

# The 1.0.5 "earlier" answer opens with the free list and the "nothing is deleted or moved into
# Plus" promise, then closes with the one-time-notice sentence. ko, ja and tr state the promise
# as its own sentence; the other locales join it with ';' or '，'. With Android OS Drive Auto
# Backup now Plus-only, every sentence but the closing notice is replaced on both platforms.
EARLIER_CLAIMS = slice(0, -1)

def replace_backup_sentence(paragraph, index, replacement, locale):
    """Replace a legacy blanket claim (one sentence index or a slice of sentences), preserving
    the other help sentences."""
    parts = [p.strip() for p in re.split(r'(?<=[。।])|(?<=\.)\s+', paragraph) if p.strip()]
    if isinstance(index, slice):
        assert parts[index], (locale, 'legacy claim sentences changed')
        parts[index] = [replacement]
    else:
        parts[index] = replacement
    return ('' if locale in CJK else ' ').join(parts)

def integrated_sources(candidate=None):
    c = candidate or account_sync_candidate.load()
    ios = json.loads((ROOT / 'docs/ios-content.json').read_text())
    android = json.loads((ROOT / 'docs/android-content.candidate.json').read_text())
    terms = json.loads((ROOT / 'docs/terms-content.json').read_text())
    us_health = json.loads((ROOT / 'docs/us-health-content.json').read_text())
    # Validate original contracts before altering the bounded fields below.
    render_ios.validate(ios)
    render_android.validate_catalog(android)
    render_terms.validate(terms, ios)
    originals = copy.deepcopy((ios, android, terms))
    ios['bundleVersion'] = android['versionName'] = c['plannedVersion']
    ios['effectiveDate'] = android['effectiveDate'] = terms['effectiveDate'] = None
    us_health['effectiveDate'] = None
    for loc, text in c['locales'].items():
        us_health['locales'][loc]['intro'] = text['releaseStatus'] + '\n\n' + us_health['locales'][loc]['intro']
        i, a, t = ios['locales'][loc], android['locales'][loc], terms['locales'][loc]
        backup_guide = i['support']['guide']['steps'][5]['body']
        ip, ap, tp = sections(i['privacy']), sections(a['privacy']), sections(t)
        join = lambda *keys: '\n\n'.join(text[k] for k in keys)
        ios_retention = text['retention']
        for label in IOS_RETENTION_STORE_LABELS[loc]:
            assert label['old'] in ios_retention, (loc, 'shared store wording changed')
            ios_retention = ios_retention.replace(label['old'], label['new'])
        assert 'Google Play' not in ios_retention, loc
        assert 'Google Drive' not in ios_retention, loc
        join_ios = lambda *keys: '\n\n'.join(ios_retention if k == 'retention' else text[k]
                                             for k in keys)
        i['privacy']['intro'] = text['releaseStatus'] + '\n\n' + i['privacy']['intro']
        i['privacy']['effectiveDate'] = text['releaseStatus']
        i['support']['labels']['lead'] = join('releaseStatus', 'account')
        ip['storage']['paragraphs'][0] = join('releaseStatus', 'account', 'sync', 'healthConsent', 'analytics', 'notice')
        # Imported Apple Health / Health Connect observations are part of the sync graph (server
        # PROTOCOL.md "Snapshot contents"): both health paragraphs say so instead of "not sent".
        ip['health']['paragraphs'][0] += ('' if loc in CJK else ' ') + text['healthSync']
        health_connect = ap['no-collection']['paragraphs'][2]
        denial = account_sync_candidate.HEALTH_CONNECT_DENIALS[loc]
        assert health_connect.count(denial) == 1, (loc, 'Health Connect paragraph changed')
        ap['no-collection']['paragraphs'][2] = health_connect.replace(denial, text['healthSync'])
        # Round 3: the live 1.0.5 text says the developer receives no records or meal data. With
        # account sync these reach the server end-to-end encrypted, so the staged text qualifies
        # each denial with the candidate's recordsSync / mealsSync (staged_disclosure_errors).
        def qualify(container, key, denial, replacement):
            assert container[key].count(denial) == 1, (loc, key, 'denial changed')
            container[key] = container[key].replace(denial, replacement)
        qualify(i['support']['released']['storage']['answers'], 0,
                account_sync_candidate.RECORD_DENIALS[loc], text['recordsSync'])
        qualify(ip['meals']['paragraphs'], 0, account_sync_candidate.MEAL_DENIALS[loc], text['mealsSync'])
        qualify(ip['next-release']['paragraphs'], 1, account_sync_candidate.MEAL_DENIALS[loc], text['mealsSync'])
        qualify(ap['next-release']['paragraphs'], 1, account_sync_candidate.MEAL_DENIALS[loc], text['mealsSync'])
        ip['backups']['paragraphs'][0] = text['manualBackupScope'] + '\n\n' + ip['backups']['paragraphs'][0] + '\n\n' + join('automaticBackup', 'iosAppDataBackup', 'sync', 'serverBackup')
        ip['deletion']['paragraphs'][0] += '\n\n' + join_ios('retention', 'webDeletion')
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
        purchase[5] = text['legacyRights']
        ip['purchases']['paragraphs'][0] = '\n\n'.join(purchase)
        for group, key in [('released', 'backup'), ('secondRelease', 'backup')]:
            i['support'][group][key]['answers'][0] = text['manualBackupScope'] + '\n\n' + i['support'][group][key]['answers'][0]
            i['support'][group][key]['answers'][-1] += '\n\n' + join('automaticBackup', 'iosAppDataBackup', 'sync')
        i['support']['guide']['steps'][5]['body'] = backup_guide + '\n\n' + join('automaticBackup', 'iosAppDataBackup')
        i['support']['released']['deletion']['answers'][-1] += '\n\n' + join_ios('retention', 'webDeletion')
        i['support']['plus']['features']['answers'][0] += '\n\n' + join('account', 'automaticBackup', 'iosAppDataBackup', 'sync')
        i['support']['plus']['manage']['answers'][-1] += '\n\n' + join_ios('account', 'retention')
        i['support']['plus']['earlier']['answers'][0] = text['legacyRights']
        for key, index, sentence in [('free', 0, -1), ('features', 1, 0), ('earlier', 1, EARLIER_CLAIMS)]:
            answers = i['support']['plus'][key]['answers']
            answers[index] = replace_backup_sentence(answers[index], sentence, text['freeFeatures'], loc)
        a['privacy']['scope'] = text['releaseStatus'] + '\n\n' + a['privacy']['scope'].replace('1.0.5', '1.0.6')
        a['home']['featureBadges'][1] = text['account']
        ap['no-collection']['paragraphs'][0] = ap['no-collection']['paragraphs'][0].replace('1.0.5', '1.0.6')
        a['support']['intro'] = join('releaseStatus', 'account', 'analytics')
        ap['scope']['paragraphs'][1] = join('account', 'sync', 'healthConsent', 'notice')
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
        # The custom app-managed Drive path belongs to the retained 1.0.5 source. The 1.0.6
        # automatic paths are E2EE server sync and Android OS Auto Backup, with distinct keys.
        # The app-managed path still ships in apps/google release/1.0.6; publication stays
        # blocked until it is removed or disclosed (serverReadiness.appManagedDriveBackupDecided).
        ap['backup']['paragraphs'][0] = join('manualBackupScope', 'androidManualFileBackup')
        ap['backup']['paragraphs'][2] = text['androidManualFileSecurity']
        ap['backup']['paragraphs'][4:] = [text['automaticBackup'], text['androidSystemBackup'], join('sync', 'serverBackup')]
        a['support']['guide']['steps'][5]['body'] = backup_guide + '\n\n' + join('automaticBackup', 'androidSystemBackup')
        ap['purchases']['paragraphs'][1] = join('account', 'sync')
        ap['purchases']['paragraphs'][2] = join('sync', 'processors')
        if c.get('serverReadiness', {}).get('verifierHostDecided') is not True:
            # The standalone Play verifier's host is undecided: keep the registered pending
            # sentence (check_site.py --release refuses it) instead of dropping the location.
            ap['purchases']['paragraphs'][2] += '\n\n' + legal_release.PENDING_VERIFIER_LOCATION[loc]
        ap['purchases']['paragraphs'][4] = text['manualBackupScope'] + '\n\n' + ap['purchases']['paragraphs'][4] + '\n\n' + text['sync']
        faq = {f['id']: f for f in a['support']['faq']}
        ap['purchases']['paragraphs'][5] = '\n\n'.join(faq['plus-cancel']['answers']) + '\n\n' + text['legacyRights']
        ap['retention']['paragraphs'][0] = join('retention', 'webDeletion')
        ap['security']['paragraphs'][0] = text['sync']
        faq['accounts']['answers'] = [join('releaseStatus', 'account', 'sync', 'analytics', 'notice')]
        faq['backup']['answers'][0] = join('manualBackupScope', 'androidManualFileFaq')
        faq['backup']['answers'][1] = join('androidManualFileDestination', 'automaticBackup', 'androidSystemBackup', 'sync')
        faq['storage']['answers'][0] = join('recordsSync', 'automaticBackup', 'androidSystemBackup')
        faq['deletion']['answers'][0] += '\n\n' + join('retention', 'webDeletion')
        faq['recovery']['answers'] = [text['sync']]
        faq['plus-features']['answers'][0] += '\n\n' + join('account', 'automaticBackup', 'androidSystemBackup', 'sync')
        faq['plus-restore']['answers'][1] = join('account', 'sync')
        faq['plus-earlier']['answers'][0] = text['legacyRights']
        for key, index, sentence in [('plus-free', 0, -1), ('plus-features', 1, 0),
                                    ('plus-earlier', 1, EARLIER_CLAIMS)]:
            answers = faq[key]['answers']
            answers[index] = replace_backup_sentence(answers[index], sentence, text['androidFreeFeatures'], loc)
        faq['plus-earlier']['answers'][1] += '\n\n' + text['androidSystemBackup']
        t['intro'] = text['releaseStatus'] + '\n\n' + t['intro']
        tp['free-plus']['paragraphs'][1] = text['legacyRights']
        tp['free-plus']['paragraphs'][0] += '\n\n' + join('account', 'automaticBackup')
        # Billing rights remain canonical: account/retention describes a different
        # subject and must never replace refund, conversion or price-change clauses.
        tp['billing']['paragraphs'][1] += '\n\n' + join('account', 'retention')
        tp['records']['paragraphs'][0] = join('automaticBackup', 'iosAppDataBackup', 'androidSystemBackup', 'sync', 'retention', 'webDeletion', 'notice', 'analytics')
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
    return {'ios-content.json': ios, 'android-content.candidate.json': android,
            'terms-content.json': terms, 'us-health-content.json': us_health}

def deletion_panel(c, loc):
    text = c['locales'][loc]
    title = html.escape(text['deletionTitle'])
    mailto = 'mailto:' + c['deletionRequest']['supportEmail'] + '?' + urlencode({'subject': 'DoseWeek account deletion request'})
    paragraphs = ''.join('<p>' + html.escape(text[k]) + '</p>' for k in ('releaseStatus', 'webDeletion', 'retention', 'automaticBackup', 'iosAppDataBackup', 'androidSystemBackup', 'serverBackup', 'account', 'analytics'))
    return f'<article id="{loc}" class="language-panel" lang="{loc}" dir="{locale_pages.direction(loc)}" data-language="{loc}" data-document-title="{title} — DoseWeek" aria-labelledby="{loc}-content"><header class="hero"><h1 id="{loc}-content">{title}</h1></header><div class="policy-card">{paragraphs}<a class="button primary" href="{html.escape(mailto, quote=True)}">{html.escape(text["requestLabel"])}</a><p><a href="{html.escape(mailto, quote=True)}">wonyoung@wonyoungchoi.dev</a></p></div></article>'

def rendered_pages(sources, candidate=None):
    c = candidate or account_sync_candidate.load()
    i, a, t = (sources[k] for k in ('ios-content.json', 'android-content.candidate.json', 'terms-content.json'))
    pages = {render_ios.PAGE_PATH: render_ios.rendered(i), render_ios.SUPPORT_PATH: render_ios.rendered_support(i), **render_ios.rendered_locale_pages(i)}
    pages.update({p: s for p,s in {**render_android.rendered_pages(a), **render_android.rendered_locale_pages(a)}.items() if p.relative_to(ROOT).as_posix().endswith(('privacy/index.html','support/index.html'))})
    pages.update(render_terms.rendered_pages(t, i))
    pages.update(render_us_health.rendered_pages(sources['us-health-content.json'], i))
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
    assert len(pages) == len(ROUTES) * (len(c['localeOrder']) + 1)
    return pages

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='Local review directory outside this public checkout')
    parser.add_argument('--check', action='store_true', help='Validate all staged sources/pages in memory without writing or publishing')
    args = parser.parse_args()
    sources = integrated_sources()
    pages = rendered_pages(sources)
    if args.check:
        assert all(markup.strip().startswith('<!doctype html>') and
                   'name="robots" content="noindex,nofollow"' in markup
                   for markup in pages.values()), 'Incomplete staged HTML or missing unpublished gate'
        print(f'OK: {len(pages)} unpublished staged pages, {len(ROUTES)} routes, 17 locales; no files written')
        return
    assert args.output is not None, 'Use --check or --output'
    output = args.output.resolve()
    assert output != ROOT and not output.is_relative_to(ROOT), 'Never render staged pages into the public checkout'
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
    print(f'OK: staged {len(pages)} pages, {len(ROUTES)} routes x 18 (hash + 17 locales), with null effective date; {output}')

if __name__=='__main__':main()
