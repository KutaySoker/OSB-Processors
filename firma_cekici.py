import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = "https://www.diyarbakirosb.org.tr/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

# OSB etapları ve sayfa sayıları
osb_list = [
    {"etap": "OSB 1. Etap", "url": "firma-kategori/osb-1-etap-firmalari", "sayfa": 14},
    {"etap": "OSB 2. Etap", "url": "firma-kategori/osb-2-etap-firmalari", "sayfa": 9},
    {"etap": "OSB 3. Etap", "url": "firma-kategori/osb-3-etap-firmalari", "sayfa": 7},
    {"etap": "OSB 4. Etap", "url": "firma-kategori/osb-4-etap-firmalari", "sayfa": 7}
]

tum_firmalar = []

for osb in osb_list:
    print(f"[*] {osb['etap']} verileri çekiliyor...")
    for page in range(1, osb["sayfa"] + 1):
        if page == 1:
            url = f"{base_url}{osb['url']}.html"
        else:
            url = f"{base_url}{osb['url'].replace('firma-kategori/', 'firma-kategori-')}/{page}.html"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[!] Sayfa alınamadı: {url}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        firma_items = soup.select("li.is-active")

        for item in firma_items:
            try:
                ad = item.select_one("h3.text").get_text(strip=True)
                href = item.select_one("a")["href"]
                detay_link = base_url + href
                tarih = item.select_one("div.date").get_text(strip=True)
            except:
                continue

            # Detay sayfasına git
            detay_resp = requests.get(detay_link, headers=headers)
            detay_soup = BeautifulSoup(detay_resp.content, "html.parser")

            telefon = email = website = adres = sektor = ""

            infos = detay_soup.select("div.col-lg-8 ul li")
            for li in infos:
                text = li.get_text(strip=True)
                if "Telefon" in text:
                    telefon = text.replace("Telefon:", "").strip()
                elif "E-Posta" in text:
                    email = text.replace("E-Posta:", "").strip()
                elif "Web Sitesi" in text:
                    website = text.replace("Web Sitesi:", "").strip()
                elif "Adres" in text:
                    adres = text.replace("Adres:", "").strip()
                elif "Sektör" in text:
                    sektor = text.replace("Sektör:", "").strip()

            tum_firmalar.append({
                "OSB Etabı": osb["etap"],
                "Firma Adı": ad,
                "Sektör": sektor,
                "Telefon": telefon,
                "E-Posta": email,
                "Web Sitesi": website,
                "Adres": adres,
                "Yayın Tarihi": tarih,
                "Detay Sayfa": detay_link
            })

            time.sleep(0.5)  # siteyi yorma

# Excel'e yaz
df = pd.DataFrame(tum_firmalar, columns=[
    "OSB Etabı", "Firma Adı", "Sektör", "Telefon", "E-Posta",
    "Web Sitesi", "Adres", "Yayın Tarihi", "Detay Sayfa"
])
df.index += 1
df.to_excel("Diyarbakir_Tum_OSB_Firmalari.xlsx", index_label="No")
print(f"\n[✔] Toplam {len(df)} firma başarıyla çekildi ve Excel'e yazıldı.")
