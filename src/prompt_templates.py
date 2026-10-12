"""
=====================================================================
 Prompt Engineering Module — IBM watsonx.ai Ready
 Customer Feedback Sentiment Analyzer
 IBM Global AI Builders Challenge 2024
=====================================================================
 Modul ini menyimpan semua template prompt yang dirancang khusus
 untuk digunakan bersama IBM watsonx.ai (model: ibm/granite-13b-chat-v2
 atau meta-llama/llama-3-70b-instruct). Prompt dirancang menggunakan
 teknik: Chain-of-Thought (CoT), Few-Shot Exemplar, Role Prompting,
 dan Structured Output Constraint.
=====================================================================
"""

from typing import List, Dict, Optional


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT TEMPLATE 1 — ANALISIS SENTIMEN PER PRODUK
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_SENTIMENT_CLASSIFICATION = """Anda adalah sistem analis sentimen profesional untuk platform e-commerce. \
Tugas Anda adalah mengklasifikasikan sentimen ulasan pelanggan secara akurat dan objektif.

### INSTRUKSI:
1. Baca setiap ulasan dengan seksama.
2. Pertimbangkan konteks keseluruhan, bukan hanya kata-kata tunggal.
3. Rating numerik (1-5) adalah sinyal tambahan, bukan penentu utama.
4. Klasifikasikan menjadi salah satu dari tiga kategori: Positive, Neutral, atau Negative.
5. Berikan confidence score (0.0 - 1.0).

### DEFINISI KATEGORI:
- **Positive**: Ulasan mengungkapkan kepuasan, apresiasi, atau rekomendasi. Rating ≥ 4 umumnya positif.
- **Neutral**: Ulasan bersifat deskriptif, campuran pro-kontra seimbang, atau kurang ekspresif. Rating = 3.
- **Negative**: Ulasan mengungkapkan kekecewaan, keluhan, atau masalah signifikan. Rating ≤ 2 umumnya negatif.

### FEW-SHOT CONTOH:
Ulasan: "Great performance but battery is terrible, lasts only 2 hours."
Rating: 3
→ Sentiment: Neutral | Confidence: 0.62
Alasan: Pro (performa) dan kontra (baterai) berimbang, rating 3 mendukung netral.

Ulasan: "Amazing laptop, fast boot, excellent display, value for money!"
Rating: 5
→ Sentiment: Positive | Confidence: 0.95
Alasan: Ekspresi positif dominan, tidak ada keluhan, rating 5.

Ulasan: "Worst purchase. Screen flickering, keyboard not working, totally wasted money."
Rating: 1
→ Sentiment: Negative | Confidence: 0.98
Alasan: Keluhan spesifik dan serius, ekspresi kekecewaan kuat, rating 1.

### DATA INPUT:
Nama Produk: {product_name}
Ulasan: {review_text}
Rating: {rating}/5

### OUTPUT FORMAT (JSON):
{{
  "sentiment": "<Positive|Neutral|Negative>",
  "confidence": <0.0-1.0>,
  "key_phrases": ["<frasa1>", "<frasa2>", "<frasa3>"],
  "reasoning": "<penjelasan singkat 1-2 kalimat>"
}}
"""


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT TEMPLATE 2 — RINGKASAN NARATIF EKSEKUTIF
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_EXECUTIVE_SUMMARY = """Anda adalah seorang analis bisnis senior yang berpengalaman dalam \
menginterpretasikan data ulasan pelanggan untuk keperluan pengambilan keputusan strategis.

### KONTEKS:
Anda sedang menganalisis {total_reviews} ulasan pelanggan untuk produk laptop kategori e-commerce. \
Data mencakup {total_products} varian produk dari brand: {brands}.

### STATISTIK GLOBAL:
- Total Ulasan: {total_reviews}
- Rata-rata Rating: {avg_rating}/5
- Distribusi Sentimen: Positive {positive_pct}% | Neutral {neutral_pct}% | Negative {negative_pct}%
- Brand dengan Rating Tertinggi: {top_brand}

### RINGKASAN PER PRODUK:
{product_summaries_text}

### TUGAS:
Buat ringkasan naratif eksekutif yang kohesif dan profesional dalam Bahasa Indonesia, \
mencakup tiga dimensi berikut:

1. **Kualitas Produk**: Bagaimana persepsi pelanggan terhadap build quality, performa, \
   display, keyboard, dan komponen hardware secara keseluruhan?

2. **Harga & Nilai**: Apakah pelanggan merasa produk-produk ini memberikan value for money? \
   Segmen harga mana yang paling diapresiasi?

3. **Pengalaman Pengiriman**: Bagaimana pengalaman pelanggan terkait kecepatan, \
   kondisi packaging, dan ketepatan waktu pengiriman?

### KETENTUAN PENULISAN:
- Panjang narasi: 150-250 kata
- Nada: objektif, presisi, profesional
- Hindari generalisasi berlebihan
- Sertakan data/angka spesifik bila relevan
- Tulis dalam paragraf, bukan bullet point

### OUTPUT:
Tulis hanya narasi ringkasan, tanpa header tambahan.
"""


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT TEMPLATE 3 — REKOMENDASI BISNIS ACTIONABLE
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_BUSINESS_RECOMMENDATIONS = """Anda adalah konsultan strategi produk dan operasional e-commerce \
yang membantu tim produk dan tim operasional mengidentifikasi area perbaikan berdasarkan \
analisis umpan balik pelanggan.

### DATA ANALISIS:
- Total Ulasan Diproses: {total_reviews}
- Overall Sentiment: {overall_sentiment}
- Rating Rata-rata: {avg_rating}/5
- Tingkat Ulasan Negatif: {negative_pct}%

### KELUHAN UTAMA YANG TERDETEKSI:
{top_complaints}

### PUJIAN UTAMA YANG TERDETEKSI:
{top_praises}

### ASPEK DENGAN SKOR TERENDAH:
{weak_aspects}

### ASPEK DENGAN SKOR TERTINGGI:
{strong_aspects}

### TUGAS:
Hasilkan rekomendasi tindakan bisnis yang konkret, spesifik, dan dapat langsung dieksekusi. \
Kelompokkan berdasarkan tingkat prioritas:

**🔴 PRIORITAS TINGGI (High Priority)** — Masalah kritis yang berdampak langsung pada \
kepuasan pelanggan dan reputasi brand. Harus ditangani dalam 1-4 minggu.

**🟡 PRIORITAS SEDANG (Medium Priority)** — Area perbaikan signifikan yang memengaruhi \
pengalaman pengguna. Target penyelesaian dalam 1-3 bulan.

**🟢 PRIORITAS RENDAH (Low Priority)** — Optimasi tambahan untuk meningkatkan keunggulan \
kompetitif. Target jangka panjang 3-6 bulan.

### KETENTUAN:
- Setiap rekomendasi harus SPESIFIK dan TERUKUR (bukan saran generik)
- Sertakan tim/departemen yang bertanggung jawab (Produk/Operasional/Logistik/Marketing)
- Format: bullet point terstruktur per kategori prioritas
- Bahasa: Indonesia yang formal dan profesional
- Maksimum 3 rekomendasi per level prioritas

### OUTPUT FORMAT:
Keluarkan hanya daftar rekomendasi terstruktur tanpa pembukaan tambahan.
"""


# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI BUILDER PROMPT
# ─────────────────────────────────────────────────────────────────────────────

def build_sentiment_prompt(product_name: str, review_text: str, rating: int) -> str:
    """Bangun prompt klasifikasi sentimen untuk satu ulasan."""
    return PROMPT_SENTIMENT_CLASSIFICATION.format(
        product_name=product_name,
        review_text=review_text,
        rating=rating,
    )


def build_executive_summary_prompt(global_stats: dict, product_summaries: list) -> str:
    """Bangun prompt ringkasan eksekutif."""
    brands = list(global_stats.get("brand_breakdown", {}).keys())
    brand_str = ", ".join(brands[:6])

    top_brand = max(
        global_stats.get("brand_breakdown", {}).items(),
        key=lambda x: x[1]["avg_rating"],
        default=("N/A", {}),
    )[0]

    # Ringkas data produk ke teks
    product_lines = []
    for ps in product_summaries[:8]:
        dist = ps.sentiment_distribution
        line = (
            f"- {ps.product_name[:50]}... | Brand: {ps.brand} | "
            f"Rating: {ps.avg_rating}/5 | Reviews: {ps.total_reviews} | "
            f"Pos:{dist.get('Positive',0)} Neu:{dist.get('Neutral',0)} Neg:{dist.get('Negative',0)}"
        )
        product_lines.append(line)
    product_text = "\n".join(product_lines)

    return PROMPT_EXECUTIVE_SUMMARY.format(
        total_reviews=global_stats["total_reviews"],
        total_products=len(product_summaries),
        brands=brand_str,
        avg_rating=global_stats["avg_rating_global"],
        positive_pct=global_stats["positive_pct"],
        neutral_pct=global_stats["neutral_pct"],
        negative_pct=global_stats["negative_pct"],
        top_brand=top_brand,
        product_summaries_text=product_text,
    )


def build_recommendations_prompt(global_stats: dict, product_summaries: list) -> str:
    """Bangun prompt rekomendasi bisnis."""
    # Kumpulkan keluhan dan pujian dari semua produk
    all_complaints = []
    all_praises = []
    aspect_scores_agg: Dict[str, List[float]] = {}

    for ps in product_summaries:
        all_complaints.extend(ps.top_negative_phrases)
        all_praises.extend(ps.top_positive_phrases)
        for asp, score in ps.aspect_scores.items():
            if score is not None:
                aspect_scores_agg.setdefault(asp, []).append(score)

    # Hitung rata-rata aspek
    aspect_avg = {
        asp: round(sum(scores) / len(scores), 2)
        for asp, scores in aspect_scores_agg.items()
        if scores
    }

    from collections import Counter
    complaint_counter = Counter(all_complaints)
    praise_counter = Counter(all_praises)

    top_complaints_str = ", ".join([f"{kw} ({cnt}x)"
                                     for kw, cnt in complaint_counter.most_common(6)])
    top_praises_str = ", ".join([f"{kw} ({cnt}x)"
                                  for kw, cnt in praise_counter.most_common(6)])

    sorted_aspects = sorted(aspect_avg.items(), key=lambda x: x[1])
    weak_str = ", ".join([f"{k}: {v*100:.0f}%" for k, v in sorted_aspects[:2]])
    strong_str = ", ".join([f"{k}: {v*100:.0f}%" for k, v in reversed(sorted_aspects[-2:])])

    # Overall sentiment
    dist = global_stats["sentiment_distribution"]
    dominant = max(dist, key=lambda k: dist[k])
    sent_label_map = {"Positive": "POSITIF", "Neutral": "NETRAL", "Negative": "NEGATIF"}
    overall = sent_label_map.get(dominant, dominant)

    return PROMPT_BUSINESS_RECOMMENDATIONS.format(
        total_reviews=global_stats["total_reviews"],
        overall_sentiment=overall,
        avg_rating=global_stats["avg_rating_global"],
        negative_pct=global_stats["negative_pct"],
        top_complaints=top_complaints_str if top_complaints_str else "Tidak ada data",
        top_praises=top_praises_str if top_praises_str else "Tidak ada data",
        weak_aspects=weak_str if weak_str else "Tidak ada data",
        strong_aspects=strong_str if strong_str else "Tidak ada data",
    )


# ─────────────────────────────────────────────────────────────────────────────
# WATSONX API INTEGRATION TEMPLATE (opsional, butuh kredensial)
# ─────────────────────────────────────────────────────────────────────────────

WATSONX_CONFIG = {
    "model_id": "ibm/granite-13b-chat-v2",
    "parameters": {
        "decoding_method": "greedy",
        "max_new_tokens": 800,
        "repetition_penalty": 1.1,
        "temperature": 0.3,
        "top_p": 0.9,
    },
    "project_id": "<YOUR_WATSONX_PROJECT_ID>",
    "url": "https://us-south.ml.cloud.ibm.com",
}


def call_watsonx_placeholder(prompt: str, config: dict = WATSONX_CONFIG) -> str:
    """
    Placeholder untuk panggilan IBM watsonx.ai API.
    Aktifkan dengan menginstal: pip install ibm-watsonx-ai
    dan mengisi WATSONX_CONFIG dengan kredensial valid.

    Contoh implementasi nyata:
    ─────────────────────────────
    from ibm_watsonx_ai.foundation_models import Model

    model = Model(
        model_id=config["model_id"],
        credentials={"apikey": "<API_KEY>", "url": config["url"]},
        project_id=config["project_id"],
        params=config["parameters"],
    )
    return model.generate_text(prompt=prompt)
    """
    return f"[WATSONX_PLACEHOLDER] Prompt diterima ({len(prompt)} karakter). " \
           f"Hubungkan ke IBM watsonx.ai untuk respons generatif."


if __name__ == "__main__":
    # Demo prompt
    sample_prompt = build_sentiment_prompt(
        product_name="Lenovo IdeaPad 3 Core i3 11th Gen",
        review_text="Great laptop for students! Fast boot, good display. Battery could be better.",
        rating=4,
    )
    print("=== SAMPLE SENTIMENT PROMPT ===")
    print(sample_prompt[:600])
    print("...")
