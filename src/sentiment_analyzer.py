"""
=====================================================================
 Customer Feedback Sentiment Analyzer — Core Engine
 IBM Global AI Builders Challenge 2024
 Track: Productivity & Smart Business / Customer Analytics
=====================================================================
 Modul ini menjalankan analisis sentimen berbasis aturan (rule-based)
 dan keyword heuristic tanpa dependensi LLM eksternal, sepenuhnya
 reproducible dan deterministik. Output-nya kompatibel dengan
 pipeline IBM watsonx.ai sebagai pre-processor atau standalone tool.
=====================================================================
"""

import csv
import re
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI LEKSIKON SENTIMEN
# ─────────────────────────────────────────────────────────────────────────────

POSITIVE_KEYWORDS = [
    "good", "great", "excellent", "amazing", "awesome", "best", "love",
    "wonderful", "fantastic", "superb", "outstanding", "perfect", "happy",
    "satisfied", "recommend", "fast", "quick", "smooth", "nice", "brilliant",
    "impressive", "value", "worth", "affordable", "premium", "sturdy",
    "reliable", "efficient", "powerful", "responsive", "lightweight",
    "classy", "sleek", "stunning", "incredible", "mind blowing", "mindblowing",
    "speedy", "instant", "gorgeous", "beautiful", "lovely", "solid",
    "durable", "handy", "comfortable", "convenient", "easy", "simple",
    "decent", "reasonable", "budget", "bargain", "deal",
]

NEGATIVE_KEYWORDS = [
    "bad", "worst", "terrible", "poor", "horrible", "awful", "disappointed",
    "disappoint", "waste", "broken", "defective", "slow", "lag", "hang",
    "freeze", "overheat", "heat", "heating", "noisy", "noise", "loud fan",
    "cheap", "flimsy", "low quality", "not good", "not great", "issue",
    "problem", "fault", "defect", "missing", "lack", "weak", "dim",
    "scratched", "dead", "damaged", "return", "refund", "failure",
    "not working", "doesn't work", "won't work", "not worth", "regret",
    "avoid", "useless", "pathetic", "worst", "never buy", "do not buy",
]

NEUTRAL_NEGATION_PATTERNS = [
    r"not bad", r"not terrible", r"not awful", r"not the worst",
]

# Aspek dimensi produk
ASPECT_KEYWORDS = {
    "kualitas_produk": [
        "build", "quality", "performance", "processor", "cpu", "gpu",
        "display", "screen", "keyboard", "trackpad", "touchpad", "speaker",
        "camera", "webcam", "ram", "ssd", "storage", "design", "body",
        "weight", "lightweight", "sturdy", "durable", "plastic", "metal",
        "hinge", "port", "connectivity", "wifi", "bluetooth",
    ],
    "harga_nilai": [
        "price", "cost", "value", "worth", "money", "budget", "affordable",
        "expensive", "cheap", "rupee", "rs.", "rs ", "₹", "k ", "thousand",
        "deal", "sale", "discount", "offer", "segment", "range", "rate",
    ],
    "pengiriman": [
        "delivery", "deliver", "shipping", "ship", "package", "packaging",
        "arrive", "arrived", "received", "dispatch", "flipkart", "amazon",
        "courier", "fast delivery", "quick delivery", "late delivery",
        "delay", "days", "on time", "timely",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# STRUKTUR DATA
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ReviewRecord:
    index: int
    product_name: str
    brand: str
    review: str
    rating: int
    sentiment_label: str = ""
    sentiment_score: float = 0.0
    aspects_detected: List[str] = field(default_factory=list)


@dataclass
class ProductSummary:
    product_name: str
    brand: str
    total_reviews: int
    avg_rating: float
    sentiment_distribution: Dict[str, int] = field(default_factory=dict)
    top_positive_phrases: List[str] = field(default_factory=list)
    top_negative_phrases: List[str] = field(default_factory=list)
    aspect_scores: Dict[str, float] = field(default_factory=dict)
    overall_sentiment: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI UTILITAS
# ─────────────────────────────────────────────────────────────────────────────

def extract_brand(product_name: str) -> str:
    """Ekstrak nama brand dari nama produk."""
    brands = ["lenovo", "dell", "hp", "asus", "acer", "apple", "redmi",
              "mi", "samsung", "msi", "gigabyte", "razer"]
    lower = product_name.lower()
    for brand in brands:
        if brand in lower:
            return brand.capitalize()
    return product_name.split()[0].capitalize()


def clean_text(text: str) -> str:
    """Normalisasi teks ulasan."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s\.\,\!\?]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def score_sentiment(text: str, rating: int) -> Tuple[str, float]:
    """
    Menghitung skor sentimen gabungan dari teks + rating.
    Mengembalikan (label, confidence_score 0.0-1.0).
    """
    cleaned = clean_text(text)

    # Netral negatif override check
    for pat in NEUTRAL_NEGATION_PATTERNS:
        cleaned = re.sub(pat, "NEUTRAL_NEG_OVERRIDE", cleaned)

    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in cleaned)
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in cleaned)

    # Bobot dari rating (skala 1-5)
    # Rating 1-2 → strong negative weight, 3 → neutral, 4-5 → positive weight
    rating_weight = (rating - 3) * 0.4  # range -0.8 to 0.8

    # Skor sentimen mentah: rentang -1.0 (sangat negatif) ke +1.0 (sangat positif)
    total_keywords = pos_count + neg_count
    if total_keywords == 0:
        keyword_score = 0.0
    else:
        keyword_score = (pos_count - neg_count) / max(total_keywords, 1)

    combined_score = (keyword_score * 0.5) + (rating_weight * 0.5)
    combined_score = max(-1.0, min(1.0, combined_score))

    # Klasifikasi label
    if combined_score >= 0.15:
        label = "Positive"
    elif combined_score <= -0.15:
        label = "Negative"
    else:
        label = "Neutral"

    # Confidence (0.0 - 1.0)
    confidence = abs(combined_score)

    return label, round(confidence, 3)


def detect_aspects(text: str) -> List[str]:
    """Deteksi aspek produk yang disebutkan dalam ulasan."""
    cleaned = clean_text(text)
    detected = []
    for aspect, keywords in ASPECT_KEYWORDS.items():
        if any(kw in cleaned for kw in keywords):
            detected.append(aspect)
    return detected


def extract_key_phrases(reviews: List[str], sentiment: str) -> List[str]:
    """
    Ekstrak frasa kunci yang paling sering muncul sesuai sentimen.
    """
    word_freq = defaultdict(int)
    target_kws = POSITIVE_KEYWORDS if sentiment == "positive" else NEGATIVE_KEYWORDS

    for review in reviews:
        cleaned = clean_text(review)
        for kw in target_kws:
            if kw in cleaned:
                word_freq[kw] += 1

    sorted_phrases = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [phrase for phrase, _ in sorted_phrases[:8]]


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE UTAMA
# ─────────────────────────────────────────────────────────────────────────────

def load_dataset(filepath: str) -> List[ReviewRecord]:
    """Muat dan parsing dataset CSV ulasan."""
    records = []
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rating = int(float(row.get("Rating", 3)))
                rating = max(1, min(5, rating))
            except (ValueError, TypeError):
                rating = 3

            product_name = row.get("Product_name", "").strip()
            review_text = row.get("Review", "").strip()
            brand = extract_brand(product_name)

            record = ReviewRecord(
                index=len(records),
                product_name=product_name,
                brand=brand,
                review=review_text,
                rating=rating,
            )
            records.append(record)
    return records


def analyze_records(records: List[ReviewRecord]) -> List[ReviewRecord]:
    """Jalankan analisis sentimen pada setiap record."""
    for rec in records:
        label, score = score_sentiment(rec.review, rec.rating)
        rec.sentiment_label = label
        rec.sentiment_score = score
        rec.aspects_detected = detect_aspects(rec.review)
    return records


def aggregate_by_product(records: List[ReviewRecord]) -> List[ProductSummary]:
    """Agregasi hasil analisis per produk unik."""
    product_groups: Dict[str, List[ReviewRecord]] = defaultdict(list)
    for rec in records:
        # Gunakan 30 karakter pertama sebagai key sederhana produk
        short_key = rec.product_name[:60].strip()
        product_groups[short_key].append(rec)

    summaries = []
    for product_key, group in product_groups.items():
        total = len(group)
        avg_rating = sum(r.rating for r in group) / total

        sent_dist = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for rec in group:
            sent_dist[rec.sentiment_label] += 1

        # Dominant sentiment
        dominant = max(sent_dist, key=lambda k: sent_dist[k])

        # Frasa kunci
        all_reviews = [r.review for r in group]
        top_pos = extract_key_phrases(all_reviews, "positive")
        top_neg = extract_key_phrases(all_reviews, "negative")

        # Skor per aspek
        aspect_scores = {}
        for aspect in ASPECT_KEYWORDS.keys():
            aspect_reviews = [r for r in group if aspect in r.aspects_detected]
            if aspect_reviews:
                pos_in_aspect = sum(1 for r in aspect_reviews if r.sentiment_label == "Positive")
                aspect_scores[aspect] = round(pos_in_aspect / len(aspect_reviews), 2)
            else:
                aspect_scores[aspect] = None

        brand = group[0].brand if group else "-"

        summaries.append(ProductSummary(
            product_name=product_key,
            brand=brand,
            total_reviews=total,
            avg_rating=round(avg_rating, 2),
            sentiment_distribution=sent_dist,
            top_positive_phrases=top_pos,
            top_negative_phrases=top_neg,
            aspect_scores=aspect_scores,
            overall_sentiment=dominant,
        ))

    return sorted(summaries, key=lambda s: s.avg_rating, reverse=True)


def compute_global_stats(records: List[ReviewRecord], summaries: List[ProductSummary]) -> dict:
    """Hitung statistik global seluruh dataset."""
    total = len(records)
    sent_dist = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for rec in records:
        sent_dist[rec.sentiment_label] += 1

    avg_rating = sum(r.rating for r in records) / total if total else 0

    brand_stats = defaultdict(lambda: {"count": 0, "rating_sum": 0, "pos": 0})
    for rec in records:
        brand_stats[rec.brand]["count"] += 1
        brand_stats[rec.brand]["rating_sum"] += rec.rating
        if rec.sentiment_label == "Positive":
            brand_stats[rec.brand]["pos"] += 1

    brand_summary = {}
    for brand, stats in brand_stats.items():
        brand_summary[brand] = {
            "total_reviews": stats["count"],
            "avg_rating": round(stats["rating_sum"] / stats["count"], 2),
            "positive_rate": round(stats["pos"] / stats["count"], 2),
        }

    return {
        "total_reviews": total,
        "avg_rating_global": round(avg_rating, 2),
        "sentiment_distribution": sent_dist,
        "positive_pct": round(sent_dist["Positive"] / total * 100, 1),
        "neutral_pct": round(sent_dist["Neutral"] / total * 100, 1),
        "negative_pct": round(sent_dist["Negative"] / total * 100, 1),
        "brand_breakdown": dict(sorted(brand_summary.items(),
                                       key=lambda x: x[1]["avg_rating"], reverse=True)),
    }


def run_pipeline(csv_path: str) -> dict:
    """Titik masuk utama pipeline analisis."""
    records = load_dataset(csv_path)
    records = analyze_records(records)
    summaries = aggregate_by_product(records)
    global_stats = compute_global_stats(records, summaries)

    return {
        "global_stats": global_stats,
        "product_summaries": summaries,
        "raw_records": records,
    }


if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "laptop_online_review.csv")
    result = run_pipeline(csv_path)
    print(json.dumps(result["global_stats"], indent=2, ensure_ascii=False))
    print(f"\nTotal produk dianalisis: {len(result['product_summaries'])}")
