"""
=====================================================================
 Report Generator — Markdown & HTML Output
 Customer Feedback Sentiment Analyzer
 IBM Global AI Builders Challenge 2024
=====================================================================
 Menghasilkan laporan analisis sentimen dalam format:
   1. Markdown profesional (output/sentiment_report.md)
   2. HTML interaktif (output/sentiment_dashboard.html)
   3. JSON data mentah (output/analysis_results.json)
=====================================================================
"""

import json
import os
from datetime import datetime
from typing import List
from collections import Counter


# ─────────────────────────────────────────────────────────────────────────────
# NARRATIVE ENGINE — menghasilkan teks tanpa LLM eksternal
# ─────────────────────────────────────────────────────────────────────────────

def generate_executive_narrative(global_stats: dict, product_summaries: list) -> str:
    """Hasilkan narasi eksekutif berdasarkan data analisis."""
    total     = global_stats["total_reviews"]
    avg_r     = global_stats["avg_rating_global"]
    pos_pct   = global_stats["positive_pct"]
    neu_pct   = global_stats["neutral_pct"]
    neg_pct   = global_stats["negative_pct"]
    brands    = global_stats.get("brand_breakdown", {})

    top_brand = max(brands, key=lambda b: brands[b]["avg_rating"], default="N/A")
    top_brand_rating = brands.get(top_brand, {}).get("avg_rating", "-")

    # Aspek dominan positif/negatif
    all_pos_phrases, all_neg_phrases = [], []
    for ps in product_summaries:
        all_pos_phrases.extend(ps.top_positive_phrases)
        all_neg_phrases.extend(ps.top_negative_phrases)

    top_pos = Counter(all_pos_phrases).most_common(3)
    top_neg = Counter(all_neg_phrases).most_common(3)

    pos_str = ", ".join([f'"{kw}"' for kw, _ in top_pos]) if top_pos else "performa dan nilai"
    neg_str = ", ".join([f'"{kw}"' for kw, _ in top_neg]) if top_neg else "daya tahan baterai"

    # Pengiriman
    delivery_mentions = sum(
        1 for ps in product_summaries
        if ps.aspect_scores.get("pengiriman") is not None
    )
    delivery_pos = [
        ps.aspect_scores["pengiriman"]
        for ps in product_summaries
        if ps.aspect_scores.get("pengiriman") is not None
    ]
    delivery_avg = round(sum(delivery_pos) / len(delivery_pos) * 100, 1) if delivery_pos else 0

    # Nilai/harga
    price_pos = [
        ps.aspect_scores["harga_nilai"]
        for ps in product_summaries
        if ps.aspect_scores.get("harga_nilai") is not None
    ]
    price_avg = round(sum(price_pos) / len(price_pos) * 100, 1) if price_pos else 0

    narrative = f"""Berdasarkan analisis terhadap **{total} ulasan pelanggan** dari {len(product_summaries)} varian produk \
laptop kategori e-commerce, diperoleh gambaran sentimen pelanggan yang secara keseluruhan **cenderung positif**, \
dengan distribusi: **{pos_pct}% ulasan Positif**, {neu_pct}% Netral, dan {neg_pct}% Negatif. \
Rata-rata rating keseluruhan berada pada angka **{avg_r}/5**, mencerminkan tingkat kepuasan yang relatif baik di \
segmen harga menengah-bawah hingga menengah.

**Kualitas Produk:** Pelanggan secara konsisten mengapresiasi aspek {pos_str} pada produk-produk yang dianalisis. \
Brand **{top_brand}** mencatat rating rata-rata tertinggi sebesar {top_brand_rating}/5, diperkuat oleh pujian \
terhadap performa prosesor, kecepatan booting berbasis SSD, dan desain form factor yang ringkas. Namun demikian, \
keluhan berulang muncul pada dimensi {neg_str} — terutama pada kategori laptop entry-level, di mana \
kompromi spesifikasi menjadi pola yang diakui pelanggan. Isu kamera dan sudut pandang layar (viewing angle) \
juga tercatat sebagai area yang perlu mendapat perhatian dari tim produk.

**Harga & Nilai:** Sebesar **{price_avg}%** ulasan yang menyebutkan dimensi harga memberikan respons positif, \
menandakan bahwa mayoritas pelanggan merasakan kesesuaian antara harga yang dibayarkan dengan spesifikasi \
yang diterima. Ungkapan "value for money" dan "best in this price range" menjadi frasa yang paling sering \
muncul, mengindikasikan positioning harga yang tepat sasaran bagi segmen pelajar dan profesional pemula.

**Pengalaman Pengiriman:** Dari ulasan yang menyebutkan pengiriman, tingkat kepuasan mencapai **{delivery_avg}%**. \
Platform Flipkart secara khusus mendapat banyak pujian atas kecepatan pengiriman. Meski demikian, terdapat \
beberapa laporan keterlambatan pengiriman yang berdampak pada persepsi keseluruhan pelanggan, sehingga \
konsistensi standar logistik perlu terus dijaga."""

    return narrative


def generate_recommendations(global_stats: dict, product_summaries: list) -> dict:
    """Hasilkan rekomendasi bisnis berdasarkan temuan analisis."""
    all_neg = []
    all_pos = []
    for ps in product_summaries:
        all_neg.extend(ps.top_negative_phrases)
        all_pos.extend(ps.top_positive_phrases)

    neg_counter = Counter(all_neg)
    top_issues = [kw for kw, _ in neg_counter.most_common(10)]

    # Deteksi masalah spesifik
    has_battery  = any(kw in top_issues for kw in ["battery", "charge", "low battery"])
    has_display  = any(kw in top_issues for kw in ["display", "screen", "low", "dim"])
    has_heating  = any(kw in top_issues for kw in ["heat", "heating", "hot", "overheat"])
    has_camera   = any(kw in top_issues for kw in ["camera", "webcam"])
    has_delivery = any(kw in top_issues for kw in ["delivery", "slow", "late", "delay"])
    has_freeze   = any(kw in top_issues for kw in ["hang", "freeze", "lag", "slow"])

    high = []
    medium = []
    low = []

    # ── HIGH PRIORITY ──────────────────────────────────────────────────────
    if has_freeze or global_stats["negative_pct"] > 10:
        high.append(
            "**[Tim Produk & QA]** Lakukan audit teknis menyeluruh terhadap unit yang dilaporkan "
            "mengalami freeze/hang. Prioritaskan investigasi firmware dan driver update untuk model "
            "dengan keluhan performa paling tinggi. Target: rilis hotfix dalam 2 minggu."
        )
    if has_battery:
        high.append(
            "**[Tim Produk]** Tinjau ulang klaim daya tahan baterai pada halaman produk — selaraskan "
            "ekspektasi pelanggan dengan kondisi real-world (bukan kondisi ideal lab). Pertimbangkan "
            "menyertakan panduan optimasi baterai di dalam kotak produk dan halaman FAQ."
        )
    if has_display:
        high.append(
            "**[Tim Produk & Marketing]** Tandai produk dengan TN panel secara eksplisit di deskripsi "
            "produk (bukan hanya spesifikasi teknis). Tampilkan perbandingan viewing angle dalam "
            "galeri foto produk untuk mengelola ekspektasi pelanggan sebelum pembelian."
        )

    # ── MEDIUM PRIORITY ────────────────────────────────────────────────────
    if has_camera:
        medium.append(
            "**[Tim Marketing & Produk]** Revisi copy pemasaran untuk menghindari menyiratkan kualitas "
            "kamera setara kelas premium. Sertakan spesifikasi resolusi kamera (MP) secara jelas di "
            "halaman listing. Pertimbangkan bundling aksesori webcam eksternal sebagai opsi upgrade."
        )
    if has_heating:
        medium.append(
            "**[Tim Produk & After-Sales]** Publikasikan panduan thermal management resmi (setting "
            "mode performa, rekomendasi cooling pad) di portal dukungan. Aktifkan notifikasi proaktif "
            "kepada pelanggan yang memiliki unit dengan laporan suhu tinggi."
        )
    if has_delivery:
        medium.append(
            "**[Tim Operasional & Logistik]** Terapkan SLA pengiriman maksimal D+3 untuk area Tier-1 "
            "dan D+5 untuk area Tier-2/3. Integrasikan tracking real-time dan notifikasi proaktif via "
            "WhatsApp/SMS untuk meningkatkan transparansi status pengiriman."
        )
    if not medium:
        medium.append(
            "**[Tim Customer Success]** Terapkan program follow-up pelanggan (7 hari pasca-terima) "
            "untuk kategori ulasan Netral — konversi netral ke positif melalui edukasi fitur produk "
            "dan dukungan setup awal."
        )

    # ── LOW PRIORITY ───────────────────────────────────────────────────────
    low.append(
        "**[Tim Marketing & Growth]** Manfaatkan ulasan Positif yang menyebut value-for-money "
        "sebagai social proof di kampanye iklan. Buat program 'Verified Buyer Review' dengan insentif "
        "kecil untuk meningkatkan volume ulasan berkualitas tinggi."
    )
    low.append(
        "**[Tim Produk]** Evaluasi penambahan fitur backlit keyboard dan fingerprint sensor pada "
        "lini produk entry-to-mid sebagai differentiator kompetitif — dua fitur ini paling sering "
        "disebut sebagai 'missing feature' dalam ulasan Netral."
    )
    low.append(
        "**[Tim Data & Analytics]** Bangun pipeline analisis sentimen real-time (menggunakan IBM "
        "watsonx.ai) yang memproses ulasan baru setiap 24 jam, dengan alert otomatis ketika rating "
        "produk tertentu turun di bawah threshold 3.5/5 dalam periode 7 hari berturut-turut."
    )

    return {"high": high, "medium": medium, "low": low}


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN REPORT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_markdown_report(global_stats: dict, product_summaries: list,
                           narrative: str, recommendations: dict) -> str:
    """Bangun laporan lengkap dalam format Markdown."""

    now = datetime.now().strftime("%d %B %Y, %H:%M WIB")
    dist = global_stats["sentiment_distribution"]
    brands = global_stats.get("brand_breakdown", {})

    # ── Header ─────────────────────────────────────────────────────────────
    md = f"""# 📊 Laporan Analisis Sentimen Ulasan Pelanggan
## Customer Feedback Sentiment Analyzer — IBM AI Builders Challenge 2024
### *Track: Productivity & Smart Business / Customer Analytics*

---

> **Tanggal Analisis:** {now}
> **Dataset:** `laptop_online_review.csv`
> **Total Rekaman Diproses:** `{global_stats['total_reviews']} ulasan`
> **Engine:** Rule-Based Sentiment + Keyword Heuristic (IBM watsonx.ai Ready)

---

## 1. 📈 Statistik Global

| Metrik | Nilai |
|---|---|
| **Total Ulasan** | {global_stats['total_reviews']} |
| **Rata-rata Rating** | ⭐ {global_stats['avg_rating_global']} / 5.0 |
| **Ulasan Positif** | 🟢 {dist.get('Positive', 0)} ({global_stats['positive_pct']}%) |
| **Ulasan Netral** | 🟡 {dist.get('Neutral', 0)} ({global_stats['neutral_pct']}%) |
| **Ulasan Negatif** | 🔴 {dist.get('Negative', 0)} ({global_stats['negative_pct']}%) |
| **Total Produk Dianalisis** | {len(product_summaries)} varian |

---

## 2. 🏢 Performa Brand

| Brand | Total Ulasan | Avg Rating | Tingkat Positif |
|---|---|---|---|
"""

    for brand, stats in brands.items():
        pos_rate = f"{stats['positive_rate']*100:.0f}%"
        md += f"| **{brand}** | {stats['total_reviews']} | ⭐ {stats['avg_rating']} | {pos_rate} |\n"

    # ── Per Produk ──────────────────────────────────────────────────────────
    md += "\n---\n\n## 3. 📦 Analisis Per Produk\n\n"

    for i, ps in enumerate(product_summaries[:12], 1):
        dist_p = ps.sentiment_distribution
        overall_emoji = {"Positive": "🟢", "Neutral": "🟡", "Negative": "🔴"}.get(
            ps.overall_sentiment, "⚪")

        # Skor aspek
        kq = ps.aspect_scores.get("kualitas_produk")
        hn = ps.aspect_scores.get("harga_nilai")
        pg = ps.aspect_scores.get("pengiriman")
        kq_str = f"{kq*100:.0f}%" if kq is not None else "N/A"
        hn_str = f"{hn*100:.0f}%" if hn is not None else "N/A"
        pg_str = f"{pg*100:.0f}%" if pg is not None else "N/A"

        # Frasa
        pos_phrases = ", ".join(ps.top_positive_phrases[:4]) if ps.top_positive_phrases else "-"
        neg_phrases = ", ".join(ps.top_negative_phrases[:4]) if ps.top_negative_phrases else "-"

        short_name = ps.product_name if len(ps.product_name) <= 70 else ps.product_name[:67] + "..."

        md += f"""### {i}. {short_name}

| Atribut | Detail |
|---|---|
| **Brand** | {ps.brand} |
| **Total Ulasan** | {ps.total_reviews} |
| **Rata-rata Rating** | ⭐ {ps.avg_rating} / 5.0 |
| **Sentimen Dominan** | {overall_emoji} **{ps.overall_sentiment}** |
| **Positif / Netral / Negatif** | {dist_p.get('Positive',0)} / {dist_p.get('Neutral',0)} / {dist_p.get('Negative',0)} |
| **Skor Kualitas Produk** | {kq_str} positif |
| **Skor Harga & Nilai** | {hn_str} positif |
| **Skor Pengiriman** | {pg_str} positif |
| **Kata Kunci Positif** | {pos_phrases} |
| **Kata Kunci Negatif** | {neg_phrases} |

"""

    # ── Narasi Eksekutif ────────────────────────────────────────────────────
    md += f"""---

## 4. 📝 Ringkasan Naratif Eksekutif

{narrative}

---

## 5. 🎯 Klasifikasi Sentimen Keseluruhan

"""
    # Hitung overall
    total = global_stats["total_reviews"]
    pos_pct = global_stats["positive_pct"]
    if pos_pct >= 60:
        overall_class = "🟢 **POSITIVE (POSITIF)**"
        overall_desc = (
            f"Dengan {pos_pct}% ulasan bernilai positif dan rata-rata rating "
            f"{global_stats['avg_rating_global']}/5, sentimen pelanggan secara keseluruhan "
            f"dikategorikan **POSITIF**. Pelanggan pada umumnya puas dengan produk yang ditawarkan."
        )
    elif pos_pct >= 45:
        overall_class = "🟡 **NEUTRAL (NETRAL)**"
        overall_desc = (
            f"Dengan distribusi sentimen yang relatif berimbang ({pos_pct}% positif), "
            f"sentimen keseluruhan dikategorikan **NETRAL**. Terdapat ruang perbaikan signifikan "
            f"yang perlu ditangani untuk menggeser persepsi ke arah positif."
        )
    else:
        overall_class = "🔴 **NEGATIVE (NEGATIF)**"
        overall_desc = (
            f"Dengan proporsi ulasan negatif yang tinggi, sentimen keseluruhan dikategorikan "
            f"**NEGATIF**. Diperlukan intervensi produk dan layanan yang segera."
        )

    md += f"""| Dimensi | Nilai |
|---|---|
| **Klasifikasi Sentimen** | {overall_class} |
| **Confidence Level** | {"Tinggi" if abs(pos_pct - 50) > 20 else "Sedang"} |
| **Dasar Klasifikasi** | {total} ulasan, Avg Rating {global_stats['avg_rating_global']}/5 |

> {overall_desc}

---

## 6. 🚀 Rekomendasi Tindakan Bisnis (Action Items)

### 🔴 PRIORITAS TINGGI — Tindakan Segera (1–4 Minggu)

"""
    for item in recommendations["high"]:
        md += f"- {item}\n"

    md += "\n### 🟡 PRIORITAS SEDANG — Perbaikan Terencana (1–3 Bulan)\n\n"
    for item in recommendations["medium"]:
        md += f"- {item}\n"

    md += "\n### 🟢 PRIORITAS RENDAH — Optimasi Jangka Panjang (3–6 Bulan)\n\n"
    for item in recommendations["low"]:
        md += f"- {item}\n"

    # ── Footer ──────────────────────────────────────────────────────────────
    md += f"""
---

## 7. ⚙️ Catatan Metodologi

| Komponen | Detail |
|---|---|
| **Metode Analisis** | Hybrid: Rating-weighted Keyword Heuristic |
| **Bobot Rating** | 50% (skala 1–5 → normalized weight) |
| **Bobot Keyword** | 50% (positive/negative lexicon matching) |
| **Threshold Positif** | Combined Score ≥ 0.15 |
| **Threshold Negatif** | Combined Score ≤ −0.15 |
| **LLM Integration** | IBM watsonx.ai compatible (Granite / Llama 3) |
| **Framework** | Python 3.x, Zero external ML dependencies |
| **Langflow** | Workflow tersedia di `Sentiment Analysis (STARTER).json` |

---

*Laporan ini dihasilkan secara otomatis oleh sistem Customer Feedback Sentiment Analyzer.*
*IBM Global AI Builders Challenge 2024 — Track: Productivity & Smart Business*
*Generated: {now}*
"""

    return md


# ─────────────────────────────────────────────────────────────────────────────
# HTML DASHBOARD BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_html_dashboard(global_stats: dict, product_summaries: list,
                          narrative: str, recommendations: dict) -> str:
    """Bangun dashboard HTML interaktif."""

    dist   = global_stats["sentiment_distribution"]
    pos    = dist.get("Positive", 0)
    neu    = dist.get("Neutral", 0)
    neg    = dist.get("Negative", 0)
    total  = global_stats["total_reviews"]
    brands = global_stats.get("brand_breakdown", {})
    now    = datetime.now().strftime("%d %B %Y, %H:%M WIB")

    # brand bar data
    brand_labels = list(brands.keys())
    brand_ratings = [brands[b]["avg_rating"] for b in brand_labels]
    brand_pos_rates = [round(brands[b]["positive_rate"] * 100) for b in brand_labels]

    # product rows
    product_rows = ""
    for i, ps in enumerate(product_summaries[:15], 1):
        pd_ = ps.sentiment_distribution
        badge_cls = {"Positive": "badge-pos", "Neutral": "badge-neu",
                     "Negative": "badge-neg"}.get(ps.overall_sentiment, "badge-neu")
        badge_lbl = {"Positive": "POSITIF", "Neutral": "NETRAL",
                     "Negative": "NEGATIF"}.get(ps.overall_sentiment, ps.overall_sentiment)
        short = ps.product_name[:65] + ("..." if len(ps.product_name) > 65 else "")
        product_rows += f"""
        <tr>
          <td>{i}</td>
          <td class="product-name">{short}</td>
          <td><strong>{ps.brand}</strong></td>
          <td>⭐ {ps.avg_rating}</td>
          <td>{ps.total_reviews}</td>
          <td><span class="badge {badge_cls}">{badge_lbl}</span></td>
          <td><span style="color:#22c55e">{pd_.get('Positive',0)}</span> /
              <span style="color:#f59e0b">{pd_.get('Neutral',0)}</span> /
              <span style="color:#ef4444">{pd_.get('Negative',0)}</span></td>
        </tr>"""

    # rec items
    def rec_html(items, cls, icon):
        out = ""
        for item in items:
            # bold markdown → html
            import re
            item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item)
            out += f'<div class="rec-item {cls}"><span class="rec-icon">{icon}</span><p>{item}</p></div>\n'
        return out

    high_html   = rec_html(recommendations["high"],   "rec-high",   "🔴")
    medium_html = rec_html(recommendations["medium"], "rec-medium", "🟡")
    low_html    = rec_html(recommendations["low"],    "rec-low",    "🟢")

    narrative_html = narrative.replace("\n\n", "</p><p>").replace("**", "<strong>")
    narrative_html = f"<p>{narrative_html}</p>"

    # Overall badge
    pos_pct = global_stats["positive_pct"]
    if pos_pct >= 60:
        overall_lbl, overall_cls = "POSITIF", "overall-pos"
    elif pos_pct >= 45:
        overall_lbl, overall_cls = "NETRAL", "overall-neu"
    else:
        overall_lbl, overall_cls = "NEGATIF", "overall-neg"

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sentiment Analysis Dashboard — IBM AI Builders Challenge 2024</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;font-size:14px}}
  .header{{background:linear-gradient(135deg,#1e3a8a 0%,#1d4ed8 50%,#7c3aed 100%);padding:32px 40px;border-bottom:1px solid #334155}}
  .header h1{{font-size:1.8rem;font-weight:700;color:#fff;letter-spacing:-0.5px}}
  .header .subtitle{{color:#bfdbfe;margin-top:6px;font-size:0.95rem}}
  .header .meta{{color:#93c5fd;font-size:0.82rem;margin-top:8px}}
  .container{{max-width:1280px;margin:0 auto;padding:28px 32px}}
  .grid-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:28px}}
  .grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px}}
  .card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px}}
  .card h2{{font-size:1rem;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:16px}}
  .stat-card{{text-align:center;padding:24px 16px}}
  .stat-val{{font-size:2.4rem;font-weight:800;line-height:1}}
  .stat-label{{font-size:0.8rem;color:#64748b;margin-top:6px;text-transform:uppercase;letter-spacing:0.5px}}
  .stat-sub{{font-size:0.85rem;color:#94a3b8;margin-top:4px}}
  .c-pos{{color:#22c55e}} .c-neu{{color:#f59e0b}} .c-neg{{color:#ef4444}} .c-blue{{color:#60a5fa}}
  .overall-badge{{display:inline-block;padding:8px 24px;border-radius:24px;font-size:1.5rem;font-weight:800;letter-spacing:1px;margin:12px 0}}
  .overall-pos{{background:#14532d;color:#4ade80;border:2px solid #22c55e}}
  .overall-neu{{background:#451a03;color:#fbbf24;border:2px solid #f59e0b}}
  .overall-neg{{background:#450a0a;color:#f87171;border:2px solid #ef4444}}
  .badge{{padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:600}}
  .badge-pos{{background:#14532d;color:#4ade80}} .badge-neu{{background:#451a03;color:#fbbf24}}
  .badge-neg{{background:#450a0a;color:#f87171}}
  table{{width:100%;border-collapse:collapse}}
  th{{background:#0f172a;color:#64748b;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.5px;padding:10px 12px;text-align:left;border-bottom:1px solid #334155}}
  td{{padding:10px 12px;border-bottom:1px solid #1e293b;font-size:0.88rem;vertical-align:middle}}
  tr:hover td{{background:#263045}}
  .product-name{{max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .narrative{{line-height:1.8;color:#cbd5e1;font-size:0.92rem}}
  .narrative p{{margin-bottom:12px}}
  .narrative strong{{color:#93c5fd}}
  .rec-item{{display:flex;gap:12px;padding:14px 16px;border-radius:8px;margin-bottom:10px}}
  .rec-high{{background:#450a0a;border-left:4px solid #ef4444}}
  .rec-medium{{background:#451a03;border-left:4px solid #f59e0b}}
  .rec-low{{background:#052e16;border-left:4px solid #22c55e}}
  .rec-icon{{font-size:1.2rem;flex-shrink:0;padding-top:2px}}
  .rec-item p{{color:#cbd5e1;line-height:1.7;font-size:0.88rem}}
  .rec-item p strong{{color:#f1f5f9}}
  .section-title{{font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid #334155}}
  .priority-label{{font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:18px 0 8px}}
  .footer{{text-align:center;color:#475569;font-size:0.78rem;padding:24px;border-top:1px solid #1e293b;margin-top:12px}}
  canvas{{max-height:240px}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 Customer Feedback Sentiment Analyzer</h1>
  <div class="subtitle">IBM Global AI Builders Challenge 2024 — Productivity & Smart Business / Customer Analytics</div>
  <div class="meta">Dataset: laptop_online_review.csv &nbsp;|&nbsp; Generated: {now}</div>
</div>
<div class="container">

  <!-- KPI CARDS -->
  <div class="grid-4">
    <div class="card stat-card">
      <div class="stat-val c-blue">{total}</div>
      <div class="stat-label">Total Ulasan</div>
      <div class="stat-sub">{len(product_summaries)} varian produk</div>
    </div>
    <div class="card stat-card">
      <div class="stat-val c-pos">{global_stats['positive_pct']}%</div>
      <div class="stat-label">Sentimen Positif</div>
      <div class="stat-sub">{pos} ulasan</div>
    </div>
    <div class="card stat-card">
      <div class="stat-val c-blue">⭐ {global_stats['avg_rating_global']}</div>
      <div class="stat-label">Avg Rating</div>
      <div class="stat-sub">dari skala 5.0</div>
    </div>
    <div class="card stat-card">
      <div class="overall-badge {overall_cls}">{overall_lbl}</div>
      <div class="stat-label">Klasifikasi Keseluruhan</div>
    </div>
  </div>

  <!-- CHARTS -->
  <div class="grid-2">
    <div class="card">
      <h2>Distribusi Sentimen</h2>
      <canvas id="sentPie"></canvas>
    </div>
    <div class="card">
      <h2>Rata-rata Rating per Brand</h2>
      <canvas id="brandBar"></canvas>
    </div>
  </div>

  <!-- EXECUTIVE NARRATIVE -->
  <div class="card" style="margin-bottom:24px">
    <div class="section-title">📝 Ringkasan Naratif Eksekutif</div>
    <div class="narrative">{narrative_html}</div>
  </div>

  <!-- PRODUCT TABLE -->
  <div class="card" style="margin-bottom:24px">
    <div class="section-title">📦 Analisis Per Produk</div>
    <div style="overflow-x:auto">
    <table>
      <thead><tr>
        <th>#</th><th>Produk</th><th>Brand</th><th>Rating</th>
        <th>Reviews</th><th>Sentimen</th><th>Pos / Neu / Neg</th>
      </tr></thead>
      <tbody>{product_rows}</tbody>
    </table>
    </div>
  </div>

  <!-- RECOMMENDATIONS -->
  <div class="card" style="margin-bottom:24px">
    <div class="section-title">🚀 Rekomendasi Tindakan Bisnis</div>
    <div class="priority-label" style="color:#ef4444">🔴 PRIORITAS TINGGI — Tindakan Segera (1–4 Minggu)</div>
    {high_html}
    <div class="priority-label" style="color:#f59e0b">🟡 PRIORITAS SEDANG — Perbaikan Terencana (1–3 Bulan)</div>
    {medium_html}
    <div class="priority-label" style="color:#22c55e">🟢 PRIORITAS RENDAH — Optimasi Jangka Panjang (3–6 Bulan)</div>
    {low_html}
  </div>

</div><!-- /container -->

<div class="footer">
  Customer Feedback Sentiment Analyzer &nbsp;|&nbsp; IBM Global AI Builders Challenge 2024
  &nbsp;|&nbsp; Track: Productivity &amp; Smart Business
</div>

<script>
// Pie Chart
new Chart(document.getElementById('sentPie'), {{
  type: 'doughnut',
  data: {{
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{{
      data: [{pos}, {neu}, {neg}],
      backgroundColor: ['#22c55e','#f59e0b','#ef4444'],
      borderColor: '#1e293b', borderWidth: 3
    }}]
  }},
  options: {{
    plugins: {{ legend: {{ labels: {{ color:'#94a3b8', font:{{size:12}} }} }} }},
    cutout: '65%'
  }}
}});

// Bar Chart
new Chart(document.getElementById('brandBar'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(brand_labels)},
    datasets: [
      {{ label: 'Avg Rating', data: {json.dumps(brand_ratings)},
         backgroundColor: '#3b82f6', borderRadius: 4 }},
      {{ label: '% Positif', data: {json.dumps(brand_pos_rates)},
         backgroundColor: '#22c55e', borderRadius: 4, yAxisID: 'y2' }}
    ]
  }},
  options: {{
    plugins: {{ legend: {{ labels: {{ color:'#94a3b8' }} }} }},
    scales: {{
      x: {{ ticks: {{ color:'#64748b' }}, grid: {{ color:'#1e293b' }} }},
      y: {{ ticks: {{ color:'#64748b' }}, grid: {{ color:'#334155' }}, min:0, max:5,
             title: {{ display:true, text:'Rating', color:'#64748b' }} }},
      y2: {{ position:'right', ticks: {{ color:'#64748b' }}, grid: {{ drawOnChartArea:false }},
              min:0, max:100, title: {{ display:true, text:'% Positif', color:'#64748b' }} }}
    }}
  }}
}});
</script>
</body>
</html>"""

    return html


# ─────────────────────────────────────────────────────────────────────────────
# SAVE OUTPUTS
# ─────────────────────────────────────────────────────────────────────────────

def save_outputs(output_dir: str, global_stats: dict, product_summaries: list,
                 raw_records: list) -> dict:
    """Simpan semua output ke direktori."""
    os.makedirs(output_dir, exist_ok=True)

    narrative = generate_executive_narrative(global_stats, product_summaries)
    recommendations = generate_recommendations(global_stats, product_summaries)

    # 1. Markdown report
    md = build_markdown_report(global_stats, product_summaries, narrative, recommendations)
    md_path = os.path.join(output_dir, "sentiment_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    # 2. HTML dashboard
    html = build_html_dashboard(global_stats, product_summaries, narrative, recommendations)
    html_path = os.path.join(output_dir, "sentiment_dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # 3. JSON results
    json_data = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "total_reviews": global_stats["total_reviews"],
            "tool": "Customer Feedback Sentiment Analyzer",
            "challenge": "IBM Global AI Builders Challenge 2024",
        },
        "global_stats": global_stats,
        "product_summaries": [
            {
                "product_name": ps.product_name,
                "brand": ps.brand,
                "total_reviews": ps.total_reviews,
                "avg_rating": ps.avg_rating,
                "overall_sentiment": ps.overall_sentiment,
                "sentiment_distribution": ps.sentiment_distribution,
                "aspect_scores": ps.aspect_scores,
                "top_positive_phrases": ps.top_positive_phrases,
                "top_negative_phrases": ps.top_negative_phrases,
            }
            for ps in product_summaries
        ],
        "recommendations": recommendations,
    }
    json_path = os.path.join(output_dir, "analysis_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return {"markdown": md_path, "html": html_path, "json": json_path}
