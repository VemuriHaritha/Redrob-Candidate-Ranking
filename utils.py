import gzip
from datetime import datetime
from config import TODAY

GROUP_LABELS = {
    "embeddings_retrieval": "embeddings/retrieval",
    "vector_db_infra":      "vector DB",
    "python_engineering":   "Python",
    "nlp_ir_core":          "NLP/IR",
    "llm_transformers":     "LLMs/transformers",
    "ranking_evaluation":   "ranking/eval",
}
 
 
def build_reasoning(candidate, matched_must):
    p       = candidate.get("profile") or {}
    signals = candidate.get("redrob_signals") or {}
    career  = candidate.get("career_history") or []
 
    title   = p.get("current_title") or "N/A"
    yrs     = p.get("years_of_experience") or "?"
    loc     = p.get("location") or "N/A"
    country = p.get("country") or ""
 
    notice      = signals.get("notice_period_days")
    github      = signals.get("github_activity_score", -1)
    open_work   = signals.get("open_to_work_flag", False)
    resp_rate   = signals.get("recruiter_response_rate")
    last_active = signals.get("last_active_date", "")
 
    matched_str = ", ".join(GROUP_LABELS.get(g, g) for g in matched_must[:3])
 
    top_role = ""
    for r in career[:2]:
        rt = r.get("title", "").lower()
        if any(kw in rt for kw in RETRIEVAL_TITLE_KWS):
            top_role = f"Recent role: {r.get('title')} at {r.get('company')}."
            break
 
    part1 = (
        f"{title} with {yrs} yrs exp in {loc}"
        f"{', ' + country if country and country.lower() != 'india' else ''}."
    )
    if top_role:
        part1 += f" {top_role}"
 
    facts = []
    if matched_str:
        facts.append(f"Skills: {matched_str}")
    if notice is not None:
        facts.append(f"notice {notice}d")
    if open_work:
        facts.append("open to work")
    if github is not None and github >= 0:
        facts.append(f"GitHub {github:.0f}/100")
    if resp_rate is not None:
        facts.append(f"response rate {resp_rate:.0%}")
    if last_active:
        try:
            ld      = datetime.strptime(last_active, "%Y-%m-%d").date()
            days_ago = (TODAY - ld).days
            facts.append(f"active {days_ago}d ago")
        except Exception:
            pass
 
    return (part1 + " " + "; ".join(facts)).strip()
 
 
def open_candidates(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")
 
