from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

BASE_URL = "https://adanaorganize.org.tr/firmalar/?_sayfa="
MAX_PAGE = 23
WAIT_TIME = 15

options = Options()
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

def temizle_email(email):
    if email is None:
        return None
    email_lower = email.lower()
    # Gmail, Hotmail, Yahoo olanları sil
    if any(x in email_lower for x in ["@gmail.com", "@hotmail.com", "@yahoo.com"]):
        return None
    return email

tum_firmalar = []

for sayfa_no in range(1, MAX_PAGE + 1):
    url = BASE_URL + str(sayfa_no)
    print(f"\n🔄 [DEBUG] {sayfa_no}. sayfaya gidiliyor: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wpgb-card-wrapper"))
        )
        print(f"✅ [DEBUG] {sayfa_no}. sayfadaki firma kartları DOM’a yüklendi")
    except:
        print(f"❌ [DEBUG] {sayfa_no}. sayfada firma kartları yüklenmedi (timeout)")
        break

    time.sleep(2)  # LazyLoad için ek bekleme

    firma_kartlari = driver.find_elements(By.CLASS_NAME, "wpgb-card-wrapper")
    print(f"🔍 [DEBUG] {sayfa_no}. sayfada {len(firma_kartlari)} firma bulundu")

    if len(firma_kartlari) == 0:
        print("✅ [DEBUG] Firma bulunamadı, sayfalar bitti!")
        break

    for idx, kart in enumerate(firma_kartlari, start=1):
        firma_adi = telefon = email = web_site = None
        try:
            firma_adi = kart.find_element(By.CLASS_NAME, "wpgb-block-2").find_element(By.TAG_NAME, "a").get_attribute("textContent").strip()
        except Exception as e:
            print(f"⚠️ [DEBUG] Firma adı alınamadı: {e}")
        try:
            telefon = kart.find_element(By.CLASS_NAME, "wpgb-block-4").get_attribute("textContent").replace("Tel:", "").strip()
        except Exception as e:
            print(f"⚠️ [DEBUG] Telefon alınamadı: {e}")
        try:
            email_raw = kart.find_element(By.CLASS_NAME, "wpgb-block-8").get_attribute("textContent").replace("Email:", "").strip()
            email = temizle_email(email_raw)
        except Exception as e:
            print(f"⚠️ [DEBUG] Email alınamadı: {e}")
        try:
            web_site = kart.find_element(By.CLASS_NAME, "wpgb-block-6").get_attribute("textContent").replace("Web:", "").strip()
        except Exception as e:
            print(f"⚠️ [DEBUG] Web sitesi alınamadı: {e}")

        print(f"📌 [DEBUG] Sayfa:{sayfa_no} | {idx}/{len(firma_kartlari)} → {firma_adi} | Tel:{telefon} | Email:{email} | Web:{web_site}")

        tum_firmalar.append({
            "Firma Adı": firma_adi,
            "Telefon": telefon,
            "Email": email,
            "Web Sitesi": web_site,
            "Sayfa": sayfa_no
        })

print(f"\n✅ [DEBUG] Tüm sayfalardan {len(tum_firmalar)} firma toplandı")

if tum_firmalar:
    df = pd.DataFrame(tum_firmalar)

    # Boş e-mailleri de kaldırmak istersen:
    df = df[df["Email"].notna()]

    df.to_excel("adana_osb_firmalar.xlsx", index=False)
    print("📂 [DEBUG] Excel dosyası oluşturuldu: adana_osb_firmalar.xlsx")
else:
    print("⚠️ [DEBUG] Veri bulunamadı, dosya oluşturulmadı")

driver.quit()
print("✅ [DEBUG] Tarayıcı kapatıldı, işlem tamamlandı")
