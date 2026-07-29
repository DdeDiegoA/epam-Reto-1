# 📊 FlowApp Review Analysis

**Author:** Diego Arenas (Diegoarenas111@gmail.com)

Professional app review cleaner. Takes a dirty CSV (~600 rows with emojis, broken ratings, duplicates) and returns: clean dataset, word frequency analysis by rating, full statistical summary. Zero external dependencies: Python 3.9+ only.

---

## ⚡ Quick Start (3 steps)

### Step 1: Setup

```bash
# Navigate to the project folder
cd /path/to/Reto1/resolucion\ de\ reto_Claude

# Verify Python 3.9+
python3 --version
# Expected: Python 3.9+ (tested with 3.11)

# Check the structure
ls -la
# You should see: procesar_resenas.py, limpieza.py, stopwords_es.py,
#                 resenas_flowapp.csv, tests/, output/
```

### Step 2: Run the analysis

**Simplest way** (recommended first time):
```bash
python3 procesar_resenas.py
# Reads from: resenas_flowapp.csv (auto-detected)
# Writes to: ./output/
# Runtime: ~1 second
```

**Custom options**:
```bash
python3 procesar_resenas.py --input other_dataset.csv --outdir my_output/ --top-n 25
```

**Verify everything works** (unit tests):
```bash
python3 tests/test_limpieza.py -v
# 13 checks for cleaning/normalization
# Runtime: <0.1s (all should pass ✅)
```

### Step 3: Review the results

```bash
cd output/
ls -la
cat resumen_estadistico.json          # statistical summary
cat reporte_calidad_datos.json        # what was cleaned/discarded
head -10 palabras_frecuentes_por_rating.csv  # top words by rating
```

---

## 📋 Quick Reference

```bash
# Run with custom parameters
python3 procesar_resenas.py --input my_dataset.csv --outdir output/ --top-n 20

# Save logs to file
python3 procesar_resenas.py 2>&1 | tee report.log

# Run tests only
python3 tests/test_limpieza.py -v

# Increase top words to 25 per rating
python3 procesar_resenas.py --top-n 25
```

---

## 📁 What's in `output/`

| File | Description |
|---|---|
| **resenas_limpias.csv** | Full processed dataset: clean text, normalized rating, quality flags |
| **reporte_calidad_datos.json** | Detailed audit: what was cleaned, discarded, and why (full transparency) |
| **resumen_estadistico.json** | Numbers: mean, median, mode, standard deviation, rating distribution |
| **palabras_frecuentes_por_rating.csv/.json** | Top-N most frequent words per rating (stopwords removed) |

## 🎯 Dataset quirks (and how they're handled)

The CSV is deliberately dirty — part of the challenge. Here's what was found and how it's addressed:

| Problem | Cases | Solution |
|----------|-------|----------|
| **Exact duplicates** | 14 rows | Same review from same user on same date. Removed, keeping the first occurrence. |
| **Empty/broken ratings** | 19 rows | Empty (9), out of range -1/0/6/7 (7), symbols `?` or `N/A`. Flagged as invalid but **not deleted**. |
| **Textual ratings** | 3 rows | `"cinco"` is a valid 5 but malformed. Auto-recovered. |
| **Empty or emoji-only text** | 26 rows | Flagged as empty, excluded from word analysis, but the row is preserved. |

**Core principle:** Nothing is silently discarded. Everything is logged in `reporte_calidad_datos.json` for full auditability.

---

## 📊 What it does

### Functional requirements (what the challenge asks for)

✅ **Text cleaning:** lowercase, emojis/special characters removed, duplicate spaces collapsed. Preserves accents/ñ (readable Spanish, not garbled text).

✅ **Deduplication:** removes exact duplicate rows re-entered by the same user on the same date.

✅ **Smart noise handling:** invalid ratings, empty text, and duplicates are never silently deleted — they're flagged and audited.

✅ **Word frequency by rating:** top-N words for each level (1⭐ to 5⭐), **without stopwords** (no "el/la/que/muy/es" noise).

✅ **Statistical summary:** mean, median, mode, standard deviation, rating distribution in absolute numbers and percentages.

✅ **Quality report:** JSON file explaining every discard/correction (full transparency).

### Non-functional requirements (how it's done)

🔒 **Reproducibility:** same input → always same output. No randomness, no order-dependent behavior.

🔒 **Auditability:** every modified/excluded row is logged with its reason. No information loss.

🔒 **Portability:** zero dependencies — Python stdlib only. Runs on any machine with Python 3.9+.

🔒 **Configurability:** CLI parameters (`--input`, `--outdir`, `--top-n`), no code changes needed.

🔒 **Testability:** cleaning logic in pure functions (`limpieza.py`), I/O separated (`procesar_resenas.py`). 11 automated tests.

🔒 **Native UTF-8:** emojis, accents, ñ work end-to-end.

🔒 **Fail-fast:** missing CSV columns abort with a clear error. Internal assertions verify numbers add up before writing output.

---

## 🏗️ Code Structure

```
resolucion de reto_Claude/
│
├── procesar_resenas.py           # 🎬 Main script: orchestrates everything
│                                 #    → read CSV → clean → analyze → write results
│
├── limpieza.py                   # 🧹 Pure cleaning functions (testable)
│                                 #    → limpiar_texto(), normalizar_rating()
│                                 #    → tokenizar_para_frecuencia(), dedup keys
│
├── stopwords_es.py               # 📍 Spanish stopwords list
│                                 #    (removes noise from frequency analysis)
│
├── resenas_flowapp.csv           # 📊 Input dataset (597 rows)
│
├── tests/
│   └── test_limpieza.py          # ✅ 13 unit tests (stdlib, zero deps)
│
├── output/  (generated at runtime)
│   ├── resenas_limpias.csv
│   ├── reporte_calidad_datos.json
│   ├── resumen_estadistico.json
│   ├── palabras_frecuentes_por_rating.csv
│   └── palabras_frecuentes_por_rating.json
│
├── .gitignore                    # Git: what to ignore
├── README.md                     # This file
└── .git/                         # Version control
```

### Why this structure

- **Separation of concerns:** `limpieza.py` knows nothing about files (pure computation), `procesar_resenas.py` handles I/O.
- **Testable:** you can test the cleaning logic without touching the CSV.
- **Reusable:** anyone can import `limpieza.py` into their own script.
- **Maintainable:** each file does one thing well.

---

## 📈 Sample Output

After running `python3 procesar_resenas.py`:

```
INFO: Reading /path/to/resenas_flowapp.csv
INFO: Rows read=597 duplicates_removed=14 final=583
INFO: Invalid ratings=19 (detail: {'(empty)': 9, '-1': 2, ...})
       | recovered from text={'cinco': 3}
       | empty texts=26
INFO: Results written to ./output
```

**File: `resumen_estadistico.json`**
```json
{
  "total_ratings_validos": 564,
  "promedio": 3.871,
  "mediana": 4.0,
  "moda": [5],
  "desviacion_estandar": 1.196,
  "distribucion_absoluta": {
    "1": 34,
    "2": 53,
    "3": 81,
    "4": 180,
    "5": 216
  },
  "distribucion_porcentual": {
    "1": 6.03,
    "2": 9.4,
    "3": 14.36,
    "4": 31.91,
    "5": 38.3
  }
}
```

**File: `palabras_frecuentes_por_rating.csv`** (sample)
```
rating,palabra,frecuencia
1,experiencia,11
1,recomiendo,10
1,dinero,10
1,app,9
1,terrible,9
5,excelente,42
5,funciona,38
5,perfecta,35
5,encanta,28
```

---

## ❓ FAQ

**Q: What if I don't have Python 3.9?**
A: Download Python 3.11+ from [python.org](https://python.org). This code is compatible with 3.9–3.13.

**Q: Why not use Pandas?**
A: The dataset is small (597 rows). Pandas is overkill. Stdlib is faster here and adds **zero dependencies**.

**Q: Can I change the input/output paths?**
A: Yes, use `--input` and `--outdir`:
```bash
python3 procesar_resenas.py --input /path/to/other.csv --outdir /output/
```

**Q: What do the tests cover?**
A: They verify `limpiar_texto()`, `normalizar_rating()`, etc. work correctly. Safety net for future changes.

**Q: How do I see more detailed logs?**
A: Change the log level in `procesar_resenas.py` around line ~38 from `INFO` to `DEBUG`.

---

## 🤝 Contact

Questions or improvements: **Diego Arenas** (Diegoarenas111@gmail.com)
