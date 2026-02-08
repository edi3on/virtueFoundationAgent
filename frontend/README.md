# Bridging Medical Deserts

**Intelligent Document Parsing & Healthcare Desert Visualization for the Virtue Foundation**

> Built for the Databricks Sponsored Track — reducing the time it takes for patients to receive lifesaving treatment by building an AI-powered healthcare intelligence layer for Ghana.

## What It Does

An interactive 2D map of Ghana that identifies **medical deserts** — areas where populations have critically insufficient access to healthcare — and provides **AI-powered analysis** of both healthcare facilities and underserved zones.

### Core Capabilities

- **Intelligent Document Parsing (IDP)**: Extracts structured insights from messy, unstructured CSV data — parsing JSON-encoded specialty lists, free-form capability descriptions, and equipment claims into actionable intelligence
- **Anomaly Detection**: Cross-references facility claims against expected infrastructure (e.g., "claims neurosurgery but no CT scan or MRI mentioned")
- **Medical Desert Identification**: Maps 10 confirmed healthcare cold spots across Ghana with severity scores, population data, and distance-to-care metrics
- **AI-Generated Analysis**: GPT-4o-mini generates contextual summaries for each location, synthesizing rule-based findings into actionable intelligence for NGO planners
- **Question-Driven Framework**: Analysis is structured around the [VF Agent Question Reference](https://docs.google.com/document/d/1-VF-Agent-Questions) categories (Q1-Q9), covering validation, anomaly detection, workforce distribution, geospatial gaps, and unmet needs

## Screenshot

_Add screenshots of the map with facility markers, desert zones, and the AI analysis sidebar._

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  index.html                      │
│         Leaflet.js 2D Map + Sidebar UI           │
│    (markers, heatmap, click → AI analysis)       │
└──────────────────────┬──────────────────────────┘
                       │ fetch
               ┌───────▼───────┐
               │ analysis.json │  ← 20 curated points
               └───────┬───────┘     with full analysis
                       │
          ┌────────────▼────────────┐
          │     prepare_data.py      │
          │                          │
          │  1. Parse CSV (IDP)      │
          │  2. Extract unstructured │
          │     fields               │
          │  3. Rule-based analysis  │
          │     (Q1-Q9)              │
          │  4. OpenAI GPT-4o-mini   │
          │     summaries            │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │  Virtue Foundation CSV   │
          │  (987 healthcare         │
          │   facilities in Ghana)   │
          └─────────────────────────┘
```

### Analysis Pipeline

**`prepare_data.py`** processes the Virtue Foundation Ghana dataset through:

1. **Unstructured Field Extraction** — Parses JSON-encoded arrays from `specialties`, `procedure`, `equipment`, and `capability` columns
2. **Rule-Based Analysis** across 7 question categories:
   - **Q1**: Basic lookups (specialty counts, regional comparison)
   - **Q3**: Validation (cross-checks claims vs. equipment evidence)
   - **Q4**: Anomaly detection (unrealistic procedure-to-size ratios, contradictory signals)
   - **Q5**: Service classification (itinerant vs. permanent, referral language)
   - **Q6**: Workforce (doctor-to-bed ratios, visiting specialist signals)
   - **Q7**: Resource gaps (sole-provider specialties)
   - **Q8**: NGO analysis (sustainability concerns)
3. **AI Summarization** — Sends extracted data + rule-based findings to GPT-4o-mini for contextual analysis
4. **Desert Zone Analysis** — Geospatial gap analysis (Q2), unmet needs (Q9), and NGO coverage gaps (Q8) for 10 curated medical desert zones

### Frontend

**`index.html`** is a single-file Leaflet.js application:

- Dark satellite map centered on Ghana
- Green markers = healthcare facilities (sized by specialty count)
- Red markers with dashed rings = medical deserts (sized by severity score)
- Connected heatmap overlay showing coverage intensity
- Click any marker → sidebar with:
  - Stats grid (specialties, beds, doctors, severity)
  - Specialty/missing specialty tags
  - Extracted capabilities (IDP output)
  - AI analysis box (GPT-4o-mini summary)
  - Question-category findings with alert/warning flags
  - Recommendations (deserts) and citations (facilities)

## Quick Start

### View the visualization (no setup needed)

```bash
cd globe
python3 -m http.server 8000
# Open http://localhost:8000/frontend/
```

The pre-generated `analysis.json` is included — the map works immediately.

### Regenerate analysis with AI (requires OpenAI key)

```bash
# Place the Virtue Foundation CSV in this directory:
# "Virtue Foundation Ghana v0.3 - Sheet1.csv"

OPENAI_API_KEY=sk-... python3 prepare_data.py
```

This re-processes the CSV and generates fresh AI summaries for all 20 locations (~2 minutes).

### Regenerate without AI (rule-based only)

```bash
python3 prepare_data.py
```

Works without an API key — produces the same rule-based analysis (Q1-Q9 findings) but without the GPT summary box.

## Data Points

### 10 Healthcare Facilities (from CSV)
| Facility | City | Beds | Specialties | Alerts |
|----------|------|------|-------------|--------|
| Greater Accra Regional Hospital | Accra | — | 16 | 1 |
| HealthLink Hospital | Accra | — | 19 | 1 |
| Chrispod Hospital & Diagnostic Center | Dome | 120 | 9 | 1 |
| Lekma Hospital – Teshie | Accra | 100 | 1 | 0 |
| Kings & Queens Medical University | Akosombo | — | 30 | 2 |
| Le Mete NGO Ghana | Tamale | — | 18 | 1 |
| Bechem Government Hospital | Bechem | 155 | 3 | 1 |
| Akatsi South Municipal Hospital | Akatsi | — | 14 | 1 |
| Banhart Specialist Hospital | Sunyani | — | 22 | 1 |
| St. John of God Hospital | Duayaw Nkwanta | — | 8 | 1 |

### 10 Medical Desert Zones
| Location | Region | Population | Severity | Nearest Hospital |
|----------|--------|-----------|----------|-----------------|
| Bole District | Savannah | 61,593 | 10/10 | 148km |
| Kadjebi | Oti | 46,000 | 9/10 | 85km |
| Damongo | Savannah | 38,000 | 8/10 | 95km |
| Dambai | Oti | 35,000 | 8/10 | 72km |
| Donkorkrom | Eastern | 31,000 | 8/10 | 65km |
| Nandom | Upper West | 48,000 | 7/10 | 110km+ |
| Enchi | Western North | 42,000 | 7/10 | 180km |
| Nalerigu | North East | 28,000 | 6/10 | local (limited) |
| Kete Krachi | Oti | 35,000 | 6/10 | local (limited) |
| Tumu | Upper West | 20,000 | 5/10 | local (limited) |

## Tech Stack

- **Frontend**: Leaflet.js, leaflet-heat.js, vanilla JS (single HTML file)
- **Data Pipeline**: Python 3 (csv, json, urllib — no dependencies)
- **AI**: OpenAI GPT-4o-mini via REST API
- **Data Source**: [Virtue Foundation Ghana Dataset](https://docs.google.com/spreadsheets/d/1Lz5RPjb3JE8LhSYDeUJL-KGxOq1RwNQmfuLJwMn7cNk)

## Evaluation Criteria Alignment

| Criteria | Weight | How We Address It |
|----------|--------|-------------------|
| **Technical Accuracy** | 35% | Rule-based cross-validation of specialty claims vs. equipment, anomaly detection for unrealistic procedure-to-size ratios, workforce signal analysis |
| **IDP Innovation** | 30% | Parses JSON-encoded arrays from free-text columns, extracts capabilities from unstructured descriptions, detects itinerant/referral language patterns |
| **Social Impact** | 25% | 10 medical deserts mapped with severity scores, population data, distance-to-care, missing specialties, and actionable intervention recommendations |
| **User Experience** | 10% | Click-to-explore map interface, natural language AI summaries, color-coded alert system, no technical knowledge required |

## License

MIT
