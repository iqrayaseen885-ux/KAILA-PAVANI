# AI Government Scheme Recommender

Find every government scheme you are eligible for, instantly.

GovScheme AI is an intelligent welfare scheme discovery platform that matches citizens of Telangana and India with relevant central and state government schemes based on their profile. It is designed for real impact: many eligible citizens miss out on benefits simply because they do not know those schemes exist.

## Live Demo

Enter your age, income, gender, occupation, social category, and district to get matched with relevant schemes, ranked by eligibility and relevance. The app also provides AI-powered guidance on which scheme to apply for first.

## What It Does

- Collects a citizen's basic profile: age, income, gender, occupation, social category, and district.
- Runs a rule-based eligibility matching engine against government scheme data.
- Scores and ranks matched schemes by relevance.
- Uses Claude AI to generate a personalized two-sentence tip on which scheme to apply for first.
- Shows benefit amounts, scheme descriptions, and step-by-step application instructions.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Scheme Data | myscheme.gov.in official Government of India API, maintained by NIC |
| AI Advisor | Anthropic Claude API, `claude-sonnet-4` |
| Hosting | Static hosting on GitHub Pages, Vercel, or Netlify |

## Data Source

All scheme data is sourced from [myscheme.gov.in](https://www.myscheme.gov.in/), the official Government of India scheme portal maintained by the National Informatics Centre.

Example API endpoint:

```text
https://api.myscheme.gov.in/search/v4/schemes?lang=en&state=Telangana&central=true
```

Using the official data source helps ensure:

- Scheme names, benefits, and eligibility rules are government-verified.
- Data can stay current as schemes are updated by the government.
- The app avoids fake or hallucinated scheme information.

## How Matching Works

### Step 1: Rule-Based Filtering

Each scheme has hard eligibility constraints such as age, income, gender, and occupation. The matching engine filters out schemes the user does not qualify for.

### Step 2: Weighted Scoring

Eligible schemes are scored from 0 to 99 percent based on:

- How far the user's income is below the eligibility ceiling.
- Whether the scheme is Telangana-specific.
- Occupation match depth.

### Step 3: AI Tip

The top matched schemes are sent to Claude with the user's profile. Claude returns a short, personalized, actionable recommendation.

## Project Structure

```text
govscheme-ai/
├── index.html          # Main app
├── README.md           # Project overview
├── CONTRIBUTING.md     # Contribution guide
├── AGENTS.md           # AI agent architecture notes
└── USER_MANUAL.md      # End-user guide
```

## Setup and Running Locally

No build step is required. Open `index.html` in a browser.

```bash
git clone https://github.com/your-username/govscheme-ai.git
cd govscheme-ai
open index.html
```

On Windows, you can double-click `index.html` or run:

```powershell
Start-Process .\index.html
```

## Enabling AI Tips

To enable the AI tip feature during local experimentation, add your Anthropic API key where the API request is configured:

```js
headers: {
  "Content-Type": "application/json",
  "x-api-key": "YOUR_ANTHROPIC_API_KEY"
}
```

For production, move the Anthropic API call to a backend server so the API key is never exposed in the browser.

## Roadmap

- [ ] Connect live myscheme.gov.in API, replacing hardcoded data.
- [ ] Add multilingual support for Telugu and Hindi.
- [ ] Add voice input for low-literacy users.
- [ ] Add WhatsApp bot integration.
- [ ] Add offline PWA mode for rural areas with poor connectivity.
- [ ] Add document checklist generation per scheme.
- [ ] Add backend and user history with Node.js and Supabase.

## Team

Built at `[Hackathon Name]` on `[Date]` by `[Team Name]`.

## License

MIT License. Free to use, modify, and distribute.
