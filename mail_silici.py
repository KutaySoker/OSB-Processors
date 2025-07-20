import pandas as pd

# Excel dosyasını yükle
dosya_adi = "antalya_osb_firmalar.xlsx"
df = pd.read_excel(dosya_adi)

# D,E,F,G,H sütunlarının index'leri (0'dan başlıyor)
sutun_indexleri = [3, 4, 5, 6, 7]

def temizle_mail_hucre(deger):
    """Eğer hücre gmail/hotmail içeriyorsa sil, yoksa bırak"""
    if pd.isna(deger):
        return deger
    text = str(deger).lower()
    if "@gmail.com" in text or "@hotmail.com" in text:
        return None
    return deger

# Seçili sütunlarda temizleme işlemi yap
for idx in sutun_indexleri:
    if idx < len(df.columns):  # Dosyada gerçekten bu sütun varsa
        col_name = df.columns[idx]
        df[col_name] = df[col_name].apply(temizle_mail_hucre)

# Yeni dosyaya kaydet
yeni_dosya = "antalya_osb_firmalar_filtreli.xlsx"
df.to_excel(yeni_dosya, index=False)

print(f"✅ Gmail/Hotmail adresleri D-H sütunlarından temizlendi → {yeni_dosya}")
