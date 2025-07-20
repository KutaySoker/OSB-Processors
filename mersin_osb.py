from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import traceback

def get_label_content(p):
    children = p.find_elements(By.XPATH, "./*")
    label = ""
    content = ""

    if children:
        first_child = children[0]
        if first_child.tag_name == "strong":
            label = first_child.text.strip().lower()
            # content = p.text.replace(first_child.text, "").strip()
            # Bu yöntem daha sağlam:
            full_text = p.text.strip()
            label_text = first_child.text.strip()
            # Label text'i kaldır, kalan content kalır
            if full_text.startswith(label_text):
                content = full_text[len(label_text):].strip()
            else:
                content = full_text.replace(label_text, "").strip()
        else:
            label = ""
            content = p.text.strip()
    else:
        label = ""
        content = p.text.strip()

    return label, content


options = Options()
# options.add_argument("--headless")  # istersen aç
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

firmalar = []

for sayfa in range(1, 36):
    url = f"https://www.mersinosb.org.tr/firmalar/?SayfaNo={sayfa}"
    print(f"\n📄 {sayfa}. sayfa açılıyor: {url}")
    driver.get(url)

    # Sayfa aşağı kaydır, dinamik yüklenme varsa gelsin diye
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    try:
        firma_kartlari = wait.until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "col-md-6"))
        )
        print(f"🔍 {len(firma_kartlari)} firma kartı bulundu.")

        for index, kart in enumerate(firma_kartlari, start=1):
            try:
                card_body = kart.find_element(By.CLASS_NAME, "blog-post")

                firma = {
                    "isim": "",
                    "adres": "",
                    "telefon": "",
                    "faks": "",
                    "email": ""
                }

                firma["isim"] = card_body.find_element(By.TAG_NAME, "h2").text.strip()
                print(f"    🔹 Firma ismi: {firma['isim']}")

                li_tags = card_body.find_elements(By.TAG_NAME, "li")
                print(f"    🔸 {len(li_tags)} <li> etiketi bulundu.")

                for li in li_tags:
                    strongs = li.find_elements(By.TAG_NAME, "strong")
                    if strongs:
                        label = strongs[0].text.strip().lower()
                        content = li.text.replace(strongs[0].text, "").strip()

                        if "adres" in label:
                            firma["adres"] = content
                            print(f"    🏠 Adres: {content}")
                        elif "telefon" in label:
                            firma["telefon"] = content
                            print(f"    📞 Telefon: {content}")
                        elif "faks" in label:
                            firma["faks"] = content
                            print(f"    📠 Faks: {content}")
                        elif "eposta" in label or "e-posta" in label:
                            firma["email"] = content
                            print(f"    📧 E-posta: {content}")

                firmalar.append(firma)

            except Exception as e:
                print(f"    ⚠️ Kart {index} içinde hata:", e)

    except Exception as e:
        print(f"🚨 Sayfa {sayfa} hata verdi:")
        traceback.print_exc()

driver.quit()

print(f"\n[✅] Toplam {len(firmalar)} firma çekildi.")

if firmalar:
    print("\n[🧪] Örnek firma:")
    print(firmalar[275])
    try:
        df = pd.DataFrame(firmalar)
        df.to_excel("mersin_osb_firmalar.xlsx", index=False)
        print("\n💾 Excel dosyası başarıyla oluşturuldu: mersin_osb_firmalar.xlsx")
    except Exception as e:
        print("❌ Excel dosyasına yazarken hata oluştu:", e)
else:
    print("[🚨] Hiçbir firma alınamadı.")
