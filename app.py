from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import re


# Load spaCy model
nlp = spacy.load("en_core_web_sm")


# Create FastAPI app
app = FastAPI(
    title="TraceGuard AI",
    description="AI Digital Footprint and Privacy Risk Analyzer"
)


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class TextInput(BaseModel):
    text: str


# --------------------------------------------------
# EMAIL DETECTION
# --------------------------------------------------

def detect_email(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    return re.findall(pattern, text)


# --------------------------------------------------
# PHONE DETECTION
# --------------------------------------------------

def detect_phone(text):
    pattern = r'\b[6-9]\d{9}\b'
    return re.findall(pattern, text)


# --------------------------------------------------
# ENTITY DETECTION
# --------------------------------------------------

def detect_entities(text):
    doc = nlp(text)
    entities = []

    # Common city/location names
    common_locations = {
        "hyderabad",
        "bangalore",
        "bengaluru",
        "mumbai",
        "delhi",
        "chennai",
        "pune",
        "kolkata",
        "ahmedabad",
        "jaipur",
        "visakhapatnam",
        "vijayawada",
        "warangal"
    }

    # Detect "My name is X"
    name_match = re.search(
        r'\bmy name is\s+([A-Za-z]+)',
        text,
        re.IGNORECASE
    )

    detected_name = None

    if name_match:
        detected_name = name_match.group(1)

    for ent in doc.ents:

        # Ignore anything that is actually a phone number
        if re.fullmatch(r'[6-9]\d{9}', ent.text):
            continue

        # Force known cities to LOCATION
        if ent.text.lower() in common_locations:
            entity_type = "LOCATION"

        elif ent.label_ == "PERSON":
            entity_type = "PERSON"

        elif ent.label_ == "ORG":
            entity_type = "ORGANIZATION"

        elif ent.label_ == "GPE":
            entity_type = "LOCATION"

        elif ent.label_ == "DATE":
            entity_type = "DATE"

        else:
            continue

        # General name detection
        if detected_name and ent.text.lower() == detected_name.lower():
            entity_type = "PERSON"

        # Hyderabad correction
        if ent.text.lower() == "hyderabad":
            entity_type = "LOCATION"

        entities.append({
            "type": entity_type,
            "value": ent.text
        })

    # If spaCy completely missed the name
    if detected_name:
        already_detected = any(
            entity["value"].lower() == detected_name.lower()
            for entity in entities
        )

        if not already_detected:
            entities.insert(
                0,
                {
                    "type": "PERSON",
                    "value": detected_name
                }
            )

    return entities


# --------------------------------------------------
# RISK CALCULATION
# --------------------------------------------------

def calculate_risk(emails, phones, entities):

    score = 0

    # Email risk
    score += len(emails) * 20

    # Phone risk
    score += len(phones) * 40

    # Entity risk
    for entity in entities:

        if entity["type"] == "PERSON":
            score += 5

        elif entity["type"] == "ORGANIZATION":
            score += 10

        elif entity["type"] == "LOCATION":
            score += 20

        elif entity["type"] == "DATE":
            score += 15

    # Maximum base score
    score = min(score, 100)

    # Risk level
    if score >= 70:
        level = "High"

    elif score >= 30:
        level = "Medium"

    else:
        level = "Low"

    return score, level


# --------------------------------------------------
# COMPOUND RISK DETECTION
# --------------------------------------------------

def detect_compound_risks(
    entities,
    emails,
    phones,
    text
):

    compound_risks = []

    entity_types = [
        entity["type"]
        for entity in entities
    ]

    # Location + Date
    if (
        "LOCATION" in entity_types
        and "DATE" in entity_types
    ):

        compound_risks.append({
            "type": "Location + Date Exposure",
            "value": "Location and date appear together",
            "risk": "High",
            "points": 15
        })

    # Phone + Location
    if (
        phones
        and "LOCATION" in entity_types
    ):

        compound_risks.append({
            "type": "Phone + Location Exposure",
            "value": "Phone number and location appear together",
            "risk": "High",
            "points": 20
        })

    # Email + Organization + Location
    if (
        emails
        and "ORGANIZATION" in entity_types
        and "LOCATION" in entity_types
    ):

        compound_risks.append({
            "type": "Identity Correlation Risk",
            "value": "Email, organization and location appear together",
            "risk": "High",
            "points": 15
        })

    # Absence exposure
    absence_keywords = [
        "away from home",
        "out of town",
        "on vacation",
        "on holiday",
        "house will be empty",
        "home will be empty",
        "traveling",
        "travelling"
    ]

    text_lower = text.lower()

    for keyword in absence_keywords:

        if keyword in text_lower:

            compound_risks.append({
                "type": "Absence Exposure",
                "value": "Text indicates absence from home",
                "risk": "High",
                "points": 25
            })

            break

    return compound_risks


# --------------------------------------------------
# PRIVACY RECOMMENDATIONS
# --------------------------------------------------

def generate_recommendations(
    emails,
    phones,
    entities,
    compound_risks
):

    recommendations = []

    entity_types = [
        entity["type"]
        for entity in entities
    ]

    # Email recommendation
    if emails:

        recommendations.append(
            "Avoid publicly sharing your personal email address."
        )

    # Phone recommendation
    if phones:

        recommendations.append(
            "Avoid sharing your phone number publicly and review your privacy settings."
        )

    # Location recommendation
    if "LOCATION" in entity_types:

        recommendations.append(
            "Avoid publicly sharing your exact location."
        )

    # Date recommendation
    if "DATE" in entity_types:

        recommendations.append(
            "Be careful when sharing future dates, travel plans or schedules."
        )

    # Person + Location
    if (
        "PERSON" in entity_types
        and "LOCATION" in entity_types
    ):

        recommendations.append(
            "Avoid combining your full identity with your location."
        )

    # Compound risk recommendations
    for compound_risk in compound_risks:

        if compound_risk["type"] == "Location + Date Exposure":

            recommendations.append(
                "Avoid publicly combining your location with dates or schedules."
            )

        elif compound_risk["type"] == "Phone + Location Exposure":

            recommendations.append(
                "Avoid exposing your phone number together with your location."
            )

        elif compound_risk["type"] == "Identity Correlation Risk":

            recommendations.append(
                "Avoid combining email, organization and location information."
            )

        elif compound_risk["type"] == "Absence Exposure":

            recommendations.append(
                "Avoid publicly announcing when your home may be empty."
            )

    return recommendations


# --------------------------------------------------
# INFERENCE DETECTION
# --------------------------------------------------

def detect_inferences(
    entities,
    emails,
    phones
):

    inferences = []

    entity_types = [
        entity["type"]
        for entity in entities
    ]

    # Person + Organization
    if (
        "PERSON" in entity_types
        and "ORGANIZATION" in entity_types
    ):

        organizations = [
            entity["value"]
            for entity in entities
            if entity["type"] == "ORGANIZATION"
        ]

        for organization in organizations:

            inferences.append({
                "type": "Education / Employment",
                "title": "Possible Organization Association",
                "description": (
                    f"The text connects a person with "
                    f"{organization}, which may reveal an "
                    f"education or employment association."
                ),
                "risk": "Medium"
            })

    # Person + Location
    if (
        "PERSON" in entity_types
        and "LOCATION" in entity_types
    ):

        locations = [
            entity["value"]
            for entity in entities
            if entity["type"] == "LOCATION"
        ]

        for location in locations:

            inferences.append({
                "type": "Identity + Location",
                "title": "Location Profile",
                "description": (
                    f"The person's identity is connected "
                    f"with {location}, which may reveal "
                    f"where they live, study or spend time."
                ),
                "risk": "Medium"
            })

    # Location + Date
    if (
        "LOCATION" in entity_types
        and "DATE" in entity_types
    ):

        inferences.append({
            "type": "Travel / Schedule",
            "title": "Possible Schedule Information",
            "description": (
                "A location and date appear together. "
                "This may reveal a person's travel plans, "
                "schedule or future whereabouts."
            ),
            "risk": "High"
        })

    # Phone + Location
    if (
        phones
        and "LOCATION" in entity_types
    ):

        inferences.append({
            "type": "Contact + Location",
            "title": "Contact Location Correlation",
            "description": (
                "A phone number is connected with a location. "
                "This can make the contact information more "
                "personally identifying."
            ),
            "risk": "High"
        })

    # Email + Organization + Location
    if (
        emails
        and "ORGANIZATION" in entity_types
        and "LOCATION" in entity_types
    ):

        inferences.append({
            "type": "Identity Correlation",
            "title": "Detailed Identity Profile",
            "description": (
                "Email, organization and location information "
                "can be combined to create a more detailed "
                "profile of the person."
            ),
            "risk": "High"
        })

    return inferences


# --------------------------------------------------
# TEXT SANITIZATION
# --------------------------------------------------

def sanitize_text(text):

    # Replace email
    sanitized = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        '[EMAIL]',
        text
    )

    # Replace phone
    sanitized = re.sub(
        r'\b[6-9]\d{9}\b',
        '[PHONE]',
        sanitized
    )

    # Detect entities
    entities = detect_entities(sanitized)

    # Replace longer entities first
    for entity in sorted(
        entities,
        key=lambda x: len(x["value"]),
        reverse=True
    ):

        replacement = {
            "PERSON": "[PERSON]",
            "ORGANIZATION": "[ORGANIZATION]",
            "LOCATION": "[LOCATION]",
            "DATE": "[DATE]"
        }.get(entity["type"])

        if replacement:

            sanitized = sanitized.replace(
                entity["value"],
                replacement
            )

    return sanitized


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "TraceGuard AI is running!"
    }


# --------------------------------------------------
# SANITIZE API
# --------------------------------------------------

@app.post("/sanitize")
def sanitize_privacy(data: TextInput):

    sanitized_text = sanitize_text(
        data.text
    )

    return {
        "original_text": data.text,
        "sanitized_text": sanitized_text
    }


# --------------------------------------------------
# ANALYZE API
# --------------------------------------------------

@app.post("/analyze")
def analyze_privacy(data: TextInput):

    # Detect basic PII
    emails = detect_email(data.text)
    phones = detect_phone(data.text)

    # Detect entities
    entities = detect_entities(data.text)

    # Detect compound risks
    compound_risks = detect_compound_risks(
        entities,
        emails,
        phones,
        data.text
    )

    # Detect possible inferences
    inferences = detect_inferences(
        entities,
        emails,
        phones
    )

    # Generate recommendations
    recommendations = generate_recommendations(
        emails,
        phones,
        entities,
        compound_risks
    )

    # Calculate base risk
    risk_score, risk_level = calculate_risk(
        emails,
        phones,
        entities
    )

    # Add compound risk points
    for compound_risk in compound_risks:

        risk_score += compound_risk["points"]

    # Maximum final score
    risk_score = min(
        risk_score,
        100
    )

    # Final risk level
    if risk_score >= 70:

        risk_level = "High"

    elif risk_score >= 30:

        risk_level = "Medium"

    else:

        risk_level = "Low"

    # Detected information list
    detected_data = []

    # Emails
    for email in emails:

        detected_data.append({
            "type": "Email",
            "value": email,
            "risk": "Medium"
        })

    # Phones
    for phone in phones:

        detected_data.append({
            "type": "Phone Number",
            "value": phone,
            "risk": "High"
        })

    # Entities
    for entity in entities:

        risk = "Low"

        if entity["type"] == "PERSON":

            risk = "Low"

        elif entity["type"] == "ORGANIZATION":

            risk = "Low"

        elif entity["type"] == "LOCATION":

            risk = "Medium"

        elif entity["type"] == "DATE":

            risk = "Medium"

        detected_data.append({
            "type": entity["type"],
            "value": entity["value"],
            "risk": risk
        })

    # Compound risks
    for compound_risk in compound_risks:

        detected_data.append({
            "type": compound_risk["type"],
            "value": compound_risk["value"],
            "risk": compound_risk["risk"]
        })

    # Final response
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "detected_data": detected_data,
        "recommendations": recommendations,
        "inferences": inferences
    }