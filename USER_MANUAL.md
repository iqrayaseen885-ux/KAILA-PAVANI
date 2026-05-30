# GovScheme AI User Manual

## Overview
GovScheme AI helps citizens of Telangana and India discover government welfare schemes they may be eligible for.

The app matches users with relevant central and state government schemes using rule-based eligibility logic and provides an AI-powered recommendation for the best scheme to apply for first.

## What It Does
- Collects a citizen's basic profile:
  - Age
  - Annual income
  - Gender
  - Occupation
  - Social category
  - District
- Runs rule-based eligibility matching against government scheme data
- Scores and ranks matched schemes by relevance
- Generates a personalized AI tip for the top matched scheme
- Shows benefits, scheme descriptions, and application guidance

## How to Use
1. Open `index.html` in a browser.
2. Enter your profile details:
   - Age
   - Income
   - Gender
   - Occupation
   - Social category
   - District
3. Submit the form.
4. Review the matched schemes in the results.
5. Read the AI recommendation tip to see which scheme to apply for first.

## How Matching Works
### Step 1: Rule-Based Filtering
The app filters schemes using hard eligibility rules such as age, income, gender, and occupation.

### Step 2: Weighted Scoring
Eligible schemes are scored based on:
- Income fit (how far the user's income is below the eligibility ceiling)
- Telangana-specific relevance
- Occupation match depth

### Step 3: AI Tip
The top matched schemes are sent to Claude AI, which returns a short, personalized recommendation.

## Data Source
The app uses official government scheme data from `myscheme.gov.in`.

Example endpoint:
```text
https://api.myscheme.gov.in/search/v4/schemes?lang=en&state=Telangana&central=true
```

Using official data ensures scheme names, benefits, and eligibility information are government-verified.

## Running the App Locally
No build step is required.

Option 1: Open `index.html` directly in your browser.

Option 2: In PowerShell:
```powershell
Start-Process .\index.html
```

## Enabling AI Tips
To enable AI tips locally, add your Anthropic API key where the AI request is configured:
```js
headers: {
  "Content-Type": "application/json",
  "x-api-key": "YOUR_ANTHROPIC_API_KEY"
}
```

> Important: For production, move the Anthropic API call to a backend server so the API key is not exposed in client-side code.

## Notes
- The core matching experience works even if the AI tip feature is disabled.
- The app is designed to avoid invented or unsupported scheme claims.

## Future Enhancements
Planned improvements include:
- Connecting live scheme data from the official API
- Telugu and Hindi support
- Voice input for low-literacy users
- WhatsApp integration
- Offline PWA mode
- Document checklist generation per scheme
- Backend user history and data storage
