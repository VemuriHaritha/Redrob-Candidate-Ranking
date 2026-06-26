# Redrob — Intelligent Candidate Ranking

Ranks 100,000 candidates against a job description and outputs the top 100 as a CSV. No GPU, no external APIs, no pip dependencies beyond Python's standard library.

---

## How it works

The pipeline runs in two stages.

**Stage 1 — Rule-based scoring (all 100K candidates)**

Each candidate is scored across eight dimensions:

| Signal | Weight |
|---|---|
| Career trajectory (titles + description keywords) | 40% |
| Must-have skill group coverage | 18% |
| Skill depth (endorsements + duration on relevant skills) | up to 15% |
| Experience years fit (ideal 5–9) | 10% |
| Behavioral signals (response rate, notice period, GitHub, last active) | 15% |
| Location fit | 5% |
| Education tier | 3% |
| Platform assessment scores + salary fit | 6% |

Before scoring, a honeypot detector drops profiles with physically impossible timelines — expert skills with zero usage months, role durations longer than claimed experience, graduation dates that contradict stated years of experience.

A hard gate filters out any candidate whose current title is non-technical (operations manager, marketing manager, HR, etc.) or who matches fewer than 2 must-have skill groups without a retrieval/ML job title. This is the single rule that prevents keyword-stuffed irrelevant profiles from reaching the final shortlist.

The top 600 survive into Stage 2.

**Stage 2 — TF-IDF re-ranking (top 600)**

Builds a TF-IDF vocabulary from the 600 candidate text blobs plus a JD reference document. Computes cosine similarity between each candidate vector and the JD vector. Normalises scores and blends with Stage 1:

```
final_score = stage1_score * 0.70 + tfidf_score * 0.30
```

Top 100 by final score are written to the output CSV.

---

## File structure

```
config.py      constants, keyword groups, disqualifier lists
scoring.py     all individual scoring functions (career, skills, behavioral, etc.)
ranking.py     TF-IDF implementation, honeypot detector, text blob builder
utils.py       file reader, reasoning string builder, CSV writer, validator
main.py        entry point — calls the above in order
```

---

## Usage

**Edit the two config lines at the top of `main.py`:**

```python
CANDIDATES_PATH = "candidates.jsonl.gz"   # or candidates.jsonl
OUTPUT_PATH     = "submission.csv"
```

**Run:**

```bash
python main.py
```

Works with both `.jsonl` and `.jsonl.gz` input. The gzip file is streamed directly — no need to decompress it first.

**Expected runtime:** ~3 minutes on a single CPU core for 100K candidates. Memory stays under 2 GB because candidates are processed line by line, never loaded in bulk.

---

## Requirements

Python 3.10 or higher. No external packages — only standard library modules (`json`, `gzip`, `csv`, `math`, `re`, `collections`, `datetime`).

---

## Output format

```
candidate_id,rank,score,reasoning
CAND_0008425,1,1.000000,"Senior NLP Engineer with 7.8 yrs exp in Kolkata..."
CAND_0006557,2,0.988596,"NLP Engineer with 7.9 yrs exp in Jaipur..."
...
```

Exactly 100 rows. Scores are non-increasing. Each reasoning string references only facts present in the candidate's profile — no inference.

---

## Sample top-10 output

| Rank | Title | Company | Score |
|---|---|---|---|
| 1 | Senior NLP Engineer | Ola | 1.000 |
| 2 | NLP Engineer | Paytm | 0.989 |
| 3 | Senior NLP Engineer | Netflix | 0.973 |
| 4 | Senior NLP Engineer | Niramai | 0.973 |
| 5 | Senior ML Engineer | Amazon | 0.972 |
| 6 | Machine Learning Engineer | Verloop.io | 0.945 |
| 7 | Senior AI Engineer | Apple | 0.934 |
| 8 | Recommendation Systems Engineer | upGrad | 0.925 |
| 9 | Senior AI Engineer | Meta | 0.897 |
| 10 | Search Engineer | Google | 0.897 |

---

## Design decisions

**Why career history carries 40% of the weight**

The JD explicitly warns that keyword matching is a trap. An Operations Manager whose skills list includes "RAG" and "Pinecone" is not a fit. A Search Engineer whose job descriptions mention ranking models, A/B testing, and offline-online correlation is a strong fit — even if their profile never uses the word "LLM". Career titles and role descriptions reveal actual work; skills sections are self-reported and often inflated.

**Why TF-IDF as Stage 2 rather than a second rule pass**

TF-IDF catches vocabulary variation that keyword lists miss — a candidate who writes "dense vector index" instead of "FAISS" still gets similarity credit against the JD reference text. It also down-weights tokens that appear in almost every candidate's profile, which reduces noise from generic terms like "Python" or "machine learning".
