# GovScheme AI Agents

This document describes the AI and automation architecture for GovScheme AI.

## Agent Purpose

The AI advisor helps users decide which eligible government scheme to apply for first. It does not determine eligibility by itself. Eligibility should be handled by rule-based logic using official scheme data.

## Core Responsibilities

The system is divided into three responsibilities:

- Profile collection: gather basic user inputs such as age, income, gender, occupation, category, and district.
- Eligibility matching: filter and rank government schemes using deterministic rules.
- AI advice: generate a short, personalized recommendation from the top matched schemes.

## Matching Agent

The matching agent applies hard eligibility rules before any AI response is generated.

Inputs:

- User age
- Annual income
- Gender
- Occupation
- Social category
- District or state
- Scheme eligibility rules

Outputs:

- Eligible schemes
- Match score from 0 to 99 percent
- Ranking by relevance
- Basic reason for each match

The matching agent should be deterministic and explainable. It should not rely on an LLM to decide whether a user is eligible.

## Scoring Rules

Eligible schemes are scored using weighted relevance signals:

- Income fit: stronger match when the user's income is comfortably below the eligibility ceiling.
- Local relevance: Telangana-specific schemes receive a local relevance bonus.
- Occupation fit: schemes closely matching the user's occupation rank higher.

The score should help order results, not create eligibility where eligibility does not exist.

## AI Advisor Agent

The AI advisor receives the user's profile and the top matched schemes. It returns a concise recommendation explaining which scheme to consider first and why.

Expected output:

- Two sentences.
- Plain language.
- Actionable next step.
- No invented benefits, deadlines, eligibility rules, or application links.

## Prompting Guidelines

The AI advisor prompt should include:

- User profile summary.
- Top matched schemes.
- Verified benefit and eligibility information.
- Instruction to avoid unsupported claims.
- Instruction to recommend only from the provided schemes.

Example instruction:

```text
Based only on the provided schemes and user profile, recommend the best scheme to apply for first. Keep the response to two sentences and do not invent eligibility rules, documents, deadlines, or benefits.
```

## Data Boundaries

Agents should use official scheme data from [myscheme.gov.in](https://www.myscheme.gov.in/) or other verified government sources.

Agents must not:

- Invent scheme names.
- Invent benefit amounts.
- Invent eligibility criteria.
- Ask for sensitive identifiers such as Aadhaar numbers, bank account numbers, passwords, or OTPs.
- Store personal user data unless a secure backend is added.

## API Key Handling

During local experimentation, the Anthropic API key may be added near the API request code. For production, move AI calls to a backend server and store the key in environment variables.

Never expose production API keys in client-side code.

## Failure Behavior

If the AI advisor fails, the app should still show rule-based scheme matches. The AI tip is helpful, but it is not required for the core matching experience.

If live scheme data is unavailable, the app should clearly indicate that results may be limited or unavailable instead of showing unverified information.

## Future Agent Improvements

- Multilingual advisor responses in Telugu and Hindi.
- Document checklist generator for each scheme.
- Voice input support.
- WhatsApp assistant integration.
- Backend-backed user history.
- Safer server-side AI routing with rate limits and logging.
