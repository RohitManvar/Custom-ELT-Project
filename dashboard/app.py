import streamlit as st
import streamlit.components.v1 as components
import psycopg2
import pandas as pd
import os
import base64
from PIL import Image

LOGO_PATH = "/app/logo/datastack logo.png"

def load_logo_b64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def load_logo_pil():
    if os.path.exists(LOGO_PATH):
        return Image.open(LOGO_PATH)
    return "⚡"

logo_b64  = load_logo_b64()
logo_src  = f"data:image/png;base64,{logo_b64}" if logo_b64 else None
logo_html = f'<img src="{logo_src}" style="height:36px;width:auto;margin-bottom:10px;display:block;" />' if logo_src else '<span style="font-size:28px;">⚡</span>'

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataStack — ELT Pipeline",
    page_icon=load_logo_pil(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Favicon (force via JS) ────────────────────────────────────────────────────
if logo_b64:
    st.markdown(f"""
    <script>
    (function() {{
        var src = "data:image/png;base64,{logo_b64}";
        function setFavicon() {{
            var links = document.querySelectorAll("link[rel*='icon']");
            links.forEach(function(l) {{ l.parentNode.removeChild(l); }});
            var link = document.createElement('link');
            link.type = 'image/png';
            link.rel = 'shortcut icon';
            link.href = src;
            document.head.appendChild(link);
        }}
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', setFavicon);
        }} else {{
            setFavicon();
        }}
        setTimeout(setFavicon, 500);
    }})();
    </script>
    """, unsafe_allow_html=True)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Prevent horizontal overflow */
html, body { overflow-x: hidden; max-width: 100vw; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 3rem;
    max-width: 100% !important;
    width: 100% !important;
    overflow-x: hidden;
    box-sizing: border-box;
}

/* Strip all default Streamlit spacing — use only our own margins */
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.element-container { margin: 0 !important; padding: 0 !important; }
.stMarkdown { margin: 0 !important; padding: 0 !important; }
[data-testid="stVerticalBlockBorderWrapper"] { margin: 0 !important; padding: 0 !important; }
iframe { display: block; margin: 0 !important; padding: 0 !important; max-width: 100%; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
    width: 100%;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-logo  { font-size: 13px; font-weight: 600; letter-spacing: 3px; color: #818cf8; text-transform: uppercase; margin-bottom: 10px; }
.hero-title { font-size: 38px; font-weight: 800; color: #f8fafc; margin: 0; line-height: 1.1; }
.hero-title span { color: #818cf8; }
.hero-sub   { font-size: 15px; color: #94a3b8; margin-top: 10px; }
.hero-pills { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
.pill {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 500;
}
.pill.green { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: #6ee7b7; }

/* ── Stats row ── */
.stats-row { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; width: 100%; box-sizing: border-box; }
.stat-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px 24px;
    flex: 1;
    min-width: 140px;
}
.stat-label { font-size: 11px; font-weight: 600; letter-spacing: 1.5px; color: #475569; text-transform: uppercase; margin-bottom: 8px; }
.stat-value { font-size: 30px; font-weight: 700; color: #f1f5f9; line-height: 1; }
.stat-value.purple { color: #818cf8; }
.stat-value.green  { color: #4ade80; }
.stat-value.blue   { color: #38bdf8; }
.stat-value.orange { color: #fb923c; }
.stat-sub { font-size: 11px; color: #475569; margin-top: 4px; }

/* ── Section title ── */
.section-title {
    font-size: 11px; font-weight: 700; letter-spacing: 2px;
    color: #475569; text-transform: uppercase;
    margin: 0 0 16px 0; padding-bottom: 10px;
    border-bottom: 1px solid #1e293b;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0f172a;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #1e293b;
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #64748b;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 16px;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] {
    background: #1e293b !important;
    color: #e2e8f0 !important;
}

/* ── Data table ── */
.stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #1e293b; }

/* ── Metric ── */
[data-testid="metric-container"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px;
}
[data-testid="metric-container"] label { color: #64748b !important; font-size: 11px !important; letter-spacing: 1px; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 24px !important; }

/* ── Alert boxes ── */
.info-box {
    background: rgba(56,189,248,0.08); border: 1px solid rgba(56,189,248,0.2);
    border-radius: 10px; padding: 14px 18px; color: #7dd3fc; font-size: 13px; margin: 10px 0;
}
.success-box {
    background: rgba(74,222,128,0.08); border: 1px solid rgba(74,222,128,0.2);
    border-radius: 10px; padding: 14px 18px; color: #86efac; font-size: 13px; margin: 10px 0;
}
.error-box {
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 10px; padding: 14px 18px; color: #fca5a5; font-size: 13px; margin: 10px 0;
}

/* ── dbt model row ── */
.model-row {
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
    background: #1e293b; border: 1px solid #334155;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 8px;
}
.model-name  { font-size: 14px; font-weight: 600; color: #e2e8f0; }
.model-desc  { font-size: 12px; color: #64748b; margin-top: 2px; }
.model-status { font-size: 12px; font-weight: 600; }

/* ── Button ── */
div.stButton > button {
    background: #1e293b; color: #94a3b8;
    border: 1px solid #334155; border-radius: 8px;
    font-size: 13px; padding: 6px 18px; transition: all 0.2s;
}
div.stButton > button:hover { background: #334155; color: #e2e8f0; border-color: #475569; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #1e293b !important; border-color: #334155 !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
}

/* ════════════════════════════════════════
   RESPONSIVE — Tablet  (≤ 900px)
   ════════════════════════════════════════ */
@media (max-width: 900px) {
    .block-container { padding: 1.5rem 1.5rem; }
    .hero { padding: 28px 24px; }
    .hero-title { font-size: 28px; }
    .hero-sub   { font-size: 13px; }
    .stat-card  { min-width: 120px; padding: 16px 18px; }
    .stat-value { font-size: 24px; }
    .stTabs [data-baseweb="tab"] { font-size: 12px; padding: 7px 12px; }
}

/* ════════════════════════════════════════
   RESPONSIVE — Mobile  (≤ 600px)
   ════════════════════════════════════════ */
@media (max-width: 600px) {
    .block-container { padding: 1rem; }
    .hero { padding: 20px 16px; border-radius: 12px; }
    .hero-logo  { font-size: 11px; }
    .hero-title { font-size: 22px; }
    .hero-sub   { font-size: 12px; }
    .hero-pills { gap: 6px; margin-top: 14px; }
    .pill       { font-size: 11px; padding: 3px 10px; }
    .stats-row  { gap: 10px; }
    .stat-card  { min-width: calc(50% - 10px); padding: 14px; }
    .stat-value { font-size: 22px; }
    .stat-label { font-size: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 11px; padding: 6px 8px; }
    .model-row  { flex-direction: column; align-items: flex-start; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 20px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── DB Config ─────────────────────────────────────────────────────────────────
SOURCE_CONFIG = {
    "host": os.environ.get("SOURCE_POSTGRES_HOST", "source_postgres"),
    "dbname": os.environ.get("SOURCE_POSTGRES_DB", "source_db"),
    "user": os.environ.get("SOURCE_POSTGRES_USER", "postgres"),
    "password": os.environ.get("SOURCE_POSTGRES_PASSWORD", "secret"),
    "port": int(os.environ.get("SOURCE_POSTGRES_PORT", 5432)), "connect_timeout": 3,
}
DEST_CONFIG = {
    "host": os.environ.get("DESTINATION_POSTGRES_HOST", "destination_postgres"),
    "dbname": os.environ.get("DESTINATION_POSTGRES_DB", "destination_db"),
    "user": os.environ.get("DESTINATION_POSTGRES_USER", "postgres"),
    "password": os.environ.get("DESTINATION_POSTGRES_PASSWORD", "secret"),
    "port": int(os.environ.get("DESTINATION_POSTGRES_PORT", 5432)), "connect_timeout": 3,
}

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def check_db(config_key):
    config = SOURCE_CONFIG if config_key == "source" else DEST_CONFIG
    try:
        conn = psycopg2.connect(**config); conn.close(); return True
    except Exception:
        return False

@st.cache_data(ttl=30)
def get_tables(config_key):
    config = SOURCE_CONFIG if config_key == "source" else DEST_CONFIG
    try:
        conn = psycopg2.connect(**config)
        cur  = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        tables = [r[0] for r in cur.fetchall()]
        rows = []
        for t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name=%s", (t,))
            cols = cur.fetchone()[0]
            rows.append({"Table": t, "Rows": cnt, "Columns": cols})
        conn.close()
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_table_data(config_key, table, limit=25):
    config = SOURCE_CONFIG if config_key == "source" else DEST_CONFIG
    try:
        conn = psycopg2.connect(**config)
        df = pd.read_sql(f"SELECT * FROM {table} LIMIT {limit}", conn)
        conn.close(); return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_dbt_models():
    models = ["films", "actors", "film_actors", "film_rating"]
    try:
        conn = psycopg2.connect(**DEST_CONFIG)
        cur  = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        existing = [r[0] for r in cur.fetchall()]
        conn.close()
        return {m: m in existing for m in models}
    except Exception:
        return {m: False for m in models}

# ── Data fetch ────────────────────────────────────────────────────────────────
src_ok    = check_db("source")
dest_ok   = check_db("dest")
src_tbl   = get_tables("source") if src_ok  else pd.DataFrame()
dst_tbl   = get_tables("dest")   if dest_ok else pd.DataFrame()
dbt_models = get_dbt_models()    if dest_ok else {}

elt_ok   = dest_ok and not dst_tbl.empty
dbt_ok   = dest_ok and bool(dbt_models) and all(dbt_models.values())
src_rows = int(src_tbl["Rows"].sum()) if not src_tbl.empty else 0
dst_rows = int(dst_tbl["Rows"].sum()) if not dst_tbl.empty else 0

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-logo">DataStack</div>
    <div class="hero-title">ELT <span>Pipeline</span> Monitor</div>
    <div class="hero-sub">Real-time tracking of your data pipeline — from raw source to transformed insights</div>
    <div class="hero-pills">
        <span class="pill">Python</span>
        <span class="pill">PostgreSQL</span>
        <span class="pill">dbt</span>
        <span class="pill">Apache Airflow</span>
        <span class="pill">Docker</span>
        <span class="pill green">● Live</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Pipeline Flow (responsive iframe) ────────────────────────────────────────
def step_card_html(icon, name, ok):
    cls       = "ok" if ok else "err"
    badge_txt = "✓ Done" if ok else "✗ Offline"
    return f'<div class="card {cls}"><div class="icon">{icon}</div><div class="name">{name}</div><span class="badge {cls}">{badge_txt}</span></div>'

def arrow_html(ok):
    cls = "ok" if ok else "err"
    return f'<div class="arrow {cls}"><i class="fa-solid fa-arrow-right"></i></div>'

steps = [
    ('<i class="fa-solid fa-database"></i>',     "Source DB",  src_ok),
    ('<i class="fa-solid fa-gears"></i>',        "ELT Script", elt_ok),
    ('<i class="fa-solid fa-server"></i>',       "Dest DB",    dest_ok),
    ('<i class="fa-solid fa-cubes"></i>',        "dbt Models", dbt_ok),
    ('<i class="fa-solid fa-chart-column"></i>', "Results",    dbt_ok),
]

inner = ""
for i, (icon, name, ok) in enumerate(steps):
    inner += step_card_html(icon, name, ok)
    if i < len(steps) - 1:
        inner += arrow_html(ok)

components.html(f"""
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Inter',sans-serif; }}
  html, body {{ background:transparent; }}
  body {{ padding:4px 6px 10px 6px; }}
  .wrapper {{
    background:#0f172a; border:1px solid #1e293b;
    border-radius:16px; padding:18px 16px;
    margin-bottom:0;
  }}
  .label {{
    font-size:11px; font-weight:700; letter-spacing:2px;
    color:#475569; text-transform:uppercase; margin-bottom:16px;
  }}
  .row {{
    display:flex; align-items:stretch; gap:4px;
    flex-wrap:nowrap; width:100%;
  }}
  .card {{
    background:#1e293b; border-radius:12px;
    padding:14px 8px; text-align:center;
    flex:1 1 0; min-width:0; overflow:hidden;
  }}
  .card.ok  {{ border:1.5px solid #4ade80; box-shadow:0 0 14px rgba(74,222,128,0.15); }}
  .card.err {{ border:1.5px solid #ef4444; opacity:0.7; }}
  .icon {{ font-size:20px; margin-bottom:7px; }}
  .card.ok  .icon {{ color:#818cf8; }}
  .card.err .icon {{ color:#f87171; }}
  .name  {{ font-size:11px; font-weight:700; color:#e2e8f0; margin-bottom:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .badge {{ display:inline-block; font-size:10px; font-weight:600; padding:2px 8px; border-radius:100px; white-space:nowrap; }}
  .badge.ok  {{ background:rgba(74,222,128,0.15); color:#4ade80; border:1px solid rgba(74,222,128,0.2); }}
  .badge.err {{ background:rgba(239,68,68,0.15);  color:#ef4444; border:1px solid rgba(239,68,68,0.2); }}
  .arrow {{ font-size:12px; padding:0 2px; flex-shrink:0; align-self:center; }}
  .arrow.ok  {{ color:#4ade80; }}
  .arrow.err {{ color:#334155; }}

  @media (max-width:600px) {{
    .wrapper {{ padding:14px 10px; }}
    .card {{ padding:10px 4px; border-radius:10px; }}
    .icon {{ font-size:16px; margin-bottom:5px; }}
    .name {{ font-size:9px; }}
    .badge {{ font-size:8px; padding:2px 5px; }}
    .arrow {{ font-size:10px; }}
  }}
</style>
<script>
  function autoResize() {{
    const wrapper = document.querySelector('.wrapper');
    const h = wrapper.getBoundingClientRect().height + 24;
    window.parent.postMessage({{isStreamlitMessage: true, type: 'streamlit:setFrameHeight', height: h}}, '*');
  }}
  window.addEventListener('load', autoResize);
  window.addEventListener('resize', autoResize);
  setTimeout(autoResize, 300);
  setTimeout(autoResize, 800);
</script>
</head>
<body>
<div class="wrapper">
  <div class="label">Pipeline Flow</div>
  <div class="row">{inner}</div>
</div>
</body>
</html>
""", height=200, scrolling=False)

# ── Stats ─────────────────────────────────────────────────────────────────────
dbt_built = sum(1 for v in dbt_models.values() if v) if dbt_models else 0
rating_df  = get_table_data("dest", "film_rating", 100) if dbt_ok else pd.DataFrame()
excellent  = int((rating_df["rating_category"] == "Excellent").sum()) if "rating_category" in rating_df.columns else 0

st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-label">Source Rows</div>
        <div class="stat-value purple">{src_rows:,}</div>
        <div class="stat-sub">Across {len(src_tbl)} tables</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Loaded Rows</div>
        <div class="stat-value blue">{dst_rows:,}</div>
        <div class="stat-sub">In destination DB</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">dbt Models</div>
        <div class="stat-value green">{dbt_built} / 4</div>
        <div class="stat-sub">Models built</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Top Rated Films</div>
        <div class="stat-value orange">{excellent}</div>
        <div class="stat-sub">Rated Excellent</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Pipeline Status</div>
        <div class="stat-value {'green' if dbt_ok else 'orange'}">{'100%' if dbt_ok else 'Partial'}</div>
        <div class="stat-sub">{'All steps complete' if dbt_ok else 'Some steps pending'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<style>
.stTabs [data-baseweb="tab-list"] button:nth-child(1) p::before {
    font-family:"Font Awesome 6 Free";font-weight:900;content:"\\f1c0";margin-right:7px;color:#818cf8;
}
.stTabs [data-baseweb="tab-list"] button:nth-child(2) p::before {
    font-family:"Font Awesome 6 Free";font-weight:900;content:"\\f085";margin-right:7px;color:#818cf8;
}
.stTabs [data-baseweb="tab-list"] button:nth-child(3) p::before {
    font-family:"Font Awesome 6 Free";font-weight:900;content:"\\f233";margin-right:7px;color:#818cf8;
}
.stTabs [data-baseweb="tab-list"] button:nth-child(4) p::before {
    font-family:"Font Awesome 6 Free";font-weight:900;content:"\\f1b3";margin-right:7px;color:#818cf8;
}
.stTabs [data-baseweb="tab-list"] button:nth-child(5) p::before {
    font-family:"Font Awesome 6 Free";font-weight:900;content:"\\f080";margin-right:7px;color:#818cf8;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p::before { color:#4ade80 !important; }
@media (max-width:600px) {
    .stTabs [data-baseweb="tab-list"] button:nth-child(1) p::before,
    .stTabs [data-baseweb="tab-list"] button:nth-child(2) p::before,
    .stTabs [data-baseweb="tab-list"] button:nth-child(3) p::before,
    .stTabs [data-baseweb="tab-list"] button:nth-child(4) p::before,
    .stTabs [data-baseweb="tab-list"] button:nth-child(5) p::before { margin-right:4px; }
}
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  Source DB",
    "  ELT Script",
    "  Destination DB",
    "  dbt Models",
    "  Results",
])

# ── Tab 1: Source DB ──────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Source Database — source_postgres:5432</div>', unsafe_allow_html=True)
    if not src_ok:
        st.markdown('<div class="error-box">⚠ Cannot connect to source_postgres:5432</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">✓ Connected to source_postgres:5432 — source_db</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.markdown('<div class="section-title">Tables</div>', unsafe_allow_html=True)
            st.dataframe(src_tbl, use_container_width=True, hide_index=True)
        with col2:
            if not src_tbl.empty:
                sel = st.selectbox("Select table to preview", src_tbl["Table"].tolist(), key="src_sel")
                df  = get_table_data("source", sel)
                st.markdown(f'<div class="section-title">{sel} — first 25 rows</div>', unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, hide_index=True)

# ── Tab 2: ELT Script ─────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">ELT Script Status</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Source DB",        "▲ Up"   if src_ok  else "▼ Down")
    c2.metric("Destination DB",   "▲ Up"   if dest_ok else "▼ Down")
    c3.metric("Data Loaded",      "✔ Yes"  if elt_ok  else "✖ No")
    c4.metric("Rows Transferred", f"{dst_rows:,}")

    st.markdown('<div class="section-title" style="margin-top:24px">How it works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    <b>Step 1:</b> Script waits for <code>source_postgres</code> to be healthy (pg_isready with retry logic)<br>
    <b>Step 2:</b> Runs <code>pg_dump</code> → dumps entire source DB to <code>data_dump.sql</code><br>
    <b>Step 3:</b> Runs <code>psql</code> → loads the SQL dump into <code>destination_postgres</code><br>
    <b>Schedule:</b> Runs automatically at <b>03:00 UTC daily</b> via cron
    </div>
    """, unsafe_allow_html=True)

    if src_ok and dest_ok and not src_tbl.empty and not dst_tbl.empty:
        st.markdown('<div class="section-title" style="margin-top:24px">Row count comparison</div>', unsafe_allow_html=True)
        merged = src_tbl.rename(columns={"Rows": "Source Rows"}).merge(
            dst_tbl[["Table","Rows"]].rename(columns={"Rows": "Dest Rows"}),
            on="Table", how="outer"
        ).fillna(0)
        merged["Source Rows"] = merged["Source Rows"].astype(int)
        merged["Dest Rows"]   = merged["Dest Rows"].astype(int)
        merged["Synced"]      = merged.apply(lambda r: "✔ Synced" if r["Source Rows"] == r["Dest Rows"] else "✖ Mismatch", axis=1)
        st.dataframe(merged, use_container_width=True, hide_index=True)

# ── Tab 3: Destination DB ─────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Destination Database — destination_postgres:5434</div>', unsafe_allow_html=True)
    if not dest_ok:
        st.markdown('<div class="error-box">⚠ Cannot connect to destination_postgres</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">✓ Connected to destination_postgres — destination_db</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.markdown('<div class="section-title">Tables</div>', unsafe_allow_html=True)
            st.dataframe(dst_tbl, use_container_width=True, hide_index=True)
        with col2:
            if not dst_tbl.empty:
                sel = st.selectbox("Select table to preview", dst_tbl["Table"].tolist(), key="dst_sel")
                df  = get_table_data("dest", sel)
                st.markdown(f'<div class="section-title">{sel} — first 25 rows</div>', unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, hide_index=True)

# ── Tab 4: dbt Models ─────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">dbt Transformation Models</div>', unsafe_allow_html=True)
    if not dest_ok:
        st.markdown('<div class="error-box">⚠ Cannot connect to destination DB</div>', unsafe_allow_html=True)
    else:
        descs = {
            "films":       "Base model — selects all films from source",
            "actors":      "Base model — selects all actors from source",
            "film_actors": "Base model — film-to-actor relationship mappings",
            "film_rating": "Final model — films enriched with actor list & rating categories",
        }
        for model, built in dbt_models.items():
            icon   = '<i class="fa-solid fa-circle-check" style="color:#4ade80"></i>' if built else '<i class="fa-solid fa-circle-xmark" style="color:#f87171"></i>'
            color  = "#4ade80" if built else "#f87171"
            status = '<i class="fa-solid fa-check" style="color:#4ade80;margin-right:5px"></i>Built' if built else '<i class="fa-solid fa-xmark" style="color:#f87171;margin-right:5px"></i>Not found'
            st.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
            <div class="model-row">
                <div>
                    <div class="model-name">{icon} &nbsp; {model}</div>
                    <div class="model-desc">{descs.get(model,'')}</div>
                </div>
                <div class="model-status" style="color:{color}">{status}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="margin-top:24px">Lineage</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="font-family:monospace;font-size:13px;line-height:2;overflow-x:auto;">
        films ──────────┐<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├──► &nbsp;<b>film_rating</b> &nbsp;→ &nbsp;JOIN + STRING_AGG actors + rating category<br>
        actors ─────────┤<br>
        film_actors ────┘
        </div>
        """, unsafe_allow_html=True)

# ── Tab 5: Results ────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Final Transformed Data — film_rating</div>', unsafe_allow_html=True)
    if not dest_ok:
        st.markdown('<div class="error-box">⚠ Cannot connect to destination DB</div>', unsafe_allow_html=True)
    elif not dbt_models.get("film_rating"):
        st.markdown('<div class="error-box">⚠ dbt model <b>film_rating</b> not found — run dbt first</div>', unsafe_allow_html=True)
    else:
        df = get_table_data("dest", "film_rating", 100)
        if df.empty:
            st.markdown('<div class="error-box">⚠ No data in film_rating table</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-box">✓ {len(df)} rows loaded from film_rating</div>', unsafe_allow_html=True)

            if "rating_category" in df.columns:
                cats        = df["rating_category"].value_counts()
                excellent_n = int(cats.get("Excellent", 0))
                good_n      = int(cats.get("Good",      0))
                average_n   = int(cats.get("Average",   0))
                poor_n      = int(cats.get("Poor",      0))
                st.markdown(f"""
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
                <div style="display:flex;gap:16px;margin:16px 0;flex-wrap:wrap;">
                    <div style="flex:1;min-width:130px;background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:20px;text-align:center;">
                        <i class="fa-solid fa-trophy" style="font-size:22px;color:#facc15;margin-bottom:10px;display:block;"></i>
                        <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:6px;">Excellent</div>
                        <div style="font-size:32px;font-weight:800;color:#facc15;">{excellent_n}</div>
                    </div>
                    <div style="flex:1;min-width:130px;background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:20px;text-align:center;">
                        <i class="fa-solid fa-circle-check" style="font-size:22px;color:#4ade80;margin-bottom:10px;display:block;"></i>
                        <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:6px;">Good</div>
                        <div style="font-size:32px;font-weight:800;color:#4ade80;">{good_n}</div>
                    </div>
                    <div style="flex:1;min-width:130px;background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:20px;text-align:center;">
                        <i class="fa-solid fa-minus-circle" style="font-size:22px;color:#38bdf8;margin-bottom:10px;display:block;"></i>
                        <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:6px;">Average</div>
                        <div style="font-size:32px;font-weight:800;color:#38bdf8;">{average_n}</div>
                    </div>
                    <div style="flex:1;min-width:130px;background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:20px;text-align:center;">
                        <i class="fa-solid fa-circle-xmark" style="font-size:22px;color:#f87171;margin-bottom:10px;display:block;"></i>
                        <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;color:#475569;text-transform:uppercase;margin-bottom:6px;">Poor</div>
                        <div style="font-size:32px;font-weight:800;color:#f87171;">{poor_n}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-title" style="margin-top:24px">All Records</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:40px;padding-top:20px;border-top:1px solid #1e293b;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
    <div style="font-size:13px;color:#334155;font-weight:600;display:flex;align-items:center;gap:8px;">{logo_html.replace('height:36px','height:20px')} DataStack — ELT Pipeline Monitor</div>
    <div style="font-size:12px;color:#334155;">Python · PostgreSQL · dbt · Apache Airflow · Docker · Streamlit</div>
</div>
""", unsafe_allow_html=True)

