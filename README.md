# GovScheme AI Streamlit App

A Streamlit prototype for matching citizens with government schemes using live myScheme data, frontend-friendly scheme cards, search/category filters, and deterministic recommendation scoring.

## What Is Implemented

- API service: `services/scheme_api.py`
- Data mapping and filters: `services/scheme_mapper.py`
- Eligibility scoring engine: `services/eligibility_engine.py`
- Streamlit frontend: `app.py`
- API team notes: `docs/API.md`

## Run Locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## API Note

The app calls:

```text
https://api.myscheme.gov.in/search/v4/schemes?lang=en&state=Telangana
```

A direct test from this machine returned `Unauthorized`, so the app includes optional API key/header fields in the sidebar. If your team receives official myScheme/APISetu credentials, enter them there and click `Fetch schemes`.

For demos without API access, click `Use local sample data` in the sidebar. The sample file is `data/schemes.json`; replace or expand it with scheme details copied from official myScheme scheme pages.

## Data Sources and Verification

- Official portal: [https://www.myscheme.gov.in/](https://www.myscheme.gov.in/)
- Official API endpoint: `https://api.myscheme.gov.in/search/v4/schemes`
- Verify every scheme on the official government scheme page before applying

## Team Responsibilities Covered

### Person 1 - API Integration Lead

- Reusable API service
- Live fetch attempt
- Loading and error states
- Raw JSON viewer
- API documentation

### Person 2 - Data Mapping and Scheme Cards

- Maps raw fields into `title`, `description`, `benefits`, `eligibility`
- Scheme cards
- Search box
- Category filter

### Person 3 - AI Eligibility Engine

- Rule-based scoring
- Match percentage
- Ranked recommendations
- Suggested first scheme from provided data

## Data Safety

The app does not invent scheme details. If the live API is unavailable, it shows an error instead of displaying unverified schemes.
