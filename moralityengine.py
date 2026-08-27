import os
import io
import re
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
    page_title="STALWART: Civic Enforcement Auditor v10.0",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚖️ STALWART CIVIC ENFORCEMENT AUDITOR V10.0")
st.caption("Omni-Jurisdiction Auditing, Ground Truth Extraction & Plain English Translations")

# 1. The V10.0 Omni-Jurisdiction Matrix (Now with Plain English)
OVERREACH_DATABASE = {
    "FEDERAL_STATE_STATUTORY_OVERRIDE": {
        "jurisdiction": "FEDERAL & STATE",
        "citation": "STATUTORY OVERRIDE",
        "plain_english": "The government is giving this entity a VIP pass to legally ignore the normal safety, zoning, and permit laws that every other citizen and small business has to follow.",
        "description": "Blanket Law Bypass (Nullifies existing transparency, safety, or criminal laws)",
        "keywords": ["notwithstanding any other provision of law", "not subject to the requirements of", "exempt from", "shall not apply", "waive the requirements", "waiver of compliance", "no local, state, or federal permit shall be required"],
        "loophole": "Inserts exception phrasing to legally vaporize baseline procedural, safety, and financial statutes that would otherwise regulate, tax, or halt the action.",
        "money": "Facilitates unreviewed capital deployment. Routes tax dollars or real estate directly to favored agencies while avoiding competitive oversight.",
        "civilian": "Removes public notice requirements, citizen review windows, and local community appeal rights.",
        "rcw_link": "RCW 9A.80.010 (Official Misconduct) & RCW 42.52 (Ethics in Public Service)",
        "scotus_link": "West Virginia v. EPA (2022) — Major Questions Doctrine",
        "action_plan": "• DEMAND EMERGENCY TAKEOVER: Petition local council to invoke a federal 'Work Takeover' (e.g., CERCLA § 104) if a private entity abandons the site.\n• PUBLIC RECORD ENFORCEMENT: File immediate FOIA/Public Records Requests for all internal agency communications justifying the 'waiver'.\n• CITIZEN SUIT: Initiate a federal Citizen Suit (e.g., 42 U.S.C. § 9659) against the agency for failing to enforce non-discretionary safety duties."
    },
    "DUE_PROCESS_JUDICIAL_BYPASS": {
        "jurisdiction": "ALL LEVELS",
        "citation": "DUE PROCESS BYPASS",
        "plain_english": "They wrote a rule saying nobody is allowed to sue them or take this to court, legally stripping away your Constitutional right to defend your property before a judge.",
        "description": "Totalitarian Authority (Strips citizens of right to sue or appeal)",
        "keywords": ["sole discretion", "unreviewable", "not subject to judicial review", "without judicial review", "deemed approved", "final and unappealable", "no liability", "shall not be liable", "shall give rise to any right to judicial review"],
        "loophole": "Labels administrative actions 'unreviewable' to strip courts of jurisdiction, shielding politicians and corporations from judicial accountability.",
        "money": "Protects infrastructure outlays, land condemnation, and corporate acquisitions from being halted by citizen lawsuits or injunctions.",
        "civilian": "Deprives citizens of 5th and 14th Amendment due process rights. Citizens cannot sue the government for seizing land or poisoning water supplies.",
        "rcw_link": "RCW 42.20.100 (Failure of Duty by Public Officer)",
        "scotus_link": "Loper Bright Enterprises v. Raimondo (2024) — Independent Judicial Review",
        "action_plan": "• FILE AN INJUNCTION: Bypass the administrative block by filing a direct constitutional challenge in State Superior Court citing Loper Bright.\n• ESTABLISH PUBLIC NUISANCE: File an emergency municipal declaration of Public Nuisance (e.g., RCW 7.48) to circumvent 'unreviewable' permit status, as immediate public safety overrides administrative immunity.\n• ESCALATE TO MEDIA: Distribute this STALWART dossier to local investigative journalists, highlighting the exact clause stripping the public's right to sue."
    },
    "UNCONSTITUTIONAL_AGENCY_DELEGATION": {
        "jurisdiction": "STATE & FEDERAL EXECUTIVE",
        "citation": "BLANK-CHECK DELEGATION",
        "plain_english": "Unelected bureaucrats are being given a blank check to make up the rules as they go, without getting voters or lawmakers to approve it.",
        "description": "Unelected Rule-Making (Vague powers granted to agency heads or boards)",
        "keywords": ["as the secretary determines appropriate", "such regulations as may be necessary", "at the discretion of the director", "broad discretion", "leaves the agency with flexibility", "as the department deems necessary"],
        "loophole": "Uses broad statutory language that allows unelected agency administrators to formulate binding policy, taxes, and legal definitions without a democratic vote.",
        "money": "Enables agency heads to allocate discretionary budgets or establish restrictive zoning boundaries that exclusively benefit massive corporate lobbies.",
        "civilian": "Subjects individuals and small businesses to arbitrary rules, taxes, and fines created without legislative accountability.",
        "rcw_link": "RCW 42.52 (Ethics in Public Service - Conflict of Interest)",
        "scotus_link": "Loper Bright v. Raimondo (2024) — Chevron Deference Overruled",
        "action_plan": "• ETHICS COMPLAINT: File a formal complaint with the State Executive Ethics Board (RCW 42.52) if the agency head stands to benefit financially from their 'discretion'.\n• LEGISLATIVE RECALL: Demand the state legislature or city council repeal the specific delegated authority block.\n• CITIZEN INITIATIVE: Draft a local citizen initiative to explicitly tie the agency's rules to voter-approved metrics."
    }
}

# 2. Public Contact Routing Directory
CIVIC_CONTACT_DIRECTORY = {
    "EPA Region 10 (Federal Oversight)": {
        "keywords": ["epa", "cercla", "environmental protection agency", "region 10", "cosmopolis", "aberdeen"],
        "contacts": [
            "Brad Martin (EPA On-Scene Coordinator) | (206) 553-1200 | epa-seattle@epa.gov",
            "Christina Vieira da Rosa (Assistant Regional Counsel) | (206) 553-2601 | VieiraDaRosa.Christina@epa.gov",
            "National Response Center (Emergency Spills) | (800) 424-8802"
        ]
    },
    "City of Aberdeen, WA (Municipal Authority)": {
        "keywords": ["aberdeen", "grays harbor"],
        "contacts": [
            "Mayor Douglas Orr | (360) 537-3227 (Office) / (360) 580-3776 (Cell) | dorr@aberdeenwa.gov",
            "Aberdeen City Council | (360) 533-4100"
        ]
    }
}

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

def parse_contacts_from_text(text_corpus):
    found_contacts = {}
    text_lower = text_corpus.lower()
    for agency, data in CIVIC_CONTACT_DIRECTORY.items():
        if any(kw in text_lower for kw in data["keywords"]):
            found_contacts[agency] = data["contacts"]
    return found_contacts

def extract_document_intelligence(text_corpus):
    """Scans the text for real-world factual metrics: gallons, dollars, hazardous chemicals, and operational status."""
    intelligence_facts = []
    # Split text into rough sentences
    sentences = re.split(r'(?<=[.!?]) +', text_corpus.replace('\n', ' '))
    keywords = ["gallon", "hazardous", "acid", "corrosive", "penalty", "million", "abandoned", "no revenue", "leak"]
    seen = set()
    
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(kw in s_lower for kw in keywords) and any(char.isdigit() for char in s_lower):
            clean_s = sentence.strip()
            # Keep reasonable length sentences to avoid pulling whole paragraphs
            if 30 < len(clean_s) < 400 and clean_s not in seen:
                seen.add(clean_s)
                intelligence_facts.append(clean_s)
                if len(intelligence_facts) >= 8: # Limit to top 8 most critical facts
                    break
    return intelligence_facts

def parse_forensic_violations(text_corpus, source_filename):
    records = []
    lines = text_corpus.split('\n')
    seen_snippets = set()
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for category, data in OVERREACH_DATABASE.items():
            if any(kw.lower() in line_lower for kw in data["keywords"]):
                context_window = [lines[j].strip() for j in range(max(0, i-2), min(len(lines), i+5)) if lines[j].strip()]
                context_str = " ".join(context_window)
                snippet_key = context_str[:60]
                
                if snippet_key not in seen_snippets and len(context_str) > 25:
                    seen_snippets.add(snippet_key)
                    records.append({
                        "id": f"ALERT#{abs(hash(snippet_key)) % 10000}",
                        "source_file": source_filename,
                        "jurisdiction": data["jurisdiction"],
                        "citation": data["citation"],
                        "plain_english": data["plain_english"],
                        "description": data["description"],
                        "evidence": context_str,
                        "loophole": data["loophole"],
                        "money": data["money"],
                        "civilian": data["civilian"],
                        "rcw_link": data["rcw_link"],
                        "scotus_link": data["scotus_link"],
                        "action_plan": data["action_plan"]
                    })
    return records

def generate_dossier_pdf(dossier_data, contact_data, intelligence_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(name="TitleStyle", parent=styles['Heading1'], alignment=1, spaceAfter=20, textColor=HexColor("#8B0000"))
    heading_style = ParagraphStyle(name="HeadingStyle", parent=styles['Heading2'], spaceAfter=10, textColor=HexColor("#333333"))
    bold_label = ParagraphStyle(name="BoldLabel", parent=styles['BodyText'], fontName="Helvetica-Bold", spaceBefore=6, textColor=HexColor("#1f2937"))
    plain_english_style = ParagraphStyle(name="PlainEnglish", parent=styles['BodyText'], fontName="Helvetica-BoldOblique", spaceAfter=12, textColor=HexColor("#b91c1c"))
    standard_body = ParagraphStyle(name="StandardBody", parent=styles['BodyText'], spaceAfter=12)
    evidence_body = ParagraphStyle(name="EvidenceBody", parent=styles['BodyText'], spaceAfter=12, fontName="Courier", textColor=HexColor("#444444"))
    
    flowables = []
    flowables.append(Paragraph("STALWART CIVIC ENFORCEMENT DOSSIER", title_style))
    flowables.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#000000"), spaceBefore=15, spaceAfter=20))
    
    # ADDED: Document Intelligence (Ground Truth)
    if intelligence_data:
        flowables.append(Paragraph("🔍 DOCUMENT INTELLIGENCE (Extracted Ground Truth)", heading_style))
        for fact in intelligence_data:
            flowables.append(Paragraph(f"• {fact}", standard_body))
        flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#000000"), spaceBefore=15, spaceAfter=20))

    # ADDED: Public Contact Directory
    if contact_data:
        flowables.append(Paragraph("📞 PUBLIC ACCOUNTABILITY DIRECTORY", heading_style))
        for agency, contacts in contact_data.items():
            flowables.append(Paragraph(f"{agency}:", bold_label))
            for contact in contacts:
                flowables.append(Paragraph(f"• {contact}", standard_body))
        flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#000000"), spaceBefore=15, spaceAfter=20))
    
    for idx, item in enumerate(dossier_data):
        flowables.append(Paragraph(f"Incident #{idx+1} — {item['id']} ({item['source_file']})", heading_style))
        flowables.append(Paragraph(f"CITATION: {item['citation']} | {item['jurisdiction']}", bold_label))
        
        # ADDED: Plain English Translation
        flowables.append(Paragraph("🗣️ Plain English Breakdown:", bold_label))
        flowables.append(Paragraph(item['plain_english'], plain_english_style))
        
        flowables.append(Paragraph("Verbatim Statutory Evidence:", bold_label))
        flowables.append(Paragraph(f"\"{item['evidence']}\"", evidence_body))
        
        flowables.append(Paragraph("Loophole Exploitation Mechanics:", bold_label))
        flowables.append(Paragraph(item['loophole'], standard_body))
        
        flowables.append(Paragraph("Financial Pipeline (Follow the Money):", bold_label))
        flowables.append(Paragraph(item['money'], standard_body))
        
        flowables.append(Paragraph("Impact on Civilians & Property Rights:", bold_label))
        flowables.append(Paragraph(item['civilian'], standard_body))
        
        flowables.append(Paragraph("🛠️ CIVIC ACTION PLAN (How to Effect Change):", bold_label))
        flowables.append(Paragraph(item['action_plan'].replace('\n', '<br/>'), standard_body))
        
        flowables.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#CCCCCC"), spaceBefore=15, spaceAfter=20))
        
    doc.build(flowables)
    return buffer.getvalue()

if 'master_dossier' not in st.session_state:
    st.session_state.master_dossier = []
if 'contact_dossier' not in st.session_state:
    st.session_state.contact_dossier = {}
if 'intelligence_dossier' not in st.session_state:
    st.session_state.intelligence_dossier = []

uploaded_files = st.file_uploader("UPLOAD LEGISLATIVE BILLS OR GOV ORDERS (PDF/TXT)", type=["txt", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("EXECUTE BATCH CIVIC FORENSIC SCAN"):
        st.session_state.master_dossier = []
        st.session_state.contact_dossier = {}
        st.session_state.intelligence_dossier = []
        
        with st.spinner("Extracting Ground Truth facts and compiling Plain English loopholes..."):
            for file in uploaded_files:
                raw_text = extract_text_from_file(file)
                file_records = parse_forensic_violations(raw_text, file.name)
                st.session_state.master_dossier.extend(file_records)
                
                # Extract Document Intelligence
                doc_facts = extract_document_intelligence(raw_text)
                st.session_state.intelligence_dossier.extend(doc_facts)
                
                # Extract Contacts
                detected_contacts = parse_contacts_from_text(raw_text)
                for agency, contacts in detected_contacts.items():
                    if agency not in st.session_state.contact_dossier:
                        st.session_state.contact_dossier[agency] = contacts
            
            # Deduplicate facts
            st.session_state.intelligence_dossier = list(dict.fromkeys(st.session_state.intelligence_dossier))

if st.session_state.master_dossier:
    st.success("🚨 SCAN COMPLETE: Ground Truth extracted. Loopholes translated.")
    
    if SimpleDocTemplate is not None:
        pdf_bytes = generate_dossier_pdf(st.session_state.master_dossier, st.session_state.contact_dossier, st.session_state.intelligence_dossier)
        st.download_button(
            label="📄 DOWNLOAD PLAIN ENGLISH CIVIC DOSSIER (PDF)",
            data=pdf_bytes,
            file_name=f"STALWART_PlainEnglish_Dossier_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            type="primary"
        )
    
    # UI Display for Ground Truth Intelligence
    if st.session_state.intelligence_dossier:
        st.subheader("🔍 DOCUMENT INTELLIGENCE (Extracted Ground Truth Facts)")
        with st.container(border=True):
            for fact in st.session_state.intelligence_dossier:
                st.markdown(f"- {fact}")
                
    # UI Display for Contacts
    if st.session_state.contact_dossier:
        st.subheader("📞 PUBLIC ACCOUNTABILITY DIRECTORY")
        for agency, contacts in st.session_state.contact_dossier.items():
            with st.expander(f"**{agency}**", expanded=True):
                for contact in contacts:
                    st.write(f"- {contact}")
        
    st.divider()
    
    for idx, item in enumerate(st.session_state.master_dossier):
        with st.container(border=True):
            col_left, col_right = st.columns([3, 1])
            with col_left:
                st.markdown(f"### Incident #{idx+1} — {item['id']}")
                st.caption(f"**Source:** `{item['source_file']}` | **Target Level:** {item['jurisdiction']}")
            with col_right:
                st.error(item['citation'])
                
            st.markdown("#### 🗣️ Plain English Breakdown:")
            st.error(item['plain_english'])
            
            st.markdown("**📜 Verbatim Statutory Evidence:**")
            st.info(f"\"{item['evidence']}\"")
            
            st.markdown("**⚙️ Loophole Exploitation Mechanics:**")
            st.write(item['loophole'])
            
            st.markdown("**💰 Financial Pipeline (Follow the Money):**")
            st.write(item['money'])
            
            st.markdown("#### 🛠️ Civic Action Plan (How to Effect Change):")
            st.write(item['action_plan'])
