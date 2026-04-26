def calculate_match_score(jd_data, candidate):
    jd_skills = {s.lower().strip() for s in jd_data.get("skills", []) if str(s).strip()}
    candidate_skills = {
        s.lower().strip() for s in candidate.get("skills", []) if str(s).strip()
    }

    # Skill Match
    matched_skills = jd_skills.intersection(candidate_skills)
    missing_skills = jd_skills.difference(candidate_skills)

    if len(jd_skills) > 0:
        skill_score = (len(matched_skills) / len(jd_skills)) * 100
    else:
        skill_score = 0

    # Experience Match
    jd_exp = jd_data.get("experience_years", 0)
    cand_exp = candidate.get("experience", 0)

    if jd_exp <= 0:
        exp_score = 100
    elif cand_exp >= jd_exp:
        exp_score = 100
    else:
        exp_score = (cand_exp / jd_exp) * 100

    # Final Match Score (weighted)
    match_score = (0.7 * skill_score) + (0.3 * exp_score)

    return {
        "match_score": round(match_score, 2),
        "skill_score": round(skill_score, 2),
        "experience_score": round(exp_score, 2),
        "matched_skills": sorted(list(matched_skills)),
        "missing_skills": sorted(list(missing_skills)),
    }