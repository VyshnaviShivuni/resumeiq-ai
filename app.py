import html
import os
import re
import textwrap

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader


# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ResumeIQ AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Global CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #050817;
    --bg-2: #081126;
    --panel: rgba(12, 20, 43, 0.86);
    --panel-2: rgba(10, 18, 38, 0.92);
    --border: rgba(148, 163, 184, 0.18);
    --border-strong: rgba(124, 58, 237, 0.42);
    --text: #F8FAFC;
    --muted: #A8B3C7;
    --muted-2: #64748B;
    --purple: #8B5CF6;
    --pink: #EC4899;
    --blue: #4F7CFF;
    --cyan: #38BDF8;
    --green: #22C55E;
    --yellow: #FACC15;
    --red: #EF4444;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    min-height: 100%;
    background:
        radial-gradient(circle at 18% 10%, rgba(79, 124, 255, 0.12), transparent 28%),
        radial-gradient(circle at 80% 0%, rgba(236, 72, 153, 0.13), transparent 24%),
        linear-gradient(135deg, #050817 0%, #071022 46%, #050817 100%) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer,
[data-testid="stDecoration"],
div[data-testid="stToolbar"],
.stDeployButton,
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

header, [data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
}

.block-container {
    max-width: 100% !important;
    padding: 0 28px 28px 46px !important;
}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[title="Open sidebar"],
button[aria-label="Open sidebar"],
button[aria-label="Expand sidebar"],
.custom-sidebar-open {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 16px !important;
    left: 14px !important;
    z-index: 999999 !important;
    width: 42px !important;
    height: 42px !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(148,163,184,0.28) !important;
    color: white !important;
    box-shadow: 0 12px 30px rgba(0,0,0,0.28) !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
button[title="Open sidebar"] svg,
button[aria-label="Open sidebar"] svg,
button[aria-label="Expand sidebar"] svg {
    color: white !important;
    stroke: white !important;
}

.custom-sidebar-open {
    text-decoration: none !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
}

#resumeiq-sidebar-open span {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 22px !important;
    height: 22px !important;
    border: 2px solid rgba(255,255,255,0.74) !important;
    border-radius: 6px !important;
    color: transparent !important;
    position: relative !important;
}

#resumeiq-sidebar-open span::before {
    content: "";
    position: absolute;
    left: 6px;
    top: 3px;
    bottom: 3px;
    width: 2px;
    background: rgba(255,255,255,0.74);
}

[data-testid="stSidebar"]:not([aria-expanded="false"]) ~ div .custom-sidebar-open {
    display: none !important;
}
/* Sidebar */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 80% 16%, rgba(124, 58, 237, 0.22), transparent 36%),
        linear-gradient(180deg, #050A1A 0%, #08132D 100%) !important;
    border-right: 1px solid rgba(148, 163, 184, 0.16) !important;
    min-width: 256px !important;
    max-width: 256px !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 24px 14px !important;
}

.sb-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 28px 0;
    padding: 0 12px;
}

.sb-brand-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    color: white;
    font-size: 17px;
    background: linear-gradient(135deg, #4F7CFF 0%, #9B5CFF 46%, #EC4899 100%);
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.35);
}

.sb-brand-title {
    color: #FFFFFF;
    font-size: 21px;
    line-height: 1;
    font-weight: 800;
    letter-spacing: 0;
}

.sb-footer {
    color: #A8B3C7;
    font-size: 13px;
    line-height: 1.9;
    text-align: center;
    padding-top: 36px;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    min-height: 52px !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    color: #CBD5E1 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 0 16px !important;
    margin: 2px 0 !important;
    text-align: left !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(124, 58, 237, 0.14) !important;
    border-color: rgba(124, 58, 237, 0.25) !important;
    color: white !important;
    transform: none !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(79,124,255,0.34), rgba(236,72,153,0.18)) !important;
    border-color: rgba(124, 58, 237, 0.35) !important;
    color: white !important;
}

.topbar {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 12px;
    min-height: 38px;
    margin-bottom: 0;
}

.user-chip {
    min-width: 156px;
    height: 38px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 4px 12px 4px 5px;
    background: rgba(5, 8, 23, 0.48);
    border: 1px solid rgba(148, 163, 184, 0.24);
    color: white;
    font-weight: 700;
    font-size: 13px;
}

.avatar {
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 999px;
    background: linear-gradient(135deg, #7C3AED, #A855F7);
    color: white;
}

.hero-title {
    margin: 0;
    font-size: 35px;
    line-height: 1.12;
    font-weight: 900;
    letter-spacing: 0;
    background: linear-gradient(90deg, #FF7A7A 0%, #EC49F2 45%, #6B7CFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    width: min(520px, 100%);
    color: #E2E8F0;
    font-size: 15px;
    line-height: 1.65;
    margin: 8px 0 16px;
}

.glass-card {
    background:
        linear-gradient(180deg, rgba(14, 24, 52, 0.94), rgba(8, 15, 34, 0.90));
    border: 1px solid var(--border);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 18px 45px rgba(0,0,0,0.15);
    border-radius: 8px;
}

.input-card {
    padding: 14px 16px 10px;
    min-height: 0;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    border-bottom-color: rgba(148, 163, 184, 0.08);
}

.section-heading {
    display: flex;
    align-items: center;
    gap: 11px;
    color: white;
    font-weight: 800;
    font-size: 15px;
    margin-bottom: 14px;
}

.num-dot {
    width: 25px;
    height: 25px;
    border-radius: 999px;
    display: inline-grid;
    place-items: center;
    flex: 0 0 auto;
    background: linear-gradient(135deg, #6A5CFF, #A855F7);
    color: white;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 10px 24px rgba(124, 58, 237, 0.32);
}

[data-testid="stFileUploader"] {
    background: rgba(8, 15, 34, 0.58) !important;
    border: 1px dashed rgba(148, 163, 184, 0.32) !important;
    border-radius: 8px !important;
    padding: 22px 14px !important;
    min-height: 88px;
    margin-top: 0 !important;
}

[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: 0 !important;
    padding: 0 !important;
}

[data-testid="stFileUploader"] button {
    background: rgba(124, 58, 237, 0.18) !important;
    border: 1px solid rgba(124, 58, 237, 0.35) !important;
    color: white !important;
    border-radius: 8px !important;
    margin-top: 0 !important;
}

[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span {
    color: #C8D2E5 !important;
}

.file-pill {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 10px;
    padding: 11px 12px;
    min-height: 58px;
    border-radius: 8px;
    background: rgba(7, 14, 31, 0.76);
    border: 1px solid rgba(148, 163, 184, 0.18);
}

.pdf-icon {
    width: 32px;
    height: 32px;
    border-radius: 7px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #F97373, #DC2626);
    color: white;
    font-size: 16px;
}

.file-name {
    color: white;
    font-size: 13px;
    font-weight: 700;
}

.file-size {
    color: #A8B3C7;
    font-size: 11px;
    margin-top: 2px;
}

.check-mark {
    margin-left: auto;
    color: #22C55E;
    font-size: 18px;
}

textarea {
    min-height: 119px !important;
    color: #E2E8F0 !important;
    font-size: 14px !important;
    background: rgba(8, 15, 34, 0.75) !important;
    border: 1px solid rgba(148, 163, 184, 0.22) !important;
    border-radius: 8px !important;
    margin-top: 0 !important;
}

textarea::placeholder { color: #94A3B8 !important; }
textarea:focus {
    border-color: rgba(124, 58, 237, 0.58) !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.16) !important;
}

.char-count {
    color: #C8D2E5;
    text-align: right;
    font-size: 11px;
    margin-top: -29px;
    padding-right: 12px;
    position: relative;
    z-index: 5;
    pointer-events: none;
}

.tip-line {
    color: #A8B3C7;
    font-size: 12px;
    margin-top: 16px;
}

.tip-line span { color: #FACC15; }

.analyze-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 234px;
    padding-top: 36px;
}

.analyze-card {
    width: 100%;
    min-height: 116px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    text-align: center;
    background: linear-gradient(135deg, #4F63FF 0%, #8B5CF6 44%, #DB1AB8 100%);
    box-shadow: 0 18px 36px rgba(124, 58, 237, 0.25);
}

.analyze-symbol {
    color: white;
    font-size: 26px;
    line-height: 1;
    margin-bottom: 10px;
}

.analyze-label {
    color: white;
    font-size: 17px;
    font-weight: 800;
}

.secure-copy {
    color: #A8B3C7;
    text-align: center;
    font-size: 12px;
    line-height: 1.35;
    margin-top: 14px;
}

div.main-action .stButton > button {
    height: 46px !important;
    margin-top: 12px !important;
    border-radius: 8px !important;
    border: 0 !important;
    color: white !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #5B6DFF 0%, #8B5CF6 45%, #EC4899 100%) !important;
    box-shadow: 0 16px 32px rgba(124, 58, 237, 0.28);
}

div.main-action .stButton > button:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
}

div.main-action .stButton > button:disabled {
    opacity: 0.45 !important;
    filter: grayscale(0.1);
    transform: none !important;
}

.metric-card {
    padding: 18px 20px 20px;
    min-height: 290px;
    height: 290px;
    overflow: visible;

    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.metric-title {
    display: flex;
    align-items: center;
    gap: 10px;
    color: white;
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 12px;
}

.metric-title .blue-text { color: #6C7CFF; }

.icon-circle {
    width: 25px;
    height: 25px;
    border-radius: 999px;
    display: inline-grid;
    place-items: center;
    font-size: 15px;
    background: rgba(79, 124, 255, 0.10);
}

.match-status {
    text-align: center;
    color: #4ADE80;
    font-weight: 800;
    font-size: 13px;
    margin-top: 4px;
}

.card-copy {
    color: #E2E8F0;
    font-size: 12px;
    line-height: 1.55;
    text-align: center;
}

.selection-value {
    color: #4ADE80;
    font-size: 23px;
    font-weight: 900;
    margin: 28px 0 14px;
}

.seg-progress {
    display: grid;
    grid-template-columns: repeat(9, 1fr);
    gap: 3px;
    margin-bottom: 17px;
}

.seg {
    height: 10px;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.16);
}

.seg.yellow { background: #FACC15; }
.seg.green { background: #4ADE80; }
.seg.dim-green { background: rgba(74, 222, 128, 0.38); }

.ranking-value {
    color: #9B5CFF;
    font-size: 26px;
    line-height: 1;
    font-weight: 900;
    margin: 25px 0 14px;
}

.analysis-card {
    padding: 17px 16px;
    height: 236px;
    overflow: hidden;
}

.analysis-body {
    height: 176px;
    overflow-y: auto;
    padding-right: 2px;
}

.css-donut {
    --value: 75;
    --color: #EC4899;

    width: 148px !important;
    height: 148px !important;

    min-width: 148px;
    min-height: 148px;

    aspect-ratio: 1 / 1;

    margin: 4px auto 0;
    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    flex-shrink: 0;

    background:
        radial-gradient(circle, #071126 0 52%, transparent 53%),
        conic-gradient(var(--color) calc(var(--value) * 1%), rgba(148,163,184,0.16) 0);
}

.css-donut-inner {
    width: 108px;
    height: 108px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: #071126;
    box-shadow: inset 0 0 24px rgba(0,0,0,0.22);
}

.css-donut-value {
    color: white;
    font-size: 32px;
    line-height: 1;
    font-weight: 900;
}

.css-donut-sub {
    color: #CBD5E1;
    font-size: 15px;
    font-weight: 700;
    margin-top: 5px;
}

.sparkline {
    width: 100%;
    height: 82px;
    margin-top: 7px;
}

.analysis-title {
    display: flex;
    align-items: center;
    gap: 9px;
    color: white;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 16px;
}

.tag {
    display: inline-block;
    color: white;
    font-size: 12px;
    line-height: 1.1;
    padding: 6px 8px;
    margin: 0 5px 7px 0;
    border-radius: 5px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    background: rgba(148, 163, 184, 0.12);
}

.tag.green {
    color: #E9FFF2;
    background: rgba(34, 197, 94, 0.14);
    border-color: rgba(34, 197, 94, 0.28);
}

.tag.yellow {
    color: #FFF7C2;
    background: rgba(250, 204, 21, 0.15);
    border-color: rgba(250, 204, 21, 0.34);
}

.tag.purple {
    color: #F5ECFF;
    background: rgba(124, 58, 237, 0.28);
    border-color: rgba(168, 85, 247, 0.46);
}

.bullet {
    display: flex;
    gap: 9px;
    color: #E2E8F0;
    font-size: 12px;
    line-height: 1.45;
    margin-bottom: 10px;
}

.bullet::before {
    content: "•";
    color: #C4B5FD;
    flex: 0 0 auto;
}

.empty-state {
    color: #718096;
    font-size: 12px;
    font-style: italic;
    margin-top: 2px;
}

.pro-tip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 15px 16px;
    margin-top: 10px;
    border-radius: 8px;
    background:
        radial-gradient(circle at 72% 40%, rgba(255,255,255,0.20), transparent 2%),
        linear-gradient(90deg, rgba(79, 75, 255, 0.95), rgba(122, 36, 212, 0.92), rgba(86, 20, 150, 0.95));
    border: 1px solid rgba(168, 85, 247, 0.55);
    box-shadow: 0 18px 50px rgba(124, 58, 237, 0.18);
}

.pro-left {
    display: flex;
    align-items: center;
    gap: 13px;
}

.gem {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background: rgba(255,255,255,0.13);
    color: white;
    font-size: 18px;
}

.pro-title {
    color: white;
    font-size: 15px;
    font-weight: 900;
}

.pro-text {
    color: white;
    font-size: 12px;
    margin-top: 3px;
}

.dl-static {
    color: white;
    font-size: 12px;
    font-weight: 800;
    padding: 9px 13px;
    border-radius: 7px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.22);
}

div.download-wrap .stDownloadButton > button {
    min-height: 36px !important;
    border-radius: 7px !important;
    color: white !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.24) !important;
}

.placeholder {
    text-align: center;
    padding: 72px 20px 40px;
}

.placeholder-icon {
    font-size: 48px;
    margin-bottom: 12px;
}

.placeholder-title {
    color: white;
    font-size: 18px;
    font-weight: 900;
    margin-bottom: 7px;
}

.placeholder-copy {
    color: #94A3B8;
    font-size: 14px;
}

.content-card {
    padding: 28px;
}

.content-card h3 {
    color: #A78BFA;
    margin: 0 0 10px 0;
}

.content-card p,
.content-card li {
    color: #CBD5E1;
    font-size: 14px;
    line-height: 1.9;
}

.js-plotly-plot .plotly .main-svg,
.stPlotlyChart {
    background: transparent !important;
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #050817; }
::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.46);
    border-radius: 999px;
}

@media (max-width: 1100px) {
    [data-testid="stSidebar"] {
        min-width: 220px !important;
        max-width: 220px !important;
    }
    .block-container { padding: 14px 18px 24px !important; }
    .hero-title { font-size: 30px; }
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Environment and client
# -----------------------------------------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
for key, default in {
    "page": "Dashboard",
    "analysis_done": False,
    "results": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.page in {"Pricing", "Settings", "Analysis History", "Saved Reports"}:
    st.session_state.page = "Dashboard"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
SECTION_KEYS = [
    "Strong Matches",
    "Missing Keywords",
    "Weak Areas",
    "Top Improvements",
    "Keywords To Add",
]


def safe(value) -> str:
    return html.escape(str(value or ""), quote=True)


def parse_sections(text: str) -> dict:
    content = {k: [] for k in SECTION_KEYS}
    cur = None

    for raw in text.splitlines():
        line = raw.strip()
        found = False

        for section in SECTION_KEYS:
            if re.match(rf"^{re.escape(section)}\s*:?\s*$", line, re.IGNORECASE):
                cur = section
                found = True
                break

        if found:
            continue

        if cur and re.match(r"^(?:[-*]|\u2022)\s+", line):
            item = re.sub(r"^(?:[-*]|\u2022)\s+", "", line).strip()
            if item:
                content[cur].append(item)

    return content


def robust_parse_sections(text: str, job_description: str = "") -> dict:
    content = {k: [] for k in SECTION_KEYS}
    cur = None

    for raw in (text or "").splitlines():
        line = raw.strip().strip("`")
        line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
        line = re.sub(r"^\s*\d+[\).]\s*", "", line)
        line = line.strip("*_ ")
        found = False

        for section in SECTION_KEYS:
            header_match = re.match(rf"^{re.escape(section)}\s*:?\s*(.*)$", line, re.IGNORECASE)
            if header_match:
                cur = section
                found = True
                inline_items = header_match.group(1).strip()
                if inline_items:
                    for item in re.split(r"\s*[,;]\s*", inline_items):
                        item = re.sub(r"^(?:[-*]|\u2022)\s*", "", item).strip()
                        if item:
                            content[cur].append(item)
                break

        if found:
            continue

        if cur and re.match(r"^(?:[-*]|\u2022)\s+", line):
            item = re.sub(r"^(?:[-*]|\u2022)\s+", "", line).strip()
            item = re.sub(r"^\*\*(.*?)\*\*$", r"\1", item).strip()
            if item:
                content[cur].append(item)

    for idx, section in enumerate(SECTION_KEYS):
        if content[section]:
            continue

        next_headers = SECTION_KEYS[idx + 1 :]
        stop_pattern = "|".join(re.escape(header) for header in next_headers)
        if stop_pattern:
            pattern = rf"{re.escape(section)}\s*:?\s*(.*?)(?=\n\s*(?:{stop_pattern})\s*:|\Z)"
        else:
            pattern = rf"{re.escape(section)}\s*:?\s*(.*)\Z"

        match = re.search(pattern, text or "", re.IGNORECASE | re.DOTALL)
        if not match:
            continue

        candidates = []
        for line in match.group(1).splitlines():
            item = re.sub(r"^\s*(?:(?:[-*]|\u2022)|\d+[\).])\s*", "", line).strip()
            item = item.strip("*_ ")
            if item and not re.match(r"^(Match Score|ATS Score|Top Ranking|Selection Chance)\s*:", item, re.I):
                candidates.append(item)
        content[section] = candidates[:8]

    if not content["Keywords To Add"] and job_description:
        ignored = {
            "and", "the", "for", "with", "you", "our", "are", "this", "that", "will",
            "from", "have", "your", "job", "role", "experience", "skills", "work",
            "team", "using", "candidate", "requirements", "responsibilities",
        }
        seen = []
        for word in re.findall(r"\b[A-Za-z][A-Za-z0-9+#.\-]{2,}\b", job_description):
            clean = word.strip(".,:;()[]{}")
            existing = {item.lower() for item in seen}
            if clean.lower() not in ignored and clean.lower() not in existing:
                seen.append(clean)
            if len(seen) >= 6:
                break
        content["Keywords To Add"] = seen

    return content


def get_int(pattern: str, text: str, default: int = 0) -> int:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return default
    return max(0, min(100, int(match.group(1))))


def get_str(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else default


def donut(value: int, color: str, center: str, sub: str = "", height: int = 168):
    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            values=[value, 100 - value],
            hole=0.74,
            showlegend=False,
            marker=dict(colors=[color, "rgba(148,163,184,0.14)"], line=dict(width=0)),
            hoverinfo="skip",
            textinfo="none",
            sort=False,
            direction="clockwise",
        )
    )
    fig.add_annotation(
        text=f"<b>{center}</b>",
        x=0.5,
        y=0.52 if not sub else 0.57,
        showarrow=False,
        font=dict(size=34 if "%" in center else 32, color="white", family="Inter"),
    )
    if sub:
        fig.add_annotation(
            text=sub,
            x=0.5,
            y=0.36,
            showarrow=False,
            font=dict(size=16, color="#CBD5E1", family="Inter"),
        )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
    )
    return fig


def ranking_sparkline():
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(15)),
            y=[2.0, 2.4, 1.9, 2.5, 2.45, 2.85, 1.65, 2.85, 2.45, 4.15, 2.0, 1.9, 2.2, 2.1, 2.3],
            mode="lines",
            fill="tozeroy",
            line=dict(color="#9B5CFF", width=2),
            fillcolor="rgba(155, 92, 255, 0.14)",
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=95,
    )
    return fig


def render_tags(items, color_class):
    if not items:
        st.markdown('<div class="empty-state">No data extracted</div>', unsafe_allow_html=True)
        return

    markup = "".join(
        f'<span class="tag {color_class}">{safe(item)}</span>'
        for item in items[:8]
    )
    st.markdown(markup, unsafe_allow_html=True)


def render_bullets(items):
    if not items:
        st.markdown('<div class="empty-state">No data extracted</div>', unsafe_allow_html=True)
        return

    markup = "".join(f'<div class="bullet">{safe(item)}</div>' for item in items[:5])
    st.markdown(markup, unsafe_allow_html=True)


def tags_markup(items, color_class):
    if not items:
        return '<div class="empty-state">No data extracted</div>'
    return "".join(f'<span class="tag {color_class}">{safe(item)}</span>' for item in items[:8])


def bullets_markup(items):
    if not items:
        return '<div class="empty-state">No data extracted</div>'
    return "".join(f'<div class="bullet">{safe(item)}</div>' for item in items[:5])


def html_clean(markup: str) -> str:
    return "".join(line.strip() for line in textwrap.dedent(markup).splitlines()).strip()


def donut_markup(value: int, color: str, label: str, sub: str = "") -> str:
    value = max(0, min(100, int(value or 0)))
    sub_html = f'<div class="css-donut-sub">{safe(sub)}</div>' if sub else ""
    return html_clean(f"""
    <div class="css-donut" style="--value:{value};--color:{color};">
        <div class="css-donut-inner">
            <div>
                <div class="css-donut-value">{safe(label)}</div>
                {sub_html}
            </div>
        </div>
    </div>
    """)


def sparkline_markup() -> str:
    return html_clean("""
    <svg class="sparkline" viewBox="0 0 320 90" preserveAspectRatio="none" aria-hidden="true">
        <defs>
            <linearGradient id="sparkFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="#9B5CFF" stop-opacity="0.42"/>
                <stop offset="100%" stop-color="#9B5CFF" stop-opacity="0.05"/>
            </linearGradient>
        </defs>
        <path d="M0,62 L24,54 L48,64 L72,52 L96,54 L120,44 L144,66 L168,46 L192,54 L216,20 L240,62 L264,64 L288,58 L320,60 L320,90 L0,90 Z" fill="url(#sparkFill)"/>
        <path d="M0,62 L24,54 L48,64 L72,52 L96,54 L120,44 L144,66 L168,46 L192,54 L216,20 L240,62 L264,64 L288,58 L320,60" fill="none" stroke="#9B5CFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """)


def build_prompt(job_description: str, resume_text: str) -> str:
    return f"""
You are an expert ATS resume evaluator and AI recruiter.

IMPORTANT RULES:
- Match Score and ATS Score MUST be different numbers.
- Match Score = keyword/skill alignment with JD (0-100).
- ATS Score = formatting, readability, keyword density (0-100).
- Top Ranking = realistic Top X% (example: Top 28%).
- Selection Chance = one of exactly: Low | Medium | Medium - High | High
- Keep bullet items short enough for compact dashboard cards.

VERY IMPORTANT:

If the resume and JD belong to different career paths,
reduce the Match Score significantly even if keywords overlap.

Examples:
- AI Engineer vs AI Content Creator → moderate or low match
- Backend Engineer vs UI Designer → low match
- ML Engineer vs Marketing Specialist → low match

Do not assume keyword overlap means role compatibility.

Transferable skills should increase score slightly,
but should NOT dominate the final evaluation.

Scoring Guidelines:
- 80-100 = Directly relevant experience and responsibilities
- 60-79 = Partial alignment with transferable experience
- 40-59 = Some overlapping skills but different core role
- 0-39 = Mostly unrelated role/domain

OUTPUT FORMAT - copy these headers EXACTLY with a colon at the end of each section header:

Match Score: [number]%
ATS Score: [number]%
Top Ranking: Top [number]%
Selection Chance: [Low|Medium|Medium - High|High]

Strong Matches:
- item
- item

Missing Keywords:
- item
- item

Weak Areas:
- item
- item

Top Improvements:
- item
- item

Keywords To Add:
- item
- item

Job Description:
{job_description}

Resume:
{resume_text}
"""


def extract_resume_text(uploaded_pdf) -> str:
    pdf_reader = PdfReader(uploaded_pdf)
    return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)


def make_report(results: dict) -> str:
    if not results:
        return ""

    lines = [
        "ResumeIQ AI Analysis Report",
        "",
        f"Match Score: {results.get('match', 0)}%",
        f"ATS Score: {results.get('ats', 0)}/100",
        f"Top Ranking: Top {results.get('ranking', 0)}%",
        f"Selection Chance: {results.get('selection', 'Medium')}",
        "",
    ]

    content = results.get("content", {})
    for section in SECTION_KEYS:
        lines.append(section)
        for item in content.get(section, []):
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["Raw AI Output", results.get("raw", "")])
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sb-brand">
            <div class="sb-brand-icon">⌂</div>
            <div class="sb-brand-title">ResumeIQ AI 🚀</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_pages = [
        ("⌂", "Dashboard"),
        ("▥", "ATS Guide"),
        ("☼", "Resume Tips"),
    ]

    for icon, label in nav_pages:
        button_type = "primary" if st.session_state.page == label else "secondary"
        if st.button(f"{icon}   {label}", key=f"nav_{label}", use_container_width=True, type=button_type):
            st.session_state.page = label
            st.rerun()

    st.markdown(
        """
        <div class="sb-footer">
            © 2025 ResumeIQ AI<br>
            Made with ❤️ for job seekers
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Main shell and topbar
# -----------------------------------------------------------------------------
page_titles = {
    "Dashboard": (
        "AI Resume Analyzer",
        "Get AI-powered insights to optimize your resume and increase your chances of landing your dream job.",
    ),
    "ATS Guide": ("ATS Guide", "Learn how Applicant Tracking Systems work."),
    "Resume Tips": ("Resume Tips", "Expert tips to make your resume stand out."),
}

pg_title, pg_subtitle = page_titles.get(st.session_state.page, ("ResumeIQ AI", ""))

components.html(
    """
    <script>
    (function () {
        const doc = window.parent.document;
        const styleId = "resumeiq-sidebar-force-style";

        if (!doc.getElementById(styleId)) {
            const style = doc.createElement("style");
            style.id = styleId;
            style.textContent = `
                body.resumeiq-sidebar-hidden [data-testid="stSidebar"] {
                    display: block !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    transform: translateX(-110%) !important;
                    left: -280px !important;
                    width: 0 !important;
                    min-width: 0 !important;
                    max-width: 0 !important;
                    pointer-events: none !important;
                    overflow: hidden !important;
                }
                body.resumeiq-sidebar-hidden #resumeiq-sidebar-open {
                    display: flex !important;
                }
                body.resumeiq-sidebar-hidden #resumeiq-sidebar-close {
                    display: none !important;
                }
                body.resumeiq-sidebar-forced [data-testid="stSidebar"] {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    transform: translateX(0) !important;
                    left: 0 !important;
                    margin-left: 0 !important;
                    width: 256px !important;
                    min-width: 256px !important;
                    max-width: 256px !important;
                    z-index: 2147483646 !important;
                }
                body:not(.resumeiq-sidebar-forced) [data-testid="stSidebar"][aria-expanded="false"] {
                    transform: translateX(-100%) !important;
                }
                body.resumeiq-sidebar-forced #resumeiq-sidebar-open {
                    display: none !important;
                }
                body.resumeiq-sidebar-forced #resumeiq-sidebar-close {
                    display: flex !important;
                }
                body.resumeiq-sidebar-forced [data-testid="stSidebar"] button[aria-label*="sidebar" i],
                body.resumeiq-sidebar-forced [data-testid="stSidebar"] button[title*="sidebar" i] {
                    display: none !important;
                }
            `;
            doc.head.appendChild(style);
        }

        function findOpenButton() {
            const buttons = Array.from(doc.querySelectorAll("button"));
            return buttons.find((btn) => {
                const label = (btn.getAttribute("aria-label") || btn.title || "").toLowerCase();
                return btn.id !== "resumeiq-sidebar-open" && (
                    label.includes("open sidebar") ||
                    label.includes("expand sidebar") ||
                    label.includes("show sidebar") ||
                    label.includes("sidebar")
                );
            });
        }

        function sidebarIsCollapsed() {
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return true;
            if (doc.body.classList.contains("resumeiq-sidebar-hidden")) return true;
            const rect = sidebar.getBoundingClientRect();
            const expanded = sidebar.getAttribute("aria-expanded");
            return !doc.body.classList.contains("resumeiq-sidebar-forced") &&
                (expanded === "false" || rect.width < 80 || rect.left < -40);
        }

        function clearSidebarInlineStyles() {
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                [
                    "display", "visibility", "opacity", "transform", "left",
                    "width", "min-width", "max-width", "pointer-events", "overflow"
                ].forEach((prop) => sidebar.style.removeProperty(prop));
            }
        }

        function hideSidebar() {
            doc.body.classList.remove("resumeiq-sidebar-forced");
            doc.body.classList.add("resumeiq-sidebar-hidden");
            clearSidebarInlineStyles();
            const btn = doc.getElementById("resumeiq-sidebar-open");
            if (btn) {
                setTimeout(() => {
                    btn.style.display = "flex";
                }, 80);
            }
        }

        function isCloseSidebarButton(el) {
            const btn = el && el.closest ? el.closest("button") : null;
            if (!btn || btn.id === "resumeiq-sidebar-open") return false;
            const label = (btn.getAttribute("aria-label") || btn.title || btn.textContent || "").toLowerCase();
            return label.includes("close sidebar") ||
                label.includes("collapse sidebar") ||
                label.includes("hide sidebar") ||
                label.trim() === "<<" ||
                label.includes("«");
        }

        function hideNativeCloseControls() {
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;

            Array.from(sidebar.querySelectorAll("button")).forEach((nativeBtn) => {
                if (nativeBtn.id === "resumeiq-sidebar-open" || nativeBtn.id === "resumeiq-sidebar-close") return;

                const label = (nativeBtn.getAttribute("aria-label") || nativeBtn.title || nativeBtn.textContent || "").toLowerCase().trim();
                const rect = nativeBtn.getBoundingClientRect();
                const looksLikeSidebarClose =
                    label.includes("close sidebar") ||
                    label.includes("collapse sidebar") ||
                    label.includes("hide sidebar") ||
                    label === "<<" ||
                    label.includes("«") ||
                    (rect.top < 120 && rect.right > 180 && rect.width <= 56 && rect.height <= 56);

                if (looksLikeSidebarClose) {
                    nativeBtn.style.setProperty("display", "none", "important");
                    nativeBtn.style.setProperty("visibility", "hidden", "important");
                    nativeBtn.style.setProperty("opacity", "0", "important");
                    nativeBtn.style.setProperty("pointer-events", "none", "important");
                }
            });
        }

        if (!window.resumeiqSidebarCloseBound) {
            window.resumeiqSidebarCloseBound = true;
            doc.addEventListener("pointerdown", function (event) {
                if (isCloseSidebarButton(event.target)) {
                    event.preventDefault();
                    event.stopPropagation();
                    hideSidebar();
                }
            }, true);
            doc.addEventListener("click", function (event) {
                if (isCloseSidebarButton(event.target)) {
                    event.preventDefault();
                    event.stopPropagation();
                    hideSidebar();
                }
            }, true);
        }

        function forceSidebarOpen() {
            doc.body.classList.remove("resumeiq-sidebar-hidden");
            doc.body.classList.add("resumeiq-sidebar-forced");
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                sidebar.style.setProperty("display", "block", "important");
                sidebar.style.setProperty("visibility", "visible", "important");
                sidebar.style.setProperty("opacity", "1", "important");
                sidebar.style.setProperty("transform", "translateX(0)", "important");
                sidebar.style.setProperty("left", "0", "important");
                sidebar.style.setProperty("width", "256px", "important");
                sidebar.style.setProperty("min-width", "256px", "important");
                sidebar.style.setProperty("max-width", "256px", "important");
                sidebar.style.setProperty("pointer-events", "auto", "important");
                sidebar.style.setProperty("overflow", "visible", "important");
            }
            setTimeout(() => {
                const nativeOpen = findOpenButton();
                if (nativeOpen) nativeOpen.click();
            }, 30);
        }

        function ensureButton() {
            hideNativeCloseControls();

            let btn = doc.getElementById("resumeiq-sidebar-open");
            if (!btn) {
                btn = doc.createElement("button");
                btn.id = "resumeiq-sidebar-open";
                btn.type = "button";
                btn.innerHTML = '<span style="font-size:22px;line-height:1;">▯</span>';
                btn.setAttribute("aria-label", "Open left navigation");
                btn.style.cssText = [
                    "position:fixed",
                    "top:16px",
                    "left:14px",
                    "z-index:2147483647",
                    "width:42px",
                    "height:42px",
                    "border-radius:12px",
                    "display:none",
                    "align-items:center",
                    "justify-content:center",
                    "background:rgba(255,255,255,0.12)",
                    "border:1px solid rgba(148,163,184,0.32)",
                    "color:white",
                    "font-size:18px",
                    "font-weight:900",
                    "cursor:pointer",
                    "box-shadow:0 12px 30px rgba(0,0,0,0.28)"
                ].join(";");
                btn.onclick = function () {
                    const nativeOpen = findOpenButton();
                    if (nativeOpen) {
                        nativeOpen.click();
                    }
                    const fallback = doc.querySelector('[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"]');
                    if (fallback) fallback.click();
                    forceSidebarOpen();
                };
                doc.body.appendChild(btn);
            }

            let closeBtn = doc.getElementById("resumeiq-sidebar-close");
            if (!closeBtn) {
                closeBtn = doc.createElement("button");
                closeBtn.id = "resumeiq-sidebar-close";
                closeBtn.type = "button";
                closeBtn.textContent = "<<";
                closeBtn.setAttribute("aria-label", "Close left navigation");
                closeBtn.style.cssText = [
                    "position:fixed",
                    "top:44px",
                    "left:204px",
                    "z-index:2147483647",
                    "width:34px",
                    "height:34px",
                    "border-radius:9px",
                    "display:flex",
                    "align-items:center",
                    "justify-content:center",
                    "background:rgba(124,58,237,0.28)",
                    "border:1px solid rgba(148,163,184,0.18)",
                    "color:#C4B5FD",
                    "font-size:17px",
                    "font-weight:900",
                    "cursor:pointer"
                ].join(";");
                closeBtn.onclick = function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    hideSidebar();
                };
                doc.body.appendChild(closeBtn);
            }

            btn.style.display = sidebarIsCollapsed() ? "flex" : "none";
            closeBtn.style.display = sidebarIsCollapsed() ? "none" : "flex";
            hideNativeCloseControls();
        }

        ensureButton();
        setInterval(ensureButton, 400);
    })();
    </script>
    """,
    height=0,
)

st.markdown(
    """
    <div class="topbar">
        <div class="user-chip">
            <div class="avatar">V</div>
            <div>Vyshnavi</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------------
if st.session_state.page == "Dashboard":
    st.markdown(html_clean(f"""
        <h1 class="hero-title">{safe(pg_title)}</h1>
        <div class="hero-subtitle">{safe(pg_subtitle)}</div>
        """), unsafe_allow_html=True)

    col_resume, col_jd, col_action = st.columns([1.25, 1.38, 0.70], gap="medium")

    with col_resume:
        st.markdown(
            """
            <div class="glass-card input-card">
                <div class="section-heading">
                    <span class="num-dot">1</span>
                    <span>Upload Your Resume</span>
                </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload PDF resume",
            type=["pdf"],
        )

        st.markdown("</div>", unsafe_allow_html=True)

        

    with col_jd:
        st.markdown(
            """
            <div class="glass-card input-card">
                <div class="section-heading">
                    <span class="num-dot">2</span>
                    <span>Paste Job Description</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        job_description = st.text_area(
            "Job Description",
            height=128,
            placeholder="Paste the job description here...",
            label_visibility="collapsed",
        )
        st.markdown(f'<div class="char-count">{len(job_description):,} characters</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tip-line"><span>💡</span> Tip: The more detailed the JD, the better the analysis</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_action:
        st.markdown(
            """
            <div class="analyze-panel">
                <div class="analyze-card">
                    <div>
                        <div class="analyze-symbol">✧</div>
                        <div class="analyze-label">Analyze Resume →</div>
                    </div>
                </div>
                <div class="secure-copy">🛡 Your data is secure and<br>never stored.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ready = bool(uploaded_file and job_description.strip())
        st.markdown('<div class="main-action">', unsafe_allow_html=True)
        analyze_clicked = st.button(
            "🚀 Analyze Resume",
            disabled=not ready,
            use_container_width=True,
            key="analyze_btn",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if not ready:
            hint = "Upload a PDF resume" if not uploaded_file else "Paste a job description"
            st.markdown(
                f'<div style="color:#64748B;text-align:center;font-size:11px;margin-top:6px;">{hint} to continue</div>',
                unsafe_allow_html=True,
            )

    if analyze_clicked and ready:
        if not client:
            st.error("GROQ_API_KEY is missing. Add it to your .env file before running analysis.")
        else:
            try:
                resume_text = extract_resume_text(uploaded_file)
                if not resume_text.strip():
                    st.error("I could not extract text from this PDF. Try a text-based PDF resume.")
                else:
                    with st.spinner("AI is analyzing your resume..."):
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": build_prompt(job_description, resume_text)}],
                            temperature=0.2,
                        )
                        ai_text = response.choices[0].message.content

                    st.session_state.results = {
                        "match": get_int(r"Match Score:\s*(\d+)%", ai_text, 0),
                        "ats": get_int(r"ATS Score:\s*(\d+)%", ai_text, 0),
                        "ranking": get_int(r"Top Ranking:\s*Top\s*(\d+)%", ai_text, 25),
                        "selection": get_str(
                            r"Selection Chance:\s*(Low|Medium - High|Medium|High)",
                            ai_text,
                            "Medium",
                        ),
                        "content": robust_parse_sections(ai_text, job_description),
                        "raw": ai_text,
                    }
                    st.session_state.analysis_done = True
                    st.rerun()
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

    if st.session_state.analysis_done and st.session_state.results:
        R = st.session_state.results
        match_val = R["match"]
        ats_val = R["ats"]
        ranking_val = R["ranking"]
        selection_val = R["selection"]
        content = R["content"]
        if R.get("raw") and not any(content.get(section) for section in SECTION_KEYS):
            content = robust_parse_sections(R["raw"])
            st.session_state.results["content"] = content

        if match_val >= 75:
            match_label = "Good Match"
            match_color = "#EC4899"
            match_desc = "Great! You have a strong match with this job role."
        elif match_val >= 50:
            match_label = "Fair Match"
            match_color = "#FACC15"
            match_desc = "Your resume partially matches. Improve the missing areas."
        else:
            match_label = "Weak Match"
            match_color = "#EF4444"
            match_desc = "Consider tailoring your resume more to this role."

        selection_color = {
            "High": "#4ADE80",
            "Medium - High": "#4ADE80",
            "Medium": "#FACC15",
            "Low": "#EF4444",
        }.get(selection_val, "#FACC15")

        st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns([1.05, 1.20, 0.95, 1.25], gap="medium")

        with m1:
            st.markdown(html_clean(f"""
                <div class="glass-card metric-card">
                    <div class="metric-title">
                        <span class="icon-circle" style="color:#FF5E7E;">↗</span>
                        <span>Overall <span class="blue-text">Match Score</span></span>
                    </div>
                    {donut_markup(match_val, match_color, f"{match_val}%")}
                    <div class="match-status">{safe(match_label)}</div>
                    <div class="card-copy" style="margin-top:14px;">{safe(match_desc)}</div>
                </div>
                """), unsafe_allow_html=True)

        with m2:
            st.markdown(html_clean(f"""
                <div class="glass-card metric-card">
                    <div class="metric-title">
                        <span class="icon-circle" style="color:#38BDF8;">◎</span>
                        <span>Selection Chance</span>
                    </div>
                    <div class="selection-value" style="color:{selection_color};">{safe(selection_val)}</div>
                    <div class="seg-progress">
                        <span class="seg yellow"></span>
                        <span class="seg yellow"></span>
                        <span class="seg yellow"></span>
                        <span class="seg green"></span>
                        <span class="seg green"></span>
                        <span class="seg green"></span>
                        <span class="seg dim-green"></span>
                        <span class="seg"></span>
                        <span class="seg"></span>
                    </div>
                    <div style="color:#CBD5E1;font-size:13px;line-height:1.55;">
                        You have a good chance of getting selected. Optimize the weak areas to improve further.
                    </div>
                </div>
                """), unsafe_allow_html=True)

        with m3:
            st.markdown(html_clean(f"""
                <div class="glass-card metric-card">
                    <div class="metric-title">
                        <span class="icon-circle" style="color:#34D399;">♦</span>
                        <span>ATS Score</span>
                    </div>
                    {donut_markup(ats_val, "#34D399", f"{ats_val}", "/100")}
                    <div class="card-copy" style="margin-top:8px;">
                        {safe("Your resume is ATS-friendly and well-optimized." if ats_val >= 75 else "Improve formatting, keywords, and readability for ATS.")}
                    </div>
                </div>
                """), unsafe_allow_html=True)

        with m4:
            st.markdown(html_clean(f"""
                <div class="glass-card metric-card">
                    <div class="metric-title">
                        <span class="icon-circle" style="color:#F59E0B;">♕</span>
                        <span>Top Ranking</span>
                    </div>
                    <div class="ranking-value">Top {ranking_val}%</div>
                    <div style="color:#CBD5E1;font-size:13px;line-height:1.55;margin-bottom:4px;">
                        You rank higher than {100 - ranking_val}% of other applicants.
                    </div>
                    {sparkline_markup()}
                </div>
                """), unsafe_allow_html=True)

        st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
        a1, a2, a3, a4, a5 = st.columns(5, gap="small")

        with a1:
            st.markdown(html_clean(f'''
                <div class="glass-card analysis-card">
                    <div class="analysis-title"><span style="color:#22C55E;">◎</span> Strong Matches</div>
                    <div class="analysis-body">{tags_markup(content.get("Strong Matches", []), "green")}</div>
                </div>
                '''), unsafe_allow_html=True)

        with a2:
            st.markdown(html_clean(f'''
                <div class="glass-card analysis-card">
                    <div class="analysis-title"><span style="color:#FACC15;">ⓘ</span> Missing Keywords</div>
                    <div class="analysis-body">{tags_markup(content.get("Missing Keywords", []), "yellow")}</div>
                </div>
                '''), unsafe_allow_html=True)

        with a3:
            st.markdown(html_clean(f'''
                <div class="glass-card analysis-card">
                    <div class="analysis-title"><span style="color:#EF4444;">△</span> Weak Areas</div>
                    <div class="analysis-body">{bullets_markup(content.get("Weak Areas", []))}</div>
                </div>
                '''), unsafe_allow_html=True)

        with a4:
            st.markdown(html_clean(f'''
                <div class="glass-card analysis-card">
                    <div class="analysis-title"><span style="color:#38BDF8;">↗</span> Top Improvements</div>
                    <div class="analysis-body">{bullets_markup(content.get("Top Improvements", []))}</div>
                </div>
                '''), unsafe_allow_html=True)

        with a5:
            st.markdown(html_clean(f'''
                <div class="glass-card analysis-card">
                    <div class="analysis-title"><span style="color:#A855F7;">◇</span> Keywords to Add</div>
                    <div class="analysis-body">{tags_markup(content.get("Keywords To Add", []), "purple")}</div>
                </div>
                '''), unsafe_allow_html=True)

        st.markdown(
            """
            <div class="pro-tip">
                <div class="pro-left">
                    <div class="gem">◇</div>
                    <div>
                        <div class="pro-title">Pro Tip</div>
                        <div class="pro-text">Optimize your resume with these insights and increase your chances of getting hired!</div>
                    </div>
                </div>
                <div class="dl-static">Download the full report below</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="download-wrap">', unsafe_allow_html=True)
        st.download_button(
            "⇩ Download Full Report",
            data=make_report(R),
            file_name="resumeiq-analysis-report.txt",
            mime="text/plain",
            use_container_width=False,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown(
            """
            <div class="placeholder">
                <div class="placeholder-icon">📄</div>
                <div class="placeholder-title">Ready to analyze your resume?</div>
                <div class="placeholder-copy">
                    Upload your PDF resume and paste a job description, then hit Analyze Resume.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# ATS Guide
# -----------------------------------------------------------------------------
elif st.session_state.page == "ATS Guide":
    st.markdown(f'<h1 class="hero-title">{safe(pg_title)}</h1><div class="hero-subtitle">{safe(pg_subtitle)}</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card content-card">
            <h3>What is an ATS?</h3>
            <p>
                An Applicant Tracking System (ATS) is software employers use to screen resumes
                before a recruiter reviews them. ATS optimization helps your resume pass automated
                checks for structure, readability, and role-specific keywords.
            </p>
            <h3>Top ATS Optimization Tips</h3>
            <ul>
                <li>Use standard headings: Experience, Education, Skills, Summary.</li>
                <li>Mirror important keywords from the job description naturally.</li>
                <li>Avoid complex tables, text boxes, images, and heavy graphics.</li>
                <li>Use a clean single-column layout with consistent spacing.</li>
                <li>Quantify achievements with numbers wherever possible.</li>
                <li>Spell out acronyms at first use, such as Machine Learning (ML).</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Resume Tips
# -----------------------------------------------------------------------------
elif st.session_state.page == "Resume Tips":
    st.markdown(f'<h1 class="hero-title">{safe(pg_title)}</h1><div class="hero-subtitle">{safe(pg_subtitle)}</div>', unsafe_allow_html=True)

    tips = [
        ("🎯", "Tailor for every job", "Customize your resume by matching the job description's skills, tools, and role language."),
        ("📊", "Quantify achievements", "Use measurable outcomes like revenue, time saved, accuracy, cost reduction, or scale."),
        ("🔤", "Start with action verbs", "Lead with verbs like Built, Led, Optimized, Delivered, Reduced, Designed, and Automated."),
        ("📏", "Keep it concise", "Prioritize relevant experience and remove older details that do not support the target role."),
        ("🖋", "Keep formatting clean", "Use consistent spacing, clear headings, and ATS-friendly structure."),
        ("🔗", "Add relevant links", "Include LinkedIn, GitHub, portfolio, or case studies when they strengthen your application."),
        ("🧹", "Proofread carefully", "Small grammar issues can distract from strong experience and reduce recruiter confidence."),
        ("📧", "Use a professional email", "Choose a simple address based on your real name."),
    ]

    col1, col2 = st.columns(2, gap="medium")
    for idx, (icon, title, desc) in enumerate(tips):
        with (col1 if idx % 2 == 0 else col2):
            st.markdown(html_clean(f"""
                <div class="glass-card content-card" style="padding:18px;margin-bottom:14px;display:flex;gap:14px;">
                    <div style="font-size:26px;line-height:1;">{icon}</div>
                    <div>
                        <div style="color:white;font-size:15px;font-weight:900;margin-bottom:5px;">{safe(title)}</div>
                        <div style="color:#CBD5E1;font-size:13px;line-height:1.65;">{safe(desc)}</div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
