import os
import io
import re
import json
import streamlit as st
from datetime import datetime

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
except ImportError:
    SimpleDocTemplate = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


st.set_page_config(
    page_title="STALWART Civic Auditor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚖️ STALWART CIVIC ENFORCEMENT AUDITOR v12.0")
st.markdown("*(Automated Legislative/Policy Analysis, Real-Time Contact Discovery & Dynamic Civic Playbooks)*")

# Sidebar for API Configuration & AI Toggle
with st.sidebar:
    st.header("⚙️ Audit Configuration")
    ai_toggle = st.checkbox("Enable Gemini AI Analysis", value=False, help="Uncheck to run offline zero-cost baseline regex checks.")
    
    if ai_toggle:
        api_key_input = st.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
        if api_key_input:
            os.environ["GEMINI_API_KEY"] = api_key_input


def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        if PdfReader is None:
            return "Error: pypdf not installed."
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text.replace('\n', ' ') + '\n'
    else:
        text = uploaded_file.read().decode('utf-8', errors='ignore')
    return text


def clean_snippet(text, match_start, match_end, window=140):
    """Extracts a readable snippet window around a regex match."""
    start = max(0, match_start - window)
    end = min(len(text), match_end + window)
    raw = text[start:end].replace('\n', ' ').strip()
    return f"...{raw}..."


def analyze_document_locally(document_text, filename):
    """Full deterministic forensic regex engine (Zero Cost, No API)."""
    ground_facts = []
    authorities = []
    alerts = []

    # 1. Extract Ground Truth Metrics
    dollars = set(re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|trillion))?', document_text, re.IGNORECASE))
    citations = set(re.findall(r'(?:\b\d+\s+U\.S\.C\.\s+§?\s*[\d\w\-]+|\bRCW\s+[\d\.]+|\bSection\s+\d{3,5}[a-zA-Z0-9\-]*)', document_text, re.IGNORECASE))
    dates = set(re.findall(r'(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}|\b\d{1,2}/\d{1,2}/\d{2,4}\b)', document_text))
    percentages = set(re.findall(r'\b\d+(?:\.\d+)?%', document_text))

    ground_facts.append(f"Audit Target: {filename} (Scanned locally via Deterministic Regex Engine)")
    if dollars:
        ground_facts.append(f"Financial Allocations Identified ({len(dollars)} items): {', '.join(list(dollars)[:8])}")
    if citations:
        ground_facts.append(f"Statutory Cites Detected ({len(citations)} items): {', '.join(list(citations)[:8])}")
    if dates:
        ground_facts.append(f"Operational Deadlines / Dates: {', '.join(list(dates)[:6])}")
    if percentages:
        ground_facts.append(f"Numerical Thresholds / Metrics: {', '.join(list(percentages)[:6])}")

    # 2. Extract Responsible Bodies & Agencies
    agency_patterns = [
        r'(?:Department of (?:the Interior|Energy|Transportation|Defense|Commerce|Agriculture|State|Treasury))',
        r'(?:Bureau of Land Management|Environmental Protection Agency|Internal Revenue Service|Federal Energy Regulatory Commission)',
        r'(?:Office of [A-Z][a-z]+(?: [A-Z][a-z]+)*)',
        r'(?:Secretary of [A-Z][a-z]+|Administrator|Attorney General|Comptroller)'
    ]
    detected_agencies = set()
    for pattern in agency_patterns:
        matches = re.findall(pattern, document_text, re.IGNORECASE)
        for m in matches:
            detected_agencies.add(m.strip())

    if detected_agencies:
        for agency in list(detected_agencies)[:6]:
            authorities.append({
                "agency_or_body": agency,
                "officials": [
                    {
                        "name": f"{agency} Administrative Officer",
                        "role": "Regulatory Oversight & Rulemaking Officer",
                        "public_contact": "Public Liaison / FOIA Portal"
                    }
                ],
                "escalation_procedure": f"Submit administrative petition or formal public records demand to {agency} pursuant to 5 U.S.C. § 552 / APA."
            })
    else:
        authorities.append({
            "agency_or_body": "Designated Regulatory Authority",
            "officials": [
                {
                    "name": "Governing Body Clerk",
                    "role": "Administrative Record Keeper",
                    "public_contact": "Official Public Registry"
                }
            ],
            "escalation_procedure": "Inspect docket index and petition administrative head under standard notice-and-comment requirements."
        })

    # 3. Deterministic Forensic Statutory Alerts
    alert_rules = [
        {
            "type": "STATUTORY OVERRIDE | DUE PROCESS BYPASS",
            "pattern": r'(?:notwithstanding any other provision|shall supersede|without regard to (?:section|title|law|subchapter)|waives compliance)',
            "plain_english": "Drafted with preemptive override language to bypass existing citizen review laws, environmental compliance (NEPA/EPA), or standard public hearing rights.",
            "pipeline": "Grants sweeping authority to administrative directors; shields recipients from statutory review.",
            "action": "File formal challenge under 5 U.S.C. § 706 (Arbitrary, Capricious, and Unlawful Agency Action) or petition legislative review board."
        },
        {
            "type": "SOLE SOURCE CARVEOUT | EXCLUSIONARY MANDATE",
            "pattern": r'(?:defined as excluding|shall not apply to any entity|special classification|shall offer the lesser of|sole source|exclusive agreement)',
            "plain_english": "Creates a carved-out legal tier that protects incumbent operations or creates conditional hurdles for competitor tech/clean energy adoption.",
            "pipeline": "Directs market control or federal access to pre-qualified entities while filtering out third-party solutions.",
            "action": "Invoke Equal Protection Clause precedents (Yick Wo v. Hopkins) and file anti-competitive procurement objections."
        },
        {
            "type": "BLANK-CHECK DELEGATION | APPROPRIATED SLUSH FUND",
            "pattern": r'(?:shall be available for|appropriated to the Secretary|unobligated balances|retained until expended|at the sole discretion)',
            "plain_english": "Appropriates multi-million/billion dollar funds with broad spending discretion and minimal audit requirements.",
            "pipeline": "Disburses public revenue directly to designated accounts without mandatory line-item oversight.",
            "action": "File targeted Freedom of Information Act (FOIA) requests demanding transactional receipts, fund ledger transfers, and PAC donation intersections."
        },
        {
            "type": "JUDICIAL PRECLUSION | ADMINISTRATIVE IMMUNITY",
            "pattern": r'(?:shall not be subject to judicial review|final and non-reviewable|no court shall have jurisdiction|immune from liability)',
            "plain_english": "Strips judicial review power from federal/state courts to prevent citizens from seeking injunctions against improper administrative execution.",
            "pipeline": "Shields agency executives and private contractors from legal liability.",
            "action": "Challenge statutory jurisdiction stripping under Article III constitutional separation-of-powers doctrine."
        }
    ]

    for rule in alert_rules:
        for match in re.finditer(rule["pattern"], document_text, re.IGNORECASE):
            snippet = clean_snippet(document_text, match.start(), match.end())
            alerts.append({
                "citation_type": rule["type"],
                "verbatim_text": snippet,
                "plain_english": rule["plain_english"],
                "financial_pipeline": rule["pipeline"],
                "tailored_action_plan": rule["action"]
            })
            if len(alerts) >= 12:  # Limit total alerts to prevent runaway loops on huge bills
                break
        if len(alerts) >= 12:
            break

    if not alerts:
        alerts.append({
            "citation_type": "CLEAN BASELINE SCAN",
            "verbatim_text": "No explicit statutory override or bypass keywords found in current text sample.",
            "plain_english": "The text does not contain explicit override phrases like 'notwithstanding' or 'exclusive agreement'.",
            "financial_pipeline": "Standard accounting/appropriations framework.",
            "tailored_action_plan": "Execute deep scan across referenced amendment codes or verify with AI enabled."
        })

    return {
        "ground_truth_facts": ground_facts,
        "responsible_authorities": authorities,
        "statutory_alerts": alerts
    }


def analyze_document_with_ai(document_text, filename):
    if genai is None or not os.environ.get("GEMINI_API_KEY"):
        return {"error": "Missing Gemini API Key or google-genai library."}

    client = genai.Client()
    
    prompt = f"""
    You are the STALWART Forensic Legislative Auditor. Analyze the following document text from '{filename}':

    Execute a thorough audit and return a strictly valid JSON object with the following schema:
    {{
        "ground_truth_facts": ["Extracted hard data points (chemical quantities, dollar amounts, dates, penalty amounts, operational status)"],
        "responsible_authorities": [
            {{
                "agency_or_body": "Name of Agency / Municipality / Department",
                "officials": [{{"name": "Official Name or Specific Office Title", "role": "Role / Position", "public_contact": "Public phone, email, or official portal link"}}],
                "escalation_procedure": "Exact public process to file a comment, petition, appeal, or FOIA request with this specific body"
            }}
        ],
        "statutory_alerts": [
            {{
                "citation_type": "STATUTORY OVERRIDE | DUE PROCESS BYPASS | BLANK-CHECK DELEGATION | SOLE SOURCE CARVEOUT | LOCAL PREEMPTION",
                "verbatim_text": "Exact quote from document",
                "plain_english": "Layman translation explaining how this impacts citizen rights or property",
                "financial_pipeline": "Who gets paid, exempted, or shielded",
                "tailored_action_plan": "Specific legal or civic counter-action tailored exclusively to this document's subject matter"
            }}
        ]
    }}
    Document Text:
    {document_text}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}


def generate_dossier_pdf(audit_results, source_files):
    if SimpleDocTemplate is None:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name="TitleStyle", parent=styles['Heading1'], alignment=1, spaceAfter=20, textColor=HexColor("#000000"))
    heading_style = ParagraphStyle(name="HeadingStyle", parent=styles['Heading2'], spaceAfter=10, textColor=HexColor("#1c293b"))
    bold_label = ParagraphStyle(name="BoldLabel", parent=styles['BodyText'], fontName="Helvetica-Bold", spaceBefore=5, textColor=HexColor("#0f172a"))
    plain_english_style = ParagraphStyle(name="PlainEnglish", parent=styles['BodyText'], fontName="Helvetica-BoldOblique", spaceAfter=10, textColor=HexColor("#b91c1c"))
    standard_body = ParagraphStyle(name="StandardBody", parent=styles['BodyText'], spaceAfter=10)
    evidence_body = ParagraphStyle(name="EvidenceBody", parent=styles['BodyText'], spaceAfter=15, fontName="Courier", textColor=HexColor("#334155"))

    flowables = []
    
    flowables.append(Paragraph("STALWART DYNAMIC CIVIC DOSSIER", title_style))
    flowables.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Sources: {', '.join(source_files)}", styles['Normal']))
    flowables.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#000000"), spaceBefore=15, spaceAfter=20))

    if audit_results.get("ground_truth_facts"):
        flowables.append(Paragraph("🎯 EXTRACTED GROUND TRUTH", heading_style))
        for fact in audit_results.get("ground_truth_facts"):
            flowables.append(Paragraph(f"• {fact}", standard_body))
        flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=15))

    if audit_results.get("responsible_authorities"):
        flowables.append(Paragraph("🏛️ PUBLIC OFFICIALS & ESCALATION DIRECTORY", heading_style))
        for auth in audit_results.get("responsible_authorities"):
            flowables.append(Paragraph(f"Agency/Body: {auth.get('agency_or_body', 'Unknown')}", bold_label))
            for off in auth.get("officials", []):
                flowables.append(Paragraph(f"• {off.get('name')} ({off.get('role')}): {off.get('public_contact')}", standard_body))
            flowables.append(Paragraph(f"Escalation Process: {auth.get('escalation_procedure')}", standard_body))
        flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=15))

    if audit_results.get("statutory_alerts"):
        flowables.append(Paragraph("⚠️ FORENSIC STATUTORY ALERTS", heading_style))
        for idx, alert in enumerate(audit_results.get("statutory_alerts")):
            flowables.append(Paragraph(f"Alert #{idx+1}: {alert.get('citation_type')}", heading_style))
            flowables.append(Paragraph("Plain English Impact:", bold_label))
            flowables.append(Paragraph(f"{alert.get('plain_english', '')}", plain_english_style))
            flowables.append(Paragraph("Verbatim Text:", bold_label))
            flowables.append(Paragraph(f"\"{alert.get('verbatim_text', '')}\"", evidence_body))
            flowables.append(Paragraph("Financial/Regulatory Pipeline:", bold_label))
            flowables.append(Paragraph(f"{alert.get('financial_pipeline', '')}", standard_body))
            flowables.append(Paragraph("Tailored Civic Action Plan:", bold_label))
            flowables.append(Paragraph(f"{alert.get('tailored_action_plan', '')}", standard_body))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e2e8f0"), spaceBefore=10, spaceAfter=15))

    doc.build(flowables)
    return buffer.getvalue()


uploaded_files = st.file_uploader("UPLOAD LEGISLATIVE BILLS, BUDGETS, OR GOV ORDERS (PDF/TXT)", type=["txt", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("EXECUTE DYNAMIC FORENSIC AUDIT"):
        combined_text = ""
        filenames = [f.name for f in uploaded_files]
        
        with st.spinner("Extracting text and running multi-vector reasoning engine..."):
            for f in uploaded_files:
                combined_text += f"\n--- Source: {f.name} ---\n" + extract_text_from_file(f)
            
            if ai_toggle:
                audit_data = analyze_document_with_ai(combined_text, ", ".join(filenames))
            else:
                audit_data = analyze_document_locally(combined_text, ", ".join(filenames))

        if "error" in audit_data:
            st.error(f"Analysis Error: {audit_data['error']}")
        else:
            st.session_state.current_audit = audit_data
            st.session_state.source_filenames = filenames

if 'current_audit' in st.session_state and st.session_state.current_audit:
    data = st.session_state.current_audit
    st.success("✔️ AUDIT COMPLETE: Contextual intelligence and customized escalation plan generated.")

    if SimpleDocTemplate is not None:
        pdf_bytes = generate_dossier_pdf(data, st.session_state.source_filenames)
        if pdf_bytes:
            st.download_button(
                label="📥 DOWNLOAD DYNAMIC CIVIC DOSSIER (PDF)",
                data=pdf_bytes,
                file_name=f"STALWART_Dossier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

    st.divider()

    if data.get("ground_truth_facts"):
        st.subheader("🎯 EXTRACTED GROUND TRUTH")
        for fact in data.get("ground_truth_facts"):
            st.markdown(f"• {fact}")

    if data.get("responsible_authorities"):
        st.subheader("🏛️ PUBLIC OFFICIALS & ESCALATION DIRECTORY")
        for auth in data.get("responsible_authorities"):
            with st.expander(f"**{auth.get('agency_or_body')}**", expanded=True):
                for off in auth.get("officials", []):
                    st.write(f"• **{off.get('name')}** ({off.get('role')}): {off.get('public_contact')}")
                if auth.get("escalation_procedure"):
                    st.info(f"**Escalation Process:** {auth.get('escalation_procedure')}")

    if data.get("statutory_alerts"):
        st.subheader("⚠️ FORENSIC STATUTORY ALERTS")
        for idx, alert in enumerate(data.get("statutory_alerts")):
            with st.container():
                st.markdown(f"### Alert #{idx+1} | {alert.get('citation_type')}")
                st.error(alert.get("plain_english"))
                st.markdown(f"**Verbatim Text:** \n> *\"{alert.get('verbatim_text')}\"*")
                st.markdown(f"**Financial/Regulatory Pipeline:** {alert.get('financial_pipeline')}")
                st.markdown(f"**Tailored Civic Action Plan:** \n{alert.get('tailored_action_plan')}")
                st.divider()
