from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import traceback

# === WebDriver ayarları ===
options = Options()
# options.add_argument("--headless")  # Arka planda çalıştırmak istersen aç
driver = webdriver.Chrome(options=options)

# === Siteye git ===
url = "https://www.antalyaosb.org.tr/tr/firmalar#"
driver.get(url)
time.sleep(3)

# === Firma kartlarını toplayan fonksiyon (her iki kart tipini destekler) ===
def firma_kartlari_al():
    divs = driver.find_elements(By.TAG_NAME, "div")
    kartlar = []
    for div in divs:
        classes = div.get_attribute("class")
        if classes:
            class_list = classes.strip().split()

            # Tip 1
            tip1 = ["col-lg-4", "col-md-4", "col-sm-6", "col-xs-12"]
            # Tip 2
            tip2 = ["col-sm-4", "clo-xs-12"]

            if (all(cls in class_list for cls in tip1) or
                all(cls in class_list for cls in tip2)):
                # Ayrıca içinde h4 ve a varsa gerçek firma kartıdır
                try:
                    h4 = div.find_element(By.TAG_NAME, "h4")
                    a = div.find_element(By.TAG_NAME, "a")
                    if h4 and a:
                        kartlar.append(div)
                except:
                    continue
    return kartlar

# === Scroll işlemi ===
firma_linkleri = []
scroll_attempts = 0
max_scroll_attempts = 15
last_firma_sayisi = 0

print("\n🔁 Scroll işlemi başlıyor...")

while scroll_attempts < max_scroll_attempts:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    kartlar = firma_kartlari_al()
    print(f"🔍 Görünen firma kartı sayısı: {len(kartlar)}")

    if len(kartlar) > last_firma_sayisi:
        try:
            son_kart = kartlar[-1]
            firma_ismi = son_kart.find_element(By.TAG_NAME, "h4").text.strip()
            print(f"🆕 Yeni firma geldi: {firma_ismi}")
        except:
            print("🆕 Yeni firma geldi ama isim alınamadı.")

        last_firma_sayisi = len(kartlar)
        scroll_attempts = 0
    else:
        scroll_attempts += 1

print(f"\n✅ Scroll tamamlandı. Toplam {last_firma_sayisi} firma kartı bulundu.")

# === Firma isimlerini ve linklerini topla ===
print("\n📥 Firma isim ve linkleri toplanıyor...")

firma_bilgileri = []

for div in firma_kartlari_al():
    try:
        isim = div.find_element(By.TAG_NAME, "h4").text.strip()
        a_tag = div.find_element(By.TAG_NAME, "a")
        link = a_tag.get_attribute("href")

        if "/firma/" in link:
            firma_bilgileri.append({"isim": isim, "link": link})
            print(f"📌 {isim} → {link}")
    except Exception as e:
        print(f"⚠️ Firma bilgisi alınamadı: {e}")

print(f"\n✅ Toplam {len(firma_bilgileri)} firma detay linki başarıyla alındı.")

# === Firma iletişim bilgilerini çek ===
print("\n📥 Firma iletişim bilgileri toplanıyor...")

firma_detaylari = []

for firma in firma_bilgileri:
    driver.get(firma["link"])
    time.sleep(2)  # Sayfanın yüklenmesi için kısa bekleme

    try:
        # unit-contact class'lı <ul> bul
        ul_element = driver.find_element(By.CLASS_NAME, "unit-contact")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        detay_bilgileri = []
        for li in li_elements:
            text = li.text.strip()

            # "Kuruluş" içeren satırı atla
            if "Kuruluş" in text:
                continue

            detay_bilgileri.append(text)

        firma_detaylari.append({
            "isim": firma["isim"],
            "link": firma["link"],
            "iletisim": detay_bilgileri
        })

        print(f"✅ {firma['isim']} iletişim bilgileri alındı")
    
    except Exception as e:
        print(f"⚠️ {firma['isim']} iletişim bilgisi alınamadı: {e}")

print("\n✅ Tüm firma detayları toplandı!")

# === Sonuçları yazdır ===
for detay in firma_detaylari:
    print("\n🔹", detay["isim"])
    print("   Link:", detay["link"])
    for bilgi in detay["iletisim"]:
        print("   -", bilgi)

# İşlem bittiğinde driver'ı kapat

# === Sonuçları Excel'e kaydet ===
df = pd.DataFrame(firma_detaylari)
excel_dosya_adi = "antalya_osb_firmalar.xlsx"
df.to_excel(excel_dosya_adi, index=False)
print(f"\n📂 Firma bilgileri '{excel_dosya_adi}' dosyasına kaydedildi.")

# İşlem bittiğinde driver'ı kapat
driver.quit()

