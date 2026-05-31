const MAX_SCORE = 99;

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function includesAny(text, values) {
  const normalizedText = normalize(text);
  return values.some((value) => normalizedText.includes(normalize(value)));
}

function combinedSchemeText(scheme) {
  return [scheme.title, scheme.description, scheme.benefits, scheme.eligibility, scheme.category, scheme.level].join(" ");
}

function incomeCeilingFromText(text) {
  const matches = [...text.matchAll(/(?:income|annual income|family income)[^\d]{0,40}(?:rs\.?|inr|rs|rupees)?\s?([\d,]{5,9})/gi)];
  const ceilings = matches
    .map((match) => Number(match[1].replace(/,/g, "")))
    .filter((amount) => Number.isFinite(amount) && amount > 0);

  return ceilings.length ? Math.max(...ceilings) : null;
}

function ageRangeFromText(text) {
  const lowerMatch = text.match(/(?:age|aged)[^\d]{0,30}(?:above|over|minimum|min\.?|from)\s+(\d{1,3})/i);
  const upperMatch = text.match(/(?:age|aged)[^\d]{0,30}(?:below|under|maximum|max\.?|up to)\s+(\d{1,3})/i);
  const betweenMatch = text.match(/(?:age|aged)[^\d]{0,30}(\d{1,3})\s*(?:-|to)\s*(\d{1,3})/i);

  if (betweenMatch) {
    return {
      min: Number(betweenMatch[1]),
      max: Number(betweenMatch[2])
    };
  }

  return {
    min: lowerMatch ? Number(lowerMatch[1]) : null,
    max: upperMatch ? Number(upperMatch[1]) : null
  };
}

function isDisqualifiedByHardRules(profile, schemeText) {
  const gender = normalize(profile.gender);
  if (gender && gender !== "any") {
    const womenOnly = includesAny(schemeText, ["women", "woman", "female", "girl"]);
    const menOnly = includesAny(schemeText, ["men only", "male candidates", "boys"]);
    if (womenOnly && !["female", "woman", "girl"].includes(gender)) return true;
    if (menOnly && !["male", "man", "boy"].includes(gender)) return true;
  }

  const category = normalize(profile.category);
  if (category && category !== "any") {
    const categoryLimited = includesAny(schemeText, ["scheduled caste", "scheduled tribe", "sc ", "st ", "obc", "minority"]);
    if (categoryLimited && !includesAny(schemeText, [category])) return true;
  }

  const ageRange = ageRangeFromText(schemeText);
  if (ageRange.min !== null && profile.age < ageRange.min) return true;
  if (ageRange.max !== null && profile.age > ageRange.max) return true;

  const incomeCeiling = incomeCeilingFromText(schemeText);
  if (incomeCeiling !== null && profile.income > incomeCeiling) return true;

  return false;
}

function occupationScore(profile, schemeText) {
  const occupation = normalize(profile.occupation);
  const studentTerms = ["student", "scholarship", "education", "matric", "school", "college"];

  if (profile.student && includesAny(schemeText, studentTerms)) return 24;
  if (occupation && includesAny(schemeText, [occupation])) return 24;
  if (occupation === "farmer" && includesAny(schemeText, ["agriculture", "crop", "farmer"])) return 24;
  if (occupation === "entrepreneur" && includesAny(schemeText, ["business", "msme", "startup", "enterprise"])) return 24;
  if (occupation === "worker" && includesAny(schemeText, ["worker", "labour", "labor", "employment"])) return 24;

  return 8;
}

function incomeScore(profile, schemeText) {
  const ceiling = incomeCeilingFromText(schemeText);
  if (!ceiling) return 15;

  const room = Math.max(0, ceiling - profile.income);
  const comfortRatio = Math.min(room / ceiling, 1);
  return 12 + Math.round(18 * comfortRatio);
}

function locationScore(profile, schemeText) {
  const state = normalize(profile.state);
  if (!state) return 10;
  if (includesAny(schemeText, [state])) return 20;
  if (includesAny(schemeText, ["central sector", "centrally sponsored", "central government"])) return 12;
  return 8;
}

function categoryScore(profile, schemeText) {
  const category = normalize(profile.category);
  if (!category || category === "any") return 10;
  return includesAny(schemeText, [category]) ? 15 : 8;
}

export function scoreScheme(profile, scheme) {
  const schemeText = combinedSchemeText(scheme);

  if (isDisqualifiedByHardRules(profile, schemeText)) {
    return {
      ...scheme,
      eligible: false,
      matchScore: 0,
      matchReason: "Filtered out by age, income, gender, or category rule detected in the scheme text."
    };
  }

  const score = Math.min(
    MAX_SCORE,
    20 + incomeScore(profile, schemeText) + locationScore(profile, schemeText) + occupationScore(profile, schemeText) + categoryScore(profile, schemeText)
  );

  return {
    ...scheme,
    eligible: true,
    matchScore: score,
    matchReason: "Passed detected hard rules and ranked by income fit, location relevance, occupation fit, and category relevance."
  };
}

export function recommendSchemes(profile, schemes, limit = 12) {
  return schemes
    .map((scheme) => scoreScheme(profile, scheme))
    .filter((scheme) => scheme.eligible)
    .sort((a, b) => b.matchScore - a.matchScore || a.title.localeCompare(b.title))
    .slice(0, limit);
}
