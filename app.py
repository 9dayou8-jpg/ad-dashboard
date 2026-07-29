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
    initial_sidebar_state="collapsed",
)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzf8yCiR_Vx0VTVbGTgAPguH08M1r7FtPaF_g3KfbY2GJWUJSd1HihLuergbrylptrYfw/exec"

PLATFORM_COLORS = {"TVING": "#6C50F3", "Wavve": "#06B6D4"}
DEVICE_COLORS   = {"CTV": "#F59E0B", "iOS": "#10B981", "Android": "#EF4444", "Web": "#3B82F6"}

PURPLE      = "#6C50F3"
PURPLE_DARK = "#5840D6"
PURPLE_LT   = "#EEE9FF"
TEXT_H      = "#18105C"
TEXT_B      = "#4B4578"
TEXT_SUB    = "#9591C4"
CHART_BG    = "rgba(0,0,0,0)"
GRID_COLOR  = "rgba(108,80,243,0.08)"

# ── 폰트 로드 (별도 호출)
st.markdown(
    '<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" rel="stylesheet">',
    unsafe_allow_html=True,
)

# ── 커스텀 HTML 요소 CSS (별도 호출 — <link>와 분리 필수)
st.markdown("""<style>
* { font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', 'Segoe UI', sans-serif !important; }

/* 커스텀 헤더 배너 */
.dash-header {
    background: linear-gradient(135deg, #6C50F3, #5840D6);
    border-radius: 20px; padding: 26px 32px; margin-bottom: 8px;
    box-shadow: 0 8px 32px rgba(108,80,243,.25);
    display: flex; align-items: center; justify-content: space-between;
}

/* 커스텀 KPI 카드 그리드 */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin: 4px 0 12px; }
.kpi-card {
    background: #fff; border-radius: 18px; padding: 18px 18px 16px;
    box-shadow: 0 4px 20px rgba(108,80,243,.09); border: 1.5px solid #EAE7FF;
    position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute; bottom: 0; left: 16px; right: 16px;
    height: 3px; border-radius: 3px 3px 0 0;
}
.kpi-card.p::after { background: linear-gradient(90deg,#6C50F3,#A78BFA); }
.kpi-card.o::after { background: linear-gradient(90deg,#F97316,#FB923C); }
.kpi-card.c::after { background: linear-gradient(90deg,#06B6D4,#22D3EE); }
.kpi-card.g::after { background: linear-gradient(90deg,#22C55E,#4ADE80); }
.kpi-card.r::after { background: linear-gradient(90deg,#EF4444,#F87171); }
.kpi-ic { width:36px; height:36px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:16px; margin-bottom:10px; }
.kpi-lbl { font-size:10px; font-weight:700; color:#9591C4; text-transform:uppercase; letter-spacing:.07em; margin-bottom:4px; }
.kpi-val { font-size:22px; font-weight:800; color:#18105C; letter-spacing:-.7px; font-variant-numeric:tabular-nums; }
.kpi-sub { font-size:10px; font-weight:600; margin-top:5px; }
.kpi-sub.up { color:#22C55E; } .kpi-sub.down { color:#EF4444; } .kpi-sub.neu { color:#9591C4; }

/* 섹션 타이틀 */
.sec-title {
    font-size:15px; font-weight:800; color:#18105C;
    margin:28px 0 14px; padding:0; display:flex; align-items:center; gap:8px; letter-spacing:-.3px;
}
.sec-title::after { content:''; flex:1; height:1.5px; background:linear-gradient(90deg,#EAE7FF,transparent); border-radius:2px; }

/* KPI 그룹 제목 */
.kpi-group { font-size:11px; font-weight:700; color:#9591C4; text-transform:uppercase; letter-spacing:.1em; margin:20px 0 8px; }

/* 고정 필터 바 */
.filter-bar {
    position: sticky; top: 2.875rem; z-index: 999;
    background: #F4F5FF; padding: 10px 0 6px;
    border-bottom: 1.5px solid #EAE7FF; margin-bottom: 12px;
}

@media (max-width:768px) { .kpi-grid { grid-template-columns:repeat(2,1fr) !important; } }
</style>
""", unsafe_allow_html=True)


# ── 헤더 ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div style="color:rgba(196,181,253,.85);font-size:12px;font-weight:700;letter-spacing:.12em;margin-bottom:5px;">TVING · 광고 성과 분석</div>
    <div style="color:#fff;font-size:26px;font-weight:800;letter-spacing:-.5px;">광고 성과 대시보드</div>
  </div>
  <div style="text-align:right;">
    <div style="color:rgba(196,181,253,.7);font-size:11px;margin-bottom:3px;">마지막 업데이트</div>
    <div style="color:#fff;font-size:13px;font-weight:700;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── 유틸 ──────────────────────────────────────────────────────────────
def fmt_num(n, suffix=""):
    if pd.isna(n) or n == 0: return "-"
    n = float(n)
    if n >= 100_000_000: return f"{n/100_000_000:.1f}억{suffix}"
    if n >= 10_000:      return f"{n/10_000:.0f}만{suffix}"
    return f"{int(n):,}{suffix}"

def fmt_pct(n):
    if pd.isna(n): return "-"
    return f"{n:.2f}%"


# ── 데이터 로드 ────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    import json as _json
    payload = {"action": "read", "key": "all"}
    try:
        resp = requests.post(
            APPS_SCRIPT_URL,
            headers={"Content-Type": "text/plain"},
            data=_json.dumps(payload),
            timeout=60,
        )
        resp.raise_for_status()
        body = resp.json()
        rows = body.get("data", [])
        if not rows:
            # 상태 디버그용으로 원본 응답 저장
            st.session_state["_api_debug"] = body
        return pd.DataFrame(rows)
    except Exception as e:
        st.session_state["_api_debug"] = str(e)
        return pd.DataFrame()

def parse_ad_unit(df):
    if "광고 단위" not in df.columns: return df
    split = df["광고 단위"].str.split("_", n=2, expand=True)
    df["플랫폼"] = split[0].str.strip()
    df["디바이스"] = split[1].str.strip() if 1 in split.columns else ""
    df["지면"]    = split[2].str.strip() if 2 in split.columns else ""
    return df

def to_numeric(df):
    for col in ["매체 집행 금액","노출수","클릭수","영상 25% 시청","영상 50% 시청","영상 75% 시청","영상 시청 완료"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


# ── 고정 필터 바 ───────────────────────────────────────────────────────
def inline_filters(df):
    opts = lambda col: sorted(df[col].dropna().unique().tolist()) if col in df.columns else []

    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1: sel_month    = st.selectbox("월",    ["전체"] + opts("월"),        label_visibility="collapsed")
    with c2: sel_platform = st.multiselect("플랫폼", opts("플랫폼"),             placeholder="플랫폼", label_visibility="collapsed")
    with c3: sel_device   = st.multiselect("디바이스", opts("디바이스"),         placeholder="디바이스", label_visibility="collapsed")
    with c4: sel_cat      = st.multiselect("업종",  opts("카테고리"),            placeholder="업종", label_visibility="collapsed")
    with c5: sel_brand    = st.multiselect("브랜드", opts("브랜드"),             placeholder="브랜드", label_visibility="collapsed")
    with c6: sel_gender   = st.multiselect("성별",  opts("성별"),               placeholder="성별", label_visibility="collapsed")
    with c7: sel_age      = st.multiselect("나이",  opts("나이"),               placeholder="나이", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    f = df.copy()
    if sel_month != "전체": f = f[f["월"] == sel_month]
    if sel_platform: f = f[f["플랫폼"].isin(sel_platform)]
    if sel_device:   f = f[f["디바이스"].isin(sel_device)]
    if sel_cat:      f = f[f["카테고리"].isin(sel_cat)]
    if sel_brand:    f = f[f["브랜드"].isin(sel_brand)]
    if sel_gender:   f = f[f["성별"].isin(sel_gender)]
    if sel_age:      f = f[f["나이"].isin(sel_age)]
    return f


# ── 캠페인 검색 ────────────────────────────────────────────────────────
def product_filter(df):
    keyword = st.text_input("🔎 캠페인 검색", placeholder="캠페인명 키워드 입력")
    col = next((c for c in ["디캠페인","캠페인 템플릿","캠페인"] if c in df.columns), None)
    if keyword and col:
        df = df[df[col].str.contains(keyword, case=False, na=False)]
        st.caption(f"'{keyword}' — {len(df):,}행")
    return df


# ── KPI HTML 카드 ──────────────────────────────────────────────────────
def kpi_card(icon, bg, label, value, sub, sub_cls, color_cls):
    return f"""<div class="kpi-card {color_cls}">
  <div class="kpi-ic" style="background:{bg}">{icon}</div>
  <div class="kpi-lbl">{label}</div>
  <div class="kpi-val">{value}</div>
  <div class="kpi-sub {sub_cls}">{sub}</div>
</div>"""

def kpi_section(df):
    spend = df["매체 집행 금액"].sum()
    imp   = df["노출수"].sum()
    clk   = df["클릭수"].sum()
    v25   = df["영상 25% 시청"].sum()  if "영상 25% 시청"  in df.columns else 0
    v50   = df["영상 50% 시청"].sum()  if "영상 50% 시청"  in df.columns else 0
    v75   = df["영상 75% 시청"].sum()  if "영상 75% 시청"  in df.columns else 0
    v100  = df["영상 시청 완료"].sum() if "영상 시청 완료" in df.columns else 0

    ctr    = clk  / imp  * 100 if imp  > 0 else 0
    vtr100 = v100 / imp  * 100 if imp  > 0 else 0
    vtr75  = v75  / imp  * 100 if imp  > 0 else 0
    vtr50  = v50  / imp  * 100 if imp  > 0 else 0
    vtr25  = v25  / imp  * 100 if imp  > 0 else 0
    cpm    = spend / imp  * 1000 if imp  > 0 else 0
    cpc    = spend / clk         if clk  > 0 else 0
    cpv100 = spend / v100        if v100 > 0 else 0

    st.markdown('<div class="kpi-group">📦 볼륨</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi_card("💰","#EEE9FF","집행 금액", fmt_num(spend,"원"), "전체 기간 합산","neu","p") +
        kpi_card("👁","#FFF3EA","노출수",    fmt_num(imp),        "전체 기간 합산","neu","o") +
        kpi_card("🖱","#E8FAFE","클릭수",    fmt_num(clk),        f"CTR {fmt_pct(ctr)}","neu","c") +
        kpi_card("🎬","#EAFAF1","완료 시청", fmt_num(v100),       f"VTR {fmt_pct(vtr100)}","up" if vtr100>=20 else "neu","g") +
    '</div>', unsafe_allow_html=True)

    st.markdown('<div class="kpi-group">🎞 영상 시청률 (VTR)</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi_card("▶","#EEE9FF","VTR 100%", fmt_pct(vtr100), "완료 시청률","up" if vtr100>=20 else "neu","p") +
        kpi_card("▷","#EEE9FF","VTR 75%",  fmt_pct(vtr75),  "75% 시청률","neu","p") +
        kpi_card("▷","#E8FAFE","VTR 50%",  fmt_pct(vtr50),  "50% 시청률","neu","c") +
        kpi_card("▷","#E8FAFE","VTR 25%",  fmt_pct(vtr25),  "25% 시청률","neu","c") +
    '</div>', unsafe_allow_html=True)

    st.markdown('<div class="kpi-group">💸 단가</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi_card("📊","#FFF3EA","CPM",      fmt_num(round(cpm),"원"),   "1천 노출당","neu","o") +
        kpi_card("🎯","#FFF3EA","CPC",      fmt_num(round(cpc),"원"),   "클릭당 비용","neu","o") +
        kpi_card("🏁","#FEF2F2","CPV 100%", fmt_num(round(cpv100),"원"),"완료시청당","neu","r") +
        kpi_card("📈","#EAFAF1","CTR",      fmt_pct(ctr),               "클릭률","up" if ctr>=0.3 else "neu","g") +
    '</div>', unsafe_allow_html=True)


# ── 차트 기본 레이아웃 ─────────────────────────────────────────────────
def _layout(height, t=45, b=10, l=10, r=10):
    return dict(
        margin=dict(t=t,b=b,l=l,r=r), height=height,
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(family="Pretendard,'Apple SD Gothic Neo','Malgun Gothic',sans-serif", color=TEXT_B),
        showlegend=False, coloraxis_showscale=False,
    )


# ── 차트 함수 ──────────────────────────────────────────────────────────
def donut(df, gcol, vcol, title, cmap=None, max_sl=7, h=300):
    if gcol not in df.columns: return go.Figure()
    agg = df.groupby(gcol)[vcol].sum().reset_index().sort_values(vcol, ascending=False)
    if len(agg) > max_sl:
        top = agg.iloc[:max_sl].copy()
        etc = pd.DataFrame({gcol:["기타"], vcol:[agg.iloc[max_sl:][vcol].sum()]})
        agg = pd.concat([top, etc], ignore_index=True)
    if agg.empty or agg[vcol].sum() == 0: return go.Figure()
    fig = px.pie(agg, names=gcol, values=vcol, title=title, hole=0.58,
                 color=gcol, color_discrete_map=cmap or {})
    fig.update_traces(textinfo="percent", textfont_size=11, textposition="outside",
                      marker=dict(line=dict(color="white", width=2)))
    lay = _layout(h, t=50, b=55)
    lay.update(showlegend=True, legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
               title=dict(font=dict(size=13, color=TEXT_H)))
    fig.update_layout(**lay)
    return fig

def hbar(df, gcol, vcol, title, top_n=10):
    if gcol not in df.columns: return go.Figure()
    agg = df.groupby(gcol)[vcol].sum().reset_index()
    agg = agg.sort_values(vcol, ascending=False).head(top_n).sort_values(vcol, ascending=True)
    fig = px.bar(agg, x=vcol, y=gcol, orientation="h", text_auto=".2s",
                 color=vcol, color_continuous_scale=[[0,PURPLE_LT],[0.5,PURPLE],[1,PURPLE_DARK]])
    fig.update_traces(marker_line_width=0)
    lay = _layout(max(300, top_n*36))
    lay.update(xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=CHART_BG))
    fig.update_layout(**lay)
    return fig

def vbar(df, gcol, vcol, title):
    if gcol not in df.columns: return go.Figure()
    agg = df.groupby(gcol)[vcol].sum().reset_index().sort_values(vcol, ascending=False)
    fig = px.bar(agg, x=gcol, y=vcol, title=title, color=vcol, text_auto=".2s",
                 color_continuous_scale=[[0,PURPLE_LT],[0.5,PURPLE],[1,PURPLE_DARK]])
    lay = _layout(320, t=45, b=60)
    lay.update(title=dict(font=dict(size=13, color=TEXT_H)),
               xaxis=dict(tickangle=-30, gridcolor=CHART_BG), yaxis=dict(gridcolor=GRID_COLOR))
    fig.update_layout(**lay)
    return fig

def funnel(df):
    stages = ["노출수","영상 25% 시청","영상 50% 시청","영상 75% 시청","영상 시청 완료"]
    labels = [s for s in stages if s in df.columns]
    values = [df[s].sum() for s in labels]
    if not values: return go.Figure()
    fig = go.Figure(go.Funnel(
        y=labels, x=values, textinfo="value+percent initial",
        marker=dict(color=[PURPLE_DARK, PURPLE, "#8B5CF6", "#A78BFA", "#22C55E"]),
        connector=dict(line=dict(color="rgba(0,0,0,0.06)", width=1)),
    ))
    lay = _layout(340, t=50, b=10)
    lay.update(title=dict(text="영상 시청 퍼널", font=dict(size=13, color=TEXT_H)))
    fig.update_layout(**lay)
    return fig

def insight_hbar(df, gcol, vcol, title, cscale, top_n=None, key=""):
    if vcol == "수량":
        agg   = df.groupby(gcol).size().reset_index(name="수량")
        ycol  = "수량"
    else:
        agg   = df.groupby(gcol)[vcol].sum().reset_index()
        ycol  = vcol
    if top_n: agg = agg.sort_values(ycol, ascending=False).head(top_n)
    agg = agg.sort_values(ycol, ascending=True)
    fig = px.bar(agg, x=ycol, y=gcol, orientation="h", title=title,
                 text_auto=".2s" if vcol != "수량" else True, color=ycol, color_continuous_scale=cscale)
    lay = _layout(max(300, len(agg)*30), t=45, b=10)
    lay.update(title=dict(font=dict(size=13, color=TEXT_H)),
               xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=CHART_BG))
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True, key=key)


# ── 메인 ──────────────────────────────────────────────────────────────
if st.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

raw = load_data()
if raw.empty:
    st.warning("데이터가 없습니다.")
    debug = st.session_state.get("_api_debug")
    if debug:
        with st.expander("연결 디버그 정보 (개발자용)"):
            st.json(debug) if isinstance(debug, dict) else st.code(str(debug))
    st.info("👉 원인: ① all 시트에 데이터가 없거나 ② Apps Script가 응답하지 않는 경우입니다.")
    st.stop()

df       = parse_ad_unit(to_numeric(raw))
filtered = inline_filters(df)

if filtered.empty:
    st.info("필터 조건에 해당하는 데이터가 없습니다.")
    st.stop()

cat_col  = next((c for c in filtered.columns if "카테고리" in c), None)
prod_col = next((c for c in filtered.columns if "캠페인 템플릿" in c), None)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "01  KPI 요약", "02  채널 분석", "03  업종·상품", "04  데모", "05  원본 데이터"
])

# ── 탭1: KPI 요약 + 월별 트렌드 ─────────────────────────────────────
with tab1:
    keyword = st.text_input("🔎 캠페인 검색", placeholder="캠페인명 키워드 입력", key="kw")
    col = next((c for c in ["디캠페인","캠페인 템플릿","캠페인"] if c in filtered.columns), None)
    f1 = filtered[filtered[col].str.contains(keyword, case=False, na=False)] if keyword and col else filtered
    if keyword and col: st.caption(f"'{keyword}' — {len(f1):,}행")

    st.markdown('<div class="sec-title">핵심 성과 지표</div>', unsafe_allow_html=True)
    kpi_section(f1)

    st.divider()
    st.markdown('<div class="sec-title">월별 트렌드</div>', unsafe_allow_html=True)
    if "월" in f1.columns and "플랫폼" in f1.columns:
        tm = st.selectbox("트렌드 지표", ["노출수","매체 집행 금액","클릭수"], key="tm")
        trend = f1.groupby(["월","플랫폼"])[tm].sum().reset_index()
        fig   = px.line(trend, x="월", y=tm, color="플랫폼",
                        color_discrete_map=PLATFORM_COLORS, markers=True, title=f"월별 {tm}")
        fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
        lay = _layout(340, t=45, b=30)
        lay.update(showlegend=True, legend=dict(orientation="h", y=-0.15),
                   title=dict(font=dict(size=13, color=TEXT_H)),
                   xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR))
        fig.update_layout(**lay)
        st.plotly_chart(fig, use_container_width=True, key="tr")

# ── 탭2: 채널 분석 ───────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-title">플랫폼 · 디바이스 · 지면 비중</div>', unsafe_allow_html=True)
    metric = st.selectbox("기준 지표", ["노출수","매체 집행 금액","클릭수","영상 시청 완료"], key="pie_m")
    c1, c2, c3 = st.columns(3)
    with c1: st.plotly_chart(donut(filtered,"플랫폼",metric,f"플랫폼별 {metric}",PLATFORM_COLORS,h=320), use_container_width=True, key="p1")
    with c2: st.plotly_chart(donut(filtered,"디바이스",metric,f"디바이스별 {metric}",DEVICE_COLORS,h=320), use_container_width=True, key="p2")
    with c3: st.plotly_chart(hbar(filtered,"지면",metric,f"지면별 {metric}",top_n=8), use_container_width=True, key="p3")

# ── 탭3: 업종·상품 ───────────────────────────────────────────────────
with tab3:
    METRICS = {
        "수량 (건수)":      {"col": "수량",            "is_count": True},
        "집행 금액":        {"col": "매체 집행 금액",   "is_count": False},
        "노출수":           {"col": "노출수",           "is_count": False},
        "클릭수":           {"col": "클릭수",           "is_count": False},
        "영상 시청 완료":   {"col": "영상 시청 완료",   "is_count": False},
    }
    sel_metric = st.selectbox("지표 선택", list(METRICS.keys()), key="cat_metric_sel")
    m_col    = METRICS[sel_metric]["col"]
    m_count  = METRICS[sel_metric]["is_count"]

    # 업종별 (퍼플)
    st.markdown('<div class="sec-title">업종별 분석</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if cat_col:
            insight_hbar(filtered, cat_col, m_col if not m_count else "수량",
                         f"업종별 · {sel_metric} 기준",
                         [[0,PURPLE_LT],[1,PURPLE_DARK]], key="i1")
    with c2:
        # 항상 집행금액과 비교 (지표가 집행금액이 아닐 때만 추가 표시)
        if cat_col and m_col != "매체 집행 금액":
            insight_hbar(filtered, cat_col, "매체 집행 금액",
                         "업종별 · 집행 금액 기준",
                         [[0,PURPLE_LT],[1,PURPLE_DARK]], key="i3")
        elif cat_col:
            insight_hbar(filtered, cat_col, "노출수",
                         "업종별 · 노출수 기준",
                         [[0,PURPLE_LT],[1,PURPLE_DARK]], key="i3b")

    st.divider()

    # 상품별 (청록)
    st.markdown('<div class="sec-title">상품별 분석 (Top 15)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if prod_col:
            insight_hbar(filtered, prod_col, m_col if not m_count else "수량",
                         f"상품별 · {sel_metric} 기준",
                         [[0,"#CCFBF1"],[1,"#0F766E"]], top_n=15, key="i2")
    with c2:
        if prod_col and m_col != "매체 집행 금액":
            insight_hbar(filtered, prod_col, "매체 집행 금액",
                         "상품별 · 집행 금액 기준",
                         [[0,"#CCFBF1"],[1,"#0F766E"]], top_n=15, key="i4")
        elif prod_col:
            insight_hbar(filtered, prod_col, "노출수",
                         "상품별 · 노출수 기준",
                         [[0,"#CCFBF1"],[1,"#0F766E"]], top_n=15, key="i4b")

    st.divider()
    st.markdown('<div class="sec-title">영상 시청 퍼널 · 업종별 성과</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(funnel(filtered), use_container_width=True, key="fn")
    with c2:
        cm = st.selectbox("업종별 지표", ["노출수","매체 집행 금액","클릭수"], key="cm")
        st.plotly_chart(vbar(filtered,"카테고리",cm,f"업종별 {cm}"), use_container_width=True, key="cv")

# ── 탭4: 데모 ────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-title">데모 분석 (나이 · 성별)</div>', unsafe_allow_html=True)
    dm = st.selectbox("데모 지표", ["노출수","클릭수","매체 집행 금액"], key="dm")
    c1, c2 = st.columns([2, 1])
    with c1: st.plotly_chart(vbar(filtered,"나이",dm,f"나이별 {dm}"), use_container_width=True, key="da")
    with c2: st.plotly_chart(donut(filtered,"성별",dm,f"성별 {dm}",h=300), use_container_width=True, key="dg")

# ── 탭5: 원본 데이터 ─────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="sec-title">원본 데이터</div>', unsafe_allow_html=True)
    show = [c for c in ["월","브랜드","카테고리","광고 계정","플랫폼","디바이스","지면",
                         "나이","성별","캠페인","매체 집행 금액","노출수","클릭수","영상 시청 완료"]
            if c in filtered.columns]
    st.dataframe(filtered[show], use_container_width=True, hide_index=True)
