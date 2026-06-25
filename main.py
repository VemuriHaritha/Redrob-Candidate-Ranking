import json
import csv
import re

from config import *
from scoring import *
from ranking import *
from utils import *


def main():
    print("=" * 60)
    print("Redrob Hackathon Candidate Ranker")
    print("=" * 60)

    results = []
    fallback = []

    total = 0
    honeypots = 0
    filtered = 0

    print("\n[Stage 1] Candidate Scoring")

    with open_candidates(CANDIDATES_PATH) as fh:

        for line in fh:
            line = line.strip()

            if not line:
                continue

            try:
                cand = json.loads(line)
            except json.JSONDecodeError:
                continue

            total += 1

            if is_honeypot(cand):
                honeypots += 1
                continue

            score, matched_must, text_blob = compute_score(cand)

            entry = {
                "id": cand.get("candidate_id"),
                "score": score,
                "matched_must": matched_must,
                "blob": text_blob,
                "candidate": cand,
            }

            if score == 0:
                filtered += 1

                if len(fallback) < 200:
                    entry["score"] = 0.001
                    fallback.append(entry)

            else:
                results.append(entry)

    print(f"Total Candidates : {total}")
    print(f"Honeypots Removed: {honeypots}")
    print(f"Filtered Out     : {filtered}")
    print(f"Remaining        : {len(results)}")

    results.sort(key=lambda x: -x["score"])

    print("\n[Stage 2] TF-IDF Re-ranking")

    top_n = results[:TOP_STAGE1]

    corpus = [r["blob"] for r in top_n] + [JD_TEXT]

    idf, tokenized = build_tfidf(corpus)

    jd_tokens = re.findall(
        r"\b[a-z][a-z0-9\-]{1,30}\b",
        JD_TEXT
    )

    jd_vec = tfidf_vec(jd_tokens, idf)

    sims = []

    for i, r in enumerate(top_n):
        cv = tfidf_vec(tokenized[i], idf)
        sims.append(cosine(cv, jd_vec))

    max_sim = max(sims) if sims else 1.0
    min_sim = min(sims) if sims else 0.0

    sim_range = max_sim - min_sim or 1.0

    sims_norm = [
        (s - min_sim) / sim_range
        for s in sims
    ]

    for i, r in enumerate(top_n):
        r["final"] = (
            r["score"] * 0.70 +
            sims_norm[i] * 0.30
        )

    top_n.sort(
        key=lambda x: (
            -x["final"],
            -len(x["matched_must"]),
            x["id"] or ""
        )
    )

    top_100 = top_n[:100]

    if len(top_100) < 100:

        needed = 100 - len(top_100)

        fallback.sort(key=lambda x: -x["score"])

        for fb in fallback:
            fb["final"] = fb["score"]

        top_100.extend(fallback[:needed])

    print("\n[Stage 3] Writing Submission")

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            ["candidate_id", "rank", "score", "reasoning"]
        )

        prev_score = None

        for rank, r in enumerate(top_100[:100], start=1):

            score = r["final"]

            if prev_score is not None and score > prev_score:
                score = prev_score

            prev_score = score

            reasoning = build_reasoning(
                r["candidate"],
                r["matched_must"]
            )

            reasoning = (
                reasoning
                .replace('"', "'")
                .replace("\n", " ")
            )

            writer.writerow([
                r["id"],
                rank,
                f"{score:.6f}",
                reasoning
            ])

    print(f"\nSubmission saved to: {OUTPUT_PATH}")

    print("\n[Validation]")

    errors = []

    with open(
        OUTPUT_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.reader(f)

        header = next(reader)

        if header != [
            "candidate_id",
            "rank",
            "score",
            "reasoning"
        ]:
            errors.append(
                f"Invalid header: {header}"
            )

        rows = list(reader)

        if len(rows) != 100:
            errors.append(
                f"Expected 100 rows, got {len(rows)}"
            )

        scores = []

        for row in rows:
            try:
                scores.append(float(row[2]))
            except Exception:
                errors.append(
                    f"Invalid score row: {row}"
                )

        for i in range(len(scores) - 1):
            if scores[i] < scores[i + 1] - 1e-9:
                errors.append(
                    f"Scores not descending at row {i+1}"
                )

    if errors:

        print("\nValidation Failed:")

        for err in errors:
            print("-", err)

    else:
        print("✓ Output valid")

    print("\nDone!")


if __name__ == "__main__":
    main()
