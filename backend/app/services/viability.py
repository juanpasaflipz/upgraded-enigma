import json
import os
import re

AI_MODEL = os.getenv("OPENAI_MODEL_GPT", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

VIABILITY_SYSTEM = (
    "You are a product triage expert. Decide if a YouTube video transcript describes a project that can be turned into a minimal software MVP.\n"
    "Return strict JSON with: mvp_viability ('mvp-ready'|'idea-only'|'not-a-project'), viability_score [0..1], viability_reason (<=200 chars)."
)

VIABILITY_USER_TMPL = """Title: {title}

Transcript (truncated if long):
{transcript}

Criteria:
- 'mvp-ready': clear user problem, target user, 2–6 concrete features, feasible scope for a clickable prototype/site/app.
- 'idea-only': a concept is discussed but lacks concrete features or target user.
- 'not-a-project': music clip, vlog, news, non-instructional content, or unrelated to building a product.

Return JSON only.
"""


def naive_fallback_viability(title: str, transcript: str):
    text = f"{title}\n{transcript}".lower()
    # quick signals
    project_terms = sum(
        bool(
            re.search(
                r"\b(sign ?up|feature|dashboard|api|pricing|onboarding|user|auth|prototype|mvp|build|launch|roadmap)\b",
                text,
            )
        )
        for _ in [0, 1, 2, 3, 4]
    )
    length_ok = len(transcript.split()) > 120
    how_to = bool(re.search(r"\b(how to|tutorial|we will build|let's build|step by step)\b", text))
    music_noise = bool(re.search(r"\b(lyrics|official video|music video)\b", text))
    vlog_noise = bool(re.search(r"\b(vlog|my day|travel vlog|reaction video)\b", text))
    news_noise = bool(re.search(r"\b(breaking news|press conference|announcement)\b", text))

    if music_noise or vlog_noise or news_noise:
        return {
            "mvp_viability": "not-a-project",
            "viability_score": 0.05,
            "viability_reason": "Looks like non-project content (music/vlog/news).",
        }

    if (project_terms >= 1 and (length_ok or how_to)):
        return {
            "mvp_viability": "mvp-ready",
            "viability_score": 0.7,
            "viability_reason": "Contains product signals (features/how-to) with enough content.",
        }

    if project_terms == 0 and not how_to:
        return {
            "mvp_viability": "not-a-project",
            "viability_score": 0.15,
            "viability_reason": "No product signals; likely not a buildable project.",
        }

    return {
        "mvp_viability": "idea-only",
        "viability_score": 0.4,
        "viability_reason": "Concept present but lacks concrete features/target user.",
    }


def check_viability(title: str, transcript: str):
    if not OPENAI_API_KEY:
        return naive_fallback_viability(title or "", transcript or "")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = VIABILITY_USER_TMPL.format(title=title or "", transcript=transcript[:8000])
        resp = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": VIABILITY_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        out = {
            "mvp_viability": data.get("mvp_viability"),
            "viability_score": float(data.get("viability_score", 0)),
            "viability_reason": (data.get("viability_reason", "") or "")[:300],
        }
        if out["mvp_viability"] not in {"mvp-ready", "idea-only", "not-a-project"}:
            return naive_fallback_viability(title or "", transcript or "")
        out["viability_score"] = max(0.0, min(1.0, out["viability_score"]))
        return out
    except Exception:
        return naive_fallback_viability(title or "", transcript or "")
