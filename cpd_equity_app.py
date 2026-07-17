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
# TAB 6 · PARKING GATES EQUITY ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:

    st.markdown("""
    <div class="callout callout-amber">
      <b>Data source:</b> CPkD FOIA R-6663 (June 30, 2024 to May 7, 2026) — Metropolis Vision
      System daily revenue, vehicle quantity, and 15-minute grace period exits for all 10 gated
      CPkD parking lots. CPkD New Parking System Quick Facts (2026). Analysis: Ana Marija Soković, PhD, MBA.
      <br><br>
      <b>Methodological note:</b> The Metropolis system replaced a prior voluntary payment system.
      Go-live dates range from November 2025 to January 2026. Revenue figures before each lot's
      go-live date reflect the legacy system. Post-go-live figures are analyzed separately.
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="kpi-grid">
      <div class="kpi kpi-red">
        <p class="kpi-val">86.6%</p>
        <p class="kpi-lbl">Rainbow Beach North grace-exit share</p>
        <p class="kpi-note">6.46 free exits per paid transaction vs 0.28 at North Avenue Beach</p>
      </div>
      <div class="kpi kpi-red">
        <p class="kpi-val">-72.5%</p>
        <p class="kpi-lbl">Foster Beach revenue year-over-year</p>
        <p class="kpi-note">Same calendar window post-Metropolis vs prior year. Transactions -70.8%.</p>
      </div>
      <div class="kpi kpi-amber">
        <p class="kpi-val">0.8% / 1.0%</p>
        <p class="kpi-lbl">Rainbow Beach share of revenue</p>
        <p class="kpi-note">Full dataset (both systems): $38,485 of $5.09M · Post-Metropolis only: $4,319 of $446K</p>
      </div>
      <div class="kpi kpi-blue">
        <p class="kpi-val">+17.4%</p>
        <p class="kpi-lbl">MSI East revenue growth post-Metropolis</p>
        <p class="kpi-note">Museum-oriented lots grew. Community park lots diverged sharply.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FINDING P1 ────────────────────────────────────────────────────────────
    st.markdown("""
    <p class="sec-head" style="margin-top:0.5rem;">
      Finding P1 — Rainbow Beach records exceptionally high short-stay exit activity
    </p>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What the data show</p>
          <p class="finding-body">At Rainbow Beach North, <b>86.6% of recorded observed visits
          ended within the 15-minute grace period</b> — 6.46 free exits per paid transaction.
          At North Avenue Beach: 21.8% grace share, 0.28 exits per paid transaction.
          Rainbow Beach South: 82.7% grace share.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What this may indicate</p>
          <p class="finding-body">The pattern is consistent with registration friction,
          visitors deciding not to remain, pickup/drop-off use, or very short visits.
          The available data does not distinguish among these explanations. All are
          plausible given the neighborhood demographics and the registration requirements.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What remains unknown</p>
          <p class="finding-body">CPkD has not disclosed registration-start vs completion
          rates, abandoned registrations, payment failures, average dwell time for grace
          exits, or customer service complaints by location. Those records are necessary
          to establish why visitors are leaving within 15 minutes.</p>
        </div>
        """, unsafe_allow_html=True)

    # Grace charts
    grace_data = pd.DataFrame([
        dict(lot="Rainbow Beach North",         grace_pct=86.6, ratio=6.46, side="7th Ward"),
        dict(lot="Rainbow Beach South",         grace_pct=82.7, ratio=4.78, side="7th Ward"),
        dict(lot="Foster",                      grace_pct=61.9, ratio=1.63, side="North Side"),
        dict(lot="MSI East",                    grace_pct=58.6, ratio=1.42, side="Museum Campus"),
        dict(lot="Oakwood Beach 39th St",       grace_pct=56.5, ratio=1.30, side="South Side"),
        dict(lot="Waveland",                    grace_pct=47.6, ratio=0.91, side="North Side"),
        dict(lot="Wilson",                      grace_pct=30.7, ratio=0.44, side="North Side"),
        dict(lot="MSI South",                   grace_pct=37.6, ratio=0.60, side="Museum Campus"),
        dict(lot="North Avenue Beach",          grace_pct=21.8, ratio=0.28, side="North Side"),
        dict(lot="55th St / South Shore Dr",    grace_pct=13.4, ratio=0.24, side="South Side"),
    ]).sort_values("grace_pct", ascending=True)

    grace_colors = {"7th Ward": RED, "North Side": BLUE, "South Side": AMBER, "Museum Campus": TEAL}

    gc1, gc2 = st.columns(2)
    with gc1:
        st.markdown('<p class="sec-sub">Grace-period exits as % of total visits per lot</p>',
                    unsafe_allow_html=True)
        fig_g1 = go.Figure()
        fig_g1.add_trace(go.Bar(
            x=grace_data["grace_pct"], y=grace_data["lot"], orientation="h",
            marker_color=[grace_colors[s] for s in grace_data["side"]],
            text=[f"{v:.1f}%" for v in grace_data["grace_pct"]],
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Grace: %{x:.1f}%<extra></extra>",
        ))
        fig_defaults(fig_g1, height=310)
        fig_g1.update_layout(
            xaxis=dict(title=dict(text="Grace exits as % of all visits"), ticksuffix="%", range=[0,100]),
            margin=dict(l=10, r=60, t=10, b=10),
        )
        st.plotly_chart(fig_g1, width="stretch")

    with gc2:
        st.markdown('<p class="sec-sub">Grace exits per 1 paid transaction</p>',
                    unsafe_allow_html=True)
        r_sorted = grace_data.sort_values("ratio", ascending=True)
        fig_g2 = go.Figure()
        fig_g2.add_trace(go.Bar(
            x=r_sorted["ratio"], y=r_sorted["lot"], orientation="h",
            marker_color=[grace_colors[s] for s in r_sorted["side"]],
            text=[f"{v:.2f}x" for v in r_sorted["ratio"]],
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>%{x:.2f} grace per paid<extra></extra>",
        ))
        fig_defaults(fig_g2, height=310)
        fig_g2.update_layout(
            xaxis=dict(title=dict(text="Grace exits per paid visit")),
            margin=dict(l=10, r=60, t=10, b=10),
        )
        st.plotly_chart(fig_g2, width="stretch")

    st.markdown("""
    <div class="callout callout-blue" style="margin-top:0.5rem;">
      <b>Note on observed visits:</b> "Observed visits" in this analysis = paid transactions +
      recorded 15-minute grace-period exits. This may not capture every vehicle movement or
      transaction category recorded by Metropolis. CPkD has not disclosed whether these two
      sheets represent exhaustive categories of all lot activity.
    </div>
    """, unsafe_allow_html=True)

    # ── FINDING P2 ────────────────────────────────────────────────────────────
    st.markdown("""
    <p class="sec-head" style="margin-top:1rem;">
      Finding P2 — Financial outcomes after Metropolis go-live vary sharply by location
    </p>
    """, unsafe_allow_html=True)

    yc1, yc2, yc3 = st.columns(3)
    with yc1:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What the data show</p>
          <p class="finding-body">Same-calendar-window year-over-year comparisons show revenue
          declines at Foster (-72.5%), 55th/South Shore (-30.9%), and Wilson (-19.4%), while
          MSI East (+17.4%), Oakwood (+24.1%), and MSI South (+43.1%) increased.
          Foster transactions fell 70.8%.</p>
        </div>
        """, unsafe_allow_html=True)
    with yc2:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What this may indicate</p>
          <p class="finding-body">The results vary materially by location. Both MSI lots and
          Oakwood increased, while Foster, 55th/South Shore, and Wilson declined substantially.
          North Avenue and Waveland were approximately flat. The pattern does not align neatly
          with a simple North–South division. The Foster result is severe and warrants
          investigation.</p>
        </div>
        """, unsafe_allow_html=True)
    with yc3:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What remains unknown</p>
          <p class="finding-body">Weather variation, special events, nearby construction,
          and operational differences must be evaluated before attributing results solely
          to the parking system. CPkD has not provided visit-purpose data, visitor surveys,
          or an equity impact assessment for any lot.</p>
        </div>
        """, unsafe_allow_html=True)

    yoy_plot = pd.DataFrame([
        dict(lot="MSI South",               rev_chg=43.1),
        dict(lot="Oakwood Beach 39th St",   rev_chg=24.1),
        dict(lot="MSI East",                rev_chg=17.4),
        dict(lot="North Avenue Beach",      rev_chg=-4.1),
        dict(lot="Waveland",                rev_chg=-3.6),
        dict(lot="Wilson",                  rev_chg=-19.4),
        dict(lot="55th St / South Shore Dr",rev_chg=-30.9),
        dict(lot="Foster",                  rev_chg=-72.5),
    ]).sort_values("rev_chg", ascending=True)

    st.markdown('<p class="sec-sub">Year-over-year revenue change: post-Metropolis period vs same calendar window '
                'prior year. Rainbow Beach excluded — prior voluntary system had near-zero recorded revenue.</p>',
                unsafe_allow_html=True)
    fig_yoy = go.Figure()
    fig_yoy.add_trace(go.Bar(
        x=yoy_plot["rev_chg"], y=yoy_plot["lot"], orientation="h",
        marker_color=[RED if v < 0 else GREEN for v in yoy_plot["rev_chg"]],
        text=[f"{v:+.1f}%" for v in yoy_plot["rev_chg"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>%{x:+.1f}%<extra></extra>",
    ))
    fig_yoy.add_vline(x=0, line_color=GREY, line_width=1)
    fig_defaults(fig_yoy, height=280)
    fig_yoy.update_layout(
        xaxis=dict(title=dict(text="Year-over-year revenue change (%)"), ticksuffix="%"),
        margin=dict(l=10, r=70, t=10, b=10),
    )
    st.plotly_chart(fig_yoy, width="stretch")

    # ── FINDING P3 ────────────────────────────────────────────────────────────
    st.markdown("""
    <p class="sec-head" style="margin-top:1rem;">
      Finding P3 — Digital-only registration creates an unmeasured equity risk
    </p>
    """, unsafe_allow_html=True)

    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What the data show</p>
          <p class="finding-body">Metropolis requires first-time users to complete
          a phone-based registration: QR code scan, phone number confirmation,
          vehicle information, and payment details. CPkD calls this "easy sign-up."
          No cash alternative or non-smartphone pathway is described in the Fact Sheet.</p>
        </div>
        """, unsafe_allow_html=True)
    with dc2:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What this may indicate</p>
          <p class="finding-body">The registration process creates plausible barriers for
          residents without smartphones, without payment cards, with limited digital
          proficiency, or who are seniors unfamiliar with QR-code flows. Rainbow Beach
          serves a community with a lower median household income (approximately $40K, ACS 2023)
          and a substantial older-adult population — making these access questions particularly
          important. The high grace-exit rate makes this an urgent question, but the available
          data do not confirm who is leaving or why.</p>
        </div>
        """, unsafe_allow_html=True)
    with dc3:
        st.markdown("""
        <div class="finding">
          <p class="finding-num">What CPkD has not disclosed</p>
          <p class="finding-body">Registration starts vs completions · Failed or abandoned
          registrations · Declined payments · Customer service complaints by location ·
          Cash or non-smartphone alternatives · ADA and language-access assessments ·
          Average dwell time for grace exits · Any equity impact assessment for the
          Metropolis system.</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Revenue tables ────────────────────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Revenue by lot: full dataset vs post-Metropolis go-live</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="callout callout-blue">
      The full-dataset figures (June 2024 to May 2026) combine revenue from the prior voluntary
      payment system and the Metropolis gate system. Most lots did not go live on Metropolis until
      late 2025 or January 2026. Post-go-live figures show only the Metropolis period. Both are
      shown below for transparency. CPkD states parking revenue supports districtwide programs
      but has not provided location-level revenue allocation records showing where each lot's
      revenue is spent.
    </div>
    """, unsafe_allow_html=True)

    rev_table = pd.DataFrame([
        dict(lot="North Avenue Beach",       area="North Side",           golive="Nov 24 2025",
             full_rev=2007285, post_rev=95418,  post_day=578,  grace_pct=21.8),
        dict(lot="MSI East",                 area="Museum Campus",        golive="Jan 7 2026",
             full_rev=1135272, post_rev=184103, post_day=1522, grace_pct=58.6),
        dict(lot="Foster",                   area="North Side",           golive="Jan 22 2026",
             full_rev=424173,  post_rev=2747,   post_day=26,   grace_pct=61.9),
        dict(lot="Waveland",                 area="North Side",           golive="Dec 24 2025",
             full_rev=369854,  post_rev=33111,  post_day=249,  grace_pct=47.6),
        dict(lot="MSI South",                area="Museum Campus",        golive="Jan 7 2026",
             full_rev=366584,  post_rev=71749,  post_day=593,  grace_pct=37.6),
        dict(lot="Wilson",                   area="North Side",           golive="Jan 7 2026",
             full_rev=304484,  post_rev=21345,  post_day=180,  grace_pct=30.7),
        dict(lot="Oakwood Beach 39th St",    area="South Side",           golive="Dec 18 2025",
             full_rev=238993,  post_rev=27807,  post_day=197,  grace_pct=56.5),
        dict(lot="55th St / South Shore Dr", area="South Side",           golive="Dec 17 2025",
             full_rev=209075,  post_rev=5667,   post_day=40,   grace_pct=13.4),
        dict(lot="Rainbow Beach North",      area="7th Ward (S. Shore)",  golive="Jan 28 2026",
             full_rev=21305,   post_rev=2692,   post_day=27,   grace_pct=86.6),
        dict(lot="Rainbow Beach South",      area="7th Ward (S. Shore)",  golive="Jan 28 2026",
             full_rev=17180,   post_rev=1627,   post_day=16,   grace_pct=82.7),
    ])

    disp = rev_table.copy()
    disp["full_rev"] = disp["full_rev"].apply(lambda v: f"${v:,.0f}")
    disp["post_rev"] = disp["post_rev"].apply(lambda v: f"${v:,.0f}")
    disp["post_day"] = disp["post_day"].apply(lambda v: f"${v:,.0f}")
    disp["grace_pct"]= disp["grace_pct"].apply(lambda v: f"{v:.1f}%")
    disp = disp.rename(columns={
        "lot":"Location","area":"Area","golive":"Metropolis Go-Live",
        "full_rev":"Full Dataset Revenue (Jun 2024-May 2026)",
        "post_rev":"Post-Go-Live Revenue","post_day":"Post-Go-Live $/Day",
        "grace_pct":"Grace Exit %"
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    st.markdown("""
    <p class="src">Source: CPkD FOIA R-6663, filed by Ana Marija Soković.
    Data period: June 30, 2024 to May 7, 2026.
    Year-over-year compares equivalent post-go-live calendar windows.
    CPkD Parking Fact Sheet: New Parking System Quick Facts (2026).</p>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# TAB 7 · PARKING GATES FINDINGS (ADVANCED ANALYSIS)
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:

    st.markdown("""
    <div class="callout callout-amber">
      Advanced analysis of Metropolis parking data from CPkD FOIA R-6663.
      All metrics use post-Metropolis-go-live data only. Quadrant and performance
      analyses are descriptive — they identify patterns that warrant further investigation
      rather than establishing causal explanations.
    </div>
    """, unsafe_allow_html=True)

    # ── 1. Quadrant plot ──────────────────────────────────────────────────────
    st.markdown('<p class="sec-head">Quadrant analysis: revenue/day vs grace-exit rate</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="callout callout-blue">
      <b>How to read this:</b> Each lot is plotted by its average daily post-Metropolis revenue
      (Y-axis) and grace-period exit rate (X-axis). Lots in the lower-right quadrant generate
      low revenue and show high grace-period activity — the combination most consistent with
      access friction or low visitor dwell time. Quadrant boundaries are set at system medians
      ($188/day revenue, 52.1% grace rate).
    </div>
    """, unsafe_allow_html=True)

    quad_data = pd.DataFrame([
        dict(label="North Ave Beach",  rev_day=582,  grace=21.8, quad="High rev / Low grace",  color=BLUE),
        dict(label="MSI East",         rev_day=1534, grace=58.6, quad="High rev / High grace", color=TEAL),
        dict(label="MSI South",        rev_day=598,  grace=37.6, quad="High rev / Low grace",  color=TEAL),
        dict(label="Waveland",         rev_day=247,  grace=47.6, quad="High rev / Low grace",  color=BLUE),
        dict(label="Oakwood Beach",    rev_day=199,  grace=56.5, quad="High rev / High grace", color=AMBER),
        dict(label="Wilson",           rev_day=178,  grace=30.7, quad="Low rev / Low grace",   color=BLUE),
        dict(label="55th/S.Shore Dr",  rev_day=40,   grace=13.4, quad="Low rev / Low grace",   color=AMBER),
        dict(label="Foster",           rev_day=26,   grace=61.9, quad="Low rev / High grace",  color=BLUE),
        dict(label="Rainbow N",        rev_day=27,   grace=86.6, quad="Low rev / High grace",  color=RED),
        dict(label="Rainbow S",        rev_day=16,   grace=82.7, quad="Low rev / High grace",  color=RED),
    ])

    fig_quad = go.Figure()

    # Quadrant shading
    fig_quad.add_shape(type="rect", x0=52.1, x1=100, y0=0,   y1=188,
                       fillcolor="rgba(176,98,0,0.07)", line=dict(width=0))
    fig_quad.add_shape(type="rect", x0=0,    x1=52.1, y0=0,   y1=188,
                       fillcolor="rgba(26,68,128,0.04)", line=dict(width=0))
    fig_quad.add_shape(type="rect", x0=0,    x1=52.1, y0=188, y1=1700,
                       fillcolor="rgba(26,107,60,0.05)", line=dict(width=0))
    fig_quad.add_shape(type="rect", x0=52.1, x1=100, y0=188, y1=1700,
                       fillcolor="rgba(27,108,168,0.05)", line=dict(width=0))

    # Median lines
    fig_quad.add_vline(x=52.1, line_dash="dash", line_color=GREY, line_width=1,
                       annotation_text="Median grace 52.1%", annotation_position="top right",
                       annotation_font=dict(size=9, color=GREY))
    fig_quad.add_hline(y=188, line_dash="dash", line_color=GREY, line_width=1,
                       annotation_text="Median $188/day", annotation_position="right",
                       annotation_font=dict(size=9, color=GREY))

    # Scatter
    for _, row in quad_data.iterrows():
        fig_quad.add_trace(go.Scatter(
            x=[row['grace']], y=[row['rev_day']],
            mode='markers+text',
            marker=dict(size=14 if 'Rainbow' in row['label'] else 10,
                       color=row['color'], opacity=0.85,
                       line=dict(width=1.5, color='white')),
            text=[row['label']],
            textposition='top center',
            textfont=dict(size=9, color=row['color']),
            name=row['label'],
            hovertemplate=f"<b>{row['label']}</b><br>Grace: {row['grace']:.1f}%<br>Rev/day: ${row['rev_day']:,.0f}<br>{row['quad']}<extra></extra>",
            showlegend=False,
        ))

    # Quadrant labels
    for txt, x, y in [("High rev / Low grace", 26, 1500), ("High rev / High grace", 75, 1500),
                       ("Low rev / Low grace", 26, 50),   ("Low rev / High grace", 75, 50)]:
        fig_quad.add_annotation(x=x, y=y, text=txt, showarrow=False,
                                font=dict(size=9, color=GREY), opacity=0.6)

    fig_defaults(fig_quad, height=420)
    fig_quad.update_layout(
        xaxis=dict(title=dict(text="Grace-exit rate (% of observed visits)"),
                   ticksuffix="%", range=[0, 100]),
        yaxis=dict(title=dict(text="Post-Metropolis avg revenue/day ($)"),
                   tickprefix="$"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_quad, width='stretch')

    # ── 2. Performance scorecard ──────────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Performance scorecard — all 10 lots ranked</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Score = revenue/day percentile (40%) + revenue/transaction '
                'percentile (30%) − grace-exit percentile (30%). Higher = better performing lot. '
                'Percentiles computed within this 10-lot Metropolis system only.</p>',
                unsafe_allow_html=True)

    scorecard_raw = [
        dict(label="MSI East",        rev_day=1534, rev_txn=21.37, grace=58.6),
        dict(label="MSI South",       rev_day=598,  rev_txn=7.35,  grace=37.6),
        dict(label="North Ave Beach", rev_day=582,  rev_txn=17.30, grace=21.8),
        dict(label="Waveland",        rev_day=247,  rev_txn=7.13,  grace=47.6),
        dict(label="Oakwood Beach",   rev_day=199,  rev_txn=5.19,  grace=56.5),
        dict(label="Wilson",          rev_day=178,  rev_txn=7.06,  grace=30.7),
        dict(label="55th/S.Shore Dr", rev_day=40,   rev_txn=5.98,  grace=13.4),
        dict(label="Foster",          rev_day=26,   rev_txn=6.26,  grace=61.9),
        dict(label="Rainbow N",       rev_day=27,   rev_txn=5.46,  grace=86.6),
        dict(label="Rainbow S",       rev_day=16,   rev_txn=5.10,  grace=82.7),
    ]
    sc_df = pd.DataFrame(scorecard_raw)

    import numpy as np
    def pct_rank(series):
        return series.rank(pct=True) * 100

    sc_df['rev_day_pct']  = pct_rank(sc_df['rev_day'])
    sc_df['rev_txn_pct']  = pct_rank(sc_df['rev_txn'])
    sc_df['grace_pct_inv']= pct_rank(sc_df['grace'].max() - sc_df['grace'])  # invert: lower grace = better
    sc_df['score'] = (sc_df['rev_day_pct']*0.40 + sc_df['rev_txn_pct']*0.30 + sc_df['grace_pct_inv']*0.30).round(1)
    sc_df = sc_df.sort_values('score', ascending=False).reset_index(drop=True)
    sc_df['rank'] = range(1, len(sc_df)+1)

    def stars(score):
        s = score/100*5
        full = int(s)
        return "★" * full + "☆" * (5 - full)

    sc_df['stars'] = sc_df['score'].apply(stars)
    sc_df['classification'] = sc_df.apply(lambda r: (
        "High-performing" if r['score'] >= 70 else
        "Above average" if r['score'] >= 50 else
        "Below average" if r['score'] >= 30 else
        "High friction / low revenue"
    ), axis=1)

    disp_sc = sc_df[['rank','label','score','stars','classification','rev_day','rev_txn','grace']].copy()
    disp_sc.columns = ['Rank','Location','Score (0-100)','Rating','Classification',
                        'Rev/Day ($)','Rev/Transaction ($)','Grace Exit %']
    disp_sc['Rev/Day ($)'] = disp_sc['Rev/Day ($)'].apply(lambda v: f"${v:,.0f}")
    disp_sc['Rev/Transaction ($)'] = disp_sc['Rev/Transaction ($)'].apply(lambda v: f"${v:.2f}")
    disp_sc['Grace Exit %'] = disp_sc['Grace Exit %'].apply(lambda v: f"{v:.1f}%")
    st.dataframe(disp_sc, use_container_width=True, hide_index=True)

    # ── 3. Pareto / revenue concentration ─────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Revenue concentration — Pareto analysis</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Post-Metropolis revenue by lot, cumulative. '
                'The top 3 lots account for 78.7% of all system revenue.</p>',
                unsafe_allow_html=True)

    pareto_data = pd.DataFrame([
        dict(label="MSI East",        rev=184103),
        dict(label="North Ave Beach", rev=95418),
        dict(label="MSI South",       rev=71749),
        dict(label="Waveland",        rev=33111),
        dict(label="Oakwood Beach",   rev=27807),
        dict(label="Wilson",          rev=21345),
        dict(label="55th/S.Shore Dr", rev=5667),
        dict(label="Foster",          rev=2747),
        dict(label="Rainbow N",       rev=2692),
        dict(label="Rainbow S",       rev=1627),
    ]).sort_values('rev', ascending=False).reset_index(drop=True)
    total_rev = pareto_data['rev'].sum()
    pareto_data['cum_pct'] = pareto_data['rev'].cumsum() / total_rev * 100
    pareto_data['rev_pct'] = pareto_data['rev'] / total_rev * 100
    lot_colors_p = [TEAL if 'MSI' in l else BLUE if l in ['North Ave Beach','Waveland','Wilson','Foster']
                    else RED if 'Rainbow' in l else AMBER for l in pareto_data['label']]

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=pareto_data['label'], y=pareto_data['rev_pct'],
        marker_color=lot_colors_p,
        name="% of total revenue",
        text=[f"{v:.1f}%" for v in pareto_data['rev_pct']],
        textposition='outside', textfont=dict(size=9),
        hovertemplate="<b>%{x}</b><br>%{y:.1f}% of system revenue<extra></extra>",
        yaxis='y',
    ))
    fig_pareto.add_trace(go.Scatter(
        x=pareto_data['label'], y=pareto_data['cum_pct'],
        mode='lines+markers',
        line=dict(color=BLUE, width=2),
        marker=dict(size=6, color=BLUE),
        name="Cumulative %",
        hovertemplate="<b>%{x}</b><br>Cumulative: %{y:.1f}%<extra></extra>",
        yaxis='y2',
    ))
    fig_pareto.add_hline(y=80, line_dash="dash", line_color=GREY, line_width=1, yref='y2',
                         annotation_text="80%", annotation_position="right",
                         annotation_font=dict(size=9, color=GREY))
    fig_defaults(fig_pareto, height=340)
    fig_pareto.update_layout(
        yaxis=dict(title=dict(text="Share of total revenue (%)"), ticksuffix="%"),
        yaxis2=dict(title=dict(text="Cumulative share (%)"), overlaying='y',
                    side='right', ticksuffix="%", range=[0, 105]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        margin=dict(l=10, r=60, t=20, b=60),
        barmode='group',
    )
    st.plotly_chart(fig_pareto, width='stretch')

    st.markdown("""
    <div class="callout callout-red">
      <b>Revenue concentration finding:</b> The top 3 lots (MSI East, North Avenue Beach,
      MSI South) account for 78.7% of all post-Metropolis system revenue. The bottom 4 lots
      — Foster, 55th/South Shore, Rainbow North, and Rainbow South — account for 2.9%
      combined. Two of those four lots are at Rainbow Beach in the 7th Ward.
    </div>
    """, unsafe_allow_html=True)

    # ── 4. Weekday vs weekend ─────────────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Weekday vs weekend revenue — post-Metropolis</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Weekend lift (how much more revenue a lot generates on weekends vs weekdays) '
                'varies dramatically by location. Rainbow Beach shows minimal weekend lift, '
                'suggesting it is not functioning as a weekend destination park.</p>',
                unsafe_allow_html=True)

    wkday_data = pd.DataFrame([
        dict(label="MSI East",        wkday=1188, wkend=2375),
        dict(label="MSI South",       wkday=317,  wkend=1299),
        dict(label="North Ave Beach", wkday=416,  wkend=999),
        dict(label="Waveland",        wkday=179,  wkend=414),
        dict(label="Oakwood Beach",   wkday=163,  wkend=284),
        dict(label="Wilson",          wkday=161,  wkend=217),
        dict(label="55th/S.Shore Dr", wkday=32,   wkend=60),
        dict(label="Foster",          wkday=24,   wkend=30),
        dict(label="Rainbow N",       wkday=25,   wkend=32),
        dict(label="Rainbow S",       wkday=16,   wkend=17),
    ]).sort_values('wkend', ascending=True)
    wkday_data['lift'] = (wkday_data['wkend'] - wkday_data['wkday']) / wkday_data['wkday'] * 100

    fig_wk = go.Figure()
    fig_wk.add_trace(go.Bar(
        name="Weekday avg", x=wkday_data['wkday'], y=wkday_data['label'],
        orientation='h', marker_color=GREY, opacity=0.7,
        hovertemplate="<b>%{y}</b><br>Weekday: $%{x:,.0f}<extra></extra>",
    ))
    fig_wk.add_trace(go.Bar(
        name="Weekend avg", x=wkday_data['wkend'], y=wkday_data['label'],
        orientation='h', marker_color=BLUE, opacity=0.85,
        hovertemplate="<b>%{y}</b><br>Weekend: $%{x:,.0f}<br>Lift: %{customdata:.0f}%<extra></extra>",
        customdata=wkday_data['lift'],
    ))
    fig_defaults(fig_wk, height=340)
    fig_wk.update_layout(
        barmode='overlay',
        xaxis=dict(title=dict(text="Average daily revenue ($)"), tickprefix="$"),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_wk, width='stretch')

    # ── 5. Seasonality ────────────────────────────────────────────────────────
    st.markdown('<p class="sec-head" style="margin-top:1rem;">Rainbow Beach monthly revenue since Metropolis go-live</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Rainbow Beach North post-go-live (January 28, 2026 onward). '
                'Spring months show some growth but absolute revenue remains minimal.</p>',
                unsafe_allow_html=True)

    rb_monthly = pd.DataFrame([
        dict(month="Feb 2026", rev=307.51),
        dict(month="Mar 2026", rev=994.65),
        dict(month="Apr 2026", rev=954.01),
        dict(month="May 2026", rev=416.86),  # partial month through May 7
    ])
    fig_sea = go.Figure()
    fig_sea.add_trace(go.Bar(
        x=rb_monthly['month'], y=rb_monthly['rev'],
        marker_color=[RED, RED, RED, AMBER],
        text=[f"${v:,.0f}" for v in rb_monthly['rev']],
        textposition='outside', textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig_defaults(fig_sea, height=260)
    fig_sea.update_layout(
        yaxis=dict(title=dict(text="Monthly revenue ($)"), tickprefix="$"),
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(
            x=3, y=450, text="May 2026 partial (data through May 7)",
            showarrow=False, font=dict(size=9, color=GREY)
        )]
    )
    st.plotly_chart(fig_sea, width='stretch')

    st.markdown("""
    <p class="src">All analyses use post-Metropolis-go-live data from CPkD FOIA R-6663.
    Performance scores are relative rankings within this 10-lot system only and should not
    be compared to other parking systems. Quadrant medians: $188/day revenue, 52.1% grace rate.
    Seasonality data covers Rainbow Beach North only (January 28 to May 7, 2026).
    Analysis: Ana Marija Soković, PhD, MBA.</p>
    """, unsafe_allow_html=True)


with tabs[7]:
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
