function firstValue(...values) {
  return values.find((value) => value !== undefined && value !== null && value !== "");
}

function textFrom(value) {
  if (!value) return "";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(textFrom).filter(Boolean).join("; ");
  if (typeof value === "object") {
    return firstValue(value.en, value.text, value.value, value.name, value.label, JSON.stringify(value));
  }
  return String(value);
}

function findSchemeArray(raw) {
  if (Array.isArray(raw)) return raw;
  if (!raw || typeof raw !== "object") return [];

  const candidates = [
    raw.data,
    raw.schemes,
    raw.results,
    raw.response,
    raw.data?.schemes,
    raw.data?.results,
    raw.payload?.schemes
  ];

  return candidates.find(Array.isArray) || [];
}

function schemeSourceUrl(scheme) {
  const title = textFrom(firstValue(scheme.scheme_name, scheme.schemeName, scheme.name, scheme.title)).toLowerCase();
  const category = textFrom(firstValue(scheme.category, scheme.schemeCategory, scheme.categoryName)).toLowerCase();
  const state = textFrom(firstValue(scheme.state, scheme.stateName, scheme.schemeState)).toLowerCase();

  if (title.includes("pmeg") || title.includes("employment generation")) return "https://www.msme.gov.in/";
  if (title.includes("mudra")) return "https://www.mudra.org.in/";
  if (title.includes("pradhan mantri kisan") || title.includes("pm kisan") || title.includes("kisan") || category.includes("agriculture")) return "https://pmkisan.gov.in/";
  if (title.includes("e-shram") || title.includes("shram") || category.includes("labour welfare")) return "https://eshram.gov.in/";
  if (title.includes("kaushal vikas") || category.includes("skill development") || title.includes("skill")) return "https://www.pmkvyofficial.org/";
  if (category.includes("scholarship") || title.includes("scholarship")) return "https://scholarships.gov.in/";
  if (title.includes("fasal bima")) return "https://pmfby.gov.in/";
  if (title.includes("shram yogi")) return "https://pmsym.gov.in/";
  if (title.includes("rythu bandhu") || (state.includes("telangana") && category.includes("agriculture"))) return "https://rythubandhu.telangana.gov.in/";

  return "";
}

export function mapScheme(scheme) {
  const name = firstValue(scheme.scheme_name, scheme.schemeName, scheme.name, scheme.title);
  const description = firstValue(scheme.description, scheme.schemeDescription, scheme.briefDescription, scheme.summary);
  const benefits = firstValue(scheme.benefits, scheme.benefit, scheme.benefitDetails);
  const eligibility = firstValue(scheme.eligibility, scheme.eligibilityCriteria, scheme.eligibility_details);
  const category = firstValue(scheme.category, scheme.schemeCategory, scheme.categoryName, scheme.nodalMinistryName);
  const level = firstValue(scheme.level, scheme.schemeLevel, scheme.schemeType);
  const sourceUrl = firstValue(scheme.source_url, scheme.sourceUrl, scheme.url, scheme.link) || schemeSourceUrl(scheme);

  return {
    id: firstValue(scheme.id, scheme.schemeId, scheme.slug, name),
    title: textFrom(name) || "Untitled scheme",
    description: textFrom(description),
    benefits: textFrom(benefits),
    eligibility: textFrom(eligibility),
    category: textFrom(category),
    level: textFrom(level),
    sourceUrl: sourceUrl,
    raw: scheme
  };
}

export function mapSchemes(raw) {
  return findSchemeArray(raw).map(mapScheme);
}

export function getCategories(schemes) {
  return [...new Set(schemes.map((scheme) => scheme.category).filter(Boolean))].sort();
}

export function filterSchemes(schemes, { search = "", category = "" } = {}) {
  const query = search.trim().toLowerCase();

  return schemes.filter((scheme) => {
    const matchesCategory = !category || scheme.category === category;
    const haystack = [scheme.title, scheme.description, scheme.benefits, scheme.eligibility, scheme.category]
      .join(" ")
      .toLowerCase();
    const matchesSearch = !query || haystack.includes(query);
    return matchesCategory && matchesSearch;
  });
}
