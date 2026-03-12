"""
Streamlit UI for the AI Research Grant Proposal Generator & Evaluator.
Minimalist academic design — white background, black text, League Spartan font.
"""
import streamlit as st
import io
from fpdf import FPDF
from crew.grant_crew import run_grant_crew
from config import GEMINI_API_KEY

# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Grant Proposal Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Custom CSS — strict white + black, League Spartan
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@300;400;500;600;700&display=swap');

    /* Global background */
    html, body, .stApp {
        background-color: #ffffff !important;
    }

    /* Header area */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    /* Apply font to text elements only, NOT to widget internals */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp p, .stApp label, .stApp li, .stApp td, .stApp th,
    .stMarkdown, .stMarkdown p, .stMarkdown li,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stTextInput input, .stTextArea textarea,
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        font-family: 'League Spartan', sans-serif !important;
        color: #000000 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f8f8f8 !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] small {
        color: #000000 !important;
        font-family: 'League Spartan', sans-serif !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 2px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #666666 !important;
        background-color: #ffffff !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
        border-bottom: 3px solid #000000 !important;
        font-weight: 600 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #f8f8f8 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
    }

    /* Buttons — white text on black background */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'League Spartan', sans-serif !important;
        font-weight: 600 !important;
        padding: 8px 24px !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        opacity: 0.85 !important;
        color: #ffffff !important;
    }
    .stButton > button p,
    .stDownloadButton > button p,
    .stButton > button span,
    .stDownloadButton > button span {
        color: #ffffff !important;
    }

    /* Text inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px !important;
        font-family: 'League Spartan', sans-serif !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] {
        color: #000000 !important;
    }
    .stSlider [role="slider"] {
        background-color: #000000 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        color: #000000 !important;
        font-weight: 600 !important;
        background-color: #f8f8f8 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
    }

    /* Tables */
    .stTable, .stDataFrame {
        border: 1px solid #e0e0e0 !important;
    }
    table {
        border-collapse: collapse !important;
    }
    th {
        background-color: #f0f0f0 !important;
        font-weight: 600 !important;
    }
    td, th {
        border: 1px solid #e0e0e0 !important;
        padding: 8px 12px !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: #000000 !important;
    }

    /* Divider */
    hr {
        border-color: #e0e0e0 !important;
    }

    /* Status messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        font-family: 'League Spartan', sans-serif !important;
    }

    /* Selectbox */
    [data-baseweb="select"] {
        font-family: 'League Spartan', sans-serif !important;
    }
    [data-baseweb="select"] * {
        color: #000000 !important;
        font-family: 'League Spartan', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📄 Grant Proposal Generator")
    st.markdown("---")

    research_topic = st.text_area(
        "Research Topic",
        placeholder="e.g., AI-powered early detection of crop diseases using drone imagery",
        height=100,
        key="research_topic_input",
    )

    max_iterations = st.slider(
        "Refinement Iterations",
        min_value=1,
        max_value=5,
        value=2,
        help="Number of evaluate → refine cycles",
    )

    show_agent_logs = st.checkbox(
        "Show Agent Logs",
        value=False,
        help="Display detailed reasoning logs from each CrewAI agent",
    )

    st.markdown("---")

    generate_btn = st.button(
        "Generate Proposal",
        use_container_width=True,
        type="primary",
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#999 !important;'>Powered by CrewAI + Google Gemini</small>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# Main Panel
# ─────────────────────────────────────────────────────────────

st.markdown("# AI Research Grant Proposal Generator")
st.markdown("*Transform a research idea into a complete, evaluated, and refined grant proposal.*")
st.markdown("---")

# Check API key
if not GEMINI_API_KEY:
    st.error(
        "⚠️ **GEMINI_API_KEY not found.** "
        "Create a `.env` file with `GEMINI_API_KEY=your_key` and restart."
    )
    st.stop()


# ─────────────────────────────────────────────────────────────
# Generation Logic
# ─────────────────────────────────────────────────────────────
if generate_btn:
    if not research_topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    progress_container = st.container()
    status_placeholder = progress_container.empty()
    progress_bar = progress_container.progress(0)

    log_messages = []

    def progress_callback(msg):
        log_messages.append(msg)
        status_placeholder.markdown(f"**Status:** {msg}")
        # Estimate progress
        progress = min(len(log_messages) / (max_iterations * 5) * 100, 95)
        progress_bar.progress(int(progress))

    with st.spinner("Running multi-agent pipeline..."):
        try:
            result = run_grant_crew(
                research_topic=research_topic.strip(),
                max_iterations=max_iterations,
                progress_callback=progress_callback,
                verbose=show_agent_logs,
            )
            progress_bar.progress(100)
            status_placeholder.markdown("**Status:** ✅ Pipeline complete!")
            st.session_state["result"] = result
            st.session_state["log_messages"] = log_messages
        except Exception as e:
            st.error(f"Pipeline error: {str(e)}")
            st.exception(e)
            st.stop()


# ─────────────────────────────────────────────────────────────
# Display Results
# ─────────────────────────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state["result"]
    iterations = result["iterations"]

    if not iterations:
        st.warning("No iterations completed.")
        st.stop()

    latest = iterations[-1]
    proposal = latest["proposal"]
    budget = latest["budget"]
    evaluation = latest["evaluation"]

    # Tab layout
    tab_labels = ["📝 Proposal", "💰 Budget & Timeline", "📊 Evaluation", "🔄 Iteration History"]
    has_logs = any(
        any(v for v in it.get("agent_logs", {}).values())
        for it in iterations
    )
    if has_logs:
        tab_labels.append("🤖 Agent Logs")

    tabs = st.tabs(tab_labels)
    tab_proposal, tab_budget, tab_eval, tab_history = tabs[0], tabs[1], tabs[2], tabs[3]
    tab_logs = tabs[4] if has_logs else None

    # ---- Proposal Tab ----
    with tab_proposal:
        st.markdown(f"### {proposal.get('title', 'Untitled Proposal')}")
        st.markdown("---")

        sections = [
            ("Abstract", "abstract"),
            ("Background / Problem Statement", "background"),
            ("Objectives", "objectives"),
            ("Methodology", "methodology"),
            ("Expected Impact", "expected_impact"),
            ("Deliverables", "deliverables"),
        ]

        for heading, key in sections:
            content = proposal.get(key, "")
            if content:
                st.markdown(f"#### {heading}")
                st.markdown(content)
                st.markdown("")

    # ---- Budget Tab ----
    with tab_budget:
        st.markdown("### Budget Breakdown")
        if budget.get("budget_table"):
            st.markdown(budget["budget_table"])
        else:
            st.info("No budget data available.")

        st.markdown("---")

        st.markdown("### Milestone Schedule")
        if budget.get("milestone_schedule"):
            st.markdown(budget["milestone_schedule"])
        else:
            st.info("No milestone data available.")

        st.markdown("---")

        st.markdown("### Cost Justification")
        if budget.get("cost_justification"):
            st.markdown(budget["cost_justification"])
        else:
            st.info("No cost justification available.")

    # ---- Evaluation Tab ----
    with tab_eval:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Score", f"{evaluation['total_score']}/100")
        with col2:
            st.metric("Rule Score", f"{evaluation['rule_score']}/40")
        with col3:
            st.metric("LLM Score", f"{evaluation['llm_score']}/60")

        st.markdown("---")

        st.markdown("#### Rubric Breakdown")
        rubric = evaluation.get("rubric_breakdown", {})
        if rubric:
            for criterion, score in rubric.items():
                col_name, col_bar, col_score = st.columns([3, 6, 1])
                with col_name:
                    st.markdown(f"**{criterion}**")
                with col_bar:
                    st.progress(score / 10)
                with col_score:
                    st.markdown(f"**{score}**/10")
        st.markdown("---")

        st.markdown("#### Critique Report")
        critique = evaluation.get("critique_report", "")
        if critique:
            st.markdown(critique)
        else:
            st.info("No critique available.")

        missing = evaluation.get("missing_sections", [])
        if missing:
            st.markdown("#### Issues Identified")
            for item in missing:
                st.markdown(f"- {item}")

    # ---- Iteration History Tab ----
    with tab_history:
        st.markdown("### Score Progression")

        if len(iterations) > 1:
            scores = [it["evaluation"]["total_score"] for it in iterations]
            iter_labels = [f"Iteration {it['iteration']}" for it in iterations]

            chart_data = {
                "Iteration": iter_labels,
                "Score": scores,
            }
            st.bar_chart(chart_data, x="Iteration", y="Score")
        else:
            st.info(
                f"Only 1 iteration completed (Score: {iterations[0]['evaluation']['total_score']}/100). "
                "Increase iterations to see improvement progression."
            )

        st.markdown("---")
        st.markdown("### Iteration Details")

        for it in iterations:
            with st.expander(
                f"Iteration {it['iteration']} — Score: {it['evaluation']['total_score']}/100",
                expanded=(it == latest),
            ):
                st.markdown(f"**Title:** {it['proposal'].get('title', 'N/A')}")
                st.markdown(f"**Score:** {it['evaluation']['total_score']}/100")

                if it.get("change_summary"):
                    st.markdown("**Changes Made:**")
                    st.markdown(it["change_summary"])

                st.markdown("**Critique:**")
                st.markdown(it["evaluation"].get("critique_report", "N/A"))

    # ---- Agent Logs Tab ----
    if tab_logs is not None:
        with tab_logs:
            st.markdown("### Agent Reasoning Logs")
            st.markdown("*Detailed logs from each CrewAI agent's execution.*")
            st.markdown("---")

            for it in iterations:
                agent_logs = it.get("agent_logs", {})
                if not any(agent_logs.values()):
                    continue
                st.markdown(f"#### Iteration {it['iteration']}")
                for agent_name, log_text in agent_logs.items():
                    if log_text:
                        with st.expander(f"{agent_name}", expanded=False):
                            st.code(log_text, language="text")
                st.markdown("---")

    # ---- Pipeline Log ----
    if "log_messages" in st.session_state:
        with st.expander("📋 Pipeline Execution Log", expanded=False):
            for msg in st.session_state["log_messages"]:
                st.markdown(f"- {msg}")

    # ---- Interactive Features ----
    st.markdown("---")
    colA, colB = st.columns([1, 1])
    
    with colA:
        st.markdown("### 📥 Download Final Proposal")

        def _build_pdf(proposal, budget, sections):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Title
            pdf.set_font("Helvetica", "B", 18)
            title = proposal.get("title", "Research Proposal")
            pdf.multi_cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(6)

            # Proposal sections
            for heading, key in sections:
                content = proposal.get(key, "")
                if content:
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.multi_cell(0, 8, heading.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(2)
                    pdf.set_font("Helvetica", "", 11)
                    # Clean markdown formatting for PDF
                    clean = content.replace("**", "").replace("*", "").replace("#", "")
                    pdf.multi_cell(0, 6, clean.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(4)

            # Budget
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 15)
            pdf.multi_cell(0, 10, "Budget & Timeline")
            pdf.ln(4)
            for bkey, bheading in [("budget_table", "Budget Breakdown"), ("milestone_schedule", "Milestone Schedule"), ("cost_justification", "Cost Justification")]:
                bval = budget.get(bkey, "")
                if bval:
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.multi_cell(0, 8, bheading)
                    pdf.ln(2)
                    pdf.set_font("Helvetica", "", 10)
                    clean = bval.replace("**", "").replace("*", "").replace("#", "").replace("|", "  ")
                    pdf.multi_cell(0, 5, clean.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(4)

            buf = io.BytesIO()
            pdf.output(buf)
            return buf.getvalue()

        pdf_bytes = _build_pdf(proposal, budget, sections)

        st.download_button(
            label="Download Proposal (PDF)",
            data=pdf_bytes,
            file_name="research_proposal.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

    with colB:
        st.markdown("### 💬 Request Specific Changes")
        user_feedback = st.text_area(
            "What should be improved?", 
            placeholder="e.g., Expand the methodology with more details...",
            label_visibility="collapsed"
        )
        if st.button("Refine Proposal", type="primary", use_container_width=True):
            if not user_feedback.strip():
                st.warning("Please enter feedback first.")
            else:
                with st.spinner("Applying feedback & re-evaluating..."):
                    from crew.grant_crew import run_user_refinement_cycle
                    _verbose = st.session_state.get("show_logs_toggle", False)
                    new_iter = run_user_refinement_cycle(
                        session_id=result["session_id"],
                        research_topic=result["research_topic"],
                        current_proposal=proposal,
                        current_budget=budget,
                        evaluation=evaluation,
                        user_feedback=user_feedback.strip(),
                        iteration=latest["iteration"] + 1,
                        verbose=show_agent_logs,
                    )
                    st.session_state["result"]["iterations"].append(new_iter)
                    st.session_state["log_messages"].append(f"✅ User-requested refinement complete (Score: {new_iter['evaluation']['total_score']}/100)")
                    st.rerun()
