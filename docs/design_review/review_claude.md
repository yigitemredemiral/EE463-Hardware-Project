# RevD5E1 bağımsız inceleme — Claude

Tarih: 10 Kasım 2026 · Kapsam: Yasin'in RevD5E1 paketi (`EE463_Team_Sharing/`) · **Bu oturumda tasarımda hiçbir değişiklik yapılmadı.**
Bütün simülasyonlar paketin kopyası olan `sim_out/lt/` altında koşuldu; paketteki `.log`/`.cir` dosyalarına dokunulmadı.
"Model" etiketli sayılar LTspice sonucudur, fiziksel ölçüm değildir.

---

## 0. Ortam doğrulaması (Aşama 1)

### 0.1 ERC / DRC (KiCad 10.0.8, paket 10.0.6 ile üretilmişti)

| Kontrol | Paket raporu | Yeniden koşu (`kicad-cli`, `--severity-all`) |
|---|---|---|
| ERC | 0 hata / 0 uyarı | **0 / 0** |
| DRC ihlal | 0 | **0** |
| Bağlanmamış | 0 | **0** |
| Şema parity | 0 | **0** |

- DRC'de yok sayılan 5 kategori paketle aynı (KiCad varsayılanları): courtyard eksik, via merkezlenmemiş iz ucu, tuning profili, footprint filtresi, footprint tipi. Hiçbir exclusion yok.
- Kurallar: clearance 0,15 mm, iz 0,15 mm, via 0,6/0,3 mm, bakır–kenar 0,5 mm.
- Kontrol sonrası `.kicad_pro` SHA256 değeri değişmedi (`aae57006…0f44`).

### 0.2 LTspice: saved-state ve 24 V / 60 W

- LTspice 26.1.1 (paket 26.0.2 ile üretilmişti) `RevD5E1_prime27.state` dosyasını **sorunsuz yükledi**, prime koşusunu yeniden üretmek gerekmedi.
- Koşu 139 s sürdü; .raw dosyası 334 MB (git dışında).

| 24 V / 60 W (12–14 ms) | Paket CSV | Yeniden koşu | Fark |
|---|---:|---:|---:|
| Vout ort. | 11,99812 V | 11,99831 V | +0,2 mV |
| Ripple | 21,63 mVpp | 20,34 mVpp | −1,3 mV |
| Iout | 4,99922 A | 4,99930 A | ≈0 |
| Pin (konnektör) | 62,843 W | 62,850 W | +0,01 % |
| Verim (konnektör) | %95,446 | %95,438 | −0,008 puan |
| IL tepe | 5,672 A | 5,656 A | |
| Q1 kaybı | 0,533 W | 0,534 W | |
| Ters kutup diyot kaybı | 1,032 W | 1,032 W | |

**Sonuç:** Paket sonucu yeniden üretildi. Ripple'daki küçük fark sürüm ve zaman adımı farkından geliyor.

Aynı karşılaştırma 90 W noktaları için de yapıldı:

| Nokta | Vout | Ripple | Iout | Q1 kaybı | Verim |
|---|---:|---:|---:|---:|---:|
| 20 V / 90 W, paket | 11,97297 V | 43,04 mVpp | 7,4831 A | 0,573 W | %94,77 |
| 20 V / 90 W, yeniden | 11,96453 V | 36,98 mVpp | 7,4778 A | 0,573 W | %94,65 |
| 48 V / 90 W, paket | 11,96738 V | 28,78 mVpp | 7,4796 A | 2,298 W | %93,81 |
| 48 V / 90 W, yeniden | 11,96613 V | 30,13 mVpp | 7,4788 A | 2,299 W | %93,82 |

### 0.3 Anahtarlama frekansı

- **Simülasyon:** 290 periyot üzerinden histerezisli kenar sayımıyla 20/24/36/48 V'ta ve 60/90 W'ta hep **145,5 kHz** ölçüldü (aralık 144,6–146,5 kHz).
- **Datasheet:** LTC3895 Rev A s. 10 ve 27'ye göre FREQ pini 20 µA kaynak akımıyla çalışıyor. Frekans için bir formül yok; yalnız Şekil 12 grafiği (RFREQ–f) ve elektriksel tablo noktaları var.
  - Tablo noktaları: 25 k → 105 kHz (tipik), 65 k → 440 kHz (375–505 kHz).
  - 25–65 k arasında doğrusal ara değerle 30,1 k → **≈148 kHz**. Şekil 12'den okunan değer ≈150 kHz.
  - FREQ pin gerilimi: 20 µA × 30,1 k = 0,602 V.
- **Sonuç:** Simülasyon (145,5 kHz) ile datasheet (148–150 kHz) uyumlu. Datasheet 30 k civarı için tolerans vermiyor; 65 k noktasındaki ±%15 bandı esas alınırsa gerçek kartta kabaca 125–170 kHz beklenmeli. Donanımda ölçülmeli.
- Not: Basit Vin/2 eşiğiyle yapılan sayım bazı koşularda SW ringing'i yüzünden 291 kHz veriyor. Bu bir ölçüm hatası; frekans **145,5 kHz**'tir.

### 0.4 PCB görsel incelemesi

Görüntüler `docs/review_assets/` altında:
- `layer_{F,In1,In2,B}.png`, `top_assembly.png`, `render_top.png`
- güç bölgesi yakın çekimleri `zoom_power_{top,in1,in2,b}.png`, giriş bölgesi `zoom_input_top.png`

Bulgular aşağıda d) ve g) maddelerine işlendi. Özet:
1. **Q1 drain pad'inde ve çevresinde hiç via yok.** Pad, F.Cu'da yalnız pad alanı ve dar bir boyunla VIN barına bağlı; ısıyı alt katmanlara taşıyacak yol yok. 2,3 W için kritik.
2. **Sıcak döngü (hot loop) uzun.**
   - CIN1–4'ün GND viaları kartın üst kenarında (y≈95,8 mm), Q2 source viaları ise y≈118 mm'de; arada ≈23 mm var.
   - In1 GND düzlemi, Q1 source / SW / Q2 drain bölgesinin altında yaklaşık 10×9 mm'lik bir dikdörtgenle kesik. Dönüş akımı bu boşluğun etrafından dolaşmak zorunda.
   - CIN6–10 Q1 drain'ine yalnız In2 → CIN1–4 viaları → F.Cu yoluyla ulaşabiliyor. Q1 drain'inde VIN viası olmadığı için yüksek frekansta etkileri sınırlı.
3. **SW düğümü** derli toplu: Q1 S1–3 ve Q2 drain arasında kısa bir F.Cu adacığı var. In1/In2/B.Cu altında kesilmiş. L1 sol pad'ine doğrudan geçiyor.
4. **Şönt Kelvin bağlantıları doğru.** SENSEP ve VOUT ölçüm izleri RS1 padlerinin iç kenarından (x = 164,37 / 165,64 mm) başlıyor, 1,27 mm'lik boşluk içinden çıkıyor. LT6105 kolu (RCSP1/RCSN1) ve U1 SENSE± kolu aynı iç kenar noktalarından besleniyor.
5. **Akım ölçüm izleri** B.Cu'da kartı enlemesine kesiyor ve Q1 ile L1'in altından geçiyor. Arada In1 GND olduğu için kalkanlı, ancak B.Cu GND dökümünü iki parçaya bölüyorlar.

---

## a) Via-in-pad

**Bulgu.** `tools/viainpad_audit.py` ile salt okuma modunda pcbnew API taraması yapıldı. Toplam 191 via var; bakır padlerin içinde **66** via bulundu. Yalnız paste penceresine denk gelen tekrar sayımlar ayıklandı.

| Footprint | Pad / net | Via | Gerekli mi? |
|---|---|---:|---|
| U1 (LTC3895 EP39) | GND | 9 (0,3 mm) | Termal ve GND bağlantısı için via gerekli, fakat **dolgu şart değil**. 6 via paste pencereleriyle çakışıyor. |
| D1, D2 (TO-263 tab) | VIN | 20 + 20 | Tab'ın VIN'e **tek bağlantısı** bu viaların In2'ye geçişi; F.Cu'da tab çevresinde döküm yok. Isı yayma da bunlara bağlı. |
| COUT2 | VOUT 4, GND 6 | 10 | Gerekli değil, pad dışına alınabilir. |
| COUT1 | GND | 6 | Gerekli değil. |
| DVIN1 | VIN | 1 | Gerekli değil. |
| Q1, Q2 | — | 0 | Q1'de via **olmaması** ayrı bir sorun (bkz. d). |

**Değerlendirme.** Reçine dolgu + kapak (IPC-4761 Type VII) yalnız iki yerde gerçekten değer katar: U1 EP'de lehim boşluğunu azaltmak ve D1/D2'de lehim çekilmesini önlemek. İkisinin de dolgusuz alternatifi var.

**Üretici desteklemezse önerilen yol:**
1. **COUT1/2 ve DVIN1:** viaları pad kenarının 0,3–0,5 mm dışına, aynı net dökümüne taşı. İş yükü ≈0,5 saat.
2. **U1 EP:**
   - Seçenek 1: 9 viayı 0,25–0,3 mm delikle bırak, B.Cu tarafını soldermask ile tent'le (kapat). Paste pencerelerini viaların arasına gelecek şekilde yeniden düzenle (6 pencere, ≈%50–60 kapsama).
   - Seçenek 2: viaların sayısını koru, üreticiden "via plugging" (Type VI, kapaksız) iste.
   - ADI datasheet'i via sayısı belirtmiyor; EP lehimlenmeli. İş yükü ≈1 saat.
3. **D1/D2:** e) maddesi uygulanırsa bu iki parça kalkar ve 40 via-in-pad kendiliğinden ortadan kalkar. Kalırlarsa:
   - tab çevresine F.Cu VIN dökümü ekle (tab–pour bağlantısı), viaları tab dışındaki dökümde 20+20 dizi olarak tut;
   - tab altındaki paste'i %60–70'e indir. İş yükü ≈1,5 saat.

**Etkilenen:** `EE463_RevD_Prototype.kicad_pcb`. U1 EP paste düzeni için ayrıca `libraries/footprints/EE463Footprints.pretty/LTC3895_FE38_31_EP39_P0p5.kicad_mod`.

**Öneri:** Üreticinin cevabını beklemeden "dolgusuz" varyantı hazırla. Bedeli küçük, 25 Kasım riskini sıfırlıyor. Dolgu desteği gelirse bile U1 EP için tent'li via kabul edilebilir bir sonuç verir.

---

## b) L1 (XAL1510-333MED) tedarik riski

**Bulgu.**
- DigiKey sayfası parçayı "no longer available at DigiKey" olarak gösteriyor.
- Yasin'in kaydına göre Mouser'da stok 0 ve 2027 tahmini var; LCSC'de stok belirsiz.
- Coilcraft stoku bu oturumda okunamadı (site 403 döndü) — **UNVERIFIED**.

Datasheet değerleri (Coilcraft Doc 947, 05/2026):
- 33 µH ±%20, DCR 18,7 / 20 mΩ, Isat(%30) 16,7 A, Irms 8,6 A (ΔT 20 K) / 12 A (ΔT 40 K)
- Kara deseni: iki pad 3,18 × 13,2 mm, merkezler arası 10,6 mm

**Footprint uyumlu alternatifler:**

| Parça | L | DCR maks | Isat | Irms / IR | Pad | XAL1510 deseniyle uyum |
|---|---|---|---|---|---|---|
| Coilcraft XAL1510-223 | 22 µH | 16 mΩ | 18,7 A (%30) | 10,5 A (20 K) | aynı | **Birebir** (aynı seri) |
| Würth WE-XHMI 74439370330 | 33 µH | 19,8 mΩ | 6,8 A (%10) / 18,15 A (%30) | 8,5 A (ΔT 40 K) | 14,1 × 3,3 mm, 10,6 mm aralık | **Yakın** (pad 0,9 mm uzun) |
| Würth WE-XHMI 74439370220 | 22 µH | 13,75 mΩ | 9,1 A (%10) / 22,35 A (%30) | 8 A (ΔT 40 K) | aynı | Yakın |
| Bourns SRP1513CA-330M | 33 µH | 22,2 mΩ | 19 A | 9 / 14 A | 15 × 6 mm | **Uyumsuz** |
| Vishay IHLP-6767GZ-11 33 µH | 33 µH | 37 mΩ | 9 A (%20) | 10,7 A | farklı | Uyumsuz; Isat yetersiz |

**Değerlendirme.**
- WE-XHMI 33 µH elektriksel olarak en yakın aday. Ancak:
  - %10 düşümde Isat 6,8 A. Bu, 90 W tepe akımında (8,5 A) endüktansın %10'dan fazla düşeceği anlamına geliyor (yumuşak doyma). Sonuç olarak ripple artar ve CC/tepe sınırı payı azalır.
  - IR 8,5 A ΔT 40 K'e göre verilmiş; 7,5 A'da ısınma ≈31 K beklenir. XAL'de aynı akımda ≈15 K.
- 22 µH seçenekleri ripple'ı %50 artırır: 48 V'ta ΔIL ≈2,8 A, tepe ≈8,9 A. Bu yine de LTC3895 ILIM=GND minimum tepe sınırı olan 10,75 A'nın altında, ama yeniden simülasyon gerekir (eğim kompanzasyonu, ripple, kayıp).

**Önerilen çözüm.**
1. L1 footprint'ini XAL1510 ile WE-XHMI 1510'u kapsayan **birleşik bir desene** genişlet: pad 3,3 × 14,1 mm, 10,6 mm aralık. XAL için lehim fileti biraz uzar, bunun bir sakıncası yok. İş yükü ≈0,5 saat; DRC'yi ve L1 altındaki B.Cu/In katmanlarını kontrol et.
2. Sipariş önceliği: Coilcraft doğrudan sample/buy (XAL1510-333MED). Bulunamazsa XAL1510-223MED ya da WE 74439370330. Hangisi alınırsa LTspice'ta L ve DCR güncellenip 3 nokta (20 V/90 W, 48 V/90 W, 24 V/60 W) tekrar koşulmalı. İş yükü ≈1 saat.
3. Stok kontrolü ve sipariş **kullanıcı onayıyla** yapılır.

**Etkilenen:** L1, `Inductor_SMD.pretty/L_Coilcraft_XAL1510-333.kicad_mod` (veya yeni bir ortak footprint), BOM.

---

## c) 90 W'ta akım sınırı çakışması — RSETT 13 k → 11,8 k

**Hesap.** Ilim = 1,25 V × 12k/(Rtop+12k) / (20 × 4 mΩ) = 187,5/(Rtop[kΩ]+12) A

| RSETT1 | Nominal Ilim | ±%3,4 bant (Yasin bütçesi) | 1,6 Ω'da garanti edilen Vout |
|---|---:|---|---:|
| 13 k (mevcut) | 7,500 A | 7,245–7,755 A | **11,59 V (±%2 dışı)** |
| 12,4 k | 7,684 A | 7,423–7,946 A | 11,88 V |
| 12,1 k | 7,780 A | 7,516–8,045 A | 12,0 V (pay ≈0) |
| **11,8 k** | **7,878 A** | **7,610–8,146 A** | **12,0 V** (alt uçta %1,5 pay) |

Not: "Garanti edilen Vout" = min(12 V, Ilim_min × 1,6 Ω).

**Simülasyonla doğrulama** (LTspice 26.1.1, yalnız RsetTop değiştirildi, `sim_out/lt/R11k8_*.cir`):

| Koşu | Vout | Ripple | Iout | LT1636 çıkışı (CCOUT) | DCL1 akımı | Durum |
|---|---:|---:|---:|---:|---:|---|
| 20 V/90 W, 13 k | 11,965 V | 37,0 mVpp | 7,478 A | **0,98 V** | 4,3 µA | **CC döngüsü aktif** |
| 20 V/90 W, 11,8 k | **11,998 V** | **14,3 mVpp** | 7,499 A | 4,98 V (ray) | ≈0 | Gerilim döngüsü |
| 48 V/90 W, 13 k | 11,966 V | 30,1 mVpp | 7,479 A | **1,00 V** | 4,1 µA | **CC döngüsü aktif** |
| 48 V/90 W, 11,8 k | **11,998 V** | 25,6 mVpp | 7,499 A | 4,98 V | ≈0 | Gerilim döngüsü |
| 48 V/70 °C/20 nH, 0,5 Ω limit, 11,8 k | 3,93 V | — | **7,860 A** | 1,12 V | 99 µA | Sınırlıyor |

**Sonuçlar.**
- Kullanıcının tespiti doğrulandı: 13 k ile 1,6 Ω yükte dönüştürücü **akım sınırında** çalışıyor. LT1636 çıkışı 1 V'a inmiş, ITH kıstırılıyor.
- Bunun yan etkisi olarak 20 V/90 W'ta ripple 37 mVpp. 11,8 k ile 14 mVpp'ye düşüyor; CC döngüsünün sınırda "kıpırdaması" ek dalgalanma üretiyor.
- 11,8 k ile 90 W tam regülasyonda ve toleransın alt ucunda bile (7,61 A) 1,6 Ω'da 12 V korunuyor.
- Sıcak köşede limit 7,86 A (nominal hesap 7,88 A).
- **Bedeli:** limit, bonus metnindeki 7,5 A hedefinin %5 üstünde. Bu iki şartın aynı anda tam karşılanması fiziksel olarak mümkün değil: 12 V/1,6 Ω = 7,5 A ve limit = 7,5 A. Limitin yükün biraz üstünde olması kaçınılmaz; seçimin gerekçesi raporda açıkça yazılmalı.
- Daha dengeli bir ara değer olarak **12,1 k** (7,78 A, +%3,7) düşünülebilir. Ancak alt toleransta 1,6 Ω'da pay ≈0; 1,6 Ω yükün kendi toleransı da (sıcakken R artar ve bu lehte olur) hesaba katılmalı. Önerim 11,8 k ile prototipte kalibrasyon.
- **Koşulmayanlar:** 11,8 k ile kısa devre (0,02 Ω) ve dönüş testi, 70 °C 1,6 Ω testi. Kısa devre akımı esas olarak LTC3895 tepe sınırına ve foldback'e bağlı, RSETT'ten etkilenmemesi beklenir; yine de koşulmalı.
- Tepe sınırı kontrolü: ILIM=GND için VSENSE(MAX) 43/50/57 mV, yani 4 mΩ'da 10,75/12,5/14,25 A. 11,8 k ile 48 V/90 W tepe IL 8,49 A, minimum sınırın %79'u. L1 Isat 16,7 A, maksimum tepe sınırının üstünde. ✓

**Etkilenen:** RSETT1 değeri (RT0603BRD0711K8L veya eşdeğeri 0,1 %), BOM, şema değeri, `Calculations/Current_Limit_Tolerance_TR.md`. PCB geometrisi değişmez. İş yükü ≈0,5 saat; simülasyonlar dahil ≈1,5 saat.

---

## d) Q1 kaybı (48 V / 90 W'ta 2,3 W) ve termal

**Kayıp yapısı (model, LTspice 26.1.1, 48 V):**

| Nokta | P_Q1 | Açılma enerjisi | Kapanma enerjisi | İletim (I²R·D) |
|---|---:|---:|---:|---:|
| 48 V/90 W | 2,30 W | 6,1 µJ | 9,6 µJ | ≈0,04 W |
| 48 V/60 W | 1,99 W | 4,2 µJ | 9,7 µJ | ≈0,02 W |
| 24 V/60 W | 0,55 W | 1,8 µJ | 1,8 µJ | — |

**Yorum.**
- Q1 kaybının **≈%98'i anahtarlama kaynaklı** ve yükten büyük ölçüde bağımsız (60 W → 90 W'ta yalnız %15 artıyor). Gerilimle kabaca V² ölçekleniyor.
- Açılmadaki enerji Q2'nin Qoss/Qrr'sini ve Q1'in Coss'unu boşaltmasıyla uyumlu: BSC026N08NS5 için Qoss 88 nC × 48 V ≈ 4,2 µJ mertebesi.
- Modelde kapanma enerjisi yükten bağımsız (≈9,6 µJ). Bu fiziksel olarak şüpheli: I·V örtüşmesi olsaydı yükle ölçeklenirdi.
- Paketteki MOSFET modeli Infineon'un resmi modeli değil, genel bir VDMOS (`Kp=70`, `Cgdmax=1.18n` vb.). **Bu sayıların modele duyarlılığı yüksek; resmi Infineon OptiMOS5 modeliyle tekrar kontrol edilmeli.**

**Mevcut termal durum.**
- Q1 drain pad'i 4,5 × 4,7 mm. Pad'de **sıfır via** var; F.Cu'da yalnız VIN barına bağlanan ≈2 mm'lik bir boyun var.
- Datasheet'teki 50 K/W değeri 6 cm² 70 µm bakır içindir; buradaki gerçek θJA bunun çok üstünde olabilir. Tahminen 70+ K/W, ölçülmedi.
- 2,3 W × 70 K/W ≈ 160 K artış → **sınır dışı.**

**Seçenekler ve VDS tepesine etkileri:**

| Seçenek | Q1 kaybına etkisi (tahmin) | VDS tepesine etkisi | PCB etkisi | İş yükü |
|---|---|---|---|---|
| **1. PCB soğutması:** Q1 drain çevresine F.Cu VIN dökümü (≥4–6 cm²), pad dışına 12–20 adet 0,3 mm termal via ile In2 VIN düzlemine bağlantı, B.Cu'da Q1 altına VIN adacığı (akım ölçüm izleri yeniden yönlendirilir) | Kayıp değişmez, θJA ≈35–45 K/W'a iner → ΔT ≈80–100 K | Yok. VIN viaları Q1 drain'ine yaklaştıkça döngü L azalır, bu da lehte | Yerleşim | 3–4 saat |
| **2. fsw düşürme:** RFREQ ≈24–25 k (≈100–105 kHz) | Anahtarlama ağırlıklı olduğu için ∝f: 2,30 → ≈1,6 W | Yok (geçiş hızı değişmez) | Yalnız değer değişikliği | 0,5 saat + simülasyon |
| **3. Q1 için daha küçük kristalli MOSFET:** BSC040N08NS5 (aynı SuperSO8, 80 V; Qgd 9,3 nC; Qsw 15 nC; Qoss 52 nC; 4,0 mΩ maks). Q2 BSC026 olarak kalır. | Qsw/Qoss oranıyla ≈%35–45 düşüş → ≈1,3–1,5 W. 20 V/90 W'ta iletim kaybı ≈0,16 W (D=0,6, sıcak) | Daha hızlı dv/dt ile aynı RGH'de ringing biraz artabilir; Q1 Coss'u küçüldüğü için dönüşte enerji azalır. **Simülasyonla kontrol şart.** | Footprint aynı | 1 saat + model |
| **4. RGH düşürme / bölünmüş gate:** RGH 4,7 → 3,3 Ω (Yasin'in sıradaki adayı), veya açılmada 4,7 Ω + kapanmada BAT54/1N4148W üzerinden ≈1 Ω | 4,7 → 2,2 Ω'da paket verisi 2,30 → 1,03 W. 3,3 Ω için ≈1,6 W bekleniyor (koşulmadı) | **Ters yönde:** 2,2 Ω'da sıcak 20 nH köşesinde VDS 70 V'a çıkıyordu (64 V hedefi aşılır). Bölünmüş gate'te Q1 kapanma di/dt'si artar ve Q1 VDS tepesi yükselir | Diyot için 1 SOD-323 yeri | 1–2 saat |
| **5. Sıcak döngü L'sini küçültme** (bkz. g-2) | Doğrudan değil; ancak düşük L, RGH'yi düşürmeye izin verir | **En etkili VDS çözümü.** VDS taşması ≈ L·di/dt. | Yerleşim | 3–5 saat |

**Öneri.** Birden fazla seçenek birlikte uygulanmalı:
- **2 + 1 + 3 birlikte:** ≈100 kHz, BSC040N08NS5 (Q1) ve termal döküm/via. Model kaybı ≈1 W'a, Tj artışı ≈40 K'e iner. RGH 4,7 Ω kalabilir, VDS payı korunur.
- Hepsi E1 regresyon simülasyonu ister: 3 nominal nokta + sıcak limit/kısa devre.
- fsw 100 kHz'e düşerse çıkış ripple'ı ≈×1,45 (hâlâ <60 mVpp) ve ITH/kompanzasyon sınırı yeniden kontrol edilmeli. Geçiş frekansı fsw/10'un altında kalmalı.

**Etkilenen:** RFREQ1, Q1 (BOM + LTspice modeli), RGH1, PCB'de Q1 çevresi.

---

## e) Ters polarite: seri Schottky yerine ideal diyot

**Mevcut kayıp** (2× RBQ20NS100ATL paralel; model 60 W; LTspice 26.1.1):

| Vin | Iin | P_Schottky | η (model) |
|---|---:|---:|---:|
| 20 V | 3,14 A | 1,28 W | %95,38 |
| 24 V | 2,62 A | 1,03 W | %95,44 |
| 36 V | 1,75 A | 0,65 W | %94,96 |
| 48 V | 1,34 A | 0,48 W | %93,38 |
| **Ortalama** | | | **%94,79 → Bη ≈ +14,8** |

**İdeal diyotla tahmin:** toplam yol 6 mΩ (MOSFET + iz) + kontrolcü IQ.
- 20 V'ta ≈0,065 W, 48 V'ta ≈0,025 W.
- η: %97,25 / 96,96 / 95,91 / 94,05 → **ortalama %96,04 (+1,25 puan) → Bη ≈ +16,0.**
- Ayrıca D1/D2'nin 2 W'a varan ısısı (20 V/90 W) ve 40 via-in-pad ortadan kalkar.

**Kontrolcü seçimi — önemli bulgu:**

| Kontrolcü | Ters giriş | Uygunluk |
|---|---|---|
| **LTC4359** (ayna kaynak, Rev D) | **−40 V** (IN/SOURCE mutlak maks) | 48 V çalışmayı destekliyor (4–80 V), ancak **48 V'luk ters bağlantıya dayanmaz.** Resmi datasheet'le teyit edilmeli. Ters polarite testi −20 V ile sınırlanırsa olur, ama riskli. |
| **TI LM74700-Q1** | ±65 V (ANODE–GND) | 3,2–65 V çalışma, IQ 80 µA, SOT-23-6, 20 mV regülasyon. OVLO 54 V'a karşı payı 11 V. **Önerim bu.** |
| TI LM74610-Q1 | 45 V | Yetersiz. |
| P-kanal yüksek taraf + zener gate clamp (80–100 V P-FET) | VDS sınırına kadar | Kontrolcüsüz, kayıp ≈0,1–0,2 W. Basit ama ideal diyottan biraz kötü. |

**PCB değişikliği.**
- D1, D2 (2× TO-263) kaldırılır.
- Yerlerine 1× SuperSO8 80 V N-FET eklenir (ör. BSC026N08NS5, BOM'da zaten var), artı LM74700 (SOT-23-6), VCAP kondansatörü (0,1 µF) ve gerekirse giriş TVS'i.
- Şema: VIN_RAW → FET (source = VIN_RAW, drain = VIN) → VIN. DVIN1 clamp kalır.
- Yerleşim: giriş bölgesi (J1, D1, D2 alanı) yeniden düzenlenir; boşalan alan Q1 termal dökümüne yarar.
- LTspice: LM74700 için TI PSpice modeli (LTspice'a uyarlanması gerekir) ya da davranışsal model; ters polarite ve açılış testleri tekrar koşulur.
- **İş yükü:** şema 1 saat + yerleşim 3–4 saat + simülasyon 2 saat ≈ 6–7 saat.

**Risk:** 25 Kasım'a 15 gün var; parça temini (LM74700-Q1 yaygın) ve modelleme süresi takvime sığar. Ancak a), c), d) ile birlikte en büyük iş kalemi bu.

---

## f) Doğrulama eksikleri (RevD5E1 için koşulmamış)

| # | Test | Durum | Önerilen yöntem |
|---|---|---|---|
| 1 | 4 noktada 60 W verim (20/24/36/48 V) | **Bu oturumda modelde koşuldu**: %95,38 / 95,44 / 94,96 / 93,38, ort. %94,79 (LTspice 26.1.1). Paket bunu E1 için içermiyordu. Çekirdek kaybı ve özısınma yok. | Donanımda J1/J2 eşzamanlı V/I. |
| 2 | FRA (4 giriş) | E1 için yok; eski D5 PM 50,7–62,2° E1'e taşınamaz. | `.cir` içindeki `@LOOP` ile 20/24/36/48 V, 60 W ve 90 W (11,8 k ile 90 W'ta CC devre dışı). |
| 3 | Kompanzasyon A/B (line/load) | Yalnız eski D5 sonuçları var. | A (10k/4,7n/100p) ve C (10k/22n/470p) E1'de; load 2,4↔1,6 Ω, line 20↔48 V. |
| 4 | Ters polarite | E1 için yok. | −20 V ve −48 V; e) seçilirse yeni devreyle. |
| 5 | Cold-start | Hiç yok (prime koşuları cold-start değil). | 0'dan 16 ms, SS = 100 nF; 20 V ve 48 V. |
| 6 | **Akım sınırlı lab kaynağıyla açılış** | Hiç yok. | Kaynak modeli: 20/24 V paralel 6 A, 36/48 V seri 3 A, CC sınırlı. **36 V/90 W kritik:** kalıcı halde Iin ≈2,66 A; açılışta çıkış kondansatörü şarjı (660 µF × 12 V / 8 ms ≈ 1 A) ile Iin ≈ (90+12)/0,94/36 ≈ **3,0 A → sınırda.** Kaynak CC'ye girerse Vin çöker ve RUN UVLO (≈16,8 V) hiccup'ı oluşabilir. 20 V/90 W'ta açılış ≈5,4 A < 6 A. |
| 7 | 11,8 k ile kısa devre ve dönüş | Koşulmadı. | 48 V/70 °C/20 nH, 0,02 Ω. |
| 8 | Sıcak kısa devre dönüşü 12,70 V tepe | Açık. | g-6'daki anti-windup önerisiyle karşılaştırma. |
| 9 | Resmi Infineon modeliyle Q1/Q2 kaybı | Yok. | 48 V/90 W ve 48 V/60 W. |
| 10 | Seçilecek L1 alternatifiyle 3 nokta | — | b) kararından sonra. |

---

## g) Kendi incelememde bulduğum diğer konular

**Pin bağlantıları ve LTC3895 ayarları** (netlist `kicad-cli sch export netlist` ile çıkarıldı). Datasheet Rev A'ya göre kontrol edildi:

| Pin | Bağlantı | Datasheet anlamı | Durum |
|---|---|---|---|
| VPRG (2) | Boşta | Ayarlanabilir, VFB = 0,8 V | ✓ |
| MODE (8) | INTVCC | Forced continuous | ✓ (ripple için doğru) |
| ILIM (37) | GND | 43/50/57 mV → 10,75–14,25 A tepe | ✓ |
| DRVSET (18) | INTVCC | DRVCC = 10 V | ✓ |
| DRVUV (19) | INTVCC | DRVCC UVLO 7,5 V; EXTVCC devralma 7,7 V | ✓ (VOUT 12 V) |
| CPUMP_EN (10) | INTVCC | Şarj pompası açık (%100 duty) | ✓ (zararsız) |
| PLLIN (13) | GND | Senkronizasyon yok | ✓ |
| PHASMD (36) | INTVCC | Yalnız CLKOUT fazı | ✓ |
| NDRV (28) | DRVCC | NDRV LDO devre dışı (datasheet önerisi) | ✓ |
| EXTVCC (32) | VOUT | Mutlak maks 14 V; "VIN'den yüksek olmamalı" | ⚠ bkz. 4 |
| Q1/Q2 | S1–3, G4, D5 | | ✓ |
| D1/D2 | Anotlar VIN_RAW, tab VIN | | ✓ |
| DCL1 | A = ITH, K = CLAMPK | | ✓ |
| RFB | 140 k / 10 k → 12,0 V | | ✓ |
| RUN | 130 k / 10 k → açılma 16,8 V (1,1–1,3 V → 15,4–18,2 V) | | ✓ |

**Bulgular:**

1. **(Yüksek) Q1 termal yolu yok.** Ayrıntı d) maddesinde.

2. **(Yüksek) Sıcak döngü yerleşimi.**
   - CIN1–4'ün GND dönüşü ile Q2 source viaları arasında ≈23 mm var. In1 GND, SW bölgesi altında ≈10×9 mm kesik ve bu kesik Q1 source ile Q2 drain'inin altını da kapsıyor; döngünün dönüş akımı tam buradan akmalı.
   - CIN6–10, Q1 drain'ine yalnız In2 → CIN1–4 viaları üzerinden ulaşıyor.
   - Modelde Lloop 5 nH nominal, 20 nH köşe varsayımı var. Mevcut geometrinin nominal varsayımı karşılaması zor görünüyor (ekstraksiyon yapılmadı).
   - **Öneri:**
     - 2–4 adet 0805/1206 100 V X7R (0,1–1 µF) kondansatörü Q1 drain ile Q2 source arasına, MOSFET'lere bitişik yerleştir.
     - In1 kesiğini yalnız SW pad + L1 SW pad'i altına daralt; Q1 source ve Q2 source altındaki dönüş yolunu sürekli tut.
     - Q1 drain'ine VIN viaları ekle (pad dışı, d-1 ile aynı iş).
     - İş yükü d-1 ile birlikte 4–5 saat. VDS tepesini düşürerek RGH'nin indirilmesine izin verir.

3. **(Orta) 1,6 Ω'da CC döngüsünün ripple'a katkısı.** 13 k ile ripple 37 mVpp, 11,8 k ile 14 mVpp (20 V). Sınır şartı geçiliyor ama c) ile birlikte kendiliğinden düzelir.

4. **(Düşük) EXTVCC = VOUT ve "EXTVCC ≤ VIN" kuralı.**
   - Giriş kesildiğinde ya da yavaş düştüğünde VOUT kondansatörleri VIN'den yüksek kalabilir; kısa bir süre EXTVCC > VIN olabilir.
   - ADI uygulamalarında EXTVCC = VOUT yaygın. Risk düşük, ancak bring-up'ta giriş kapatma dalga şekli bakılmalı. Gerekirse EXTVCC'ye seri 1 A Schottky eklenebilir (yeni parça).

5. **(Düşük) OVLO payı.**
   - 825 k / 18,7 k ile OVLO 1,1/1,2/1,3 V → 49,6 / 54,1 / 58,6 V.
   - En kötü durumda 48 V nominale (Schottky sonrası ≈47,5 V) karşı yalnız ≈2 V pay var. Kaynak aşımında ya da e) uygulanınca (düşüm ≈0 V) pay ≈1,6 V'a iner.
   - Öneri: ROVT 825 k → 866 k (OVLO min ≈52 V). Değer değişikliği, 0,25 saat.

6. **(Orta) Kısa devre dönüşü tepe 12,70 V.**
   - CC döngüsü ITH'yi kıstırırken LTC3895 gerilim hata yükselteci doymada kalıyor; yük kalkınca ITH yüksek kaldığı için aşma oluşuyor.
   - Aday anti-windup: SS pinini CC sınırı sırasında aşağı çekmek (ör. SS → BAT54 → CCOUT ya da ITH clamp düğümü). Böylece yük kalktığında çıkış soft-start rampasıyla döner.
   - 1 diyot + 1 direnç. **Simülasyonla doğrulanmadan önerilmez**; normal açılışı ve CC regülasyonunu bozmadığı gösterilmeli. İş yükü 2–3 saat.

7. **(Düşük) U1 EP paste pencereleri 9 viadan 6'sının üstüne denk geliyor** → lehim çekilmesi riski. Ayrıntı a) maddesinde.

8. **(Düşük) D1/D2 tab'ları F.Cu'da yalnız pad.** VIN'e bağlantı tamamen via-in-pad üzerinden. a) ya da e) ile çözülür.

9. **(Bilgi) MOSFET modeli.** Yasin'in netlisti Infineon'un resmi modeli yerine genel VDMOS kullanıyor. Q1 kaybı ve VDS sonuçları buna duyarlı (bkz. d).

10. **(Bilgi) LTC3895 iç kaybı.** EXTVCC devreye girene kadar (VOUT < 7,7 V; kısa devre dahil) DRVCC, VIN'den lineer besleniyor:
    - (48 − 10) V × (2 × 74 nC × 145 kHz ≈ 21,5 mA) ≈ 0,82 W
    - θJA 28 K/W ile ≈23 K artış
    - Sürekli kısa devrede kabul edilebilir, ancak EP lehim kalitesine bağlı (bkz. a).

11. **(Bilgi) Yerleşim — akım ölçüm izleri B.Cu'da** kartı enlemesine kesiyor. In1 kalkanı nedeniyle gürültü riski düşük; termal açıdan d-1 uygulanırken yeniden yönlendirilmesi B.Cu dökümünü bütünleştirir.

12. **(Bilgi) Dosya adı.** Şartname dosyası `docs/proje/EE463 Hardware Project.md` (boşluklu).

---

## Önceliklendirilmiş öneri listesi (onay bekliyor)

| Sıra | Değişiklik | Tür | Tahmini iş |
|---|---|---|---|
| 1 | RSETT1 13 k → 11,8 k (c) | Değer | 1,5 saat (simülasyonla) |
| 2 | Q1 termal döküm + VIN viaları + sıcak döngü kapasitörleri + In1 kesiğinin daraltılması (d-1, g-2) | Yerleşim | 5–6 saat |
| 3 | Via-in-pad'siz varyant (a) | Yerleşim | 2–3 saat |
| 4 | fsw ≈100 kHz ve/veya Q1 = BSC040N08NS5 (d-2/3) | Değer / BOM | 2–3 saat + simülasyon |
| 5 | İdeal diyot LM74700-Q1 + N-FET (e) | Şema + yerleşim | 6–7 saat |
| 6 | L1 birleşik footprint (b) | Footprint | 1 saat |
| 7 | ROVT 866 k (g-5) | Değer | 0,25 saat |
| 8 | Anti-windup çalışması (g-6) | Simülasyon önce | 2–3 saat |
| 9 | f) maddesindeki simülasyonlar (FRA, A/B, cold-start, kaynak-sınırlı açılış) | Doğrulama | 4–6 saat CPU + analiz |

Toplam ≈25–33 saat; 25 Kasım'a kadar sığar. Gerber/Drill ancak 1–3 ve seçilen diğer maddeler kapandıktan ve ERC/DRC/parity 0 sağlandıktan sonra üretilmeli.

**Hiçbir sipariş ya da üreticiye gönderim yapılmadı.**

---

### Ek: Bu oturumdaki dosyalar
- `tools/ltraw_measure.py` — LTspice ikili .raw okuyucu ve ölçümler (Vout, ripple, verim, kayıplar, fsw)
- `tools/fsw_measure.py` — histerezisli fsw ölçümü
- `tools/sw_edges.py` — SW kenar zamanlaması ve Q1 açılma/kapanma enerjisi
- `tools/viainpad_audit.py`, `tools/pcb_probe.py` — pcbnew salt okuma denetimleri (kart kaydedilmez)
- `docs/review_assets/*.png` — katman görüntüleri
- Simülasyon kopyaları ve .raw dosyaları: `sim_out/` (git dışı)
