# Customer Feedback Sentiment Analyzer
## IBM Global AI Builders Challenge 2024
### Track: Productivity & Smart Business / Customer Analytics

---

## Deskripsi Proyek

Sistem analisis sentimen otomatis dan generator insight bisnis yang memproses dataset ulasan pelanggan e-commerce. Sistem dirancang untuk kompetisi **IBM Global AI Builders Challenge 2024** dan sepenuhnya kompatibel dengan **IBM watsonx.ai**.

Sistem melakukan dua tugas utama:
1. **Ringkasan Naratif Eksekutif** — narasi kohesif berdasarkan dimensi kualitas produk, harga/nilai, dan pengalaman pengiriman
2. **Klasifikasi Sentimen** — Positive / Neutral / Negative + rekomendasi bisnis terstruktur berdasarkan tingkat prioritas

---

## Struktur Direktori

```
Dashboard/
├── laptop_online_review.csv          # Dataset ulasan produk laptop
├── Sentiment Analysis (STARTER).json # Template workflow Langflow
├── run_analysis.py                   # Entry point utama — jalankan ini
├── src/
│   ├── sentiment_analyzer.py         # Core engine analisis sentimen
│   ├── prompt_templates.py           # Prompt engineering (IBM watsonx.ai ready)
│   └── report_generator.py           # Generator laporan MD/HTML/JSON
└── output/                           # Hasil analisis (auto-generated)
    ├── sentiment_report.md           # Laporan lengkap format Markdown
    ├── sentiment_dashboard.html      # Dashboard interaktif dengan Chart.js
    └── analysis_results.json         # Data mentah JSON untuk integrasi lanjutan
```

---

## Cara Menjalankan

### Prasyarat
- Python 3.8+
- Tidak ada dependensi eksternal (zero pip install required)

### Menjalankan Analisis

```bash
# Dari direktori root proyek (ai agent/)
python Dashboard/run_analysis.py

# Dengan path kustom
python Dashboard/run_analysis.py --csv path/to/reviews.csv --output path/to/output
```

### Melihat Hasil

```
Dashboard/output/
  sentiment_report.md        → Buka dengan text editor / GitHub renderer
  sentiment_dashboard.html   → Buka dengan browser untuk tampilan interaktif
  analysis_results.json      → Data terstruktur untuk integrasi sistem lain
```

---

## Arsitektur Sistem

```
[CSV Dataset]
     |
     v
[sentiment_analyzer.py]
  - Load & Parse Dataset
  - Rule-Based Sentiment Scoring
    (Rating Weight 50% + Keyword Heuristic 50%)
  - Aspect Detection (Kualitas / Harga / Pengiriman)
  - Per-Product Aggregation
     |
     v
[prompt_templates.py]
  - Prompt Template 1: Sentiment Classification (CoT + Few-Shot)
  - Prompt Template 2: Executive Summary Generation
  - Prompt Template 3: Business Recommendations
  - IBM watsonx.ai API Integration (Granite / Llama 3)
     |
     v
[report_generator.py]
  - Narrative Engine (rule-based, no LLM required)
  - Markdown Report Builder
  - HTML Dashboard Builder (Chart.js)
  - JSON Export
     |
     v
[OUTPUT]
  sentiment_report.md
  sentiment_dashboard.html
  analysis_results.json
```

---

## Metodologi

| Komponen | Detail |
|---|---|
| **Metode Sentimen** | Hybrid: Rating-weighted + Keyword Heuristic |
| **Bobot Rating** | 50% (dinormalisasi dari skala 1–5) |
| **Bobot Keyword** | 50% (positive/negative lexicon matching) |
| **Threshold Positif** | Combined Score ≥ 0.15 |
| **Threshold Negatif** | Combined Score ≤ −0.15 |
| **Aspek Analisis** | Kualitas Produk, Harga & Nilai, Pengiriman |
| **LLM Integration** | IBM watsonx.ai (Granite 13B / Llama 3 70B) |
| **Langflow** | Workflow diagram tersedia di `Sentiment Analysis (STARTER).json` |

---

## Hasil Analisis Dataset

| Metrik | Nilai |
|---|---|
| Total Ulasan Diproses | 1.001 ulasan |
| Total Varian Produk | 101 produk |
| Rata-rata Rating Global | 4.39 / 5.0 |
| Sentimen Positif | 90.3% |
| Sentimen Netral | 2.8% |
| Sentimen Negatif | 6.9% |
| **Klasifikasi Keseluruhan** | **POSITIF** |

---

## Integrasi IBM watsonx.ai

Untuk mengaktifkan generasi teks berbasis LLM, edit `src/prompt_templates.py`:

```python
from ibm_watsonx_ai.foundation_models import Model

model = Model(
    model_id="ibm/granite-13b-chat-v2",
    credentials={"apikey": "<YOUR_API_KEY>", "url": "https://us-south.ml.cloud.ibm.com"},
    project_id="<YOUR_PROJECT_ID>",
    params={"decoding_method": "greedy", "max_new_tokens": 800, "temperature": 0.3},
)
response = model.generate_text(prompt=build_executive_summary_prompt(global_stats, summaries))
```

---

## Tim / Kontributor

- **Kompetisi**: IBM Global AI Builders Challenge 2024
- **Track**: Productivity & Smart Business / Customer Analytics
- **Tools**: Python, IBM watsonx.ai, Langflow, Chart.js

---

*Generated with Customer Feedback Sentiment Analyzer — IBM AI Builders Challenge 2024*
