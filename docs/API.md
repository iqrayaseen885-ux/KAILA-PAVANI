# myScheme API Notes

GovScheme AI is wired to the myScheme search endpoint from the project brief:

```text
https://api.myscheme.gov.in/search/v4/schemes?lang=en&state=Telangana
```

## Streamlit Service

The reusable Python API wrapper lives in `services/scheme_api.py`.

```python
from services.scheme_api import fetch_schemes

raw_json = fetch_schemes("Telangana")
```

`fetch_schemes(state, api_key="", api_key_header="x-api-key")` accepts:

- `state`: state or union territory name, such as `Telangana`.
- `api_key`: optional official myScheme/APISetu gateway key.
- `api_key_header`: optional header name, defaulting to `x-api-key`.

The function returns raw JSON and raises a readable error for non-2xx responses.

## Verification Status

Tested on 30 May 2026 from PowerShell:

```powershell
Invoke-WebRequest -Uri "https://api.myscheme.gov.in/search/v4/schemes?lang=en&state=Telangana" -Method Get
```

Observed response:

```json
{"message":"Unauthorized"}
```

So the Streamlit integration, loading state, raw JSON viewer, and error state are implemented, but the endpoint is not confirmed as a public unauthenticated API. The team should request official myScheme/APISetu access before marking the raw JSON deliverable as fully complete.

## Mapping

`services/scheme_mapper.py` maps likely API fields into card fields:

```python
{
    "title": scheme["name"],
    "description": scheme["description"],
    "benefits": scheme["benefits"],
    "eligibility": scheme["eligibility"],
}
```

It also supports variants such as `scheme_name`, `schemeName`, `briefDescription`, and `eligibilityCriteria`.
