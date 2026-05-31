import { fetchSchemes } from "./services/schemeApi.js";
import { mapSchemes, filterSchemes, getCategories } from "./services/schemeMapper.js";
import { recommendSchemes } from "./services/eligibilityEngine.js";

const form = document.querySelector("#profile-form");
const cardsEl = document.querySelector("#cards");
const statusEl = document.querySelector("#status");
const rawJsonEl = document.querySelector("#raw-json");
const searchEl = document.querySelector("#search");
const categoryFilterEl = document.querySelector("#category-filter");

let currentSchemes = [];
let recommendedSchemes = [];

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function readProfile() {
  return {
    age: Number(form.age.value),
    income: Number(form.income.value),
    gender: form.gender.value,
    state: form.state.value,
    occupation: form.occupation.value,
    category: form.category.value,
    student: form.student.checked
  };
}

function setStatus(message, variant = "info") {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", variant === "error");
}

function renderCategories(schemes) {
  const selected = categoryFilterEl.value;
  const categories = getCategories(schemes);
  categoryFilterEl.innerHTML = '<option value="">All categories</option>';

  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categoryFilterEl.append(option);
  });

  if (categories.includes(selected)) {
    categoryFilterEl.value = selected;
  }
}

function renderCards() {
  const search = searchEl.value;
  const category = categoryFilterEl.value;
  const visibleSchemes = filterSchemes(recommendedSchemes, { search, category });

  cardsEl.innerHTML = "";

  if (!visibleSchemes.length) {
    setStatus(currentSchemes.length ? "No schemes match the current search and filters." : "No schemes loaded yet.");
    return;
  }

  setStatus(`Showing ${visibleSchemes.length} matched scheme${visibleSchemes.length === 1 ? "" : "s"}.`);

  visibleSchemes.forEach((scheme) => {
    const card = document.createElement("article");
    card.className = "scheme-card";
    card.innerHTML = `
      <div class="meta-row">
        <span class="pill score">${scheme.matchScore}% match</span>
        <span class="pill">${escapeHtml(scheme.category || "Uncategorized")}</span>
        <span class="pill">${escapeHtml(scheme.level || "Scheme")}</span>
      </div>
      <h3>${escapeHtml(scheme.title)}</h3>
      <p>${escapeHtml(scheme.description || "Description unavailable from the API response.")}</p>
      <p><strong>Benefits:</strong> ${escapeHtml(scheme.benefits || "Benefit details unavailable from the API response.")}</p>
      <p><strong>Eligibility:</strong> ${escapeHtml(scheme.eligibility || "Eligibility details unavailable from the API response.")}</p>
      <p><strong>Why matched:</strong> ${escapeHtml(scheme.matchReason)}</p>
    `;
    cardsEl.append(card);
  });
}

async function loadSchemes(profile) {
  setStatus("Fetching live scheme data...");
  cardsEl.innerHTML = "";

  try {
    const raw = await fetchSchemes(profile.state);
    rawJsonEl.textContent = JSON.stringify(raw, null, 2);
    currentSchemes = mapSchemes(raw);
    recommendedSchemes = recommendSchemes(profile, currentSchemes);
    renderCategories(recommendedSchemes);
    renderCards();
  } catch (error) {
    currentSchemes = [];
    recommendedSchemes = [];
    rawJsonEl.textContent = error.stack || String(error);
    setStatus(`Could not fetch live myScheme data: ${error.message}`, "error");
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  loadSchemes(readProfile());
});

searchEl.addEventListener("input", renderCards);
categoryFilterEl.addEventListener("change", renderCards);
