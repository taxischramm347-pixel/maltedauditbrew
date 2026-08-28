import os
import io
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
    page_title="STALWART: Civic Enforcement Auditor v12.0",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚖️ STALWART CIVIC ENFORCEMENT AUDITOR V12.0")
st.caption("AI-Powered Statutory Analysis, Real-Time Contact Discovery & Dynamic Civic Playbooks")

# Sidebar for API Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        if PdfReader is None:
            return ""
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text.replace('-\n', '') + "\n"
    else:
        text = uploaded_file.read().decode('utf-8', errors='ignore')
    return text

def analyze_document_with_ai(document_text, filename):
    """Sends the document to Gemini with Search Grounding to dynamically generate contacts,

    plain-English breakdowns, and a document-specific civic action plan."""
    if not os.environ.get("GEMINI_API_KEY"):
        return None, "Missing Gemini API Key. Please provide an API key in the sidebar."

    client = genai.Client()
    
    prompt = f"""
    You are the STALWART Forensic Legislative Auditor. Analyze the following document text from '{filename}'.
    
    Execute a thorough audit and return a strictly valid JSON object with the following schema:
    {{
        "ground_truth_facts": [
            "Extracted hard data points (chemical quantities, dollar amounts, dates, penalty amounts, operational status)"
        ],
        "responsible_authorities": [
            {{
                "agency_or_body": "Name of Agency / Municipality / Department",
                "officials": [
                    {{
                        "name": "Official Name or Specific Office Title",
                        "role": "Role / Position",
                        "public_contact": "Public phone, email, or official portal link"
                    }}
                ],
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

    DOCUMENT TEXT:
    {document_text[:40000]}
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        return json.loads(response.text), None
    except Exception as e:
        return None, str(e)

def generate_dossier_pdf(audit_results, source_files):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(name="TitleStyle", parent=styles['Heading1'], alignment=1, spaceAfter=20, textColor=HexColor("#8B0000"))
    heading_style = ParagraphStyle(name="HeadingStyle", parent=styles['Heading2'], spaceAfter=10, textColor=HexColor("#1e293b"))
    bold_label = ParagraphStyle(name="BoldLabel", parent=styles['BodyText'], fontName="Helvetica-Bold", spaceBefore=6, textColor=HexColor("#0f172a"))
    plain_english_style = ParagraphStyle(name="PlainEnglish", parent=styles['BodyText'], fontName="Helvetica-BoldOblique", spaceAfter=10, textColor=HexColor("#b91c1c"))
    standard_body = ParagraphStyle(name="StandardBody", parent=styles['BodyText'], spaceAfter=10)
    evidence_body = ParagraphStyle(name="EvidenceBody", parent=styles['BodyText'], spaceAfter=10, fontName="Courier", textColor=HexColor("#334155"))
    
    flowables = []
    flowables.append(Paragraph("STALWART DYNAMIC CIVIC DOSSIER", title_style))
    flowables.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Sources: {', '.join(source_files)}", styles['Normal']))
    flowables.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#000000"), spaceBefore=15, spaceAfter=20))
    
    # 1. Ground Truth Section
    if audit_results.get("ground_truth_facts"):
        flowables.append(Paragraph("🔍 EXTRACTED GROUND TRUTH (Key Data & Metrics)", heading_style))
        for fact in audit_results["ground_truth_facts"]:
            flowables.append(Paragraph(f"• {fact}", standard_body))
        flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=15))

    # 2. Responsible Authorities & Contacts
    if audit_results.get("responsible_authorities"):
        flowables.append(Paragraph("🏛️ PUBLIC OFFICIALS & ESCALATION DIRECTORY", heading_style))
        for auth in audit_results["responsible_authorities"]:
            flowables.append(Paragraph(f"<b>{auth.get('agency_or_body', 'Authority')}</b>", bold_label))
            for off in auth.get("officials", []):
                flowables.append(Paragraph(f"• <b>{off.get('name')}</b> ({off.get('role')}): {off.get('public_contact')}", standard_body))
            if auth.get("escalation_procedure"):
                flowables.append(Paragraph(f"<i>Filing/Escalation Process:</i> {auth.get('escalation_procedure')}", standard_body))
        flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=15))

    # 3. Statutory Alerts
    if audit_results.get("statutory_alerts"):
        flowables.append(Paragraph("🚨 FORENSIC STATUTORY ALERTS", heading_style))
        for idx, alert in enumerate(audit_results["statutory_alerts"]):
            flowables.append(Paragraph(f"Alert #{idx+1}: {alert.get('citation_type')}", heading_style))
            flowables.append(Paragraph("🗣️ Plain English Impact:", bold_label))
            flowables.append(Paragraph(alert.get("plain_english", ""), plain_english_style))
            flowables.append(Paragraph("📜 Verbatim Text:", bold_label))
            flowables.append(Paragraph(f"\"{alert.get('verbatim_text', '')}\"", evidence_body))
            flowables.append(Paragraph("💰 Financial/Regulatory Pipeline:", bold_label))
            flowables.append(Paragraph(alert.get("financial_pipeline", ""), standard_body))
            flowables.append(Paragraph("🛠️ Tailored Civic Action Plan:", bold_label))
            flowables.append(Paragraph(alert.get("tailored_action_plan", ""), standard_body))
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
                combined_text += f"\n--- SOURCE: {f.name} ---\n" + extract_text_from_file(f)
            
            audit_data, error = analyze_document_with_ai(combined_text, ", ".join(filenames))
            
            if error:
                st.error(f"Analysis Error: {error}")
            else:
                st.session_state.current_audit = audit_data
                st.session_state.source_filenames = filenames

if "current_audit" in st.session_state and st.session_state.current_audit:
    data = st.session_state.current_audit
    
    st.success("🚨 AUDIT COMPLETE: Contextual intelligence and customized escalation plan generated.")
    
    if SimpleDocTemplate is not None:
        pdf_bytes = generate_dossier_pdf(data, st.session_state.source_filenames)
        st.download_button(
            label="📄 DOWNLOAD DYNAMIC CIVIC DOSSIER (PDF)",
            data=pdf_bytes,
            file_name=f"STALWART_Dossier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            type="primary"
        )
    
    st.divider()

    # UI Rendering
    if data.get("ground_truth_facts"):
        st.subheader("🔍 EXTRACTED GROUND TRUTH")
        for fact in data["ground_truth_facts"]:
            st.markdown(f"- {fact}")

    if data.get("responsible_authorities"):
        st.subheader("🏛️ PUBLIC OFFICIALS & ESCALATION DIRECTORY")
        for auth in data["responsible_authorities"]:
            with st.expander(f"**{auth.get('agency_or_body')}**", expanded=True):
                for off in auth.get("officials", []):
                    st.write(f"- **{off.get('name')}** ({off.get('role')}): `{off.get('public_contact')}`")
                if auth.get("escalation_procedure"):
                    st.info(f"**Escalation Process:** {auth.get('escalation_procedure')}")

    if data.get("statutory_alerts"):
        st.subheader("🚨 FORENSIC STATUTORY ALERTS")
        for idx, alert in enumerate(data["statutory_alerts"]):
            with st.container(border=True):
                st.markdown(f"### Alert #{idx+1} — {alert.get('citation_type')}")
                st.error(f"**Plain English:** {alert.get('plain_english')}")
                st.markdown(f"**Verbatim Text:**\n> \"{alert.get('verbatim_text')}\"")
                st.markdown(f"**Financial Pipeline:** {alert.get('financial_pipeline')}")
                st.markdown(f"**Tailored Civic Action Plan:**\n{alert.get('tailored_action_plan')}")
