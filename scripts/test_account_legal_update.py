#!/usr/bin/env python3
"""Assertion-only 1.0.6 account/health-consent and backup disclosure regression checks."""
import json
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'docs/account-sync-content.candidate.json'
LOCALES = ('ko','en','ja','de','fr','es','it','nl','pt-PT','pl','sv','hi','pt-BR','ar','zh-Hans','zh-Hant','tr')
# Localized concepts, rather than numbers alone, guard equivalent disclosures in every locale.
HEALTH = {
 'ko': ('별도 선택 동의','약 이름','주사 일정','투여 기록','체중','식사','단백질','증상','메모','복원','30일','7일','기본 기록','동기화는 쓸 수 없어요'),
 'en': ('separate optional consent','medicine names','injection schedules','dose records','weight','meals','protein','symptoms','notes','restore','30 days','7 days','local-record','sync is unavailable'),
 'ja': ('別の任意の同意','薬の名前','注射予定','投与記録','体重','食事','たんぱく質','症状','メモ','復元','30日','7日','端末の記録','同期は利用できません'),
 'de': ('gesonderte freiwillige Einwilligung','Medikamentennamen','Injektionszeiten','Dosisaufzeichnungen','Gewicht','Mahlzeiten','Protein','Symptome','Notizen','wiederherzustellen','30 Tagen','7 Tage','lokale Aufzeichnungen','Synchronisierung ist nicht verfügbar'),
 'fr': ('consentement facultatif distinct','noms des médicaments','horaires d’injection','prises','poids','repas','protéines','symptômes','notes','restaurer','30 jours','7 jours','enregistrement local','synchronisation est indisponible'),
 'es': ('consentimiento opcional separado','nombres de medicamentos','horarios de inyección','registros de dosis','peso','comidas','proteínas','síntomas','notas','restaurar','30 días','7 días','registro local','sincronización no está disponible'),
 'it': ('consenso facoltativo separato','nomi dei farmaci','orari delle iniezioni','somministrazioni','peso','pasti','proteine','sintomi','note','ripristinare','30 giorni','7 giorni','registrazione locale','sincronizzazione non è disponibile'),
 'nl': ('afzonderlijke vrijwillige toestemming','medicijnnamen','injectietijden','dosisregistraties','gewicht','maaltijden','eiwitten','symptomen','notities','herstellen','30 dagen','7 dagen','lokale registratie','synchronisatie is niet beschikbaar'),
 'pt-PT': ('consentimento facultativo separado','nomes dos medicamentos','horários de injeção','registos de doses','peso','refeições','proteínas','sintomas','notas','restaurar','30 dias','7 dias','registo local','sincronização não está disponível'),
 'pl': ('odrębnej dobrowolnej zgody','nazwy leków','harmonogramy wstrzyknięć','zapisy dawek','masę ciała','posiłki','białko','objawy','notatki','przywracać','30 dni','7 dni','lokalne zapisy','synchronizacja jest niedostępna'),
 'sv': ('separat frivilligt samtycke','läkemedelsnamn','injektionsscheman','dosregistreringar','vikt','måltider','protein','symtom','anteckningar','återställa','30 dagar','7 dagar','lokala registreringar','synkronisering är inte tillgänglig'),
 'hi': ('अलग वैकल्पिक सहमति','दवाओं के नाम','इंजेक्शन समय','खुराक रिकॉर्ड','वज़न','भोजन','प्रोटीन','लक्षण','नोट','बहाल','30 दिन','7 दिन','स्थानीय रिकॉर्ड','सिंक उपलब्ध नहीं'),
 'pt-BR': ('consentimento opcional separado','nomes dos medicamentos','horários de injeção','registros de doses','peso','refeições','proteínas','sintomas','notas','restaurar','30 dias','7 dias','registro local','sincronização não está disponível'),
 'ar': ('موافقة اختيارية منفصلة','أسماء الأدوية','جداول الحقن','سجلات الجرعات','الوزن','الوجبات','البروتين','الأعراض','الملاحظات','استعادة','30 يومًا','7 أيام','التسجيل المحلي','المزامنة غير متاحة'),
 'zh-Hans': ('单独的可选同意','药品名称','注射时间','用药记录','体重','饮食','蛋白质','症状','备注','恢复','30天','7天','本地记录','无法使用同步'),
 'zh-Hant': ('單獨的選擇性同意','藥品名稱','注射時間','用藥紀錄','體重','飲食','蛋白質','症狀','備註','復原','30天','7天','本機紀錄','無法使用同步'),
 'tr': ('ayrı isteğe bağlı onay','ilaç adları','enjeksiyon zamanları','doz kayıtları','kilo','öğünler','protein','belirtiler','notlar','geri yüklemek','30 gün','7 gün','yerel kayıt','eşitleme kullanılamaz'),
}
BACKUP = {
 'ko': ('매일','업로드 전에','암호화','Amazon S3','서울','매주','OS','7일','다시 사용하지 않아요'),
 'en': ('daily','before upload','encrypted','Amazon S3','Seoul','weekly','OS','7 days','never reactivated'),
 'ja': ('毎日','アップロード前','暗号化','Amazon S3','ソウル','毎週','OS','7日','再利用しません'),
 'de': ('täglich','vor dem Upload','verschlüsselt','Amazon S3','Seoul','wöchentlich','OS','7 Tagen','nicht wieder verwendet'),
 'fr': ('chaque jour','avant le téléversement','chiffrées','Amazon S3','Séoul','chaque semaine','OS','7 jours','ne sont jamais réutilisées'),
 'es': ('diarias','antes de subirlos','cifrados','Amazon S3','Seúl','semanales','OS','7 días','no se reutilizan'),
 'it': ('giornaliere','prima del caricamento','cifrati','Amazon S3','Seul','settimanali','OS','7 giorni','non vengono riutilizzati'),
 'nl': ('dagelijks','vóór het uploaden','versleuteld','Amazon S3','Seoul','wekelijks','OS','7 dagen','nooit opnieuw gebruikt'),
 'pt-PT': ('diárias','antes do envio','cifrados','Amazon S3','Seul','semanais','OS','7 dias','não são reutilizados'),
 'pl': ('codziennie','przed wysłaniem','szyfrowane','Amazon S3','Seulu','co tydzień','OS','7 dni','nie są ponownie używane'),
 'sv': ('dagligen','före uppladdning','krypterade','Amazon S3','Seoul','varje vecka','OS','7 dagar','återanvänds aldrig'),
 'hi': ('रोज़','अपलोड से पहले','एन्क्रिप्ट','Amazon S3','सियोल','साप्ताहिक','OS','7 दिन','दोबारा इस्तेमाल नहीं'),
 'pt-BR': ('diários','antes do envio','criptografados','Amazon S3','Seul','semanais','OS','7 dias','não são reutilizados'),
 'ar': ('يوميًا','قبل الرفع','مشفّرة','Amazon S3','سيول','أسبوعيًا','OS','7 أيام','لا تُستخدم مجددًا'),
 'zh-Hans': ('每天','上传前','加密','Amazon S3','首尔','每周','OS','7天','不会重新使用'),
 'zh-Hant': ('每天','上傳前','加密','Amazon S3','首爾','每週','OS','7天','不會重新使用'),
 'tr': ('günlük','yüklemeden önce','şifrelenir','Amazon S3','Seul','haftalık','OS','7 gün','yeniden kullanılmaz'),
}
IMMEDIATE = {
 'ko': ('동의를 철회','30일 대기기간','장애 유예','즉시','지체 없이'),
 'en': ('withdraw consent','30-day waiting period','store-outage extension','immediately','without delay'),
 'ja': ('同意を撤回','30日の待機期間','ストア障害による延長','直ちに','遅滞なく'),
 'de': ('Einwilligung widerrufen','30-tägige Wartezeit','Verlängerung bei Store-Ausfällen','sofort','unverzüglich'),
 'fr': ('retirez votre consentement','délai de 30 jours','prolongation liée à une panne du store','immédiatement','sans délai'),
 'es': ('retira su consentimiento','espera de 30 días','prórroga por fallo de la tienda','inmediatamente','sin demora'),
 'it': ('revochi il consenso','attesa di 30 giorni','proroga per guasti dello store','subito','senza ritardo'),
 'nl': ('toestemming intrekt','wachttijd van 30 dagen','verlenging bij een winkelstoring','direct','zonder vertraging'),
 'pt-PT': ('retirar o consentimento','espera de 30 dias','adiamento por falha da loja','imediatamente','sem demora'),
 'pl': ('wycofasz zgodę','30-dniowy okres oczekiwania','przedłużenie z powodu awarii sklepu','natychmiast','bez zwłoki'),
 'sv': ('återkallar samtycket','väntetiden på 30 dagar','förlängningen vid butiksavbrott','omedelbart','utan dröjsmål'),
 'hi': ('सहमति वापस','30 दिन की प्रतीक्षा','स्टोर बाधा का विस्तार','तुरंत','बिना देरी'),
 'pt-BR': ('retirar o consentimento','espera de 30 dias','adiamento por falha da loja','imediatamente','sem demora'),
 'ar': ('سحب الموافقة','انتظار 30 يومًا','التمديد بسبب تعطل المتجر','فورًا','دون تأخير'),
 'zh-Hans': ('撤回同意','30天等待期','商店故障延期','立即','及时删除'),
 'zh-Hant': ('撤回同意','30天等待期','商店故障延期','立即','及時刪除'),
 'tr': ('onayınızı geri çekerseniz','30 günlük bekleme','mağaza kesintisi uzatması','hemen','gecikmeden'),
}

RETENTION_BASELINE = {
 'ko': ('확인한 마지막 Plus 기간이 끝나고 30일','스토어에 한 번 더 확인','최대 7일','서버 사본만 삭제','계정 전체','스토어 구독은 취소되지 않아요'),
 'en': ('30 days after the end of the last Plus period that the server verified','checks with the store again','up to 7 days','delete only the server copy','whole account','does not cancel a store subscription'),
 'ja': ('確認した最後のPlus期間の終了から30日','ストアへ再確認','最大7日','コピーだけを削除','アカウント全体','定期購入は解約されません'),
 'de': ('30 Tage nach dem Ende des letzten Plus-Zeitraums','erneut beim Store','bis zu 7 Tage','nur die Serverkopie','gesamte Konto','beendet kein Store-Abo'),
 'fr': ('30 jours après la fin de la dernière période Plus','à nouveau le store','7 jours au maximum','uniquement la copie sur le serveur','tout le compte','n’annule pas l’abonnement'),
 'es': ('30 días después del final del último periodo de Plus','vuelve a consultar la tienda','hasta 7 días','solo la copia del servidor','toda la cuenta','no cancela la suscripción'),
 'it': ('30 giorni dopo la fine dell’ultimo periodo Plus','ricontrolla con lo store','fino a 7 giorni','solo la copia sul server','intero account','non annulla l’abbonamento'),
 'nl': ('30 dagen na het einde van de laatste Plus-periode','opnieuw bij de store','maximaal 7 dagen','alleen de serverkopie','hele account','zegt een store-abonnement niet op'),
 'pt-PT': ('30 dias após o fim do último período Plus','volta a consultar a loja','até 7 dias','apenas a cópia no servidor','toda a conta','não cancela a subscrição'),
 'pl': ('30 dni po zakończeniu ostatniego okresu Plus','ponownie sprawdza sklep','maksymalnie o 7 dni','tylko kopię na serwerze','całe konto','nie anuluje subskrypcji'),
 'sv': ('30 dagar efter slutet av den sista Plus-period','med butiken igen','högst 7 dagar','enbart serverkopian','hela kontot','avslutar inte ett butiksabonnemang'),
 'hi': ('अंतिम Plus अवधि','30 दिन बाद','स्टोर से फिर जाँच','अधिकतम 7 दिन','केवल सर्वर प्रति','पूरा खाता','सदस्यता रद्द नहीं होती'),
 'pt-BR': ('30 dias após o fim do último período do Plus','consulta a loja de novo','até 7 dias','só a cópia no servidor','conta inteira','não cancela a assinatura'),
 'ar': ('30 يومًا من انتهاء آخر فترة Plus','المتجر مرة أخرى','حتى 7 أيام','الخادم فقط','الحساب كله','لا يلغي اشتراك المتجر'),
 'zh-Hans': ('核实的最后一个 Plus 期间结束 30 天','再次向商店核实','最多可推迟 7 天','只删除服务器副本','整个账户','不会取消商店订阅'),
 'zh-Hant': ('驗證的最後一個 Plus 期間結束 30 天','再次向商店確認','最多可延後 7 天','只刪除伺服器副本','整個帳戶','不會取消商店訂閱'),
 'tr': ('doğruladığı son Plus döneminin bitiminden 30 gün','mağazayı yeniden denetler','en fazla 7 gün','yalnızca sunucudaki kopyayı','hesabın tamamını','mağaza aboneliğini iptal etmez'),
}

class AccountLegalUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(SOURCE.read_text(encoding='utf-8'))

    def assert_localized_concepts(self, field, expected):
        for locale in LOCALES:
            with self.subTest(locale=locale, field=field):
                value = self.raw.get('locales', {}).get(locale, {}).get(field, '')
                for concept in expected[locale]:
                    self.assertIn(concept, value, f'{locale}.{field}: missing {concept!r}')

    def test_health_consent_categories_purpose_retention_and_refusal_all_locales(self):
        self.assert_localized_concepts('healthConsent', HEALTH)

    def test_hybrid_backup_encryption_cadence_deletion_and_restore_all_locales(self):
        self.assert_localized_concepts('serverBackup', BACKUP)

    def test_direct_deletion_and_consent_withdrawal_have_no_expiry_wait_all_locales(self):
        self.assert_localized_concepts('retention', IMMEDIATE)

    def test_store_confirmed_expiry_recheck_reset_account_and_subscription_boundaries_all_locales(self):
        self.assert_localized_concepts('retention', RETENTION_BASELINE)

    def test_business_operator_and_representative_all_locales(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                text = self.raw.get('locales', {}).get(locale, {}).get('processors', '')
                self.assertIn('Wonyoung Labs', text)
                self.assertIn('Wonyoung Choi', text)
                self.assertIn('863-25-02023', text)
                self.assertIn('201, 6 Surim-ro 81beon-gil, Geumjeong-gu, Busan 46281', text)

    def test_unverified_backup_and_deletion_features_remain_publication_gated(self):
        readiness = self.raw.get('serverReadiness', {})
        for flag in ('retentionRecheckWired', 'syncResetRoute', 'syncResetUiIos', 'syncResetUiAndroid', 'backupWindowVerified'):
            self.assertIs(readiness.get(flag), False, flag)
        self.assertEqual(self.raw.get('status'), 'pre-release-candidate-not-published')

if __name__ == '__main__':
    unittest.main()
