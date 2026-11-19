# RevF1 rev 2 — Paket 3 öncesi ek işler (madde 1–12)

Tarih: 2026-11-12. LTspice 26.1.1, KiCad 10.0.8. Bütün sayılar **simülasyon (model)**; ölçüm değil.
Önceki raporlar: `docs/paket1_sonuclar.md`, `docs/paket2_yerlesim.md` (ikisinde de rev 2 düzeltme notları var).

## 0. Özet

| Konu | Sonuç |
|---|---|
| Resmî Infineon modeli | `_L0` seviyesiyle (e) kayıpları VDMOS'tan belirgin yüksek. Örn. 48 V/90 W'ta Q1 0,73 → 1,00 W. Ölçeklenmiş modelin c/d'de gösterdiği 68–77 V'luk Q2 VDS dikenleri ise resmî modelde yok (~52 V). |
| **(e) seçimi** | **Artık geçerli değil.** c, d ve e kuralların hepsini geçiyor; e en düşük verimli ve gate'te çapraz iletime giriyor. **Varyant (c) uygulandı:** RFREQ 24,3 k (94,3 kHz), RGH 4,7 Ω, Q1 BSC040. |
| RGH uçurumu | 8,2 ile 10 Ω arasında. 10 Ω'da Q1+Q2 kaybı 4,5 W. Mekanizma: RGH Q1'in kapanışını geciktiriyor, ama LTC3895 ölü zamanı TG pininden ölçüyor. 6,8 Ω gate'te zaten −24 ns örtüşüyordu. |
| 8,55 A ile 7,876 A | Ölçüm penceresi artefaktı: CC integratörü raydan inerken ölçülmüş. Oturmuş limit 7,876 A. |
| LM74700 / LM74500 | LM74500 yalnız DDF-8 paketinde, DBV'ye pin uyumlu **değil**; ters akım blokajı yok; stok Mart 2027. LM74700 DBV kaldı. Pin-pin yedek: **AP74700QW6-7** (Diodes). |
| Hot-plug (48 V) | ANODE en fazla 54,4 V, Q3 VDS en fazla 38 V (0,5 µH kablo); sınırların altında. Q3 drain'ine 1 µF eklemek önerilir. Bring-up prosedürü yazıldı. |
| HF kondansatörleri | CHF2/CHF3 eklendi. Sıcak köşede Q2 VDS 67,0 → **49,6 V** (resmî model). |
| RUN kondansatörü | CRUN1 1 nF takılı. Açılış eşiği 16,800 → 16,809 V (değişmedi); RUN ripple'ı 0,36 → 0,003 Vpp. |
| FRA 90 W | PM 58,5–66,1°, GM > 15–22 dB. |
| Kısa devre dönüşü | Tepe 12,34 V (+%2,8), 1,4 ms'de %2 bandı. Anti-windup eklenmedi. |
| Termal | Gerçek pencere 0,37 cm². Soğutucuyla Tj 82 → 67 °C (40 °C, 90 W); soğutucusuz da yeterli. |
| ERC / DRC / parity | 0 / 0 / 0. `.kicad_pro` hash'i paketle aynı. |

Nihai konfigürasyon **H** = varyant (c) + LM74700-Q1 (davranışsal v2) + kompanzasyon A (8,2 k / 27 nF / 470 pF)
+ CRUN 1 nF + yeni HF yolu (CHF1 + CHF2 + CHF3 = 3×100 nF, ~1 nH). Q1 ve Q2 için resmî `_L0` modeli, Q3 için VDMOS.

## 1. Resmî Infineon modeli ve (e) seçimi (madde 1)

### Model ve çözücü notları

- **Kütüphane:** `models/infineon/OptiMOS5/OptiMOS5_80V_LTSpice.lib` (sürüm 280225); BSC040N08NS5 ve BSC026N08NS5 içinde.
- **`_L1` seviyesi kullanılamadı.** Sıcaklığa bağlı, ayrıntılı kapasite modeli olan `_L1` bu dönüştürücüde varsayılan
  seçeneklerle ilk anahtarlama kenarlarında yakınsamıyor ("time step too small", düğüm `x?:x1:e_eds3`).
  `cshunt=1e-15` ile yakınsıyor, ama adım ~0,2 ns'ye düşüyor; 3 ms'lik bir koşu saatler sürüyor.
- **`_L0` kullanıldı.** Aynı kütüphanenin level-3 MOS modeli: gövde diyotu (TT 15 ns), anahtarlı Cgd, paket
  indüktansları, Rd/Rs sıcaklık katsayıları. VDMOS hızına yakın koşuyor.
- **Q3 (ideal diyot MOSFET'i) VDMOS'ta kaldı.** Resmî Q3 + davranışsal LM74700 kaynağı başlangıç noktasında takılıyor.
  Q3 yalnız iletimde çalıştığı için etkisi yok.
- **Çözücü seçenekleri arıza sonuçlarını bozuyor; bu yüzden arıza ve dönüş testleri varsayılan seçeneklerle yapıldı.**
  - `cshunt` (VDMOS'ta da denendi): LT1636 CC döngüsü devreye girmiyor.
  - Gevşetilmiş reltol / abstol / vntol: kısa devreden dönüş olmuyor.
  - `_L0` varsayılan seçeneklerle çalıştığı için arıza/dönüş testleri ve nihai "HD" koşuları bu ayarla yapıldı.
  - Kalıcı haldeki etkisi ihmal edilebilir: 48 V/90 W/70 °C'de verim 95,98 ile 95,96 %, Q1 kaybı 0,905 ile 0,909 W.
- **uic soğuk başlangıç fsw'yi kaydırıyor.** LTC3895 modelinde fsw ~%4 düşük oturuyor (90,1 / 95,4 kHz yerine
  94,3 / 99,6). Varyant tablosundaki c/d/e koşuları uic'li prime'lardan; üçü aynı sapmayı taşıdığı için
  karşılaştırma geçerli. Nihai H sayıları uic'siz prime'lardan (fsw 94,3 kHz).

### Varyant tablosu — resmî model

Koşullar Paket 1 ile aynı: Schottky giriş, 24 V prime, 14 ms koşu, sıcak köşe = 70 °C / 20 nH / 0,5 Ω olayı.

| Varyant | η @60 W 20/24/36/48 V (%) | ort. | Q1/Q2 @48/60 (W) | Q1/Q2 @48/90 (W) | VDS Q1/Q2 sıcak 90 W (V) | VDS Q1/Q2 sıcak arıza (V) | IL tepe (A) | ripple maks. (mVpp) |
|---|---|---|---|---|---|---|---|---|
| (c) 24,3 k, RGH 4,7 | 95.72 / 96.02 / 96.33 / 96.27 | **96.09** | 0.63 / 0.14 | 0.85 / 0.22 | 51.3 / 50.2 | 53.1 / 51.5 | 9.08 | 38.5 |
| (d) 24,3 k, RGH 3,3 | 95.73 / 96.03 / 96.35 / 96.28 | **96.10** | 0.60 / 0.15 | 0.79 / 0.24 | 51.3 / 50.2 | 53.2 / 51.5 | 9.07 | 35.6 |
| (e) 24,9 k, RGH 6,8 | 95.68 / 95.97 / 96.24 / 96.13 | **96.01** | 0.72 / 0.12 | 1.00 / 0.20 | 50.9 / 50.3 | 53.2 / 51.6 | 8.99 | 35.7 |
| (e) VDMOS (Paket 1) | 95.82 / 96.15 / 96.57 / 96.62 | 96.29 | 0.48 / 0.07 | 0.73 / 0.12 | – | 53.5 / 56.8 | 8.95 | 38.4 |

(b) BSC026 Q1, kısa yöntemle: 48 V/90 W'ta Q1 1,14 W; fsw düzeltmesiyle ~1,19 W, sınırda. Verimi en düşük; elendi.

**Karar.**
- Resmî modelle üç varyant da kuralları geçiyor. VDS ≤ 56 V; Q1 ≤ 1,0 W; IL ≤ 9,1 A; ripple ≤ 39 mVpp.
- Kural en yüksek verimi seçiyor: d (%96,10) ve c (%96,09). Aradaki 0,01 puan model belirsizliğinin çok altında.
- Gate ölü zamanına göre (bölüm 2) **c'yi seçtim.**
  - c: 27 °C'de +9 ns, 70 °C'de +15 ns (TG kapanış kenarı).
  - d: 70 °C'de en kötü kenar −3 ns.
  - e: −24 / −14 ns.
- **(e) seçimi resmî modelle geçerliliğini kaybetti.** (e)'nin gerekçesi c/d'nin VDS aşmasıydı; bu, ölçeklenmiş
  VDMOS modelinin bir artefaktı çıktı.
- Uygulanan değişiklik: RFREQ1 24,9 k → **24,3 k** (RC0603FR-0724K3L), RGH1 6,8 → **4,7 Ω**, yani paketteki değer.

## 2. RGH taraması (madde 7)

Resmî `_L0`, 48 V / 90 W, (e) frekansı. Kısa soğuk başlangıç yöntemiyle; mutlak kayıplar ~%4 düşük, eğilim geçerli.
Ölü zaman, gate-source gerilimi 3,0 V'u geçtiği anlardan ölçüldü (`LTspice_RevF1/deadtime.py`).
Pozitif = boşluk, negatif = örtüşme.

| RGH | Q1 / Q2 kaybı 27 °C (W) | Q1 / Q2 kaybı 70 °C (W) | Pinde TG↓→BG↑ (ns) | **Gate'te TG↓→BG↑, 27 / 70 °C (ns)** | Gate'te BG↓→TG↑ (ns) | VDS Q1 maks (V) |
|---|---|---|---|---|---|---|
| 5,6 Ω | 0.95 / 0.22 | 0.96 / 0.25 | 38 | −11 / +4,5 | 34 | 49,6 |
| 6,8 Ω | 1.01 / 0.20 | 1.03 / 0.23 | 36 | **−24 / −14** | 36 | 49,4 |
| 8,2 Ω | 1.25 / 0.26 | 1.12 / 0.22 | 33 | −33 / −28 | 37 | 49,7 |
| 10 Ω | **3.33 / 1.16** | **2.90 / 0.99** | 28 | −45 / −40 | 39 | 52,7 |

- **Mekanizma.** LTC3895'in uyarlamalı ölü zamanı TG pinindeki gerilime bakıyor. RGH, TG pini düştükten sonra Q1'in
  gerçek gate'inin boşalmasını geciktiriyor. Pinde ölü zaman hep pozitif (28–38 ns), ama Q1 gate'i Vth'nin üstündeyken
  BG yükseliyor. 10 Ω'da örtüşme 45 ns'ye çıkınca çapraz iletim kaybı patlıyor (Q2 1,16 W).
- **Uçurum 8,2–10 Ω arasında başlıyor.** Kayıp 8,2 Ω'da artmaya başlıyor (Q1+Q2 1,51 W), 10 Ω'da 4,5 W.
- **6,8 Ω'un payı az.** Gate'te zaten 24 ns örtüşüyor; uçuruma ~1,4–3 Ω uzak. MOSFET Vth ve Rg toleransı,
  sürücü direnci ve sıcaklık bu payı yiyebilir.
- **Karar: RGH 4,7 Ω** (varyant c). VDS'yi HF kondansatörleri kontrol ediyor (bölüm 7).
- Nihai H'de gate ölü zamanı, 48 V/90 W:
  - TG↓→BG↑: 27 °C'de **+9,1 ns**, 70 °C'de **+14,8 ns**.
  - BG↓→TG↑: 28,5 ve 39,3 ns.
- Ek seçenek (uygulanmadı, onay gerekir): RGH'ye ters paralel küçük bir Schottky. Kapanış hızlı, açılış yavaş olur;
  turn-off örtüşmesi RGH'den bağımsız hale gelir.

## 3. 8,55 A ile 7,876 A farkı (madde 2)

- **Devre davranışı.** Harici CC döngüsünde Cerr (10 nF) ITH ile ERRN arasında; CCOUT ise RISO + BAT54 üzerinden
  ITH'ye bağlı. Normal çalışmada BAT54 kesimde olduğu için LT1636 açık çevrimde, CCOUT pozitif rayda (4,98 V).
- **Aşırı yük gelince:**
  - LT1636 önce raydan inmek zorunda; bu sürede akımı LTC3895'in kendi tepe sınırı tutuyor (ITH 1,8 V'ta, IL tepe 12,6 A).
  - İlk 0,5 ms'de yük akımı ayrıca çıkış kapasitesinin 0,5 Ω'a boşalmasını içeriyor (ortalama 17,5 A).
- **(e) koşusu.** CCOUT'un 2 V altına inmesi 1,56 ms sürdü (7,0 → 8,56 ms). Arıza 3 ms'ydi (7–10 ms); ölçüm penceresi
  (9–10 ms) akımın hâlâ indiği döneme denk geldi: 9,0–9,5 ms'de 9,00 A, 9,5–10 ms'de 8,09 A, ortalama **8,55 A**.
- **F koşusu.** Aynı geçiş 0,77 ms sürdü. Akım 9,5 ms'de 7,86 A'ya oturdu; 13 ms'lik arızada 12–13 ms ortalaması **7,876 A**.
- **Sonuç.** 7,876 A doğru oturmuş limit; 8,55 A pencere artefaktı. Raydan inme süresinin 0,8–1,6 ms arasında
  değişmesi LT1636 makromodelinin doyumdan çıkışına bağlı. Bu süre boyunca akım 7,9 A'nın üstünde kalıyor; anti-windup
  bunu kısaltır.

## 4. LM74700-Q1 / LM74500-Q1 stok ve alternatifler (madde 3, 12)

**DigiKey, 2026-11-11.** Mouser, Farnell ve TI store otomatik erişimi engelledi; o rakamlar **doğrulanmadı**, elle
bakılmalı. Fiyatlar 1 adet içindir.

| Parça (paket) | Stok | Tedarik | Gelecek | 1 adet |
|---|---|---|---|---|
| LM74700QDBVRQ1 (SOT-23-6 DBV, **kartta**) | 0 | 26 hf | 1.655 adet, tahmini 11-Kas; 1.345 adet 17-Kas-2026 | $2.54 |
| LM74700QDBVTQ1 (DBV) | 0 | 26 hf | backorder | $2.75 |
| LM74700QDDFRQ1 (SOT-23-8 DDF) | 0 | 26 hf | 2.660 adet 19-Kas-2026 | $2.40 |
| **LM74500QDDFRQ1 (yalnız DDF-8)** | 0 | 26 hf | 3.000 adet **09-Mar-2027** | $2.28 |
| **AP74700QW6-7 (Diodes, SOT-26)** | 0 | ? | – | $0.82 |
| LTC4359CMS8 (MSOP-8) | 409 | 10 hf | – | $7.77 |

**LM74500-Q1** (TI SNOSDB7, indirildi: `docs/datasheets/lm74500-q1.pdf`):
- **Yalnız SOT-23-8 (DDF)** paketinde var.
- Pinler: 1 EN, 2 GND, 3 NC, 4 VCAP, 5 SOURCE, 6 GATE, 7 NC, 8 NC. CATHODE pini yok.
- **LM74700 DBV ile pin uyumlu değil.** Paket 1'deki "pin uyumlu yedek" ifadesi yanlıştı ve düzeltildi.
- Ters akım blokajı yok: FET'i sürekli tam açık tutar, yalnız ters polariteye karşı korur.

**Kayıp karşılaştırması** (20 V/90 W, aynı Q3, davranışsal modeller):

| | Q3 kaybı | Verim |
|---|---|---|
| LM74700 (20 mV regülasyon) | 95 mW | %96,99 |
| LM74500 (VGS ~12 V, tam açık) | 43 mW | %97,04 |

Fark +0,05 puan; 60 W'ta daha da küçük.

**Karar: LM74500 birinci seçim yapılmadı.**
- Stok Mart 2027.
- Footprint değişikliği gerekir (DDF-8).
- Ters akım blokajı yok.
- Kazanç ihmal edilebilir.

LM74700 DBV kalıyor. **Pin-pin yedek: AP74700QW6-7.** Diodes DS45004'e göre aynı SOT-26 pinleri, ANODE ±65 V,
20 mV regülasyon; layout değişmeden BOM'a ikinci kaynak olarak yazılabilir. İkisi de 25 Kasım'a kadar gelmezse:
- **Düşük riskli yedek:** DDF-8 footprint. LM74700QDDF (19 Kasım) ya da LM74500 takılabilir. Yeni footprint + sembol;
  ek parça yok.
- **Stokta olan tek ≥65 V seçenek:** LTC4359 (MSOP-8, 100 V). Bloğun yeniden tasarımı gerekir, ~3 kat pahalı.

## 5. Hot-plug: 48 V, kaynak açıkken bağlantı (madde 4)

Model: G konfigürasyonu (VDMOS), kart cansız, 1 µs'de ideal 48 V adımı.
Kablo 1 µH + 50 mΩ ya da 0,5 µH + 20 mΩ; ANODE'da CANODE 22 nF; yük 2,4 Ω.

**Model düzeltmesi.** Temel netlist'te ters polarite elemanıyla giriş kapasiteleri arasında 200 nH'lik bir "Lcable"
var. Kablo L'si ayrıca modellenince bu çift sayım oluyor. RevF1'de Q3 drain'i VIN dökümü ve 33 via ile In2'ye bağlı,
bu yüzden 20 nH alındı.
- 200 nH ile Q3 drain'i 107–132 V'a çıkıyordu (VDMOS'ta çığ yok).
- Mekanizma: LC rezonansında akım ters dönünce LM74700'ün −11 mV'luk hızlı kapatması ters akımı kesiyor.

| Kablo | Kart L | CATHODE kondansatörü | ANODE tepe (65 V) | CATHODE tepe | Q3 VDS tepe (80 V) | VIN tepe | Q1 / Q2 VDS | Kaynak tepe akımı |
|---|---|---|---|---|---|---|---|---|
| 1 µH / 50 mΩ | 20 nH | – | 52,5 V | 60,3 V | 30,0 V | 50,6 V | 50,6 / 49,6 V | 375 A |
| 1 µH / 50 mΩ | 20 nH | 1 µF | 50,7 V | 50,3 V | 20,5 V | 50,6 V | 50,6 / 49,6 V | 376 A |
| 0,5 µH / 20 mΩ | 20 nH | – | **54,4 V** | **67,2 V** | **38,4 V** | 52,3 V | 52,4 / 51,0 V | 559 A |
| 0,5 µH / 20 mΩ | 20 nH | 1 µF | 52,9 V | 52,7 V | 23,7 V | 52,3 V | 52,4 / 51,0 V | 561 A |
| (eski 200 nH, karşılaştırma) | 200 nH | – | 61,2 V | 132 V | 89 V | 54,8 V | – | 521 A |

**Değerlendirme.**
- Gerçekçi kart L'si ile bütün tepeler sınırların altında: ANODE ≤ 54,4 V (sınır 65 V), MOSFET'ler ≤ 52 V (sınır 80 V).
- Model kaynağı ideal ve kart cansız; gerçek bir laboratuvar kaynağının çıkış kapasitesi ve iç direnci 375–560 A'lık
  tepeyi büyük ölçüde sınırlar, ama aşmayı tamamen yok etmez.
- **Önerilen çözüm (uygulanmadı, onay gerekir):** Q3 drain'ine (LM74700 CATHODE) 1 µF / 100 V X7R kondansatör.
  - LM74700 veri sayfası CATHODE'da ≥0,1 µF istiyor. Şu an bu ihtiyacı uzaktaki CIN'ler In2 üzerinden karşılıyor.
  - Bu kondansatörle CATHODE tepesi 67 → 53 V, Q3 VDS 38 → 24 V.
  - Kartta yer var: Q3 drain dökümü, x 108–120, y 97–100.
- **TVS hâlâ önerilmiyor.** 48 V işletim ile 65 V mutlak sınır arasına sığan bir TVS yok.

**Bring-up prosedürü** (kart ilk kez, sonra her demo):
1. Lab kaynağını **kapalıyken** ayarla: 48 V ise seri 60 V / 3 A modu, akım sınırı 1 A ile başla.
2. Kabloyu **kaynak kapalıyken** J1'e bağla. Polariteyi ölçü aleti ile doğrula. Ters bağlantı LM74700 tarafından
   bloke edilir; yine de ilk denemede 1 A sınırı tut.
3. Yük bağlıysa ilk açılışta 2,4 Ω yerine hafif yük (ör. 12 Ω) kullan.
4. Kaynağı aç; VIN, VOUT ve kaynak akımını izle. Beklenen açılma VIN ≈ 16,8 V (RUN).
5. **Kaynak açıkken kablo takıp çıkarma yok.** Bağlantıyı değiştirmeden önce kaynağı kapat, VIN'in 5 V'un altına inmesini bekle.
6. Ölçüm sırasında ANODE (Q3 source) ile toprak arasını ilk hot-plug denemesinde osiloskopla izle. Sınır 65 V,
   beklenen ≤ 55 V.

## 6. RUN filtresi (madde 5 ve 9) ve kısa devre dönüşü

**CRUN1:** 1 nF / 50 V C0G, RUN–GND, **takılı** (madde 9, madde 5'teki DNP isteğinin yerine). Kartta RRUNB1'in yanında.
Model G, VIN 0 → 20 V / 20 ms rampa:

| | RUN = 1,2 V anındaki VIN | İlk anahtarlamadaki VIN | RUN ripple (son 1 ms) |
|---|---|---|---|
| CRUN yok | 16,800 V | 17,93 V | 0,36 Vpp |
| **CRUN 1 nF** | **16,809 V** | 17,95 V | **0,003 Vpp** |

Açılış eşiği değişmiyor: 9 mV'luk fark, 9 µs'lik RC gecikmesinin (130 k ∥ 10 k · 1 nF) 1 V/ms rampadaki karşılığı.

**Kısa devre dönüşü** (H, resmî `_L0`, varsayılan çözücü; 5 mΩ, 7–13 ms):

| Durum | Arızada çıkış akımı | Q1 / Q2 VDS | Dönüş tepesi | %2 bandına dönüş |
|---|---|---|---|---|
| 48 V, 70 °C, sıcak köşe | 5,80 A (LTC3895 foldback) | 51,5 / 49,6 V | **12,335 V (+%2,8)** | 1,42 ms |
| 20 V, 27 °C | 5,78 A | 22,6 / 28,0 V | **12,335 V** | 1,38 ms |
| 0,5 Ω limit, 48 V, 70 °C | **7,876 A** | 51,6 / 49,6 V | 12,211 V | 1,12 ms |

- Kısa devre dönüşü ±%2 bandını ~0,1 V ve ~1 ms aşıyor. Sürekli hal şartı değil, ama raporda belirtilmeli.
- Anti-windup kullanıcı talimatıyla eklenmedi. Muhtemel çözüm: CCOUT'u ~1,5–2 V'a kıstırmak ya da SS'ye bir yol eklemek.
- Kıyas: VDMOS F konfigürasyonunda 12,29–12,35 V; D5E1 paketinde 12,70 V.

## 7. HF kondansatörleri ve RGH1 konumu (madde 8)

**PCB:**
- **CHF2 ve CHF3** (100 nF / 100 V X7R 0805, C2012X7R2A104K125AA): Q1'in solunda, U1 ile Q1 courtyard'ları arasındaki
  2,5 mm'lik şeritte, dikey.
  - VIN pedleri Q1 drain dökümünde.
  - GND pedleri 2 + 1 yeni via ve U1 pin 37'nin GND via'sıyla doğrudan kesintisiz In1'e bağlı.
  - Q1 ve Q2'nin sağ tarafı gate devresiyle dolu olduğu için yalnız bu konum mümkündü.
- **Q1 termal via sayısı** bu yüzden 25 → 12.
- **RGH1**, Q1 gate pinine 1,5 mm mesafeye taşındı (eskisi diyagonal ~2,7 mm). TG via'sı RGH1'in yanında;
  In2 TG rotası SW kesiğinin içinden oraya kısaldı.

**Simülasyon** (resmî `_L0`, varsayılan çözücü, 48 V, 70 °C, sıcak köşe, 0,5 Ω olayı):

| HF yolu | Q1 / Q2 VDS kalıcı hal | Q1 / Q2 VDS olay başlangıcı |
|---|---|---|
| Eski yerleşime karşılık gelen CHF1 (100 nF, ~3 nH) | 50,7 / 56,9 V | 53,0 / **67,0 V** |
| **Yeni: CHF1+2+3 (300 nF, ~1 nH)** | 49,5 / 48,6 V | 51,6 / **49,6 V** |

Yeni yerleşimle Q2 tepesi ~17 V düşüyor. Paket 1 netlist'indeki 0,5 nH'lik CHF1 varsayımı eski kartta gerçekçi
değildi; yeni yerleşim bu varsayıma yaklaştırıyor. (Döngü L'leri elle tahmin; ekstraksiyon yapılmadı.)

## 8. Nihai konfigürasyon H — performans

Resmî `_L0` Q1/Q2; uic'siz prime'lar; fsw 94,3 kHz; 27 °C. 48 V/60 W sonucu 20 ms'lik koşudan
(`RevF1_H2_48V_60W`; zincir prime'dan gelen 2 ms'lik koşu geçişliydi).

| Nokta | Vout (V) | Ripple (mVpp) | η (%) | Q1 / Q2 / Q3 (W) | IL tepe / RMS (A) | VDS Q1 / Q2 (V) |
|---|---|---|---|---|---|---|
| 20 V / 60 W | 11.998 | 25.5 | 97.63 | 0.226 / 0.103 / 0.063 | 5.83 / 5.03 | 21.1 / 24.0 |
| 24 V / 60 W | 11.998 | 21.2 | 97.51 | 0.273 / 0.115 / 0.053 | 5.97 / 5.04 | 25.1 / 27.2 |
| 36 V / 60 W | 11.998 | 32.4 | 97.20 | 0.452 / 0.137 / 0.035 | 6.34 / 5.07 | 37.3 / 37.1 |
| 48 V / 60 W | 11.998 | 37.3 | 96.91 | 0.674 / 0.151 / 0.027 | 6.51 / 5.08 | 49.2 / 48.3 |
| **4 nokta ort.** | | | **97.31** | | | |
| 20 V / 90 W | 11.998 | 22.2 | 96.95 | 0.349 / 0.164 / 0.095 | 8.29 / 7.52 | 21.2 / 25.9 |
| 48 V / 90 W | 11.998 | 32.4 | 96.44 | 0.899 / 0.239 / 0.041 | 8.98 / 7.56 | 49.4 / 48.5 |
| 48 V / 90 W, 70 °C sıcak köşe | 12.025 | 33.6 | 95.98 | 0.905 / 0.275 / 0.041 | 9.01 / 7.58 | 49.9 / 48.9 |

Kurallar: VDS ≤ 64 V ✓, Q1 ≤ 1,2 W ✓ (0,90 W), IL tepe ≤ 12 A ✓ (9,0 A), ripple ≤ 60 mVpp ✓.

**FRA, H (madde 10):**

| Nokta | fc | PM | GM |
|---|---|---|---|
| 20 V / 60 W | 3,67 kHz | 59,0° | > 30 dB (45 kHz'e kadar faz > 0) |
| 20 V / 90 W | 3,43 kHz | 58,5° | > 22 dB |
| 48 V / 90 W | 3,20 kHz | 66,1° | > 15 dB (≥16 kHz noktaları bu koşuda bozuk; 11,3 kHz'te kazanç −15 dB, faz 50°) |

VDMOS'lu G konfigürasyonunda (e değerleri) 90 W: 20 V'ta 3,81 kHz / 66,2°, 48 V'ta 3,23 kHz / 66,3°.

## 9. Soğutucu penceresi ve termal (madde 11)

**Karar: pencere büyütülmedi.**
- SENSEP/VOUT Kelvin hatları U1'den (x ≈ 123,9) RS1'e (x ≈ 161) B.Cu'da tek bir yoldan geçiyor (y = 105,1 / 105,6).
- U1'in altındaki diğer B.Cu sinyalleri (RUN, DRVCC, BG, FREQ, FB) y ≥ 109'da olduğu için Kelvin hatları ancak y < 109'da
  kalabiliyor.
- Kaydırırsam hatlar SW düğümünün ve L1'in altından geçer. In1 artık kesintisiz olsa da akım ölçümü (limit toleransı)
  için risk.
- En iyi ihtimalle pencere 0,37 → ~0,7–1 cm²'ye çıkar. Soğutucu zaten gerekmiyor.

Termal tablo gerçek pencereyle yeniden hesaplandı (`LTspice_RevF1/thermal2.py`; elle model):
- Pencere 0,37 cm²; adaya inen via sayısı 9; toplam 12 termal via.
- Pad: Sil-Pad 900S ≈ 3,9 K·cm²/W → 10,6 K/W.
- Kayıplar H'den.

| Soğutma | θ_yerel | Nokta | Ta 25 °C | Ta 40 °C |
|---|---|---|---|---|
| (a) bakır + 12 via | 38 K/W | 48 V/60 W | 55 °C | 70 °C |
| (a) | | 48 V/90 W | 67 °C | **82 °C** |
| (b) + 0,37 cm² yalıtkan ped + 18 K/W soğutucu (seri yol 54 K/W) | 22,4 K/W | 48 V/90 W | 52 °C | 67 °C |
| (c) + 40 mm fan | 15,8 K/W | 48 V/90 W | 44 °C | 59 °C |

- Paket 1 tablosu ~2 cm² temas varsaymıştı. Gerçek pencereyle soğutucunun katkısı daha küçük
  (Paket 1: 73 → ~60 °C; şimdi 82 → 67 °C).
- Q1 kaybı resmî modelde daha yüksek: 48 V/90 W'ta 0,94 W, VDMOS'ta 0,78 W.
- BSC040 Tj maks 150 °C; **soğutucusuz (a) yeterli**. Fan önerilmez (verimi ~1 puan düşürür).

## 10. ERC / DRC / parity (madde 6)

`tools/revf1_build.sh` şema ve PCB'yi paket dosyalarından baştan üretir, `.kicad_pro`'yu geri yükler ve kontrolleri koşar.

| Kontrol | Sonuç |
|---|---|
| ERC (`--severity-all`) | 0 |
| DRC (`--severity-all`) | 0 ihlal, 0 bağlantısız, 0 parity |
| `.kicad_pro` SHA256 | `aae57006…0f44` (paketle aynı) |
| Kural gevşetme / exclusion | yok |

**rev 2 şema/PCB değişiklikleri:**
- RFREQ1 24,9 k → 24,3 k; RGH1 6,8 → 4,7 Ω (paket değeri).
- Yeni parçalar: CHF2, CHF3 (100 nF / 100 V 0805), CRUN1 (1 nF C0G 0603, takılı).
- RGH1 ve TG via'sı Q1 gate'ine taşındı.
- Görüntüler güncellendi: `docs/paket2_assets/after_*`, `RevF1_schematic.pdf`.

## Onay bekleyen kararlar (rev 2)

1. **Varyant (c) uygulandı:** RFREQ 24,3 k (94,3 kHz), RGH 4,7 Ω, Q1 BSC040.
   - Gerekçe: resmî modelle (e)'nin VDS gerekçesi ortadan kalktı, 6,8 Ω gate'te örtüşüyor.
   - d ile verim farkı 0,01 puan; c'nin gate ölü zamanı her iki sıcaklıkta pozitif.
   - Madde 7'deki "RGH'yi düşür" talimatına dayanarak uyguladım; geri almak `tools/revf1_sch.py`'de iki satır.
2. **Resmî model seviyesi `_L0`.** `_L1` bu devrede pratik değil. `_L0` sıcaklığı yalnız Rd/Rs TC ile
   yansıtıyor (Vth sabit).
3. **Q3 = 1 µF CATHODE kondansatörü önerisi (uygulanmadı):** hot-plug CATHODE tepesini 67 → 53 V'a indiriyor, veri
   sayfası gereğini lokal karşılıyor. Kartta yer var.
4. **LM74700 DBV kalıyor; AP74700QW6-7 BOM'a ikinci kaynak olarak yazılabilir.** LM74500 birinci seçim yapılmadı
   (DDF-8, stok Mart 2027, ters akım blokajı yok).
5. **Kısa devre dönüşü 12,34 V** (+%2,8, ~1 ms). Anti-windup / SS düzenlemesi bekliyor.
6. **Soğutucu penceresi büyütülmedi** (Kelvin hatlarının riski). Soğutucu gereksiz.
7. **Q1 termal via sayısı 12** (HF kondansatörleri yer aldı). Termal hesapta yeterli.
8. **RGH'ye ters paralel Schottky** (kapanış hızı RGH'den bağımsız) — isteğe bağlı iyileştirme, uygulanmadı.
9. **Simülasyon yöntem notu:** LTC3895 ve LT1636 makromodellerinin arıza davranışı çözücü seçeneklerine duyarlı.
   Arıza ve dönüş sonuçları varsayılan seçeneklerle alındı; diğer seçeneklerle alınanlar raporda kullanılmadı.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `LTspice_RevF1/gen7.py` | resmî model bağlantıları, `_L0`, 0 V ölçüm kaynakları |
| `gen9.py`, `gen12.py` | resmî modelle varyant ve RGH çalışması |
| `gen10.py`, `gen11.py` | G (VDMOS): FRA 90 W, kısa devre, hot-plug, RUN, LM74500 |
| `gen13.py` | nihai H |
| `deadtime.py`, `progress.py`, `thermal2.py` | analiz araçları |
| `results.json` | tüm ölçümler |
| `RevF1_HD_*` | H'nin varsayılan çözücüyle arıza ve kalıcı hal kontrolleri |
| `tools/revf1_build.sh` | KiCad yeniden üretimi |

`models/infineon/` (Infineon kütüphanesi) ve `docs/datasheets/` üçüncü taraf dosyaları olduğu için git dışında.
