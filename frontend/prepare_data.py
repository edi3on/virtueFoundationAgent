#!/usr/bin/env python3
"""
Prepare analysis.json for the Ghana Healthcare Desert Globe.
Structures analysis around the VF Agent question categories:
  - Basic Queries & Lookups (Q1)
  - Geospatial Queries (Q2)
  - Validation & Verification (Q3)
  - Misrepresentation & Anomaly Detection (Q4)
  - Service Classification & Inference (Q5)
  - Workforce Distribution (Q6)
  - Resource Distribution & Gaps (Q7)
  - NGO & International Organization Analysis (Q8)
  - Unmet Needs & Demand Analysis (Q9)
"""

import csv
import json
import math
import os
import sys
import time
import urllib.request
print("starting")

CSV_FILE = "Virtue Foundation Ghana v0.3 - Sheet1.csv"
OUTPUT_FILE = "analysis.json"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = "gpt-4o-mini"


def call_openai(system_prompt, user_prompt, max_tokens=800):
    """Call OpenAI chat completion API."""
    if not OPENAI_API_KEY:
        return None

    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"    OpenAI error: {e}")
        return None

# ──────────────────────────────────────────
#  Parse unstructured JSON-like text fields
# ──────────────────────────────────────────
def parse_json_field(raw):
    if not raw or raw.strip() in ('null', '[]', ''):
        return []
    raw = raw.strip()
    try:
        val = json.loads(raw)
        if isinstance(val, list):
            return [str(v).strip() for v in val if v and str(v).strip()]
        return [str(val)]
    except:
        raw = raw.strip('[]')
        return [s.strip().strip('"').strip("'") for s in raw.split('","') if s.strip()]

def clean(v):
    if not v or v.strip().lower() == 'null':
        return ''
    return v.strip()

def camel_to_readable(s):
    """Convert camelCase specialty to readable text."""
    result = ''
    for i, c in enumerate(s):
        if c.isupper() and i > 0:
            result += ' '
        result += c
    return result.replace(' And ', ' & ').replace(' Or ', '/').title()

# ──────────────────────────────────────────
#  Equipment requirements for validation (Q3/Q4)
# ──────────────────────────────────────────
SPECIALTY_EQUIPMENT_REQUIREMENTS = {
    'neurosurgery': ['operating microscope', 'CT scan', 'MRI', 'ICU', 'ventilator'],
    'cardiology': ['ECG', 'echocardiograph', 'defibrillator', 'cardiac monitor'],
    'cardiacSurgery': ['heart-lung machine', 'operating theatre', 'ICU', 'ventilator', 'blood bank'],
    'ophthalmology': ['slit lamp', 'operating microscope', 'tonometer', 'fundoscope'],
    'radiology': ['X-ray', 'ultrasound', 'CT scan'],
    'orthopedicSurgery': ['X-ray', 'operating theatre', 'C-arm'],
    'nephrology': ['dialysis machine', 'ultrasound'],
    'generalSurgery': ['operating theatre', 'anaesthesia machine', 'sterilizer', 'blood bank'],
    'gynecologyAndObstetrics': ['ultrasound', 'fetal monitor', 'delivery suite', 'operating theatre'],
    'pediatrics': ['neonatal unit', 'incubator', 'pediatric ward'],
    'emergencyMedicine': ['emergency department', 'defibrillator', 'ventilator', 'trauma kit'],
    'dentistry': ['dental chair', 'dental X-ray', 'autoclave'],
    'psychiatry': ['counselling room', 'inpatient ward'],
}

# Procedure complexity tiers
COMPLEX_PROCEDURES = {
    'neurosurgery', 'cardiacSurgery', 'plasticSurgery', 'hepatobiliarySurgery',
    'spineNeurosurgery', 'transplantSurgery', 'interventionalRadiology',
}
MODERATE_PROCEDURES = {
    'generalSurgery', 'orthopedicSurgery', 'gynecologyAndObstetrics',
    'ophthalmology', 'urology',
}

# ──────────────────────────────────────────
#  Extract facility from CSV row
# ──────────────────────────────────────────
def extract_facility(row, row_idx):
    specialties = parse_json_field(row.get('specialties', ''))
    procedures = parse_json_field(row.get('procedure', ''))
    equipment = parse_json_field(row.get('equipment', ''))
    capabilities = parse_json_field(row.get('capability', ''))
    description = clean(row.get('description', ''))
    org_desc = clean(row.get('organizationDescription', ''))

    return {
        'name': clean(row.get('name', '')),
        'city': clean(row.get('address_city', '')),
        'region': clean(row.get('address_stateOrRegion', '')),
        'address': clean(row.get('address_line1', '')),
        'facilityType': clean(row.get('facilityTypeId', '')),
        'operatorType': clean(row.get('operatorTypeId', '')),
        'specialties': specialties,
        'procedures': procedures,
        'equipment': equipment,
        'capabilities': capabilities,
        'description': description,
        'orgDescription': org_desc,
        'numDoctors': int(clean(row.get('numberDoctors', ''))) if clean(row.get('numberDoctors', '')) else None,
        'bedCapacity': int(clean(row.get('capacity', ''))) if clean(row.get('capacity', '')) else None,
        'sourceUrl': clean(row.get('source_url', '')),
        'websites': parse_json_field(row.get('websites', '')),
        'phone': parse_json_field(row.get('phone_numbers', '')),
        'csvRow': row_idx + 2,
    }


# ──────────────────────────────────────────
#  Analysis generators per question category
# ──────────────────────────────────────────

def analyze_basic_lookups(f, all_facilities_in_region):
    """Q1: Basic Queries & Lookups"""
    findings = []

    # Q1.1 / Q1.2: Specialty and procedure presence
    if f['specialties']:
        findings.append({
            'question': 'Q1.1: What specialties does this facility offer?',
            'answer': f"This facility reports {len(f['specialties'])} specialties: {', '.join(camel_to_readable(s) for s in f['specialties'][:10])}" + (f" and {len(f['specialties'])-10} more." if len(f['specialties']) > 10 else "."),
            'confidence': 'high',
        })

    # Q1.5: Region comparison
    region = f['region'] or f['city']
    if region and all_facilities_in_region:
        count = len(all_facilities_in_region)
        hospitals = sum(1 for r in all_facilities_in_region if clean(r.get('facilityTypeId','')) == 'hospital')
        findings.append({
            'question': f'Q1.5: How does {region} compare?',
            'answer': f"{region} has {count} facilities in the dataset ({hospitals} hospitals). This {'is one of the most served regions' if count > 20 else 'has moderate coverage' if count > 5 else 'has limited healthcare infrastructure'}.",
            'confidence': 'high',
        })

    return findings


def analyze_validation(f):
    """Q3: Validation & Verification"""
    findings = []
    cap_text = ' '.join(f['capabilities']).lower()
    equip_text = ' '.join(f['equipment']).lower()
    desc_text = (f['description'] + ' ' + f['orgDescription']).lower()
    all_text = cap_text + ' ' + equip_text + ' ' + desc_text

    # Q3.1: Claim specialty but lack equipment
    for spec in f['specialties']:
        if spec in SPECIALTY_EQUIPMENT_REQUIREMENTS:
            required = SPECIALTY_EQUIPMENT_REQUIREMENTS[spec]
            found = [eq for eq in required if any(eq.lower() in all_text for _ in [1])]
            missing = [eq for eq in required if not any(eq.lower() in all_text for _ in [1])]
            if missing and len(missing) > len(found):
                findings.append({
                    'question': f'Q3.1: Does this facility have equipment for {camel_to_readable(spec)}?',
                    'answer': f"Claims {camel_to_readable(spec)} but no mention of: {', '.join(missing)}. " +
                              (f"Only evidence of: {', '.join(found)}." if found else "No supporting equipment evidence found in unstructured text."),
                    'confidence': 'medium',
                    'flag': 'warning',
                })

    # Q3.4: Procedure-equipment cross-check
    if f['specialties'] and not f['equipment']:
        findings.append({
            'question': 'Q3.4: Is equipment data available to verify procedure claims?',
            'answer': f"Facility claims {len(f['specialties'])} specialties but has NO structured equipment data. Verification relies entirely on unstructured capability text.",
            'confidence': 'low',
            'flag': 'warning',
        })

    return findings


def analyze_anomalies(f):
    """Q4: Misrepresentation & Anomaly Detection"""
    findings = []
    complex_claimed = [s for s in f['specialties'] if s in COMPLEX_PROCEDURES]
    moderate_claimed = [s for s in f['specialties'] if s in MODERATE_PROCEDURES]
    cap_text = ' '.join(f['capabilities']).lower()
    all_text = cap_text + ' ' + f['description'].lower() + ' ' + f['orgDescription'].lower()

    # Q4.4: Unrealistic procedure count for size
    if f['bedCapacity'] and f['bedCapacity'] < 50 and len(f['specialties']) > 10:
        findings.append({
            'question': 'Q4.4: Are the claimed procedures realistic for this facility size?',
            'answer': f"RED FLAG: Facility claims {len(f['specialties'])} specialties with only {f['bedCapacity']} beds. " +
                      f"A facility this size would typically support 3-5 specialties. The breadth of claims ({', '.join(camel_to_readable(s) for s in f['specialties'][:5])}...) is disproportionate to stated capacity.",
            'confidence': 'high',
            'flag': 'alert',
        })
    elif not f['bedCapacity'] and len(f['specialties']) > 15:
        findings.append({
            'question': 'Q4.4: Are the claimed procedures realistic for this facility size?',
            'answer': f"CAUTION: Facility claims {len(f['specialties'])} specialties but reports no bed capacity. Without size data, the breadth of specialty claims cannot be verified.",
            'confidence': 'medium',
            'flag': 'warning',
        })

    # Q4.7: Correlated characteristics
    if f['bedCapacity'] and f['bedCapacity'] >= 100 and not f['numDoctors']:
        findings.append({
            'question': 'Q4.7: Do facility characteristics correlate as expected?',
            'answer': f"Facility reports {f['bedCapacity']} beds but no doctor count. A {f['bedCapacity']}-bed facility would typically require 20-40+ physicians. Missing staffing data weakens confidence in capacity claims.",
            'confidence': 'medium',
            'flag': 'warning',
        })

    # Q4.8: High breadth, minimal infrastructure
    if complex_claimed and not f['equipment']:
        findings.append({
            'question': 'Q4.8: Is the breadth of procedures supported by infrastructure?',
            'answer': f"Claims advanced specialties ({', '.join(camel_to_readable(s) for s in complex_claimed)}) but lists NO equipment. " +
                      f"These specialties require significant infrastructure (operating theatres, ICU, specialized imaging). Absence of equipment data is a major red flag.",
            'confidence': 'high',
            'flag': 'alert',
        })

    # Q4.9: Things that shouldn't move together
    has_24hr = '24' in all_text or 'emergency' in all_text
    has_nhis = 'nhis' in all_text or 'insurance' in all_text
    if complex_claimed and not has_24hr:
        findings.append({
            'question': 'Q4.9: Are there contradictory signals?',
            'answer': f"Claims complex specialties ({', '.join(camel_to_readable(s) for s in complex_claimed[:3])}) but no mention of 24-hour or emergency services. Complex procedures require round-the-clock post-operative care.",
            'confidence': 'medium',
            'flag': 'warning',
        })

    # No issues found
    if not findings:
        findings.append({
            'question': 'Q4: Anomaly Detection Summary',
            'answer': "No significant anomalies detected. Specialty claims appear proportionate to reported infrastructure, though independent verification is recommended.",
            'confidence': 'medium',
            'flag': 'ok',
        })

    return findings


def analyze_service_classification(f):
    """Q5: Service Classification & Inference"""
    findings = []
    cap_text = ' '.join(f['capabilities']).lower()
    all_text = cap_text + ' ' + f['description'].lower() + ' ' + f['orgDescription'].lower()

    # Q5.1: Itinerant vs permanent
    itinerant_signals = ['visiting', 'camp', 'outreach', 'mission', 'periodic', 'twice a year', 'annual', 'quarterly']
    permanent_signals = ['24/7', '24 hours', 'permanent', 'full-time', 'daily']
    found_itinerant = [s for s in itinerant_signals if s in all_text]
    found_permanent = [s for s in permanent_signals if s in all_text]

    if found_itinerant:
        findings.append({
            'question': 'Q5.1: Are services permanent or itinerant?',
            'answer': f"ITINERANT SIGNALS DETECTED: Text contains '{', '.join(found_itinerant)}'. Some services may be delivered through periodic outreach rather than permanent service lines." +
                      (f" However, also found permanent signals: '{', '.join(found_permanent)}'." if found_permanent else ""),
            'confidence': 'medium',
            'flag': 'warning',
        })
    elif found_permanent:
        findings.append({
            'question': 'Q5.1: Are services permanent or itinerant?',
            'answer': f"Services appear to be permanently staffed. Indicators: '{', '.join(found_permanent)}'.",
            'confidence': 'medium',
            'flag': 'ok',
        })

    # Q5.2: Referral language
    referral_signals = ['refer', 'arrange', 'collaborate', 'send to', 'partner', 'transfer']
    found_referral = [s for s in referral_signals if s in all_text]
    if found_referral:
        findings.append({
            'question': 'Q5.2: Does the facility perform procedures or refer them?',
            'answer': f"Referral language detected: '{', '.join(found_referral)}'. Some claimed capabilities may involve referring patients to other facilities rather than in-house delivery.",
            'confidence': 'medium',
            'flag': 'warning',
        })

    return findings


def analyze_workforce(f):
    """Q6: Workforce Distribution"""
    findings = []
    all_text = ' '.join(f['capabilities']).lower() + ' ' + f['description'].lower() + ' ' + f['orgDescription'].lower()

    # Q6.1: Workforce presence
    if f['numDoctors']:
        findings.append({
            'question': 'Q6.1: What is the known workforce at this facility?',
            'answer': f"Facility reports {f['numDoctors']} doctors." +
                      (f" For {f['bedCapacity']} beds, this is a doctor-to-bed ratio of 1:{f['bedCapacity']//f['numDoctors']}." if f['bedCapacity'] and f['numDoctors'] > 0 else ""),
            'confidence': 'high',
        })
    else:
        findings.append({
            'question': 'Q6.1: What is the known workforce at this facility?',
            'answer': "No doctor count reported. Workforce data gap — cannot assess staffing adequacy.",
            'confidence': 'low',
            'flag': 'warning',
        })

    # Q6.4/Q6.6: Visiting vs permanent
    visiting_signals = ['visiting', 'consultant', 'locum', 'part-time']
    found_visiting = [s for s in visiting_signals if s in all_text]
    if found_visiting:
        findings.append({
            'question': 'Q6.4: Is there evidence of visiting vs permanent specialists?',
            'answer': f"Visiting specialist signals detected: '{', '.join(found_visiting)}'. Service continuity may be fragile if tied to individual practitioners.",
            'confidence': 'medium',
            'flag': 'warning',
        })

    return findings


def analyze_resource_gaps(f, all_rows_in_region):
    """Q7: Resource Distribution & Gaps"""
    findings = []

    # Q7.5: Single-provider procedures
    if f['specialties']:
        region_specs = {}
        for r in all_rows_in_region:
            specs = parse_json_field(r.get('specialties', ''))
            for s in specs:
                region_specs[s] = region_specs.get(s, 0) + 1

        sole_provider = [s for s in f['specialties'] if region_specs.get(s, 0) <= 2]
        if sole_provider:
            findings.append({
                'question': 'Q7.5: Are any procedures dependent on very few facilities?',
                'answer': f"This facility is one of very few in its region providing: {', '.join(camel_to_readable(s) for s in sole_provider[:5])}. " +
                          "Loss of this facility would create critical coverage gaps.",
                'confidence': 'high',
                'flag': 'alert',
            })

    return findings


def analyze_ngo(f):
    """Q8: NGO & International Organization Analysis"""
    findings = []
    all_text = ' '.join(f['capabilities']).lower() + ' ' + f['description'].lower() + ' ' + f['orgDescription'].lower()
    org_type = clean(f.get('operatorType', '') or '')

    ngo_signals = ['ngo', 'foundation', 'charity', 'mission', 'non-profit', 'nonprofit', 'volunteer', 'international', 'aid']
    found_ngo = [s for s in ngo_signals if s in all_text or s in f['name'].lower()]

    if found_ngo or org_type in ('ngo', 'charity', 'mission'):
        findings.append({
            'question': 'Q8.1: Is this an NGO-operated facility?',
            'answer': f"NGO/mission signals detected: '{', '.join(found_ngo[:3])}'. " +
                      "Sustainability should be assessed — NGO-operated facilities may depend on external funding cycles.",
            'confidence': 'medium',
        })

    return findings


# ──────────────────────────────────────────
#  Desert analysis generators
# ──────────────────────────────────────────

def analyze_desert_geospatial(d, all_facilities):
    """Q2: Geospatial analysis for desert zones"""
    findings = []

    # Q2.3: Cold spot analysis
    findings.append({
        'question': f'Q2.3: Is {d["name"]} a geographic cold spot?',
        'answer': f'{d["name"]} in {d["region"]} is a confirmed healthcare cold spot. ' +
                  f'The nearest facility with meaningful capacity is {d["nearestFacility"]}, ' +
                  (f'{d["nearestDistance_km"]}km away. ' if d["nearestDistance_km"] > 0 else 'but it has severe capacity limitations. ') +
                  f'Population of ~{d["population"]:,} people has ' +
                  f'no access to: {", ".join(camel_to_readable(s) for s in d["missingSpecialties"][:4])}.',
        'confidence': 'high',
        'flag': 'alert',
    })

    # Find closest facilities from dataset
    closest = []
    for fac in all_facilities:
        dist = math.sqrt((fac['lat'] - d['lat'])**2 + (fac['lng'] - d['lng'])**2) * 111
        closest.append((dist, fac['name'], fac.get('specialties', [])))
    closest.sort()

    if closest:
        top3 = closest[:3]
        findings.append({
            'question': 'Q2.1: What are the nearest facilities in the dataset?',
            'answer': '\n'.join(f"• {name} — {dist:.0f}km ({len(specs)} specialties)" for dist, name, specs in top3),
            'confidence': 'high',
        })

    return findings


def analyze_desert_unmet_needs(d):
    """Q9: Unmet Needs for desert zones"""
    findings = []

    findings.append({
        'question': f'Q9.5: Does {d["name"]} have capacity for its population?',
        'answer': f'Population ~{d["population"]:,} with ' +
                  (f'nearest hospital {d["nearestDistance_km"]}km away. ' if d["nearestDistance_km"] > 0 else 'severely under-resourced local facility. ') +
                  f'Missing {len(d["missingSpecialties"])} critical specialties. ' +
                  f'Based on WHO guidelines, a population this size requires at minimum: ' +
                  f'basic emergency obstetric care, surgical capability, and diagnostic services — none of which are available locally.',
        'confidence': 'high',
        'flag': 'alert',
    })

    return findings


def analyze_desert_ngo_gaps(d, all_facilities):
    """Q8.3: NGO gaps for desert zones"""
    findings = []

    # Check if any NGOs are nearby
    ngo_nearby = False
    for fac in all_facilities:
        dist = math.sqrt((fac['lat'] - d['lat'])**2 + (fac['lng'] - d['lng'])**2) * 111
        if dist < 100:
            all_text = ' '.join(fac.get('capabilities', [])).lower() + ' ' + (fac.get('orgDescription', '') or '').lower()
            if any(s in all_text or s in fac['name'].lower() for s in ['ngo', 'foundation', 'mission', 'volunteer']):
                ngo_nearby = True
                break

    if not ngo_nearby:
        findings.append({
            'question': 'Q8.3: Are there NGOs working in this area despite evident need?',
            'answer': f'No NGO or international organization presence detected within 100km of {d["name"]}. ' +
                      f'This area has a population of ~{d["population"]:,} with significant unmet needs, ' +
                      f'making it a high-priority target for development organizations.',
            'confidence': 'medium',
            'flag': 'alert',
        })
    else:
        findings.append({
            'question': 'Q8.3: Are there NGOs working in this area?',
            'answer': f'At least one NGO/mission-affiliated facility exists within 100km, but coverage gaps remain significant for the population of ~{d["population"]:,}.',
            'confidence': 'medium',
        })

    return findings


def generate_desert_recommendations(d):
    """Generate actionable recommendations."""
    recs = []
    if d['nearestDistance_km'] > 80:
        recs.append("Deploy mobile health clinics for emergency triage and stabilization")
    recs.append("Establish telemedicine link to nearest specialist hospital for remote consultation")
    if 'generalSurgery' in d['missingSpecialties']:
        recs.append("Prioritize surgical capacity — even a minor surgical theatre could save lives in emergency cases")
    if 'gynecologyAndObstetrics' in d['missingSpecialties'] or 'pediatrics' in d['missingSpecialties']:
        recs.append("Urgent need for maternal and child health services — high maternal mortality area")
    if 'emergencyMedicine' in d['missingSpecialties']:
        recs.append("Establish 24/7 emergency stabilization point to reduce transfer mortality")
    if 'ophthalmology' in d['missingSpecialties']:
        recs.append("Schedule periodic ophthalmology outreach camps (high prevalence of preventable blindness)")
    recs.append("Recruit and train community health workers for early detection and referral pathways")
    return recs


# ──────────────────────────────────────────
#  Facility selections (with real coords)
# ──────────────────────────────────────────
FACILITY_SELECTIONS = [
    (368, 5.5560, -0.1969),   # Greater Accra Regional Hospital
    (388, 5.5780, -0.2110),   # HealthLink Hospital, Accra
    (189, 5.6380, -0.2350),   # Chrispod Hospital, Dome
    (515, 5.5810, -0.1040),   # Lekma Hospital, Teshie
    (461, 6.2950, 0.0500),    # Kings & Queens Medical Univ, Akosombo
    (511, 9.4075, -0.8390),   # Le Mete NGO, Tamale
    (133, 7.0940, -2.0280),   # Bechem Government Hospital
    (58,  6.1200, 0.8000),    # Akatsi South Municipal Hospital
    (125, 7.3349, -2.3266),   # Banhart Specialist Hospital, Sunyani
    (756, 6.9500, -2.0833),   # St. John of God Hospital, Duayaw Nkwanta
]

DESERT_ZONES = [
    {
        'name': 'Bole District', 'lat': 9.0333, 'lng': -2.4833, 'region': 'Savannah Region',
        'population': 61593, 'nearestFacility': 'Tamale Teaching Hospital', 'nearestDistance_km': 148,
        'missingSpecialties': ['neurosurgery','cardiology','nephrology','oncology','neonatology'],
        'context': 'Bole District is in the Savannah Region with a population of ~61,000. The nearest hospital with surgical capability is Tamale Teaching Hospital, 148km away on poorly maintained roads. The district has a few CHPS compounds but no hospital with surgical, emergency, or specialist capacity. Maternal mortality is significantly above the national average.',
    },
    {
        'name': 'Damongo', 'lat': 9.0833, 'lng': -1.8167, 'region': 'Savannah Region',
        'population': 38000, 'nearestFacility': 'Tamale Teaching Hospital', 'nearestDistance_km': 95,
        'missingSpecialties': ['generalSurgery','orthopedicSurgery','ophthalmology','radiology','emergencyMedicine'],
        'context': 'Damongo is the capital of the Savannah Region but lacks a well-equipped hospital. The West Gonja District Hospital has minimal capacity. Patients requiring surgery or specialist care must travel to Tamale. Road conditions deteriorate severely during the rainy season.',
    },
    {
        'name': 'Nalerigu', 'lat': 10.5250, 'lng': -0.3700, 'region': 'North East Region',
        'population': 28000, 'nearestFacility': 'Baptist Medical Centre Nalerigu', 'nearestDistance_km': 0,
        'missingSpecialties': ['neurosurgery','cardiology','oncology','nephrology','psychiatry'],
        'context': 'While Nalerigu has the Baptist Medical Centre (one of few hospitals in the North East Region), it serves an enormous catchment of over 500,000 people across multiple districts. The hospital has limited specialist capacity and no advanced imaging. Most surrounding communities are 50-100km from any health facility.',
    },
    {
        'name': 'Nandom', 'lat': 10.8500, 'lng': -2.7500, 'region': 'Upper West Region',
        'population': 48000, 'nearestFacility': 'Nandom District Hospital', 'nearestDistance_km': 0,
        'missingSpecialties': ['generalSurgery','orthopedicSurgery','ophthalmology','pediatrics','radiology'],
        'context': 'Nandom is in Ghana\'s most underserved region. The district hospital exists but has severe staffing shortages — often operating without a single doctor. The Upper West Region has the lowest doctor-to-patient ratio in Ghana at 1:30,000+. Most patients requiring anything beyond basic care must travel to Wa (110km) or Tamale (350km).',
    },
    {
        'name': 'Dambai', 'lat': 8.0667, 'lng': 0.1833, 'region': 'Oti Region',
        'population': 35000, 'nearestFacility': 'Nkwanta District Hospital', 'nearestDistance_km': 72,
        'missingSpecialties': ['generalSurgery','emergencyMedicine','gynecologyAndObstetrics','pediatrics','radiology'],
        'context': 'Dambai is the capital of the newly created Oti Region (2019), carved from the Volta Region. Despite being a regional capital, healthcare infrastructure has not kept pace. The town sits on the eastern bank of the Volta Lake, and many communities depend on boat transport. The nearest hospital with surgical capacity is 72km away on unpaved roads.',
    },
    {
        'name': 'Kadjebi', 'lat': 7.5333, 'lng': 0.5333, 'region': 'Oti Region',
        'population': 46000, 'nearestFacility': 'Kadjebi Health Centre', 'nearestDistance_km': 85,
        'missingSpecialties': ['generalSurgery','emergencyMedicine','ophthalmology','dentistry','radiology'],
        'context': 'Kadjebi District in the Oti Region is mountainous with scattered communities that are extremely difficult to reach. The health centre has no surgical capability, limited medication, and intermittent electricity. Pregnant women in emergency situations face dangerous journeys of 2-4 hours to reach the nearest hospital. Snake bite cases — common in this region — often result in death due to lack of antivenom.',
    },
    {
        'name': 'Donkorkrom', 'lat': 6.6333, 'lng': -0.1333, 'region': 'Eastern Region',
        'population': 31000, 'nearestFacility': 'Atua Government Hospital', 'nearestDistance_km': 65,
        'missingSpecialties': ['generalSurgery','pediatrics','ophthalmology','radiology','emergencyMedicine'],
        'context': 'Donkorkrom in the Kwahu Afram Plains District is one of the most isolated areas in the Eastern Region. Located across the Volta Lake, many communities can only be reached by boat. The health centre has no doctor and minimal equipment. The population has high rates of bilharzia and waterborne diseases, yet no diagnostic capability exists.',
    },
    {
        'name': 'Enchi', 'lat': 5.8333, 'lng': -2.8333, 'region': 'Western North Region',
        'population': 42000, 'nearestFacility': 'Enchi District Hospital', 'nearestDistance_km': 0,
        'missingSpecialties': ['neurology','cardiology','orthopedicSurgery','ophthalmology','radiology'],
        'context': 'Enchi is the capital of Aowin Municipal in Western North Region. The district hospital is severely under-resourced, serving a large catchment including many cocoa farming communities with high rates of pesticide-related illness. The nearest specialist hospital is in Takoradi (180km). Galamsey (illegal mining) activities create significant health hazards with no local treatment capacity.',
    },
    {
        'name': 'Tumu', 'lat': 10.8833, 'lng': -1.9833, 'region': 'Upper West Region',
        'population': 20000, 'nearestFacility': 'Tumu District Hospital', 'nearestDistance_km': 0,
        'missingSpecialties': ['generalSurgery','gynecologyAndObstetrics','pediatrics','ophthalmology','emergencyMedicine'],
        'context': 'Tumu is the capital of Sissala East District in the Upper West Region, near the Burkina Faso border. The district hospital has minimal capacity and frequently runs without a doctor. The Sissala districts have some of Ghana\'s worst health indicators: high maternal mortality, high under-5 mortality, and widespread malnutrition. Cross-border disease outbreaks (meningitis, cholera) from Burkina Faso regularly overwhelm the limited health infrastructure.',
    },
    {
        'name': 'Kete Krachi', 'lat': 7.8000, 'lng': -0.0333, 'region': 'Oti Region',
        'population': 35000, 'nearestFacility': 'Kete Krachi District Hospital', 'nearestDistance_km': 0,
        'missingSpecialties': ['generalSurgery','ophthalmology','radiology','cardiology','psychiatry'],
        'context': 'Kete Krachi sits on a peninsula jutting into the Volta Lake. Many communities in its catchment can only be reached by boat, making emergency medical transfers extremely challenging. The district hospital has basic capability but no surgical theatre and limited diagnostic equipment. River blindness (onchocerciasis) remains endemic in surrounding communities, yet ophthalmological services are completely absent.',
    },
]


SYSTEM_PROMPT_FACILITY = """You are a healthcare intelligence analyst for the Virtue Foundation, analyzing healthcare facilities in Ghana.
You are given structured data extracted from a facility's CSV record plus rule-based analysis findings.
Write a concise but insightful summary (3-5 paragraphs) that:
1. Describes the facility's capabilities and role in its region
2. Highlights any RED FLAGS or anomalies (equipment mismatches, suspicious claims, missing data)
3. Assesses whether the facility's claimed specialties are realistic given its infrastructure
4. Notes workforce signals (visiting vs permanent staff, staffing adequacy)
5. Identifies what this facility is critical for in its region (sole provider of certain specialties?)
Be direct and analytical. Use specific data points. Flag concerns clearly."""

SYSTEM_PROMPT_DESERT = """You are a healthcare intelligence analyst for the Virtue Foundation, identifying medical deserts in Ghana.
You are given data about an underserved area including population, nearest facilities, and missing specialties.
Write a concise but powerful summary (3-5 paragraphs) that:
1. Explains why this area is a medical desert and the human impact
2. Quantifies the gap (distance to care, population affected, missing capabilities)
3. Identifies the most urgent unmet needs
4. Suggests specific, actionable interventions prioritized by impact
5. Notes any compounding factors (geography, seasonal access, cross-border issues)
Be direct and evidence-based. This analysis will be used by NGO planners to allocate resources."""


def ai_summarize_facility(f, analysis_findings):
    """Generate AI summary for a facility using OpenAI."""
    user_msg = f"""Facility: {f['name']}
Location: {f['city']}, {f['region']}
Type: {f['facilityType']}
Bed Capacity: {f['bedCapacity'] or 'Unknown'}
Doctors: {f['numDoctors'] or 'Unknown'}
Specialties ({len(f['specialties'])}): {', '.join(f['specialties'][:15])}
Equipment listed: {', '.join(f['equipment'][:10]) if f['equipment'] else 'NONE reported'}
Key capabilities: {'; '.join(f['capabilities'][:6])}
Description: {f['description'][:300]}

Rule-based analysis findings:
"""
    for cat, findings in analysis_findings.items():
        for finding in findings:
            flag = finding.get('flag', 'info')
            user_msg += f"\n[{flag.upper()}] {finding['question']}: {finding['answer']}"

    return call_openai(SYSTEM_PROMPT_FACILITY, user_msg)


def ai_summarize_desert(d, analysis_findings):
    """Generate AI summary for a medical desert using OpenAI."""
    user_msg = f"""Medical Desert: {d['name']}
Region: {d['region']}
Population: ~{d['population']:,}
Nearest Facility: {d['nearestFacility']} ({d['nearestDistance_km']}km away)
Missing Specialties: {', '.join(d['missingSpecialties'])}
Context: {d['context']}

Rule-based analysis findings:
"""
    for cat, findings in analysis_findings.items():
        for finding in findings:
            flag = finding.get('flag', 'info')
            user_msg += f"\n[{flag.upper()}] {finding['question']}: {finding['answer']}"

    return call_openai(SYSTEM_PROMPT_DESERT, user_msg)


def main():
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from CSV")

    # Index by region/city for cross-referencing
    by_region = {}
    by_city = {}
    for r in rows:
        region = clean(r.get('address_stateOrRegion', ''))
        city = clean(r.get('address_city', ''))
        if region:
            by_region.setdefault(region, []).append(r)
        if city:
            by_city.setdefault(city, []).append(r)

    output = {'facilities': [], 'deserts': [], 'metadata': {}}

    # ── Process facilities ──
    for row_idx, lat, lng in FACILITY_SELECTIONS:
        raw = rows[row_idx]
        f = extract_facility(raw, row_idx)

        # Get regional context
        region_rows = by_region.get(f['region'], []) or by_city.get(f['city'], [])

        # Run all analysis categories
        analysis = {
            'basicLookups': analyze_basic_lookups(f, region_rows),
            'validation': analyze_validation(f),
            'anomalyDetection': analyze_anomalies(f),
            'serviceClassification': analyze_service_classification(f),
            'workforceDistribution': analyze_workforce(f),
            'resourceGaps': analyze_resource_gaps(f, region_rows),
            'ngoAnalysis': analyze_ngo(f),
        }

        # Count flags
        all_findings = []
        for cat_findings in analysis.values():
            all_findings.extend(cat_findings)
        alerts = sum(1 for fi in all_findings if fi.get('flag') == 'alert')
        warnings = sum(1 for fi in all_findings if fi.get('flag') == 'warning')

        # AI summary
        ai_summary = None
        if OPENAI_API_KEY:
            print(f"    🤖 Generating AI summary...")
            ai_summary = ai_summarize_facility(f, analysis)
            if ai_summary:
                print(f"    ✅ Got {len(ai_summary)} chars")
            time.sleep(0.5)  # rate limit

        output['facilities'].append({
            'id': f'facility_{row_idx}',
            'type': 'facility',
            'lat': lat, 'lng': lng,
            'name': f['name'],
            'city': f['city'],
            'region': f['region'],
            'facilityType': f['facilityType'],
            'specialties': f['specialties'],
            'equipment': f['equipment'],
            'capabilities': f['capabilities'][:8],
            'numDoctors': f['numDoctors'],
            'bedCapacity': f['bedCapacity'],
            'analysis': analysis,
            'aiSummary': ai_summary,
            'alertCount': alerts,
            'warningCount': warnings,
            'citation': {
                'csvRow': f['csvRow'],
                'source': f['sourceUrl'],
                'fields_used': ['specialties', 'procedure', 'equipment', 'capability', 'description', 'organizationDescription', 'numberDoctors', 'capacity'],
            },
        })
        flags = f" ({alerts} alerts, {warnings} warnings)" if alerts or warnings else ""
        print(f"  + Facility: {f['name'][:50]} ({f['city']}){flags}")

    # ── Process desert zones ──
    for d in DESERT_ZONES:
        # Calculate severity
        severity = 2
        if d['nearestDistance_km'] > 100: severity += 3
        elif d['nearestDistance_km'] > 50: severity += 2
        elif d['nearestDistance_km'] > 0: severity += 1
        severity += min(len(d['missingSpecialties']), 3)
        if d['population'] > 40000: severity += 2
        elif d['population'] > 20000: severity += 1
        severity = min(10, severity)

        # Run analysis
        analysis = {
            'geospatial': analyze_desert_geospatial(d, output['facilities']),
            'unmetNeeds': analyze_desert_unmet_needs(d),
            'ngoGaps': analyze_desert_ngo_gaps(d, output['facilities']),
        }

        recommendations = generate_desert_recommendations(d)

        all_findings = []
        for cat_findings in analysis.values():
            all_findings.extend(cat_findings)
        alerts = sum(1 for fi in all_findings if fi.get('flag') == 'alert')

        # AI summary
        ai_summary = None
        if OPENAI_API_KEY:
            print(f"    🤖 Generating AI summary...")
            ai_summary = ai_summarize_desert(d, analysis)
            if ai_summary:
                print(f"    ✅ Got {len(ai_summary)} chars")
            time.sleep(0.5)

        output['deserts'].append({
            'id': f'desert_{d["name"].lower().replace(" ", "_")}',
            'type': 'desert',
            'lat': d['lat'], 'lng': d['lng'],
            'name': d['name'],
            'region': d['region'],
            'population': d['population'],
            'nearestFacility': d['nearestFacility'],
            'nearestDistance_km': d['nearestDistance_km'],
            'missingSpecialties': d['missingSpecialties'],
            'context': d['context'],
            'severityScore': severity,
            'analysis': analysis,
            'aiSummary': ai_summary,
            'recommendations': recommendations,
            'alertCount': alerts,
        })
        print(f"  + Desert: {d['name']} (severity: {severity}/10, {alerts} alerts)")

    # ── Metadata ──
    total_alerts = sum(f['alertCount'] for f in output['facilities']) + sum(d['alertCount'] for d in output['deserts'])
    total_warnings = sum(f.get('warningCount', 0) for f in output['facilities'])
    output['metadata'] = {
        'totalFacilities': len(output['facilities']),
        'totalDeserts': len(output['deserts']),
        'csvRowsAnalyzed': len(rows),
        'totalAlerts': total_alerts,
        'totalWarnings': total_warnings,
        'questionCategories': [
            'Q1: Basic Queries & Lookups',
            'Q2: Geospatial Queries',
            'Q3: Validation & Verification',
            'Q4: Misrepresentation & Anomaly Detection',
            'Q5: Service Classification & Inference',
            'Q6: Workforce Distribution',
            'Q7: Resource Distribution & Gaps',
            'Q8: NGO & International Organization Analysis',
            'Q9: Unmet Needs & Demand Analysis',
        ],
        'dataSource': 'Virtue Foundation Ghana v0.3',
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    size = os.path.getsize(OUTPUT_FILE)
    print(f"\nSaved {OUTPUT_FILE} ({size//1024}KB)")
    print(f"  {len(output['facilities'])} facilities + {len(output['deserts'])} desert zones")
    print(f"  {total_alerts} alerts, {total_warnings} warnings detected")


if __name__ == '__main__':
    main()
