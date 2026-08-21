const slides = [
  {
    section: "Giriş",
    eyebrow: "BARİŞ ÖZCAN KANAL ANALİZİ · 20 AĞUSTOS 2026",
    title: "849 videonun <span class='accent'>DNA’sı</span>",
    lead: "Bir başarı formülü aradım. Verinin gösterdiği şey, formülden daha ilginçti.",
    stats: [["849", "katalog videosu"], ["800", "Türkçe transcript"], ["1,2 M", "normalize kelime"]],
    source: "analysis-summary.json · creator-style-summary.json",
    note: "Orijinal açılış klibinden sonra: Ben merak ettim. Ama bu kez tek bir videonun içindeki veriyi değil, videoların tamamının oluşturduğu büyük resmi merak ettim."
  },
  {
    section: "Hazırlık",
    eyebrow: "01 · HAM GİRDİLER",
    title: "Analiz bir grafikle değil, dört ham veri kaynağıyla başladı.",
    pipeline: [
      ["01", "catalog.jsonl", "video kimliği · başlık · tarih"],
      ["02", "metadata", "izlenme · beğeni · yorum"],
      ["03", "manifest", "altyazı kaynağı · dosya yolu"],
      ["04", "subtitles/", "manuel ve otomatik SRT"]
    ],
    source: "build_dataset.py · lines 159–169",
    note: "İlk iş bu dosyaları yan yana açmak değil, ortak video kimliği üzerinden birleştirmekti. Katalog, zenginleştirilmiş metadata, altyazı manifesti ve SRT dosyaları aynı akışa girdi."
  },
  {
    section: "SQLite",
    eyebrow: "02 · VERİTABANI",
    title: "Ham dosyaları tek bir <span class='accent'>SQLite</span> veritabanında birleştirdim.",
    database: [
      ["videos", "849 kayıt", ["id · primary key", "title · upload_date", "duration · views", "likes · comments", "thumbnail_url"]],
      ["transcripts", "video başına 1", ["video_id · foreign key", "manual / automatic", "raw_text", "normalized_text", "word_count · cue_count"]],
      ["transcript_cues", "198.638 kayıt", ["transcript_id", "cue_index", "start_seconds", "end_seconds", "text · is_speech"]]
    ],
    terminal: ["$ sqlite3 analysis.sqlite3", "sqlite> .tables", "transcript_cues   transcripts   videos"],
    source: "analysis/build_dataset.py · SQLite schema",
    note: "Veritabanında üç ana tablo oluşturdum. Video metadatası videos tablosunda, video başına transcript transcripts tablosunda, zaman kodlu her altyazı satırı transcript_cues tablosunda tutuldu."
  },
  {
    section: "Ayrıştırma",
    eyebrow: "03 · VERİYİ AYIRMA",
    title: "Aynı konuşmayı üç farklı ihtiyaca göre sakladım.",
    takeaways: [
      ["RAW", "Orijinal SRT metni: geri dönüp kontrol etmek için."],
      ["CLEAN", "Normalize metin: kelime, konu ve anlatım analizi için."],
      ["TIMED", "Başlangıç ve bitiş saniyeleri: açılışları incelemek için."],
      ["JOIN", "video_id: bütün katmanları aynı videoda birleştirmek için."]
    ],
    source: "build_dataset.py · parse_srt · normalize_cues · transcript_cues",
    note: "Ham metni kaybetmedim. HTML etiketlerini ve gereksiz boşlukları temizleyip ayrı normalize metin oluşturdum. Zaman kodlarını da satır satır sakladım. Manuel altyazı varsa otomatik olana tercih edildi."
  },
  {
    section: "Veri seti",
    eyebrow: "04 · SON VERİ SETİ",
    title: "Veritabanını açtığımda karşımdaki ölçek buydu.",
    metrics: [
      ["849", "Video", "Tam katalog"],
      ["800", "Transcript", "%94,2 kapsama"],
      ["1,2 M", "Normalize kelime", "198.638 zaman kodlu cue"],
      ["891,6 M", "Toplam izlenme", "Tarihli snapshot"]
    ],
    source: "baseline.json · analysis-summary.json · snapshot 2026-08-20",
    note: "Sonuçta 849 video, 800 Türkçe transcript, yaklaşık 1,2 milyon normalize kelime ve 198.638 zaman kodlu altyazı satırı oluştu. İzlenme snapshot’ı yaklaşık 891,6 milyondu."
  },
  {
    section: "Arka katalog",
    eyebrow: "05 · DAĞILIM",
    title: "İzlenmeler birkaç viral videoda toplanmıyor.",
    metrics: [
      ["10 video", "Kataloğun %1,2’si", "Toplam izlenmenin yalnızca %8,4’ü"],
      ["383 video", "Kataloğun %45,1’i", "Toplam izlenmenin yaklaşık %80’i"],
      ["466 video", "Kalan katalog", "Toplam izlenmenin yaklaşık %20’si"]
    ],
    source: "channel-distribution.json · videolar en çok izlenenden aza sıralandı",
    note: "En çok izlenen ilk 10 video, 891,6 milyonluk toplamın yalnızca yüzde 8,4’ünü getiriyor. Toplam izlenmenin yüzde 80’ine ulaşmak için en çok izlenen 383 videoyu birlikte saymak gerekiyor. Yani başarı birkaç viral videoda değil, yüzlerce videoya yayılan arka katalogda."
  },
  {
    section: "Paketleme",
    eyebrow: "06 · SÜRE",
    title: "En net betimsel ayrım: <span class='accent'>uzun form</span>.",
    image: "../charts/03-duration-performance.png",
    metrics: [
      ["577", "10 dk+ video", "843.727 medyan izlenme · 627/gün"],
      ["189", "5–10 dk video", "543.500 medyan · 187/gün"],
      ["83", "5 dk altı", "68.644 medyan · 17/gün"]
    ],
    source: "performance-summary.json · ilişki, nedensellik değil",
    note: "Bu, videoyu uzatırsanız izlenir demek değil. Konular ve kanal dönemleri farklı. Fakat katalog içinde uzun formun ana anlatım biçimi olduğu çok net."
  },
  {
    section: "Paketleme",
    eyebrow: "07 · BAŞLIK",
    title: "Başlık için temiz bir karakter reçetesi yok.",
    metrics: [
      ["< 40", "karakter", "737.597 medyan izlenme · 406/gün"],
      ["40–79", "karakter", "708.976 medyan izlenme · 506/gün"],
      ["80+", "karakter", "650.413 medyan izlenme · 426/gün"]
    ],
    source: "analysis-summary.json · title_length_groups",
    note: "Kısa başlıkların toplam medyanı biraz daha yüksek. Orta uzunluktakilerin günlük hızı daha yüksek. İnsanlar cetvelle başlık seçmiyor; buradan evrensel bir sayı çıkaramıyoruz."
  },
  {
    section: "Tahmin",
    eyebrow: "08 · YOUTUBE GELİRİ",
    title: "1 milyar izlenme kaç dolar etmiş olabilir?",
    takeaways: [
      ["SNAPSHOT", "1.000.694.083 güncel kanal izlenmesi."],
      ["ARALIK", "$0,50 M – $2,80 M tahmini platform geliri."],
      ["ORTA", "$1,10 M · bugünkü kurla yaklaşık ₺52,7 M."],
      ["KELİME", "Analiz kataloğunda ≈ $0,82 · ₺39,13 / kelime."]
    ],
    source: "revenue-estimate.json · RPM senaryosu, doğrulanmış gelir değil",
    note: "Bu gelir açıklanmış değil. YouTube Studio verisi olmadan yalnızca senaryo kuruyoruz. Güncel 1,0007 milyar izlenmeye Türkiye için 0,50–1,10–2,80 dolar RPM bandı uygulandı. Sponsorluk ve vergi hariç. Kelime hesabı tutarlılık için ayrı 849 videoluk analiz snapshot’ını kullanıyor; bu eğlenceli bir normalizasyon, nedensel ölçüm değil."
  },

  {
    section: "Thumbnail",
    eyebrow: "09 · TEMEL GÖRSEL SİNYALLER",
    title: "Sihirli renk çıkmadı.",
    image: "../charts/04-thumbnail-correlations.png",
    callouts: [["+0,233", "Doygunluk × log izlenme"], ["+0,152", "Parlaklık × log izlenme"], ["−0,086", "Kenar yoğunluğu × log izlenme"]],
    source: "thumbnail-performance.json · Pearson · n=849",
    note: "Doygunluk, parlaklık ve kenar yoğunluğu ilişkilerinin hiçbiri tek başına güçlü değil. Üstelik elimizde CTR ve impression verisi yok; bunlar tıklama nedeni olarak yorumlanamaz."
  },
  {
    section: "Thumbnail",
    eyebrow: "10 · QWEN VISION DENEYİ",
    title: "İkna edici etiket, tahmin gücü değildir.",
    image: "../thumbnail-samples/qwen-vision-sample-contact-sheet.jpg",
    callouts: [["120", "Dengeli ve keşifsel örnek"], ["39", "Zaman bazlı test videosu"], ["0,526 → 0,272", "Baseline → vision eklenmiş model"]],
    source: "thumbnail-vision-ablation.json · genellenemez keşifsel test",
    note: "Qwen yüz, metin, kompozisyon ve hook etiketleri üretti. Fakat 39 videoluk zaman testinde bu etiketler baseline’ı iyileştirmedi. Örnek küçük ve sonuç genellenemez."
  },
  {
    section: "Tahmin",
    eyebrow: "11 · TAM KATALOG ZAMAN TESTİ",
    title: "Daha fazla özellik, daha iyi tahmin demek değil.",
    image: "../charts/06-temporal-ablation.png",
    callouts: [["0,287", "Paketleme"], ["0,179", "+ içerik"], ["0,102", "+ temel thumbnail"]],
    source: "packaging-ablation.json · Spearman · 2025+ test n=90",
    note: "Bu ayrı, 849 videoluk deney. Başlık, süre ve yıl modelinin sıralama korelasyonu 0,287. İçerik ve temel thumbnail ölçümleri eklendiğinde 0,102’ye düşüyor. Tek model ve tek zaman bölmesi; evrensel benchmark değil."
  },
  {
    section: "Anlatım",
    eyebrow: "12 · SES PARMAK İZİ",
    title: "Asıl tekrar eden yapı transcriptlerde.",
    metrics: [
      ["480", "Manuel altyazı", "Noktalama duyarlı ölçümler"],
      ["10,8", "Kelime / cümle", "Medyan"],
      ["ORTA", "Okunabilirlik", "66,9 / 100 · Türkçe metin ölçümü"],
      ["11,3", "Doğrudan hitap", "1.000 kelime başına"]
    ],
    source: "creator-style-summary.json · manual captions",
    note: "Medyan cümle uzunluğu yaklaşık 10,8 kelime. Türkçe metinler için kullanılan okunabilirlik hesabında sonuç 66,9 bölü 100; yani orta düzey. Bu bölüm yalnızca noktalaması güvenilir 480 manuel altyazıya dayanıyor."
  },
  {
    section: "Anlatım",
    eyebrow: "13 · İLK 90 SANİYE",
    title: "Soru odaklı açılış sinyali baskın.",
    image: "../charts/05-intro-hooks.png",
    callouts: [["550", "Soru sinyali"], ["209", "Şaşırtıcı iddia"], ["9", "Düz ifade"]],
    source: "creator-style-summary.json · rule-based classifier · n=800",
    note: "Bu sonuç ilk cümleyi değil, ilk 90 saniyeyi sınıflandırıyor. 550 videoda soru odaklı sinyal, 209 videoda şaşırtıcı iddia, dokuz videoda düz ifade bulundu. Kural tabanlı bir navigasyon yardımı; insan etiketi değil."
  },
  {
    section: "Canlı demo",
    eyebrow: "14 · ARŞİV ARAŞTIRMASI",
    title: "Bir sonuçtan, onu söyleyen videoya geri dön.",
    takeaways: [
      ["01", "Soruyu 3.775 kaynak parçası içinde ara."],
      ["02", "Yalnızca yeterli kanıt bulunan parçaları kullan."],
      ["03", "Cevabı video ve zaman koduyla birlikte göster."],
      ["DEMO", "Şimdi gerçek arayüzde tek bir soru soracağız."]
    ],
    source: "Arşiv Konuş · gerçek arayüz kaydı",
    note: "Bu slayttan gerçek Arşiv Konuş sayfasına kes. Doğrudan Arşiv Araştırması sekmesini seç; Merak Sohbeti'ni gösterme. Tek soru sor, cevabın tamamını okumak yerine kaynak video ve zaman kodu kartlarına yakınlaş."
  },

  {
    section: "Kanıt",
    eyebrow: "15 · SONUÇTAN KAYNAĞA",
    title: "Her sayı, yayınlanan bir kanıt dosyasına geri dönüyor.",
    evidence: [
      ["analysis-summary.json", "GENEL ÖZET"],
      ["channel-distribution.json", "DAĞILIM"],
      ["video-performance.csv", "849 SATIR"],
      ["packaging-ablation.json", "ZAMAN TESTİ"],
      ["creator-style-summary.json", "ANLATIM"],
      ["CLAIM_LEDGER.md", "SINIRLAR"]
    ],
    source: "GitHub paketi · türetilmiş raporlar ve analiz kodu",
    note: "Canlı demodan sonra yayınlanan kanıt paketine dön: bütün grafikler ve iddialar bu dosyalara geri bağlanıyor. Ham altyazılar ve model ağırlıkları pakette yok; türetilmiş kanıt ve kod açık."
  },
  {
    section: "Sonuç",
    eyebrow: "16 · CEVAP",
    title: "Formül değil, yıllara yayılan bir <span class='accent'>editoryal sistem</span>.",
    takeaways: [
      ["01", "Katalog birkaç viral videoya bağlı değil."],
      ["02", "Uzun form baskın; ama sonuç nedensel değil."],
      ["03", "Renkler ve vision etiketleri başarı reçetesi vermiyor."],
      ["04", "En tekrar eden iz, soru odaklı anlatım yapısı."]
    ],
    source: "Korelasyon neden değildir · snapshot 2026-08-20",
    note: "Bir kanalın parmak izini kısmen ölçebiliriz. Fakat hiçbir model anlatılmaya değer fikrin yerini tutmaz. Belki de asıl güç tek bir formülde değil; aynı merak kasını yıllar boyunca farklı konularda çalıştırmaktır."
  }
];

const app = document.querySelector("#app");
const sectionName = document.querySelector("#section-name");
const slideCount = document.querySelector("#slide-count");
const progress = document.querySelector("#progress");
const dots = document.querySelector("#dots");
const notes = document.querySelector("#notes");
const notesCopy = document.querySelector("#notes-copy");
const prev = document.querySelector("#prev");
const next = document.querySelector("#next");
let index = Math.min(Math.max(Number(new URLSearchParams(location.search).get("slide")) || 1, 1), slides.length) - 1;
let idleTimer;

const metricMarkup = (items, four = false) => `
  <div class="metrics ${four ? "metrics--four metrics--compact" : ""}">
    ${items.map(([value, label, detail]) => `<div class="metric"><strong>${value}</strong><span>${label}</span>${detail ? `<small>${detail}</small>` : ""}</div>`).join("")}
  </div>`;

function render() {
  const slide = slides[index];
  let body = "";

  if (slide.stats) {
    body = `<p class="lead">${slide.lead}</p><div class="hero-stats">${slide.stats.map(([value, label]) => `<div class="hero-stat"><strong>${value}</strong><span>${label}</span></div>`).join("")}</div>`;
  } else if (slide.database) {
    body = `<div class="db-grid">${slide.database.map(([name, count, fields]) => `<article class="db-table"><header><code>${name}</code><span>${count}</span></header><div>${fields.map((field) => `<code>${field}</code>`).join("")}</div></article>`).join("")}</div><div class="terminal-strip">${slide.terminal.map((line) => `<code>${line}</code>`).join("")}</div>`;
  } else if (slide.pipeline) {
    body = `<div class="pipeline">${slide.pipeline.map(([number, title, copy]) => `<div class="pipeline__step"><b>${number}</b><strong>${title}</strong><span>${copy}</span></div>`).join("")}</div>`;
  } else if (slide.evidence) {
    body = `<div class="evidence-list">${slide.evidence.map(([file, label]) => `<div class="evidence-item"><code>${file}</code><span>${label}</span></div>`).join("")}</div>`;
  } else if (slide.takeaways) {
    body = `<div class="takeaways">${slide.takeaways.map(([number, copy]) => `<div class="takeaway"><b>${number}</b><strong>${copy}</strong></div>`).join("")}</div>`;
  } else if (slide.image) {
    const support = slide.callouts ? `<div class="stack">${slide.callouts.map(([value, label]) => `<div class="callout"><strong>${value}</strong><span>${label}</span></div>`).join("")}</div>` : metricMarkup(slide.metrics || []);
    body = `<div class="split"><div class="visual ${slide.image.includes("contact-sheet") ? "visual--sheet" : ""}"><img src="${slide.image}" alt="${slide.title.replace(/<[^>]+>/g, "")}"></div>${support}</div>`;
  } else if (slide.metrics) {
    body = metricMarkup(slide.metrics, slide.metrics.length === 4);
  }

  app.innerHTML = `<section class="slide"><div class="eyebrow">${slide.eyebrow}</div><h${index === 0 ? "1" : "2"}>${slide.title}</h${index === 0 ? "1" : "2"}>${body}<div class="source">${slide.source}</div></section>`;
  sectionName.textContent = slide.section;
  slideCount.textContent = `${String(index + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}`;
  progress.style.setProperty("--progress", `${((index + 1) / slides.length) * 100}%`);
  notesCopy.textContent = slide.note;
  prev.disabled = index === 0;
  next.disabled = index === slides.length - 1;
  [...dots.children].forEach((dot, dotIndex) => dot.classList.toggle("is-active", dotIndex === index));
  const url = new URL(location.href);
  url.searchParams.set("slide", index + 1);
  history.replaceState(null, "", url);
}

function go(delta) {
  const nextIndex = Math.min(Math.max(index + delta, 0), slides.length - 1);
  if (nextIndex === index) return;
  index = nextIndex;
  render();
}

slides.forEach((slide, dotIndex) => {
  const dot = document.createElement("button");
  dot.type = "button";
  dot.className = "dot";
  dot.setAttribute("aria-label", `${dotIndex + 1}. slayt: ${slide.section}`);
  dot.addEventListener("click", () => { index = dotIndex; render(); });
  dots.append(dot);
});

prev.addEventListener("click", () => go(-1));
next.addEventListener("click", () => go(1));
document.querySelector("#notes-toggle").addEventListener("click", () => {
  const open = notes.classList.toggle("is-open");
  notes.setAttribute("aria-hidden", String(!open));
});
document.querySelector("#fullscreen").addEventListener("click", () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen();
});

document.addEventListener("keydown", (event) => {
  if (["ArrowRight", "PageDown", " "].includes(event.key)) { event.preventDefault(); go(1); }
  if (["ArrowLeft", "PageUp"].includes(event.key)) { event.preventDefault(); go(-1); }
  if (event.key === "Home") { index = 0; render(); }
  if (event.key === "End") { index = slides.length - 1; render(); }
  if (event.key.toLowerCase() === "n") document.querySelector("#notes-toggle").click();
  if (event.key.toLowerCase() === "f") document.querySelector("#fullscreen").click();
});

document.addEventListener("mousemove", () => {
  document.body.classList.remove("idle");
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => document.body.classList.add("idle"), 1800);
});

render();
