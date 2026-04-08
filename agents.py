import google.generativeai as genai
import json
import re

# 🔑 Configure Gemini API
genai.configure(api_key="YOUR GEMINI API KEY")

model = genai.GenerativeModel("gemini-2.5-flash")


# 🛠️ Utility: Extract JSON safely from LLM response
def extract_json_with_confidence(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        data = json.loads(match.group())

        # Ensure confidence exists
        if "confidence" not in data:
            data["confidence"] = round(0.7, 2)

        return data
    except:
        return {
            "raw": text,
            "confidence": 0.5
        }


# 🩺 1. Symptom Interpretation Agent
def symptom_agent(symptoms):

    prompt = f"""
    Symptoms: {symptoms}

     Identify the most likely medical condition and severity

    Also provide confidence (0 to 1).

    JSON:
    {{
        "condition": "",
        "severity": "",
        "confidence": 0.0
    }}
    """

    response = model.generate_content(prompt)
    return extract_json_with_confidence(response.text)


# 🧪 2. Diagnostic Agent
def diagnostic_agent(symptom_result):

    prompt = f"""
    You are a clinical decision support system.

    Condition: {symptom_result}

    Suggest ONLY medically appropriate first-line diagnostic tests.

    RULES:
    - Avoid generic tests unless clinically justified
    - Be condition-specific

    Examples:
    - Syncope → ECG, Blood Pressure Monitoring
    - Cardiac issues → ECG, Troponin
    - Infection → CBC

    Return JSON:
    {{
        "tests": [],
        "confidence": 0.0
    }}
    """

    response = model.generate_content(prompt)
    data = extract_json_with_confidence(response.text)

    # ✅ Normalize tests
    if "tests" in data:
        data["tests"] = [str(t) for t in data["tests"]]

    return data


def treatment_agent(symptom_result, treatment):

    prompt = f"""
    You are a healthcare decision system.

    Condition: {symptom_result}
    Selected Treatment: {treatment}

    Evaluate whether the treatment is:
    - Appropriate
    - Over-treatment
    - Under-treatment

    Also provide a short reason.

    RULES:
    - Be clinically logical
    - Keep reason simple (1 line)

    Return ONLY JSON:
    {{
        "status": "",
        "reason": "",
        "confidence": 0.0
    }}
    """

    response = model.generate_content(prompt)
    result = extract_json_with_confidence(response.text)

    # ✅ Rule-based override (important for correctness)
    severity = symptom_result.get("severity", "")

    if severity == "Low" and treatment == "Surgery":
        result["status"] = "Over-treatment"
        result["reason"] = "Surgery is not required for low severity conditions"
        result["confidence"] = 0.9

    elif severity == "High" and treatment == "Consultation":
        result["status"] = "Under-treatment"
        result["reason"] = "Consultation alone may be insufficient for high severity"
        result["confidence"] = 0.9

    return result


# 💰 4. Claim Decision Agent (Hybrid: Rule + LLM)
def claim_agent(plan, cost, treatment, diagnostic):

    if plan == "Basic" and cost > 20000:
        return {
            "status": "Partial Approval",
            "reason": "Cost exceeds basic plan",
            "confidence": 0.85
        }

    prompt = f"""
    Plan: {plan}
    Cost: {cost}
    Treatment: {treatment}
    Diagnostics: {diagnostic}

    Decide claim + confidence.

    JSON:
    {{
        "status": "",
        "reason": "",
        "confidence": 0.0
    }}
    """

    response = model.generate_content(prompt)
    return extract_json_with_confidence(response.text)


# 📄 5. Explanation Agent (XAI)
def explanation_agent(symptom, diagnostic, treatment, claim):

    prompt = f"""
    You are a healthcare AI assistant.

    Summarize the decision process clearly in BULLET POINTS.

    Data:
    Symptom Analysis: {symptom}
    Diagnostics Suggested: {diagnostic}
    Treatment Evaluation: {treatment}
    Claim Decision: {claim}

    RULES:
    - Use short bullet points
    - Each bullet should be 1 line
    - Keep it simple and clear
    - No paragraphs

    Return ONLY JSON:
    {{
        "points": [],
        "confidence": 0.0
    }}
    """

    response = model.generate_content(prompt)
    return extract_json_with_confidence(response.text)