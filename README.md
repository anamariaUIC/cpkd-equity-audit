# Chicago Park District Capital Investment Equity Audit
### An independent, data-driven analysis of CPD capital investment 2011–2024

**Live dashboard:** [deploy link goes here after you push to Streamlit Cloud]

---

## What this is

An interactive equity audit of Chicago Park District capital investment from 2011 through 2024, normalized by park acreage using GIS polygon data. Built by Ana Marija Soković as part of ongoing civic accountability work in Chicago's 7th Ward and South Shore neighborhood.

The analysis confirms through independent GIS-normalized calculation that **Park No. 566 (79th St./USX lakefront) and Rainbow Beach are the two most disinvested lakefront parks in Chicago**, receiving $0.20/sq ft and $0.40/sq ft respectively — compared to $8.06/sq ft at Grant Park and $8.59/sq ft at Burnham Park.

---

## Data sources

| Source | Description |
|--------|-------------|
| CPD Park Capital Projects 2011–2024 | April 2024 release, ~3,000 line items, 79 pages |
| SEIU Local 73 "State of the Parks Revisited: 2025 Update" | Dr. Molly Hudgens, PhD; programming data via FOIA 5844 (Oct 2024) and FOIA 5902 (Nov 2024) |
| Chicago Park District GIS polygon data | Park acreage from CPD GIS shapefiles; key corrections to CPD's published acreage for Rainbow Beach and Park No. 566 |
| CPD Budgets 2010 & 2025 | Management contract and staffing data |

**Note on acreage methodology:** CPD's published acreage for several lakefront parks (notably Rainbow Beach at 15 acres listed vs. 171 acres actual GIS polygon) significantly understates park size and would artificially inflate per-sq-ft investment figures. This analysis uses GIS polygon acreage throughout for consistency.

---

## Dashboard tabs

1. **Regional Overview** — Total investment by region, per-park averages, outside funding share, pending projects
2. **Per-Acre Analysis** — 14 parks compared by $/sq ft; Marquette vs. Grant spotlight
3. **Lakefront Equity** — Lakefront-only comparison; Park 566 ($0.20/sq ft) and Rainbow Beach ($0.40/sq ft) vs. North Side lakefront parks
4. **Programming Gap** — Verified SEIU 73 data: regional programs and enrollees; N4 vs. S2 area comparison (8.6× gap); Culture & Arts FTE decline; privatization contracts
5. **Most Disinvested** — All parks ranked ascending by $/sq ft with annotations
6. **Key Findings** — Eight narrative findings with policy recommendations

---

## Key findings

- The North Lakefront's 3 parks received ~43% of all CPD capital investment 2011–2024 ($485M of ~$1.1B)
- Park No. 566 (South Shore lakefront) received $0.20/sq ft — 43× less than Burnham Park ($8.59/sq ft)
- Rainbow Beach received $0.40/sq ft — the second most disinvested lakefront park
- North Region Area 4 offered 8.6× more programs than comparable South Region Area 2 in 2024 (5,044 vs. 587)
- Over half of 739 completed capital projects (2019–2024) concentrated in only 53 of 615 parks
- Culture & Arts instructor FTEs fell 30% since 2010; Music Instructors (M) fell 78%
- Private management contracts grew 168% ($31.8M → $85.5M) while field staff fell by 30+ year-round positions

---

## Running locally

```bash
git clone https://github.com/YOUR_USERNAME/cpd-equity-audit.git
cd cpd-equity-audit
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## Methodological notes

- All per-sq-ft figures calculated as: total capital investment ÷ (GIS polygon acres × 43,560 sq ft/acre)
- "Outside funding" in CPD data includes TIF, grants, and private donations; excluded from CPD-only equity comparisons
- Programming data excludes gymnastics per CPD coding conventions (FOIA 5844 footnote)
- Regional totals (25,229) differ from district total (26,201) by 972 programs not assigned to a region

---

## Contact / methodology questions

Ana Marija Soković | Lead Computational Scientist, UIC ACER | Civic accountability writer, 7th Ward South Shore
