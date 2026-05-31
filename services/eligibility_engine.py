import re
from typing import Any

MAX_SCORE = 99
OCCUPATION_TAGS = {
    "student": {"student", "scholarship", "education", "school", "college"},
    "farmer": {"farmer", "agriculture", "crop", "landholder"},
    "entrepreneur": {"entrepreneur", "business", "msme", "startup", "enterprise", "loan"},
    "worker": {"worker", "labour", "labor", "unorganised worker", "pension"},
    "unemployed": {"unemployed", "skill", "training", "job", "placement", "livelihood"},
}


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def includes_any(text: str, values: list[str]) -> bool:
    lowered = normalize(text)
    return any(normalize(value) in lowered for value in values)


def normalized_tags(scheme: dict[str, Any]) -> set[str]:
    tags = scheme.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    return {normalize(tag) for tag in tags if normalize(tag)}


def scheme_text(scheme: dict[str, Any]) -> str:
    return " ".join(str(scheme.get(key, "")) for key in ["title", "description", "benefits", "eligibility", "category", "level", "state", "tags"])


def is_student_scheme(text: str) -> bool:
    return includes_any(text, ["student", "scholarship", "education", "matric", "school", "college"])


def is_farmer_scheme(text: str) -> bool:
    return includes_any(text, ["farmer", "agriculture", "crop", "landholder", "land holder", "rythu"])


def is_entrepreneur_scheme(text: str) -> bool:
    return includes_any(text, ["business", "msme", "startup", "enterprise", "entrepreneur"])


def is_worker_scheme(text: str) -> bool:
    return includes_any(text, ["worker", "labour", "labor", "employment", "wage"])


def is_unemployed_scheme(text: str) -> bool:
    return includes_any(text, ["unemployed", "employment", "skill", "training", "job", "placement", "livelihood"])


def matches_selected_occupation(profile: dict[str, Any], scheme: dict[str, Any], text: str) -> bool:
    occupation = normalize(profile.get("occupation"))
    tags = normalized_tags(scheme)
    expected_tags = OCCUPATION_TAGS.get(occupation)

    if expected_tags and tags:
        return bool(tags & expected_tags)

    if occupation == "student":
        return is_student_scheme(text)
    if occupation == "farmer":
        return is_farmer_scheme(text)
    if occupation == "entrepreneur":
        return is_entrepreneur_scheme(text)
    if occupation == "worker":
        return is_worker_scheme(text)
    if occupation == "unemployed":
        return is_unemployed_scheme(text)

    return True


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


def disqualified_by_hard_rules(profile: dict[str, Any], scheme: dict[str, Any], text: str) -> bool:
    if not matches_selected_occupation(profile, scheme, text):
        return True

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
        limited = includes_any(text, ["scheduled caste", "scheduled tribe", "sc ", "st ", "obc", "minority", "minorities"])
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


def occupation_score(profile: dict[str, Any], scheme: dict[str, Any], text: str) -> int:
    occupation = normalize(profile.get("occupation"))
    tags = normalized_tags(scheme)
    expected_tags = OCCUPATION_TAGS.get(occupation, set())

    if expected_tags and tags & expected_tags:
        return 28

    if occupation == "student" and profile.get("student") and is_student_scheme(text):
        return 24
    if occupation and includes_any(text, [occupation]):
        return 24
    if occupation == "farmer" and is_farmer_scheme(text):
        return 24
    if occupation == "entrepreneur" and is_entrepreneur_scheme(text):
        return 24
    if occupation == "worker" and is_worker_scheme(text):
        return 24
    if occupation == "unemployed" and is_unemployed_scheme(text):
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
    if disqualified_by_hard_rules(profile, scheme, text):
        return {**scheme, "eligible": False, "match_score": 0, "match_reason": "Filtered out by a detected hard rule."}

    score = min(
        MAX_SCORE,
        20 + income_score(profile, text) + location_score(profile, text) + occupation_score(profile, scheme, text) + category_score(profile, text),
    )
    return {
        **scheme,
        "eligible": True,
        "match_score": score,
        "match_reason": "Matched using income fit, location relevance, occupation fit, and category relevance.",
    }


def recommend_schemes(profile: dict[str, Any], schemes: list[dict[str, Any]], limit: int | None = None) -> list[dict[str, Any]]:
    scored = [score_scheme(profile, scheme) for scheme in schemes]
    eligible = [scheme for scheme in scored if scheme["eligible"]]
    ordered = sorted(eligible, key=lambda item: (-item["match_score"], item["title"]))
    return ordered if limit is None else ordered[:limit]
