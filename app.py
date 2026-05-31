import html
from typing import Any
import json
from urllib.parse import quote_plus

import streamlit as st

from services.eligibility_engine import recommend_schemes
from services.scheme_mapper import filter_schemes, map_schemes

st.set_page_config(
    page_title="GovScheme AI",
    page_icon="GS",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #f5f7fa; }
    .hero { padding: 1.2rem 0 0.35rem; }
    .hero h1 { margin: 0; color: #1d2430; font-size: 2.15rem; letter-spacing: 0; }
    .hero p { color: #5d6878; margin-top: 0.35rem; max-width: 760px; }
    .metric-strip { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem; margin: 1rem 0; }
    .metric-box, .scheme-card, .notice-box { background: #ffffff; border: 1px solid #d9e0ea; border-radius: 8px; padding: 1rem; }
    .metric-box span { color: #5d6878; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; }
    .metric-box strong { display: block; margin-top: 0.25rem; color: #1f7a63; font-size: 1.35rem; }
    .scheme-card { margin-bottom: 0.85rem; }
    .scheme-card h3 { margin: 0.35rem 0 0.45rem; color: #1d2430; font-size: 1.05rem; }
    .scheme-card p { color: #5d6878; line-height: 1.48; margin-bottom: 0.45rem; }
    .pill-row { display: flex; flex-wrap: wrap; gap: 0.45rem; }
    .pill { border: 1px solid #d9e0ea; border-radius: 999px; color: #5d6878; font-size: 0.78rem; font-weight: 700; padding: 0.18rem 0.55rem; }
    .score-pill { background: #155544; border-color: #155544; color: #ffffff; }
    .notice-box { border-left: 4px solid #1f7a63; color: #405063; }
    .recommend-box { background: #e4f5ec; border: 1px solid #bee5cf; border-radius: 8px; padding: 1rem; color: #0f5d3d; }
    .recommend-box h3 { margin: 0 0 0.5rem; color: #0f5d3d; font-size: 1rem; }
    .recommend-box p { margin: 0 0 0.75rem; line-height: 1.5; }
    .next-step { background: #ffffff; border: 1px solid #d9e0ea; border-radius: 8px; padding: 1rem; color: #405063; margin-top: 0.85rem; }
    @media (max-width: 780px) { .metric-strip { grid-template-columns: 1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe(value: Any) -> str:
    return html.escape(str(value or ""))


def load_local_sample_data() -> list[dict[str, Any]]:
    with open("data/schemes.json", "r", encoding="utf-8-sig") as file:
        return json.load(file)


def render_scheme_card(scheme: dict[str, Any]) -> None:
    source_url = scheme.get("source_url") or f"https://www.myscheme.gov.in/search?q={quote_plus(scheme.get('title', ''))}"

    st.markdown(
        f"""
        <div class="scheme-card">
            <div class="pill-row">
                <span class="pill score-pill">{safe(scheme['match_score'])}% match</span>
                <span class="pill">{safe(scheme['category'])}</span>
                <span class="pill">{safe(scheme['level'])}</span>
            </div>
            <h3>{safe(scheme['title'])}</h3>
            <p>{safe(scheme['description'] or 'Description unavailable from the API response.')}</p>
            <p><strong>Benefits:</strong> {safe(scheme['benefits'] or 'Benefit details unavailable from the API response.')}</p>
            <p><strong>Eligibility:</strong> {safe(scheme['eligibility'] or 'Eligibility details unavailable from the API response.')}</p>
            <p><strong>Reference:</strong> {safe(scheme.get('reference_text', 'Official myScheme portal and trusted government sources.'))}</p>
            <p><strong>Source:</strong> <a href="{safe(source_url)}" target="_blank">View official scheme details</a></p>
            <p><strong>Why matched:</strong> {safe(scheme['match_reason'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <h1>GovScheme AI</h1>
        <p>Find relevant government schemes based on your profile and compare recommendations with clear match scores.</p>
    </div>
    <div class="notice-box">
        <strong>Data source:</strong> Scheme details are drawn from the official myScheme portal and related government scheme sources. Users should verify all eligibility and benefit details against the official scheme website before applying.
        <br>
        <a href="https://www.myscheme.gov.in/" target="_blank">myscheme.gov.in</a>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("User Profile")
    age = st.number_input("Age", min_value=0, max_value=120, value=22, step=1, key="profile_age")
    gender = st.selectbox("Gender", ["Female", "Male", "Transgender", "Any"], key="profile_gender")
    state = st.selectbox("State", ["Telangana", "Andhra Pradesh", "Karnataka", "Maharashtra", "Tamil Nadu", "Delhi"], key="profile_state")
    income = st.number_input("Annual income", min_value=0, value=150000, step=1000, key="profile_income")
    occupation = st.selectbox("Occupation", ["Student", "Farmer", "Entrepreneur", "Worker", "Unemployed", "Other"], key="profile_occupation")
    category = st.selectbox("Social category", ["Any", "SC", "ST", "OBC", "Minority", "General"], key="profile_category")
    if occupation == "Student":
        student = st.checkbox("Student profile", value=True, key="profile_student")
    else:
        student = False
        st.caption("Student profile is off because occupation is not Student.")

    st.divider()
    find_clicked = st.button("Find your schemes", type="primary", use_container_width=True, key="find_schemes")

profile = {
    "age": age,
    "gender": gender,
    "state": state,
    "income": income,
    "occupation": occupation,
    "category": category,
    "student": student,
}

if "raw_json" not in st.session_state:
    st.session_state.raw_json = None
if "schemes" not in st.session_state:
    st.session_state.schemes = []
if "error" not in st.session_state:
    st.session_state.error = ""

if find_clicked:
    st.session_state.error = ""
    st.session_state.raw_json = load_local_sample_data()
    st.session_state.schemes = map_schemes(st.session_state.raw_json)

schemes = st.session_state.schemes
recommendations = recommend_schemes(profile, schemes) if schemes else []

st.markdown(
    f"""
    <div class="metric-strip">
        <div class="metric-box"><span>Available schemes</span><strong>{len(schemes)}</strong></div>
        <div class="metric-box"><span>Matching schemes</span><strong>{len(recommendations)}</strong></div>
        <div class="metric-box"><span>Selected state</span><strong>{safe(state)}</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.error:
    st.error(st.session_state.error)
    st.warning("Could not load scheme data. Please check the local data file.")
elif not schemes:
    st.info("Fill your profile and click Find your schemes.")

left, right = st.columns([0.66, 0.34], gap="large")

with left:
    st.subheader("Scheme Cards")
    search_query = st.text_input("Search schemes", placeholder="Scholarship, farmer, housing", key="scheme_search")
    categories = ["All categories"] + sorted({scheme["category"] for scheme in recommendations})
    selected_category = st.selectbox("Category filter", categories, key="scheme_category_filter")

    visible = filter_schemes(recommendations, search_query, selected_category)
    if visible:
        for scheme in visible:
            render_scheme_card(scheme)
    elif schemes:
        st.warning("No recommended schemes match the current search or category filter.")
