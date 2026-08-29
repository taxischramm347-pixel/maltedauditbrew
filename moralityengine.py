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
    ai_toggle = st.checkbox("Enable Gemini AI Analysis", value=True, help="Uncheck to run offline zero-cost baseline checks.")
    
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


def analyze_document_locally(filename):
    """Zero-cost offline baseline scan mimicking the expected JSON schema."""
    return {
        "ground_truth_facts": [
            f"File analyzed locally (AI Disabled): {filename}",
            "Standard compliance check initiated.",
            "No API credits consumed during this audit."
        ],
        "responsible_authorities": [
            {
                "agency_or_body": "Pending AI Activation",
                "officials": [
                    {
                        "name": "Local Audit Mode Active",
                        "role": "System Baseline",
                        "public_contact": "N/A"
                    }
                ],
                "escalation_procedure": "Re-run with AI toggle enabled for dynamic contact extraction."
            }
        ],
        "statutory_alerts": [
            {
                "citation_type": "OFFLINE_MODE_ACTIVE",
                "verbatim_text": "N/A",
                "plain_english": "The audit was run using the zero-cost offline toggle. Deep semantic checks and dynamic playbooks were bypassed.",
                "financial_pipeline": "Zero API credits consumed.",
                "tailored_action_plan": "Review document manually or check the 'Enable Gemini AI Analysis' box in the sidebar."
            }
        ]
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
                audit_data = analyze_document_locally(", ".join(filenames))

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
