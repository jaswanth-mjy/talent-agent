import csv
import io
from typing import Dict, List

import streamlit as st

from core.agent import TalentAgent


st.set_page_config(
    page_title="TalentDesk",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

PIPELINE_TIMEOUT_SECONDS = 90
STAGE_ORDER = [
    "JD Parsing", "Discovery", "Matching",
    "Outreach", "Scoring", "Ranking", "Complete",
]


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

        :root {
            --navy:       #1B2B4B;
            --slate:      #4A5568;
            --muted:      #6B7A99;
            --line:       #DDE2EE;
            --stone:      #F5F6FA;
            --mist:       #EEF1F7;
            --white:      #FFFFFF;
            --teal:       #0E7C6B;
            --teal-bg:    #E4F4F1;
            --teal-line:  #A7D9D2;
            --blue:       #1A56DB;
            --blue-bg:    #EBF2FF;
            --blue-line:  #A4C3F8;
            --amber:      #92400E;
            --amber-bg:   #FEF3C7;
            --amber-line: #FDE68A;
            --rose:       #9B1C1C;
            --rose-bg:    #FEE2E2;
            --rose-line:  #FCA5A5;
            --radius:     10px;
            --radius-lg:  16px;
            --shadow:     0 1px 3px rgba(27,43,75,0.07), 0 4px 12px rgba(27,43,75,0.05);
            --shadow-sm:  0 1px 2px rgba(27,43,75,0.06);

            --bg-page:    var(--stone);
            --bg-surface: var(--white);
            --bg-soft:    var(--mist);
            --text-main:  var(--navy);
            --text-sub:   var(--slate);
            --text-muted: var(--muted);
            --sidebar-bg: var(--navy);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --line:       #334155;
                --stone:      #0F172A;
                --mist:       #1E293B;
                --white:      #111827;
                --navy:       #E5E7EB;
                --slate:      #CBD5E1;
                --muted:      #94A3B8;
                --shadow:     0 1px 2px rgba(0,0,0,0.35), 0 8px 20px rgba(0,0,0,0.22);
                --shadow-sm:  0 1px 2px rgba(0,0,0,0.3);

                --bg-page:    #0F172A;
                --bg-surface: #111827;
                --bg-soft:    #1E293B;
                --text-main:  #E5E7EB;
                --text-sub:   #CBD5E1;
                --text-muted: #94A3B8;
                --sidebar-bg: #0B1220;
            }
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
        }
        .stApp { background-color: var(--bg-page); }
        .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }

        [data-testid="stMarkdownContainer"],
        [data-testid="stText"],
        [data-testid="stCaptionContainer"] {
            color: var(--text-sub);
        }

        section[data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
            border-right: none;
        }
        section[data-testid="stSidebar"] * { color: #C8D3EC !important; }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] strong { color: #FFFFFF !important; }
        section[data-testid="stSidebar"] .stTextArea textarea {
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }

        h1, h2, h3 { font-family: 'Lora', Georgia, serif; letter-spacing: -0.02em; color: var(--text-main); }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1rem 1.3rem;
            background: linear-gradient(135deg, #162645 0%, #1B2B4B 55%, #22355c 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: var(--radius-lg);
            margin: 1.75rem 0 1.35rem 0;
            box-shadow: var(--shadow);
            flex-wrap: wrap;
        }
        .tb-brand { display: flex; align-items: center; gap: 0.75rem; }
        .tb-icon {
            width: 38px; height: 38px; border-radius: 10px;
            background: rgba(255,255,255,0.12);
            display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
        }
        .tb-name { font-family: 'Lora', Georgia, serif; font-size: 1.02rem; font-weight: 700; color: #FFFFFF; }
        .tb-tag  { font-size: 0.78rem; color: #8FA3C8; margin-top: 0.1rem; }
        .tb-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end; }
        .tb-pill {
            padding: 0.38rem 0.8rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            color: #C8D3EC;
            font-size: 0.76rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .sec-head {
            font-family: 'Lora', Georgia, serif;
            font-size: 0.92rem; font-weight: 600; color: var(--slate);
            text-transform: uppercase; letter-spacing: 0.07em;
            margin: 1.5rem 0 0.7rem 0;
            padding-bottom: 0.45rem;
            border-bottom: 2px solid var(--navy);
        }

        .card {
            background: var(--bg-surface); border: 1px solid var(--line);
            border-radius: var(--radius-lg); padding: 1.2rem 1.3rem;
            box-shadow: var(--shadow);
        }

        .cand {
            background: var(--bg-surface); border: 1px solid var(--line);
            border-left: 4px solid var(--navy);
            border-radius: var(--radius-lg);
            padding: 1.1rem 1.2rem 0.95rem;
            box-shadow: var(--shadow-sm); margin-bottom: 0.85rem;
            transition: box-shadow 0.12s;
        }
        .cand:hover { box-shadow: var(--shadow); }
        .cand-rank { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); }
        .cand-name { font-family: 'Lora', Georgia, serif; font-size: 0.95rem; font-weight: 700; color: var(--text-main); }
        .cand-meta { font-size: 0.82rem; color: var(--text-sub); margin-top: 0.18rem; }

        .mini {
            background: var(--bg-soft); border: 1px solid var(--line);
            border-radius: var(--radius); padding: 0.6rem 0.75rem; text-align: center;
        }
        .mini-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.09em; color: var(--text-muted); margin-bottom: 0.2rem; }
        .mini-val   { font-family: 'Lora', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: var(--text-main); }
        .mini-sub   { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.08rem; }

        .badge {
            display: inline-flex; align-items: center; gap: 0.25rem;
            padding: 0.32rem 0.7rem; border-radius: 999px;
            font-size: 0.76rem; font-weight: 600; line-height: 1;
        }
        .b-fast   { background: var(--teal-bg);  color: var(--teal);  border: 1px solid var(--teal-line); }
        .b-screen { background: var(--blue-bg);  color: var(--blue);  border: 1px solid var(--blue-line); }
        .b-warm   { background: var(--amber-bg); color: var(--amber); border: 1px solid var(--amber-line); }
        .b-low    { background: var(--rose-bg);  color: var(--rose);  border: 1px solid var(--rose-line); }

        .chip {
            display: inline-flex; padding: 0.25rem 0.55rem; border-radius: 6px;
            background: var(--bg-soft); border: 1px solid var(--line);
            color: var(--text-sub); font-size: 0.76rem; font-weight: 500;
            margin: 0 0.25rem 0.25rem 0;
        }

        .pipe-row {
            display: flex; flex-wrap: wrap; gap: 0.4rem;
            padding: 0.75rem 1rem;
            background: var(--bg-surface); border: 1px solid var(--line); border-radius: var(--radius);
        }
        .stage {
            display: inline-flex; align-items: center; gap: 0.3rem;
            padding: 0.28rem 0.65rem; border-radius: 999px;
            font-size: 0.76rem; font-weight: 600;
        }
        .s-done    { background: var(--teal-bg);  color: var(--teal);  border: 1px solid var(--teal-line); }
        .s-running { background: var(--blue-bg);  color: var(--blue);  border: 1px solid var(--blue-line); }
        .s-wait    { background: var(--mist);     color: var(--muted); border: 1px solid var(--line); }

        .stButton > button {
            background: #0E7C6B !important; color: #FFFFFF !important;
            font-weight: 600 !important; border: none !important;
            border-radius: var(--radius) !important; padding: 0.72rem 1.1rem !important;
            font-size: 0.9rem !important;
            box-shadow: 0 2px 8px rgba(14,124,107,0.3) !important;
        }
        .stButton > button:hover { opacity: 0.92 !important; }

        .stDownloadButton > button {
            background: var(--bg-surface) !important; color: var(--text-main) !important;
            border: 1.5px solid var(--line) !important;
            border-radius: var(--radius) !important; font-weight: 600 !important;
        }

        [data-testid="stMetric"] {
            background: var(--bg-surface); border: 1px solid var(--line);
            border-radius: var(--radius); padding: 0.9rem 1rem; box-shadow: var(--shadow-sm);
        }
        [data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.8rem !important; }
        [data-testid="stMetricValue"] { color: var(--text-main) !important; font-weight: 700 !important; }

        .stProgress > div > div { border-radius: 99px; }
        div[data-testid="stExpander"] {
            border-radius: var(--radius) !important;
            border: 1px solid var(--line) !important;
            background: var(--bg-soft) !important;
        }

        .info-wrap {
            background: var(--bg-surface); border: 1px solid var(--line);
            border-radius: var(--radius-lg); padding: 1.6rem 1.8rem; box-shadow: var(--shadow-sm);
        }
        .info-step { display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1.2rem; }
        .info-step:last-child { margin-bottom: 0; }
        .info-num {
            min-width: 28px; height: 28px; border-radius: 999px;
            background: var(--navy); color: #fff;
            font-size: 0.8rem; font-weight: 700;
            display: flex; align-items: center; justify-content: center; margin-top: 0.05rem;
        }
        .info-title { font-weight: 600; color: var(--text-main); font-size: 0.92rem; }
        .info-body  { font-size: 0.83rem; color: var(--text-sub); margin-top: 0.12rem; line-height: 1.55; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _shortlist_to_csv(rows: List[Dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=[
        "name", "final_score", "match_score", "interest_score",
        "skill_score", "experience_score", "skill_coverage",
        "experience_gap", "recommendation", "explanation",
    ])
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "name":             row.get("name", "Unknown"),
            "final_score":      row.get("final_score", 0),
            "match_score":      row.get("match_score", 0),
            "interest_score":   row.get("interest_score", 0),
            "skill_score":      row.get("skill_score", 0),
            "experience_score": row.get("experience_score", 0),
            "skill_coverage":   row.get("skill_coverage", 0),
            "experience_gap":   row.get("experience_gap", 0),
            "recommendation":   row.get("recommendation", ""),
            "explanation":      " | ".join(row.get("explanation", [])),
        })
    return buffer.getvalue()


def _badge(rec: str):
    r = rec.lower()
    if "fast-track" in r: return "b-fast",   "✦"
    if "screen"     in r: return "b-screen", "◈"
    if "warm"       in r: return "b-warm",   "◎"
    return "b-low", "○"


def _stage_bar(state: Dict[str, str]) -> str:
    out = []
    for s in STAGE_ORDER:
        v = state.get(s, "pending")
        if v == "complete":  css, ic = "s-done",    "✓"
        elif v == "running": css, ic = "s-running",  "▶"
        else:                css, ic = "s-wait",     "·"
        out.append(f'<span class="stage {css}">{ic} {s}</span>')
    return f'<div class="pipe-row">{"".join(out)}</div>'


def _chip(t: str) -> str:
    return f'<span class="chip">{t}</span>'


st.session_state.setdefault("contacted_candidates", set())
st.session_state.setdefault("pipeline_result", None)
st.session_state.setdefault("stage_state", {s: "pending" for s in STAGE_ORDER})
st.session_state.setdefault("stage_messages", [])

# ─────────────────────────────────────────────────────────────────────────────
_apply_styles()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Find Candidates")
    st.caption("Describe the role and hit Run.")
    st.markdown("")
    default_jd = "Looking for Python backend developer with Django and SQL, 2 years experience"
    jd_input = st.text_area(
        "Job Description", value=default_jd, height=210,
        placeholder="Role, skills, years of experience…",
    )
    st.caption("Shortlist size")
    top_k = st.slider("", min_value=1, max_value=10, value=5, label_visibility="collapsed")
    st.markdown("")
    run_clicked = st.button("▶  Run Pipeline", use_container_width=True)
    st.markdown("---")
    st.caption("**Scoring**  \nMatch = 0.7 × Skill + 0.3 × Experience  \nFinal = 0.6 × Match + 0.4 × Interest")


st.markdown(
    "<div style='height:0.35rem;'></div>",
    unsafe_allow_html=True,
)

st.markdown(
        """
        <div class="topbar">
            <div class="tb-brand">
                <div class="tb-icon">👥</div>
                <div>
                    <div class="tb-name">TalentDesk</div>
                    <div class="tb-tag">AI-powered candidate scouting &amp; ranking</div>
                </div>
            </div>
            <div class="tb-pills">
                <div class="tb-pill">Shortlist size: 1–10</div>
                <div class="tb-pill">Explainable scores</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
)


@st.cache_resource
def get_agent() -> TalentAgent:
    return TalentAgent()


# ── Run pipeline ─────────────────────────────────────────────────────────────
if run_clicked:
    if not jd_input.strip():
        st.error("Please enter a job description before running.")
    else:
        st.session_state["stage_state"]    = {s: "pending" for s in STAGE_ORDER}
        st.session_state["stage_messages"] = []

        st.markdown('<div class="sec-head">Pipeline progress</div>', unsafe_allow_html=True)
        stage_ph   = st.empty()
        message_ph = st.empty()

        def update_progress(stage: str, message: str) -> None:
            sm, passed = {}, False
            for s in STAGE_ORDER:
                if s == stage:   sm[s] = "running"; passed = True
                elif not passed: sm[s] = "complete"
                else:            sm[s] = "pending"
            st.session_state["stage_state"] = sm
            st.session_state["stage_messages"].append((stage, message))
            stage_ph.markdown(_stage_bar(sm), unsafe_allow_html=True)
            html = "".join(
                f"<div style='font-size:0.82rem;color:var(--text-muted);margin-top:0.3rem;'>"
                f"<strong style='color:var(--text-sub)'>{s}:</strong> {m}</div>"
                for s, m in st.session_state["stage_messages"][-6:]
            )
            message_ph.markdown(html, unsafe_allow_html=True)

        try:
            with st.spinner("Running talent pipeline…"):
                agent  = get_agent()
                output = agent.run(jd_input, top_k, progress_callback=update_progress)
            st.session_state["pipeline_result"] = output
            st.session_state["stage_state"] = {s: "complete" for s in STAGE_ORDER}
            stage_ph.markdown(_stage_bar(st.session_state["stage_state"]), unsafe_allow_html=True)
        except RuntimeError as err:
            st.error(str(err))
            st.info("Start Ollama with `ollama serve` and pull required models, then retry.")
            st.stop()
        except Exception as err:
            st.error(f"Pipeline failed: {err}")
            st.info("Check Ollama status. Try reducing shortlist size.")
            st.stop()


# ── Results ───────────────────────────────────────────────────────────────────
result = st.session_state.get("pipeline_result")

if result:
    parsed_jd = result["parsed_jd"]
    shortlist = result["results"]
    best      = shortlist[0] if shortlist else {}

    st.markdown('<div class="sec-head">Summary</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Role",              parsed_jd.get("role", "—"))
    c2.metric("Skills Detected",   len(parsed_jd.get("skills", [])))
    c3.metric("Candidates Ranked", len(shortlist))
    c4.metric("Top Pick",          best.get("name", "—"))

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown('<div class="sec-head">Role Details</div>', unsafe_allow_html=True)
        st.markdown(
            f"""<div class="card">
                    <div style="font-weight:600;color:var(--text-main);font-size:0.84rem;margin-bottom:0.45rem;">
                    {parsed_jd.get('role','Unknown')}
                    <span style="font-weight:400;color:var(--text-muted);font-size:0.84rem;">
                    &nbsp;·&nbsp;{parsed_jd.get('experience_years', 0)} yrs exp
                    </span>
                </div>
                {"".join(_chip(s) for s in parsed_jd.get("skills", []))}
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sec-head">Export & Actions</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇  Download Shortlist CSV",
            data=_shortlist_to_csv(shortlist),
            file_name="shortlist.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.metric("Candidates Contacted", len(st.session_state["contacted_candidates"]))

        if best:
            bcss, bic = _badge(best.get("recommendation", ""))
            st.markdown(
                f"""<div class="card" style="margin-top:0.85rem;border-left:4px solid var(--text-main);">
                    <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                                letter-spacing:0.09em;color:var(--text-muted);margin-bottom:0.35rem;">
                        Top Candidate
                    </div>
                    <div style="font-family:'Lora',Georgia,serif;font-size:0.92rem;
                                font-weight:700;color:var(--text-main);">
                        {best.get('name','—')}
                    </div>
                    <div style="margin-top:0.4rem;">
                        <span class="badge {bcss}">{bic} {best.get('recommendation','—')}</span>
                    </div>
                    <div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.35rem;">
                        Final score: <strong style="color:var(--text-main)">{best.get('final_score',0)}</strong>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sec-head">Pipeline Trace</div>', unsafe_allow_html=True)
        st.markdown(_stage_bar(st.session_state.get("stage_state", {})), unsafe_allow_html=True)
        for stage, msg in st.session_state.get("stage_messages", [])[-5:]:
            st.caption(f"**{stage}:** {msg}")

    with right:
        st.markdown('<div class="sec-head">Ranked Candidates</div>', unsafe_allow_html=True)

        for idx, row in enumerate(shortlist, start=1):
            key       = row.get("name", f"candidate_{idx}")
            contacted = key in st.session_state["contacted_candidates"]
            bcss, bic = _badge(row.get("recommendation", ""))

            with st.container():
                st.markdown('<div class="cand">', unsafe_allow_html=True)

                hl, hr = st.columns([2, 1])
                with hl:
                    st.markdown(
                        f"""<div class="cand-rank">#{idx}</div>
                        <div class="cand-name">{row['name']}</div>
                        <div class="cand-meta">
                            Final&nbsp;<strong>{row['final_score']}</strong>&nbsp;·&nbsp;
                            Match&nbsp;<strong>{row['match_score']}</strong>&nbsp;·&nbsp;
                            Interest&nbsp;<strong>{row['interest_score']}</strong>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with hr:
                    dot = (
                        '<div style="color:#0E7C6B;font-size:0.8rem;font-weight:600;">● Contacted</div>'
                        if contacted else
                        '<div style="color:var(--text-muted);font-size:0.8rem;">○ Not contacted</div>'
                    )
                    st.markdown(
                        f"""<div style="text-align:right;padding-top:0.15rem;">
                            <span class="badge {bcss}">{bic} {row.get('recommendation','Review')}</span>
                            <div style="margin-top:0.45rem;">{dot}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                s1, s2, s3 = st.columns(3)
                s1.markdown(
                    f"""<div class="mini"><div class="mini-label">Match</div>
                        <div class="mini-val">{row['match_score']}</div>
                        <div class="mini-sub">Skill {row.get('skill_score',0)} · Exp {row.get('experience_score',0)}</div>
                    </div>""", unsafe_allow_html=True)
                s2.markdown(
                    f"""<div class="mini"><div class="mini-label">Interest</div>
                        <div class="mini-val">{row['interest_score']}</div>
                        <div class="mini-sub">Outreach signal</div>
                    </div>""", unsafe_allow_html=True)
                s3.markdown(
                    f"""<div class="mini"><div class="mini-label">Final</div>
                        <div class="mini-val">{row['final_score']}</div>
                        <div class="mini-sub">{row.get('recommendation','Review')}</div>
                    </div>""", unsafe_allow_html=True)

                p1, p2 = st.columns([3, 2])
                with p1:
                    st.progress(min(int(row.get("skill_coverage", 0)), 100),
                                text=f"Skill coverage: {row.get('skill_coverage', 0)}%")
                    st.progress(min(int(row.get("match_score", 0)), 100),
                                text=f"Match strength: {row.get('match_score', 0)} / 100")
                with p2:
                    st.markdown("**Why this candidate**")
                    st.markdown("".join(_chip(i) for i in row.get("explanation", [])),
                                unsafe_allow_html=True)
                    st.caption(
                        f"Coverage: **{row.get('skill_coverage', 0)}%** · "
                        f"Exp gap: **{row.get('experience_gap', 0)} yrs**"
                    )

                a1, a2 = st.columns([1, 2])
                with a1:
                    if not contacted:
                        if st.button("Mark Contacted", key=f"c_{idx}_{key}", use_container_width=True):
                            st.session_state["contacted_candidates"].add(key)
                            st.rerun()
                    else:
                        if st.button("Unmark", key=f"u_{idx}_{key}", use_container_width=True):
                            st.session_state["contacted_candidates"].discard(key)
                            st.rerun()
                with a2:
                    with st.expander("View outreach conversation"):
                        st.json(row.get("conversation", []))

                st.markdown("</div>", unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
else:
    st.markdown('<div class="sec-head">How it works</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-wrap">
            <div class="info-step">
                <div class="info-num">1</div>
                <div>
                    <div class="info-title">Paste the Job Description</div>
                    <div class="info-body">Describe the role, required skills, and years of experience in the sidebar. Plain English works — no special format needed.</div>
                </div>
            </div>
            <div class="info-step">
                <div class="info-num">2</div>
                <div>
                    <div class="info-title">Run the Pipeline</div>
                    <div class="info-body">The agent parses the JD, discovers candidates, simulates outreach, scores fit, and ranks everyone in one click. Each stage updates live.</div>
                </div>
            </div>
            <div class="info-step">
                <div class="info-num">3</div>
                <div>
                    <div class="info-title">Act on the Shortlist</div>
                    <div class="info-body">Every candidate comes with a clear recommendation and explainable score. Export to CSV, mark who you've contacted, and move fast.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )