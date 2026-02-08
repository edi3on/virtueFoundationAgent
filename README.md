# Virtue Foundation Agent — Bridging Medical Deserts

**AI-Powered Healthcare Intelligence Platform for Ghana**

> Built for Databricks Sponsored Track — Reducing time-to-treatment by providing an intelligent healthcare access analysis layer for the Virtue Foundation.

---

## Purpose

This project identifies and analyzes **medical deserts** in Ghana — areas where populations face critical healthcare access gaps. By combining intelligent document parsing, geospatial analysis, and AI-powered insights, it transforms raw facility data into actionable intelligence for healthcare planning and NGO intervention strategies.

**Key Objectives:**
- Parse unstructured healthcare facility data into structured insights
- Identify geographic gaps in healthcare coverage (medical deserts)
- Detect facility claim anomalies and infrastructure inconsistencies
- Generate AI analysis for evidence-based healthcare planning

---

## Quick Start

### Prerequisites

- **Python 3.8+** (for data processing)
- **OpenAI API Key** (for AI analysis generation)
- **Modern Web Browser** (for visualization)

### Installation & Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/virtueFoundationAgent.git
cd virtueFoundationAgent
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure OpenAI API Key

```bash
# Set your OpenAI API key as environment variable
export OPENAI_API_KEY="your-api-key-here"

# Or add to your shell profile (~/.zshrc or ~/.bashrc):
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### 4. Process Data & Generate Analysis

```bash
cd frontend

# Run the data preparation script
# This will:
# - Parse the CSV file
# - Perform intelligent document parsing (IDP)
# - Run rule-based analysis (Q1-Q9)
# - Generate AI summaries with GPT-4o-mini
# - Output analysis.json
python3 prepare_data.py
```

**Expected Output:**
```
starting
Loading CSV...
Loaded 987 rows.
Processing 20 curated points...
  [1/20] Processing facility: 109/No 1 Bekwai Rd...
    ✓ Parsed specialties, capabilities, equipment
    ✓ Rule-based analysis complete
    ✓ AI summary generated
  [2/20] Processing desert: Bole District...
...
Done! Wrote analysis.json (20 points)
```

#### 5. Launch the Visualization

```bash
# Open index.html in your browser
# Option 1: Double-click index.html in Finder/Explorer
# Option 2: Use a local server (recommended)
python3 -m http.server 8000

# Then open: http://localhost:8000
```

#### 6. Explore the Map

- **Click facility markers** (green) to see AI-powered analysis
- **Click desert markers** (red) to understand healthcare gaps
- **Toggle heatmap** to visualize coverage density
- **Search locations** using the search box
- **Switch map styles** (Dark, Satellite, Streets, Terrain)

---

## Project Structure

```
virtueFoundationAgent/
├── README.md                          # This file - main project documentation
├── LICENSE                            # Project license
├── requirements.txt                   # Python dependencies (top-level)
│
├── frontend/                          # Interactive visualization & AI analysis
│   ├── index.html                     # Main web application
│   ├── prepare_data.py                # Data processing & AI analysis engine
│   ├── analysis.json                  # Generated: 20 curated points with AI insights
│   ├── geocode_cache.json             # Geocoding cache (OpenStreetMap API results)
│   └── README.md                      # Detailed frontend documentation
│
└── data-processing/                   # Data parsing & geocoding utilities
    ├── parse_and_geocode.py           # Address parser & geocoder (Nominatim)
    ├── requirements.txt               # Python dependencies (pandas, geopy, certifi)
    ├── SCHEMA_DOCUMENTATION.md        # Complete CSV schema definitions
    ├── SETUP_SUMMARY.md               # Setup guide & usage examples
    ├── README.md                      # Data processing documentation
    └── datasets/                      # Dataset directory
        ├── Virtue Foundation Ghana v0.3 - Sheet1.csv  # Source data (987 records)
        ├── test_dataset_50_records.csv                 # Test subset (50 records)
        ├── TEST_DATASET_README.md                      # Test dataset documentation
        ├── geocoded_test_facilities.csv                # Output: geocoded test data
        └── test_facilities.geojson                     # Output: GeoJSON for mapping
```

---

## Component Overview

### 1. Frontend — Interactive Map & AI Analysis

**Location:** `frontend/`

The main visualization and analysis interface built with vanilla JavaScript, Leaflet.js, and Leaflet.heat.

**Key Files:**

- **`index.html`** (748 lines)
  - Interactive 2D map with Leaflet.js
  - Facility markers (green) and medical desert markers (red)
  - Heatmap layer showing healthcare density
  - Collapsible sidebar with detailed AI analysis
  - Multiple map styles (Dark, Satellite, Streets, Terrain)
  - Search functionality for Ghana locations

- **`prepare_data.py`** (824 lines)
  - **Intelligent Document Parsing (IDP)**: Extracts structured data from messy CSV fields
  - **Rule-Based Analysis**: Implements Q1-Q9 question framework
  - **Anomaly Detection**: Cross-references claims vs. infrastructure
  - **AI Summary Generation**: Calls GPT-4o-mini for contextual insights
  - **Geocoding**: Uses OpenStreetMap Nominatim API with caching
  - Outputs: `analysis.json` (20 curated points with full analysis)

- **`analysis.json`**
  - 10 healthcare facilities with parsed specialties, capabilities, equipment
  - 10 medical deserts with severity scores, population data, missing specialties
  - Each point includes:
    - Basic info (name, location, coordinates)
    - Parsed IDP data (specialties, capabilities, equipment lists)
    - Rule-based findings organized by question category (Q1-Q9)
    - AI-generated summary from GPT-4o-mini
    - Citation data (source CSV row, fields used)

**Features:**

✅ **Intelligent Document Parsing**: Extracts from JSON-encoded arrays, free-form text, and unstructured fields  
✅ **9 Question Categories**: Validation, Anomaly Detection, Workforce Distribution, Geospatial Gaps, etc.  
✅ **AI-Powered Insights**: GPT-4o-mini generates contextual summaries  
✅ **Collapsible UI**: Expandable dropdowns for long text answers and AI analysis  
✅ **Interactive Heatmap**: Toggle-able visualization of healthcare density  
✅ **Multi-layer Map**: Dark mode, satellite, street, and terrain views  

---

### 2. Data Processing — Geocoding & Schema Tools

**Location:** `data-processing/`

Utilities for parsing addresses from the CSV and converting them to coordinates for mapping.

**Key Files:**

- **`parse_and_geocode.py`**
  - Parses address components from CSV (line1, line2, line3, city, region, country)
  - Builds complete address strings
  - Geocodes addresses to lat/lon using Nominatim (OpenStreetMap)
  - Exports to CSV and GeoJSON formats
  - Supports test mode for quick iterations

- **`SCHEMA_DOCUMENTATION.md`**
  - Complete field definitions for all 41 CSV columns
  - Data types, formats, and examples
  - Medical specialty hierarchy
  - Facility facts categories (procedure, equipment, capability)

- **`datasets/`**
  - `Virtue Foundation Ghana v0.3 - Sheet1.csv` — Source data (987 records)
  - `test_dataset_50_records.csv` — Test subset for development
  - Output files: `geocoded_test_facilities.csv`, `test_facilities.geojson`

**Usage:**

```bash
cd data-processing

# Test mode (50 records, ~1 minute)
python3 parse_and_geocode.py --test

# Full dataset (987 records, ~16-20 minutes)
python3 parse_and_geocode.py
```

**Output:**
- CSV with latitude/longitude columns added
- GeoJSON file for mapping applications
- Success rate: 60-85% (varies by address quality)

---

## Technology Stack

### Frontend
- **Leaflet.js** — Interactive mapping library
- **Leaflet.heat** — Heatmap visualization
- **Vanilla JavaScript** — No framework dependencies
- **OpenStreetMap Tiles** — Map base layers

### Data Processing
- **Python 3.8+**
- **pandas** — CSV parsing and data manipulation
- **geopy** — Geocoding (Nominatim/OpenStreetMap)
- **OpenAI API** (GPT-4o-mini) — AI summary generation
- **urllib** — HTTP requests (no external dependencies)

### Data Sources
- Virtue Foundation Ghana healthcare facilities CSV (987 records)
- OpenStreetMap Nominatim API (geocoding)
- OpenAI GPT-4o-mini (AI analysis)

---

## Key Features

### 🔍 Intelligent Document Parsing (IDP)

Extracts structured insights from unstructured data:

- **JSON-encoded lists**: Parses specialty arrays like `["internalMedicine","pediatrics"]`
- **Free-form text**: Extracts capabilities from narrative descriptions
- **Equipment mentions**: Identifies medical devices (CT scan, MRI, ultrasound, etc.)
- **Address parsing**: Splits multi-line addresses into structured components

### 🚨 Anomaly Detection

Cross-references facility claims against expected infrastructure:

- **Specialty-Equipment Mismatch**: "Claims neurosurgery but no operating microscope mentioned"
- **Capability Gaps**: "24/7 emergency care but no ambulance or ICU capability"
- **Missing Workforce**: High specialty count but no doctor count reported

### 🗺️ Medical Desert Identification

Identifies 10 confirmed healthcare cold spots:

- **Severity scoring** (1-10 scale)
- **Population impact** estimates
- **Distance to nearest facility**
- **Missing specialty analysis**
- **Intervention recommendations**

### 🤖 AI-Powered Analysis

GPT-4o-mini generates contextual summaries:

- **Facility analysis**: Strengths, gaps, verification needs
- **Desert context**: Population impact, access barriers, priority interventions
- **Evidence-based**: Grounded in parsed data and rule-based findings

### 📊 Question-Driven Framework

Analysis structured around 9 VF Agent question categories:

1. **Basic Queries & Lookups** (Q1): Facility info, contact, location
2. **Geospatial Queries** (Q2): Nearest facilities, coverage radius
3. **Validation & Verification** (Q3): Data completeness, claim verification
4. **Misrepresentation & Anomaly Detection** (Q4): Claim-infrastructure mismatches
5. **Service Classification & Inference** (Q5): Emergency care, maternity services
6. **Workforce Distribution** (Q6): Doctor counts, staffing patterns
7. **Resource Distribution & Gaps** (Q7): Equipment, bed capacity
8. **NGO & International Organization** (Q8): Faith-based affiliations, partnerships
9. **Unmet Needs & Demand Analysis** (Q9): Missing specialties, desert severity

---

## Data Schema

The CSV contains 987 healthcare facilities across Ghana with 41 fields:

**Core Fields:**
- `name`, `phone_numbers`, `email`, `websites`, `officialWebsite`
- `address_line1`, `address_line2`, `address_line3`, `address_city`, `address_stateOrRegion`, `address_country`
- `facilityTypeId` (hospital, clinic, pharmacy, dentist)
- `operatorTypeId` (public, private)
- `specialties` (JSON array of medical specialties)
- `procedure`, `equipment`, `capability` (free-form facility facts)

**See** `data-processing/SCHEMA_DOCUMENTATION.md` for complete field definitions.

---

## Development

### Running Locally

```bash
# Frontend development
cd frontend
python3 -m http.server 8000
# Open http://localhost:8000

# Data processing development
cd data-processing
python3 parse_and_geocode.py --test
```

### Modifying Analysis

Edit `frontend/prepare_data.py` to adjust:
- **Question categories** (Q1-Q9 functions)
- **Anomaly detection rules** (SPECIALTY_EQUIPMENT_REQUIREMENTS)
- **AI prompt templates** (system_prompt, user_prompt)
- **Curated points selection** (CURATED_FACILITIES, CURATED_DESERTS)

### Adding New Medical Deserts

1. Add to `CURATED_DESERTS` in `prepare_data.py`
2. Include: name, coordinates, severity, population, nearest distance, missing specialties
3. Re-run: `python3 prepare_data.py`

---

## Limitations & Future Work

### Current Limitations

- **Data Quality**: Some facilities have incomplete addresses or missing fields
- **Geocoding**: 60-85% success rate due to address quality
- **Manual Curation**: 20 points manually selected (10 facilities, 10 deserts)
- **Static Analysis**: Rule-based + AI, not real-time data

### Future Enhancements

- [ ] Expand to all 987 facilities with automated desert detection
- [ ] Real-time facility status updates
- [ ] Patient flow modeling and wait time predictions
- [ ] Mobile app for field workers
- [ ] Integration with Ghana Health Service APIs
- [ ] Multi-language support (English, Twi, Ewe, Ga)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Virtue Foundation** for the Ghana healthcare facilities dataset
- **Databricks** for sponsoring the hackathon track
- **OpenStreetMap** for geocoding services
- **OpenAI** for GPT-4o-mini API access

---

## Support

For questions or issues:
- Open an issue on GitHub
- Email: your-email@example.com
- Documentation: See `frontend/README.md` and `data-processing/README.md`

---

**Built with ❤️ to bridge medical deserts and improve healthcare access in Ghana.**