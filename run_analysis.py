"""
=====================================================================
 Main Workflow Orchestrator
 Customer Feedback Sentiment Analyzer
 IBM Global AI Builders Challenge 2024
=====================================================================
 Jalankan skrip ini untuk memproses dataset dan menghasilkan
 seluruh output (Markdown, HTML, JSON) secara otomatis.

 Penggunaan:
   python run_analysis.py
   python run_analysis.py --csv path/to/review.csv
   python run_analysis.py --csv path/to/review.csv --output ./output
=====================================================================
"""

import os
import sys
import argparse
import time

# Tambahkan path src ke sys.path agar dapat diimport
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
sys.path.insert(0, SRC_DIR)

from sentiment_analyzer import run_pipeline
from report_generator import save_outputs


# ─────────────────────────────────────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────────────────────────────────────

BANNER = """
======================================================================
   Customer Feedback Sentiment Analyzer
   IBM Global AI Builders Challenge 2024
   Track: Productivity & Smart Business / Customer Analytics
======================================================================
"""


def print_progress(step: int, total: int, label: str):
    bar_len = 40
    filled = int(bar_len * step / total)
    bar = "#" * filled + "-" * (bar_len - filled)
    pct = int(100 * step / total)
    print(f"\r  [{bar}] {pct:3d}%  {label:<35}", end="", flush=True)
    if step == total:
        print()


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Customer Feedback Sentiment Analyzer — IBM AI Builders Challenge 2024"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=os.path.join(SCRIPT_DIR, "laptop_online_review.csv"),
        help="Path ke file CSV dataset ulasan (default: Dashboard/laptop_online_review.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(SCRIPT_DIR, "output"),
        help="Direktori output laporan (default: Dashboard/output/)",
    )
    args = parser.parse_args()

    csv_path    = args.csv
    output_dir  = args.output

    # Validasi file
    if not os.path.isfile(csv_path):
        print(f"  ❌ ERROR: File tidak ditemukan: {csv_path}")
        print(f"     Pastikan file CSV tersedia di: {csv_path}")
        sys.exit(1)

    print(f"  📂 Dataset   : {csv_path}")
    print(f"  📁 Output    : {output_dir}")
    print()

    start = time.time()

    # ── STEP 1: Load & Parse ─────────────────────────────────────────────
    print_progress(0, 5, "Memuat dataset CSV...")
    time.sleep(0.1)

    # ── STEP 2: Jalankan pipeline ────────────────────────────────────────
    print_progress(1, 5, "Menjalankan analisis sentimen...")
    result = run_pipeline(csv_path)
    time.sleep(0.1)

    global_stats      = result["global_stats"]
    product_summaries = result["product_summaries"]
    raw_records       = result["raw_records"]

    print_progress(2, 5, "Menghasilkan narasi eksekutif...")
    time.sleep(0.1)

    # ── STEP 3: Simpan output ────────────────────────────────────────────
    print_progress(3, 5, "Menyusun rekomendasi bisnis...")
    time.sleep(0.1)

    print_progress(4, 5, "Menyimpan laporan (MD/HTML/JSON)...")
    output_paths = save_outputs(output_dir, global_stats, product_summaries, raw_records)

    print_progress(5, 5, "Selesai!")
    elapsed = time.time() - start

    # ── RINGKASAN HASIL ──────────────────────────────────────────────────
    dist = global_stats["sentiment_distribution"]
    brands = global_stats.get("brand_breakdown", {})
    top_brand = max(brands, key=lambda b: brands[b]["avg_rating"], default="N/A")

    print()
    print("  +-----------------------------------------------------+")
    print("  |                  HASIL ANALISIS                     |")
    print("  +-----------------------------------------------------+")
    print(f"  |  Total Ulasan Diproses   : {global_stats['total_reviews']:<26}|")
    print(f"  |  Total Varian Produk     : {len(product_summaries):<26}|")
    print(f"  |  Rata-rata Rating Global : {str(global_stats['avg_rating_global'])+'/5.0':<26}|")
    print(f"  |  Sentimen Positif        : {str(global_stats['positive_pct'])+'%':<26}|")
    print(f"  |  Sentimen Netral         : {str(global_stats['neutral_pct'])+'%':<26}|")
    print(f"  |  Sentimen Negatif        : {str(global_stats['negative_pct'])+'%':<26}|")
    print(f"  |  Brand Rating Tertinggi  : {top_brand:<26}|")
    print(f"  |  Waktu Eksekusi          : {str(round(elapsed,2))+' detik':<26}|")
    print("  +-----------------------------------------------------+")
    print()
    print("  Output yang dihasilkan:")
    for key, path in output_paths.items():
        rel = os.path.relpath(path, SCRIPT_DIR)
        print(f"     [OK] {key.upper():<10} -> {rel}")
    print()
    print("  Buka sentiment_dashboard.html di browser untuk tampilan interaktif.")
    print("  Lihat sentiment_report.md untuk laporan lengkap format Markdown.")
    print()


if __name__ == "__main__":
    main()
