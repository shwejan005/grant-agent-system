"""
Streamlit UI for the AI Research Grant Proposal Generator & Evaluator.
Refined editorial aesthetic design — white background, black text, Syne & DM Sans.
"""
import streamlit as st
import io
import sqlite3
import os
import json
import plotly.express as px
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
# Custom CSS — Refined Brutalism
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Syne:wght@400..800&display=swap');

    html, body, .stApp {
        background-color: #ffffff !important;
        font-family: 'DM Sans', sans-serif !important;
        color: #0a0a0a !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Syne', sans-serif !important;
        color: #0a0a0a !important;
        letter-spacing: -0.02em !important;
    }

    [data-testid="stHeader"] { background-color: transparent !important; }

    /* .block-container */
    .block-container {
        max-width: 1100px !important;
        padding: 2rem 3rem !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f5f5f5 !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] > div {
        box-shadow: none !important;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border-radius: 0 !important;
        border: none !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: none !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    .stButton > button p,
    .stDownloadButton > button p { color: #ffffff !important; }

    /* Inputs */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid #0a0a0a !important;
        border-radius: 0 !important;
        font-family: 'DM Sans', sans-serif !important;
        color: #0a0a0a !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, [data-baseweb="select"] > div:focus-within {
        outline: 2px solid #0a0a0a !important;
        outline-offset: -1px;
        border-color: #0a0a0a !important;
        box-shadow: none !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e0e0e0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Syne', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        background-color: transparent !important;
        color: #6b6b6b !important;
        border: none !important;
        padding-bottom: 1rem !important;
        padding-top: 1rem !important;
        margin-right: 2rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0a0a0a !important;
        border-bottom: 2px solid #0a0a0a !important;
    }

    /* Tables */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        font-family: 'DM Sans', sans-serif !important;
        margin-bottom: 2rem !important;
    }
    th {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        font-family: 'Syne', sans-serif !important;
        padding: 0.8rem !important;
        text-align: left !important;
        border: 1px solid #0a0a0a !important;
        font-weight: normal !important;
    }
    td {
        padding: 0.8rem !important;
        border: 1px solid #0a0a0a !important;
        color: #0a0a0a !important;
        background-color: #ffffff !important;
    }
    tr:nth-child(even) td {
        background-color: #f5f5f5 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #f5f5f5 !important;
        border: 1px solid #0a0a0a !important;
        border-radius: 0 !important;
        padding: 1.5rem !important;
        text-align: left !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Syne', sans-serif !important;
        color: #6b6b6b !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'DM Sans', sans-serif !important;
        color: #0a0a0a !important;
    }

    /* Progress */
    .stProgress > div > div {
        background-color: #0a0a0a !important;
    }
    .stProgress > div {
        background-color: #e0e0e0 !important;
    }

    /* Blockquote */
    blockquote {
        margin: 1.5rem 0 !important;
        padding: 1.5rem !important;
        border-left: 3px solid #0a0a0a !important;
        background-color: #f5f5f5 !important;
        color: #6b6b6b !important;
        font-style: italic !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Slider label color */
    .stSlider [data-baseweb="slider"] {
        color: #000000 !important;
    }
    .stSlider [role="slider"] {
        background-color: #000000 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Syne', sans-serif !important;
        color: #0a0a0a !important;
    }
    
    hr {
        border-color: #e0e0e0 !important;
    }
    
    /* Code Blocks / Agent Logs */
    [data-testid="stCodeBlock"] pre, [data-testid="stCodeBlock"] code, [data-testid="stCodeBlock"] span {
        background-color: #ffffff !important;
        color: #0a0a0a !important;
    }

    /* Checkbox & Text Labels */
    .stCheckbox label span, .stCheckbox label p, [data-testid="stWidgetLabel"] {
        color: #0a0a0a !important;
    }
    
    /* Plotly generic */
    .js-plotly-plot .plotly .main-svg { background-color: transparent !important; }
</style>
""", unsafe_allow_html=True)


# Helper: Format a section header with '0X' prefix
def section_header(prefix: str, title: str):
    st.markdown(f"""
        <div style="border-top: 2px solid #0a0a0a; padding-top: 1rem; margin-top: 2rem; margin-bottom: 1.5rem; display: flex; align-items: baseline; gap: 1rem;">
            <span style="font-family: 'Syne', sans-serif; font-size: 0.9rem; color: #6b6b6b; font-weight: 600;">{prefix}</span>
            <span style="font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em; color: #0a0a0a;">{title}</span>
        </div>
    """, unsafe_allow_html=True)


# Fetch last run timestamp
def get_last_run_timestamp():
    db_path = "db/proposals.db"
    if not os.path.exists(db_path):
        return "N/A"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT created_at FROM proposals ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            # simple format conversion if it's ISO
            return row[0].replace("T", " ")[:19]
    except Exception:
        pass
    return "N/A"


# ─────────────────────────────────────────────────────────────
# Sidebar & Layout Switching
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h1 style='margin-bottom:0;'>AI Grant Proposal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b6b6b; font-style:italic; font-family:\"DM Sans\", sans-serif; margin-top:0.5rem;'>Automated academic research framework</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)

    st.markdown("<label style='font-family: \"Syne\", sans-serif; color: #0a0a0a; font-weight: 600; font-size: 0.9rem; margin-top: 1rem; display: block;'>REFINEMENT ITERATIONS</label>", unsafe_allow_html=True)
    max_iterations = st.slider(
        "",
        min_value=1,
        max_value=5,
        value=2,
        label_visibility="collapsed"
    )

    show_agent_logs = st.checkbox(
        "Show Agent Logs",
        value=False,
    )
    
    # Render the input in the sidebar ONLY if a result is present
    if "result" in st.session_state:
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        st.markdown("<label style='font-family: \"Syne\", sans-serif; color: #0a0a0a; font-weight: 600; font-size: 0.9rem;'>NEW RESEARCH TOPIC</label>", unsafe_allow_html=True)
        sidebar_topic = st.text_area(
            "New Topic",
            height=120,
            key="sidebar_topic_input",
            label_visibility="collapsed"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        sidebar_generate = st.button(
            "Generate Another",
            use_container_width=True,
            key="btn_sidebar"
        )
    
    last_run = get_last_run_timestamp()
    st.markdown(f"<div style='text-align: center; color: #6b6b6b; font-size: 0.75rem; margin-top: 2rem;'>LAST GENERATED: {last_run}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Main Panel View Logic
# ─────────────────────────────────────────────────────────────
research_topic = ""
generate_btn = False

if "result" not in st.session_state:
    # ─── 1. Landing Page / Hero Section ───
    st.markdown("""
        <style>
        [data-testid="stHeader"] { display: none; background-color: transparent !important; }
        .block-container { max-width: 1200px !important; padding-top: 0 !important; }
        
        /* Hero UI Overrides */
        [data-testid="stTextArea"] {
            background-color: #fcfcfc !important;
            border: 1px solid #0a0a0a !important;
            border-radius: 40px !important;
            box-shadow: 0px 10px 40px 5px rgba(194,194,194,0.25) !important;
            padding: 1rem 1.5rem !important;
            animation: fadeInUp 0.8s ease-out 0.5s both;
        }
        [data-testid="stTextArea"] textarea {
            border: none !important;
            background: transparent !important;
            font-size: 1.1rem !important;
        }
        [data-testid="stButton"] button {
            background: linear-gradient(180deg, #333 0%, #0a0a0a 100%) !important;
            box-shadow: inset -4px -6px 25px 0px rgba(201,201,201,0.08), inset 4px 4px 10px 0px rgba(29,29,29,0.24) !important;
            border-radius: 40px !important;
            border: none !important;
            padding: 1.5rem !important;
            color: white !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            font-family: 'Syne', sans-serif !important;
            font-weight: 700 !important;
            display: block;
            animation: fadeInUp 0.8s ease-out 0.6s both;
        }
        [data-testid="stButton"] p { font-size: 1.1rem !important; }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-delay-1 { animation: fadeInUp 0.8s ease-out 0.1s both; }
        .animate-delay-2 { animation: fadeInUp 0.8s ease-out 0.3s both; }
        .animate-delay-4 { animation: fadeInUp 0.8s ease-out 0.7s both; }
        </style>
        
        <video autoplay loop muted playsinline style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; object-fit: cover; transform: scaleY(-1); z-index: -2;">
          <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260302_085640_276ea93b-d7da-4418-a09b-2aa5b490e838.mp4" type="video/mp4">
        </video>
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; background: linear-gradient(to bottom, rgba(255,255,255,0) 26.416%, white 66.943%); pointer-events: none;"></div>
        
        <div style="display: flex; flex-direction: column; align-items: center; text-align: center; padding-top: 15vh; gap: 32px; margin-bottom: 2rem;">
            <h1 class="animate-delay-1" style="font-family: 'Syne', sans-serif; font-weight: 700; font-size: 80px; letter-spacing: -0.02em; color: #0a0a0a; line-height: 1.1; margin: 0;">
                Automated <span style="font-family: 'DM Sans', sans-serif; font-style: italic; font-size: 100px; font-weight: 400;">academic</span> research framework
            </h1>
            <p class="animate-delay-2" style="font-family: 'DM Sans', sans-serif; font-size: 18px; color: #373a46; opacity: 0.8; max-width: 554px; line-height: 1.5; margin: 0;">
                Transform complex research topics into comprehensively structured, agency-ready grant proposals through evaluating multi-agent refinement.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 5, 1.5])
    with col2:
        research_topic = st.text_area(
            "Research Topic",
            placeholder="Describe your research objective... e.g., AI-powered early detection of crop diseases using drone imagery",
            height=120,
            key="hero_topic_input",
            label_visibility="collapsed"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("Generate Proposal", use_container_width=True, key="btn_hero")
        
    st.markdown("""
        <div class="animate-delay-4" style="text-align: center; margin-top: 40px; display: flex; flex-direction: column; align-items: center;">
            <div style="font-family: 'Syne', sans-serif; font-weight: 600; font-size: 14px; text-transform: uppercase; color: #0a0a0a; border: 1px solid #0a0a0a; padding: 10px 24px; border-radius: 99px; background: rgba(255,255,255,0.7); backdrop-filter: blur(10px);">
                ⭐ 1,400+ Proposals Generated
            </div>
        </div>
    """, unsafe_allow_html=True)

else:
    # ─── 2. Results Mode ───
    research_topic = st.session_state.get("sidebar_topic_input", "")
    generate_btn = st.session_state.get("btn_sidebar", False)



# ─────────────────────────────────────────────────────────────
# Main Panel
# ─────────────────────────────────────────────────────────────

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
            st.rerun() # Refresh to update SQLite timestamp
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

    # Tabs
    tab_labels = ["PROPOSAL", "BUDGET", "EVALUATION", "HISTORY"]
    has_logs = any(
        any(v for v in it.get("agent_logs", {}).values())
        for it in iterations
    )
    if has_logs:
        tab_labels.append("AGENT LOGS")

    tabs = st.tabs(tab_labels)
    tab_proposal, tab_budget, tab_eval, tab_history = tabs[0], tabs[1], tabs[2], tabs[3]
    tab_logs = tabs[4] if has_logs else None

    # ---- Tab 01: Proposal ----
    with tab_proposal:
        section_header("01", proposal.get('title', 'Untitled Proposal'))
        
        # Proposal container logic
        c1, c2 = st.columns([8, 2])
        with c2:
            st.markdown(f"""
                <div style="background: #0a0a0a; color: #fff; padding: 0.5rem 1rem; border-radius: 99px; text-align: center; font-family: 'Syne', sans-serif; font-weight: 700; width: fit-content; margin-left: auto;">
                    SCORE: {evaluation.get('total_score', 'N/A')}
                </div>
            """, unsafe_allow_html=True)
        
        sections = [
            ("Abstract", "abstract"),
            ("Background / Problem Statement", "background"),
            ("Objectives", "objectives"),
            ("Methodology", "methodology"),
            ("Expected Impact", "expected_impact"),
            ("Deliverables", "deliverables"),
        ]

        # Use a standard container and output the sections as native Markdown.
        # Streamlit doesn't support wrapping elements in custom HTML safely.
        with st.container():
            for heading, key in sections:
                content = proposal.get(key, "")
                if content:
                    st.markdown(f"#### {heading}")
                    st.markdown(content)
                    st.divider()

    # ---- Tab 02: Budget ----
    with tab_budget:
        section_header("02", "Budget & Timeline")
        
        st.markdown("#### Budget Breakdown")
        raw_budget = budget.get("budget_table", "")
        st.markdown(raw_budget if raw_budget else "*No budget data available.*")

        st.markdown("#### Timeline Milestones")
        raw_timeline = budget.get("milestone_schedule", "")
        st.markdown(raw_timeline if raw_timeline else "*No milestone data available.*")
            
        st.markdown("#### Cost Justification")
        justification = budget.get("cost_justification", "")
        if justification:
            st.markdown(f"<blockquote>{justification}</blockquote>", unsafe_allow_html=True)


    # ---- Tab 03: Evaluation ----
    with tab_eval:
        section_header("03", "Evaluation Metrics")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("TOTAL SCORE", f"{evaluation.get('total_score', 0)}/100")
        with c2: st.metric("RULE BASE", f"{evaluation.get('rule_score', 0)}/40")
        with c3: st.metric("LLM CRITIQUE", f"{evaluation.get('llm_score', 0)}/60")
        
        st.markdown("#### Rubric Breakdown")
        rubric = evaluation.get("rubric_breakdown", {})
        if rubric:
            for criterion, score in rubric.items():
                pct = (score / 10) * 100
                st.markdown(f"""
                    <div style='display: flex; align-items: center; margin-bottom: 0.8rem; font-family: "DM Sans", sans-serif;'>
                        <div style='flex: 0 0 200px; font-weight: 600; color: #0a0a0a; text-transform: uppercase; font-size: 0.85rem;'>{criterion}</div>
                        <div style='flex: 1; background-color: #e0e0e0; height: 8px; margin: 0 1.5rem; position: relative;'>
                            <div style='background-color: #0a0a0a; height: 100%; width: {pct}%;'></div>
                        </div>
                        <div style='flex: 0 0 50px; text-align: right; font-weight: 600; color: #0a0a0a;'>{score}/10</div>
                    </div>
                """, unsafe_allow_html=True)
                
        st.markdown("#### LLM Critique Report")
        critique = evaluation.get("critique_report", "")
        if critique:
            st.markdown(f"<blockquote>{critique}</blockquote>", unsafe_allow_html=True)

        missing = evaluation.get("missing_sections", [])
        if missing:
            st.markdown("#### Missing Required Sections")
            for item in missing:
                st.markdown(f"- {item}")


    # ---- Tab 04: History ----
    with tab_history:
        section_header("04", "Iteration History")
        
        if len(iterations) > 1:
            scores = [it["evaluation"]["total_score"] for it in iterations]
            iter_labels = [f"Iter {it['iteration']}" for it in iterations]
            
            # minimal plotly chart
            fig = px.line(
                x=iter_labels, y=scores, 
                markers=True,
                labels={"x": "", "y": "Total Score"}
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, color="#0a0a0a"),
                yaxis=dict(showgrid=False, zeroline=False, color="#0a0a0a"),
                font=dict(family="DM Sans", color="#0a0a0a"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=300
            )
            fig.update_traces(line_color="#0a0a0a", marker=dict(color="#0a0a0a", size=8))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("*Only 1 iteration completed. Chart available when there are multiple refinements.*")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Iteration cards
        for it in iterations:
            score = it['evaluation'].get('total_score', 0)
            iter_num = it['iteration']
            with st.container():
                st.markdown(f"""
                    <div style='border: 1px solid #0a0a0a; background-color: #f5f5f5; padding: 1.5rem; margin-bottom: 1rem;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                            <div style='font-family: "Syne", sans-serif; font-size: 1.2rem; font-weight: 700; text-transform: uppercase;'>Iteration 0{iter_num}</div>
                            <div style='background: #0a0a0a; color: #fff; padding: 0.2rem 0.8rem; border-radius: 99px; font-family: "Syne", sans-serif; font-weight: 700; font-size: 0.9rem;'>
                                SCORE: {score}
                            </div>
                        </div>
                        <div style='font-family: "DM Sans", sans-serif; color: #0a0a0a;'>
                            <strong>Title:</strong> {it['proposal'].get('title', 'N/A')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander(f"Iter 0{iter_num} Details"):
                    st.markdown("**Changes Made:**")
                    st.markdown(it.get("change_summary", "*No summary available*"))
                    st.markdown("**Critique:**")
                    st.markdown(it['evaluation'].get("critique_report", ""))

    # ---- AGENT LOGS ----
    if tab_logs is not None:
        with tab_logs:
            section_header("05", "Agent Reasoning")
            for it in iterations:
                agent_logs = it.get("agent_logs", {})
                if not any(agent_logs.values()):
                    continue
                st.markdown(f"#### Iteration {it['iteration']}")
                for agent_name, log_text in agent_logs.items():
                    if log_text:
                        with st.expander(f"🤖 {agent_name}", expanded=False):
                            st.code(log_text, language="text")

    # ---- Actions ----
    st.markdown("<hr style='margin: 3rem 0; border-color: #0a0a0a;'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    
    with c1:
        st.markdown("<h4 style='font-family: \"Syne\", sans-serif;'>DOWNLOAD PROPOSAL</h4>", unsafe_allow_html=True)

        def _build_pdf(proposal, budget, sections):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            title = proposal.get("title", "Research Proposal")
            pdf.multi_cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(6)
            for heading, key in sections:
                content = proposal.get(key, "")
                if content:
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.multi_cell(0, 8, heading.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(2)
                    pdf.set_font("Helvetica", "", 11)
                    clean = content.replace("#", "")
                    pdf.multi_cell(0, 6, clean.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(4)
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
                    clean = bval.replace("#", "").replace("|", "  ")
                    pdf.multi_cell(0, 5, clean.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(4)
            buf = io.BytesIO()
            pdf.output(buf)
            return buf.getvalue()

        pdf_bytes = _build_pdf(proposal, budget, sections)

        st.download_button(
            label="DOWNLOAD PDF FORMAT",
            data=pdf_bytes,
            file_name="research_proposal.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

    with c2:
        st.markdown("<h4 style='font-family: \"Syne\", sans-serif;'>REQUEST REVISIONS</h4>", unsafe_allow_html=True)
        user_feedback = st.text_area(
            "Instructions", 
            placeholder="e.g., Focus more on the computational overhead in methodology...",
            label_visibility="collapsed",
            height=100
        )
        if st.button("EXECUTE REFINEMENT", type="primary", use_container_width=True):
            if not user_feedback.strip():
                st.warning("Please enter revision instructions first.")
            else:
                with st.spinner("Applying instructions & re-evaluating..."):
                    from crew.grant_crew import run_user_refinement_cycle
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

