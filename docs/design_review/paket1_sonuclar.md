# RevF1 — Paket 1 sonuçları (LTspice, model)

Tarih: 2026-11-11. Simülatör: LTspice 26.1.1 (bu makine). Temel netlist: Yasin'in `RevD5E1_24V_60W.cir`
(değiştirilmeden `LTspice_RevF1/base_RevD5E1_24V_60W.cir.txt` olarak kopyalandı). Her RevF1 netlist'i
`LTspice_RevF1/gen.py` + `gen2.py` + `gen4.py` ile, temel netlist üzerinde **assert edilen** metin değişiklikleriyle üretildi.
Paketteki orijinal `.cir/.log` dosyalarına dokunulmadı.

> Bütün sayılar **simülasyon (model)** sonucudur, ölçüm değildir. RevC/D3/D4/D5/D5E1 sonuçları burada
> karşılaştırma için bile kullanılmadı; tablodaki her satır bu oturumda RevF1 netlist'leriyle koşuldu.

Ortak RevF1 değişiklikleri (bütün varyantlarda): RSETT 13 k → **11,8 k** (limit ≈ 7,88 A), ROVB 18,7 k → **17,4 k**
(OVLO ≈ 58,1 V). Varyant karşılaştırması (madde 1) paket girişindeki Schottky (2× RBQ20NS100A) ile yapıldı;
nihai konfigürasyon **F** = varyant (e) + LM74700-Q1 ideal diyot (madde 3).


## 1. Varyant karşılaştırması (madde 1)

Koşullar: 27 °C nominal parazitikler (60/90 W); "sıcak köşe" = 70 °C, Lloop 20 nH, LgH/LgL 20 nH, CinCer 5 µF, L1 DCR 24 mΩ,
48 V, 7 ms'de 0,5 Ω yük (limit olayı). Q1 BSC040N08NS5 modeli **resmî değildir**: standart kütüphanede yok, Infineon
modeli indirilmedi (dosya indirme izni gerektiriyor); BSC026N08NS5 VDMOS modelinden ölçeklendi (kapasiteler ×0,58,
dirençler ×1,54, Rg 1,1 Ω). Kayıplar `Id·Vds` zaman ortalaması (sürücü kaybı hariç).

| Varyant | η @60 W 20/24/36/48 V (%) | 4 nokta ort. | Q1/Q2 kaybı 48 V/60 W (W) | Q1/Q2 kaybı 48 V/90 W (W) | VDS tepe Q1/Q2 sıcak köşe (V) | IL tepe/RMS maks. normal (A) | Ripple maks. (mVpp) |
|---|---|---|---|---|---|---|---|
| (a) 145 kHz, Q1 BSC026, RGH 4,7 | 95.38 / 95.44 / 94.96 / 93.39 | **94.79** | 1.96 / 0.54 | **2.29** / 0.54 | 54.1 / 51.5 | 8.49 / 7.54 | 26.1 |
| (b) 94 kHz, Q1 BSC026, RGH 4,7 | 95.75 / 95.95 / 95.72 / 94.63 | **95.51** | 1.37 / 0.41 | **1.55** / 0.41 | 53.1 / 51.3 | 9.00 / 7.56 | 39.1 |
| (c) 94 kHz, Q1 BSC040, RGH 4,7 | 95.88 / 96.20 / 96.62 / 96.69 | **96.34** | 0.40 / 0.06 | 0.61 / 0.12 | 53.1 / **67.7** | 9.00 / 7.56 | 37.5 |
| (d) 94 kHz, Q1 BSC040, RGH 3,3 | 95.88 / 96.21 / 96.62 / 96.72 | **96.36** | 0.37 / 0.06 | 0.56 / 0.13 | 53.3 / **77.4** | 9.01 / 7.56 | 38.0 |
| (c2) 99,6 kHz, Q1 BSC040, RGH 4,7 (ek) | – | – | 0.42 / 0.06 | 0.64 / 0.12 | 53.4 / **68.3** | 8.93 / 7.55 | 35.1 |
| **(e) 99,6 kHz, Q1 BSC040, RGH 6,8 (ek)** | 95.82 / 96.15 / 96.57 / 96.62 | **96.29** | 0.48 / 0.07 | **0.73** / 0.12 | 53.5 / **56.8** | 8.95 / 7.55 | 38.4 |
| (f) 99,6 kHz, Q1 BSC040, RGH 10 (ek) | – | – | 3.99 / 1.91 | **4.24** / 1.90 | 58.4 / 51.3 | 8.92 / 7.55 | 34.1 |

fsw ölçümü (histerezisli kenar sayımı): RFREQ 30,1 k → 145,5 kHz; 24,3 k → 94,3 kHz; 24,9 k → **99,6 kHz**.

**Seçim kuralı** (VDS ≤ 64 V, Q1 kaybı 48 V/90 W ≤ 1,2 W, IL tepe ≤ 12 A normal çalışmada, ripple ≤ 60 mVpp; sağlayanlar içinde
en yüksek 4 nokta verim):
- (a), (b): Q1 kaybı kuralı sağlanmıyor (2,29 / 1,55 W).
- (c), (d): verim en yüksek, ama sıcak köşede **Q2 VDS 67,7 / 77,4 V** (Q1 hızlı açılınca SW yükselen kenarında aşma).
- Ek varyantlar bu yüzden koşuldu: RGH büyütülerek Q1 açılışı yavaşlatıldı. (c2) 4,7 Ω hâlâ 68,3 V; (f) 10 Ω Q1'i yavaş
  açtığı için kayıp 4,2 W (reddedildi).
- **(e) RFREQ 24,9 k (99,6 kHz) + Q1 BSC040N08NS5 + RGH 6,8 Ω: bütün kuralları sağlayan tek varyant** → seçildi.
  Verimde (c)/(d)'ye göre kaybı 0,05–0,07 puan.

## 2. Nihai konfigürasyon F (e + LM74700-Q1 ideal diyot)

F = (e) + D1/D2 yerine LM74700-Q1 + BSC026N08NS5 (Q3). Davranışsal LM74700 modeli `gen2.IDEAL` (TI modeli değil;
veri sayfası değerleri: 20 mV ileri regülasyon, 11 mA şarj pompası akımı, −11 mV ters kesim, ~13 V VGS sınırı,
3,9 V UVLO, 80 µA IQ). İlk sürüm (sert `if()` geçişleri) VIN rampası / VIN adımında çözücüyü kilitledi; v2'de
bütün geçişler `tanh` ile yumuşatıldı. **F sonuçlarının tamamı v2 ile yeniden koşuldu**; v1 sonuçları atıldı.
Kalıcı hal koşuları her VIN için o VIN'de üretilmiş prime durumundan başlar (`RevF1_F_prime27_{20,24,36,48}V`,
`RevF1_F_prime70_48V`).

| Nokta (27 °C) | Vout (V) | Ripple (mVpp) | η konnektörden (%) | Q1 / Q2 / Q3 (W) | IL tepe / RMS (A) |
|---|---|---|---|---|---|
| 20 V / 60 W | 11.998 | 20.2 | 97.69 | 0.232 / 0.030 / 0.063 | 5.77 / 5.03 |
| 24 V / 60 W | 11.998 | 20.8 | 97.66 | 0.258 / 0.036 / 0.052 | 5.93 / 5.04 |
| 36 V / 60 W | 11.998 | 33.1 | 97.52 | 0.356 / 0.047 / 0.035 | 6.28 / 5.06 |
| 48 V / 60 W | 11.998 | 35.0 | 97.24 | 0.491 / 0.068 / 0.026 | 6.43 / 5.08 |
| **4 nokta ort.** | | | **97.53** | | |
| 20 V / 90 W (1,6 Ω) | 11.997 | 33.2 | 96.97 | 0.408 / 0.066 / 0.095 | 8.34 / 7.52 |
| 48 V / 90 W (1,6 Ω) | 11.998 | 35.6 | 96.73 | 0.741 / 0.117 / 0.041 | 8.93 / 7.55 |

Ters polarite elemanının etkisi: Schottky'li (e) 4 nokta ortalaması %96,29 → ideal diyotlu F **%97,53 (+1,24 puan)**.
24 V/60 W'ta Schottky kaybı 1,02 W, Q3 kaybı 0,052 W.

> Not: Bu verimler yalnız güç katı + kontrol devresi modelini kapsar (konnektör girişinden yük direncine). Kart bakır
> kayıpları, kapasitör ESR'nin sıcaklıkla değişimi, BSC040'ın gerçek modeli ve ölçüm belirsizliği dahil değildir;
> laboratuvarda 1–2 puan daha düşük çıkması beklenmeli.

### 2b. FRA ve kompanzasyon (madde 2)

`.fra` (LTspice 26), @LOOP OUT–FBOUT, 500 Hz–32 kHz, 2 nokta/oktav, 60 W, 27 °C. LTspice faz ekranı 180° + ∠T'dir
(500 Hz'te integratör + çıkış kutbu için ~45° okunması ile doğrulandı), bu yüzden 0 dB'deki faz doğrudan faz payıdır.
GM: fazın 0°'ı kestiği frekanstaki −kazanç; 32 kHz'e kadar kesmiyorsa alt sınır olarak verildi.

| Kompanzasyon (RITH / CITH / CITHP) | 20 V | 24 V | 36 V | 48 V | en kötü PM | en kötü GM |
|---|---|---|---|---|---|---|
| D5E1: 10 k / 22 n / 470 p | 4,48 kHz, **44,1°** | 3,95 kHz, 55,5° | 3,55 kHz, 54,7° | 3,86 kHz, 60,9° | **44,1° ✗** | 29,1 dB |
| B: 10 k / 33 n / 470 p | 4,55 kHz, 46,7° | 4,04 kHz, 56,8° | 3,57 kHz, 58,1° | 3,96 kHz, 62,2° | 46,7° | 28,2 dB |
| **A: 8,2 k / 27 n / 470 p** | 3,83 kHz, **52,3°** | 3,34 kHz, 63,0° | 2,89 kHz, 58,0° | 3,33 kHz, 62,5° | **52,3° ✓** | ≥ 30,2 dB |

20 V'ta PM < 45° olduğu için kompanzasyon değiştirildi. **A seçildi** (en kötü PM 52,3°, GM ≥ 30 dB). Sıfır frekansı aynı
(~720 Hz), fc ~%15 düştü. B sınırda kaldığı için seçilmedi. A ile 90 W, limit ve başlangıç testleri yeniden koşuldu
(bölüm 4, 6): 20 V/90 W ripple 30,1 mVpp, 48 V/90 W 36,0 mVpp, regülasyon değişmedi. Bölüm 2'deki kalıcı hal tablosu
D5E1 kompanzasyonuyla koşuldu; kompanzasyon DC çalışma noktasını değiştirmediği için verim aynı (20 V/90 W: 96,97 → 97,01 %).

## 3. Ters polarite: LM74700-Q1 + N-MOSFET (madde 3)

**Devre** (veri sayfası tipik uygulaması, SOT-23-6 DBV: 1 VCAP, 2 GND, 3 EN, 4 CATHODE, 5 GATE, 6 ANODE):

| Eleman | Değer / parça | Gerekçe |
|---|---|---|
| U5 | LM74700QDBVRQ1 | ANODE ±65 V mutlak maks.; 20 mV ileri regülasyon; −11 mV'ta hızlı ters kesim; IQ 80 µA |
| Q3 | **BSC026N08NS5ATMA1** (80 V, 2,6 mΩ, TDSON-8) | VDS ≥ 80 V şartı; Q2 ile aynı parça (BOM'da yeni kalem yok, footprint ortak); stok DigiKey 6491, Farnell 8757 (2026-11-10) |
| CVCAP1 | 100 nF / 50 V X7R 0603, VCAP–ANODE | veri sayfası ≥ 0,1 µF |
| CANODE1 | 22 nF / 100 V X7R 0603, ANODE–GND | veri sayfası ≥ 22 nF |
| EN | ANODE'a bağlı | sürekli etkin |
| COUT | mevcut CIN1–10 (22 µF etkin) | veri sayfası ≥ 0,1 µF |

Q3 yönü: **source = konnektör (VIN_RAW), drain = dönüştürücü (VIN)**; gövde diyotu ileri yönde iletir, ters bağlantıda kesimde.

**Kayıp hesabı (veri sayfası):** Iin·RDS(on) < 20 mV olduğu sürece (I < 7,7 A @25 °C, ~5 A @RDS 4 mΩ sıcak) denetleyici
VGS'yi düşürüp düşümü 20 mV'ta tutar → P ≈ 20 mV · Iin. 24 V/60 W: 2,56 A → 51 mW (sim. 52 mW); 20 V/90 W: 4,64 A → 93 mW
(sim. 95 mW). IQ kaybı 48 V'ta 4 mW. Schottky'ye göre kazanç 0,6–1,9 W.

**Simülasyon (davranışsal model v2):**
- −48 V ters bağlantı (0 → −48 V, 0,5 ms rampa, 2,5 ms bekletme; `RevF1_F_reverse48_only`): kaynaktan akım < 1 nA,
  Q3 VGS = 0 V, Q3 VDS = 47,8 V, VIN en düşük −0,160 V, INTVCC en düşük −0,205 V (LTC3895 mutlak min −0,3 V), Vout 0 V.
- −48 V → 0 → +24 V (`RevF1_F_reverse48_then24V`, CSS 100 nF, 2,4 Ω): ters fazda aynı değerler; doğru polarite
  geldikten 7,8 ms sonra Vout %2 bandında, tepe 12,054 V, son 11,998 V; Q3 VGS 4,93 V, Q3 düşümü 19,6 mV (regülasyonda).
- Doğru polarite başlangıcı ayrıca bölüm 6'daki akım sınırlı kaynak testleriyle (20/36/48 V) doğrulandı.

**Riskler:**
- **Stok:** LM74700QDBVRQ1 DigiKey'de 0 adet (backorder, 26 hafta tedarik); Farnell'de yok; Mouser doğrulanamadı.
  ~~Pin uyumlu yedek: LM74500-Q1 … Kart iki parçayı da kabul eder.~~ **DÜZELTME (2026-11-12):** bu yanlıştı.
  LM74500-Q1 yalnız SOT-23-8 (DDF) paketinde var, pin dizilişi farklı (TI SNOSDB7). DBV footprint'ine takılmaz.
  Gerçek pin-pin yedek: Diodes **AP74700QW6-7** (SOT-26, LM74700 DBV ile aynı pinler). Ayrıntı: `docs/paket2b_ek_sonuclar.md`.
- **TVS yok:** 48 V işletim + 65 V mutlak maks. arasına sığan bir TVS yok (SMBJ48A Vc ≈ 77 V). Lab kaynağı ile risk düşük;
  uzun kablo / sıcak takma gerilim aşması ANODE'u 65 V'un üstüne çıkarabilir.
- Model TI'ın modeli değildir; ters kesim hızı ve şarj pompası dinamiği yaklaşık.

## 4. Akım sınırı RSETT 11,8 k (madde 4)

| Durum | Sonuç |
|---|---|
| 20 V / 90 W, 1,6 Ω (komp. A) | Vout 11,997 V, ripple 30,1 mVpp, CCOUT 4,98 V (CC döngüsü serbest, regülasyonu bozmuyor) |
| 48 V / 90 W, 1,6 Ω (komp. A) | Vout 11,998 V, ripple 36,0 mVpp, CCOUT 4,98 V |
| 0,5 Ω, 48 V, 27 °C nominal (komp. A) | limit **7,876 A** (Vout 3,94 V); Q1/Q2 VDS tepe 50,6 / 52,7 V; kalkınca 1,12 ms'de %2 bandı, tepe 12,18 V |
| 0,5 Ω, 48 V, 70 °C sıcak köşe (komp. A) | limit **7,876 A**; Q1/Q2 VDS tepe 54,1 / 56,9 V; kalkınca tepe 12,21 V, 1,12 ms; Vout 70 °C'de 12,025 V |

Hesap: Ilim = 1,25·12/(11,8+12)/(20·4 mΩ) = 7,88 A nominal. LT6654A ±%0,05, RSETT/RSETB %0,1, şönt %1, LT6105 kazanç
±%1, LT6105 ofseti (~75 mA eşdeğer) → kaba en kötü ±%3 → ~7,64–8,12 A. 90 W'ta (7,5 A) en kötü alt sınırla bile ~0,14 A pay var (13 k'da pay yoktu).

**CC döngüsü wind-up (onay bekleyen not):** Normal yükte LT1636 integratörü üst raya (CCOUT ≈ 4,98 V) doyuyor. Aşırı
yükte limitin oturması ~1 ms sürüyor; bu sürede akımı LTC3895'in kendi tepe sınırı tutuyor (IL tepe **12,59 A**,
yalnız geçici; L1 doyma akımıyla veri sayfasından karşılaştırılmalı). Kısa devre / limit girişinde bu davranış beklenen; iyileştirmek
için CCOUT'a ~1,5–2 V'ta anti-windup kıstırma önerilir. Simüle edilmedi, RevF1'e eklenmedi.

## 5. OVLO (madde 5)

OVLO bölücü ROVT 825 k / **ROVB 17,4 k** (her ikisi %1), LTC3895 OVLO eşiği 1,1 / 1,2 / 1,3 V (min/tip/maks), histerezis 100 mV.

| | ROVB 18,7 k (D5E1) | **ROVB 17,4 k (F1)** |
|---|---|---|
| Nominal kapanma | 54,1 V | **58,1 V** |
| En kötü alt (1,1 V, ROVT −%1, ROVB +%1) | 48,7 V (48 V'a 0,7 V pay) | **52,2 V** |
| En kötü üst (1,3 V, ROVT +%1, ROVB −%1) | 59,9 V | **64,2 V** |
| Nominal tekrar açılma (−100 mV) | 49,6 V | **53,3 V** |

64,2 V en kötü üst sınır LM74700 ANODE mutlak maksimumunun (65 V) ve Q1–Q3 80 V değerinin altında. Gerekirse %0,5'lik
dirençlerle bant 53,6–62,4 V'a daralır. RUN (130 k/10 k) değişmedi: nominal 16,8 V açılma.

## 6. Akım sınırlı lab kaynağıyla başlangıç (madde 6)

Model: kaynak 0 → VIN, 2 ms rampa, akım sınırı (seri mod 3 A, paralel mod 6 A), kaynak çıkışında 220 µF; yük 1,6 Ω (90 W);
soğuk başlangıç (prime yok, gear), **CSS 100 nF** (değişmedi). Sonuçlar nihai kompanzasyonla (A).

| Kaynak | Iin maks. | Vout tepe | %2 bandına giriş | Kaynak akım sınırında | Son Vout | Sonuç |
|---|---|---|---|---|---|---|
| 20 V, paralel 6 A | 6,0 A (anlık) | 12,032 V | 9,97 ms | 0,03 ms | 11,998 V | takılma yok |
| 36 V, seri 3 A | 3,0 A | 12,036 V | 11,31 ms | 8,0 ms | 11,997 V | takılma yok |
| 48 V, seri 3 A | 3,0 A | 12,033 V | 11,34 ms | 7,5 ms | 11,998 V | takılma yok |

Seri modda akım sınırındaki ~7,5–8 ms'nin çoğu giriş kapasitelerinin (~320 µF) 3 A ile dolmasıdır (kaynak terminali
bu sürede ~14 V'a kadar düşük kalır, RUN 16,8 V'ta açar); dönüştürücü çalıştıktan sonra kaynak sınırdan çıkar, hiccup
yok. **CSS büyütmeye gerek görülmedi** (220/330 nF denenmedi). 20 V'ta RUN pininde anahtarlama dikenleri 1,1 V altına
toplam 0,26 µs iniyor (0,5 µs ortalamada en düşük 1,394 V); kapanma olmadı — bkz. onay bekleyen kararlar.

## 7. Termal (madde 7) — elle model, ölçüm değil

Tj = Ta + P_Q1·θ_yerel + P_diğer·θ_bağlaşım. P_Q1 = LTspice Q1 kaybı (27 °C model) + RDS(on)'un ~100 °C'deki artışı
(iletim payı ×1,7). P_diğer = konnektör kaybı − Q1 − L1 DCR kaybı (L1 kendi gövdesinde ısınır).
θ değerleri: (a) 4 katlı kart, ~6 cm² VIN bakırı + 25 termal via: 35 K/W (BSC040 θJC ≈ 1,4 K/W dahil; literatür 30–40 K/W);
(b) + alt yüzdeki açık VIN bakırına ~2 cm² yalıtkan ped (≈2,5 K/W) + 18 K/W pasif soğutucu (ör. Boyd 573300D00000G):
paralel yol → 15,6 K/W; (c) + 40 mm 12 V fan (ör. Sunon MF40101V1-1000U-A99, 0,62 W): soğutucu ≈ 10 K/W, kart 20 K/W
→ 9,4 K/W, bağlaşım 3 K/W.

| Soğutma | Nokta | Ta (°C) | P_Q1 (W) | Diğer kart kaybı (W) | Tj Q1 (°C) |
|---|---|---|---|---|---|
| (a) bakır dökümü + termal via (4 kat) | 48V/60W | 25 | 0.51 | 0.71 | 46 |
| (a) bakır dökümü + termal via (4 kat) | 48V/60W | 40 | 0.51 | 0.71 | 61 |
| (a) bakır dökümü + termal via (4 kat) | 48V/90W | 25 | 0.78 | 1.18 | 58 |
| (a) bakır dökümü + termal via (4 kat) | 48V/90W | 40 | 0.78 | 1.18 | 73 |
| (b) (a) + alt yüzde açık bakıra yalıtkan pedle küçük soğutucu | 48V/60W | 25 | 0.51 | 0.71 | 36 |
| (b) (a) + alt yüzde açık bakıra yalıtkan pedle küçük soğutucu | 48V/60W | 40 | 0.51 | 0.71 | 51 |
| (b) (a) + alt yüzde açık bakıra yalıtkan pedle küçük soğutucu | 48V/90W | 25 | 0.78 | 1.18 | 43 |
| (b) (a) + alt yüzde açık bakıra yalıtkan pedle küçük soğutucu | 48V/90W | 40 | 0.78 | 1.18 | 58 |
| (c) (b) + 40 mm 12 V fan (0,62 W, çıkıştan) | 48V/60W | 25 | 0.51 | 0.71 | 32 |
| (c) (b) + 40 mm 12 V fan (0,62 W, çıkıştan) | 48V/60W | 40 | 0.51 | 0.71 | 47 |
| (c) (b) + 40 mm 12 V fan (0,62 W, çıkıştan) | 48V/90W | 25 | 0.78 | 1.18 | 36 |
| (c) (b) + 40 mm 12 V fan (0,62 W, çıkıştan) | 48V/90W | 40 | 0.78 | 1.18 | 51 |

**Fan gücünün verime etkisi** (fan çıkıştan beslenir; dönüştürücü 60 W + 0,62 W verir, verim 60 W yüke göre):

| VIN | η (fan yok) % | η (fan dahil) % |
|---|---|---|
| 20 V | 97.69 | 96.69 |
| 24 V | 97.66 | 96.66 |
| 36 V | 97.52 | 96.52 |
| 48 V | 97.24 | 96.24 |
| ort. | 97.53 | 96.53 |

Sonuç: Q1 kaybı (e)/F'de 0,74 W'a düştüğü için **(a) bakır + via yeterli** (40 °C ortamda 90 W'ta ~73 °C, BSC040 Tj maks
150 °C). Soğutucu yalnız pay için; fan verim bonusunu ~1 puan düşürüyor → **önerilmez** (J3 DNP olarak kartta).

## Özet: RevF1 değer/parça listesi (Paket 2'ye girdi)

| Ref | D5E1 | **RevF1** |
|---|---|---|
| RFREQ1 | 30,1 k (145 kHz) | **24,9 k** (99,6 kHz) — RC0603FR-0724K9L |
| Q1 | BSC026N08NS5 | **BSC040N08NS5ATMA1** (aynı TDSON-8 footprint) |
| RGH1 | 4,7 Ω | **6,8 Ω** — RC0603FR-076R8L |
| RITH1 / CITH1 / CITHP1 | 10 k / 22 n / 470 p | **8,2 k / 27 n C0G** / 470 p — RC0603FR-078K2L, GRM21B5C1H273JA01L |
| RSETT1 | 13 k 0,1 % | **11,8 k 0,1 %** — RT0603BRD0711K8L |
| ROVB1 | 18,7 k | **17,4 k** — RC0603FR-0717K4L |
| CSS1 | 100 n | 100 n (değişmedi) |
| D1, D2 | 2× RBQ20NS100A | **çıkarıldı** → U5 LM74700QDBVRQ1 + Q3 BSC026N08NS5ATMA1 + CVCAP1 100 n + CANODE1 22 n |
| L1 | XAL1510-333 footprint | **çift footprint** XAL1510-333 / WE-XHMI 1510 (Paket 2) |
| J3 | – | 12 V fan konnektörü, **DNP** (Paket 2) |

## Onay bekleyen kararlar

1. **Varyant (e) seçimi:** RFREQ 24,9 k (99,6 kHz), Q1 BSC040N08NS5, RGH 6,8 Ω. Gerekçe: dört kuralı sağlayan tek varyant.
   (c)/(d) %0,05–0,07 daha verimli ama sıcak köşede Q2 VDS 67,7/77,4 V. RGH 6,8 Ω, Q1 açılışını yavaşlatarak Q2 VDS'yi
   56,8 V'a indiriyor; frekansın 94 → 99,6 kHz olması RFREQ'in E96 değeri (24,9 k) ile ilgili, verime etkisi küçük.
2. **BSC040N08NS5 modeli ölçeklenmiş, resmî değil.** Infineon SPICE modeli indirilip (izin gerekir) (e) yeniden koşulmalı;
   özellikle VDS tepe (56,8 V) ve Q1 kaybı (0,74 W) bu modele bağlı. BSC040 stok: Farnell 4944 (2709860).
3. **Kompanzasyon A** (RITH 8,2 k, CITH 27 nF): 20 V'ta PM 44° → 52°. Line/load transient bonusu için ikinci kompanzasyon
   olarak D5E1 (10 k / 22 n) veya B (10 k / 33 n) A/B karşılaştırmasında kullanılabilir.
4. **Q3 = BSC026N08NS5** (Q2 ile aynı parça). Alternatif BSC035N10NS5 (100 V, daha fazla pay, DigiKey 14984).
5. **LM74700-Q1 stok riski:** DigiKey 0 / Farnell yok. Sipariş öncesi Mouser/TI store kontrol edilmeli; yedek
   ~~LM74500-Q1 aynı footprint'e takılır~~ (yanlış, bkz. düzeltme bölüm 3). Pin-pin yedek AP74700QW6-7. Sipariş verilmedi.
6. **TVS konmadı:** 65 V ANODE sınırına uyan TVS yok. Lab kaynağı ve kısa kablo varsayıldı. Sıcak takma testinde
   ANODE gerilimi izlenmeli.
7. **CSS 100 nF korundu:** 20 V/6 A ve 36/48 V/3 A'da takılma yok.
8. **RUN filtre kondansatörü (öneri, uygulanmadı):** 20 V'ta RUN'da 0,26 µs'lik dikenler 1,1 V altına iniyor. RUN–GND
   arasına 1–10 nF (DNP footprint) eklemek ucuz bir önlem; Paket 2'de eklenmedi, onay gerekiyor.
9. **CC döngüsü wind-up / anti-windup kıstırma (öneri, uygulanmadı):** limit girişinde ~1 ms boyunca IL tepe 12,6 A.
10. **Termal:** bakır + via yeterli (Tj ≤ ~73 °C @40 °C, 90 W). Soğutucu bölgesi kartta hazır, fan DNP; fan verimi
    ~1 puan düşürdüğü için önerilmez.
11. **LM74700 davranışsal modeli** (v2, TI modeli değil): ters kesim ve şarj pompası dinamiği yaklaşık; TI modeli
    (izinle indirilirse) ile ters polarite ve hot-plug yeniden koşulmalı.

## Dosyalar

- `LTspice_RevF1/gen.py, gen2.py, gen4.py, gen5.py, gen6.py` — netlist üreteçleri; `run.py` (paralel batch, bir kez farklı
  ayarla tekrar), `meas.py`, `fra.py`, `events.py`, `thermal.py`; `results.json` — tüm ölçümler.
- `RevF1_*.cir / .log` — her koşunun netlist'i ve log'u; `.state` prime durumları. `.raw` dosyaları git dışında.
- Yakınsama: bütün koşular ilk denemede tamamlandı. LM74700 modeli v1 ile 0 V'tan rampa / VIN adımı koşuları
  ilerlemediği için durduruldu ve model v2 ile hepsi yeniden koşuldu; v1 F sonuçları silindi, raporda kullanılmadı.
