# Video script — 849 videodan bir kanalın DNA'sını çıkarmak

## Paketleme

**Ana başlık:** Barış Özcan'ın 849 Videosunu Yapay Zekâyla Analiz Ettim

**Alternatif başlıklar:**

- 1,2 Milyon Kelime Barış Özcan Hakkında Ne Söylüyor?
- Barış Özcan'ın Kanal Formülünü Verilerle Aradım
- 849 Video, 800 Transcript ve Bir Yapay Zekâ

**Thumbnail metni:** `849 VİDEONUN DNA'SI`

**Tek cümlelik vaat:** Barış Özcan kanalının 849 videosunu, 800 transcriptini ve bütün thumbnail kataloğunu analiz ederek gerçekten tekrarlanabilen anlatım ve paketleme sinyallerini; çalışmayan “başarı formüllerinden” ayırıyoruz.

**Hedef süre:** 12–13 dakika

---
## Metrik sunum sayfası

Repo kökünde şu komutu çalıştır:

```bash
python -m http.server 8000 --directory video-assets
```

Ardından `http://localhost:8000/presenter/` adresini aç. `←` / `→` veya boşluk slayt değiştirir; `F` tam ekran, `N` konuşmacı notlarıdır. Kayıtta notları kapalı tut.

---


## Temiz konuşma metni ve prodüksiyon notları

### 0:00 — Cold open

[ORİJİNAL KLİP — “Neden tişörtlerimin veritabanı var?”, 00:00]

> “Buradan ve şuradan giren veri miktarını hiç merak ettiniz mi?”

[WEB 00 · GİRİŞ: İlk cümle biter bitmez sunum sayfasına kes. `849`, `800`, `1,2 M` sırayla görünür.]

Ben merak ettim.

Ama bu kez tek bir videonun içindeki veriyi değil, videoların tamamının oluşturduğu büyük resmi merak ettim.

Bir kanal yıllar boyunca yüzlerce video yayınladığında geride sadece bir oynatma listesi bırakmıyor. Başlıklarıyla, thumbnail'leriyle, anlattığı hikâyelerle ve kullandığı milyonlarca kelimeyle kendine ait bir parmak izi bırakıyor.

Peki o parmak izini gerçekten ölçebilir miyiz?

Barış Özcan'ın kanalındaki 849 videoyu, ulaşabildiğim 800 transcripti ve thumbnail kataloğunun tamamını analiz ettim. Sonra transcriptleri ve görselleri ayrı ayrı yapay zekâ destekli analizlerden geçirdim.

Ama en ilginç sonuç, bulduğum bir başarı formülü değildi.

Tam tersine, formül sandığımız bazı şeylerin veride neredeyse hiç çalışmamasıydı.

[BEAT]

Şimdi önce bu veri setinin nasıl kurulduğuna bakalım.

---

### 0:52 — Ham dosyalardan SQLite'a

[WEB 01 · HAM GİRDİLER: `catalog.jsonl`, metadata, manifest ve `subtitles/` kutularını göster.]

İşe hazır bir tabloyla başlamadım.

Elimde kanal kataloğu, ayrı bir metadata dosyası, hangi videoda hangi altyazının bulunduğunu söyleyen bir manifest ve yüzlerce SRT dosyası vardı.

Bu dosyaların ortak noktası video kimliğiydi. İlk adımda hepsini bu kimlik üzerinden eşleştirdim.

[WEB 02 · SQLITE: `videos`, `transcripts` ve `transcript_cues` tablolarını göster.]

Sonra yerel bir SQLite veritabanı oluşturdum.

İlk tabloda videonun başlığı, yayın tarihi, süresi, izlenmesi, beğenisi, yorumu ve thumbnail adresi duruyor.

İkinci tabloda her videonun transcripti var. Altyazının manuel mi otomatik mi olduğu, ham metin, temizlenmiş metin, kelime ve cue sayısı burada tutuluyor.

Üçüncü tablo ise zaman kodlu altyazı satırları. Her cümlenin başlangıç ve bitiş saniyesini ayrı saklıyor.

[WEB 03 · VERİYİ AYIRMA: `RAW`, `CLEAN`, `TIMED`, `JOIN` kartlarını sırayla göster.]

Aynı konuşmayı üç farklı biçimde saklamamın nedeni buydu.

Ham SRT dosyasını, bir hata gördüğümde orijinale dönebilmek için korudum.

HTML etiketlerini ve gereksiz boşlukları temizleyerek kesintisiz bir normalize metin oluşturdum. Kelime, konu ve anlatım analizlerini bunun üzerinde yaptım.

Zaman kodlu cue'ları ise özellikle videoların ilk 90 saniyesini inceleyebilmek için ayrı tuttum.

Bir videoda hem manuel hem otomatik Türkçe altyazı varsa manuel olanı tercih ettim. Böylece noktalama işaretine bağlı cümle ölçümlerinde daha güvenilir bir alt küme kullanabildim.

[WEB 04 · SON VERİ SETİ: 849 video, 800 transcript, 1,2 milyon kelime, 198.638 cue ve 891,6 milyon izlenme.]

Veritabanını açtığımda karşımdaki ölçek buydu:

849 video, 800 Türkçe transcript, yaklaşık 1,2 milyon normalize kelime ve 198.638 zaman kodlu altyazı satırı.

Her video için metadata, transcript ve görsel ölçümleri aynı video kimliğinde birleşiyordu.

Analizi yaptığım andaki toplam izlenme görüntüsü yaklaşık 891,6 milyondu. Bu sayı sabit değil; videolar izlenmeye devam ediyor. O nedenle eski ve yeni videoları yalnızca toplam izlenmeyle karşılaştırmadım. Yaş farkını azaltmak için günlük izlenme hızını da kullandım.

Buradan sonra veriyi üç kola ayırdım: performans ve paketleme, transcript ve anlatım, thumbnail ve vision.

Transcriptleri ayrıca 3.775 anlamlı parçaya böldüm. 849 thumbnail'de temel görsel özellikler çıkardım; dengeli 120 örneği de yerel görsel modelle etiketledim.

Burada çok önemli bir sınır var.

Bu çalışma “hangi thumbnail kesin tıklanır?” sorusunun sihirli cevabı değil. İzlenme sayısı; konu, yayın tarihi, dağıtım, izleyici ilgisi ve ölçemediğimiz pek çok değişkenden etkileniyor. Birazdan göreceğiniz ilişkiler neden-sonuç değil; katalogda gördüğümüz betimsel sinyaller.

---

### 2:50 — Kanal birkaç viral videodan mı ibaret?

[WEB 05 · ARKA KATALOG: `10 video → %8,4` ve `383 video → yaklaşık %80` kartlarını göster.]

İlk sorum şuydu: Kanalın toplam başarısı birkaç dev videonun omzunda mı duruyor?

Öyle görünmüyor.

En çok izlenen ilk 10 video, 891,6 milyonluk toplam izlenmenin yalnızca yüzde 8,4'ünü getiriyor. Toplam izlenmenin yüzde 80'ine ulaşmak içinse en çok izlenen 383 videoyu birlikte saymamız gerekiyor. Bu, kataloğun yüzde 45,1'i.

Yani kanal yalnızca birkaç viral videoya bağlı değil. İzlenmeler yüzlerce videoya yayılıyor; güçlü bir arka katalog var. Eski videolar da yeni videolarla birlikte izlenme toplamını taşımaya devam ediyor.

Bir başka deyişle burada tek gecelik bir patlamadan çok, yıllar boyunca biriken bir kütüphane etkisi görüyoruz.

[B-ROLL: Eski videolardan yenilere doğru thumbnail şeridi. İki saniyeyi geçmesin.]

Bu bence videonun geri kalanı için önemli. Çünkü tek bir viral başlığın sırrını aramak yerine, tekrar tekrar çalışabilen editoryal sistemi aramamız gerekiyor.

---

### 3:50 — En net paketleme sinyali

[WEB 06 · SÜRE: Grafikle birlikte üç süre grubunun video sayısı ve medyanları.]

Paketleme tarafındaki en net betimsel ayrım video süresinde çıktı.

Katalogda 10 dakikanın üzerindeki 577 videonun medyan izlenmesi yaklaşık 844 bin. Medyan günlük izlenme hızı ise 627.

Beş ile 10 dakika arasındaki videolarda medyan izlenme yaklaşık 544 bin ve günlük hız 187.

Beş dakikanın altındaki videolarda medyan izlenme yaklaşık 69 bin; günlük hız ise 17.

Bu “videoyu uzatırsanız izlenir” demek değil. Uzun videoların konusu, yayınlandığı dönem veya kanalın gelişim evresi farklı olabilir. Fakat katalog içinde uzun formun kanalın ana anlatım biçimi olduğu çok net.

[WEB 07 · BAŞLIK: `<40`, `40–79`, `80+` karakter grupları.]

Başlık uzunluğunda ise aynı ölçüde güçlü bir ayrım yok.

Kısa başlıkların toplam medyan izlenmesi biraz daha yüksekken, 40–79 karakterlik orta uzunluktaki başlıkların günlük izlenme hızı daha yüksek. Yani veriden “başlığın tam olarak şu kadar karakter olsun” diye temiz bir reçete çıkaramıyoruz.

Bu da iyi bir hatırlatma: İnsanlar cetvelle başlık seçmiyor.

---

### 5:05 — Tahmini YouTube geliri

[WEB 08 · YOUTUBE GELİRİ: Güncel izlenme, RPM aralığı, orta senaryo ve kelime başı tahmin.]

Bu kadar izlenmeyi görünce akla gelen kaçınılmaz bir soru var:

Bu kanal YouTube'dan şimdiye kadar ne kadar kazanmış olabilir?

Gerçek rakamı Barış Özcan'ın YouTube Studio ekranı olmadan bilemeyiz. YouTube'un kullandığı RPM, içerik üreticisinin bin toplam izlenme başına platformdan elde ettiği geliri gösteriyor.

Social Blade'ın bugünkü sayacında kanal 1 milyar izlenme sınırını geçmiş durumda: 1 milyar 694 bin 83 izlenme. Türkiye ağırlıklı kanallar için yayımlanan tahmini RPM bandını bin izlenme başına 0,50 dolar, 1,10 dolar ve 2,80 dolar olarak üç senaryoya ayırdım.

Bu model, kanalın ömür boyu YouTube platform gelirini yaklaşık 500 bin dolarla 2,8 milyon dolar arasına yerleştiriyor. Orta senaryo yaklaşık 1,1 milyon dolar.

20 Ağustos 2026 tarihli merkez bankası kuruyla bu orta senaryonun bugünkü karşılığı yaklaşık 52,7 milyon lira.

Bu, geçmişte gerçekten tahsil edilen lira tutarı değil. Bugünkü kurla çevrilmiş bir karşılık. Sponsorluklar, marka anlaşmaları, vergiler ve YouTube dışı gelirler de bu hesabın dışında.

Bir de tamamen eğlencelik bir normalizasyon yaptım. Aynı 849 videoluk analiz snapshot'ında orta senaryo geliri 1 milyon 200 bin 642 normalize kelimeye böldüğümüzde kelime başına yaklaşık 82 cent, yani bugünkü kurla 39 lira çıkıyor.

Elbette her kelime eşit para kazandırmadı. Bu yalnızca kanalın ölçeğini başka bir açıdan görmek için yapılmış kaba bir tahmin.


---

### 6:05 — Thumbnail'lerde sihirli renk var mı?

[B-ROLL: Qwen örnek contact sheet'i kısa süre tam ekran göster.]

Sonra thumbnail'lere baktım.

849 görselin tamamında doygunluk, parlaklık, kontrast ve kenar yoğunluğu gibi basit sinyalleri ölçtüm.

[WEB 09 · TEMEL THUMBNAIL: Korelasyon grafiği ve üç katsayı.]

Doygunlukla logaritmik izlenme arasındaki Pearson korelasyonu artı 0,233. Ortalama parlaklıkta artı 0,152. Kenar yoğunluğunda ise eksi 0,086.

Bunların hiçbiri tek başına güçlü bir ilişki değil.

[WEB 10 · QWEN: 120 örnek, 39 test videosu, `0,526 → 0,272`.]

Daha sonra 120 thumbnail'lik dengeli örneği görsel modele gösterdim. Model; yüz sayısı, metin konumu, ana özne, hook tipi, renk paleti ve kompozisyon gibi etiketler üretti.

Peki temel görsel ölçümler ve bu daha detaylı yapay zekâ etiketleri tahmini iyileştirdi mi?

[WEB 11 · TAM KATALOG TESTİ: `0,287 → 0,179 → 0,102`.]

Önce 849 videoluk tam katalog testine baktım. 2025 ve sonrası videolarda başlık, süre ve yıl gibi temel paketleme özelliklerinin Spearman sıralama korelasyonu 0,287'ydi. İçerik ve temel thumbnail ölçümleri eklendiğinde bu değer 0,102'ye kadar düştü.

Ayrı yürüttüğüm 120 thumbnail'lik keşifsel Qwen deneyinde de görsel etiketler temel modeli iyileştirmedi. Fakat bu deneyin zaman bazlı test bölümü yalnızca 39 videodan oluşuyordu; dolayısıyla sonucu genelleştiremeyiz.

Yani bu iki deneyde de daha fazla özellik, otomatik olarak daha iyi tahmin demek değildi.

Bu örnek özellikle önemli. Çünkü model bir thumbnail'e çok ikna edici etiketler verebilir. “Yüz var, kontrast yüksek, merak uyandırıyor” diyebilir. Fakat ikna edici açıklama, tahmin gücüyle aynı şey değil.

Görsel yapay zekâ burada bize thumbnail'leri düzenlemek ve örnekleri bulmak için yardımcı oluyor. Başarıyı açıklayan kesin bir makineye dönüşmüyor.

---

### 7:40 — Asıl parmak izi: anlatım

[WEB 12 · ANLATIM: 480 manuel altyazı, 10,8 kelime/cümle ve `ORTA` okunabilirlik.]

Asıl belirgin parmak izi transcriptlerde ortaya çıktı.

Noktalama işaretleri güvenilir olduğu için bu bölümde özellikle 480 manuel altyazıyı temel aldım.


Medyan cümle uzunluğu yaklaşık 10,8 kelime. Türkçe metinler için kullanılan okunabilirlik hesabında medyan sonuç 66,9 bölü 100; yani orta düzey. Başka bir deyişle anlatım teknik konulara girse de gereksiz yere ağırlaşmıyor.

[WEB 13 · İLK 90 SANİYE: 550 soru sinyali, 209 şaşırtıcı iddia, 9 düz ifade.]

Ama daha ilginç olan açılışlar.

İlk 90 saniyeyi inceleyen kural tabanlı sınıflandırıcı, 800 transcriptin 550'sinde soru odaklı bir açılış sinyali buldu. 209 videoyu şaşırtıcı iddia, yalnızca dokuz videoyu düz ifade olarak sınıflandırdı.

Bu kanalın tekrar eden anlatım hareketi burada görünüyor:

Önce tanıdık ya da somut bir şey gösteriliyor.

Sonra bir soru açılıyor.

Ardından o küçük gözlemin altındaki kavram açıklanıyor ve çerçeve giderek genişletiliyor.

Teknik bir konu anlatılırken bile doğrudan hitap ve benzetmeler devreye giriyor. Fakat bunlar her cümlede üst üste yığılmıyor.

Bunu tek bir cümleyle özetlemem gerekirse: erişilebilir, soru odaklı, benzetmelere açık ve izleyiciyle doğrudan konuşan bir anlatım.

Fakat burada da bir “başarı düğmesi” bulmadık. Yıla göre normalize ettiğim stil özelliklerinin performansla ilişkileri zayıftı. En güçlü sinyalin mutlak Spearman değeri bile yaklaşık 0,15.

Demek ki ilk 90 saniyeye bir soru eklemek, tek başına videoyu başarılı yapmıyor.

Sorunun arkasında anlatılmaya değer bir fikir olması gerekiyor.

---

### 9:05 — Arşiv Araştırması

[WEB 14 · ARŞİV ARAŞTIRMASI: Geçiş kartı. Ardından gerçek `Arşiv Konuş` sayfasına kes.]

Bu noktada sonuçları yalnızca grafiklerde bırakmak istemedim.

800 transcripti böldüğüm 3.775 kaynak parçasını aranabilir bir arşive dönüştürdüm.

[EKRAN KAYDI: Doğrudan `ARŞİV ARAŞTIRMASI` sekmesini seç. `MERAK SOHBETİ` modunu açma.]

Arşiv Araştırması modunda sistem önce soruyla ilgili transcript parçalarını arıyor. Yeterli kanıt bulursa cevabı o parçalarla kuruyor ve kullanılan videoları zaman kodlarıyla birlikte gösteriyor.

[DEMO SORUSU: `Newton beşiği nedir? Arşivdeki videolardan kaynak ve zaman koduyla açıkla.`]

[EKRAN: Cevabın tamamını okumak yerine kaynak video ve zaman kodu kartlarına yakınlaş.]

Burada benim için önemli olan cevabın ne kadar güzel yazıldığı değil.

Önemli olan, cevaptan onu söyleyen gerçek videoya ve saniyeye geri dönebilmek.

Demo bu bağlantıyı kuramazsa o kaydı kullanmam. Çünkü kaynak göstermeyen akıcı bir cevap, bu videonun anlattığı yönteme ters düşer.


---

### 10:05 — Sonuçtan kaynağa

[WEB 15 · KANIT: Rapor dosyaları ekranda. `analysis-summary.json` ile başlayıp `CLAIM_LEDGER.md` satırında bitir.]

Canlı arayüzün yanında, analiz sonuçlarını kayıt sırasında kullanabileceğim tek bir sunum ekranında topladım.

Ama burada önemli olan tasarım değil. Ekranda gördüğünüz her sayı, yayınlanan bir kanıt dosyasına geri dönüyor.

Katalog dağılımı için ayrı rapor var. 849 videonun performans satırları ayrı. Thumbnail deneyleri, zaman testleri ve anlatım ölçümleri de kendi dosyalarında duruyor.

Böylece bir grafiğin yalnızca sonucunu değil, hangi veriyle üretildiğini ve nerede sınırlandığını da görebiliyorsunuz.

Ham altyazıları, yüzlerce thumbnail dosyasını ve model ağırlıklarını bu pakete koymadım. Fakat videoda kullandığım türetilmiş tablolar, analiz kodları, grafikler ve iddia defteri açık.

Çünkü “yapay zekâ böyle söyledi” tek başına kanıt değil.

Asıl değerli olan, söylediği şeyi veriye geri bağlayabilmek.

---

### 10:50 — Sonuç

[WEB 16 · SONUÇ: Dört çıkarım görünsün. Son cümlede ekranda yalnızca `FORMÜL DEĞİL, SİSTEM` kalsın.]

Başta tek bir soru sorduk:

Bir kanalın yıllar boyunca bıraktığı parmak izini ölçebilir miyiz?

Kısmen, evet.

Bu katalog birkaç viral videoya bağlı değil. Uzun form baskın. Thumbnail renkleri ve yapay zekâ etiketleri tek başına güvenilir bir başarı formülü vermiyor. En tekrarlanabilir özellik ise anlatımın yapısında: somut bir ayrıntıyla başlayan, soru soran, kavramı açan ve sonunda daha geniş bir fikre bağlanan bir akış.

Fakat verinin bize söylemediği şey de en az bunlar kadar önemli.

Korelasyon, neden değildir. Bir özelliği sayabiliyor olmamız, onun izlenmeyi yarattığı anlamına gelmez. Ve hiçbir model, anlatılmaya değer fikrin yerini tutmaz.

Belki de kanalın asıl gücü tek bir formülde değil; yıllar boyunca aynı merak kasını farklı konularda tekrar tekrar çalıştırmasındadır.

[WEB 16: Sonuç kartlarını sırayla kapat; başlık ve `editoryal sistem` ifadesi ekranda kalsın.]

Tüm grafikler, özet tablolar, analiz kodları ve bu videonun kaynak defteri GitHub'da açık olacak.

Bir sonraki videoda hangi kanalın sayılarla görünmeyen parmak izini çıkarmamı istersiniz?

---

## Kayıt sırasında dikkat edilecekler

- Sayıları ezberden yuvarlama; ekrandaki grafikle aynı değeri söyle.
- Web sunumunda `N` ile açılan konuşmacı notlarını kayıt sırasında kapat; tam ekran için `F` kullan.
- Qwen vision sonucunu 120 videoluk keşifsel örnek, zaman bazlı testini ise 39 video olarak tanımla; tam katalog deneyiyle karıştırma.
- Arşiv demosunda yalnızca `ARŞİV ARAŞTIRMASI` modunu göster; `MERAK SOHBETİ` modunu açma. Kaynak video ve zaman kodu görünmeyen cevabı videoda kullanma.
- Cold open klibini kısa tut; video adı ve bağlantısını açıklamada belirt.
- Temiz kayıt metni yaklaşık 1.600 konuşma kelimesidir; canlı demo, klip ve doğal duraklamalarla 12–13 dakika hedefler.
