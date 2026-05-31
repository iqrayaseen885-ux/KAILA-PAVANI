from typing import Any

import requests

MYSCHEME_SEARCH_URL = "https://api.myscheme.gov.in/search/v4/schemes"


def fetch_schemes(state: str, api_key: str = "", api_key_header: str = "x-api-key") -> dict[str, Any]:
    """Fetch raw scheme JSON from myScheme."""
    params = {"lang": "en", "state": state}
    headers = {"Accept": "application/json"}

    if api_key:
        headers[api_key_header or "x-api-key"] = api_key

    response = requests.get(MYSCHEME_SEARCH_URL, params=params, headers=headers, timeout=25)

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(f"myScheme returned non-JSON response: HTTP {response.status_code}") from exc

    if response.status_code >= 400:
        message = data.get("message") if isinstance(data, dict) else str(data)
        raise RuntimeError(f"myScheme API request failed: HTTP {response.status_code} - {message}")

    return data
