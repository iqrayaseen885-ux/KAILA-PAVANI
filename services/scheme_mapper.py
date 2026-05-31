import json
from typing import Any
from urllib.parse import quote_plus


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


def list_from(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [text_from(item) for item in value if text_from(item)]
    return [text_from(value)]


def lower_text(value: Any) -> str:
    return text_from(value).lower()


def scheme_source_url(scheme: dict[str, Any]) -> str:
    title_raw = text_from(first_value(scheme.get("scheme_name"), scheme.get("schemeName"), scheme.get("name"), scheme.get("title")))
    title = title_raw.lower()
    category = lower_text(first_value(scheme.get("category"), scheme.get("schemeCategory"), scheme.get("categoryName")))
    state = lower_text(first_value(scheme.get("state"), scheme.get("stateName"), scheme.get("schemeState")))

    if "pmeg" in title or "employment generation" in title:
        return "https://www.msme.gov.in/"
    if "mudra" in title:
        return "https://www.mudra.org.in/"
    if "pradhan mantri kisan samman nidhi" in title or "pm kisan" in title or "kisan" in title or "agriculture" in category:
        return "https://pmkisan.gov.in/"
    if "e-shram" in title or "eshram" in title or "shram" in title or "labour welfare" in category:
        return "https://eshram.gov.in/"
    if "kaushal vikas" in title or "skill development" in category or "skill" in title:
        return "https://www.pmkvyofficial.org/"
    if "scholarship" in category or "scholarship" in title:
        return "https://scholarships.gov.in/"
    if "fasal bima" in title:
        return "https://pmfby.gov.in/"
    if "shram yogi" in title:
        return "https://pmsym.gov.in/"
    if "rythu bandhu" in title or ("telangana" in state and "agriculture" in category):
        return "https://rythubandhu.telangana.gov.in/"

    # fallback to myScheme search with quoted title for more exact results
    return f"https://www.myscheme.gov.in/search?q={quote_plus('"' + title_raw + '"')}"


def build_scheme_reference(scheme: dict[str, Any]) -> str:
    title = lower_text(first_value(scheme.get("scheme_name"), scheme.get("schemeName"), scheme.get("name"), scheme.get("title")))
    category = lower_text(first_value(scheme.get("category"), scheme.get("schemeCategory"), scheme.get("categoryName")))
    state = lower_text(first_value(scheme.get("state"), scheme.get("stateName"), scheme.get("schemeState")))

    references = ["Official source: myScheme portal"]
    if "telangana" in state or "telangana" in title:
        references.append("Telangana government scheme portal")
    if "pradhan mantri kisan samman nidhi" in title or "pm kisan" in title or "kisan" in title or "agriculture" in category:
        references.append("Ministry of Agriculture and Farmers Welfare")
    if "mudra" in title:
        references.append("Ministry of Finance / MUDRA scheme portal")
    if "kaushal vikas" in title or "skill development" in category or "skill" in title:
        references.append("Ministry of Skill Development and Entrepreneurship")
    if "e-shram" in title or "eshram" in title or "shram" in title or "labour welfare" in category:
        references.append("Ministry of Labour and Employment")
    if "scholarship" in category or "scholarship" in title:
        references.append("Ministry of Education / UGC / official scholarship portal")

    return "; ".join(dict.fromkeys(references)) + "."


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
    state = first_value(scheme.get("state"), scheme.get("stateName"), scheme.get("schemeState"))
    tags = first_value(scheme.get("tags"), scheme.get("keywords"), scheme.get("schemeTags"))
    source_url = first_value(scheme.get("source_url"), scheme.get("sourceUrl"), scheme.get("url"), scheme.get("link"))

    return {
        "id": text_from(first_value(scheme.get("id"), scheme.get("schemeId"), scheme.get("slug"), name)),
        "title": text_from(name) or "Untitled scheme",
        "description": text_from(description),
        "benefits": text_from(benefits),
        "eligibility": text_from(eligibility),
        "category": text_from(category) or "Uncategorized",
        "level": text_from(level) or "Scheme",
        "state": text_from(state),
        "tags": list_from(tags),
        "source_url": text_from(source_url) or scheme_source_url(scheme),
        "raw": scheme,
    }


def map_schemes(raw: Any) -> list[dict[str, Any]]:
    return [map_scheme(scheme) for scheme in find_scheme_array(raw) if isinstance(scheme, dict)]


def filter_schemes(schemes: list[dict[str, Any]], query: str, category: str) -> list[dict[str, Any]]:
    query = str(query or "").strip().lower()
    filtered = []

    for scheme in schemes:
        matches_category = category == "All categories" or scheme["category"] == category
        haystack = " ".join(str(scheme.get(key, "")) for key in ["title", "description", "benefits", "eligibility", "category", "state", "tags"]).lower()
        matches_query = not query or query in haystack
        if matches_category and matches_query:
            filtered.append(scheme)

    return filtered
