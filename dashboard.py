"""
dashboard.py  —  RedFlagIQ Dashboard
Run: streamlit run dashboard.py
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="RedFlagIQ",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG       = "F0F2F8"
SURFACE  = "FFFFFF"
ACCENT   = "2563EB"
RED      = "DC2626"
RED_LT   = "FEF2F2"
AMBER    = "D97706"
AMBER_LT = "FFFBEB"
GREEN    = "16A34A"
GREEN_LT = "F0FDF4"
TEXT     = "111827"
TEXT2    = "6B7280"
TEXT3    = "9CA3AF"
BORDER   = "E5E7EB"
BORDER2  = "D1D5DB"

def hx(c): return f"#{c}"

RISK_HEX = {"HIGH": hx(RED), "MEDIUM": hx(AMBER), "LOW": hx(GREEN)}
RISK_BG  = {"HIGH": hx(RED_LT), "MEDIUM": hx(AMBER_LT), "LOW": hx(GREEN_LT)}
today    = datetime.now().strftime("%d %b %Y")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
.stApp {{ background: #{BG}; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: #{SURFACE} !important;
    border-right: 1px solid #{BORDER} !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}
/* Hide default collapse button */
section[data-testid="stSidebar"] button[kind="header"] {{
    display: none !important;
}}

/* ── Sidebar buttons styled as nav items ── */
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
    text-align: left !important;
    padding: 9px 14px !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #{TEXT2} !important;
    transition: all 0.15s !important;
    margin-bottom: 1px !important;
    display: flex !important;
    justify-content: flex-start !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: #{BG} !important;
    color: #{TEXT} !important;
}}
section[data-testid="stSidebar"] .stButton > button p {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: inherit !important;
}}

/* ── Hide streamlit chrome ── */
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
header    {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ── Cards ── */
.card {{
    background: #{SURFACE};
    border: 1px solid #{BORDER};
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}}
.card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.08); border-color: #{BORDER2}; }}

.kpi {{
    background: #{SURFACE};
    border: 1px solid #{BORDER};
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: all 0.2s;
}}
.kpi:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
.kpi-lbl {{ font-size: 12px; font-weight: 600; color: #{TEXT2}; margin-bottom: 8px; }}
.kpi-val {{ font-size: 28px; font-weight: 700; color: #{TEXT}; letter-spacing: -0.8px; line-height: 1; }}
.kpi-badge {{ display:inline-flex; align-items:center; gap:3px; font-size:11px; font-weight:600; padding:3px 9px; border-radius:20px; margin-top:8px; }}
.badge-up  {{ background:#{GREEN_LT}; color:#{GREEN}; }}
.badge-dn  {{ background:#{RED_LT};   color:#{RED};   }}
.badge-neu {{ background:#F3F4F6;     color:#{TEXT2}; }}

.date-chip {{
    display:inline-flex; align-items:center; gap:6px;
    font-size:12px; color:#{TEXT2}; font-weight:500;
    background:#{SURFACE}; border:1px solid #{BORDER};
    border-radius:8px; padding:6px 12px;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);
}}

.pill-H {{ display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;background:#{RED_LT};color:#{RED};border:1px solid rgba(220,38,38,0.2); }}
.pill-M {{ display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;background:#{AMBER_LT};color:#{AMBER};border:1px solid rgba(217,119,6,0.2); }}
.pill-L {{ display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;background:#{GREEN_LT};color:#{GREEN};border:1px solid rgba(22,163,74,0.2); }}
.flag-ok  {{ display:inline-flex;align-items:center;gap:4px;padding:2px 9px;border-radius:8px;font-size:11px;font-weight:600;background:#{GREEN_LT};color:#{GREEN}; }}
.flag-bad {{ display:inline-flex;align-items:center;gap:4px;padding:2px 9px;border-radius:8px;font-size:11px;font-weight:600;background:#{RED_LT};color:#{RED}; }}

.ptable {{ width:100%;border-collapse:collapse;font-size:13px; }}
.ptable th {{ font-size:10px;font-weight:600;color:#{TEXT3};text-transform:uppercase;letter-spacing:1px;padding:8px 12px;border-bottom:1px solid #{BORDER};text-align:left; }}
.ptable td {{ padding:13px 12px;color:#{TEXT2};border-bottom:1px solid #F9FAFB;vertical-align:middle; }}
.ptable tr:last-child td {{ border-bottom:none; }}
.ptable tr:hover td {{ background:#FAFAFA; }}
.td-tkr {{ font-weight:700;color:#{TEXT};font-family:'JetBrains Mono',monospace;font-size:12px; }}
.td-num {{ font-family:'JetBrains Mono',monospace;font-size:12px;color:#{TEXT}; }}

.hbar-row {{ display:flex;align-items:center;gap:10px;margin-bottom:10px; }}
.hbar-lbl {{ font-family:'JetBrains Mono',monospace;font-size:11px;color:#{TEXT2};width:46px;text-align:right;flex-shrink:0; }}
.hbar-trk {{ flex:1;height:7px;background:#F3F4F6;border-radius:4px;overflow:hidden; }}
.hbar-fill {{ height:100%;border-radius:4px; }}
.hbar-val {{ font-family:'JetBrains Mono',monospace;font-size:11px;color:#{TEXT3};width:38px;flex-shrink:0; }}

.score-big {{ font-size:48px;font-weight:700;letter-spacing:-2px;line-height:1;font-family:'JetBrains Mono',monospace;text-align:center; }}
.score-lbl {{ font-size:11px;color:#{TEXT3};text-transform:uppercase;letter-spacing:1px;text-align:center;margin-top:6px; }}

.stat-band {{ display:flex;gap:1px;border-radius:14px;overflow:hidden;margin-bottom:20px;border:1px solid #{BORDER}; }}
.sbi {{ flex:1;padding:16px 18px;background:#{SURFACE}; }}
.sbi-lbl {{ font-size:10px;font-weight:600;color:#{TEXT3};text-transform:uppercase;letter-spacing:1px; }}
.sbi-val {{ font-size:20px;font-weight:700;color:#{TEXT};font-family:'JetBrains Mono',monospace;margin:3px 0; }}
.sbi-sub {{ font-size:11px;color:#{TEXT3}; }}

.flag-row {{ display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid #F9FAFB; }}
.flag-row:last-child {{ border-bottom:none; }}
.flag-nm {{ font-size:12px;color:#{TEXT2}; }}

.act-row {{ display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid #F9FAFB; }}
.act-row:last-child {{ border-bottom:none; }}
.act-icon {{ width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;background:#{GREEN_LT}; }}

.prog-wrap {{ margin-bottom:12px; }}
.prog-label {{ display:flex;justify-content:space-between;margin-bottom:5px; }}
.prog-name {{ font-size:12px;font-weight:600;color:#{TEXT}; }}
.prog-pct  {{ font-size:12px;color:#{TEXT2}; }}
.prog-track {{ height:8px;background:#F3F4F6;border-radius:4px;overflow:hidden; }}
.prog-fill  {{ height:100%;border-radius:4px; }}

.co-banner {{
    border-radius:14px;padding:18px 22px;margin-bottom:14px;
    border:1px solid #{BORDER};background:#{SURFACE};
    display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
}}
</style>
""", unsafe_allow_html=True)

PBASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color=hx(TEXT2)),
    margin=dict(t=20, b=20, l=10, r=10),
)
GRID_L = dict(gridcolor="#F3F4F6", zerolinecolor="#F3F4F6")

@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "outputs", "results.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df["m_score"] = pd.to_numeric(df["m_score"], errors="coerce")
    df["z_score"] = pd.to_numeric(df["z_score"], errors="coerce")
    df["custom_flags_triggered"] = (
        pd.to_numeric(df["custom_flags_triggered"], errors="coerce")
        .fillna(0).astype(int)
    )
    df["overall_risk"] = df["overall_risk"].fillna("UNKNOWN")
    return df

def pill(risk):
    cls = {"HIGH":"pill-H","MEDIUM":"pill-M","LOW":"pill-L"}
    ico = {"HIGH":"▲","MEDIUM":"◆","LOW":"●"}
    return f'<span class="{cls.get(risk,"pill-M")}">{ico.get(risk,"")} {risk}</span>'

def flag_badge(val):
    if str(val).upper() == "FLAG":
        return '<span class="flag-bad">▲ FLAG</span>'
    return '<span class="flag-ok">✓ OK</span>'

def risk_color(risk):
    return RISK_HEX.get(risk, hx(TEXT2))

def z_color(z):
    if z > 2.99: return hx(GREEN)
    if z > 1.81: return hx(AMBER)
    return hx(RED)

def hbar(label, pct, val_str, color):
    return f"""<div class="hbar-row">
      <div class="hbar-lbl">{label}</div>
      <div class="hbar-trk"><div class="hbar-fill" style="width:{pct:.1f}%;background:{color}"></div></div>
      <div class="hbar-val">{val_str}</div>
    </div>"""

def gauge(value, title, min_v, max_v, threshold, low_good=True):
    if low_good:
        col = hx(RED) if value > threshold else (hx(AMBER) if value > threshold-0.5 else hx(GREEN))
    else:
        col = hx(RED) if value < threshold*0.6 else (hx(AMBER) if value < threshold else hx(GREEN))
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=round(value,2),
        title={"text":title,"font":{"size":12,"color":hx(TEXT2),"family":"Plus Jakarta Sans"}},
        number={"font":{"size":28,"color":col,"family":"JetBrains Mono"}},
        gauge={
            "axis":{"range":[min_v,max_v],"tickfont":{"size":9,"color":hx(TEXT3)}},
            "bar":{"color":col,"thickness":0.22},
            "bgcolor":hx(BG),"bordercolor":hx(BORDER),"borderwidth":1,
            "threshold":{"line":{"color":col,"width":2},"thickness":0.7,"value":threshold},
            "steps":[
                {"range":[min_v,threshold],"color":hx(GREEN_LT) if not low_good else hx(RED_LT)},
                {"range":[threshold,max_v],"color":hx(RED_LT) if not low_good else hx(GREEN_LT)},
            ],
        }
    ))
    fig.update_layout(**PBASE, height=195)
    return fig

# ── Routing ───────────────────────────────────────────────────────────────────
if "p" not in st.query_params:
    st.query_params["p"] = "overview"
active = st.query_params.get("p", "overview")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(f"""
    <div style="padding:22px 18px 16px;border-bottom:1px solid #{BORDER};margin-bottom:10px">
      <div style="display:flex;align-items:center;gap:9px">
        <div style="width:32px;height:32px;background:#{GREEN};border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px">🚨</div>
        <div>
          <div style="font-size:15px;font-weight:700;color:#{TEXT};letter-spacing:-0.3px">RedFlagIQ</div>
          <div style="font-size:10px;color:#{TEXT3}">Financial Intelligence</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Section: MAIN ─────────────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:10px;font-weight:700;color:#{TEXT3};text-transform:uppercase;letter-spacing:1.5px;padding:8px 18px 4px">MAIN</div>', unsafe_allow_html=True)

    nav_items_main = [
        ("overview",   "🏠", "Overview"),
        ("company",    "🔍", "Company View"),
        ("comparison", "⚖️", "Comparison"),
    ]
    for key, icon, label in nav_items_main:
        is_active = (active == key)
        if is_active:
            st.markdown(f"""
            <div style="margin:1px 10px;padding:9px 12px;border-radius:10px;
                        background:#{TEXT};display:flex;align-items:center;gap:9px">
              <span>{icon}</span>
              <span style="font-size:13px;font-weight:600;color:white">{label}</span>
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True):
                st.query_params["p"] = key
                st.rerun()

    # ── Section: INTELLIGENCE ─────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:10px;font-weight:700;color:#{TEXT3};text-transform:uppercase;letter-spacing:1.5px;padding:14px 18px 4px">INTELLIGENCE</div>', unsafe_allow_html=True)

    nav_items_intel = [
        ("beneish", "📐", "Beneish M-Score"),
        ("altman",  "📈", "Altman Z-Score"),
    ]
    for key, icon, label in nav_items_intel:
        is_active = (active == key)
        if is_active:
            st.markdown(f"""
            <div style="margin:1px 10px;padding:9px 12px;border-radius:10px;
                        background:#{TEXT};display:flex;align-items:center;gap:9px">
              <span>{icon}</span>
              <span style="font-size:13px;font-weight:600;color:white">{label}</span>
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True):
                st.query_params["p"] = key
                st.rerun()

    # ── Section: OTHERS ───────────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:10px;font-weight:700;color:#{TEXT3};text-transform:uppercase;letter-spacing:1.5px;padding:14px 18px 4px">OTHERS</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin:0 10px">
      <div style="padding:9px 12px;border-radius:10px;font-size:13px;font-weight:500;color:#{TEXT2};display:flex;align-items:center;gap:9px">⚙️ <span>Settings</span></div>
      <div style="padding:9px 12px;border-radius:10px;font-size:13px;font-weight:500;color:#{TEXT2};display:flex;align-items:center;gap:9px">❓ <span>Help</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI Assistant ──────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin:0 10px 8px;padding:14px;background:#{GREEN_LT};border:1px solid rgba(22,163,74,0.2);border-radius:14px">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:10px">
        <span style="font-size:14px">🤖</span>
        <span style="font-size:13px;font-weight:600;color:#{TEXT}">AI Assistant</span>
        <div style="width:7px;height:7px;background:#{GREEN};border-radius:50%;margin-left:auto"></div>
      </div>
      <div style="background:white;border:1px solid #{BORDER};border-radius:8px;padding:8px 10px;font-size:11px;color:#{TEXT3};display:flex;align-items:center;justify-content:space-between">
        <span>Ask anything finance...</span>
        <span style="color:#{GREEN};font-weight:700">▶</span>
      </div>
      <div style="display:flex;gap:6px;margin-top:8px">
        <div style="background:white;border:1px solid #{BORDER};border-radius:6px;padding:4px 8px;font-size:10px;font-weight:500;color:#{TEXT2}">Risk tips</div>
        <div style="background:white;border:1px solid #{BORDER};border-radius:6px;padding:4px 8px;font-size:10px;font-weight:500;color:#{TEXT2}">M-Score help</div>
      </div>
    </div>
    <div style="text-align:center;font-size:10px;color:#{TEXT3};padding:6px 0">github.com/shetty30/redflagiq</div>
    """, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data()
if df is None:
    st.error("outputs/results.csv not found. Run: python main.py --batch tickers.csv")
    st.stop()

SORT_RISK = {"HIGH":0,"MEDIUM":1,"LOW":2}
FLAG_NAMES = [
    "Revenue growing but OCF flat or declining",
    "Receivables growing 2x faster than revenue",
    "Gross margin declining year-over-year",
    "Debt-to-equity spike > 40% in one year",
    "Net income positive but FCF negative",
]
FLAG_COLS = ["flag_1_revenue_ocf","flag_2_ar_revenue","flag_3_gross_margin",
             "flag_4_debt_equity","flag_5_ni_fcf"]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if active == "overview":

    total  = len(df)
    high   = len(df[df["overall_risk"]=="HIGH"])
    medium = len(df[df["overall_risk"]=="MEDIUM"])
    low    = len(df[df["overall_risk"]=="LOW"])
    avg_m  = df["m_score"].mean()
    avg_z  = df["z_score"].mean()

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid #{BORDER}">
      <div style="font-size:20px;font-weight:700;color:#{TEXT}">Overview Dashboard</div>
      <div class="date-chip">📅 {today}</div>
    </div>
    """, unsafe_allow_html=True)

    k1,k2,k3 = st.columns(3)
    with k1:
        st.markdown(f"""<div class="kpi">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
            <div class="kpi-lbl">Companies Analysed</div>
            <span style="font-size:11px;color:#{TEXT3};background:#F3F4F6;padding:3px 8px;border-radius:6px">FY2024</span>
          </div>
          <div class="kpi-val">{total}</div>
          <div class="kpi-badge badge-neu">S&P listed companies</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
            <div class="kpi-lbl">High Risk Detected</div>
            <span style="font-size:11px;color:#{TEXT3};background:#F3F4F6;padding:3px 8px;border-radius:6px">FY2024</span>
          </div>
          <div class="kpi-val" style="color:#{RED}">{high}</div>
          <div class="kpi-badge badge-dn">▲ AMC · Ford</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
            <div class="kpi-lbl">Average Z-Score</div>
            <span style="font-size:11px;color:#{TEXT3};background:#F3F4F6;padding:3px 8px;border-radius:6px">FY2024</span>
          </div>
          <div class="kpi-val" style="color:#{GREEN}">{avg_z:.2f}</div>
          <div class="kpi-badge badge-up">↑ Safe zone > 2.99</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    k4,k5,k6 = st.columns(3)
    with k4:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-lbl" style="margin-bottom:8px">Average M-Score</div>
          <div class="kpi-val">{avg_m:.2f}</div>
          <div class="kpi-badge badge-dn">Threshold: −1.78</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-lbl" style="margin-bottom:8px">Medium Risk</div>
          <div class="kpi-val" style="color:#{AMBER}">{medium}</div>
          <div class="kpi-badge badge-neu">Monitor closely</div>
        </div>""", unsafe_allow_html=True)
    with k6:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-lbl" style="margin-bottom:8px">Low Risk</div>
          <div class="kpi-val" style="color:#{GREEN}">{low}</div>
          <div class="kpi-badge badge-up">Clean signals</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    left, right = st.columns([3,2])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px"><span style="font-size:14px;font-weight:700;color:#{TEXT}">M-Score Distribution</span><span style="font-size:11px;color:#{TEXT3};background:#F3F4F6;padding:3px 10px;border-radius:6px">Manipulation Risk</span></div>', unsafe_allow_html=True)
        mdf = df[["ticker","m_score","overall_risk"]].sort_values("m_score")
        fig_bar = px.bar(mdf, x="ticker", y="m_score", color="overall_risk",
                         color_discrete_map={"HIGH":hx(RED),"MEDIUM":hx(AMBER),"LOW":hx(GREEN)},
                         text="m_score")
        fig_bar.add_hline(y=-1.78, line_dash="dash", line_color="rgba(220,38,38,0.5)", line_width=1.5,
                          annotation_text="−1.78 threshold",
                          annotation_font=dict(color="rgba(220,38,38,0.65)",size=10))
        fig_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside",
                              textfont=dict(size=10,color=hx(TEXT2)),
                              marker_line_width=0, marker_cornerradius=4)
        fig_bar.update_layout(**PBASE, height=260, showlegend=False)
        fig_bar.update_xaxes(**GRID_L, title="")
        fig_bar.update_yaxes(**GRID_L, title="")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:4px">Risk Distribution</div><div style="font-size:11px;color:#{TEXT3};margin-bottom:14px">10 companies</div>', unsafe_allow_html=True)
        rc = df["overall_risk"].value_counts().reindex(["HIGH","MEDIUM","LOW"],fill_value=0)
        fig_d = go.Figure(go.Pie(
            labels=["High","Medium","Low"], values=rc.values, hole=0.60,
            marker=dict(colors=[hx(RED),hx(AMBER),hx(GREEN)],
                        line=dict(color="white",width=3)),
            textinfo="label+value",
            textfont=dict(size=11,color=hx(TEXT),family="Plus Jakarta Sans"),
        ))
        fig_d.update_layout(**PBASE, height=180, showlegend=False,
                             annotations=[dict(text=f"<b>{total}</b>",x=0.5,y=0.5,
                                               font=dict(size=20,color=hx(TEXT),family="JetBrains Mono"),
                                               showarrow=False)])
        st.plotly_chart(fig_d, use_container_width=True)
        st.markdown(f"""
        <div style="border-top:1px solid #{BORDER};padding-top:12px">
          <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #F9FAFB"><span style="font-size:12px;color:#{TEXT2}">Avg Flags Triggered</span><span style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#{TEXT}">1.1 / 5</span></div>
          <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #F9FAFB"><span style="font-size:12px;color:#{TEXT2}">Distress Zone</span><span style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#{RED}">2</span></div>
          <div style="display:flex;justify-content:space-between;padding:7px 0"><span style="font-size:12px;color:#{TEXT2}">Models Applied</span><span style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#{TEXT}">3</span></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    tl,tr = st.columns([3,2])
    with tl:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px"><span style="font-size:14px;font-weight:700;color:#{TEXT}">Company Risk Table</span><span style="font-size:11px;color:#{TEXT3};background:#F3F4F6;padding:3px 10px;border-radius:6px">FY2024</span></div>', unsafe_allow_html=True)
        tdf = df[["ticker","company_name","m_score","z_score","custom_flags_triggered","overall_risk"]].copy()
        tdf = tdf.sort_values("overall_risk",key=lambda x:x.map(SORT_RISK))
        rows = "".join(f"""<tr>
          <td><span class="td-tkr">{r['ticker']}</span></td>
          <td style="font-size:12px;color:#{TEXT2}">{str(r['company_name'])[:20]}</td>
          <td class="td-num" style="text-align:center">{r['m_score']:.2f}</td>
          <td class="td-num" style="text-align:center">{r['z_score']:.2f}</td>
          <td style="text-align:center;font-size:13px;color:#{TEXT2}">{int(r['custom_flags_triggered'])}</td>
          <td style="text-align:center">{pill(r['overall_risk'])}</td>
        </tr>""" for _,r in tdf.iterrows())
        st.markdown(f"""<table class="ptable"><thead><tr>
          <th>Ticker</th><th>Company</th>
          <th style="text-align:center">M-Score</th><th style="text-align:center">Z-Score</th>
          <th style="text-align:center">Flags</th><th style="text-align:center">Risk</th>
        </tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tr:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px"><span style="font-size:14px;font-weight:700;color:#{TEXT}">Recent Activity</span><span style="font-size:11px;color:#{TEXT3};background:#F3F4F6;padding:3px 10px;border-radius:6px">This Run</span></div>', unsafe_allow_html=True)
        acts = [("🍎","AAPL","Apple Inc.","MEDIUM","neutral"),("🪟","MSFT","Microsoft","MEDIUM","neutral"),
                ("⚡","TSLA","Tesla","MEDIUM","neutral"),("📦","AMZN","Amazon","MEDIUM","neutral"),
                ("🎬","AMC","AMC Entmt.","HIGH","negative"),("🚗","F","Ford Motor","HIGH","negative")]
        for icon,tkr,name,risk,sent in acts:
            vc = f"color:#{RED};font-weight:600" if sent=="negative" else f"color:#{TEXT2};font-weight:600"
            vt = "HIGH RISK" if sent=="negative" else "MEDIUM"
            st.markdown(f"""<div class="act-row">
              <div style="display:flex;align-items:center;gap:10px">
                <div class="act-icon">{icon}</div>
                <div><div style="font-size:13px;font-weight:600;color:#{TEXT}">{tkr}</div><div style="font-size:11px;color:#{TEXT3}">{name}</div></div>
              </div>
              <div style="{vc}">{vt}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">Flags Triggered</div>', unsafe_allow_html=True)
        fdf = df[["ticker","custom_flags_triggered","overall_risk"]].sort_values("custom_flags_triggered",ascending=False)
        for _,r in fdf.iterrows():
            st.markdown(hbar(r["ticker"],r["custom_flags_triggered"]*20,f"{int(r['custom_flags_triggered'])}/5",risk_color(r["overall_risk"])), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — COMPANY VIEW
# ══════════════════════════════════════════════════════════════════════════════
elif active == "company":

    st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid #{BORDER}"><div style="font-size:20px;font-weight:700;color:#{TEXT}">Company Deep Dive</div><div class="date-chip">📅 {today}</div></div>', unsafe_allow_html=True)

    options  = [f"{r['ticker']}  —  {r['company_name']}" for _,r in df.iterrows()]
    selected = st.selectbox("", options, label_visibility="collapsed")
    ticker   = selected.split("  —  ")[0].strip()
    row      = df[df["ticker"]==ticker].iloc[0]
    risk     = row["overall_risk"]

    st.markdown(f"""<div class="co-banner" style="border-left:4px solid {risk_color(risk)}">
      <div>
        <div style="font-size:20px;font-weight:700;color:#{TEXT}">{row['company_name']}
          <span style="font-size:13px;color:#{TEXT3};font-weight:400"> ({ticker})</span></div>
        <div style="font-size:12px;color:#{TEXT2};margin-top:4px">{row.get('sector','N/A')} · FY{row.get('analysis_year','2024')} vs FY{row.get('prior_year','2023')}</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:10px;color:#{TEXT3};text-transform:uppercase;letter-spacing:1px;margin-bottom:5px">Overall Risk</div>
        {pill(risk)}
      </div>
    </div>""", unsafe_allow_html=True)

    g1,g2,g3 = st.columns(3)
    with g1:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.plotly_chart(gauge(row["m_score"],"Beneish M-Score",-5,2,-1.78,True), use_container_width=True)
        st.markdown(f'<div style="text-align:center;font-size:11px;color:#{TEXT3};margin-top:-6px">{str(row.get("m_score_verdict","N/A"))}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with g2:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.plotly_chart(gauge(row["z_score"],"Altman Z-Score",0,12,2.99,False), use_container_width=True)
        st.markdown(f'<div style="text-align:center;font-size:11px;color:#{TEXT3};margin-top:-6px">{str(row.get("z_score_zone","N/A"))}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with g3:
        flags = int(row["custom_flags_triggered"])
        fcol  = hx(RED) if flags>=3 else (hx(AMBER) if flags>=1 else hx(GREEN))
        st.markdown(f"""<div class="card" style="text-align:center;height:222px;display:flex;flex-direction:column;justify-content:center">
          <div class="kpi-lbl">Custom Red Flags</div>
          <div class="score-big" style="color:{fcol}">{flags}</div>
          <div class="score-lbl">out of 5 triggered</div>
          <div style="margin-top:12px">{pill(risk)}</div>
        </div>""", unsafe_allow_html=True)

    k1,k2,k3,k4 = st.columns(4)
    for col,lbl,val,sub in [
        (k1,"M-Score",f"{row['m_score']:.4f}","Threshold: −1.78"),
        (k2,"Z-Score",f"{row['z_score']:.4f}","Safe: > 2.99"),
        (k3,"Flags",f"{flags} / 5","Custom checks"),
        (k4,"Flagged Ratios",str(row.get("m_flagged_ratios","None") or "None"),"Beneish ratios"),
    ]:
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-lbl">{lbl}</div><div class="kpi-val" style="font-size:18px">{val}</div><div style="font-size:11px;color:#{TEXT3};margin-top:4px">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">Custom Red Flag Checklist</div>', unsafe_allow_html=True)
    for name,val in zip(FLAG_NAMES,[str(row.get(c,"OK")).upper() for c in FLAG_COLS]):
        st.markdown(f'<div class="flag-row"><div class="flag-nm">{name}</div>{flag_badge(val)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    c1p,c2p = st.columns(2)
    with c1p:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        m_pct = max(0,min(100,((-row["m_score"])/5)*100))
        st.markdown(f"""<div class="prog-wrap">
          <div class="prog-label"><span class="prog-name">M-Score Safety</span><span class="prog-pct">{m_pct:.0f}%</span></div>
          <div class="prog-track"><div class="prog-fill" style="width:{m_pct:.1f}%;background:#{ACCENT}"></div></div>
          <div style="font-size:11px;color:#{TEXT3};margin-top:4px">{row['m_score']:.4f} (lower = safer)</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2p:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        z_pct = max(0,min(100,(row["z_score"]/10)*100))
        zc    = z_color(row["z_score"])
        st.markdown(f"""<div class="prog-wrap">
          <div class="prog-label"><span class="prog-name">Z-Score Health</span><span class="prog-pct">{z_pct:.0f}%</span></div>
          <div class="prog-track"><div class="prog-fill" style="width:{z_pct:.1f}%;background:{zc}"></div></div>
          <div style="font-size:11px;color:#{TEXT3};margin-top:4px">{row['z_score']:.4f} (higher = safer)</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif active == "comparison":

    st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid #{BORDER}"><div style="font-size:20px;font-weight:700;color:#{TEXT}">Comparison View</div><div class="date-chip">📅 {today}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px"><span style="font-size:14px;font-weight:700;color:#{TEXT}">M-Score vs Z-Score — Risk Quadrant Map</span><span style="font-size:11px;color:#{TEXT3};background:#F3F4F6;padding:3px 10px;border-radius:6px">Bubble = Flags</span></div>', unsafe_allow_html=True)
    m_min = df["m_score"].min()-0.5; m_max = df["m_score"].max()+0.5; z_max_v = df["z_score"].max()+2
    fig_sc = px.scatter(df, x="m_score", y="z_score", size="custom_flags_triggered",
                        color="overall_risk", color_discrete_map={"HIGH":hx(RED),"MEDIUM":hx(AMBER),"LOW":hx(GREEN)},
                        text="ticker",
                        hover_data={"company_name":True,"m_score":":.3f","z_score":":.3f","custom_flags_triggered":True},
                        size_max=40)
    fig_sc.add_vline(x=-1.78,line_dash="dash",line_color="rgba(220,38,38,0.4)",line_width=1.5,
                     annotation_text="M=−1.78",annotation_font=dict(color="rgba(220,38,38,0.55)",size=10))
    fig_sc.add_hline(y=2.99,line_dash="dash",line_color="rgba(22,163,74,0.4)",line_width=1.5,
                     annotation_text="Z=2.99 Safe",annotation_font=dict(color="rgba(22,163,74,0.55)",size=10))
    fig_sc.add_shape(type="rect",x0=m_min,x1=-1.78,y0=2.99,y1=z_max_v,fillcolor="rgba(22,163,74,0.04)",line_width=0)
    fig_sc.add_shape(type="rect",x0=-1.78,x1=m_max,y0=0,y1=2.99,fillcolor="rgba(220,38,38,0.04)",line_width=0)
    fig_sc.update_traces(textposition="top center",textfont=dict(size=11,color=hx(TEXT2)),
                         marker=dict(line=dict(color="white",width=1.5)))
    fig_sc.update_layout(**PBASE,height=380,showlegend=False)
    fig_sc.update_xaxes(**GRID_L,title="M-Score (lower = safer)")
    fig_sc.update_yaxes(**GRID_L,title="Z-Score (higher = safer)")
    st.plotly_chart(fig_sc, use_container_width=True)
    st.markdown(f'<div style="font-size:11px;color:#{TEXT3};text-align:center;margin-top:-10px">Top-left = Safe + Clean · Bottom-right = High Risk Zone</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">M-Score Ranking <span style="font-size:11px;font-weight:400;color:#{TEXT3}">Lower = Safer</span></div>', unsafe_allow_html=True)
        mdf2 = df[["ticker","m_score","overall_risk"]].sort_values("m_score")
        m_rng = mdf2["m_score"].max()-mdf2["m_score"].min()+0.5
        for _,r in mdf2.iterrows():
            pct = max(0,min(100,((r["m_score"]-mdf2["m_score"].min())/m_rng)*100))
            st.markdown(hbar(r["ticker"],pct,f"{r['m_score']:.2f}",risk_color(r["overall_risk"])), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">Z-Score Ranking <span style="font-size:11px;font-weight:400;color:#{TEXT3}">Higher = Safer</span></div>', unsafe_allow_html=True)
        zdf2 = df[["ticker","z_score","overall_risk"]].sort_values("z_score")
        z_rng = max(df["z_score"].max(),12)
        for _,r in zdf2.iterrows():
            pct = max(0,min(100,(r["z_score"]/z_rng)*100))
            st.markdown(hbar(r["ticker"],pct,f"{r['z_score']:.1f}",z_color(r["z_score"])), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">Full Comparison Table</div>', unsafe_allow_html=True)
    cdf = df[["ticker","company_name","m_score","z_score","custom_flags_triggered","m_flagged_ratios","overall_risk"]].copy()
    cdf = cdf.sort_values("overall_risk",key=lambda x:x.map(SORT_RISK))
    rows2 = "".join(f"""<tr>
      <td><span class="td-tkr">{r['ticker']}</span></td>
      <td style="font-size:12px;color:#{TEXT2}">{str(r['company_name'])[:24]}</td>
      <td class="td-num" style="text-align:center">{r['m_score']:.3f}</td>
      <td class="td-num" style="text-align:center">{r['z_score']:.3f}</td>
      <td style="text-align:center;font-size:13px;color:#{TEXT2}">{int(r['custom_flags_triggered'])}</td>
      <td style="font-size:11px;color:#{TEXT3}">{str(r['m_flagged_ratios'] or 'None')}</td>
      <td style="text-align:center">{pill(r['overall_risk'])}</td>
    </tr>""" for _,r in cdf.iterrows())
    st.markdown(f"""<table class="ptable"><thead><tr>
      <th>Ticker</th><th>Company</th>
      <th style="text-align:center">M-Score</th><th style="text-align:center">Z-Score</th>
      <th style="text-align:center">Flags</th><th>Flagged Ratios</th>
      <th style="text-align:center">Risk</th>
    </tr></thead><tbody>{rows2}</tbody></table>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — BENEISH
# ══════════════════════════════════════════════════════════════════════════════
elif active == "beneish":

    st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid #{BORDER}"><div style="font-size:20px;font-weight:700;color:#{TEXT}">Beneish M-Score</div><div class="date-chip">📅 {today}</div></div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="stat-band">
      <div class="sbi"><div class="sbi-lbl">Model</div><div class="sbi-val">M-Score</div><div class="sbi-sub">Beneish 1999</div></div>
      <div class="sbi"><div class="sbi-lbl">Manipulation Threshold</div><div class="sbi-val" style="color:#{RED}">−1.78</div><div class="sbi-sub">Score above = likely manipulator</div></div>
      <div class="sbi"><div class="sbi-lbl">Grey Zone</div><div class="sbi-val" style="color:#{AMBER}">−2.22</div><div class="sbi-sub">Monitor closely</div></div>
      <div class="sbi"><div class="sbi-lbl">Ratios Used</div><div class="sbi-val">8</div><div class="sbi-sub">DSRI · GMI · AQI · SGI + 4</div></div>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">The 8 Ratios</div>', unsafe_allow_html=True)
        ri = [("DSRI","Receivables growing faster than sales","> 1.031"),("GMI","Gross margin deteriorating","> 1.014"),
              ("AQI","Non-productive assets growing","> 1.040"),("SGI","Revenue growth pressure","> 1.134"),
              ("DEPI","Depreciation rate slowing","> 1.001"),("SGAI","Overheads outpacing revenue","> 1.054"),
              ("TATA","Earnings not backed by cash","> 0.018"),("LVGI","Leverage increasing","> 1.111")]
        rows_r = "".join(f'<tr><td><span class="td-tkr">{r[0]}</span></td><td style="font-size:12px;color:#{TEXT2}">{r[1]}</td><td class="td-num">{r[2]}</td></tr>' for r in ri)
        st.markdown(f'<table class="ptable"><thead><tr><th>Ratio</th><th>What It Detects</th><th>Red Flag</th></tr></thead><tbody>{rows_r}</tbody></table>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:10px">Formula</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#{TEXT2};line-height:2;background:#F9FAFB;padding:14px;border-radius:10px;border:1px solid #{BORDER}">M = −4.84 + (0.920×DSRI) + (0.528×GMI) + (0.404×AQI)<br>&nbsp;&nbsp;&nbsp;&nbsp;+ (0.892×SGI) + (0.115×DEPI) − (0.172×SGAI)<br>&nbsp;&nbsp;&nbsp;&nbsp;− (0.327×TATA) + (4.679×LVGI)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">AAPL — Ratio Breakdown (FY2024)</div>', unsafe_allow_html=True)
        aapl = [("DSRI",1.1098,True),("GMI",0.9551,False),("AQI",1.000,False),("SGI",1.0202,False),
                ("DEPI",0.9355,False),("SGAI",1.026,False),("TATA",-0.0672,False),("LVGI",0.8694,False)]
        v_max = max(abs(r[1]) for r in aapl)
        for name,val,flagged in aapl:
            pct = min(100,abs(val)/(v_max*1.1)*100)
            col = hx(RED) if flagged else hx(GREEN)
            st.markdown(hbar(name,pct,f"{val:.3f}",col), unsafe_allow_html=True)
        st.markdown(f"""<div style="margin-top:14px;padding-top:14px;border-top:1px solid #{BORDER}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-size:12px;color:#{TEXT2}">Final M-Score</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700;color:#{AMBER}">2.89</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:12px;color:#{TEXT2}">Verdict</span>
            <span class="pill-M">Grey Zone — Monitor</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">All Companies</div>', unsafe_allow_html=True)
        mdf3 = df[["ticker","m_score","overall_risk"]].sort_values("m_score")
        m_rng3 = mdf3["m_score"].max()-mdf3["m_score"].min()+0.5
        for _,r in mdf3.iterrows():
            pct = max(0,min(100,((r["m_score"]-mdf3["m_score"].min())/m_rng3)*100))
            st.markdown(hbar(r["ticker"],pct,f"{r['m_score']:.2f}",risk_color(r["overall_risk"])), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — ALTMAN
# ══════════════════════════════════════════════════════════════════════════════
elif active == "altman":

    st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid #{BORDER}"><div style="font-size:20px;font-weight:700;color:#{TEXT}">Altman Z-Score</div><div class="date-chip">📅 {today}</div></div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="stat-band">
      <div class="sbi"><div class="sbi-lbl">Model</div><div class="sbi-val">Z-Score</div><div class="sbi-sub">Altman 1968</div></div>
      <div class="sbi"><div class="sbi-lbl">Safe Zone</div><div class="sbi-val" style="color:#{GREEN}">&gt; 2.99</div><div class="sbi-sub">Low distress probability</div></div>
      <div class="sbi"><div class="sbi-lbl">Grey Zone</div><div class="sbi-val" style="color:#{AMBER}">1.81—2.99</div><div class="sbi-sub">Uncertain</div></div>
      <div class="sbi"><div class="sbi-lbl">Distress Zone</div><div class="sbi-val" style="color:#{RED}">&lt; 1.81</div><div class="sbi-sub">High bankruptcy risk</div></div>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">The 5 Factors</div>', unsafe_allow_html=True)
        fi = [("X1","Working Capital / TA","1.2×","Liquidity"),("X2","Retained Earnings / TA","1.4×","Profitability"),
              ("X3","EBIT / TA","3.3×","Operating efficiency"),("X4","Market Cap / Liabilities","0.6×","Solvency"),
              ("X5","Revenue / TA","1.0×","Asset turnover")]
        rows_f = "".join(f'<tr><td><span class="td-tkr">{f[0]}</span></td><td class="td-num" style="font-size:11px">{f[1]}</td><td class="td-num">{f[2]}</td><td style="font-size:12px;color:#{TEXT2}">{f[3]}</td></tr>' for f in fi)
        st.markdown(f'<table class="ptable"><thead><tr><th>Factor</th><th>Ratio</th><th>Weight</th><th>Measures</th></tr></thead><tbody>{rows_f}</tbody></table>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:12px;font-family:\'JetBrains Mono\',monospace;font-size:12px;color:#{TEXT2};background:#F9FAFB;padding:12px;border-radius:10px;border:1px solid #{BORDER}">Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">Zone Reference</div>', unsafe_allow_html=True)
        for score,zone,meaning,col in [("> 2.99","Safe Zone","Low bankruptcy probability",hx(GREEN)),
                                        ("1.81–2.99","Grey Zone","Monitor closely",hx(AMBER)),
                                        ("< 1.81","Distress Zone","High distress probability",hx(RED))]:
            st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid #F9FAFB"><div><div style="font-family:\'JetBrains Mono\',monospace;font-size:13px;font-weight:600;color:{col}">{score}</div><div style="font-size:11px;color:#{TEXT3};margin-top:2px">{meaning}</div></div><div style="font-size:12px;font-weight:600;color:{col}">{zone}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">AAPL — Factor Breakdown (FY2024)</div>', unsafe_allow_html=True)
        aapl_z = [("X1 WC/TA",-0.077),("X2 RE/TA",-0.073),("X3 EBIT/TA",1.114),("X4 MC/TL",6.817),("X5 Rev/TA",1.071)]
        for name,weighted in aapl_z:
            pct = min(100,abs(weighted)/8*100)
            col = hx(GREEN) if weighted>=0 else hx(RED)
            st.markdown(hbar(name,pct,f"{weighted:.3f}",col), unsafe_allow_html=True)
        st.markdown(f"""<div style="margin-top:14px;padding-top:14px;border-top:1px solid #{BORDER}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-size:12px;color:#{TEXT2}">Final Z-Score</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700;color:#{GREEN}">8.85</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:12px;color:#{TEXT2}">Zone</span>
            <span class="pill-L">Safe Zone</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#{TEXT};margin-bottom:14px">All Companies</div>', unsafe_allow_html=True)
        zdf3 = df[["ticker","z_score","overall_risk"]].sort_values("z_score")
        z_rng3 = max(df["z_score"].max(),12)
        for _,r in zdf3.iterrows():
            pct = max(0,min(100,(r["z_score"]/z_rng3)*100))
            st.markdown(hbar(r["ticker"],pct,f"{r['z_score']:.1f}",z_color(r["z_score"])), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)