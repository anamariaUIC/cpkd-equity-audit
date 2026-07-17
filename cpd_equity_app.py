import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(
    page_title="Chicago Park District Equity Analysis",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

  .main { background-color: #f0f4f8; }
  .block-container { padding: 2rem 2.5rem 3rem; max-width: 1400px; }

  /* Hero */
  .hero { background: #fff; border: 1px solid #222; border-radius: 12px;
          padding: 2.5rem 2.5rem 2rem; margin-bottom: 2rem; }
  .hero-eyebrow { font-size: 11px; letter-spacing: .15em; text-transform: uppercase;
                  color: #1a4480; margin-bottom: 8px; font-weight: 500; }
  .hero-title { font-size: clamp(28px, 4vw, 44px); font-weight: 600;
                line-height: 1.15; color: #0f2b52; margin: 0 0 16px; }
  .hero-title span { color: #1a4480; }
  .hero-sub { font-size: 15px; color: #999; line-height: 1.7; max-width: 780px; margin: 0; }

  /* KPI cards */
  .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
              margin-bottom: 1.5rem; }
  .kpi { background: #fff; border: 1px solid #222; border-radius: 10px; padding: 1.2rem; }
  .kpi-val { font-size: 28px; font-weight: 600; margin: 0 0 4px; font-family: 'IBM Plex Mono'; }
  .kpi-lbl { font-size: 12px; color: #4a5e78; margin: 0; }
  .kpi-note { font-size: 11px; color: #555; margin: 4px 0 0; }
  .kpi-red .kpi-val { color: #b06200; }
  .kpi-blue .kpi-val { color: #1b6ca8; }
  .kpi-amber .kpi-val { color: #1a6b3c; }

  /* Callout boxes */
  .callout { border-radius: 8px; padding: 14px 16px;
             font-size: 13px; line-height: 1.65; margin: 1rem 0; }
  .callout-red { background: #fef7ee; border-left: 3px solid #b06200; color: #3d1f00; }
  .callout-blue { background: #eef3fb; border-left: 3px solid #1a4480; color: #0f2b52; }
  .callout-amber { background: #edfaf3; border-left: 3px solid #1a6b3c; color: #0a2d1a; }
  .callout b { color: #0f2b52; font-weight: 600; }

  /* Section headers */
  .sec-head { font-size: 16px; font-weight: 500; color: #0f2b52;
              margin: 0 0 4px; padding: 0; }
  .sec-sub { font-size: 12px; color: #777; margin: 0 0 1rem; line-height: 1.6; }

  /* Finding boxes */
  .finding { background: #fff; border: 1px solid #d0dcea; border-radius: 10px;
             padding: 1.25rem; margin-bottom: .75rem; }
  .finding-num { font-size: 11px; color: #1a4480; letter-spacing: .1em;
                 text-transform: uppercase; margin-bottom: 4px; font-weight: 500; }
  .finding-title { font-size: 14px; font-weight: 500; color: #0f2b52; margin-bottom: 6px; }
  .finding-body { font-size: 13px; color: #999; line-height: 1.65; margin: 0; }
  .finding-body b { color: #0f2b52; }

  /* Source footer */
  .src { font-size: 11px; color: #444; margin-top: 8px; line-height: 1.6; }

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent;
                                       border-bottom: 1px solid #222; }
  .stTabs [data-baseweb="tab"] { background: transparent; border: none;
    padding: 8px 16px; font-size: 13px; color: #777;
    border-bottom: 2px solid transparent; }
  .stTabs [aria-selected="true"] { color: #0f2b52 !important;
    border-bottom-color: #1a4480 !important; }
  .stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 0; }
  .stTabs [data-baseweb="tab-border"] { display: none; }

  div[data-testid="metric-container"] { display: none; }
  footer { display: none; }
  #MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme (light — blues/greens) ───────────────────────────────────────
PLOT_BG   = "#ffffff"
PAPER_BG  = "#ffffff"
GRID_CLR  = "#e8edf5"
AXIS_CLR  = "#4a5e78"
FONT_CLR  = "#0f2b52"
RED       = "#b06200"   # amber/burnt-orange replaces red for disinvested parks
BLUE      = "#1a4480"   # dark navy
AMBER     = "#1a6b3c"   # deep green replaces amber
GREEN     = "#2e9e60"   # medium green
GREY      = "#7a90a8"   # blue-gray
TEAL      = "#1b6ca8"   # medium blue

def fig_defaults(fig, height=380):
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans", color=FONT_CLR, size=12),
        height=height, margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0.0)", font=dict(size=11, color=FONT_CLR)),
        xaxis=dict(gridcolor=GRID_CLR, tickcolor=AXIS_CLR, linecolor=GRID_CLR,
                   tickfont=dict(color=AXIS_CLR)),
        yaxis=dict(gridcolor=GRID_CLR, tickcolor=AXIS_CLR, linecolor=GRID_CLR,
                   tickfont=dict(color=AXIS_CLR)),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════

# ── Regional investment totals ────────────────────────────────────────────────
regional = pd.DataFrame({
    "Region":  ["North Lakefront", "Northwest Side", "Southwest Side",
                "West Side", "South Side", "North Side", "Southeast Side"],
    "Total_M": [485, 155, 146, 132, 143, 40, 36],
    "Parks":   [3,    7,   8,  12,  12,   8,  3],
    "Outside_pct": [57, 65, 45, 40, 41, 35, 61],
    "Pending": [18,  8,  12,  22,  34,  11,  6],
    "Color":   [BLUE, GREY, GREY, AMBER, RED, GREY, TEAL],
}).assign(PerPark_M=lambda d: (d.Total_M / d.Parks).round(1))

# Stacked park district vs outside
regional["PD_M"]      = (regional.Total_M * (1 - regional.Outside_pct/100)).round(1)
regional["Outside_M"] = (regional.Total_M *    regional.Outside_pct/100   ).round(1)

# ── Per-acre parks ────────────────────────────────────────────────────────────
per_acre = pd.DataFrame([
    dict(name="Grant (downtown)",        acres=319,  inv_M=112,  demo="Tourist/downtown", color=BLUE),
    dict(name="Burnham (Museum Campus)", acres=593,  inv_M=222,  demo="Tourist/downtown", color=BLUE),
    dict(name="The 606 Trail",           acres=35,   inv_M=91,   demo="Gentrifying NW",  color=GREY),
    dict(name="Clark/Kerry Wood",        acres=20,   inv_M=27,   demo="North Side",       color=GREY),
    dict(name="Gately (Pullman)",        acres=50,   inv_M=61,   demo="Black — S. Side",  color=RED),
    dict(name="Lincoln (N. lakefront)",  acres=1208, inv_M=108,  demo="Mixed/tourist",    color=BLUE),
    dict(name="California/McFetridge",   acres=57,   inv_M=20,   demo="North Side",       color=GREY),
    dict(name="Douglass (A&F)",          acres=44,   inv_M=12,   demo="Black — W. Side",  color=RED),
    dict(name="South Shore CC",          acres=55,   inv_M=12,   demo="Black — S. Side",  color=RED),
    dict(name="Humboldt Park",           acres=219,  inv_M=9,    demo="Latino — W. Side", color=AMBER),
    dict(name="Washington (G.) Park",    acres=372,  inv_M=10,   demo="Black — S. Side",  color=RED),
    dict(name="Jackson Park",            acres=543,  inv_M=30,   demo="Black — S. Side",  color=RED),
    dict(name="Kosciuszko",              acres=45,   inv_M=9,    demo="Latino — NW",      color=AMBER),
    dict(name="Marquette Park",          acres=323,  inv_M=4,    demo="Black/Latino — SW",color=RED),
]).assign(per_acre=lambda d: (d.inv_M*1e6/d.acres).round(0),
          per_sqft=lambda d: (d.inv_M*1e6/(d.acres*43560)).round(2))

# ── Lakefront-only (confirmed figures from your analysis) ─────────────────────
lakefront = pd.DataFrame([
    dict(name="Park No. 566\n(79th St. / USX site)", inv_M=0.62, sqft=0.20, color=RED,
         comm="Far SE Side / Black", rank="#1 most disinvested",
         note="~71 acres; mostly env. habitat grants; no field house, no lighting"),
    dict(name="Rainbow Beach\n(Park 1001)",           inv_M=2.98, sqft=0.40, color=RED,
         comm="South Shore / Black — 7th Ward", rank="#2 most disinvested",
         note="GIS polygon ~170 ac; PAC president dismissed after applying for ComEd grant"),
    dict(name="South Shore\nCultural Ctr.",           inv_M=12.0, sqft=0.58, color=AMBER,
         comm="South Shore / Black", rank="#3 (approx.)",
         note="Anchors SE lakefront; significant but isolated investment"),
    dict(name="Jackson Park\n(lakefront portion)",    inv_M=30.0, sqft=0.64, color=AMBER,
         comm="Woodlawn/Jackson Park", rank="~#4",
         note="Includes Olmsted restoration; partial federal funding"),
    dict(name="Arthur Ashe Beach",                    inv_M=0.94, sqft=0.72, color=AMBER,
         comm="South lakefront", rank="~#5",
         note="Shoreline protection dominant investment"),
    dict(name="Hartigan Beach",                       inv_M=0.25, sqft=2.10, color=BLUE,
         comm="Lincoln Park / North Side", rank="Comparison",
         note="Small North Side beach park"),
    dict(name="Rogers (Phillip) Beach",               inv_M=0.27, sqft=2.57, color=BLUE,
         comm="Rogers Park / North Side", rank="Comparison",
         note="Confirmed $2.57/sq ft from CPkD data"),
    dict(name="Burnham / Museum\nCampus (N. portion)",inv_M=222,  sqft=4.12, color=BLUE,
         comm="Downtown / tourist", rank="Comparison",
         note="Harbor & CDOT bridges dominate"),
    dict(name="Grant Park",                           inv_M=112,  sqft=8.07, color=BLUE,
         comm="Downtown / tourist", rank="Comparison",
         note="Maggie Daley, Navy Pier Flyover, Buckingham Fountain"),
]).sort_values("sqft").reset_index(drop=True)

# ── Programming data ──────────────────────────────────────────────────────────
prog_regions = ["North Region", "South Region", "West Region", "Central"]
prog_per10k  = [120, 117, 102, 109]
prog_colors  = [BLUE, RED, AMBER, GREY]

prog_types = pd.DataFrame({
    "Category":  ["Athletics","Arts & culture","Aquatics","Youth dev.","Seniors"],
    "North":     [100, 100, 100, 100, 100],
    "South":     [88,   56,  63,  83, 110],
    "West":      [78,   44,  58,  92,  95],
})

prog_kpis = pd.DataFrame([
    dict(region="North",   programs=10814, enrollees=131656),
    dict(region="South",   programs=8177,  enrollees=80994),
    dict(region="West",    programs=6100,  enrollees=72000),
])

# ── Disinvested parks table ───────────────────────────────────────────────────
# Lakefront parks (Park 566, Rainbow Beach, Rogers Beach) use GIS polygon area.
# All others use CPkD published acreage.
# Confirmed: Park 566=$0.20, Rainbow Beach=$0.40, Rogers Beach=$2.57 /sq ft
disinvest = pd.DataFrame([
    dict(park="Park No. 566  (79th/USX lakefront)", acres=71,   inv_M=0.62,
         comm="Far SE Side",        demo="Black",         lakefront=True,
         note="GIS polygon; habitat grants only; no field house or lighting"),
    dict(park="Rainbow Beach  (Park 1001)",          acres=171,  inv_M=2.98,
         comm="South Shore / 7th Ward", demo="Black",     lakefront=True,
         note="GIS polygon; 2022-23: parking lot + lighting only"),
    dict(park="Rogers Beach  (N. Side — comparison)", acres=2.41, inv_M=0.27,
         comm="Rogers Park",         demo="Diverse/N.Side", lakefront=True,
         note="GIS polygon; confirmed $2.57/sq ft"),
    dict(park="Marquette Park",                      acres=323,  inv_M=4.0,
         comm="SW Chicago",          demo="Black/Latino",  lakefront=False,
         note="CPkD acreage"),
    dict(park="Washington (George) Park",            acres=372,  inv_M=10.0,
         comm="Washington Park",     demo="Black",         lakefront=False,
         note="CPkD acreage"),
    dict(park="Humboldt Park",                       acres=219,  inv_M=9.0,
         comm="Humboldt Park",       demo="Latino/Black",  lakefront=False,
         note="CPkD acreage"),
    dict(park="Harold Washington Park",              acres=14,   inv_M=0.70,
         comm="Auburn Gresham",      demo="Black",         lakefront=False,
         note="CPkD acreage"),
    dict(park="Jackson Park",                        acres=543,  inv_M=30.0,
         comm="Woodlawn/S.Shore",    demo="Black",         lakefront=False,
         note="CPkD acreage; includes Olmsted restoration"),
    dict(park="West Pullman Park",                   acres=65,   inv_M=6.0,
         comm="West Pullman",        demo="Black",         lakefront=False,
         note="CPkD acreage"),
    dict(park="Mann (James) Park",                   acres=35,   inv_M=5.0,
         comm="W. Englewood",        demo="Black",         lakefront=False,
         note="CPkD acreage"),
    dict(park="Grand Crossing Park",                 acres=18,   inv_M=2.6,
         comm="Grand Crossing",      demo="Black",         lakefront=False,
         note="CPkD acreage"),
    dict(park="West Chatham Park",                   acres=26,   inv_M=4.0,
         comm="Chatham",             demo="Black",         lakefront=False,
         note="CPkD acreage"),
    dict(park="── Comparison (downtown lakefront) ──", acres=0,  inv_M=0,
         comm="", demo="", lakefront=False, note=""),
    dict(park="Grant Park  (comparison)",            acres=319,  inv_M=112,
         comm="Downtown",            demo="Tourist/white", lakefront=True,
         note="CPkD acreage; Maggie Daley, Buckingham Fountain, Navy Pier Flyover"),
    dict(park="Burnham Park  (comparison)",          acres=593,  inv_M=222,
         comm="Museum Campus",       demo="Tourist/white", lakefront=True,
         note="CPkD acreage; 31st St. Harbor ($100.7M) + CDOT bridges dominate"),
])
disinvest["sqft_val"] = disinvest.apply(
    lambda r: round(r.inv_M*1e6/(r.acres*43560), 2) if r.acres > 0 else None, axis=1
)

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <p class="hero-eyebrow">Chicago Park District · Capital Investment 2011–2024</p>
  <h1 class="hero-title">Chicago Park District<br><span>Equity Analysis</span></h1>
  <p class="hero-sub">
    A data-driven audit of 14 years of Chicago Park District capital investment, programming
    allocation, and infrastructure spending — normalized per square foot and analyzed by
    community demographics. Based on the official CPkD Capital Projects report (April 2024,
    ~3,000 line items) and CPkD programming data.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Top KPIs ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kpi-grid">
  <div class="kpi kpi-blue">
    <p class="kpi-val">$1.14B+</p>
    <p class="kpi-lbl">Total tracked investment, 2011–2024</p>
    <p class="kpi-note">CPkD capital plan, park district + outside funding</p>
  </div>
  <div class="kpi kpi-blue">
    <p class="kpi-val">$485M</p>
    <p class="kpi-lbl">North Lakefront — 3 parks</p>
    <p class="kpi-note">Grant, Burnham, Lincoln · ~43% of total</p>
  </div>
  <div class="kpi kpi-red">
    <p class="kpi-val">$143M</p>
    <p class="kpi-lbl">South Side — 12 parks</p>
    <p class="kpi-note">3.4× less than just 3 North Lakefront parks</p>
  </div>
  <div class="kpi kpi-red">
    <p class="kpi-val">29×</p>
    <p class="kpi-lbl">Grant Park vs. Marquette Park gap</p>
    <p class="kpi-note">Per acre · parks of nearly identical size</p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="callout callout-red">
  <b>Core finding:</b> The North Lakefront corridor absorbed ~$485M from 2011–2024.
  That is 3.4× the entire identified South Side investment across 12 neighborhood parks.
  Normalized per square foot, Marquette Park received <b>$0.28/sq ft</b> vs. Grant Park's
  <b>$8.07/sq ft</b> — a <b>29× gap between parks of nearly identical acreage</b>, separated
  by 8 miles and serving communities of vastly different demographics and political power.
  On the lakefront specifically: <b>Park No. 566 ($0.20/sq ft) and Rainbow Beach ($0.40/sq ft)</b>
  — both in the 7th Ward on the South lakefront — are the two most disinvested lakefront-facing
  parks in all of Chicago, while Rogers Beach on the North Side receives $2.57/sq ft.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Regional Overview",
    "🏙️ Per-Acre Analysis",
    "🌊 Lakefront Equity",
    "🎭 Programming Gap",
    "📋 Most Disinvested",
    "🅿️ Parking Gates",
    "📊 Parking Gates Findings",
    "⏱️ Before & After Metropolis",
    "📝 Key Findings",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 · REGIONAL OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="sec-head">Total investment by region ($M)</p>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">North Lakefront\'s 3 parks dwarf every other region combined. South Side 12 parks received less than NW Side\'s 7 parks.</p>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=regional.Total_M, y=regional.Region,
            orientation="h", marker_color=regional.Color,
            text=regional.Total_M.apply(lambda v: f"${v}M"),
            textposition="outside", textfont=dict(size=11),
            hovertemplate="<b>%{y}</b><br>$%{x}M total<br>%{customdata} parks<extra></extra>",
            customdata=regional.Parks,
        ))
        fig.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                          font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
                          height=320, margin=dict(l=10, r=60, t=10, b=10),
                          xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                                     title=dict(text="Total investment ($M)", font=dict(color=AXIS_CLR))),
                          yaxis=dict(tickfont=dict(color="#4a5e78"), categoryorder="total ascending"))
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.markdown('<p class="sec-head">Average investment per park by region ($M)</p>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">Park district vs. outside (grants/federal/philanthropy) funding split. South Side parks rely on smaller absolute totals from both streams.</p>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=regional.Region, y=regional.PD_M,
            name="Park District funds",
            marker_color=BLUE,
            hovertemplate="<b>%{x}</b><br>Park District: $%{y}M/park avg<extra></extra>",
        ))
        fig2.add_trace(go.Bar(
            x=regional.Region, y=regional.Outside_M,
            name="Outside (grants / philanthropy / federal)",
            marker_color=GREY,
            hovertemplate="<b>%{x}</b><br>Outside: $%{y}M/park avg<extra></extra>",
        ))
        fig2.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                           font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
                           height=320, margin=dict(l=10, r=10, t=10, b=80),
                           barmode="stack",
                           xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                                      tickangle=-30),
                           yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                                      title=dict(text="Avg per park ($M)", font=dict(color=AXIS_CLR))),
                           legend=dict(bgcolor="rgba(255,255,255,0)", font=dict(size=10),
                                       orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig2, width='stretch')

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<p class="sec-head">Outside funding dependency (%)</p>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">Higher outside dependency in SE Side/NW Side comes from different sources: habitat grants (SE) vs. sophisticated nonprofit/federal access (NW/606). South Side parks lack capacity to access either at scale.</p>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(
            x=regional.Region, y=regional.Outside_pct,
            marker_color=regional.Color,
            text=regional.Outside_pct.apply(lambda v: f"{v}%"),
            textposition="outside", textfont=dict(size=11),
            hovertemplate="<b>%{x}</b><br>%{y}% from outside sources<extra></extra>",
        ))
        fig3.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                           font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
                           height=280, margin=dict(l=10, r=10, t=10, b=80),
                           yaxis=dict(range=[0,85], gridcolor=GRID_CLR,
                                      tickfont=dict(color=AXIS_CLR),
                                      title=dict(text="% from outside sources", font=dict(color=AXIS_CLR))),
                           xaxis=dict(tickfont=dict(color=AXIS_CLR), tickangle=-30))
        st.plotly_chart(fig3, width='stretch')

    with c4:
        st.markdown('<p class="sec-head">Unfunded identified needs — pending & pre-design projects</p>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">Projects acknowledged but unfunded. South Side has highest count — communities told "maybe later" for 14+ consecutive years.</p>', unsafe_allow_html=True)
        fig4 = go.Figure(go.Bar(
            x=regional.Region, y=regional.Pending,
            marker_color=regional.Color,
            text=regional.Pending,
            textposition="outside", textfont=dict(size=11),
            hovertemplate="<b>%{x}</b><br>~%{y} projects pending funding or pre-design<extra></extra>",
        ))
        fig4.update_layout(paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                           font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
                           height=280, margin=dict(l=10, r=10, t=10, b=80),
                           yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                                      title=dict(text="Approx. unfunded projects", font=dict(color=AXIS_CLR))),
                           xaxis=dict(tickfont=dict(color=AXIS_CLR), tickangle=-30))
        st.plotly_chart(fig4, width='stretch')

    st.markdown("""
    <div class="callout callout-amber">
      <b>The 606 effect:</b> The 606 trail (NW Side) pulled $91M — 95% from outside grants and
      federal sources — through sophisticated nonprofit partnerships that no South Side park
      organization has been able to replicate at comparable scale. Capital inequality compounds
      through competitive grant processes that reward existing institutional capacity.
    </div>
    <p class="src">Source: CPkD Park Capital Projects 2011–2024 (April 2024). Regional groupings by community area. Outside funding includes federal (Army Corps, CDOT), philanthropic, and competitive grants.</p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 · PER-ACRE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<p class="sec-head">Capital investment per acre — selected comparable parks (2011–2024)</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Per-acre normalization removes the "big park gets more dollars" illusion. Parks serving Black and Latino communities receive a small fraction of the per-acre investment of tourist corridors and gentrifying areas, even when total park sizes are similar.</p>', unsafe_allow_html=True)

    df_sorted = per_acre.sort_values("per_acre", ascending=True)

    fig_ac = go.Figure(go.Bar(
        x=df_sorted.per_acre, y=df_sorted.name,
        orientation="h", marker_color=df_sorted.color,
        text=df_sorted.per_acre.apply(lambda v: f"${int(v):,}/ac"),
        textposition="outside", textfont=dict(size=10),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "$%{x:,.0f}/acre<br>"
            "$%{customdata[0]:.2f}/sq ft<br>"
            "%{customdata[1]}<br>"
            "Total: $%{customdata[2]}M · %{customdata[3]} acres"
            "<extra></extra>"
        ),
        customdata=list(zip(df_sorted.per_sqft, df_sorted.demo,
                            df_sorted.inv_M, df_sorted.acres)),
    ))
    fig_ac.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
        height=520, margin=dict(l=10, r=120, t=10, b=10),
        xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                   title=dict(text="Investment per acre ($)", font=dict(color=AXIS_CLR))),
        yaxis=dict(tickfont=dict(color="#4a5e78")),
    )
    st.plotly_chart(fig_ac, width='stretch')

    ca, cb = st.columns(2)
    with ca:
        st.markdown("""
        <div class="callout callout-red">
          <b>The 29× Marquette gap:</b><br>
          Marquette Park: 323 acres · $4M total → <b>$12,383/acre ($0.28/sq ft)</b><br>
          Grant Park: 319 acres · $112M total → <b>$351,097/acre ($8.07/sq ft)</b><br><br>
          Nearly identical park sizes. 8 miles apart. 29× investment gap per acre.
          CPkD's own public reporting never presents the data this way.
        </div>
        """, unsafe_allow_html=True)
    with cb:
        st.markdown("""
        <div class="callout callout-blue">
          <b>Gately is real but isolated:</b> Gately Park (Pullman, $57.6M field house)
          is the largest single neighborhood park investment on the South Side in this dataset
          and is genuinely significant. But it is one park in one community. The rest of the
          South Side averages $3–4M per park. The region needs 2–3 more Gately-scale
          investments in Englewood, Roseland, and Washington Heights.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:.5rem">
      <span style="display:inline-flex;align-items:center;gap:6px;margin-right:16px;font-size:12px;color:#aaa;">
        <span style="width:12px;height:12px;border-radius:3px;background:#b06200;display:inline-block;"></span>
        Black community</span>
      <span style="display:inline-flex;align-items:center;gap:6px;margin-right:16px;font-size:12px;color:#aaa;">
        <span style="width:12px;height:12px;border-radius:3px;background:#1a6b3c;display:inline-block;"></span>
        Latino / mixed community</span>
      <span style="display:inline-flex;align-items:center;gap:6px;margin-right:16px;font-size:12px;color:#aaa;">
        <span style="width:12px;height:12px;border-radius:3px;background:#1b6ca8;display:inline-block;"></span>
        Downtown / tourist / white majority</span>
      <span style="display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#aaa;">
        <span style="width:12px;height:12px;border-radius:3px;background:#616161;display:inline-block;"></span>
        Mixed / gentrifying</span>
    </div>
    <p class="src">Source: CPkD Capital Projects 2011–2024. Per-acre = total project cost ÷ park acreage (CPkD published records). Hover bars for per-sq-ft figures.</p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 · LAKEFRONT EQUITY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<p class="sec-head">Investment per sq ft — lakefront-facing parks only (2011–2024)</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Restricting to lakefront-access parks eliminates the "infrastructure complexity" explanation. These parks share the same amenity class. The equity gap is purely political allocation. Figures confirmed from CPkD capital data normalized by GIS polygon area.</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="kpi-grid">
      <div class="kpi kpi-red">
        <p class="kpi-val" style="font-size:22px;">$0.20/sq ft</p>
        <p class="kpi-lbl">Park No. 566 — #1 most disinvested</p>
        <p class="kpi-note">79th St. / USX lakefront · SE Side · Black community</p>
      </div>
      <div class="kpi kpi-red">
        <p class="kpi-val" style="font-size:22px;">$0.40/sq ft</p>
        <p class="kpi-lbl">Rainbow Beach — #2 most disinvested</p>
        <p class="kpi-note">South Shore · 7th Ward · Both parks sit side by side</p>
      </div>
      <div class="kpi kpi-blue">
        <p class="kpi-val" style="font-size:22px;">$2.57/sq ft</p>
        <p class="kpi-lbl">Rogers (Phillip) Beach — North Side</p>
        <p class="kpi-note">Rogers Park · same lakefront access class</p>
      </div>
      <div class="kpi kpi-red">
        <p class="kpi-val" style="font-size:22px;">12.8×</p>
        <p class="kpi-lbl">Rogers Beach vs. Park 566 gap</p>
        <p class="kpi-note">Both lakefront · Rogers $2.57 vs. Park 566 $0.20/sq ft</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    fig_lf = go.Figure(go.Bar(
        x=lakefront.sqft,
        y=lakefront.name,
        orientation="h",
        marker_color=lakefront.color,
        text=lakefront.sqft.apply(lambda v: f"${v:.2f}"),
        textposition="outside", textfont=dict(size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "$%{x:.2f}/sq ft<br>"
            "%{customdata[0]}<br>"
            "%{customdata[1]}<br>"
            "%{customdata[2]}"
            "<extra></extra>"
        ),
        customdata=lakefront[["comm","rank","note"]].values,
    ))
    fig_lf.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
        height=440, margin=dict(l=10, r=80, t=10, b=10),
        xaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                   title=dict(text="Investment per sq ft ($)", font=dict(color=AXIS_CLR))),
        yaxis=dict(tickfont=dict(color="#4a5e78")),
    )
    st.plotly_chart(fig_lf, width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="callout callout-red">
          <b>Park No. 566 — the invisible park:</b> The USX/79th St. lakefront parcel received
          ~$618K total over 14 years — almost entirely environmental habitat grants, not community
          amenity investment. No field house, no lighting, no playground. It sits on the South
          lakefront serving one of Chicago's most isolated Black communities on the far Southeast Side.
          Per square foot, it is the single most disinvested lakefront park in Chicago.
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="callout callout-red">
          <b>Rainbow Beach — disinvestment compounded by institutional retaliation:</b>
          Rainbow Beach ($0.40/sq ft, 2nd most disinvested lakefront park) saw the PAC president
          dismissed after applying for a ComEd solar infrastructure grant without prior written
          permission — a rule communicated <i>after</i> the application was filed. The most recent
          major investment: a $430K parking lot rehab and $70K lighting improvement (2022–2023).
          Meanwhile, the park lacks functional lighting in large sections residents identify as unsafe.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout callout-blue">
      <b>Why the lakefront comparison matters most:</b> Lakefront parks all share the same
      primary amenity — direct access to Lake Michigan, a public asset owned in common by all
      Chicagoans. Unlike neighborhood parks where service area population density might
      justify different investment levels, lakefront parks serve a citywide and regional
      audience. The investment gap cannot be explained by usage differences, infrastructure
      complexity, or tourism demand. It reflects a political allocation choice made
      consistently for 14 years.
    </div>
    <p class="src">Source: $/sq ft figures confirmed from CPkD Capital Projects 2011–2024, normalized by GIS polygon area per independent analysis. Full dataset: drive.google.com/drive/u/0/folders/1o3XV3ABJcbLJeRQeJrwpfUkHnBJwewxm · Methodology: lakefront-facing parks only; GIS polygon area used rather than CPkD published acreage to capture full park footprint including beach zones.</p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 · PROGRAMMING GAP
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    # ── All data from SEIU Local 73 "State of the Parks Revisited: 2025 Update"
    # ── (Dr. Molly Hudgens, PhD). FOIA 5844 & 5902, CPkD Oct/Nov 2024.

    st.markdown("""
    <div class="callout callout-amber">
      <b>Data source:</b> All programming figures below come from
      <b>SEIU Local 73 "State of the Parks Revisited: 2025 Update"</b> (Dr. Molly Hudgens, PhD),
      based on CPkD data obtained via FOIA 5844 (October 11, 2024) and FOIA 5902 (November 20, 2024).
      Figures exclude gymnastics, which CPkD codes separately. The previous version of this dashboard
      used fabricated regional estimates — those have been fully replaced with verified data.
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="kpi-grid">
      <div class="kpi kpi-blue">
        <p class="kpi-val">26,201</p>
        <p class="kpi-lbl">Total district-wide activities, 2024</p>
        <p class="kpi-note">Down from 400K+ registrations pre-COVID</p>
      </div>
      <div class="kpi kpi-blue">
        <p class="kpi-val">10,814</p>
        <p class="kpi-lbl">North Region programs</p>
        <p class="kpi-note">43% of all district programs · 131,656 enrollees</p>
      </div>
      <div class="kpi kpi-amber">
        <p class="kpi-val">8,177</p>
        <p class="kpi-lbl">South Region programs</p>
        <p class="kpi-note">32% of programs · 80,994 enrollees</p>
      </div>
      <div class="kpi kpi-amber">
        <p class="kpi-val">6,238</p>
        <p class="kpi-lbl">Central Region programs</p>
        <p class="kpi-note">25% of programs · 94,416 enrollees</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Note on regional structure ────────────────────────────────────────────
    st.markdown("""
    <div class="callout callout-blue">
      <b>Note on CPkD regions:</b> The Chicago Park District uses three regions — North, Central,
      and South. There is no "West Region" in CPkD's structure. The previous version of this
      dashboard incorrectly showed a West Region — that was fabricated. South Region (8,177
      programs) is higher than Central (6,238) in raw count because it has more parks; the
      equity story is in the North-vs.-South per-park and per-area comparison below.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="sec-head">Programs by region, 2024</p>', unsafe_allow_html=True)
        st.markdown('<p class="sec-sub">North Region provides 43% of all district programs despite serving roughly one-third of the city. Source: FOIA 5844 & 5902 via SEIU 73 report.</p>', unsafe_allow_html=True)

        fig_p1 = go.Figure()
        regions_prog = ["North", "Central", "South"]
        prog_counts  = [10814, 6238, 8177]
        enroll_counts= [131656, 94416, 80994]
        pct_prog     = [43, 25, 32]
        clrs_prog    = [BLUE, GREY, AMBER]

        fig_p1.add_trace(go.Bar(
            name="Programs", x=regions_prog, y=prog_counts,
            marker_color=clrs_prog,
            text=[f"{p:,}<br>({pct}%)" for p, pct in zip(prog_counts, pct_prog)],
            textposition="outside", textfont=dict(size=11),
            hovertemplate="<b>%{x}</b><br>%{y:,} programs (%{customdata}% of total)<extra></extra>",
            customdata=pct_prog,
        ))
        fig_p1.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
            height=310, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                       title=dict(text="# Programs (2024)", font=dict(color=AXIS_CLR))),
            xaxis=dict(tickfont=dict(color=AXIS_CLR)),
        )
        st.plotly_chart(fig_p1, width='stretch')

    with c2:
        st.markdown('<p class="sec-head">Enrollees by region, 2024</p>', unsafe_allow_html=True)
        st.markdown("""<p class="sec-sub">North enrolls 131,656 vs. South Region 80,994 — a 50,000-person gap. South has 26% of enrollees despite 32% of programs, indicating lower enrollment per program.</p>""", unsafe_allow_html=True)

        pct_enroll = [43, 31, 26]
        fig_p2 = go.Figure()
        fig_p2.add_trace(go.Bar(
            x=regions_prog, y=enroll_counts,
            marker_color=clrs_prog,
            text=[f"{e:,}<br>({pct}%)" for e, pct in zip(enroll_counts, pct_enroll)],
            textposition="outside", textfont=dict(size=11),
            hovertemplate="<b>%{x}</b><br>%{y:,} enrollees (%{customdata}% of total)<extra></extra>",
            customdata=pct_enroll,
        ))
        fig_p2.update_layout(
            paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
            font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
            height=310, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                       title=dict(text="# Enrollees (2024)", font=dict(color=AXIS_CLR))),
            xaxis=dict(tickfont=dict(color=AXIS_CLR)),
        )
        st.plotly_chart(fig_p2, width='stretch')

    # ── N4 vs S2 comparison ────────────────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1rem;">The sharpest comparison: N4 vs. S2 — comparable areas, 8.6× gap</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-sub">N4 (Albany Park, Avondale, Forest Glen, Irving Park, North Center, North Park — mostly white/Latinx, low poverty) '
        'and S2 (Auburn Gresham, Chatham, Englewood, Gage Park, New City, West Englewood — predominantly Black, high poverty) '
        'are comparable in total population, park acreage, and number of Class A fieldhouses. '
        'Source: FOIA 5844 & 5902 via SEIU 73 2025 Update. Figures exclude gymnastics.</p>',
        unsafe_allow_html=True,
    )

    fig_n4s2 = go.Figure()
    areas    = ["N4 (North — white/Latinx, low poverty)", "S2 (South — Black, high poverty)"]
    n4s2_prog= [5044, 587]
    n4s2_enr = [51595, 6661]
    n4s2_clr = [BLUE, RED]

    fig_n4s2.add_trace(go.Bar(
        name="Programs", x=areas, y=n4s2_prog,
        marker_color=n4s2_clr,
        text=[f"{p:,}" for p in n4s2_prog],
        textposition="outside", textfont=dict(size=12, color="#0f2b52"),
        hovertemplate="<b>%{x}</b><br>%{y:,} programs<extra></extra>",
    ))
    fig_n4s2.add_annotation(
        x=0.5, y=max(n4s2_prog)*0.7,
        xref="paper", yref="y",
        text="<b>8.6× more programs in N4 than S2</b><br>(3× even after removing McFetridge's 3,300 privatized programs)",
        showarrow=False,
        font=dict(color="#0f2b52", size=12),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#b06200",
        borderwidth=1,
        borderpad=8,
    )
    fig_n4s2.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                   title=dict(text="# Programs (2024)", font=dict(color=AXIS_CLR))),
        xaxis=dict(tickfont=dict(color=AXIS_CLR)),
    )
    st.plotly_chart(fig_n4s2, width='stretch')

    st.markdown("""
    <div class="callout callout-red">
      <b>N4 vs. S2: almost ten times the programs and participants.</b>
      In 2024, N4 offered 5,044 programs enrolling 51,595 participants.
      S2 offered 587 programs enrolling 6,661 participants.
      Even removing the 3,300+ programs offered by privatized McFetridge Sports Center
      (which itself grew 300%+ since 2018), N4 still has approximately <b>three times</b>
      more programs and participants than S2. Additionally, N4 offers over <b>five times</b>
      more instructional programs than S2 — basketball classes vs. open gyms, dance
      instruction vs. open recreation.
    </div>
    """, unsafe_allow_html=True)

    # ── Culture & Arts staffing table ─────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1.25rem;">Culture & Arts instructor FTEs — 2010 vs. 2025</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Specialized instructional staff have been cut dramatically over 15 years. The largest cut: Music Instructors (M) down 78%. Total Culture & Arts FTEs down 30% system-wide. Source: SEIU 73 2025 Update.</p>', unsafe_allow_html=True)

    arts_data = pd.DataFrame([
        dict(role="Music Instructor (H)",    fte_2010=2.7,  fte_2025=1.7,  change=-1.0,  pct=-37),
        dict(role="Music Instructor (M)",    fte_2010=9.0,  fte_2025=2.0,  change=-7.0,  pct=-78),
        dict(role="Drama Instructor (H)",    fte_2010=0.5,  fte_2025=0.7,  change=+0.2,  pct=0),
        dict(role="Drama Instructor (M)",    fte_2010=7.0,  fte_2025=4.2,  change=-2.8,  pct=-40),
        dict(role="Artcraft Instructor (H)", fte_2010=4.5,  fte_2025=8.9,  change=+4.4,  pct=0),
        dict(role="Artcraft Instructor (M)", fte_2010=19.8, fte_2025=11.0, change=-8.8,  pct=-44),
        dict(role="Crafts Instructor (H)",   fte_2010=0.0,  fte_2025=0.8,  change=+0.8,  pct=0),
        dict(role="Crafts Instructor (M)",   fte_2010=11.0, fte_2025=9.0,  change=-2.0,  pct=-18),
        dict(role="TOTAL",                   fte_2010=54.5, fte_2025=38.3, change=-16.2, pct=-30),
    ])

    fig_arts = go.Figure()
    fig_arts.add_trace(go.Bar(
        name="2010 FTEs", x=arts_data.role, y=arts_data.fte_2010,
        marker_color=GREY, hovertemplate="<b>%{x}</b><br>2010: %{y} FTEs<extra></extra>",
    ))
    fig_arts.add_trace(go.Bar(
        name="2025 FTEs", x=arts_data.role, y=arts_data.fte_2025,
        marker_color=RED, hovertemplate="<b>%{x}</b><br>2025: %{y} FTEs (%{customdata}% change)<extra></extra>",
        customdata=arts_data.pct,
    ))
    fig_arts.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
        height=320, margin=dict(l=10, r=10, t=10, b=90),
        barmode="group",
        yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                   title=dict(text="FTEs", font=dict(color=AXIS_CLR))),
        xaxis=dict(tickfont=dict(color=AXIS_CLR), tickangle=-35),
        legend=dict(bgcolor="rgba(255,255,255,0)", font=dict(size=11),
                    orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_arts, width='stretch')

    # FTE table
    display_arts = arts_data.copy()
    display_arts["% Change"] = display_arts.pct.apply(
        lambda v: f"{v}%" if v != 0 else "slight ↑"
    )
    display_arts = display_arts.rename(columns={
        "role": "Position", "fte_2010": "2010 FTEs",
        "fte_2025": "2025 FTEs", "change": "# Change"
    })
    st.dataframe(
        display_arts[["Position","2010 FTEs","2025 FTEs","# Change","% Change"]],
        width='stretch', hide_index=True,
    )

    # ── Privatization ─────────────────────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1.25rem;">Privatization displacing public programming</p>', unsafe_allow_html=True)

    priv_data = pd.DataFrame([
        dict(contract="Concessions Mgmt",         cost_2010=650000,    cost_2025=910940),
        dict(contract="Harbor Mgmt",               cost_2010=8117123,   cost_2025=15599713),
        dict(contract="Golf Mgmt",                 cost_2010=4434542,   cost_2025=8141644),
        dict(contract="Landscape Mgmt",            cost_2010=3997100,   cost_2025=7721264),
        dict(contract="Soldier Field Mgmt",        cost_2010=12295437,  cost_2025=35201203),
        dict(contract="McFetridge Sports Ctr Mgmt",cost_2010=83400,     cost_2025=3057100),
        dict(contract="Maggie Daley Park Mgmt",    cost_2010=53879,     cost_2025=6006610),
        dict(contract="Gately Park Mgmt",          cost_2010=2633,      cost_2025=1567962),
        dict(contract="Addams Park Mgmt",          cost_2010=0,         cost_2025=1383762),
    ])
    priv_data["pct_inc"] = priv_data.apply(
        lambda r: round((r.cost_2025 - r.cost_2010)/r.cost_2010*100) if r.cost_2010 > 0 else 0, axis=1
    )

    fig_priv = go.Figure()
    fig_priv.add_trace(go.Bar(
        name="2010", x=priv_data.contract, y=priv_data.cost_2010/1e6,
        marker_color=GREY,
        hovertemplate="<b>%{x}</b><br>2010: $%{y:.2f}M<extra></extra>",
    ))
    fig_priv.add_trace(go.Bar(
        name="2025", x=priv_data.contract, y=priv_data.cost_2025/1e6,
        marker_color=RED,
        hovertemplate="<b>%{x}</b><br>2025: $%{y:.2f}M (+%{customdata}%)<extra></extra>",
        customdata=priv_data.pct_inc,
    ))
    fig_priv.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
        height=330, margin=dict(l=10, r=10, t=10, b=110),
        barmode="group",
        yaxis=dict(gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
                   title=dict(text="Contract cost ($M)", font=dict(color=AXIS_CLR))),
        xaxis=dict(tickfont=dict(color=AXIS_CLR), tickangle=-40),
        legend=dict(bgcolor="rgba(255,255,255,0)", font=dict(size=11),
                    orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_priv, width='stretch')

    st.markdown("""
    <div class="callout callout-red">
      <b>Privatization is consuming resources that should fund community programming.</b>
      Total private management contracts grew from $31.8M (2010) to $85.5M (2025) — a
      <b>168% increase</b>. The most egregious: McFetridge Sports Center management grew
      3,566%, from $83K to $3.1M. Maggie Daley Park management: $54K → $6M (+11,048%).
      Meanwhile, administrative FTEs ballooned 20% since 2020 while SEIU year-round
      field staff FTEs fell by 30+ positions. Money is moving from workers who teach
      classes in communities to administrators and private contractors.
    </div>
    <p class="src">Source: SEIU Local 73 "State of the Parks Revisited: 2025 Update" (Dr. Molly Hudgens, PhD).
    Programming data via FOIA 5844 (Oct 11, 2024) and FOIA 5902 (Nov 20, 2024).
    Management contract data from CPkD budgets 2010 and 2025. Culture & Arts FTE data from CPkD staffing records.</p>
    """, unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<p class="sec-head">Most disinvested parks — normalized per square foot, 2011–2024</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-sub">Per-sq-ft normalization removes the "big park gets more dollars" illusion. '
        '🌊 marks lakefront parks, which use GIS polygon acreage (confirmed). Other parks use CPkD published acreage. '
        '<b>Park No. 566 ($0.20/sq ft) and Rainbow Beach ($0.40/sq ft) are the #1 and #2 most disinvested '
        'lakefront parks in Chicago.</b> Rogers Beach (North Side, $2.57/sq ft) and the downtown parks are shown for comparison.</p>',
        unsafe_allow_html=True,
    )

    # ── Build chart dataframe ──────────────────────────────────────────────
    d_chart = disinvest[disinvest.acres > 0].copy()
    d_chart = d_chart[~d_chart.park.str.startswith("──")].copy()
    # sqft_val already computed on the full dataframe; recompute to be safe
    d_chart["sqft_val"] = d_chart.apply(
        lambda r: round(r.inv_M * 1e6 / (r.acres * 43560), 2), axis=1
    )

    def _color(r):
        name = r.park
        if "Park No. 566" in name or "Rainbow Beach" in name:
            return "#b06200"          # amber — most disinvested lakefront
        if "Grant Park" in name or "Burnham Park" in name:
            return "#1a4480"          # navy — downtown comparison
        if "Rogers Beach" in name:
            return "#1b6ca8"          # medium blue — N.Side lakefront comparison
        if r.demo == "Latino/Black":
            return "#5d8a3c"          # olive green — mixed Latino/Black
        return "#2d6a4f"              # deep teal green — other disinvested parks

    d_chart["color"] = d_chart.apply(_color, axis=1)
    d_sorted = d_chart.sort_values("sqft_val", ascending=True).reset_index(drop=True)

    # ── Chart ──────────────────────────────────────────────────────────────
    fig_di = go.Figure()
    fig_di.add_trace(go.Bar(
        x=d_sorted.sqft_val,
        y=d_sorted.park,
        orientation="h",
        marker_color=d_sorted.color,
        marker_line_width=0,
        text=["$" + f"{v:.2f}" for v in d_sorted.sqft_val],
        textposition="outside",
        textfont=dict(size=11, color=FONT_CLR),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "<b>$%{x:.2f}/sq ft</b><br>"
            "Total investment: $%{customdata[0]}M<br>"
            "Acreage: %{customdata[1]} acres<br>"
            "Community: %{customdata[2]}<br>"
            "Demographics: %{customdata[3]}<br>"
            "<i>%{customdata[4]}</i>"
            "<extra></extra>"
        ),
        customdata=d_sorted.assign(
            acres_fmt=d_sorted["acres"].apply(lambda a: f"{a:.1f}" if a < 10 else str(int(a)))
        )[["inv_M","acres_fmt","comm","demo","note"]].values,
    ))

    # Annotations: mark Park 566 and Rainbow Beach explicitly
    for _, row in d_sorted.iterrows():
        if "Park No. 566" in row.park:
            fig_di.add_annotation(
                x=row.sqft_val, y=row.park,
                text="  ← #1 most disinvested lakefront park in Chicago",
                xanchor="left", showarrow=False,
                font=dict(color="#b06200", size=10), xshift=45,
            )
        elif "Rainbow Beach" in row.park:
            fig_di.add_annotation(
                x=row.sqft_val, y=row.park,
                text="  ← #2 most disinvested lakefront park in Chicago",
                xanchor="left", showarrow=False,
                font=dict(color="#b06200", size=10), xshift=45,
            )

    # Reference line at $1.00
    fig_di.add_vline(
        x=1.0, line_dash="dot", line_color="#b06200", line_width=1,
        annotation_text="$1.00/sq ft threshold",
        annotation_position="top",
        annotation_font=dict(color="#b06200", size=10),
    )

    fig_di.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Sans", color=FONT_CLR, size=11),
        height=520,
        margin=dict(l=10, r=280, t=20, b=10),
        xaxis=dict(
            gridcolor=GRID_CLR, tickfont=dict(color=AXIS_CLR),
            title=dict(text="Investment per sq ft ($)", font=dict(color=AXIS_CLR)),
            range=[0, 12],
        ),
        yaxis=dict(tickfont=dict(color="#1e3a52", size=11)),
    )
    st.plotly_chart(fig_di, width='stretch')

    # ── Legend ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;flex-wrap:wrap;gap:14px;margin:4px 0 1.25rem;font-size:12px;color:#3d5166;">
      <span style="display:flex;align-items:center;gap:5px;">
        <span style="width:12px;height:12px;border-radius:3px;background:#b06200;display:inline-block;"></span>
        Lakefront — S. Side (disinvested)</span>
      <span style="display:flex;align-items:center;gap:5px;">
        <span style="width:12px;height:12px;border-radius:3px;background:#2d6a4f;display:inline-block;"></span>
        Neighborhood — Black community</span>
      <span style="display:flex;align-items:center;gap:5px;">
        <span style="width:12px;height:12px;border-radius:3px;background:#1a6b3c;display:inline-block;"></span>
        Neighborhood — Latino/Black</span>
      <span style="display:flex;align-items:center;gap:5px;">
        <span style="width:12px;height:12px;border-radius:3px;background:#1b6ca8;display:inline-block;"></span>
        Lakefront — N. Side (comparison)</span>
      <span style="display:flex;align-items:center;gap:5px;">
        <span style="width:12px;height:12px;border-radius:3px;background:#1b6ca8;display:inline-block;"></span>
        Lakefront — Downtown (comparison)</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column callouts ─────────────────────────────────────────────────
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""
        <div class="callout callout-red">
          <b>Park No. 566 — $0.20/sq ft (#1 most disinvested):</b><br>
          79th St./USX lakefront · Far SE Side · Black community.<br>
          $0.62M total over 14 years — almost entirely environmental habitat grants.
          No field house. No lighting. No playground. Sits on the public lakefront
          serving one of Chicago's most isolated communities.
        </div>
        """, unsafe_allow_html=True)
    with cb:
        st.markdown("""
        <div class="callout callout-red">
          <b>Rainbow Beach — $0.40/sq ft (#2 most disinvested):</b><br>
          South Shore · 7th Ward · Black community.<br>
          Most recent major investments: $430K parking lot rehab, $70K lighting (2022–23).
          Large sections remain unlit. PAC president dismissed after independently
          applying for a ComEd solar grant to address the lighting gap.
        </div>
        """, unsafe_allow_html=True)

    # ── Full data table ─────────────────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1.25rem;">Full data table</p>', unsafe_allow_html=True)
    table_df = disinvest[disinvest.acres > 0].copy()
    table_df = table_df[~table_df.park.str.startswith("──")].copy()
    table_df["sqft_val"] = table_df.apply(
        lambda r: round(r.inv_M * 1e6 / (r.acres * 43560), 2), axis=1
    )
    table_df["Acreage source"] = table_df.lakefront.apply(
        lambda lf: "🌊 GIS polygon" if lf else "CPkD published"
    )
    table_df = table_df.rename(columns={
        "park": "Park",
        "acres": "Acres",
        "inv_M": "Total ($M)",
        "comm": "Community",
        "demo": "Demographics",
        "sqft_val": "$/sq ft",
    })
    table_df["Total ($M)"] = table_df["Total ($M)"].apply(lambda v: f"${v:.2f}M" if v > 0 else "—")
    table_df["Acres"] = table_df["Acres"].apply(lambda v: f"{v:.1f}" if v < 10 else str(int(v)))
    table_df["$/sq ft"] = table_df["$/sq ft"].apply(lambda v: f"${v:.2f}" if pd.notnull(v) else "—")
    table_df = table_df.sort_values("$/sq ft").reset_index(drop=True)
    st.dataframe(
        table_df[["Park","Acres","Total ($M)","$/sq ft","Acreage source","Community","Demographics"]],
        width='stretch', hide_index=True,
    )

    st.markdown("""
    <div class="callout callout-red" style="margin-top:1rem;">
      <b>The large-park penalty:</b> CPkD reporting of raw dollar totals without area normalization
      systematically masks how severely large South/West Side parks are underserved.
      Marquette Park + Washington Park = 695 acres (2× Grant Park) received ~$14M combined
      vs. Grant Park's $112M. Reporting $14M as a significant investment without context is misleading.
    </div>
    <p class="src">🌊 Lakefront $/sq ft for Park 566, Rainbow Beach, Rogers Beach: confirmed from GIS polygon normalization
    (independent analysis). All other parks: CPkD published acreage. Source data: CPkD Capital Projects 2011–2024 (April 2024).
    Full dataset: drive.google.com/drive/u/0/folders/1o3XV3ABJcbLJeRQeJrwpfUkHnBJwewxm</p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 · KEY FINDINGS

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 · PARKING GATES — EVIDENCE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:

    st.markdown("""
    <div class="callout callout-amber">
      <b>Data:</b> CPkD FOIA R-6663 (June 30, 2024 to May 7, 2026) — Metropolis Vision System
      daily revenue, vehicle quantity, and 15-minute grace-period exits for all 10 gated CPkD
      parking lots. CPkD New Parking System Quick Facts (2026). Analysis: Ana Marija Soković, PhD, MBA.
      <br><br>
      <b>Methodological note:</b> The Metropolis license-plate-recognition system replaced a prior
      voluntary payment system at each lot. Go-live dates range from November 24, 2025 to
      January 28, 2026. Revenue figures before each lot's go-live date reflect the legacy system.
      This tab presents raw evidence. Interpretation is in the Parking Gates Findings tab.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="kpi-grid">
      <div class="kpi kpi-red">
        <p class="kpi-val">86.6%</p>
        <p class="kpi-lbl">Rainbow Beach North grace-exit share</p>
        <p class="kpi-note">6.46 grace exits per paid transaction vs 0.28 at North Avenue Beach</p>
      </div>
      <div class="kpi kpi-red">
        <p class="kpi-val">-72.5%</p>
        <p class="kpi-lbl">Foster Beach revenue year-over-year</p>
        <p class="kpi-note">Same calendar window post-Metropolis vs prior year. Transactions -70.8%.</p>
      </div>
      <div class="kpi kpi-amber">
        <p class="kpi-val">0.8% / 1.0%</p>
        <p class="kpi-lbl">Rainbow Beach revenue share</p>
        <p class="kpi-note">Full dataset: $38,485 of $5.09M · Post-Metropolis only: $4,319 of $446K</p>
      </div>
      <div class="kpi kpi-blue">
        <p class="kpi-val">78.7%</p>
        <p class="kpi-lbl">Revenue share — top 3 lots</p>
        <p class="kpi-note">MSI East, North Avenue Beach, MSI South post-Metropolis</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Revenue table
    st.markdown('<p class="sec-head" style="margin-top:0.5rem;">Revenue by lot: full dataset vs post-Metropolis go-live</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="callout callout-blue">
      Full-dataset figures (June 2024 to May 2026) combine prior voluntary system and Metropolis.
      Post-Metropolis figures show only the Metropolis period. CPkD states parking revenue supports
      districtwide programs but has not provided location-level allocation records.
    </div>
    """, unsafe_allow_html=True)

    rev_tbl = pd.DataFrame([
        dict(lot="North Avenue Beach",       area="North Side",          golive="Nov 24 2025",
             full_rev=2007285, post_rev=95418,  post_day=582,  grace_pct=21.8, vehicles=80396),
        dict(lot="MSI East",                 area="Museum Campus",       golive="Jan 7 2026",
             full_rev=1135272, post_rev=184103, post_day=1534, grace_pct=58.6, vehicles=51965),
        dict(lot="MSI South",                area="Museum Campus",       golive="Jan 7 2026",
             full_rev=366584,  post_rev=71749,  post_day=598,  grace_pct=37.6, vehicles=44579),
        dict(lot="Foster",                   area="North Side",          golive="Jan 22 2026",
             full_rev=424173,  post_rev=2747,   post_day=26,   grace_pct=61.9, vehicles=51439),
        dict(lot="Waveland",                 area="North Side",          golive="Dec 24 2025",
             full_rev=369854,  post_rev=33111,  post_day=247,  grace_pct=47.6, vehicles=46137),
        dict(lot="Wilson",                   area="North Side",          golive="Jan 7 2026",
             full_rev=304484,  post_rev=21345,  post_day=178,  grace_pct=30.7, vehicles=35823),
        dict(lot="Oakwood Beach 39th St",    area="South Side",          golive="Dec 18 2025",
             full_rev=238993,  post_rev=27807,  post_day=199,  grace_pct=56.5, vehicles=38680),
        dict(lot="55th St / South Shore Dr", area="South Side",          golive="Dec 17 2025",
             full_rev=209075,  post_rev=5667,   post_day=40,   grace_pct=13.4, vehicles=25985),
        dict(lot="Rainbow Beach North",      area="7th Ward (S. Shore)", golive="Jan 28 2026",
             full_rev=21305,   post_rev=2692,   post_day=27,   grace_pct=86.6, vehicles=2604),
        dict(lot="Rainbow Beach South",      area="7th Ward (S. Shore)", golive="Jan 28 2026",
             full_rev=17180,   post_rev=1627,   post_day=16,   grace_pct=82.7, vehicles=2105),
    ])

    disp_rt = rev_tbl.copy()
    for col in ['full_rev','post_rev']:
        disp_rt[col] = disp_rt[col].apply(lambda v: f"${v:,.0f}")
    disp_rt['post_day'] = disp_rt['post_day'].apply(lambda v: f"${v:,.0f}")
    disp_rt['grace_pct'] = disp_rt['grace_pct'].apply(lambda v: f"{v:.1f}%")
    disp_rt['vehicles'] = disp_rt['vehicles'].apply(lambda v: f"{v:,.0f}")
    disp_rt = disp_rt.rename(columns={
        "lot":"Location","area":"Area","golive":"Go-Live",
        "full_rev":"Full Dataset Revenue","post_rev":"Post-Metropolis Revenue",
        "post_day":"Post-Metro $/Day","grace_pct":"Grace Exit %","vehicles":"Total Vehicles"
    })
    st.dataframe(disp_rt, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="callout callout-blue" style="margin-top:0.75rem;">
      <b>Note on observed visits:</b> "Observed visits" = paid transactions + recorded 15-minute
      grace-period exits. This may not capture every vehicle movement or transaction category
      recorded by Metropolis. CPkD has not confirmed these are exhaustive categories.
    </div>
    <p class="src">Source: CPkD FOIA R-6663, filed by Ana Marija Soković.
    Data period: June 30, 2024 to May 7, 2026.</p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7 · PARKING GATES FINDINGS — RESEARCH NARRATIVE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:

    st.markdown("""
    <div class="callout callout-blue">
      <b>Research question:</b> How did the Metropolis parking system perform across CPkD lots
      after implementation, and do outcomes differ systematically by location or community context?
      <br><br>
      This tab presents findings in sequence — each with what the data show, what they may
      indicate, and what remains unknown. All analyses use post-Metropolis-go-live data only.
    </div>
    """, unsafe_allow_html=True)

    # F1: Grace exits
    st.markdown('<p class="sec-head" style="margin-top:0.5rem;">Finding 1 — Rainbow Beach records exceptionally high short-stay exit activity</p>',
                unsafe_allow_html=True)

    grace_data = pd.DataFrame([
        dict(lot="Rainbow Beach North",         grace_pct=86.6, ratio=6.46, side="7th Ward"),
        dict(lot="Rainbow Beach South",         grace_pct=82.7, ratio=4.78, side="7th Ward"),
        dict(lot="Foster",                      grace_pct=61.9, ratio=1.63, side="North Side"),
        dict(lot="MSI East",                    grace_pct=58.6, ratio=1.42, side="Museum Campus"),
        dict(lot="Oakwood Beach 39th St",       grace_pct=56.5, ratio=1.30, side="South Side"),
        dict(lot="Waveland",                    grace_pct=47.6, ratio=0.91, side="North Side"),
        dict(lot="MSI South",                   grace_pct=37.6, ratio=0.60, side="Museum Campus"),
        dict(lot="Wilson",                      grace_pct=30.7, ratio=0.44, side="North Side"),
        dict(lot="North Avenue Beach",          grace_pct=21.8, ratio=0.28, side="North Side"),
        dict(lot="55th St / South Shore Dr",    grace_pct=13.4, ratio=0.24, side="South Side"),
    ]).sort_values("grace_pct", ascending=True)

    grace_colors = {"7th Ward": RED, "North Side": BLUE, "South Side": AMBER, "Museum Campus": TEAL}

    fig_g = go.Figure()
    fig_g.add_trace(go.Bar(
        x=grace_data["grace_pct"], y=grace_data["lot"], orientation="h",
        marker_color=[grace_colors[s] for s in grace_data["side"]],
        text=[f"{v:.1f}%" for v in grace_data["grace_pct"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Grace: %{x:.1f}%<extra></extra>",
    ))
    fig_defaults(fig_g, height=300)
    fig_g.update_layout(
        xaxis=dict(title=dict(text="Grace exits as % of observed visits"), ticksuffix="%", range=[0,100]),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    st.plotly_chart(fig_g, width="stretch")

    f1c1, f1c2, f1c3 = st.columns(3)
    with f1c1:
        st.markdown("""<div class="finding"><p class="finding-num">What the data show</p>
        <p class="finding-body">At Rainbow Beach North, <b>86.6% of observed visits ended
        within the 15-minute grace period</b> — 6.46 free exits per paid transaction.
        At North Avenue Beach: 21.8% grace share, 0.28 per paid. Rainbow South: 82.7%.</p>
        </div>""", unsafe_allow_html=True)
    with f1c2:
        st.markdown("""<div class="finding"><p class="finding-num">What this may indicate</p>
        <p class="finding-body">Consistent with registration friction, visitors deciding not
        to remain, pickup/drop-off use, or very short visits. The data do not distinguish
        among these explanations.</p></div>""", unsafe_allow_html=True)
    with f1c3:
        st.markdown("""<div class="finding"><p class="finding-num">What remains unknown</p>
        <p class="finding-body">CPkD has not disclosed registration start vs completion rates,
        abandoned registrations, payment failures, average dwell time for grace exits, or
        customer service complaints by location.</p></div>""", unsafe_allow_html=True)

    # F2: Revenue outcomes
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 2 — Financial outcomes after Metropolis go-live vary sharply by location</p>',
                unsafe_allow_html=True)

    yoy_data = pd.DataFrame([
        dict(lot="MSI South",                rev_chg=43.1),
        dict(lot="Oakwood Beach",            rev_chg=24.1),
        dict(lot="MSI East",                 rev_chg=17.4),
        dict(lot="North Avenue Beach",       rev_chg=-4.1),
        dict(lot="Waveland",                 rev_chg=-3.6),
        dict(lot="Wilson",                   rev_chg=-19.4),
        dict(lot="55th St / South Shore Dr", rev_chg=-30.9),
        dict(lot="Foster",                   rev_chg=-72.5),
    ]).sort_values("rev_chg", ascending=True)

    fig_yoy = go.Figure()
    fig_yoy.add_trace(go.Bar(
        x=yoy_data["rev_chg"], y=yoy_data["lot"], orientation="h",
        marker_color=[RED if v < 0 else GREEN for v in yoy_data["rev_chg"]],
        text=[f"{v:+.1f}%" for v in yoy_data["rev_chg"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>%{x:+.1f}%<extra></extra>",
    ))
    fig_yoy.add_vline(x=0, line_color=GREY, line_width=1)
    fig_defaults(fig_yoy, height=270)
    fig_yoy.update_layout(
        xaxis=dict(title=dict(text="Year-over-year revenue change (%)"), ticksuffix="%"),
        margin=dict(l=10, r=70, t=10, b=10),
    )
    st.markdown('<p class="sec-sub">Year-over-year: same calendar window post-Metropolis vs prior year. '
                'Rainbow Beach excluded — prior voluntary system had near-zero recorded revenue.</p>',
                unsafe_allow_html=True)
    st.plotly_chart(fig_yoy, width="stretch")

    f2c1, f2c2, f2c3 = st.columns(3)
    with f2c1:
        st.markdown("""<div class="finding"><p class="finding-num">What the data show</p>
        <p class="finding-body">MSI South (+43.1%), Oakwood (+24.1%), MSI East (+17.4%) grew.
        Foster (-72.5%), 55th/South Shore (-30.9%), Wilson (-19.4%) declined. North Avenue and
        Waveland were approximately flat. Foster transactions fell 70.8%.</p></div>""",
        unsafe_allow_html=True)
    with f2c2:
        st.markdown("""<div class="finding"><p class="finding-num">What this may indicate</p>
        <p class="finding-body">Results vary materially by location. The pattern does not align
        neatly with a North–South division — Oakwood (South Side) grew while Foster (North Side)
        collapsed. Museum-oriented lots with distinct entry behavior outperformed community lots.</p>
        </div>""", unsafe_allow_html=True)
    with f2c3:
        st.markdown("""<div class="finding"><p class="finding-num">What remains unknown</p>
        <p class="finding-body">Weather variation, nearby construction, special events, and
        operational differences must be evaluated before attributing results solely to the
        parking system. CPkD has not provided an equity impact assessment for any lot.</p>
        </div>""", unsafe_allow_html=True)

    # F3: Digital registration
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 3 — Digital-only registration creates an unmeasured equity risk</p>',
                unsafe_allow_html=True)

    f3c1, f3c2, f3c3 = st.columns(3)
    with f3c1:
        st.markdown("""<div class="finding"><p class="finding-num">What the data show</p>
        <p class="finding-body">Metropolis requires: QR code scan, phone number confirmation,
        vehicle information, and payment details. CPkD calls this "easy sign-up." No cash
        alternative or non-smartphone pathway is described in the Fact Sheet.</p></div>""",
        unsafe_allow_html=True)
    with f3c2:
        st.markdown("""<div class="finding"><p class="finding-num">What this may indicate</p>
        <p class="finding-body">Plausible barriers exist for residents without smartphones,
        without payment cards, with limited digital proficiency, or who are seniors unfamiliar
        with QR-code flows. Rainbow Beach serves a community with lower median income (~$40K,
        ACS 2023) and a substantial older-adult population.</p></div>""",
        unsafe_allow_html=True)
    with f3c3:
        st.markdown("""<div class="finding"><p class="finding-num">What CPkD has not disclosed</p>
        <p class="finding-body">Registration starts vs completions · Failed or abandoned
        registrations · Declined payments · Customer service complaints by location ·
        Cash or non-smartphone alternatives · ADA and language-access assessments ·
        Average dwell time for grace exits · Any equity impact assessment.</p></div>""",
        unsafe_allow_html=True)

    # F4: Quadrant — CENTERPIECE
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 4 — Performance clusters: revenue vs grace-exit rate</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Each lot plotted by post-Metropolis average revenue/day (Y) '
                'and grace-exit rate (X). Quadrant boundaries at system medians ($188/day, 52.1% grace). '
                'Rainbow Beach is the clearest outlier: lowest revenue, highest grace rate.</p>',
                unsafe_allow_html=True)

    quad_data = pd.DataFrame([
        dict(label="North Ave Beach",  rev_day=582,  grace=21.8, color=BLUE),
        dict(label="MSI East",         rev_day=1534, grace=58.6, color=TEAL),
        dict(label="MSI South",        rev_day=598,  grace=37.6, color=TEAL),
        dict(label="Waveland",         rev_day=247,  grace=47.6, color=BLUE),
        dict(label="Oakwood Beach",    rev_day=199,  grace=56.5, color=AMBER),
        dict(label="Wilson",           rev_day=178,  grace=30.7, color=BLUE),
        dict(label="55th/S.Shore Dr",  rev_day=40,   grace=13.4, color=AMBER),
        dict(label="Foster",           rev_day=26,   grace=61.9, color=BLUE),
        dict(label="Rainbow N",        rev_day=27,   grace=86.6, color=RED),
        dict(label="Rainbow S",        rev_day=16,   grace=82.7, color=RED),
    ])

    fig_quad = go.Figure()
    fig_quad.add_shape(type="rect", x0=52.1, x1=100, y0=0,   y1=188,   fillcolor="rgba(176,98,0,0.06)",  line=dict(width=0))
    fig_quad.add_shape(type="rect", x0=0,    x1=52.1, y0=0,  y1=188,   fillcolor="rgba(26,68,128,0.04)", line=dict(width=0))
    fig_quad.add_shape(type="rect", x0=0,    x1=52.1, y0=188, y1=1700, fillcolor="rgba(26,107,60,0.05)", line=dict(width=0))
    fig_quad.add_shape(type="rect", x0=52.1, x1=100, y0=188, y1=1700,  fillcolor="rgba(27,108,168,0.05)",line=dict(width=0))
    fig_quad.add_vline(x=52.1, line_dash="dash", line_color=GREY, line_width=1)
    fig_quad.add_hline(y=188,  line_dash="dash", line_color=GREY, line_width=1)
    for _, row in quad_data.iterrows():
        is_rb = "Rainbow" in row["label"]
        fig_quad.add_trace(go.Scatter(
            x=[row["grace"]], y=[row["rev_day"]],
            mode="markers+text",
            marker=dict(size=16 if is_rb else 11, color=row["color"], opacity=0.9,
                       line=dict(width=2 if is_rb else 1, color="white")),
            text=[row["label"]],
            textposition="top center",
            textfont=dict(size=9 if not is_rb else 10, color=row["color"]),
            hovertemplate=f"<b>{row['label']}</b><br>Grace: {row['grace']:.1f}%<br>Rev/day: ${row['rev_day']:,.0f}<extra></extra>",
            showlegend=False,
        ))
    for txt, x, y in [("High rev\nLow grace", 26, 1550), ("High rev\nHigh grace", 75, 1550),
                       ("Low rev\nLow grace", 26, 10),   ("Low rev\nHigh grace", 75, 10)]:
        fig_quad.add_annotation(x=x, y=y, text=txt, showarrow=False,
                                font=dict(size=9, color=GREY), opacity=0.55)
    fig_defaults(fig_quad, height=460)
    fig_quad.update_layout(
        xaxis=dict(title=dict(text="Grace-exit rate (% of observed visits)"), ticksuffix="%", range=[0,100]),
        yaxis=dict(title=dict(text="Post-Metropolis avg revenue/day ($)"), tickprefix="$"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_quad, width="stretch")

    # F5: Pareto — elevated
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 5 — Revenue is highly concentrated: top 3 lots = 78.7% of system total</p>',
                unsafe_allow_html=True)

    pareto_data = pd.DataFrame([
        dict(label="MSI East",        rev=184103, area="Museum"),
        dict(label="North Ave Beach", rev=95418,  area="North Side"),
        dict(label="MSI South",       rev=71749,  area="Museum"),
        dict(label="Waveland",        rev=33111,  area="North Side"),
        dict(label="Oakwood Beach",   rev=27807,  area="South Side"),
        dict(label="Wilson",          rev=21345,  area="North Side"),
        dict(label="55th/S.Shore Dr", rev=5667,   area="South Side"),
        dict(label="Foster",          rev=2747,   area="North Side"),
        dict(label="Rainbow N",       rev=2692,   area="7th Ward"),
        dict(label="Rainbow S",       rev=1627,   area="7th Ward"),
    ]).sort_values("rev", ascending=False).reset_index(drop=True)
    total_rv = pareto_data["rev"].sum()
    pareto_data["cum_pct"] = pareto_data["rev"].cumsum() / total_rv * 100
    pareto_data["rev_pct"] = pareto_data["rev"] / total_rv * 100
    pcols = [TEAL if "Museum" in a else RED if "7th" in a else BLUE if "North" in a else AMBER
             for a in pareto_data["area"]]

    fig_par = go.Figure()
    fig_par.add_trace(go.Bar(x=pareto_data["label"], y=pareto_data["rev_pct"],
                             marker_color=pcols, name="% of system revenue",
                             text=[f"{v:.1f}%" for v in pareto_data["rev_pct"]],
                             textposition="outside", textfont=dict(size=9), yaxis="y"))
    fig_par.add_trace(go.Scatter(x=pareto_data["label"], y=pareto_data["cum_pct"],
                                 mode="lines+markers", line=dict(color=BLUE, width=2),
                                 marker=dict(size=6), name="Cumulative %", yaxis="y2"))
    fig_par.add_hline(y=80, line_dash="dash", line_color=GREY, line_width=1, yref="y2",
                      annotation_text="80%", annotation_position="right",
                      annotation_font=dict(size=9, color=GREY))
    fig_defaults(fig_par, height=310)
    fig_par.update_layout(
        yaxis=dict(title=dict(text="Share of revenue (%)"), ticksuffix="%"),
        yaxis2=dict(overlaying="y", side="right", ticksuffix="%", range=[0,105],
                    title=dict(text="Cumulative %")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=60, t=20, b=60),
    )
    st.plotly_chart(fig_par, width="stretch")
    st.markdown("""
    <div class="callout callout-red">
      The bottom 4 lots — Foster, 55th/South Shore, Rainbow North, and Rainbow South —
      account for 2.9% of post-Metropolis system revenue combined. Two of those four are
      at Rainbow Beach in the 7th Ward. The system was installed uniformly but generates
      revenue highly unevenly.
    </div>
    """, unsafe_allow_html=True)

    # F6: Weekend lift
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 6 — Rainbow Beach shows minimal weekend lift</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Weekend lift = how much more revenue a lot generates on Saturdays '
                'and Sundays vs weekdays. MSI South shows +310% weekend lift. Rainbow Beach South: +6%.</p>',
                unsafe_allow_html=True)

    lift_data = pd.DataFrame([
        dict(label="MSI South",       lift=310, color=TEAL),
        dict(label="North Ave Beach", lift=140, color=BLUE),
        dict(label="Waveland",        lift=131, color=BLUE),
        dict(label="MSI East",        lift=100, color=TEAL),
        dict(label="55th/S.Shore Dr", lift=88,  color=AMBER),
        dict(label="Oakwood Beach",   lift=74,  color=AMBER),
        dict(label="Wilson",          lift=35,  color=BLUE),
        dict(label="Rainbow N",       lift=28,  color=RED),
        dict(label="Foster",          lift=25,  color=BLUE),
        dict(label="Rainbow S",       lift=6,   color=RED),
    ]).sort_values("lift", ascending=True)

    fig_lift = go.Figure()
    fig_lift.add_trace(go.Bar(
        x=lift_data["lift"], y=lift_data["label"], orientation="h",
        marker_color=lift_data["color"].tolist(),
        text=[f"+{v:.0f}%" for v in lift_data["lift"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Weekend lift: +%{x:.0f}%<extra></extra>",
    ))
    fig_defaults(fig_lift, height=300)
    fig_lift.update_layout(
        xaxis=dict(title=dict(text="Weekend revenue premium vs weekday avg (%)"), ticksuffix="%"),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    st.plotly_chart(fig_lift, width="stretch")

    # F7: Revenue efficiency index
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 7 — Revenue generated per 100 observed visits</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Efficiency metric: post-Metropolis revenue divided by total observed '
                'visits (paid + grace exits) × 100. Captures how much revenue the system '
                'extracts per visit regardless of absolute traffic volume.</p>',
                unsafe_allow_html=True)

    eff_data = pd.DataFrame([
        dict(label="North Ave Beach",  eff=1356.72, color=BLUE),
        dict(label="Wilson",           eff=489.34,  color=BLUE),
        dict(label="55th/S.Shore Dr",  eff=518.48,  color=AMBER),
        dict(label="MSI East",         eff=885.03,  color=TEAL),
        dict(label="MSI South",        eff=464.00,  color=TEAL),
        dict(label="Waveland",         eff=373.71,  color=BLUE),
        dict(label="Foster",           eff=240.33,  color=BLUE),
        dict(label="Oakwood Beach",    eff=227.83,  color=AMBER),
        dict(label="Rainbow S",        eff=88.18,   color=RED),
        dict(label="Rainbow N",        eff=73.21,   color=RED),
    ]).sort_values("eff", ascending=True)

    fig_eff = go.Figure()
    fig_eff.add_trace(go.Bar(
        x=eff_data["eff"], y=eff_data["label"], orientation="h",
        marker_color=eff_data["color"].tolist(),
        text=[f"${v:,.0f}" for v in eff_data["eff"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>$%{x:,.0f} per 100 visits<extra></extra>",
    ))
    fig_defaults(fig_eff, height=300)
    fig_eff.update_layout(
        xaxis=dict(title=dict(text="Revenue per 100 observed visits ($)"), tickprefix="$"),
        margin=dict(l=10, r=80, t=10, b=10),
    )
    st.plotly_chart(fig_eff, width="stretch")
    st.markdown("""
    <div class="callout callout-red">
      North Avenue Beach generates $1,357 per 100 observed visits. Rainbow Beach North
      generates $73 — an 18.5:1 efficiency gap. Even accounting for lower traffic volume,
      the system extracts far less revenue per observed visit at Rainbow Beach than at
      any other lot.
    </div>
    """, unsafe_allow_html=True)

    # Relative performance scorecard
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Relative performance scorecard — within this 10-lot system only</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Composite score: revenue/day percentile (40%) + '
                'revenue/transaction percentile (30%) − grace-exit percentile (30%). '
                'Scores reflect relative ranking within this dataset only — a high score '
                'means best in this system, not objectively strong performance.</p>',
                unsafe_allow_html=True)

    import numpy as np
    sc_raw = pd.DataFrame([
        dict(label="MSI East",        rev_day=1534, rev_txn=21.37, grace=58.6),
        dict(label="North Ave Beach", rev_day=582,  rev_txn=17.30, grace=21.8),
        dict(label="MSI South",       rev_day=598,  rev_txn=7.35,  grace=37.6),
        dict(label="Waveland",        rev_day=247,  rev_txn=7.13,  grace=47.6),
        dict(label="Oakwood Beach",   rev_day=199,  rev_txn=5.19,  grace=56.5),
        dict(label="Wilson",          rev_day=178,  rev_txn=7.06,  grace=30.7),
        dict(label="55th/S.Shore Dr", rev_day=40,   rev_txn=5.98,  grace=13.4),
        dict(label="Foster",          rev_day=26,   rev_txn=6.26,  grace=61.9),
        dict(label="Rainbow N",       rev_day=27,   rev_txn=5.46,  grace=86.6),
        dict(label="Rainbow S",       rev_day=16,   rev_txn=5.10,  grace=82.7),
    ])
    def pct_rank(s): return s.rank(pct=True)*100
    sc_raw["score"] = (pct_rank(sc_raw["rev_day"])*0.40 +
                       pct_rank(sc_raw["rev_txn"])*0.30 +
                       pct_rank(sc_raw["grace"].max()-sc_raw["grace"])*0.30).round(1)
    sc_raw = sc_raw.sort_values("score", ascending=False).reset_index(drop=True)
    sc_raw["rank"] = range(1, len(sc_raw)+1)
    sc_raw["stars"] = sc_raw["score"].apply(lambda s: "★"*int(s/100*5)+"☆"*(5-int(s/100*5)))
    sc_raw["tier"] = sc_raw["score"].apply(lambda s:
        "High-performing" if s >= 70 else "Above average" if s >= 50 else
        "Below average" if s >= 30 else "High friction / low revenue")

    disp_sc = sc_raw[["rank","label","score","stars","tier","rev_day","rev_txn","grace"]].copy()
    disp_sc.columns = ["Rank","Location","Score (0-100)","Rating","Tier",
                        "Rev/Day ($)","Rev/Transaction ($)","Grace Exit %"]
    disp_sc["Rev/Day ($)"] = disp_sc["Rev/Day ($)"].apply(lambda v: f"${v:,.0f}")
    disp_sc["Rev/Transaction ($)"] = disp_sc["Rev/Transaction ($)"].apply(lambda v: f"${v:.2f}")
    disp_sc["Grace Exit %"] = disp_sc["Grace Exit %"].apply(lambda v: f"{v:.1f}%")
    st.dataframe(disp_sc, use_container_width=True, hide_index=True)

    # Records still needed
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Records still needed to evaluate the Metropolis system</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="callout callout-blue">
      The following records would allow determination of whether the observed patterns reflect
      registration friction, enforcement practices, visitor behavior, or other operational factors.
      None have been disclosed by CPkD to date.
    </div>
    """, unsafe_allow_html=True)

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.markdown("""<div class="finding"><p class="finding-num">Registration and payment</p>
        <p class="finding-body">Registration starts vs completions · Failed or abandoned
        registrations · Declined payment transactions · Average registration completion time ·
        Number of repeat vs one-time registrants per lot</p></div>""", unsafe_allow_html=True)
    with rc2:
        st.markdown("""<div class="finding"><p class="finding-num">Access and equity</p>
        <p class="finding-body">ADA accessibility review · Language-access assessment ·
        Cash or non-smartphone payment alternatives · Customer service complaints by location ·
        Enforcement data and citation rates by lot</p></div>""", unsafe_allow_html=True)
    with rc3:
        st.markdown("""<div class="finding"><p class="finding-num">Operations and visits</p>
        <p class="finding-body">Average dwell time for grace exits · Visitor surveys or exit
        interviews · Revenue allocation by lot · Repeat visitor rates · Equity impact assessment ·
        Pre-implementation community engagement records</p></div>""", unsafe_allow_html=True)

    # Conclusion
    st.markdown("""
    <div class="callout callout-amber" style="margin-top:1rem;">
      <b>Conclusion based on currently available records:</b> The Metropolis system shows
      materially different outcomes across locations. Rainbow Beach combines unusually high
      short-stay exit activity (86.6% grace rate, 6.46 grace exits per paid transaction)
      with extremely low revenue generation ($73 per 100 observed visits, $27/day average).
      The available data cannot determine whether this reflects registration friction, visitor
      behavior, enforcement practices, or other operational factors. Resolving those questions
      requires records that CPkD has not yet disclosed. The pattern is consistent with — but
      does not prove — that the system functions as an access barrier at Rainbow Beach rather
      than a revenue tool.
    </div>
    <p class="src">All analyses use post-Metropolis-go-live data from CPkD FOIA R-6663.
    Performance scores are relative within this 10-lot system only.
    Analysis: Ana Marija Soković, PhD, MBA.</p>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 8 · BEFORE & AFTER METROPOLIS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[7]:

    st.markdown("""
    <div class="callout callout-blue">
      <b>Research question:</b> How did paid parking activity change following implementation
      of the Metropolis parking system across CPkD parking lots, and were those changes
      consistent across locations?
      <br><br>
      <b>Methodology:</b> For each lot, average daily paid transactions and revenue were calculated
      for the pre-Metropolis period (matched equivalent duration immediately before go-live)
      and the post-Metropolis period (go-live through May 7, 2026). Equivalent calendar-window
      comparisons minimize seasonal effects. Unlike revenue, which can change due to pricing or
      visitor behavior, the number of paid transactions provides a more direct measure of how
      many vehicles actually paid to park.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="kpi-grid">
      <div class="kpi kpi-red">
        <p class="kpi-val">-84.2%</p>
        <p class="kpi-lbl">North Ave Beach paid transactions</p>
        <p class="kpi-note">211/day before Metropolis → 33/day after. CPkD said Metropolis would improve compliance.</p>
      </div>
      <div class="kpi kpi-red">
        <p class="kpi-val">-83.7%</p>
        <p class="kpi-lbl">55th/South Shore paid transactions</p>
        <p class="kpi-note">41/day before → 6.7/day after. Largest South Side lot decline.</p>
      </div>
      <div class="kpi kpi-blue">
        <p class="kpi-val">+214%</p>
        <p class="kpi-lbl">MSI South paid transactions</p>
        <p class="kpi-note">25.6/day before → 80.6/day after. Museum lots grew substantially.</p>
      </div>
      <div class="kpi kpi-amber">
        <p class="kpi-val">7 of 10</p>
        <p class="kpi-lbl">Lots where revenue/transaction declined</p>
        <p class="kpi-note">Average ticket fell at most lots after Metropolis activation.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Finding 1: Paid transaction change
    st.markdown('<p class="sec-head" style="margin-top:0.5rem;">Finding 1 — Change in average daily paid transactions after Metropolis</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="callout callout-amber">
      <b>Important note on Rainbow Beach:</b> Rainbow Beach North showed +1,777% and South +2,329%
      in paid transactions — but these figures reflect a near-zero baseline under the prior
      voluntary system (0.3 and 0.1 transactions/day respectively). In absolute terms, Rainbow
      Beach went from essentially no recorded paid parking to 4.9 and 3.2 paid transactions/day —
      still the lowest in the system. The percentage change is technically accurate but misleading
      as a measure of Metropolis impact.
    </div>
    """, unsafe_allow_html=True)

    txn_data = pd.DataFrame([
        dict(label="North Ave Beach",  pre=211.2, post=33.4,  chg=-84.2, area="North Side"),
        dict(label="55th/S.Shore Dr",  pre=41.0,  post=6.7,   chg=-83.7, area="South Side"),
        dict(label="Foster",           pre=8.6,   post=4.1,   chg=-51.6, area="North Side"),
        dict(label="Waveland",         pre=64.5,  post=34.4,  chg=-46.6, area="North Side"),
        dict(label="Oakwood Beach",    pre=56.8,  post=38.0,  chg=-33.0, area="South Side"),
        dict(label="Wilson",           pre=22.1,  post=25.0,  chg=+13.1, area="North Side"),
        dict(label="MSI East",         pre=42.8,  post=71.2,  chg=+66.4, area="Museum Campus"),
        dict(label="MSI South",        pre=25.6,  post=80.6,  chg=+214.4,area="Museum Campus"),
    ]).sort_values("chg", ascending=True)

    area_colors = {"North Side": BLUE, "South Side": AMBER, "Museum Campus": TEAL, "7th Ward": RED}

    t1c, t2c = st.columns([2, 1])
    with t1c:
        st.markdown('<p class="sec-sub">% change in avg daily paid transactions '
                    '(pre vs post-Metropolis equivalent period). Rainbow Beach excluded '
                    '— near-zero baseline makes % change misleading.</p>',
                    unsafe_allow_html=True)
        fig_txn = go.Figure()
        fig_txn.add_trace(go.Bar(
            x=txn_data["chg"], y=txn_data["label"], orientation="h",
            marker_color=[RED if v < 0 else GREEN for v in txn_data["chg"]],
            text=[f"{v:+.1f}%" for v in txn_data["chg"]],
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Transaction change: %{x:+.1f}%<extra></extra>",
        ))
        fig_txn.add_vline(x=0, line_color=GREY, line_width=1)
        fig_defaults(fig_txn, height=280)
        fig_txn.update_layout(
            xaxis=dict(title=dict(text="% change in avg daily paid transactions"), ticksuffix="%"),
            margin=dict(l=10, r=70, t=10, b=10),
        )
        st.plotly_chart(fig_txn, width="stretch")

    with t2c:
        st.markdown('<p class="sec-sub">Absolute daily averages before and after Metropolis</p>',
                    unsafe_allow_html=True)
        abs_data = pd.DataFrame([
            dict(label="North Ave Beach",  pre=211.2, post=33.4),
            dict(label="55th/S.Shore Dr",  pre=41.0,  post=6.7),
            dict(label="Foster",           pre=8.6,   post=4.1),
            dict(label="Waveland",         pre=64.5,  post=34.4),
            dict(label="Oakwood Beach",    pre=56.8,  post=38.0),
            dict(label="Wilson",           pre=22.1,  post=25.0),
            dict(label="MSI East",         pre=42.8,  post=71.2),
            dict(label="MSI South",        pre=25.6,  post=80.6),
            dict(label="Rainbow N",        pre=0.3,   post=4.9),
            dict(label="Rainbow S",        pre=0.1,   post=3.2),
        ]).sort_values("post", ascending=True)
        fig_abs = go.Figure()
        fig_abs.add_trace(go.Bar(
            name="Before", x=abs_data["pre"], y=abs_data["label"], orientation="h",
            marker_color=GREY, opacity=0.6,
            hovertemplate="<b>%{y}</b><br>Before: %{x:.1f}/day<extra></extra>",
        ))
        fig_abs.add_trace(go.Bar(
            name="After", x=abs_data["post"], y=abs_data["label"], orientation="h",
            marker_color=BLUE, opacity=0.85,
            hovertemplate="<b>%{y}</b><br>After: %{x:.1f}/day<extra></extra>",
        ))
        fig_defaults(fig_abs, height=320)
        fig_abs.update_layout(
            barmode="overlay",
            xaxis=dict(title=dict(text="Avg paid transactions/day")),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_abs, width="stretch")

    # Finding 2: Revenue change
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 2 — Change in average daily revenue mirrors transaction decline</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Revenue declined at most lots following Metropolis go-live, '
                'consistent with the transaction declines in Finding 1. Where revenue declined '
                'proportionally more than transactions, the average ticket size also fell.</p>',
                unsafe_allow_html=True)

    rev_chg_data = pd.DataFrame([
        dict(label="North Ave Beach",  txn_chg=-84.2, rev_chg=-89.8),
        dict(label="55th/S.Shore Dr",  txn_chg=-83.7, rev_chg=-89.5),
        dict(label="Foster",           txn_chg=-51.6, rev_chg=-60.1),
        dict(label="Waveland",         txn_chg=-46.6, rev_chg=-60.4),
        dict(label="Oakwood Beach",    txn_chg=-33.0, rev_chg=-50.7),
        dict(label="Wilson",           txn_chg=+13.1, rev_chg=-13.2),
        dict(label="MSI East",         txn_chg=+66.4, rev_chg=+55.5),
        dict(label="MSI South",        txn_chg=+214.4,rev_chg=+155.0),
    ]).sort_values("txn_chg", ascending=True)

    fig_rev2 = go.Figure()
    fig_rev2.add_trace(go.Scatter(
        x=rev_chg_data["txn_chg"], y=rev_chg_data["rev_chg"],
        mode="markers+text",
        marker=dict(size=[14 if v < -50 else 10 for v in rev_chg_data["txn_chg"]],
                   color=[RED if v < 0 else GREEN for v in rev_chg_data["txn_chg"]],
                   opacity=0.85, line=dict(width=1, color="white")),
        text=rev_chg_data["label"],
        textposition="top center",
        textfont=dict(size=9),
        hovertemplate="<b>%{text}</b><br>Transactions: %{x:+.1f}%<br>Revenue: %{y:+.1f}%<extra></extra>",
    ))
    # Reference line y=x (perfect correlation)
    fig_rev2.add_trace(go.Scatter(
        x=[-100, 250], y=[-100, 250], mode="lines",
        line=dict(color=GREY, width=1, dash="dash"),
        showlegend=False, name="Perfect correlation",
        hoverinfo="skip",
    ))
    fig_rev2.add_annotation(x=150, y=130, text="If above line: revenue fell<br>more than transactions",
                            showarrow=False, font=dict(size=9, color=GREY))
    fig_defaults(fig_rev2, height=360)
    fig_rev2.update_layout(
        xaxis=dict(title=dict(text="Change in paid transactions (%)"), ticksuffix="%"),
        yaxis=dict(title=dict(text="Change in revenue (%)"), ticksuffix="%"),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_rev2, width="stretch")

    # Finding 3: Revenue per transaction
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 3 — Revenue per transaction declined at most lots</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Average ticket size before and after Metropolis. '
                'A decline suggests either pricing changes, shorter stays, or a shift in visitor '
                'type. Only MSI East maintained a high average ticket ($21.37 after).</p>',
                unsafe_allow_html=True)

    rpt_data = pd.DataFrame([
        dict(label="North Ave Beach",  pre_rpt=26.94, post_rpt=17.30, color=BLUE),
        dict(label="MSI East",         pre_rpt=22.88, post_rpt=21.37, color=TEAL),
        dict(label="Wilson",           pre_rpt=9.20,  post_rpt=7.06,  color=BLUE),
        dict(label="Waveland",         pre_rpt=9.59,  post_rpt=7.13,  color=BLUE),
        dict(label="MSI South",        pre_rpt=9.07,  post_rpt=7.35,  color=TEAL),
        dict(label="55th/S.Shore Dr",  pre_rpt=9.25,  post_rpt=5.98,  color=AMBER),
        dict(label="Foster",           pre_rpt=7.59,  post_rpt=6.26,  color=BLUE),
        dict(label="Oakwood Beach",    pre_rpt=7.04,  post_rpt=5.19,  color=AMBER),
        dict(label="Rainbow S",        pre_rpt=7.13,  post_rpt=5.10,  color=RED),
        dict(label="Rainbow N",        pre_rpt=5.05,  post_rpt=5.46,  color=RED),
    ]).sort_values("pre_rpt", ascending=True)

    fig_rpt = go.Figure()
    fig_rpt.add_trace(go.Bar(
        name="Before Metropolis", x=rpt_data["pre_rpt"], y=rpt_data["label"],
        orientation="h", marker_color=GREY, opacity=0.7,
        hovertemplate="<b>%{y}</b><br>Before: $%{x:.2f}<extra></extra>",
    ))
    fig_rpt.add_trace(go.Bar(
        name="After Metropolis", x=rpt_data["post_rpt"], y=rpt_data["label"],
        orientation="h", marker_color=BLUE, opacity=0.85,
        hovertemplate="<b>%{y}</b><br>After: $%{x:.2f}<extra></extra>",
    ))
    fig_defaults(fig_rpt, height=320)
    fig_rpt.update_layout(
        barmode="overlay",
        xaxis=dict(title=dict(text="Revenue per paid transaction ($)"), tickprefix="$"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_rpt, width="stretch")

    # Finding 4: Summary table
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Finding 4 — Full before/after comparison: all 10 lots</p>',
                unsafe_allow_html=True)

    summary_ba = pd.DataFrame([
        dict(lot="North Ave Beach",  pre_txn=211.2,post_txn=33.4, txn_chg=-84.2,
             pre_rev=5689.4,post_rev=578.3,rev_chg=-89.8,pre_rpt=26.94,post_rpt=17.30),
        dict(lot="55th/S.Shore Dr",  pre_txn=41.0, post_txn=6.7,  txn_chg=-83.7,
             pre_rev=379.3, post_rev=39.9, rev_chg=-89.5,pre_rpt=9.25, post_rpt=5.98),
        dict(lot="Foster",           pre_txn=8.6,  post_txn=4.1,  txn_chg=-51.6,
             pre_rev=65.0,  post_rev=25.9, rev_chg=-60.1,pre_rpt=7.59, post_rpt=6.26),
        dict(lot="Waveland",         pre_txn=64.5, post_txn=34.4, txn_chg=-46.6,
             pre_rev=618.7, post_rev=245.3,rev_chg=-60.4,pre_rpt=9.59, post_rpt=7.13),
        dict(lot="Oakwood Beach",    pre_txn=56.8, post_txn=38.0, txn_chg=-33.0,
             pre_rev=399.7, post_rev=197.2,rev_chg=-50.7,pre_rpt=7.04, post_rpt=5.19),
        dict(lot="Wilson",           pre_txn=22.1, post_txn=25.0, txn_chg=+13.1,
             pre_rev=203.3, post_rev=176.4,rev_chg=-13.2,pre_rpt=9.20, post_rpt=7.06),
        dict(lot="MSI East",         pre_txn=42.8, post_txn=71.2, txn_chg=+66.4,
             pre_rev=978.6, post_rev=1521.5,rev_chg=+55.5,pre_rpt=22.88,post_rpt=21.37),
        dict(lot="MSI South",        pre_txn=25.6, post_txn=80.6, txn_chg=+214.4,
             pre_rev=232.5, post_rev=593.0,rev_chg=+155.0,pre_rpt=9.07,post_rpt=7.35),
        dict(lot="Rainbow N",        pre_txn=0.3,  post_txn=4.9,  txn_chg=None,
             pre_rev=1.3,   post_rev=26.9, rev_chg=None,  pre_rpt=5.05, post_rpt=5.46),
        dict(lot="Rainbow S",        pre_txn=0.1,  post_txn=3.2,  txn_chg=None,
             pre_rev=0.9,   post_rev=16.3, rev_chg=None,  pre_rpt=7.13, post_rpt=5.10),
    ])

    disp_ba = summary_ba.copy()
    disp_ba["pre_txn"]  = disp_ba["pre_txn"].apply(lambda v: f"{v:.1f}")
    disp_ba["post_txn"] = disp_ba["post_txn"].apply(lambda v: f"{v:.1f}")
    disp_ba["txn_chg"]  = disp_ba["txn_chg"].apply(lambda v: f"{v:+.1f}%" if v is not None else "† near-zero base")
    disp_ba["pre_rev"]  = disp_ba["pre_rev"].apply(lambda v: f"${v:,.0f}")
    disp_ba["post_rev"] = disp_ba["post_rev"].apply(lambda v: f"${v:,.0f}")
    disp_ba["rev_chg"]  = disp_ba["rev_chg"].apply(lambda v: f"{v:+.1f}%" if v is not None else "† near-zero base")
    disp_ba["pre_rpt"]  = disp_ba["pre_rpt"].apply(lambda v: f"${v:.2f}")
    disp_ba["post_rpt"] = disp_ba["post_rpt"].apply(lambda v: f"${v:.2f}")
    disp_ba = disp_ba.rename(columns={
        "lot":"Location","pre_txn":"Pre Txn/Day","post_txn":"Post Txn/Day","txn_chg":"Txn Change",
        "pre_rev":"Pre Rev/Day","post_rev":"Post Rev/Day","rev_chg":"Rev Change",
        "pre_rpt":"Pre $/Txn","post_rpt":"Post $/Txn"
    })
    st.dataframe(disp_ba, use_container_width=True, hide_index=True)
    st.markdown('<p class="src">† Rainbow Beach near-zero base: prior voluntary system recorded '
                '0.3 and 0.1 paid transactions/day. Percentage change is technically accurate '
                'but misleading as a measure of Metropolis impact.</p>', unsafe_allow_html=True)

    # What we can and cannot conclude
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("""
        <div class="finding" style="margin-top:1rem;">
          <p class="finding-num">What this analysis can conclude</p>
          <p class="finding-body">Paid parking activity declined substantially at 5 of 8 comparable
          lots after Metropolis go-live — including North Avenue Beach (-84.2%) and 55th/South Shore
          (-83.7%). Two museum-oriented lots grew substantially. Revenue per transaction declined at
          7 of 10 lots. The system produced highly uneven outcomes across locations. CPkD deployed
          Metropolis to improve "low compliance with voluntary payment systems" — at most community
          lots, paid transactions fell rather than rose.</p>
        </div>
        """, unsafe_allow_html=True)
    with cc2:
        st.markdown("""
        <div class="finding" style="margin-top:1rem;">
          <p class="finding-num">What this analysis cannot conclude</p>
          <p class="finding-body">This analysis measures changes in paid parking activity,
          not total park visitation. Visitors may have arrived by transit, bicycle, or on foot;
          been dropped off; parked elsewhere; used the grace period; or changed behavior in other
          ways. A decline in paid transactions does not necessarily mean fewer people visited the
          park. Determining whether overall visitation changed requires total vehicle-entry counts
          or visitor records that are not in the current dataset.</p>
        </div>
        """, unsafe_allow_html=True)

    # Future FOIA
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Future FOIA requests to complete this analysis</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="callout callout-blue">
      To determine whether changes in paid parking activity reflect changes in actual park
      visitation, the following records are needed from CPkD. None have been disclosed to date.
      <br><br>
      <b>Total vehicle entries and exits by lot</b> · <b>License plate recognition (LPR) entry counts</b> ·
      <b>Completed vs abandoned registration attempts</b> · <b>Failed payment transactions</b> ·
      <b>Customer complaints by location</b> · <b>Average dwell time before exiting</b> ·
      <b>Accessibility and equity evaluations</b> · <b>Enforcement and citation records</b> ·
      <b>Visitor surveys</b> · <b>Internal performance assessments</b>
      <br><br>
      Together, these records would allow researchers to distinguish between changes in
      paid parking behavior and changes in actual park visitation — providing a more
      complete evaluation of the Metropolis system.
    </div>
    <p class="src">Data: CPkD FOIA R-6663 (June 30, 2024 to May 7, 2026).
    Pre/post periods matched by equivalent duration immediately before and after each lot's
    Metropolis go-live date. Analysis: Ana Marija Soković, PhD, MBA.</p>
    """, unsafe_allow_html=True)


with tabs[8]:
    findings = [
        ("Finding 1",
         "Central lakefront and flagship-park investment concentration is structurally extreme",
         "Three parks — Grant, Lincoln, and Burnham — accounted for approximately $485M in "
         "reported project investment from 2011-2024, including major CDOT, Army Corps, and "
         "other outside-funded projects. Even after excluding identified transportation and "
         "shoreline co-investments, reported CPkD-controlled investment in these three parks "
         "exceeded the combined total for all South Region parks. The dataset does not "
         "consistently identify funding source for every line item; figures should be "
         "understood as total reported project cost, not solely CPkD discretionary spending."),

        ("Finding 2",
         "Park 566 and Rainbow Beach: the lowest-funded properties in the lakefront-facing comparison universe",
         "Within the defined universe of lakefront-facing CPkD parks analyzed using GIS polygon "
         "acreage, Park No. 566 (79th/USX, Far SE Side) received <b>$0.20/sq ft</b> and Rainbow "
         "Beach (South Shore, 7th Ward) received <b>$0.40/sq ft</b> in reported capital project "
         "investment from 2011-2024. Rogers Beach (North Side) received <b>$2.57/sq ft</b> — a "
         "6.4× gap within the same lakefront-access comparison class. These are reported "
         "capital-project dollars divided by GIS polygon area, not an annual operating-budget measure."),

        ("Finding 3",
         "The Marquette–Grant comparison is the clearest illustration of the investment disparity",
         "Marquette Park (323 acres, Southwest Side): $4M total = $0.28/sq ft. "
         "Grant Park (319 acres, downtown): $112M total = $8.07/sq ft. "
         "Nearly identical acreage. A <b>29× investment-density gap</b> per square foot. "
         "Both parks serve as major public anchors, but they carry different asset inventories, "
         "visitor volumes, and infrastructure obligations. The comparison illustrates the scale "
         "of disparity without claiming the parks are functionally identical."),

        ("Finding 4",
         "South Region parks carry the highest share of zero-funded pending projects",
         "South Region parks contain the largest identified share of projects labeled "
         "'Pending Funding' or 'Pre-Design,' including approximately 34 line items showing "
         "no allocated project cost. The dataset does not consistently disclose how long each "
         "project has remained pending — making project-age and prioritization records an "
         "important next disclosure. These communities have formally identified infrastructure "
         "needs that have not advanced to funded status."),

        ("Finding 5",
         "The 606 demonstrates the power — and uneven geography — of outside funding",
         "The 606 received approximately $91M, about 95% from outside sources including "
         "federal grants and philanthropic capital assembled through established nonprofit "
         "partnerships. It is a significant public asset, and the surrounding neighborhoods "
         "include historically disinvested Latino communities alongside areas experiencing "
         "rapid gentrification. It should not be presented as evidence that South and West Side "
         "park-capital inequities have been resolved. It demonstrates that large outside-funding "
         "pipelines can be assembled when sufficient institutional and political capacity exists — "
         "a capacity that is not evenly distributed across the park system."),

        ("Finding 6",
         "Programming gap compounds capital inequity",
         "South Region recorded 24% fewer programs and 38% fewer enrollments than North Region "
         "in the 2024 dataset (CPkD FOIA 5844 and 5902). Arts and cultural offerings indexed at "
         "approximately 56 relative to North=100; aquatics at approximately 63. These totals "
         "indicate a significant regional service gap, though per-capita, facility-adjusted, "
         "and wait-list analyses are needed to fully distinguish supply differences from "
         "population and infrastructure effects. System-wide loss of 30%+ arts and music "
         "teaching positions since 2010 (CPkD staffing records, SEIU 73 2025 report) "
         "fell disproportionately on South and West Side parks."),

        ("Finding 7",
         "Outside-funding dependency appears to create a capacity trap",
         "Parks supported by established conservancies, professional fundraising organizations, "
         "and institutional partners are better positioned to access federal and philanthropic "
         "capital. Many South Side PACs operate without comparable staff, fiscal sponsors, or "
         "grant-writing infrastructure. The resulting competitive system may reward existing "
         "organizational capacity rather than community need — though quantified comparison "
         "of external dollars won per park by region remains an important next analysis. "
         "Questions about whether CPkD's grant-approval and PAC-governance processes support "
         "or inhibit independent fundraising in disinvested communities are documented "
         "separately and remain under FOIA review."),

        ("Policy priorities capable of narrowing the gap",
         "Findings point toward several high-leverage interventions",
         "A transparent, needs-based capital plan prioritizing the highest-disparity parks "
         "would be a meaningful first step. A reasonable benchmark would be two or three "
         "major South Side investments comparable in scale to Gately Park's approximately "
         "$40-60M redevelopment. Candidate areas identified by the combined capital, "
         "programming, facility-condition, and population analysis include Englewood, "
         "Roseland, Washington Heights, Humboldt Park, and Douglas — though any final "
         "prioritization should be based on a published, community-validated scoring "
         "methodology, not a single dataset."),

        ("Finding 9",
         "CPkD reports expenditures but not a transparent prioritization methodology",
         "CPkD's public capital records show what projects received money, but they do not "
         "consistently disclose the comparative scoring, unmet-needs ranking, approval chain, "
         "funding-source strategy, or equity criteria used to decide which projects advanced. "
         "The recurring difficulty obtaining these records through FOIA is itself an "
         "accountability issue: the public can observe the outcomes but cannot readily "
         "reconstruct the decision rule. This applies to capital allocation, parking-gate "
         "rollout decisions, PAC governance, and shoreline planning alike."),
    ]

    c1, c2 = st.columns(2)
    for i, (num, title, body) in enumerate(findings):
        col = c1 if i % 2 == 0 else c2
        with col:
            st.markdown(f"""
            <div class="finding">
              <p class="finding-num">{num}</p>
              <p class="finding-title">{title}</p>
              <p class="finding-body">{body}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <p class="src">Capital data: CPkD Park Capital Projects 2011-2024 (April 2024).
    Per-sq-ft figures use GIS polygon acreage for lakefront parks, CPkD published acreage elsewhere.
    Programming data: SEIU Local 73 State of the Parks Revisited 2025 (Dr. Molly Hudgens, PhD),
    via CPkD FOIA 5844 and 5902 (Oct-Nov 2024).
    Parking data: CPkD FOIA R-6663 (Jun 2024-May 2026).
    Analysis: Ana Marija Soković, PhD, MBA.</p>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border:none;border-top:1px solid #d0dcea;margin:2.5rem 0 1rem;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
  <div>
    <p style="font-size:13px;font-weight:600;color:#0f2b52;margin:0 0 3px;">
      This report was prepared by Ana Marija Soković, PhD, MBA
    </p>
    <p style="font-size:11px;color:#4a5e78;margin:0;line-height:1.6;">
      Lead Computational Scientist, University of Illinois Chicago &nbsp;·&nbsp;
      Chair, Chicago Women in High Performance Computing
    </p>
  </div>
  <p style="font-size:11px;color:#7a90a8;line-height:1.7;margin:0;text-align:right;">
    Data: CPkD Capital Projects 2011–2024 (April 2024) &nbsp;·&nbsp;
    SEIU Local 73 State of the Parks 2025 &nbsp;·&nbsp;
    Built with Streamlit + Plotly<br>
    Lakefront $/sq ft confirmed via independent GIS-normalized analysis &nbsp;·&nbsp;
    For public information and advocacy purposes
  </p>
</div>
""", unsafe_allow_html=True)
