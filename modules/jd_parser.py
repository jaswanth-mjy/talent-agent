from llm.ollama_client import generate
import json
import re


def _coerce_experience(value):
    if isinstance(value, int):
        return max(value, 0)
    if isinstance(value, float):
        return max(int(value), 0)
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group())
    return 0


def _normalize_output(data):
    role = str(data.get("role", "Unknown")).strip() or "Unknown"
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in re.split(r",|/|\\|\n", skills) if s.strip()]
    if not isinstance(skills, list):
        skills = []
    skills = [str(skill).strip() for skill in skills if str(skill).strip()]
    experience = _coerce_experience(data.get("experience_years", 0))
    return {
        "role": role,
        "skills": skills,
        "experience_years": experience,
    }


def clean_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return _normalize_output(json.loads(match.group()))
    except:
        pass
    return None


def _fallback_parse(jd_text):
    skills = []
    known_skills = [
        "python",
        "django",
        "flask",
        "fastapi",
        "sql",
        "postgresql",
        "mysql",
        "aws",
        "docker",
        "kubernetes",
        "java",
        "spring",
        "javascript",
        "react",
    ]
    lowered = jd_text.lower()
    for skill in known_skills:
        if skill in lowered:
            skills.append(skill)

    exp_match = re.search(r"(\d+)\+?\s*(?:years|year|yrs|yr)", lowered)
    experience_years = int(exp_match.group(1)) if exp_match else 0

    role = "Unknown"
    role_match = re.search(
        r"(?:looking for|hiring|need|seeking)\s+(.+?)(?:with|who|having|,|\.|$)",
        lowered,
    )
    if role_match:
        role = role_match.group(1).strip().title()

    return {
        "role": role,
        "skills": skills,
        "experience_years": experience_years,
    }


def parse_jd(jd_text):
    prompt = f"""
    Extract structured fields from this job description.

    Required JSON schema:
    {{
      "role": "string",
      "skills": ["skill1", "skill2"],
      "experience_years": number
    }}

    Rules:
    1) Return ONLY valid JSON
    2) Do not include markdown
    3) Keep skills concise

    JD:
    {jd_text}
    """

    response = generate(prompt)

    data = clean_json(response)

    if data:
        return data

    return _fallback_parse(jd_text)