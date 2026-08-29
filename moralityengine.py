import os
import io
import re
import json
import urllib.request
import urllib.error
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


st.set_page_config(
    page_title="STALWART Hybrid Civic Auditor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 8px;
        padding-bottom: 8px;
        padding-left: 16px;
        padding-right: 16px;
        border-radius: 4px 4px 0px 0px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ STALWART HYBRID FORENSIC AUDITOR v15.1")
st.markdown("*(Dual-Engine Architecture: Deterministic Regex Harvester + Local Offline GPU Reasoning)*")


# Sidebar Settings with Explicit Toggle
with st.sidebar:
    st.header("⚙️ Local Engine Status")
    use_ollama = st.checkbox("Enable Local AI Synthesis (Ollama)", value=True)
    ollama_model = st.selectbox("Local Offline Model", ["llama3.1", "mistral", "qwen2.5:7b"], index=0)
    st.info("💡 **Hybrid Mode:** If enabled, the engine harvests exact citations via regex, then feeds them to your local GPU for deep causal reasoning. If disabled, it runs purely on local regex.")


def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        if PdfReader is None:
            return "Error: pypdf is not installed."
        reader = PdfReader(uploaded_file)
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n[Page {idx+1}]\n" + page_text.replace('\n', ' ') + '\n'
    else:
        text = uploaded_file.read().decode('utf-8', errors='ignore')
    return text


def clean_snippet(text, match_start, match_end, window=180):
    start = max(0, match_start - window)
    end = min(len(text), match_end + window)
    raw = text[start:end].replace('\n', ' ').strip()
    return f"...{raw}..."


def harvest_deterministic_data(document_text, filename):
    """Stage 1: Extracts exact, unalterable facts, citations, and sentences."""
    dollars = list(set(re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|trillion))?', document_text, re.IGNORECASE)))
    usc_cites = list(set(re.findall(r'\b\d+\s+U\.S\.C\.\s+§?\s*[\d\w\-]+', document_text, re.IGNORECASE)))
    rcw_cites = list(set(re.findall(r'\bRCW\s+[\d\.]+', document_text, re.IGNORECASE)))
    sec_cites = list(set(re.findall(r'\bSection\s+\d{3,5}[a-zA-Z0-9\-]*', document_text, re.IGNORECASE)))
    citations = usc_cites + rcw_cites + sec_cites
    dates = list(set(re.findall(r'(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}|\b\d{1,2}/\d{1,2}/\d{2,4}\b)', document_text)))

    sentences = re.split(r'(?<=[.!?])\s+', document_text.replace('\n', ' '))

    harm_patterns = r'\b(penalty|fine|fined|imprisonment|violation|prohibited|low-income|poverty|impoverished|underserved|disadvantaged|rural|tenant|resident|voter|worker)\b'
    benefit_patterns = r'\b(tax credit|exemption|deduction|subsidy|direct pay|contractor|vendor|procurement|grantee|exclusive|sole source|qualified manufacturer)\b'

    harvested_harms = [s.strip() for s in sentences if re.search(harm_patterns, s, re.IGNORECASE) and len(s.strip()) > 35][:6]
    harvested_benefits = [s.strip() for s in sentences if re.search(benefit_patterns, s, re.IGNORECASE) and len(s.strip()) > 35][:6]

    override_patterns = [
        ("PREEMPTIVE STATUTORY OVERRIDE", r'(?:notwithstanding any other provision|shall supersede|without regard to)'),
        ("JUDICIAL IMMUNITY / PRECLUSION", r'(?:shall not be subject to judicial review|final and non-reviewable|immune from liability)'),
        ("DISCRETIONARY SLUSH FUNDING", r'(?:shall be available for|appropriated to the Secretary|retained until expended|at the sole discretion)')
    ]
    loopholes = []
    for cat, pattern in override_patterns:
        for m in re.finditer(pattern, document_text, re.IGNORECASE):
            loopholes.append({
                "loophole_type": cat,
                "verbatim_text": clean_snippet(document_text, m.start(), m.end()),
                "mechanism_how_it_works": "Bypasses standard public disclosure, administrative review, or judicial oversight.",
                "why_drafted": "Protects agency actions and private contractors from legal accountability."
            })
            if len(loopholes) >= 6:
                break

    agencies = list(set(re.findall(r'(?:Department of [A-Z][a-z]+|Bureau of [A-Z][a-z]+|Environmental Protection Agency|Internal Revenue Service|Federal [A-Z][a-z]+ Commission)', document_text)))

    return {
        "ground_facts": [
            f"Target Document: {filename}",
            f"Character Count: {len(document_text):,}",
            f"Financial Figures Detected: {', '.join(dollars[:8]) if dollars else 'None explicitly declared'}",
            f"Statutes & Sections Cited: {', '.join(citations[:8]) if citations else 'None explicitly cited'}",
            f"Key Operational Deadlines: {', '.join(dates[:6]) if dates else 'Standard enactment timelines'}"
        ],
        "citations": citations,
        "harvested_harms": harvested_harms,
        "harvested_benefits": harvested_benefits,
        "loopholes": loopholes,
        "agencies": agencies
    }


def query_local_ollama(prompt, model_name="llama3.1"):
    """Queries local Ollama instance with enhanced JSON cleaning and a 120s timeout."""
    url = "http://localhost:11434/api/generate"
    payload = json.dumps({
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            raw_response = res_data.get("response", "{}")
            # Strip markdown formatting if the model hallucinates backticks
            clean_json = raw_response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
    except Exception as e:
        print(f"Ollama Connection/Parse Error: {e}")
        return None


def execute_hybrid_audit(document_text, filename, model_name, run_ollama):
    """Combines Stage 1 Harvest with explicit toggle for Stage 2 Local GPU Reasoning."""
    stage1 = harvest_deterministic_data(document_text, filename)

    local_ai_results = None
    if run_ollama:
        ollama_prompt = f"""[INST] <<SYS>>
You are the STALWART Forensic Legislative Auditor. Your job is to extract raw, unvarnished causal truth from statutory text.
NEVER repeat placeholder words like "Specific demographic" or "Detailed causal explanation". 
Analyze the provided text and write real, factual sentences detailing who loses rights or money, and which corporations profit.
<</SYS>>

Document Filename: {filename}
Key Citations Found: {stage1['citations']}
Harvested Text Samples:
{document_text[:3500]}

Generate a valid JSON response with this exact structure, filled with YOUR original analysis:
{{
    "human_cost_who_hurts": [
        {{
            "impacted_group": "Name the specific group of people affected (e.g. low-income renters, registered voters, small repair shops)",
            "nature_of_harm": "What practical right, money, or access is being taken away",
            "why_it_harms": "Explain the step-by-step mechanism of how this statutory wording causes the injury",
            "severity": "CRITICAL"
        }}
    ],
    "corporate_beneficiaries": [
        {{
            "entity_or_industry": "Name the specific industry or corporate body getting the advantage",
            "benefit_received": "The specific tax credit, liability shield, or sole-source contract granted",
            "why_rewarded": "Why the legislative wording was drafted to favor them",
            "pipeline_details": "The financial or regulatory channel delivering the benefit"
        }}
    ]
}}
[/INST]"""
        local_ai_results = query_local_ollama(ollama_prompt, model_name)

    # 1. Build Statutes Broken Tab
    statutes_broken = []
    if stage1['citations']:
        for cite in stage1['citations'][:8]:
            statutes_broken.append({
                "statute_citation": cite,
                "manipulation_type": "STATUTORY CODE CITATION",
                "law_name": "Codified Legal Framework",
                "details": f"The bill modifies, supersedes, or directs regulatory enforcement under {cite}."
            })
    else:
        statutes_broken.append({
            "statute_citation": "Administrative Procedure Act (5 U.S.C. § 706)",
            "manipulation_type": "RULEMAKING DELEGATION",
            "law_name": "Administrative Code",
            "details": "Establishes administrative execution standards without explicit judicial bounds."
        })

    # 2. Build Human Cost Tab 
    if local_ai_results and local_ai_results.get("human_cost_who_hurts"):
        human_cost = local_ai_results.get("human_cost_who_hurts")
    elif stage1['harvested_harms']:
        human_cost = [{
            "impacted_group": "Public / Impacted Demographic",
            "nature_of_harm": "Direct Statutory Mandate Extracted from Text",
            "why_it_harms": f"Verbatim Statutory Language: \"{s}\"",
            "severity": "CRITICAL"
        } for s in stage1['harvested_harms']]
    else:
        human_cost = [{
            "impacted_group": "General Citizens & Taxpayers",
            "nature_of_harm": "Standard Administrative Regulation",
            "why_it_harms": "No explicit penalty or targeting clauses extracted from text sample.",
            "severity": "MODERATE"
        }]

    # 3. Build Corporate Beneficiaries Tab 
    if local_ai_results and local_ai_results.get("corporate_beneficiaries"):
        corp_beneficiaries = local_ai_results.get("corporate_beneficiaries")
    elif stage1['harvested_benefits']:
        corp_beneficiaries = [{
            "entity_or_industry": "Commercial Grantees / Industry Recipients",
            "benefit_received": "Statutory Advantage / Financial Pathway",
            "why_rewarded": "Identified in specific legislative authorization clause.",
            "pipeline_details": f"\"{s}\""
        } for s in stage1['harvested_benefits']]
    else:
        corp_beneficiaries = [{
            "entity_or_industry": "Administering Agencies & Incumbent Vendors",
            "benefit_received": "Standard Procurement & Program Execution",
            "why_rewarded": "Direct legislative appropriation.",
            "pipeline_details": "Standard budgetary channels."
        }]

    # 4. Build Responsible Parties Tab
    responsible_parties = []
    if stage1['agencies']:
        for agency in stage1['agencies'][:4]:
            responsible_parties.append({
                "agency_or_actor": agency,
                "role_in_scheme": "Enforcing & Administering Body",
                "contact_portal": "Official Public Docket / FOIA Liaison",
                "escalation_procedure": f"Submit administrative petition or records demand to {agency} pursuant to 5 U.S.C. § 552.",
                "legal_paperwork_playbook": f"1. File FOIA Demand for agency communications.\n2. Submit Formal Comment under 5 U.S.C. § 553.\n3. Prepare APA § 706 Injunctive Complaint."
            })
    else:
        responsible_parties.append({
            "agency_or_actor": "Regulatory Governing Agency",
            "role_in_scheme": "Administrative Body",
            "contact_portal": "Agency Clerk",
            "escalation_procedure": "Petition administrative head during public comment period.",
            "legal_paperwork_playbook": "1. Public Records Act Demand.\n2. Motion for Administrative Stay."
        })

    return {
        "ground_truth_facts": stage1['ground_facts'],
        "statutes_broken": statutes_broken,
        "human_cost_who_hurts": human_cost,
        "corporate_beneficiaries": corp_beneficiaries,
        "loopholes_exploited": stage1['loopholes'] if stage1['loopholes'] else [{
            "loophole_type": "STANDARD STATUTORY BOILERPLATE",
            "verbatim_text": "No explicit preemptive override keywords found in text sample.",
            "mechanism_how_it_works": "Operates under standard administrative rulemaking frameworks.",
            "why_drafted": "Standard baseline legislation."
        }],
        "responsible_parties_and_action": responsible_parties,
        "used_ollama": local_ai_results is not None
    }


def generate_dossier_pdf(data, source_files):
    if SimpleDocTemplate is None:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name="TitleStyle", parent=styles['Heading1'], alignment=1, spaceAfter=15, textColor=HexColor("#0f172a"))
    section_style = ParagraphStyle(name="SectionStyle", parent=styles['Heading2'], spaceBefore=12, spaceAfter=8, textColor=HexColor("#1e293b"))
    sub_title = ParagraphStyle(name="SubTitle", parent=styles['Normal'], fontName="Helvetica-Bold", spaceBefore=6, textColor=HexColor("#0284c7"))
    body_text = ParagraphStyle(name="Body", parent=styles['BodyText'], spaceAfter=6, fontSize=9, leading=12)
    verbatim_text = ParagraphStyle(name="Verbatim", parent=styles['BodyText'], spaceAfter=6, fontSize=8, leading=11, fontName="Courier", textColor=HexColor("#334155"))
    alert_text = ParagraphStyle(name="AlertText", parent=styles['BodyText'], fontName="Helvetica-BoldOblique", spaceAfter=6, fontSize=9, leading=12, textColor=HexColor("#b91c1c"))

    flowables = []
    flowables.append(Paragraph("STALWART HYBRID FORENSIC DOSSIER", title_style))
    flowables.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target: {', '.join(source_files)}", styles['Normal']))
    flowables.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#0f172a"), spaceBefore=10, spaceAfter=15))

    if data.get("ground_truth_facts"):
        flowables.append(Paragraph("🎯 EXTRACTED GROUND TRUTH & METRICS", section_style))
        for fact in data.get("ground_truth_facts", []):
            flowables.append(Paragraph(f"• {fact}", body_text))
        flowables.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=12))

    if data.get("statutes_broken"):
        flowables.append(Paragraph("⚖️ STATUTES & CODES REFERENCED / BROKEN", section_style))
        for s in data.get("statutes_broken", []):
            flowables.append(Paragraph(f"{s.get('statute_citation')} — {s.get('law_name')} [{s.get('manipulation_type')}]", sub_title))
            flowables.append(Paragraph(f"{s.get('details')}", body_text))
        flowables.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=12))

    if data.get("loopholes_exploited"):
        flowables.append(Paragraph("🕳️ FORENSIC LOOPHOLES & HIDDEN PREEMPTIONS", section_style))
        for lp in data.get("loopholes_exploited", []):
            flowables.append(Paragraph(f"Loophole: {lp.get('loophole_type')}", sub_title))
            flowables.append(Paragraph(f"Verbatim Text: \"{lp.get('verbatim_text')}\"", verbatim_text))
            flowables.append(Paragraph(f"Mechanic: {lp.get('mechanism_how_it_works')}", body_text))
            flowables.append(Paragraph(f"Intent: {lp.get('why_drafted')}", alert_text))
        flowables.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=12))

    if data.get("human_cost_who_hurts"):
        flowables.append(Paragraph("🛑 HUMAN COST & CITIZEN HARM ANALYSIS", section_style))
        for hc in data.get("human_cost_who_hurts", []):
            flowables.append(Paragraph(f"Impacted Group: {hc.get('impacted_group')} [SEVERITY: {hc.get('severity')}]", sub_title))
            flowables.append(Paragraph(f"Nature of Harm: {hc.get('nature_of_harm')}", alert_text))
            flowables.append(Paragraph(f"Why it Harms: {hc.get('why_it_harms')}", body_text))
        flowables.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=12))

    if data.get("corporate_beneficiaries"):
        flowables.append(Paragraph("🏢 CORPORATE BENEFICIARIES & PAYOFF PIPELINES", section_style))
        for cb in data.get("corporate_beneficiaries", []):
            flowables.append(Paragraph(f"Beneficiary: {cb.get('entity_or_industry')}", sub_title))
            flowables.append(Paragraph(f"Benefit: {cb.get('benefit_received')}", body_text))
            flowables.append(Paragraph(f"Why Rewarded: {cb.get('why_rewarded')}", body_text))
            flowables.append(Paragraph(f"Pipeline: {cb.get('pipeline_details')}", verbatim_text))
        flowables.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=12))

    if data.get("responsible_parties_and_action"):
        flowables.append(Paragraph("🏛️ RESPONSIBLE ACTORS & LEGAL PLAYBOOK", section_style))
        for rp in data.get("responsible_parties_and_action", []):
            flowables.append(Paragraph(f"Target Body: {rp.get('agency_or_actor')} ({rp.get('role_in_scheme')})", sub_title))
            flowables.append(Paragraph(f"Contact: {rp.get('contact_portal')}", body_text))
            flowables.append(Paragraph(f"Escalation: {rp.get('escalation_procedure')}", body_text))
            flowables.append(Paragraph(f"Legal Paperwork to File:\n{rp.get('legal_paperwork_playbook')}", verbatim_text))

    doc.build(flowables)
    return buffer.getvalue()


# Streamlit File Upload & Analysis Execution
uploaded_files = st.file_uploader("UPLOAD LEGISLATIVE BILLS, BUDGETS, OR STATUTORY ORDERS (PDF/TXT)", type=["txt", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("EXECUTE HYBRID FORENSIC AUDIT"):
        combined_text = ""
        filenames = [f.name for f in uploaded_files]

        with st.spinner("Executing Stage 1 Regex Harvest & Stage 2 Offline GPU Reasoning..."):
            for f in uploaded_files:
                combined_text += f"\n--- Source: {f.name} ---\n" + extract_text_from_file(f)

            audit_data = execute_hybrid_audit(combined_text, ", ".join(filenames), ollama_model, use_ollama)
            st.session_state.current_audit = audit_data
            st.session_state.source_filenames = filenames

# Render Output Interface
if 'current_audit' in st.session_state and st.session_state.current_audit:
    data = st.session_state.current_audit

    if data.get("used_ollama"):
        st.success("✔️ HYBRID AUDIT COMPLETE: Ground facts verified by regex & synthesized via local offline Ollama.")
    else:
        st.info("ℹ️ LOCAL AUDIT COMPLETE: Deterministic sentence harvester active (Ollama disabled or failed; exact statutory sentences extracted).")

    # PDF Download Button
    if SimpleDocTemplate is not None:
        try:
            pdf_bytes = generate_dossier_pdf(data, st.session_state.source_filenames)
            if pdf_bytes:
                st.download_button(
                    label="📥 DOWNLOAD FULL FORENSIC CIVIC DOSSIER (PDF)",
                    data=pdf_bytes,
                    file_name=f"STALWART_Forensic_Dossier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as pdf_err:
            st.error(f"⚠️ Error compiling PDF dossier: {pdf_err}")

    st.divider()

    tab_summary, tab_statutes, tab_loopholes, tab_harm, tab_corps, tab_action = st.tabs([
        "🎯 Ground Truth",
        "⚖️ Statutes Broken",
        "🕳️ Loopholes & Hidden Text",
        "🛑 Human Cost & Harms",
        "🏢 Corporate Beneficiaries",
        "🏛️ Responsible Actors & Legal Playbook"
    ])

    with tab_summary:
        st.subheader("🎯 Extracted Ground Truth & Metrics")
        for fact in data.get("ground_truth_facts", []):
            st.markdown(f"• {fact}")

    with tab_statutes:
        st.subheader("⚖️ Statutes & Codes Modified / Broken")
        for s in data.get("statutes_broken", []):
            with st.container():
                st.markdown(f"### {s.get('statute_citation')} — {s.get('law_name')}")
                st.warning(f"**Manipulation Category:** {s.get('manipulation_type')}")
                st.markdown(f"**Forensic Details:**\n{s.get('details')}")
                st.divider()

    with tab_loopholes:
        st.subheader("🕳️ Loopholes Exploited & Statutory Overrides")
        for lp in data.get("loopholes_exploited", []):
            with st.container():
                st.markdown(f"### ⚠️ {lp.get('loophole_type')}")
                st.error(f"**Verbatim Text:** \n> *\"{lp.get('verbatim_text')}\"*")
                st.markdown(f"**How it Works:** {lp.get('mechanism_how_it_works')}")
                st.info(f"**Legislative Intent:** {lp.get('why_drafted')}")
                st.divider()

    with tab_harm:
        st.subheader("🛑 Human Cost: Who it Hurts & Specific Harms")
        for hc in data.get("human_cost_who_hurts", []):
            with st.container():
                severity_color = "🔴" if hc.get("severity") == "CRITICAL" else "🟠"
                st.markdown(f"### {severity_color} Impacted Target: **{hc.get('impacted_group')}**")
                st.error(f"**Nature of Harm:** {hc.get('nature_of_harm')}")
                st.markdown(f"**Why it Harms:** {hc.get('why_it_harms')}")
                st.divider()

    with tab_corps:
        st.subheader("🏢 Corporate Beneficiaries & Payoff Pipelines")
        for cb in data.get("corporate_beneficiaries", []):
            with st.container():
                st.markdown(f"### 💰 Beneficiary: **{cb.get('entity_or_industry')}**")
                st.success(f"**Advantage Received:** {cb.get('benefit_received')}")
                st.markdown(f"**Why Rewarded:** {cb.get('why_rewarded')}")
                st.markdown(f"**Pipeline Details:** \n`{cb.get('pipeline_details')}`")
                st.divider()

    with tab_action:
        st.subheader("🏛️ Responsible Actors & Citizen Legal Playbook")
        for rp in data.get("responsible_parties_and_action", []):
            with st.expander(f"**Target Body: {rp.get('agency_or_actor')}**", expanded=True):
                st.markdown(f"**Role in Scheme:** {rp.get('role_in_scheme')}")
                st.markdown(f"**Contact Portal:** {rp.get('contact_portal')}")
                st.info(f"**Escalation Process:** {rp.get('escalation_procedure')}")
                st.markdown(f"**Legal Paperwork to File:**")
                st.code(rp.get("legal_paperwork_playbook", ""), language="markdown")
