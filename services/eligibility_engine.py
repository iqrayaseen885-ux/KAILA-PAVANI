import re
from typing import Any

MAX_SCORE = 99


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def includes_any(text: str, values: list[str]) -> bool:
    lowered = normalize(text)
    return any(normalize(value) in lowered for value in values)


def scheme_text(scheme: dict[str, Any]) -> str:
    return " ".join(str(scheme.get(key, "")) for key in ["title", "description", "benefits", "eligibility", "category", "level"])


def income_ceiling_from_text(text: str) -> int | None:
    matches = re.findall(r"(?:income|annual income|family income)[^0-9]{0,45}(?:rs\.?|inr|rs|rupees)?\s?([0-9,]{5,9})", text, flags=re.I)
    amounts = [int(match.replace(",", "")) for match in matches if match.replace(",", "").isdigit()]
    return max(amounts) if amounts else None


def age_range_from_text(text: str) -> tuple[int | None, int | None]:
    between = re.search(r"(?:age|aged)[^0-9]{0,30}([0-9]{1,3})\s*(?:-|to)\s*([0-9]{1,3})", text, flags=re.I)
    if between:
        return int(between.group(1)), int(between.group(2))

    lower = re.search(r"(?:age|aged)[^0-9]{0,30}(?:above|over|minimum|min\.?|from)\s+([0-9]{1,3})", text, flags=re.I)
    upper = re.search(r"(?:age|aged)[^0-9]{0,30}(?:below|under|maximum|max\.?|up to)\s+([0-9]{1,3})", text, flags=re.I)
    return (int(lower.group(1)) if lower else None, int(upper.group(1)) if upper else None)


def disqualified_by_hard_rules(profile: dict[str, Any], text: str) -> bool:
    gender = normalize(profile.get("gender"))
    if gender and gender != "any":
        women_only = includes_any(text, ["women", "woman", "female", "girl"])
        men_only = includes_any(text, ["men only", "male candidates", "boys"])
        if women_only and gender not in ["female", "woman", "girl"]:
            return True
        if men_only and gender not in ["male", "man", "boy"]:
            return True

    category = normalize(profile.get("category"))
    if category and category != "any":
        limited = includes_any(text, ["scheduled caste", "scheduled tribe", "sc ", "st ", "obc", "minority"])
        if limited and not includes_any(text, [category]):
            return True

    min_age, max_age = age_range_from_text(text)
    if min_age is not None and profile["age"] < min_age:
        return True
    if max_age is not None and profile["age"] > max_age:
        return True

    ceiling = income_ceiling_from_text(text)
    if ceiling is not None and profile["income"] > ceiling:
        return True

    return False


def occupation_score(profile: dict[str, Any], text: str) -> int:
    occupation = normalize(profile.get("occupation"))
    if profile.get("student") and includes_any(text, ["student", "scholarship", "education", "matric", "school", "college"]):
        return 24
    if occupation and includes_any(text, [occupation]):
        return 24
    if occupation == "farmer" and includes_any(text, ["agriculture", "crop", "farmer"]):
        return 24
    if occupation == "entrepreneur" and includes_any(text, ["business", "msme", "startup", "enterprise"]):
        return 24
    if occupation == "worker" and includes_any(text, ["worker", "labour", "labor", "employment"]):
        return 24
    return 8


def income_score(profile: dict[str, Any], text: str) -> int:
    ceiling = income_ceiling_from_text(text)
    if not ceiling:
        return 15
    room = max(0, ceiling - profile["income"])
    return 12 + round(18 * min(room / ceiling, 1))


def location_score(profile: dict[str, Any], text: str) -> int:
    state = normalize(profile.get("state"))
    if state and includes_any(text, [state]):
        return 20
    if includes_any(text, ["central sector", "centrally sponsored", "central government"]):
        return 12
    return 8


def category_score(profile: dict[str, Any], text: str) -> int:
    category = normalize(profile.get("category"))
    if not category or category == "any":
        return 10
    return 15 if includes_any(text, [category]) else 8


def score_scheme(profile: dict[str, Any], scheme: dict[str, Any]) -> dict[str, Any]:
    text = scheme_text(scheme)
    if disqualified_by_hard_rules(profile, text):
        return {**scheme, "eligible": False, "match_score": 0, "match_reason": "Filtered out by a detected hard rule."}

    score = min(
        MAX_SCORE,
        20 + income_score(profile, text) + location_score(profile, text) + occupation_score(profile, text) + category_score(profile, text),
    )
    return {
        **scheme,
        "eligible": True,
        "match_score": score,
        "match_reason": "Matched using income fit, location relevance, occupation fit, and category relevance.",
    }


def recommend_schemes(profile: dict[str, Any], schemes: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    scored = [score_scheme(profile, scheme) for scheme in schemes]
    eligible = [scheme for scheme in scored if scheme["eligible"]]
    return sorted(eligible, key=lambda item: (-item["match_score"], item["title"]))[:limit]
