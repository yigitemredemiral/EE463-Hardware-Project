# RevF1 — Paket 2: şema ve PCB yerleşimi

Tarih: 2026-11-11. KiCad 10.0.8 (kicad-cli + pcbnew python). Proje: `KiCad_RevF1/` (paketin kopyası; dosya adları
`EE463_RevD_Prototype.*` olarak korundu ki şema instance yolları ve footprint path'leri geçerli kalsın).
Paketteki `EE463_Team_Sharing/KiCad/` dokunulmadı.

Bütün düzenlemeler betikle yapıldı ve tekrarlanabilir:
- `tools/revf1_sch.py` — şema (paket şemasından başlar, her değişiklik assert edilir).
- `tools/revf1_pcb.py` — PCB (paket kartından başlar). Log: `sim_out/revf1_pcb_log.txt` (git dışı).

**Doğrulama (2026-11-11, orijinal `.kicad_pro` ile):**

| Kontrol | Sonuç |
|---|---|
| ERC (`--severity-all`) | **0** hata / 0 uyarı |
| DRC (`--severity-all`) | **0** ihlal |
| Bağlantısız | **0** |
| Şema–PCB parity | **0** |
| Kural gevşetme / exclusion | yok (`drc_exclusions` boş; kurallar paketle aynı: 0,15/0,15 mm, via 0,6/0,3) |
| `.kicad_pro` SHA256 | `aae57006…0f44` (paketle aynı) |

`.kicad_pro` notu: pcbnew `SaveBoard` dosyayı yeniden yazdı (teardrop ve net_settings'te kozmetik alanlar, kural değeri
değişmedi). Paketin baytları geri yüklendi; DRC/ERC geri yüklenmiş dosyayla tekrar koşuldu.

## 1. Şema değişiklikleri

| Ref | Eski | Yeni | Kaynak |
|---|---|---|---|
| RFREQ1 | 30,1 k | ~~24,9 k~~ → **24,3 k** (RC0603FR-0724K3L) | rev 2: varyant (c), resmî Infineon modeli (paket2b) |
| Q1 | BSC026N08NS5 | **BSC040N08NS5** (BSC040N08NS5ATMA1), aynı footprint | varyant (e) |
| RGH1 | 4,7 Ω | ~~6,8 Ω~~ → **4,7 Ω (değişmedi)** | rev 2: varyant (c); 6,8 Ω gate'te örtüşüyor (paket2b) |
| CHF2, CHF3 | – | **100 n / 100 V X7R 0805** (C2012X7R2A104K125AA), Q1 drain'inin solunda | rev 2, madde 8 |
| CRUN1 | – | **1 n / 50 V C0G 0603** (GRM1885C1H102JA01D), RUN–GND, takılı | rev 2, madde 9 |
| RITH1 / CITH1 | 10 k / 22 n | **8,2 k / 27 n C0G** (RC0603FR-078K2L / GRM21B5C1H273JA01L) | FRA komp. A |
| RSETT1 | 13 k 0,1 % | **11,8 k 0,1 %** (RT0603BRD0711K8L) | onaylı |
| ROVB1 | 18,7 k | **17,4 k** (RC0603FR-0717K4L) | onaylı |
| CSS1 | 100 n | 100 n (değişmedi) | başlangıç testleri |
| D1, D2 | RBQ20NS100A ×2 | **silindi** | onaylı |
| U5, Q3, CVCAP1, CANODE1 | – | **LM74700-Q1 + BSC026N08NS5 + 100 n + 22 n** | ideal diyot |
| L1 | footprint XAL1510 | **EE463Footprints:L_XAL1510_WE-XHMI1510_Dual** | onaylı |
| J3 | – | **1×2 pin header, DNP**, VOUT/GND (fan) | madde 2f |

- İdeal diyot bloğu, eski D1/D2'nin yerine sayfa 1 "POWER PATH" bölümüne çizildi. Q3 source = VIN_RAW, drain = VIN.
  U5 pinleri: ANODE = VIN_RAW, CATHODE = VIN, GATE = IDGATE, VCAP = IDVCAP, EN = VIN_RAW. Açıklama notu bloğun yanında.
- LM74700-Q1 sembolü KiCad 10 resmî kütüphanesinden (Power_Management:LM74700) kopyalanıp `EE463.kicad_sym`'e eklendi.
- Notlar güncellendi: başlık RevF1, rev "F1 PROTOTYPE", OVLO 58,1 V, limit 7,88 A, kompanzasyon notu.
- Kütüphanelere eklenen footprint'ler: `Package_TO_SOT_SMD:SOT-23-6`,
  `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` (KiCad 10 resmî kütüphaneden kopya + 3D model),
  `EE463Footprints:L_XAL1510_WE-XHMI1510_Dual`. `fp-lib-table`'a pin header kütüphanesi eklendi.

Şema PDF: `docs/paket2_assets/RevF1_schematic.pdf`.

## 2. PCB değişiklikleri

> **rev 2 (2026-11-12) özeti** (ayrıntı `docs/paket2b_ek_sonuclar.md`):
> - CHF2/CHF3, Q1'in solunda U1 ile Q1 courtyard'ları arasında dikey 0805 olarak yerleştirildi. VIN pedleri Q1 drain
>   dökümünde; GND pedleri 2 + 1 yeni via ve U1 pin 37'nin GND via'sıyla kesintisiz In1'e bağlı.
> - Bu yüzden Q1 termal via sayısı 25 → **12**.
> - RGH1, Q1 gate pinine 1,5 mm mesafeye (141,45, 107,5) taşındı. TG via'sı (143,2, 107,5) RGH1'in yanında;
>   In2 TG rotası oraya kısaldı. Eski TG via'sı (142,1, 102,4) kaldırıldı.
> - CRUN1, RRUNB1'in soluna kondu (RUN–GND).
> - Bütün düzenleme `tools/revf1_build.sh` ile paket dosyalarından baştan üretiliyor.


Kart boyutu **değişmedi (90 × 65 mm, 4 katman)**. D1/D2'nin iki TO-263'ü kalkınca giriş bölgesinde yer açıldı; büyütmeye
gerek kalmadı.

### a) Q1 termal
- F.Cu'da Q1 drain'ini CIN1–4 VIN pedlerine bağlayan **VIN bakır dökümü** eklendi (124,6–139,6 × 98,3–106,9 mm, öncelik 2).
- **25 termal via** (0,6/0,3 mm, ped dışında) eklendi: CIN pedleri ile Q1 tab'ları arasında bir sıra, Q1'in solunda iki sütun.
  In2 VIN düzlemine ve alt yüzdeki VIN adasına bağlanırlar.
- Q1 sağ tarafı GH/TG/RGSH hatlarıyla dolu olduğu için oraya via konamadı.
- In2'deki **TG hattı Q1 drain'inin altından çıkarıldı**: eskiden VIN düzlemini Q1'in tam altında kesiyordu. Yeni rota
  In2 SW kesiğinin içinden geçiyor (132,5,115,7 → 132,5,109,2 → 143,3,109,2 → 143,3,103,6 → 142,1,102,4).
  TG zaten SW referanslı olduğundan bu, gürültü açısından da daha uygun.

### b) Sıcak döngü
- **In1.Cu GND'deki 134–144 × 106,5–115,5 mm kesik kapatıldı.** In1 artık Q1/Q2/SW altında kesintisiz. CIN1–4 → Q1 →
  Q2 → Q2 source via'ları (y ≈ 118,4–119,4) → In1 → CIN GND via'ları (y ≈ 95,9) dönüş yolu, F.Cu'nun ~0,2 mm altından
  doğrudan geçiyor; eskiden kesiğin etrafından dolaşıyordu.
- Giriş seramikleri yerinde bırakıldı. CIN1–4 VIN pedleri Q1 drain tab'larına zaten ~2,3 mm uzakta, CHF1 Q1 yanında.
  CIN6–10 sırası Q2 source'a 6,7 mm uzakta; yakına çekmek RFREQ/GL/TP7 bölgesinin baştan yerleşimini gerektiriyordu,
  yapılmadı (onay bekleyen kararlar).
- SW bakırı büyütülmedi. In2 ve B.Cu'daki SW altı kesikler korundu. In1'in SW altında GND olması, L1 pedi dahil
  ~70 mm² SW alanı için ~14 pF ek kapasite getiriyor (Coss ~1 nF yanında ihmal edilebilir).

### c) İdeal diyot bloğu (giriş bölgesi)
- **Q3** (TDSON-8) (113, 104) mm, rot 90: drain üstte, source/gate altta. **U5** (SOT-23-6) (117,5, 111), rot 90.
  CVCAP1 (114,7, 112,6), CANODE1 (109,6, 112,4).
- VIN_RAW: J1 pin 1'den Q3 source'larına F.Cu bakır dökümü (L şeklinde, öncelik 3). Eski 2,5 mm VIN_RAW izleri silindi.
- VIN: Q3 drain'i F.Cu + B.Cu VIN dökümü ve **33 via** ile In2 VIN düzlemine bağlanıyor (eski D1/D2 tab'larındaki 40
  via-in-pad'in yerine). ROVT1/TP2'ye giden mevcut VIN izleri bu döküme bağlı.
- U5 bağlantıları kısa F.Cu izleriyle: GATE → Q3 gate, CATHODE → VIN dökümü, ANODE ve EN → VIN_RAW dökümü
  (EN SOT-23'ün çaprazında olduğu için alttan dolaşıyor), VCAP → CVCAP1, GND → via.

### d) Çift L1 footprint
- Pedler 3,18 × 13,2 → **3,3 × 14,1 mm**, aralık 10,6 mm (XAL1510 ve WE-XHMI 1510 land pattern'lerinin zarfı).
  Pedler arasında via yok. Courtyard ve 3D model XAL1510'unki.

### e) Dolgusuz via-in-pad çözümü
- Paketteki 104 via-in-pad → **4** (yalnız U1 EP, bilerek).
- COUT1 GND (6), COUT2 VOUT (4) + GND (6): via'lar ped kenarının 0,4–0,6 mm dışına alındı, 0,8 mm izle pede bağlandı.
- DVIN1 VIN (1): ped dışına alındı.
- D1/D2 tab'larındaki 40 via: D1/D2 ile birlikte silindi.
- **U1 EP:** 9 via → **4 via** (x = 128,0; y = 110,2 / 111,4 / 112,6 / 113,8). Paste pencereleri 6 × 0,8 × 1,4 mm,
  x = ±0,85'e taşındı (EP kaplaması %51,6). Ortada 0,9 mm paste'siz sütun kaldı; via'lar paste ile çakışmıyor,
  dolgusuz üretilebilir. Footprint açıklaması da güncellendi.

### f) Soğutucu bölgesi ve fan
- Q1'in arkasında **B.Cu VIN adası** (132,4–141,2 × 99,4–104,5 mm), 0,3 mm içeriden **B.Mask açıklığı** ve
  "HEATSINK AREA = VIN! insulating pad" alt silk yazısı var. Termal via'ların bir kısmı bu adaya iner.
- B.Cu'daki SENSEP/VOUT Kelvin hatları (y = 105,1 / 105,6) adanın 0,5 mm altında; dokunulmadı.
- **J3** (2,54 mm 1×2 header, DNP) (166,2, 120,5): pin 1 VOUT (THT, In2 VOUT düzlemine), pin 2 GND.
- Alt silk "RevD …" yazısı "RevF1 …" yapıldı ve soğutucu penceresinden uzağa (162, 156) taşındı.

### g) Kart boyutu
Büyütülmedi. D1/D2 TO-263'leri (2 × ~10 × 15 mm) kalktı; yeni blok ~12 × 12 mm.

## 3. Görüntüler

Hepsi `docs/paket2_assets/` altında. `before_*` paket kartından (RevD5E1), `after_*` RevF1 kartından.

| İçerik | Önce | Sonra |
|---|---|---|
| F.Cu tümü / yakın | `before_F.Cu.png` / `before_zoom_F.Cu.png` | `after_F.Cu.png` / `after_zoom_F.Cu.png` |
| In1.Cu (GND) | `before_In1.Cu.png`, `before_zoom_In1.Cu.png` | `after_In1.Cu.png`, `after_zoom_In1.Cu.png` |
| In2.Cu (VIN/VOUT) | `before_In2.Cu.png`, `before_zoom_In2.Cu.png` | `after_In2.Cu.png`, `after_zoom_In2.Cu.png` |
| B.Cu | `before_B.Cu.png`, `before_zoom_B.Cu.png` | `after_B.Cu.png`, `after_zoom_B.Cu.png` |
| 3D | – | `after_3d_top.png`, `after_3d_bottom.png` |

Yakın görüntüler giriş + güç katı bölgesidir (100–147 × 95–128 mm).

Görsel öz kontrol:
- In1 Q1/Q2 altında kesintisiz.
- In2'de TG Q1 drain altından çıkmış.
- Alt yüzde VIN penceresi açık.
- Q3/U5 bloğu giriş bölgesinde; VIN_RAW ve VIN dökümleri ayrı.

## 4. Kullanıcı kontrol listesi (KiCad'de açınca)

1. `KiCad_RevF1/EE463_RevD_Prototype.kicad_pro` ile açın. Kaydetmeden önce/sonra `.kicad_pro` SHA256'yı kontrol edin
   (CLAUDE.md kural 1).
2. Zone'ları **B** ile yeniden doldurun ve DRC çalıştırın; 0 / 0 / 0 beklenir.
3. Giriş bloğu:
   - Q3 yönü: source pinleri (1–3) J1 tarafında, drain tab'ı VIN dökümünde mi?
   - U5 pin 1 işareti ile CVCAP1/CANODE1 değerleri doğru mu?
   - EN izi ANODE'a bağlı mı?
4. Q1 çevresi:
   - Termal via yoğunluğu yeterli mi? Sağ tarafa (GH/RGSH bölgesi) via eklemek için gate bileşenlerini kaydırmak ister misiniz?
5. In1: Q1–Q2–CIN altında kesik kalmadığını 3D/katman görünümünde teyit edin.
6. In2 TG yeni rotası: SW kesiğinin içinde. GH/TG gate döngüsünün uzunluğunu (via 131,7,116,5 → 142,1,102,4) kabul ediyor musunuz?
7. L1 çift footprint: iki üreticinin land pattern çizimiyle karşılaştırın.
8. U1 EP: 4 dolgusuz via + paste düzeni. Üretici "tented via in pad" (alt taraf kapalı) yapabiliyorsa onu seçin;
   yapamıyorsa via'lar açık kalır, az miktarda lehim kaçağı beklenir.
9. Soğutucu: alt yüzde açık bakır VIN potansiyelinde. Yalıtkan ped (Sil-Pad vb.) zorunlu; soğutucu montaj deliği yok
   (yapıştırma varsayıldı).
10. J3 DNP: kullanılmayacaksa footprint kalabilir.
11. Silk ve referans yazıları: yeni parçaların referansları 0,8 mm.

## 5. Onay bekleyen kararlar (Paket 2)

1. **CIN6–10 sırası yerinde bırakıldı.** Sıcak döngü CIN1–4 + kesintisiz In1 ile kısaltıldı. Alt sırayı Q2 source'a
   yaklaştırmak alt bölgedeki RFREQ/GL/TP yerleşiminin yeniden yapılmasını gerektirir.
2. **Q1 termal via sayısı 12** (rev 2'de CHF2/CHF3 sol tarafı aldı; sağ taraf gate devresiyle dolu). Güncel termal hesap paket2b'de.
3. **TG In2 rotası uzadı** (SW kesiğinin içinden dolaşıyor). Gate döngüsü indüktansı biraz artar ama RGH 6,8 Ω ile
   sönümleniyor. rev 2'de RGH1 Q1 gate pinine taşındı ve TG rotası kısaldı.
4. **Soğutucu penceresi küçük** (8,2 × 4,5 mm); SENSEP/VOUT Kelvin hatları altından geçtiği için büyütülmedi.
   Bu hatları aşağı kaydırıp pencereyi büyütmek mümkün.
5. **U1 EP'de 4 dolgusuz via** (üreticinin dolgu desteği belirsiz olduğu için). Dolgu destekleniyorsa paketteki 9 via'lı
   düzen geri alınabilir.
6. **RUN filtre kondansatörü ve CC anti-windup** (Paket 1 kararları 8–9) karta eklenmedi.
7. LM74700 stok riski (Paket 1 karar 5). ~~footprint LM74500-Q1 ile de uyumlu~~ — **yanlış** (LM74500 yalnız DDF-8);
   pin-pin yedek AP74700QW6-7. Bkz. `docs/paket2b_ek_sonuclar.md`.

Paket 3 (tam doğrulama) ve Paket 4 (üretim dosyaları) kullanıcı onayı bekliyor. Gerber/drill **üretilmedi**,
üreticiye bir şey gönderilmedi.
