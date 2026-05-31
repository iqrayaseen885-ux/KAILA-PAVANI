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

export function mapScheme(scheme) {
  const name = firstValue(scheme.scheme_name, scheme.schemeName, scheme.name, scheme.title);
  const description = firstValue(scheme.description, scheme.schemeDescription, scheme.briefDescription, scheme.summary);
  const benefits = firstValue(scheme.benefits, scheme.benefit, scheme.benefitDetails);
  const eligibility = firstValue(scheme.eligibility, scheme.eligibilityCriteria, scheme.eligibility_details);
  const category = firstValue(scheme.category, scheme.schemeCategory, scheme.categoryName, scheme.nodalMinistryName);
  const level = firstValue(scheme.level, scheme.schemeLevel, scheme.schemeType);

  return {
    id: firstValue(scheme.id, scheme.schemeId, scheme.slug, name),
    title: textFrom(name) || "Untitled scheme",
    description: textFrom(description),
    benefits: textFrom(benefits),
    eligibility: textFrom(eligibility),
    category: textFrom(category),
    level: textFrom(level),
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
