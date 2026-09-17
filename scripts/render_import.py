#!/usr/bin/env python3
"""Render the shared record import guide and its localized downloads."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ['ko', 'en', 'ja', 'de', 'fr', 'es', 'it', 'nl', 'pt-PT', 'pl', 'sv', 'hi', 'pt-BR', 'ar', 'zh-Hans', 'zh-Hant', 'tr']
LABELS = dict(zip(LANGUAGES, ['한국어', 'English', '日本語', 'Deutsch', 'Français', 'Español', 'Italiano', 'Nederlands', 'Português (Portugal)', 'Polski', 'Svenska', 'हिन्दी', 'Português (Brasil)', 'العربية', '简体中文', '繁體中文', 'Türkçe']))
BASE = 'https://doseweek-legal.wonyoungchoi.dev/'
SCALAR_FIELDS = ['source_app', 'source_record_id', 'date_text', 'date_iso', 'time_text', 'time_24h', 'time_zone', 'utc_offset', 'medication_name', 'dose_value_text', 'dose_unit', 'site_text', 'measurement_type', 'measurement_value_text', 'measurement_unit', 'symptom_text', 'severity_text', 'note']
# Owner decision TRANSFER-20260913-10: the published guide leads from a new AI chat to the in-app
# review and selected append. In the supported state every locale quotes the app's own labels for
# the import screen, its file button and its add button (identical in the iOS and Android apps).
IMPORT_IOS_VERSION = '1.0.5'
APP_LABELS = {
    'ko': ('다른 앱에서 기록 가져오기', '파일 선택', '선택한 기록 추가'),
    'en': ('Import records from another app', 'Choose file', 'Add selected records'),
    'ja': ('ほかのアプリから記録を取り込む', 'ファイルを選択', '選択した記録を追加'),
    'de': ('Einträge aus einer anderen App importieren', 'Datei auswählen', 'Ausgewählte Einträge hinzufügen'),
    'fr': ('Importer des données d’une autre app', 'Choisir un fichier', 'Ajouter les données sélectionnées'),
    'es': ('Importar registros de otra app', 'Elegir archivo', 'Añadir registros seleccionados'),
    'it': ('Importa registrazioni da un’altra app', 'Scegli file', 'Aggiungi registrazioni selezionate'),
    'nl': ('Gegevens uit een andere app importeren', 'Bestand kiezen', 'Geselecteerde registraties toevoegen'),
    'pt-PT': ('Importar registos de outra aplicação', 'Escolher ficheiro', 'Adicionar registos selecionados'),
    'pl': ('Importuj wpisy z innej aplikacji', 'Wybierz plik', 'Dodaj wybrane wpisy'),
    'sv': ('Importera poster från en annan app', 'Välj fil', 'Lägg till valda poster'),
    'hi': ('दूसरे ऐप से रिकॉर्ड आयात करें', 'फ़ाइल चुनें', 'चुने गए रिकॉर्ड जोड़ें'),
    'pt-BR': ('Importar registros de outro aplicativo', 'Escolher arquivo', 'Adicionar registros selecionados'),
    'ar': ('استيراد سجلات من تطبيق آخر', 'اختيار ملف', 'إضافة السجلات المحددة'),
    'zh-Hans': ('从其他应用导入记录', '选择文件', '添加所选记录'),
    'zh-Hant': ('從其他 App 匯入紀錄', '選擇檔案', '新增所選紀錄'),
    'tr': ('Başka bir uygulamadan kayıt aktar', 'Dosya seç', 'Seçilen kayıtları ekle'),
}
STEP_COUNTS = {'preparation_only': 3, 'supported': 6}
RECORD = {'row_id': 'row-0001', 'record_type': 'unclassified', 'source_app': None, 'source_record_id': None, 'source_references': [{'document': None, 'page': None, 'row': None, 'visible_text': None}]}
RECORD.update({key: None for key in SCALAR_FIELDS if key not in RECORD})
RECORD['needs_review'] = []
TEMPLATE = {'format': 'doseweek.record_extraction_draft', 'version': 1, 'reviewed_by_user': False, 'records': [RECORD], 'unreadable_sections': []}


def validate(content: dict, require_all: bool = False) -> None:
    assert set(content) == {'status', 'formatVersion', 'locales'}
    assert content['status'] in {'preparation_only', 'supported'}, 'Unknown publication state.'
    assert content['formatVersion'] == 1
    locales = content['locales']
    assert {'ko', 'en', 'ja'} <= locales.keys() <= set(LANGUAGES)
    if require_all:
        assert set(locales) == set(LANGUAGES), 'The published guide requires all 17 locales.'
    keys = set(locales['en'])
    lists = {'steps': STEP_COUNTS[content['status']], 'review_rules': 5, 'prompt_rules': 10, 'spec_rules': 7}
    for lang, value in locales.items():
        assert set(value) == keys, f'{lang}: translation keys differ'
        for key, field in value.items():
            if key in lists:
                assert isinstance(field, list) and len(field) == lists[key], f'{lang}.{key}: wrong shape'
                for item in field:
                    if key == 'steps':
                        assert set(item) == {'title', 'body'} and all(isinstance(v, str) and v.strip() for v in item.values())
                    else:
                        assert isinstance(item, str) and item.strip(), f'{lang}.{key}: empty rule'
            else:
                assert isinstance(field, str) and field.strip(), f'{lang}.{key}: empty translation'
        if content['status'] == 'supported':
            steps_text = ' '.join(step['body'] for step in value['steps'])
            for label in (*APP_LABELS[lang], value['copy_label']):
                assert label in steps_text, f'{lang}: steps must quote the label {label!r}'
            assert IMPORT_IOS_VERSION in value['status_body'], f'{lang}: status must name iOS {IMPORT_IOS_VERSION}'
        for token in ('date_text', 'time_text', 'source_references', 'source_record_id', 'row_id', 'row-0001', 'needs_review', 'unclassified', 'unreadable_sections', 'reviewed_by_user', 'false', 'null', 'administration', 'body_measurement', 'symptom', 'measurement_type', 'weight', 'height', 'waist', 'body_fat', 'lean_body_mass'):
            assert token in ' '.join(value['prompt_rules']), f'{lang}: missing machine token {token}'


def dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def prompt(value: dict) -> str:
    rules = '\n\n'.join(f'{i}. {rule}' for i, rule in enumerate(value['prompt_rules'], 1))
    return f"# {value['prompt_title']}\n\n{value['status_body']}\n\n{value['prompt_preamble']}\n\n{rules}\n\n{value['prompt_output']}\n\n```json\n{dump(TEMPLATE)}```\n\n{value['prompt_footer']}\n"


def spec(value: dict) -> str:
    return f"# {value['spec_title']}\n\n{value['status_body']}\n\n{value['spec_intro']}\n\n{value['app_limits']}\n\n" + '\n\n'.join(f'{i}. {rule}' for i, rule in enumerate(value['spec_rules'], 1)) + '\n\n```json\n' + dump(TEMPLATE) + '```\n'


def schema() -> dict:
    text = {'type': ['string', 'null'], 'minLength': 1}
    reference = {'type': 'object', 'additionalProperties': False, 'required': ['document', 'page', 'row', 'visible_text'], 'properties': {'document': text, 'page': {'type': ['integer', 'null'], 'minimum': 1}, 'row': text, 'visible_text': text}}
    properties = {key: dict(text) for key in SCALAR_FIELDS}
    properties.update({
        'row_id': {'type': 'string', 'pattern': '^row-[0-9]{4,}$'},
        'record_type': {'enum': ['administration', 'body_measurement', 'symptom', 'unclassified']},
        'source_references': {'type': 'array', 'minItems': 1, 'items': reference},
        'date_iso': {'type': ['string', 'null'], 'format': 'date', 'pattern': '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'},
        'time_24h': {'type': ['string', 'null'], 'pattern': '^([01][0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9](\\.[0-9]+)?)?$'},
        'utc_offset': {'type': ['string', 'null'], 'pattern': '^[+-]((0[0-9]|1[0-3]):[0-5][0-9]|14:00)$'},
        'measurement_type': {'enum': ['weight', 'height', 'waist', 'body_fat', 'lean_body_mass', None]},
        'needs_review': {'type': 'array', 'items': {'type': 'string', 'minLength': 1}},
    })
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': BASE + 'import/draft-v1.schema.json', 'title': 'DoseWeek record extraction draft v1', 'description': 'Unreviewed transcription draft for DoseWeek Import records from another app. Not an encrypted backup. Passing this schema does not mean a row can be saved; every row is reviewed in the app before the selected rows are added.', '$comment': 'Application resource limits: at most 10000 records, input JSON at most 10 MiB (10485760 bytes), nesting depth at most 32, and each decoded JSON string at most 16 KiB (16384 UTF-8 bytes). JSON Schema maxLength counts Unicode code points, not UTF-8 bytes; the importer must enforce the byte and nesting limits separately.', 'type': 'object', 'additionalProperties': False, 'required': list(TEMPLATE), 'properties': {'format': {'const': TEMPLATE['format']}, 'version': {'const': 1}, 'reviewed_by_user': {'const': False}, 'records': {'type': 'array', 'maxItems': 10000, 'items': {'type': 'object', 'additionalProperties': False, 'required': list(RECORD), 'properties': properties}}, 'unreadable_sections': {'type': 'array', 'items': {'type': 'string', 'minLength': 1}}}}


def rendered(content: dict) -> dict[str, str]:
    validate(content)
    locales = content['locales']
    status = content['status']
    description = locales['en']['lead'] + ' ' + locales['en']['status_title']
    langs = [lang for lang in LANGUAGES if lang in locales]
    e = html.escape
    downloads = {}
    panels = []
    skips = []
    links = []
    for lang in langs:
        value = locales[lang]
        direction = 'rtl' if lang == 'ar' else 'ltr'
        text = prompt(value)
        downloads[f'import/prompt.{lang}.md'] = text
        downloads[f'import/format.{lang}.md'] = spec(value)
        links.append(f'<li><a class="language-link" href="#{lang}" lang="{lang}" hreflang="{lang}" data-language-link="{lang}">{LABELS[lang]}</a></li>')
        skips.append(f'<a class="skip-link" href="#{lang}-title" lang="{lang}" dir="{direction}" data-language-skip="{lang}">{e(value["skip_label"])}</a>')
        steps = ''.join(f'<li class="info-card"><h2>{e(step["title"])}</h2><p>{e(step["body"])}</p></li>' for step in value['steps'])
        review = ''.join(f'<li>{e(rule)}</li>' for rule in value['review_rules'])
        spec_rules = ''.join(f'<li>{e(rule)}</li>' for rule in [value['app_limits'], *value['spec_rules']])
        panels.append(f'''<article id="{lang}" class="language-panel" lang="{lang}" dir="{direction}" data-language="{lang}" data-document-title="DoseWeek — {e(value['title'])}" aria-labelledby="{lang}-title">
<header class="hero"><h1 id="{lang}-title" tabindex="-1" data-skip-target>{e(value['title'])}</h1><p class="hero-copy">{e(value['lead'])}</p>
<div class="notice import-status" role="note" data-import-status="{status}"><strong>{e(value['status_title'])}</strong></div></header>
<ol class="card-grid three import-steps">{steps}</ol>
<section class="content-section" aria-labelledby="{lang}-prompt"><h2 id="{lang}-prompt">{e(value['prompt_title'])}</h2><p>{e(value['prompt_intro'])}</p>
<div class="button-row"><button class="button primary" type="button" data-copy-prompt="{lang}-prompt-text" data-copy-status="{lang}-copy-status" data-copy-success="{e(value['copied_label'])}" data-copy-failure="{e(value['copy_failed_label'])}" hidden>{e(value['copy_label'])}</button><a class="button" href="prompt.{lang}.md" download>{e(value['download_label'])}</a></div>
<p id="{lang}-copy-status" class="import-copy-status" role="status" aria-live="polite"></p>
<div class="faq-list"><details><summary><span>{e(value['prompt_details_label'])}</span><span class="summary-symbol" aria-hidden="true"></span></summary><div class="faq-answer"><pre id="{lang}-prompt-text" class="import-prompt" dir="ltr" tabindex="0">{e(text)}</pre></div></details>
<details><summary><span>{e(value['review_title'])}</span><span class="summary-symbol" aria-hidden="true"></span></summary><div class="faq-answer"><p>{e(value['status_body'])}</p><ul>{review}</ul></div></details>
<details><summary><span>{e(value['format_title'])}</span><span class="summary-symbol" aria-hidden="true"></span></summary><div class="faq-answer"><p>{e(value['format_intro'])}</p><ul>{spec_rules}</ul><p><a href="draft-v1.schema.json" download>{e(value['schema_label'])}</a></p><p><a href="format.{lang}.md" download>{e(value['spec_label'])}</a></p><p><a href="draft.example.json" download>{e(value['example_label'])}</a></p></div></details></div></section>
<footer class="site-footer"><a href="../#{lang if lang in ['en','ja','ko'] else 'en'}">{e(value['home_label'])}</a><a href="../support/#{lang}">{e(value['support_label'])}</a><a href="../android/support/#{lang}">{e(value['android_support_label'])}</a></footer>
</article>''')
    page = f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{e(description)}">
<meta name="color-scheme" content="light dark"><title>DoseWeek — {e(locales['ko']['title'])}</title>
<link rel="canonical" href="{BASE}import/"><link rel="icon" type="image/png" href="../assets/app-icon.png"><link rel="apple-touch-icon" href="../assets/app-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="DoseWeek"><meta property="og:title" content="DoseWeek — Prepare records from another app"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{BASE}import/"><meta property="og:image" content="{BASE}assets/app-icon.png"><meta property="og:image:alt" content="DoseWeek app icon">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="DoseWeek — Prepare records from another app"><meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{BASE}assets/app-icon.png"><meta name="twitter:image:alt" content="DoseWeek app icon">
<link rel="stylesheet" href="../assets/site.css"><link rel="stylesheet" href="../assets/import.css"><script src="../assets/language.js" defer></script><script src="../assets/import.js" defer></script>
</head><body>{''.join(skips)}
<header class="site-header site-shell"><a class="brand" href="../" aria-label="DoseWeek"><img class="brand-mark" src="../assets/app-icon.png" alt="" width="36" height="36"><span class="brand-label">DoseWeek</span></a><nav class="language-nav many-languages" aria-label="Language / 언어 / 言語"><ul class="language-list">{''.join(links)}</ul></nav></header>
<main id="main" class="site-shell" tabindex="-1"><div class="language-stack">{''.join(panels)}</div></main>
</body></html>
'''
    downloads['import/index.html'] = page
    downloads['import/draft-v1.schema.json'] = dump(schema())
    downloads['import/draft.example.json'] = dump({**TEMPLATE, 'records': []})
    return downloads


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--require-all-locales', action='store_true')
    args = parser.parse_args()
    content = json.loads((ROOT / 'import/content.json').read_text())
    validate(content, require_all=args.require_all_locales)
    for relative, text in rendered(content).items():
        target = ROOT / relative
        if args.check:
            assert target.exists() and target.read_text() == text, f'{relative}: stale generated output'
        else:
            target.write_text(text)
    print(f"OK: import guide and downloads ({len(content['locales'])} locales); status {content['status']}")

if __name__ == '__main__':
    main()
