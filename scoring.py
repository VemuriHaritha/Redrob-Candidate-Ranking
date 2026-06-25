from config import *
from datetime import datetime


def is_honeypot(candidate):
    """Detect subtly impossible profiles. Returns True if honeypot."""
    profile  = candidate.get("profile", {})
    skills   = candidate.get("skills", [])
    career   = candidate.get("career_history", [])
    yrs_exp  = float(profile.get("years_of_experience") or 0)
 
    hp = 0
 
    # Expert skill with zero duration — physically impossible
    expert_zero = sum(
        1 for s in skills
        if s.get("proficiency") == "expert" and (s.get("duration_months") or 0) == 0
    )
    if expert_zero >= 2:
        hp += 3
 
    # Implausibly many expert skills
    if sum(1 for s in skills if s.get("proficiency") == "expert") >= 10:
        hp += 2
 
    # Single role duration > claimed total experience + 12 months grace
    if career and yrs_exp > 0:
        max_role = max((r.get("duration_months") or 0) for r in career)
        if max_role > (yrs_exp * 12 + 12):
            hp += 2
 
    # Single skill duration > experience + 18 months grace
    if skills and yrs_exp > 0:
        max_skill = max((s.get("duration_months") or 0) for s in skills)
        if max_skill > (yrs_exp * 12 + 18):
            hp += 2
 
    # Graduation year implies far more experience than claimed
    education = candidate.get("education", [])
    if education and yrs_exp > 0:
        end_years = [e.get("end_year") for e in education if e.get("end_year")]
        if end_years:
            years_since_grad = TODAY.year - max(end_years)
            if years_since_grad > yrs_exp + 15:
                hp += 1
 
    return hp >= 3
 
 
# ─── TEXT BLOB ────────────────────────────────────────────────────────────────
 
def build_text_blob(candidate):
    """Weighted lowercase text blob for keyword matching."""
    parts = []
    p = candidate.get("profile", {})
 
    if p.get("current_title"):
        parts.append((p["current_title"] + " ") * 5)
    if p.get("headline"):
        parts.append((p["headline"] + " ") * 3)
    if p.get("summary"):
        parts.append(p["summary"])
 
    for role in candidate.get("career_history", []):
        if role.get("title"):
            parts.append((role["title"] + " ") * 3)
        if role.get("description"):
            parts.append(role["description"])
        if role.get("industry"):
            parts.append(role["industry"])
 
    for s in candidate.get("skills", []):
        if s.get("name"):
            w = 3 if s.get("proficiency") in ("expert", "advanced") else 1
            parts.append((s["name"] + " ") * w)
 
    for cert in candidate.get("certifications", []):
        if cert.get("name"):
            parts.append((cert["name"] + " ") * 2)
 
    for edu in candidate.get("education", []):
        if edu.get("field_of_study"):
            parts.append(edu["field_of_study"])
 
    return " ".join(parts).lower()
 
 
# ─── SCORING FUNCTIONS ────────────────────────────────────────────────────────
 
def score_career(profile, career_history):
    """
    Career-first scoring — the single most important signal.
    Returns (career_score 0-1, disq_penalty 0-1, has_retrieval_title bool).
    """
    if not career_history:
        return 0.2, 0.0, False
 
    titles_lower     = [r.get("title", "").lower() for r in career_history]
    companies_lower  = [r.get("company", "").lower() for r in career_history]
    industries_lower = [r.get("industry", "").lower() for r in career_history]
    descriptions     = " ".join(r.get("description", "") for r in career_history).lower()
 
    score = 0.0
    disq  = 0.0
 
    # Hard disqualifier: non-technical current title
    current_title = (profile.get("current_title") or "").lower()
    if any(bk in current_title for bk in BAD_TITLE_KWS):
        disq = 0.80
 
    # Retrieval / search / ranking title bonus
    has_retrieval = any(
        any(rt in t for rt in RETRIEVAL_TITLE_KWS)
        for t in titles_lower
    )
    if has_retrieval:
        score += 0.55
 
    # Career description keyword bonus
    desc_keywords = [
        "ranking", "retrieval", "recommendation", "search", "relevance",
        "matching", "embeddings", "vector", "learning to rank",
        "offline-online", "a/b test", "ndcg", "mrr", "rerank",
        "personalization", "candidate matching", "job matching",
    ]
    desc_hits = sum(1 for kw in desc_keywords if kw in descriptions)
    score += min(0.30, desc_hits * 0.035)
 
    # Product company / startup bonus
    product_signals = [
        "food delivery", "e-commerce", "fintech", "edtech", "saas",
        "ai", "ml", "analytics", "software", "internet", "startup",
        "transportation", "platform",
    ]
    for ind in industries_lower:
        if any(ps in ind for ps in product_signals):
            score += 0.10
            break
 
    # Consulting-only penalty
    n = len(companies_lower)
    if n > 0:
        consulting_n = sum(1 for co in companies_lower
                           if any(cf in co for cf in CONSULTING_FIRMS))
        if consulting_n == n:
            disq = max(disq, 0.60)
        elif consulting_n / n > 0.7:
            disq = max(disq, 0.30)
 
    # Tenure stability
    durations  = [r.get("duration_months") or 0 for r in career_history]
    avg_tenure = sum(durations) / len(durations) if durations else 0
    if avg_tenure >= 24:
        score += 0.05
    elif avg_tenure < 12:
        score -= 0.05
 
    return min(1.0, max(0.0, score)), disq, has_retrieval
 
 
def score_skills(text_blob, skills_list):
    """Score skill keyword coverage and depth."""
    matched_must = []
    for group, keywords in MUST_HAVE_GROUPS.items():
        if any(kw in text_blob for kw in keywords):
            matched_must.append(group)
 
    matched_nice = []
    for group, keywords in NICE_TO_HAVE_GROUPS.items():
        if any(kw in text_blob for kw in keywords):
            matched_nice.append(group)
 
    ai_kws = set()
    for kw_list in MUST_HAVE_GROUPS.values():
        ai_kws.update(kw_list)
 
    depth_bonus = 0.0
    for s in skills_list:
        nm = s.get("name", "").lower()
        if any(kw in nm for kw in ai_kws):
            prof = s.get("proficiency", "")
            dur  = s.get("duration_months") or 0
            end  = s.get("endorsements") or 0
            if prof in ("expert", "advanced"):
                depth_bonus += min(1.0, (dur / 24.0) * 0.5 + (end / 30.0) * 0.5)
 
    must_score  = len(matched_must) / len(MUST_HAVE_GROUPS)
    nice_score  = len(matched_nice) / len(NICE_TO_HAVE_GROUPS)
    depth_score = min(0.15, depth_bonus * 0.025)
 
    # Penalty: CV / speech only without NLP/IR
    has_nlp = any(g in matched_must for g in [
        "nlp_ir_core", "embeddings_retrieval", "ranking_evaluation", "llm_transformers"
    ])
    cv_only = any(kw in text_blob for kw in [
        "computer vision", "object detection", "speech recognition",
        "robotics", "opencv", "yolo",
    ])
    if cv_only and not has_nlp:
        must_score *= 0.4
 
    return must_score, nice_score, depth_score, matched_must
 
 
def score_experience(yrs):
    """Score years of experience fit. Ideal: 5-9 years."""
    if 5 <= yrs <= 9:   return 1.00
    if 4 <= yrs < 5:    return 0.85
    if 9 < yrs <= 11:   return 0.90
    if 3 <= yrs < 4:    return 0.60
    if yrs > 11:        return 0.70
    if 2 <= yrs < 3:    return 0.35
    return 0.15
 
 
def score_location(profile):
    loc     = (profile.get("location") or "").lower()
    country = (profile.get("country") or "").lower()
    if country == "india":
        return 1.0 if any(city in loc for city in INDIA_PREFERRED) else 0.75
    return 0.30
 
 
def score_behavioral(signals):
    """Score all 23 Redrob behavioral signals."""
    if not signals:
        return 0.25
 
    s = 0.0
 
    if signals.get("open_to_work_flag"):
        s += 0.10
 
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            ld   = datetime.strptime(last_active, "%Y-%m-%d").date()
            days = (TODAY - ld).days
            if days <= 7:    s += 0.10
            elif days <= 30: s += 0.08
            elif days <= 90: s += 0.05
            else:            s += 0.01
        except Exception:
            s += 0.03
 
    notice = signals.get("notice_period_days")
    if notice is not None:
        if notice <= 30:   s += 0.13
        elif notice <= 60: s += 0.09
        elif notice <= 90: s += 0.04
        else:              s += 0.00
    else:
        s += 0.05
 
    resp_rate = signals.get("recruiter_response_rate")
    if resp_rate is not None:
        s += resp_rate * 0.12
 
    resp_time = signals.get("avg_response_time_hours")
    if resp_time is not None:
        s += max(0.0, 1.0 - resp_time / 168.0) * 0.07
 
    completeness = signals.get("profile_completeness_score")
    if completeness is not None:
        s += (completeness / 100.0) * 0.06
 
    if signals.get("verified_email"):    s += 0.02
    if signals.get("verified_phone"):    s += 0.02
    if signals.get("linkedin_connected"): s += 0.02
 
    github = signals.get("github_activity_score", -1)
    if github is not None and github >= 0:
        s += (github / 100.0) * 0.08
 
    saved = signals.get("saved_by_recruiters_30d") or 0
    s += min(0.06, saved * 0.006)
 
    icr = signals.get("interview_completion_rate")
    if icr is not None:
        s += icr * 0.08
 
    oar = signals.get("offer_acceptance_rate")
    if oar is not None and oar >= 0:
        s += oar * 0.04
 
    if signals.get("willing_to_relocate"):
        s += 0.03
 
    return min(1.0, s)
 
 
def score_education(education):
    if not education:
        return 0.40
    tier_map  = {"tier_1": 1.0, "tier_2": 0.85, "tier_3": 0.65,
                 "tier_4": 0.50, "unknown": 0.40}
    rel_fields = [
        "computer science", "information technology", "software",
        "artificial intelligence", "machine learning", "data science",
        "electronics", "electrical", "mathematics", "statistics",
        "computational", "engineering",
    ]
    best = 0.0
    for edu in education:
        base  = tier_map.get(edu.get("tier", "unknown"), 0.40)
        field = (edu.get("field_of_study") or "").lower()
        if any(rf in field for rf in rel_fields):
            base = min(1.0, base + 0.10)
        best = max(best, base)
    return best
 
 
def score_certifications(certs):
    if not certs:
        return 0.0
    total = 0.0
    for cert in certs:
        nm   = (cert.get("name") or "").lower()
        year = cert.get("year") or 0
        rec  = 1.0 if year >= 2022 else (0.7 if year >= 2019 else 0.4)
        if any(kw in nm for kw in AI_CERTS):
            total += 0.05 * rec
    return min(0.15, total)
 
 
def score_salary(signals):
    sal = (signals.get("expected_salary_range_inr_lpa") or {})
    mx  = sal.get("max")
    if mx is None: return 0.50
    if mx <= 30:   return 1.00
    if mx <= 40:   return 0.85
    if mx <= 50:   return 0.65
    if mx <= 60:   return 0.45
    return 0.20
 
 
def score_assessments(signals):
    assessments = signals.get("skill_assessment_scores") or {}
    relevant    = [v for k, v in assessments.items()
                   if k.lower() in ROLE_RELEVANT_ASSESSMENTS]
    if not relevant:
        return 0.0
    return (sum(relevant) / len(relevant)) / 100.0

# ─── COMPOSITE SCORE ──────────────────────────────────────────────────────────
 
def compute_score(candidate):
    """Returns (score, matched_must, text_blob)."""
    profile  = candidate.get("profile") or {}
    career   = candidate.get("career_history") or []
    skills   = candidate.get("skills") or []
    signals  = candidate.get("redrob_signals") or {}
    edu      = candidate.get("education") or []
    certs    = candidate.get("certifications") or []
 
    text_blob = build_text_blob(candidate)
 
    career_s, disq, has_retrieval = score_career(profile, career)
    must_s, nice_s, depth_s, matched_must = score_skills(text_blob, skills)
 
    # Hard gate: need retrieval title OR ≥2 must-have skill groups
    if not has_retrieval and len(matched_must) < 2:
        return 0.0, matched_must, text_blob
 
    yrs      = float(profile.get("years_of_experience") or 0)
    exp_s    = score_experience(yrs)
    loc_s    = score_location(profile)
    beh_s    = score_behavioral(signals)
    edu_s    = score_education(edu)
    cert_s   = score_certifications(certs)
    sal_s    = score_salary(signals)
    assess_s = score_assessments(signals)
 
    composite = (
        career_s  * 0.40 +
        must_s    * 0.18 +
        nice_s    * 0.06 +
        depth_s   * 1.00 +   # capped at 0.15
        exp_s     * 0.10 +
        beh_s     * 0.15 +
        loc_s     * 0.05 +
        edu_s     * 0.03 +
        cert_s    * 1.00 +   # capped at 0.15
        assess_s  * 0.03 +
        sal_s     * 0.03
    )
    composite *= (1.0 - disq)
    return min(1.0, max(0.0, composite)), matched_must, text_blob
__all__ = [
    "is_honeypot",
    "compute_score",
    "build_text_blob"
]
