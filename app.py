import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(
    page_title="광고 성과 대시보드",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzf8yCiR_Vx0VTVbGTgAPguH08M1r7FtPaF_g3KfbY2GJWUJSd1HihLuergbrylptrYfw/exec"
TEAM_ACCOUNTS   = []

PLATFORM_COLORS = {"TVING": "#6C50F3", "Wavve": "#06B6D4"}
DEVICE_COLORS   = {"CTV": "#F59E0B", "iOS": "#10B981", "Android": "#EF4444", "Web": "#3B82F6"}

PURPLE      = "#6C50F3"
PURPLE_DARK = "#5840D6"
PURPLE_LT   = "#EEE9FF"
ORANGE      = "#F97316"
CYAN        = "#06B6D4"
GREEN       = "#22C55E"
TEXT_H      = "#18105C"
TEXT_B      = "#4B4578"
TEXT_SUB    = "#9591C4"
CHART_BG    = "rgba(0,0,0,0)"
GRID_COLOR  = "rgba(108,80,243,0.08)"

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

html, body, [class*="css"], .stApp, .stMarkdown, .stMetric,
.stSelectbox, .stMultiSelect, .stTextInput, .stButton,
.stDataFrame, .stTabs, button, input, select, textarea {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', 'Segoe UI', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── 전체 배경 ── */
.stApp { background: #F4F5FF !important; }
.block-container { padding: 1.6rem 2rem 3rem !important; max-width: 1440px; }

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #6C50F3 0%, #5840D6 100%) !important;
    border-right: none !important;
    box-shadow: 6px 0 32px rgba(108,80,243,.22) !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; font-family: 'Pretendard','Malgun Gothic',sans-serif !important; }
[data-testid="stSidebar"] label { font-weight: 600 !important; font-size: 12px !important; letter-spacing: .03em; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: rgba(255,255,255,.15) !important;
    border: 1.5px solid rgba(255,255,255,.25) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div *,
[data-testid="stSidebar"] .stMultiSelect > div > div * { color: #fff !important; }
[data-testid="stSidebar"] h3 {
    color: #fff !important; font-size: 14px !important; font-weight: 800 !important;
    letter-spacing: .02em; border-bottom: 1px solid rgba(255,255,255,.2);
    padding-bottom: 8px; margin-bottom: 14px;
}

/* ── KPI 카드 ── */
[data-testid="stMetric"] {
    background: #fff !important;
    border-radius: 18px !important;
    padding: 18px 20px !important;
    box-shadow: 0 4px 20px rgba(108,80,243,.09), 0 1px 3px rgba(0,0,0,.04) !important;
    border: 1.5px solid #EAE7FF !important;
    transition: transform .18s, box-shadow .18s;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(108,80,243,.16) !important;
}
[data-testid="stMetricLabel"] {
    color: #9591C4 !important; font-size: 11px !important;
    font-weight: 700 !important; text-transform: uppercase; letter-spacing: .07em;
}
[data-testid="stMetricValue"] {
    color: #18105C !important; font-size: 24px !important;
    font-weight: 800 !important; letter-spacing: -.5px;
    font-variant-numeric: tabular-nums;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; font-weight: 600 !important; }

/* ── 섹션 타이틀 ── */
.sec-title {
    font-size: 15px; font-weight: 800; color: #18105C;
    margin: 24px 0 14px; display: flex; align-items: center; gap: 8px;
    letter-spacing: -.3px;
}
.sec-title::after {
    content: ''; flex: 1; height: 1.5px;
    background: linear-gradient(90deg, #EAE7FF, transparent);
    border-radius: 2px;
}

/* ── 커스텀 KPI 카드 (HTML) ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 6px; }
.kpi-card {
    background: #fff; border-radius: 18px;
    padding: 18px 18px 16px;
    box-shadow: 0 4px 20px rgba(108,80,243,.09);
    border: 1.5px solid #EAE7FF;
    position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute; bottom: 0; left: 16px; right: 16px;
    height: 2.5px; border-radius: 2px 2px 0 0;
}
.kpi-card.p::after { background: linear-gradient(90deg,#6C50F3,#A78BFA); }
.kpi-card.o::after { background: linear-gradient(90deg,#F97316,#FB923C); }
.kpi-card.c::after { background: linear-gradient(90deg,#06B6D4,#22D3EE); }
.kpi-card.g::after { background: linear-gradient(90deg,#22C55E,#4ADE80); }
.kpi-card.r::after { background: linear-gradient(90deg,#EF4444,#F87171); }
.kpi-ic {
    width: 36px; height: 36px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; margin-bottom: 12px;
}
.kpi-lbl { font-size: 10px; font-weight: 700; color: #9591C4; text-transform: uppercase; letter-spacing: .07em; margin-bottom: 4px; }
.kpi-val { font-size: 22px; font-weight: 800; color: #18105C; letter-spacing: -.7px; font-variant-numeric: tabular-nums; }
.kpi-sub { font-size: 10px; font-weight: 600; margin-top: 5px; }
.kpi-sub.up   { color: #22C55E; }
.kpi-sub.down { color: #EF4444; }
.kpi-sub.neu  { color: #9591C4; }

/* ── 그룹 헤더 ── */
.kpi-group-title {
    font-size: 11px; font-weight: 700; color: #9591C4;
    text-transform: uppercase; letter-spacing: .1em;
    margin: 16px 0 8px; display: flex; align-items: center; gap: 6px;
}

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: #fff;
    border-radius: 14px; padding: 5px;
    box-shadow: 0 2px 12px rgba(108,80,243,.08);
    border: 1.5px solid #EAE7FF;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px; padding: 8px 20px;
    font-weight: 700; font-size: 13px; color: #9591C4;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#6C50F3,#5840D6) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(108,80,243,.3);
}

/* ── 버튼 ── */
.stButton > button {
    background: linear-gradient(135deg,#6C50F3,#5840D6) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    padding: 9px 20px !important;
    box-shadow: 0 4px 14px rgba(108,80,243,.35) !important;
    font-size: 13px !important; letter-spacing: -.1px;
    transition: all .18s !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(108,80,243,.45) !important;
    transform: translateY(-1px) !important;
}

/* ── 셀렉트박스 / 멀티셀렉트 ── */
.stSelectbox > div > div, .stMultiSelect > div > div {
    border-color: #EAE7FF !important; border-radius: 12px !important;
    background: #fff !important;
}
.stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {
    border-color: #6C50F3 !important;
    box-shadow: 0 0 0 3px rgba(108,80,243,.12) !important;
}

/* ── 텍스트 입력 ── */
.stTextInput > div > div {
    border-color: #EAE7FF !important; border-radius: 12px !important;
}
.stTextInput > div > div:focus-within {
    border-color: #6C50F3 !important;
    box-shadow: 0 0 0 3px rgba(108,80,243,.12) !important;
}

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] { border-radius: 14px !important; overflow: hidden; }
.stDataFrame { background: #fff !important; border-radius: 14px !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #fff !important; border-radius: 12px !important;
    border: 1.5px solid #EAE7FF !important; font-weight: 700 !important; color: #18105C !important;
}

/* ── Divider ── */
hr { border-color: #EAE7FF !important; margin: 20px 0 !important; }

/* ── 헤더 배너 ── */
.dash-header {
    background: linear-gradient(135deg, #6C50F3 0%, #5840D6 100%);
    border-radius: 20px; padding: 26px 32px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(108,80,243,.25);
    display: flex; align-items: center; justify-content: space-between;
}

@media (max-width: 768px) { .block-container { padding: 1rem .75rem !important; } .kpi-grid { grid-template-columns: repeat(2,1fr) !important; } }
</style>
""", unsafe_allow_html=True)


# ── 헤더 ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div style="color:rgba(196,181,253,.9);font-size:12px;font-weight:700;letter-spacing:.1em;margin-bottom:5px;">
      TVING · 광고 성과 분석
    </div>
    <div style="color:#fff;font-size:26px;font-weight:800;letter-spacing:-.5px;">
      광고 성과 대시보드
    </div>
  </div>
  <div style="text-align:right;">
    <div style="color:rgba(196,181,253,.7);font-size:11px;font-weight:600;margin-bottom:3px;">마지막 업데이트</div>
    <div style="color:#fff;font-size:13px;font-weight:700;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── 유틸 ─────────────────────────────────────────────────────────────
def fmt_num(n, suffix=""):
    if pd.isna(n) or n == 0: return "-"
    n = float(n)
    if n >= 100_000_000: return f"{n/100_000_000:.1f}억{suffix}"
    if n >= 10_000:      return f"{n/10_000:.0f}만{suffix}"
    return f"{int(n):,}{suffix}"

def fmt_pct(n):
    if pd.isna(n): return "-"
    return f"{n:.2f}%"


# ── 데이터 ───────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(sheet_type: str) -> pd.DataFrame:
    import json as _json
    sheet_key = {"overall": "all"}.get(sheet_type, sheet_type)
    payload   = {"action": "read", "key": sheet_key}
    try:
        resp = requests.post(
            APPS_SCRIPT_URL,
            headers={"Content-Type": "text/plain"},
            data=_json.dumps(payload),
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("data", [])
        if not rows:
            g    = requests.get(f"{APPS_SCRIPT_URL}?type={sheet_key}", timeout=30)
            rows = g.json().get("data", [])
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

def parse_ad_unit(df):
    if "광고 단위" not in df.columns: return df
    split = df["광고 단위"].str.split("_", n=2, expand=True)
    df["플랫폼"] = split[0].str.strip()
    df["디바이스"] = split[1].str.strip() if 1 in split.columns else ""
    df["지면"]   = split[2].str.strip() if 2 in split.columns else ""
    return df

def to_numeric(df):
    for col in ["매체 집행 금액","노출수","클릭수","영상 25% 시청","영상 50% 시청","영상 75% 시청","영상 시청 완료"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


# ── 사이드바 필터 ────────────────────────────────────────────────────
def sidebar_filters(df, prefix):
    with st.sidebar:
        st.markdown("### 필터")
        opts = lambda col: sorted(df[col].dropna().unique().tolist()) if col in df.columns else []
        sel_month    = st.selectbox("월", ["전체"] + opts("월"), key=f"{prefix}_month")
        sel_platform = st.multiselect("플랫폼", opts("플랫폼"), key=f"{prefix}_platform", placeholder="전체")
        sel_device   = st.multiselect("디바이스", opts("디바이스"), key=f"{prefix}_device", placeholder="전체")
        sel_cat      = st.multiselect("업종(카테고리)", opts("카테고리"), key=f"{prefix}_cat", placeholder="전체")
        sel_brand    = st.multiselect("브랜드", opts("브랜드"), key=f"{prefix}_brand", placeholder="전체")
        sel_gender   = st.multiselect("성별", opts("성별"), key=f"{prefix}_gender", placeholder="전체")
        sel_age      = st.multiselect("나이", opts("나이"), key=f"{prefix}_age", placeholder="전체")

    f = df.copy()
    if sel_month != "전체": f = f[f["월"] == sel_month]
    if sel_platform: f = f[f["플랫폼"].isin(sel_platform)]
    if sel_device:   f = f[f["디바이스"].isin(sel_device)]
    if sel_cat:      f = f[f["카테고리"].isin(sel_cat)]
    if sel_brand:    f = f[f["브랜드"].isin(sel_brand)]
    if sel_gender:   f = f[f["성별"].isin(sel_gender)]
    if sel_age:      f = f[f["나이"].isin(sel_age)]
    return f


# ── 광고 상품 검색 ───────────────────────────────────────────────────
def product_filter(df, prefix=""):
    keyword = st.text_input(
        "캠페인 검색",
        placeholder="캠페인명 키워드 입력 (예: KBO, TOP20)",
        key=f"product_keyword_{prefix}",
    )
    search_col = next((c for c in ["디캠페인","캠페인 템플릿","캠페인"] if c in df.columns), None)
    if keyword and search_col:
        df = df[df[search_col].str.contains(keyword, case=False, na=False)]
        st.caption(f"'{keyword}' 포함 — {len(df):,}행")
    return df


# ── KPI HTML 카드 ────────────────────────────────────────────────────
def kpi_card_html(icon, label, value, sub, sub_class, color_class):
    return f"""
<div class="kpi-card {color_class}">
  <div class="kpi-ic" style="background:{'#EEE9FF' if color_class=='p' else '#FFF3EA' if color_class=='o' else '#E8FAFE' if color_class=='c' else '#EAFAF1' if color_class=='g' else '#FEF2F2'}">
    {icon}
  </div>
  <div class="kpi-lbl">{label}</div>
  <div class="kpi-val">{value}</div>
  <div class="kpi-sub {sub_class}">{sub}</div>
</div>"""

def kpi_section(df):
    spend = df["매체 집행 금액"].sum()
    imp   = df["노출수"].sum()
    clk   = df["클릭수"].sum()
    v25   = df.get("영상 25% 시청", pd.Series(dtype=float)).sum() if "영상 25% 시청" in df.columns else 0
    v50   = df.get("영상 50% 시청", pd.Series(dtype=float)).sum() if "영상 50% 시청" in df.columns else 0
    v75   = df.get("영상 75% 시청", pd.Series(dtype=float)).sum() if "영상 75% 시청" in df.columns else 0
    v100  = df["영상 시청 완료"].sum() if "영상 시청 완료" in df.columns else 0

    ctr    = round(clk  / imp  * 100, 2) if imp  > 0 else 0
    vtr100 = round(v100 / imp  * 100, 2) if imp  > 0 else 0
    cpm    = round(spend / imp  * 1000)  if imp  > 0 else 0
    cpc    = round(spend / clk)          if clk  > 0 else 0
    cpv100 = round(spend / v100)         if v100 > 0 else 0
    vtr75  = round(v75  / imp  * 100, 2) if imp  > 0 else 0
    vtr50  = round(v50  / imp  * 100, 2) if imp  > 0 else 0
    vtr25  = round(v25  / imp  * 100, 2) if imp  > 0 else 0

    # 볼륨 행
    st.markdown('<div class="kpi-group-title">📦 볼륨</div>', unsafe_allow_html=True)
    cards_vol = (
        kpi_card_html("💰", "집행 금액",  fmt_num(spend, "원"),  "전체 기간 합산", "neu", "p") +
        kpi_card_html("👁", "노출수",     fmt_num(imp),           "전체 기간 합산", "neu", "o") +
        kpi_card_html("🖱", "클릭수",     fmt_num(clk),           f"CTR {fmt_pct(ctr)}", "neu", "c") +
        kpi_card_html("🎬", "완료 시청수", fmt_num(v100),          f"VTR {fmt_pct(vtr100)}", "up" if vtr100 >= 20 else "neu", "g")
    )
    st.markdown(f'<div class="kpi-grid">{cards_vol}</div>', unsafe_allow_html=True)

    # VTR 행
    st.markdown('<div class="kpi-group-title">🎞 영상 시청률 (VTR)</div>', unsafe_allow_html=True)
    cards_vtr = (
        kpi_card_html("▶", "VTR 100%", fmt_pct(vtr100), "영상 완료 시청률", "up" if vtr100 >= 20 else "neu", "p") +
        kpi_card_html("▷", "VTR 75%",  fmt_pct(vtr75),  "75% 시청률", "neu", "p") +
        kpi_card_html("▷", "VTR 50%",  fmt_pct(vtr50),  "50% 시청률", "neu", "c") +
        kpi_card_html("▷", "VTR 25%",  fmt_pct(vtr25),  "25% 시청률", "neu", "c")
    )
    st.markdown(f'<div class="kpi-grid">{cards_vtr}</div>', unsafe_allow_html=True)

    # 단가 행
    st.markdown('<div class="kpi-group-title">💸 단가</div>', unsafe_allow_html=True)
    cards_cost = (
        kpi_card_html("📊", "CPM",      fmt_num(cpm, "원"),    "1천 노출당", "neu", "o") +
        kpi_card_html("🎯", "CPC",      fmt_num(cpc, "원"),    "클릭당 비용", "neu", "o") +
        kpi_card_html("🏁", "CPV 100%", fmt_num(cpv100, "원"), "완료시청당", "neu", "r") +
        kpi_card_html("📈", "CTR",      fmt_pct(ctr),          "클릭률", "up" if ctr >= 0.3 else "neu", "g")
    )
    st.markdown(f'<div class="kpi-grid">{cards_cost}</div>', unsafe_allow_html=True)


# ── 차트 기본 레이아웃 ───────────────────────────────────────────────
def _base_layout(height, t=45, b=10, l=10, r=10):
    return dict(
        margin=dict(t=t, b=b, l=l, r=r),
        height=height,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif",
                  color=TEXT_B),
        showlegend=False,
        coloraxis_showscale=False,
    )


# ── 차트 함수 ─────────────────────────────────────────────────────────
def donut_chart(df, group_col, value_col, title, color_map=None, max_slices=7, height=300):
    if group_col not in df.columns: return go.Figure()
    agg = df.groupby(group_col)[value_col].sum().reset_index()
    agg = agg.sort_values(value_col, ascending=False)
    if len(agg) > max_slices:
        top = agg.iloc[:max_slices].copy()
        etc = pd.DataFrame({group_col: ["기타"], value_col: [agg.iloc[max_slices:][value_col].sum()]})
        agg = pd.concat([top, etc], ignore_index=True)
    if agg.empty or agg[value_col].sum() == 0: return go.Figure()

    fig = px.pie(agg, names=group_col, values=value_col, title=title, hole=0.58,
                 color=group_col, color_discrete_map=color_map or {})
    fig.update_traces(
        textinfo="percent", textfont_size=11, textposition="outside",
        marker=dict(line=dict(color="white", width=2)),
    )
    layout = _base_layout(height, t=50, b=55)
    layout.update(
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
        title=dict(font=dict(size=13, color=TEXT_H)),
    )
    fig.update_layout(**layout)
    return fig

def hbar_chart(df, group_col, value_col, title, top_n=10):
    if group_col not in df.columns: return go.Figure()
    agg = df.groupby(group_col)[value_col].sum().reset_index()
    agg = agg.sort_values(value_col, ascending=False).head(top_n)
    agg = agg.sort_values(value_col, ascending=True)
    fig = px.bar(agg, x=value_col, y=group_col, orientation="h",
                 text_auto=".2s", color=value_col,
                 color_continuous_scale=[[0, PURPLE_LT], [0.5, PURPLE], [1, PURPLE_DARK]])
    fig.update_traces(marker_line_width=0)
    layout = _base_layout(max(300, top_n * 36))
    layout.update(xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=CHART_BG))
    fig.update_layout(**layout)
    return fig

def bar_chart(df, group_col, value_col, title, color_map=None):
    if group_col not in df.columns: return go.Figure()
    agg = df.groupby(group_col)[value_col].sum().reset_index().sort_values(value_col, ascending=False)
    fig = px.bar(agg, x=group_col, y=value_col, title=title,
                 color=value_col, text_auto=".2s",
                 color_continuous_scale=[[0, PURPLE_LT], [0.5, PURPLE], [1, PURPLE_DARK]])
    layout = _base_layout(320, t=45, b=60)
    layout.update(
        title=dict(font=dict(size=13, color=TEXT_H)),
        xaxis=dict(tickangle=-30, gridcolor=CHART_BG),
        yaxis=dict(gridcolor=GRID_COLOR),
    )
    fig.update_layout(**layout)
    return fig

def funnel_chart(df):
    stages = ["노출수","영상 25% 시청","영상 50% 시청","영상 75% 시청","영상 시청 완료"]
    labels = [s for s in stages if s in df.columns]
    values = [df[s].sum() for s in stages if s in df.columns]
    if not values: return go.Figure()
    fig = go.Figure(go.Funnel(
        y=labels, x=values,
        textinfo="value+percent initial",
        marker=dict(color=[PURPLE_DARK, PURPLE, "#8B5CF6", "#A78BFA", GREEN]),
        connector=dict(line=dict(color="rgba(0,0,0,0.06)", width=1)),
    ))
    layout = _base_layout(340, t=50, b=10)
    layout.update(title=dict(text="영상 시청 퍼널", font=dict(size=13, color=TEXT_H)))
    fig.update_layout(**layout)
    return fig

def insight_hbar(df, group_col, value_col, title, color_scale, top_n=None, key=""):
    if value_col == "수량":
        agg   = df.groupby(group_col).size().reset_index(name="수량")
        y_col = "수량"
    else:
        agg   = df.groupby(group_col)[value_col].sum().reset_index()
        y_col = value_col
    if top_n: agg = agg.sort_values(y_col, ascending=False).head(top_n)
    agg = agg.sort_values(y_col, ascending=True)
    fig = px.bar(agg, x=y_col, y=group_col, orientation="h", title=title,
                 text_auto=".2s" if value_col != "수량" else True,
                 color=y_col, color_continuous_scale=color_scale)
    layout = _base_layout(max(300, len(agg) * 30), t=45, b=10)
    layout.update(
        title=dict(font=dict(size=13, color=TEXT_H)),
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=CHART_BG),
    )
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, key=key)


# ── 이슈 감지 ────────────────────────────────────────────────────────
def detect_issues(df):
    issues = []
    if "광고 계정" not in df.columns: return issues
    by  = df.groupby("광고 계정").agg(imp=("노출수","sum"), clk=("클릭수","sum")).reset_index()
    by["ctr"] = by["clk"] / by["imp"].replace(0, pd.NA)
    avg = by["ctr"].mean()
    if avg and not pd.isna(avg):
        for acct in by[by["ctr"] < avg * 0.5]["광고 계정"].tolist():
            issues.append(f"[{acct}] CTR이 평균 대비 50% 미만 — 소재/타겟 점검 필요")
    for acct in by[by["imp"] == 0]["광고 계정"].tolist():
        issues.append(f"[{acct}] 노출수 0 — 캠페인 상태 확인 필요")
    return issues


# ── 전체 대시보드 ────────────────────────────────────────────────────
def page_overall():
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("🔄 새로고침", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with c2:
        st.caption(f"캐시 유효시간 1시간 · 로드: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    raw = load_data("overall")
    if raw.empty:
        st.warning("데이터가 없습니다. Apps Script URL을 확인하세요.")
        return

    df       = parse_ad_unit(to_numeric(raw))
    df       = product_filter(df, prefix="overall")
    filtered = sidebar_filters(df, "overall")
    if filtered.empty:
        st.info("필터 조건에 해당하는 데이터가 없습니다.")
        return

    # KPI
    st.markdown('<div class="sec-title">핵심 성과 지표</div>', unsafe_allow_html=True)
    kpi_section(filtered)

    st.divider()

    # 플랫폼 · 디바이스
    st.markdown('<div class="sec-title">플랫폼 · 디바이스 · 지면 비중</div>', unsafe_allow_html=True)
    metric = st.selectbox("기준 지표", ["노출수","매체 집행 금액","클릭수","영상 시청 완료"], key="pie_metric")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(donut_chart(filtered, "플랫폼",  metric, f"플랫폼별 {metric}",  PLATFORM_COLORS, height=300), use_container_width=True, key="ov_platform")
    with c2:
        st.plotly_chart(donut_chart(filtered, "디바이스", metric, f"디바이스별 {metric}", DEVICE_COLORS,   height=300), use_container_width=True, key="ov_device")
    with c3:
        st.plotly_chart(hbar_chart(filtered, "지면", metric, f"지면별 {metric}", top_n=8), use_container_width=True, key="ov_jimen")

    st.divider()

    # 인사이트
    st.markdown('<div class="sec-title">업종 · 상품 운영 비중</div>', unsafe_allow_html=True)
    cat_col  = next((c for c in filtered.columns if "카테고리" in c), None)
    prod_col = next((c for c in filtered.columns if "캠페인 템플릿" in c), None)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if cat_col:  insight_hbar(filtered, cat_col,  "수량",         "업종별 (수량)",     [[0,PURPLE_LT],[1,PURPLE_DARK]], key="i_cat_cnt")
    with c2:
        if prod_col: insight_hbar(filtered, prod_col, "수량",         "상품별 (수량 Top15)",[[0,PURPLE_LT],[1,PURPLE_DARK]], top_n=15, key="i_prod_cnt")
    with c3:
        if cat_col:  insight_hbar(filtered, cat_col,  "매체 집행 금액","업종별 (예산)",     [[0,"#99F6E4"],[1,"#0F766E"]], key="i_cat_spend")
    with c4:
        if prod_col: insight_hbar(filtered, prod_col, "매체 집행 금액","상품별 (예산 Top15)",[[0,"#99F6E4"],[1,"#0F766E"]], top_n=15, key="i_prod_spend")

    st.divider()

    # 퍼널 · 업종별
    st.markdown('<div class="sec-title">영상 시청 퍼널 · 업종별 성과</div>', unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    with c4:
        st.plotly_chart(funnel_chart(filtered), use_container_width=True, key="ov_funnel")
    with c5:
        cat_metric = st.selectbox("업종별 지표", ["노출수","매체 집행 금액","클릭수"], key="cat_metric")
        st.plotly_chart(bar_chart(filtered, "카테고리", cat_metric, f"업종별 {cat_metric}"), use_container_width=True, key="ov_cat")

    st.divider()

    # 데모
    st.markdown('<div class="sec-title">데모 분석 (나이 · 성별)</div>', unsafe_allow_html=True)
    demo_metric = st.selectbox("데모 지표", ["노출수","클릭수","매체 집행 금액"], key="demo_metric")
    c5, c6 = st.columns([2, 1])
    with c5:
        st.plotly_chart(bar_chart(filtered, "나이", demo_metric, f"나이별 {demo_metric}"), use_container_width=True, key="ov_age")
    with c6:
        st.plotly_chart(donut_chart(filtered, "성별", demo_metric, f"성별 {demo_metric}", height=300), use_container_width=True, key="ov_gender")

    st.divider()

    # 월별 트렌드
    if "월" in filtered.columns and "플랫폼" in filtered.columns:
        st.markdown('<div class="sec-title">월별 트렌드</div>', unsafe_allow_html=True)
        trend_metric = st.selectbox("트렌드 지표", ["노출수","매체 집행 금액","클릭수"], key="trend_metric")
        trend = filtered.groupby(["월","플랫폼"])[trend_metric].sum().reset_index()
        fig   = px.line(trend, x="월", y=trend_metric, color="플랫폼",
                        color_discrete_map=PLATFORM_COLORS, markers=True,
                        title=f"월별 {trend_metric} (플랫폼별)")
        fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
        layout = _base_layout(320, t=45, b=30)
        layout.update(
            showlegend=True,
            legend=dict(orientation="h", y=-0.15),
            title=dict(font=dict(size=13, color=TEXT_H)),
            xaxis=dict(gridcolor=GRID_COLOR),
            yaxis=dict(gridcolor=GRID_COLOR),
        )
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True, key="ov_trend")

    st.divider()

    with st.expander("원본 데이터 보기"):
        show = [c for c in ["월","브랜드","카테고리","광고 계정","플랫폼","디바이스","지면",
                             "나이","성별","캠페인","매체 집행 금액","노출수","클릭수","영상 시청 완료"]
                if c in filtered.columns]
        st.dataframe(filtered[show], use_container_width=True, hide_index=True)


# ── 팀 대시보드 ──────────────────────────────────────────────────────
def page_team():
    st.markdown('<div class="sec-title">팀 운영 대시보드</div>', unsafe_allow_html=True)
    st.caption("데일리 모니터링 — 예산 소진 및 성과 이슈 체크")

    c1, c2 = st.columns([1, 6])
    with c1:
        if st.button("🔄 새로고침", use_container_width=True, key="team_refresh"):
            st.cache_data.clear()
            st.rerun()
    with c2:
        st.caption(f"마지막 로드: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    raw = load_data("overall")
    if raw.empty:
        st.warning("데이터가 없습니다.")
        return

    df = parse_ad_unit(to_numeric(raw))
    if TEAM_ACCOUNTS:
        df = df[df["광고 계정"].isin(TEAM_ACCOUNTS)]

    issues = detect_issues(df)
    if issues:
        st.error("⚠️ 성과 이슈 감지")
        for issue in issues:
            st.markdown(f"- {issue}")

    accounts = sorted(df["광고 계정"].dropna().unique().tolist()) if "광고 계정" in df.columns else []
    sel = st.multiselect("모니터링 계정", accounts, placeholder="전체 계정", key="team_acct")
    if sel: df = df[df["광고 계정"].isin(sel)]
    filtered = sidebar_filters(df, "team")

    st.divider()
    st.markdown('<div class="sec-title">계정별 성과 요약</div>', unsafe_allow_html=True)
    if "광고 계정" not in filtered.columns or filtered.empty:
        st.info("데이터가 없습니다.")
        return

    summary = (filtered.groupby("광고 계정")
               .agg(집행금액=("매체 집행 금액","sum"), 노출수=("노출수","sum"),
                    클릭수=("클릭수","sum"), 완료시청=("영상 시청 완료","sum"))
               .reset_index())
    imp = summary["노출수"].replace(0, pd.NA)
    summary["CTR(%)"]      = (summary["클릭수"]  / imp * 100).round(2)
    summary["VTR 100%(%)"] = (summary["완료시청"] / imp * 100).round(2)
    summary["CPM"]         = (summary["집행금액"] / imp * 1000).round(0)
    summary["CPC"]         = (summary["집행금액"] / summary["클릭수"].replace(0, pd.NA)).round(0)
    summary = summary.sort_values("집행금액", ascending=False)
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.divider()
    if "월" in filtered.columns:
        st.markdown('<div class="sec-title">월별 계정 집행 금액</div>', unsafe_allow_html=True)
        monthly = filtered.groupby(["월","광고 계정"])["매체 집행 금액"].sum().reset_index()
        fig = px.bar(monthly, x="월", y="매체 집행 금액", color="광고 계정",
                     barmode="stack", title="월별 계정별 집행 금액")
        layout = _base_layout(350, t=45, b=30)
        layout.update(showlegend=True, title=dict(font=dict(size=13, color=TEXT_H)))
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True, key="team_monthly")

    st.divider()
    st.markdown('<div class="sec-title">플랫폼 · 디바이스 현황</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(donut_chart(filtered, "플랫폼",  "노출수", "플랫폼별 노출수", PLATFORM_COLORS), use_container_width=True, key="tm_platform")
    with c2:
        st.plotly_chart(donut_chart(filtered, "디바이스", "노출수", "디바이스별 노출수", DEVICE_COLORS),  use_container_width=True, key="tm_device")

    st.divider()
    st.markdown('<div class="sec-title">계정별 CTR · VTR 비교</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        fig_ctr = px.bar(summary.sort_values("CTR(%)"), x="광고 계정", y="CTR(%)",
                         color="CTR(%)", color_continuous_scale=[[0,PURPLE_LT],[1,PURPLE_DARK]], text_auto=".2f")
        layout = _base_layout(300, t=45, b=60)
        layout.update(title=dict(text="계정별 CTR", font=dict(size=13, color=TEXT_H)), xaxis=dict(tickangle=-30))
        fig_ctr.update_layout(**layout)
        st.plotly_chart(fig_ctr, use_container_width=True, key="team_ctr")
    with c4:
        fig_vtr = px.bar(summary.sort_values("VTR 100%(%)"), x="광고 계정", y="VTR 100%(%)",
                         color="VTR 100%(%)", color_continuous_scale=[[0,"#99F6E4"],[1,"#0F766E"]], text_auto=".2f")
        layout = _base_layout(300, t=45, b=60)
        layout.update(title=dict(text="계정별 VTR(100%)", font=dict(size=13, color=TEXT_H)), xaxis=dict(tickangle=-30))
        fig_vtr.update_layout(**layout)
        st.plotly_chart(fig_vtr, use_container_width=True, key="team_vtr")


# ── 메인 ────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 전체 대시보드", "👥 팀 운영"])
with tab1:
    page_overall()
with tab2:
    page_team()
