import json
from typing import Any


def first_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return ""


def text_from(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "; ".join(filter(None, (text_from(item) for item in value)))
    if isinstance(value, dict):
        preferred = first_value(
            value.get("en"),
            value.get("text"),
            value.get("value"),
            value.get("name"),
            value.get("label"),
        )
        return text_from(preferred) if preferred else json.dumps(value, ensure_ascii=True)
    return str(value)


def find_scheme_array(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, dict):
        return []

    candidates = [
        raw.get("data"),
        raw.get("schemes"),
        raw.get("results"),
        raw.get("response"),
        raw.get("payload", {}).get("schemes") if isinstance(raw.get("payload"), dict) else None,
    ]

    if isinstance(raw.get("data"), dict):
        candidates.extend([raw["data"].get("schemes"), raw["data"].get("results")])

    for candidate in candidates:
        if isinstance(candidate, list):
            return candidate
    return []


def map_scheme(scheme: dict[str, Any]) -> dict[str, Any]:
    name = first_value(scheme.get("scheme_name"), scheme.get("schemeName"), scheme.get("name"), scheme.get("title"))
    description = first_value(
        scheme.get("description"),
        scheme.get("schemeDescription"),
        scheme.get("briefDescription"),
        scheme.get("summary"),
    )
    benefits = first_value(scheme.get("benefits"), scheme.get("benefit"), scheme.get("benefitDetails"))
    eligibility = first_value(
        scheme.get("eligibility"),
        scheme.get("eligibilityCriteria"),
        scheme.get("eligibility_details"),
    )
    category = first_value(scheme.get("category"), scheme.get("schemeCategory"), scheme.get("categoryName"))
    level = first_value(scheme.get("level"), scheme.get("schemeLevel"), scheme.get("schemeType"))

    return {
        "id": text_from(first_value(scheme.get("id"), scheme.get("schemeId"), scheme.get("slug"), name)),
        "title": text_from(name) or "Untitled scheme",
        "description": text_from(description),
        "benefits": text_from(benefits),
        "eligibility": text_from(eligibility),
        "category": text_from(category) or "Uncategorized",
        "level": text_from(level) or "Scheme",
        "raw": scheme,
    }


def map_schemes(raw: Any) -> list[dict[str, Any]]:
    return [map_scheme(scheme) for scheme in find_scheme_array(raw) if isinstance(scheme, dict)]


def filter_schemes(schemes: list[dict[str, Any]], query: str, category: str) -> list[dict[str, Any]]:
    query = str(query or "").strip().lower()
    filtered = []

    for scheme in schemes:
        matches_category = category == "All categories" or scheme["category"] == category
        haystack = " ".join(str(scheme.get(key, "")) for key in ["title", "description", "benefits", "eligibility", "category"]).lower()
        matches_query = not query or query in haystack
        if matches_category and matches_query:
            filtered.append(scheme)

    return filtered
