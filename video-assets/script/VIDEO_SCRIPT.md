# Video script — 849 videodan bir kanalın DNA'sını çıkarmak

## Paketleme

**Ana başlık:** Barış Özcan'ın 849 Videosunu Yapay Zekâyla Analiz Ettim

**Alternatif başlıklar:**

- 1,2 Milyon Kelime Barış Özcan Hakkında Ne Söylüyor?
- Barış Özcan'ın Kanal Formülünü Verilerle Aradım
- 849 Video, 800 Transcript ve Bir Yapay Zekâ

**Thumbnail metni:** `849 VİDEONUN DNA'SI`

**Tek cümlelik vaat:** Barış Özcan kanalının 849 videosunu, 800 transcriptini ve bütün thumbnail kataloğunu analiz ederek gerçekten tekrarlanabilen anlatım ve paketleme sinyallerini; çalışmayan “başarı formüllerinden” ayırıyoruz.

**Hedef süre:** 9–11 dakika

---

## Temiz konuşma metni ve prodüksiyon notları

### 0:00 — Cold open

[ORİJİNAL KLİP — “Neden tişörtlerimin veritabanı var?”, 00:00]

> “Buradan ve şuradan giren veri miktarını hiç merak ettiniz mi?”

[EKRAN: Cümle biter bitmez görüntü donsun. Kadrajın üzerine sırasıyla `849 VİDEO`, `800 TRANSCRIPT`, `1,2 MİLYON KELİME` gelsin.]

Ben merak ettim.

Ama bu kez tek bir videonun içindeki veriyi değil, videoların tamamının oluşturduğu büyük resmi merak ettim.

Bir kanal yıllar boyunca yüzlerce video yayınladığında geride sadece bir oynatma listesi bırakmıyor. Başlıklarıyla, thumbnail'leriyle, anlattığı hikâyelerle ve kullandığı milyonlarca kelimeyle kendine ait bir parmak izi bırakıyor.

Peki o parmak izini gerçekten ölçebilir miyiz?

Barış Özcan'ın kanalındaki 849 videoyu, ulaşabildiğim 800 transcripti ve thumbnail kataloğunun tamamını analiz ettim. Sonra bu verilerle konuşabilen küçük bir yapay zekâ sistemi kurdum.

Ama en ilginç sonuç, bulduğum bir başarı formülü değildi.

Tam tersine, formül sandığımız bazı şeylerin veride neredeyse hiç çalışmamasıydı.

[BEAT]

Şimdi önce veri setini açalım.

---

### 0:52 — Ne topladım?

[EKRAN: `video-assets/charts/01-channel-scale.png`]

Katalogda 849 video var.

Bunların 800 tanesinde kullanılabilir Türkçe transcript bulabildim. Manuel ve otomatik altyazıları temizleyip normalize ettiğimde elimde yaklaşık 1,2 milyon kelime kaldı.

Her video için yayın tarihi, süre, izlenme, beğeni, yorum, başlık ve thumbnail bilgilerini aynı veri setinde birleştirdim.

Analizi yaptığım andaki toplam izlenme görüntüsü yaklaşık 891,6 milyondu. Bu sayı sabit değil; video yayına girdikten sonra da izlenmeye devam ediyor. O nedenle eski ve yeni videoları yalnızca toplam izlenmeyle karşılaştırmadım. Yaş farkını azaltmak için günlük izlenme hızını da kullandım.

[EKRAN: Kod akışı — katalog → metadata → transcript → thumbnail → analiz]

Transcriptleri 3.775 anlamlı parçaya böldüm. Konuları ve duygu etiketlerini hafif bir içerik haritası olarak kullandım. 849 thumbnail'de renk, parlaklık ve kenar yoğunluğu gibi temel görsel özellikleri çıkardım. Ayrıca zamana ve performans grubuna göre dengelenmiş 120 thumbnail'i yerel bir görsel modelle etiketledim.

Burada çok önemli bir sınır var.

Bu çalışma “hangi thumbnail kesin tıklanır?” sorusunun sihirli cevabı değil. İzlenme sayısı; konu, yayın tarihi, dağıtım, izleyici ilgisi ve bizim ölçemediğimiz pek çok değişkenden etkileniyor. Bu yüzden birazdan göreceğiniz ilişkiler neden-sonuç değil. Bunlar, katalogda gördüğümüz betimsel sinyaller.

---

### 2:05 — Kanal birkaç viral videodan mı ibaret?

[EKRAN: `video-assets/charts/02-catalog-lorenz.png`]

İlk sorum şuydu: Kanalın toplam başarısı birkaç dev videonun omzunda mı duruyor?

Öyle görünmüyor.

En çok izlenen ilk 10 videonun katalogdaki toplam izlenmeden aldığı pay yaklaşık yüzde 8,4. Toplam izlenmenin yüzde 80'ine ulaşmak için videoların yaklaşık yüzde 45'ine ihtiyaç var.

Bu, kanalın yalnızca birkaç viral videoya bağlı olmadığını gösteriyor. Güçlü bir arka katalog var. Eski videolar da yeni videolarla birlikte izlenme toplamını taşımaya devam ediyor.

Bir başka deyişle burada tek gecelik bir patlamadan çok, yıllar boyunca biriken bir kütüphane etkisi görüyoruz.

[EKRAN: En eski videolardan yenilere doğru hızlanan bir katalog şeridi.]

Bu bence videonun geri kalanı için önemli. Çünkü tek bir viral başlığın sırrını aramak yerine, tekrar tekrar çalışabilen editoryal sistemi aramamız gerekiyor.

---

### 3:05 — En net paketleme sinyali

[EKRAN: `video-assets/charts/03-duration-performance.png`]

Paketleme tarafındaki en net betimsel ayrım video süresinde çıktı.

Katalogda 10 dakikanın üzerindeki 577 videonun medyan izlenmesi yaklaşık 844 bin. Medyan günlük izlenme hızı ise 627.

Beş ile 10 dakika arasındaki videolarda medyan izlenme yaklaşık 544 bin ve günlük hız 187.

Beş dakikanın altındaki videolarda medyan izlenme yaklaşık 69 bin; günlük hız ise 17.

Bu “videoyu uzatırsanız izlenir” demek değil. Uzun videoların konusu, yayınlandığı dönem veya kanalın gelişim evresi farklı olabilir. Fakat katalog içinde uzun formun kanalın ana anlatım biçimi olduğu çok net.

Başlık uzunluğunda ise aynı ölçüde güçlü bir ayrım yok.

Kısa başlıkların toplam medyan izlenmesi biraz daha yüksekken, 40–79 karakterlik orta uzunluktaki başlıkların günlük izlenme hızı daha yüksek. Yani veriden “başlığın tam olarak şu kadar karakter olsun” diye temiz bir reçete çıkaramıyoruz.

Bu da iyi bir hatırlatma: İnsanlar cetvelle başlık seçmiyor.

---

### 4:18 — Thumbnail'lerde sihirli renk var mı?

[EKRAN: `video-assets/thumbnail-samples/qwen-vision-sample-contact-sheet.jpg`]

Sonra thumbnail'lere baktım.

849 görselin tamamında doygunluk, parlaklık, kontrast ve kenar yoğunluğu gibi basit sinyalleri ölçtüm.

[EKRAN: `video-assets/charts/04-thumbnail-correlations.png`]

Doygunlukla logaritmik izlenme arasındaki Pearson korelasyonu artı 0,233. Ortalama parlaklıkta artı 0,152. Kenar yoğunluğunda ise eksi 0,086.

Bunların hiçbiri tek başına güçlü bir ilişki değil.

Daha sonra 120 thumbnail'lik dengeli örneği görsel modele gösterdim. Model; yüz sayısı, metin konumu, ana özne, hook tipi, renk paleti ve kompozisyon gibi etiketler üretti.

Peki bu daha detaylı görsel etiketler tahmini iyileştirdi mi?

[EKRAN: `video-assets/charts/06-temporal-ablation.png`]

2025 ve sonrası videolardan oluşan zaman bazlı testte, başlık-süre-yıl gibi temel paketleme modelinin Spearman sıralama korelasyonu 0,288'di. İçerik ve thumbnail özellikleri eklendiğinde bu değer 0,103'e kadar düştü.

Yani daha fazla özellik, otomatik olarak daha iyi tahmin demek değil.

Bu örnek özellikle önemli. Çünkü model bir thumbnail'e çok ikna edici etiketler verebilir. “Yüz var, kontrast yüksek, merak uyandırıyor” diyebilir. Fakat ikna edici açıklama, tahmin gücüyle aynı şey değil.

Görsel yapay zekâ burada bize thumbnail'leri düzenlemek ve örnekleri bulmak için yardımcı oluyor. Başarıyı açıklayan kesin bir makineye dönüşmüyor.

---

### 5:52 — Asıl parmak izi: anlatım

[EKRAN: `video-assets/charts/05-intro-hooks.png`]

Asıl belirgin parmak izi transcriptlerde ortaya çıktı.

Noktalama işaretleri güvenilir olduğu için bu bölümde özellikle 480 manuel altyazıyı temel aldım.

Medyan cümle uzunluğu yaklaşık 10,8 kelime. Ateşman okunabilirlik skoru yaklaşık 66,9. Yani anlatım teknik konulara girse bile cümleler çoğunlukla erişilebilir kalıyor.

Ama daha ilginç olan açılışlar.

800 transcript içinde 550 video bir soruyla başlıyor. 209 video şaşırtıcı bir iddia kullanıyor. Düz bir ifadeyle başlayanların sayısı ise yalnızca dokuz.

Bu kanalın tekrar eden anlatım hareketi burada görünüyor:

Önce tanıdık ya da somut bir şey gösteriliyor.

Sonra bir soru açılıyor.

Ardından o küçük gözlemin altındaki kavram açıklanıyor ve çerçeve giderek genişletiliyor.

Teknik bir konu anlatılırken bile doğrudan hitap ve benzetmeler devreye giriyor. Fakat bunlar her cümlede üst üste yığılmıyor.

Bunu tek bir cümleyle özetlemem gerekirse: erişilebilir, soru odaklı, benzetmelere açık ve izleyiciyle doğrudan konuşan bir anlatım.

Fakat burada da bir “başarı düğmesi” bulmadık. Yıla göre normalize ettiğim stil özelliklerinin performansla ilişkileri zayıftı. En güçlü sinyalin mutlak Spearman değeri bile yaklaşık 0,15.

Demek ki bir videoyu soru işaretiyle açmak, tek başına başarılı olmasını sağlamıyor.

Sorunun arkasında anlatılmaya değer bir fikir olması gerekiyor.

---

### 7:18 — Verilerle konuşan chatbot

[EKRAN KAYDI: Public chatbot arayüzü. Önce “Merak Sohbeti”, sonra “Arşiv Araştırması”. Erişim anahtarını kayıtta gösterme.]

Son adımda bu analizi statik grafiklerden çıkarıp konuşulabilir hale getirdim.

800 videonun transcriptlerini 3.775 parçalık semantik bir arama indeksine dönüştürdüm. Kullanıcı bir soru sorduğunda sistem önce ilgili transcript parçalarını buluyor.

Arşiv Araştırması modunda ikinci bir kontrol, bu parçaların soruyu gerçekten cevaplayıp cevaplamadığını denetliyor. Kanıt varsa yanıtın yanında video ve saniye bağlantıları geliyor. Kanıt yoksa sistem bunu açıkça söylüyor.

[DEMO SORUSU: “Newton beşiği nedir?”]

[EKRAN: Yanıttaki S1/S2 kaynaklarına ve timestamp kartlarına yakınlaş.]

Merak Sohbeti modunda ise transcriptlerden çıkardığım yapısal anlatım profili kullanılıyor. Soru odaklı açılış, erişilebilir cümleler, ölçülü benzetmeler ve genişleyen çerçeve bütün cevaplara uygulanıyor.

Bu bir insanın dijital kopyası değil. Kişisel anı veya görüş üretmiyor. Yaptığı şey, kamuya açık videolardan ölçtüğümüz anlatım yapılarını ve arşiv içeriğini kullanılabilir bir araştırma arayüzüne dönüştürmek.

[DEMO SORUSU: “Bir fikri hikâyeye dönüştürmek neden işe yarar?”]

İşte bütün bu çalışmanın bence en kullanışlı çıktısı bu.

Grafik size katalog hakkında bir sonuç gösteriyor. Chatbot ise sizi o sonucun dayandığı videoya ve cümleye geri götürüyor.

---

### 8:38 — Sonuç

Başta tek bir soru sorduk:

Bir kanalın yıllar boyunca bıraktığı parmak izini ölçebilir miyiz?

Kısmen, evet.

Bu katalog birkaç viral videoya bağlı değil. Uzun form baskın. Thumbnail renkleri ve yapay zekâ etiketleri tek başına güvenilir bir başarı formülü vermiyor. En tekrarlanabilir özellik ise anlatımın yapısında: somut bir ayrıntıyla başlayan, soru soran, kavramı açan ve sonunda daha geniş bir fikre bağlanan bir akış.

Fakat verinin bize söylemediği şey de en az bunlar kadar önemli.

Korelasyon, neden değildir. Bir özelliği sayabiliyor olmamız, onun izlenmeyi yarattığı anlamına gelmez. Ve hiçbir model, anlatılmaya değer fikrin yerini tutmaz.

Belki de kanalın asıl gücü tek bir formülde değil; yıllar boyunca aynı merak kasını farklı konularda tekrar tekrar çalıştırmasındadır.

[EKRAN: Grafikler geriye doğru kapanır, en sonda 849 thumbnail'den oluşan mozaik kalır.]

Tüm grafikler, özet tablolar, analiz kodları ve bu videonun kaynak defteri GitHub'da açık olacak.

Bir sonraki videoda hangi kanalın sayılarla görünmeyen parmak izini çıkarmamı istersiniz?

---

## Kayıt sırasında dikkat edilecekler

- Sayıları ezberden yuvarlama; ekrandaki grafikle aynı değeri söyle.
- “Şu özellik videoyu başarılı yapıyor” deme. “Katalogda ilişki/sinyal gördük” de.
- Thumbnail vision sonucunu yalnızca 120 videoluk keşifsel örnek olarak tanımla.
- Chatbot demosunda erişim anahtarını, terminal yolunu veya yerel servis ayrıntılarını gösterme.
- Cold open klibini kısa tut; video adı ve bağlantısını açıklamada belirt.
- Script yaklaşık 1.350–1.500 konuşma kelimesidir; doğal tempoda 9–11 dakika hedefler.
