import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
from utils.db import get_supabase
from dotenv import load_dotenv
import re
load_dotenv()

st.set_page_config(page_title="AI Study Plan", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
    
    * { font-family: 'DM Sans', sans-serif; }
    h1,h2,h3 { font-family: 'Syne', sans-serif; }

    .hero-banner {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem; border-radius: 20px; color: white;
        margin-bottom: 2rem; position: relative; overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(102,126,234,0.15) 0%, transparent 60%),
                    radial-gradient(circle at 70% 50%, rgba(118,75,162,0.15) 0%, transparent 60%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse { 0%,100%{opacity:0.6} 50%{opacity:1} }

    .metric-glass {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 1.2rem;
        text-align: center; color: white;
    }

    .streak-card {
        background: linear-gradient(135deg, #f6d365, #fda085);
        border-radius: 16px; padding: 1.5rem;
        color: white; text-align: center;
        box-shadow: 0 8px 25px rgba(253,160,133,0.4);
    }
    .streak-number {
        font-family: 'Syne', sans-serif;
        font-size: 3.5rem; font-weight: 800;
        line-height: 1;
    }

    .exam-countdown {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        border-radius: 16px; padding: 1.5rem;
        color: white; text-align: center;
        box-shadow: 0 8px 25px rgba(245,87,108,0.4);
    }
    .countdown-number {
        font-family: 'Syne', sans-serif;
        font-size: 3.5rem; font-weight: 800;
        line-height: 1;
    }

    .plan-day-card {
        background: white; border-radius: 14px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 3px 15px rgba(0,0,0,0.07);
        border-left: 5px solid #667eea;
        margin-bottom: 0.8rem;
        transition: transform 0.2s;
    }
    .plan-day-card:hover { transform: translateX(4px); }
    .plan-day-card.revision { border-left-color: #f093fb; }
    .plan-day-card.rest { border-left-color: #a8edea; }
    .plan-day-card.exam { border-left-color: #f5576c; }

    .task-pill {
        display: inline-block;
        padding: 3px 10px; border-radius: 20px;
        font-size: 12px; font-weight: 500; margin: 2px;
    }
    .pill-video   { background:#dbeafe; color:#1e40af; }
    .pill-assign  { background:#fef3c7; color:#92400e; }
    .pill-cheat   { background:#d1fae5; color:#065f46; }
    .pill-revision{ background:#ede9fe; color:#4c1d95; }
    .pill-rest    { background:#f1f5f9; color:#475569; }

    .progress-subject {
        background: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 3px 20px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        color: white !important;
    }
    .progress-subject h3 { color: white !important; }
    .progress-subject span { color: rgba(255,255,255,0.75) !important; }
    .progress-subject strong { color: white !important; }
    .progress-track {
        background: rgba(255,255,255,0.1); border-radius: 999px;
        height: 12px; margin: 8px 0; overflow: hidden;
    }
    .progress-track {
        background: #f1f5f9; border-radius: 999px;
        height: 12px; margin: 8px 0; overflow: hidden;
    }
    .progress-fill {
        height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.8s ease;
    }

    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px; margin-top: 8px;
    }
    .cal-day {
        aspect-ratio: 1; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 600;
    }
    .cal-active   { background: #667eea; color: white; }
    .cal-inactive { background: #f1f5f9; color: #94a3b8; }
    .cal-today    { background: #f5576c; color: white; }
    .cal-header   { background: transparent; color: #94a3b8; font-size: 10px; }

    .insight-card {
        background: linear-gradient(135deg, #e0f2fe, #dbeafe);
        border-radius: 14px; padding: 1.2rem;
        border-left: 4px solid #3b82f6;
        margin-bottom: 0.8rem;
    }

    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem; font-weight: 700;
        color: #1e1b4b; margin: 1.5rem 0 0.8rem;
        display: flex; align-items: center; gap: 8px;
    }
    /* ── Insights Cards ── */
    .insight-alert {
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 15px;
        font-weight: 500;
        letter-spacing: 0.2px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .insight-icon {
        font-size: 1.4rem;
        flex-shrink: 0;
    }
    .insight-text {
        font-family: 'Syne', sans-serif;
        font-size: 14px;
        line-height: 1.5;
    }

    /* ── Section Titles ── */
    .section-title {
        font-family: 'Syne', sans-serif !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 1.8rem 0 0.8rem !important;
        letter-spacing: 0.3px;
    }

    /* ── Estimated Completion Cards ── */
    .eta-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin-bottom: 0.7rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .eta-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: white;
    }
    .eta-sub {
        font-size: 12px;
        color: rgba(255,255,255,0.45);
        margin-top: 3px;
    }
    .eta-days {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .eta-date {
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        text-align: right;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Auth Guard ────────────────────────────────────────
if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student = st.session_state.student
sb = get_supabase()
enrolled = student.get("enrolled_subjects", [])

# ─── Hero Banner ───────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <div style="position:relative;z-index:1;">
        <h1 style="font-size:2rem;margin:0;font-family:'Syne',sans-serif;">🧠 AI Study Plan</h1>
        <p style="opacity:0.85;margin:6px 0 0;font-size:1.05rem;">
            Personalized roadmap to ace your exam — with streaks, progress & smart revisions
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

if not enrolled:
    st.warning("Please enroll in a subject first from **My Subjects**.")
    st.stop()

# ═══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

def get_progress_data(student_id, subjects):
    """Fetch ALL data in 5 bulk queries only — no per-item DB calls."""

    # ── 5 bulk fetches ──────────────────────────────────
    all_subjects    = sb.table("subjects").select("*").execute()
    all_topics      = sb.table("topics").select("*").execute()
    all_videos      = sb.table("videos").select("id, topic_id").execute()
    all_assignments = sb.table("assignments").select("id, topic_id").execute()
    all_progress    = sb.table("student_progress").select("video_id").eq(
                        "student_id", student_id).eq("completed", True).execute()
    all_submissions = sb.table("submissions").select("assignment_id").eq(
                        "student_id", student_id).execute()

    # ── Build lookup sets ───────────────────────────────
    completed_video_ids  = {p["video_id"]      for p in all_progress.data}
    submitted_assign_ids = {s["assignment_id"] for s in all_submissions.data}

    # ── Index by id ─────────────────────────────────────
    subject_map  = {s["id"]: s for s in all_subjects.data}
    subject_name_map = {s["name"]: s for s in all_subjects.data}

    # videos/assignments grouped by topic_id
    videos_by_topic = {}
    for v in all_videos.data:
        videos_by_topic.setdefault(v["topic_id"], []).append(v["id"])

    assigns_by_topic = {}
    for a in all_assignments.data:
        assigns_by_topic.setdefault(a["topic_id"], []).append(a["id"])

    # topics grouped by subject_id
    topics_by_subject = {}
    for t in all_topics.data:
        topics_by_subject.setdefault(t["subject_id"], []).append(t)

    # ── Build result ────────────────────────────────────
    data = {}
    for subj_name in subjects:
        if subj_name not in subject_name_map:
            continue
        s = subject_name_map[subj_name]
        topics = sorted(
            topics_by_subject.get(s["id"], []),
            key=lambda x: x.get("order_index", 0)
        )

        subj_data = {
            "total_videos": 0, "completed_videos": 0,
            "total_assignments": 0, "completed_assignments": 0,
            "topics": []
        }

        for t in topics:
            vid_ids    = videos_by_topic.get(t["id"], [])
            assign_ids = assigns_by_topic.get(t["id"], [])

            comp_vids    = len([v for v in vid_ids    if v in completed_video_ids])
            comp_assigns = len([a for a in assign_ids if a in submitted_assign_ids])

            subj_data["total_videos"]          += len(vid_ids)
            subj_data["completed_videos"]      += comp_vids
            subj_data["total_assignments"]     += len(assign_ids)
            subj_data["completed_assignments"] += comp_assigns

            subj_data["topics"].append({
                "title":                t["title"],
                "total_videos":         len(vid_ids),
                "completed_videos":     comp_vids,
                "total_assignments":    len(assign_ids),
                "completed_assignments":comp_assigns,
            })

        data[subj_name] = subj_data
    return data


def get_streak(student_id):
    """Calculate streak — reuses already-fetched data, no extra calls."""
    progress = sb.table("student_progress").select("completed_at").eq(
        "student_id", student_id).eq("completed", True).execute()
    subs = sb.table("submissions").select("submitted_at").eq(
        "student_id", student_id).execute()

    active_dates = set()
    for p in progress.data:
        raw = p.get("completed_at")
        if raw:
            try:
                active_dates.add(
                    datetime.fromisoformat(raw.replace("Z","").split(".")[0]).date()
                )
            except: pass

    for s in subs.data:
        raw = s.get("submitted_at")
        if raw:
            try:
                active_dates.add(
                    datetime.fromisoformat(raw.replace("Z","").split(".")[0]).date()
                )
            except: pass

    streak = 0
    check = date.today()
    while check in active_dates:
        streak += 1
        check -= timedelta(days=1)

    return streak, sorted(active_dates)


def generate_study_plan(progress_data, exam_date, subjects, student_name):
    """Generate AI study plan using Groq."""
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    today = date.today()
    days_left = (exam_date - today).days

    summary = []
    for subj, d in progress_data.items():
        pct_v = int(d["completed_videos"] / d["total_videos"] * 100) if d["total_videos"] else 0
        pct_a = int(d["completed_assignments"] / d["total_assignments"] * 100) if d["total_assignments"] else 0
        incomplete_topics = [t["title"] for t in d["topics"]
                             if t["completed_videos"] < t["total_videos"]
                             or t["completed_assignments"] < t["total_assignments"]]
        summary.append({
            "subject": subj,
            "videos_done": f"{d['completed_videos']}/{d['total_videos']} ({pct_v}%)",
            "assignments_done": f"{d['completed_assignments']}/{d['total_assignments']} ({pct_a}%)",
            "incomplete_topics": incomplete_topics
        })
    max_days = min(days_left, 30)
    prompt = f"""You are an expert study planner for programming courses.

Student: {student_name}
Exam Date: {exam_date.strftime('%Y-%m-%d')} ({days_left} days left)
Subjects: {', '.join(subjects)}

Current Progress:
{json.dumps(summary, indent=2)}

Create a day-by-day study plan for the next {max_days} days (today: {today.strftime('%Y-%m-%d')}).
    Keep each day's tasks concise. Maximum {max_days} days in the plan array.

Rules:
- Cover all incomplete topics with videos, assignments, and cheatsheet reviews
- Add revision days every 5-6 days
- Add a full revision week before exam
- Keep daily study load realistic (max 3-4 tasks/day)
- Include rest/light days when needed
- On exam day, just put "EXAM DAY 🎯"

Return ONLY valid JSON, no extra text:
{{
  "plan": [
    {{
      "date": "YYYY-MM-DD",
      "day_label": "Day 1",
      "type": "study",
      "subject": "Python",
      "topic": "Topic name",
      "tasks": [
        {{"type": "video", "title": "Watch: topic videos", "duration": "45 min"}},
        {{"type": "assignment", "title": "Complete: assignment name", "duration": "30 min"}},
        {{"type": "cheatsheet", "title": "Review: cheatsheet", "duration": "15 min"}}
      ],
      "total_time": "90 min",
      "tip": "motivational tip for this day"
    }}
  ],
  "insights": [
    "Key insight about the student's progress",
    "Another insight or recommendation"
  ],
  "weekly_targets": {{
    "week1": "Focus description",
    "week2": "Focus description"
  }}
}}

Type can be: "study", "revision", "rest", "exam"
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=6000
    )

    raw = response.choices[0].message.content.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON found in response")
    raw = raw[start:end]

    # Fix truncated JSON by trimming to last complete day entry
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Find last complete plan entry (last complete closing brace of a day)
        last_good = raw.rfind('},\n')
        if last_good == -1:
            last_good = raw.rfind('}')
        # Close off the plan array and JSON object
        trimmed = raw[:last_good + 1] + '\n    ]\n}'
        try:
            return json.loads(trimmed)
        except json.JSONDecodeError:
            # Last resort: shorten plan array manually
            plan_end = raw.rfind('"plan"')
            if plan_end != -1:
                short = raw[:last_good + 1] + '\n    ],\n"insights": ["Stay consistent and follow the plan!"],\n"weekly_targets": {"week1": "Complete pending topics"}\n}'
                return json.loads(short)
            raise


# ═══════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════
tab1, tab2 = st.tabs([
    "📊 Progress Overview",
    "🗓 AI Study Plan"
])

# ═══════════════════════════════════════════════════════
# TAB 1 — PROGRESS OVERVIEW
# ═══════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📊 Your Learning Progress</div>', unsafe_allow_html=True)

    with st.spinner("Loading progress..."):
        progress_data = get_progress_data(student["id"], enrolled)

    # Overall metrics
    total_v = sum(d["total_videos"] for d in progress_data.values())
    done_v  = sum(d["completed_videos"] for d in progress_data.values())
    total_a = sum(d["total_assignments"] for d in progress_data.values())
    done_a  = sum(d["completed_assignments"] for d in progress_data.values())

    overall_pct = int(((done_v + done_a) / (total_v + total_a) * 100) if (total_v + total_a) > 0 else 0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎬 Videos Done", f"{done_v}/{total_v}",
                  delta=f"{int(done_v/total_v*100) if total_v else 0}%")
    with col2:
        st.metric("📝 Assignments Done", f"{done_a}/{total_a}",
                  delta=f"{int(done_a/total_a*100) if total_a else 0}%")
    with col3:
        st.metric("📚 Subjects Enrolled", len(enrolled))
    with col4:
        st.metric("🏆 Overall Progress", f"{overall_pct}%")

    st.write("")

    # Per-subject breakdown
    for subj_name, d in progress_data.items():
        icon = "🐍" if subj_name == "Python" else "⚡"
        color = "#3776AB" if subj_name == "Python" else "#00599C"

        pct_v = int(d["completed_videos"] / d["total_videos"] * 100) if d["total_videos"] else 0
        pct_a = int(d["completed_assignments"] / d["total_assignments"] * 100) if d["total_assignments"] else 0
        overall = int((d["completed_videos"] + d["completed_assignments"]) /
                      max(d["total_videos"] + d["total_assignments"], 1) * 100)

        st.markdown(f"""
        <div class="progress-subject">
            <h3 style="color:{color};margin:0 0 12px;">{icon} {subj_name}</h3>
            <div style="display:flex;gap:2rem;flex-wrap:wrap;">
                <div style="flex:1;min-width:200px;">
                    <div style="display:flex;justify-content:space-between;">
                        <span>🎬 Videos</span>
                        <strong>{d['completed_videos']}/{d['total_videos']} ({pct_v}%)</strong>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width:{pct_v}%;background:linear-gradient(90deg,{color},{color}99);"></div>
                    </div>
                </div>
                <div style="flex:1;min-width:200px;">
                    <div style="display:flex;justify-content:space-between;">
                        <span>📝 Assignments</span>
                        <strong>{d['completed_assignments']}/{d['total_assignments']} ({pct_a}%)</strong>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width:{pct_a}%;background:linear-gradient(90deg,#f093fb,#f5576c);"></div>
                    </div>
                </div>
            </div>
            <div style="margin-top:12px;">
                <div style="display:flex;justify-content:space-between;">
                    <span><strong>Overall</strong></span>
                    <strong>{overall}% Complete</strong>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{overall}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Topic-wise breakdown
        with st.expander(f"📌 Topic-wise breakdown for {subj_name}"):
            for t in d["topics"]:
                tv = int(t["completed_videos"] / t["total_videos"] * 100) if t["total_videos"] else 0
                ta = int(t["completed_assignments"] / t["total_assignments"] * 100) if t["total_assignments"] else 0
                status = "✅" if tv == 100 and ta == 100 else ("🔄" if tv > 0 or ta > 0 else "🔲")
                st.markdown(f"""
                **{status} {t['title']}**
                — Videos: `{t['completed_videos']}/{t['total_videos']}` 
                &nbsp;|&nbsp; Assignments: `{t['completed_assignments']}/{t['total_assignments']}`
                """)

    # Bar chart using st.bar_chart
    st.markdown('<div class="section-title">📈 Videos vs Assignments Completion</div>', unsafe_allow_html=True)

    try:
        import pandas as pd
        chart_rows = []
        for subj_name, d in progress_data.items():
            for t in d["topics"]:
                chart_rows.append({
                    "Topic": t["title"][:20],
                    "Videos %": int(t["completed_videos"] / t["total_videos"] * 100) if t["total_videos"] else 0,
                    "Assignments %": int(t["completed_assignments"] / t["total_assignments"] * 100) if t["total_assignments"] else 0,
                })
        if chart_rows:
            df = pd.DataFrame(chart_rows).set_index("Topic")
            st.bar_chart(df, height=300)
    except Exception as e:
        st.info("Install pandas for charts: `pip install pandas`")



# ═══════════════════════════════════════════════════════
# TAB 3 — AI STUDY PLAN
# ═══════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🗓 Generate Your AI Study Plan</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        exam_date_input = st.date_input(
            "📅 When is your exam?",
            value=date.today() + timedelta(days=30),
            min_value=date.today() + timedelta(days=1)
        )
    with col2:
        days_remaining = (exam_date_input - date.today()).days
        st.markdown(f"""
        <div class="exam-countdown" style="margin-top:8px;">
            <div style="font-size:0.9rem;opacity:0.9;">⏰ Days Until Exam</div>
            <div class="countdown-number">{days_remaining}</div>
            <div style="font-size:0.85rem;opacity:0.85;">{exam_date_input.strftime('%d %b %Y')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Subject filter for plan
    plan_subjects = st.multiselect(
        "📚 Include subjects in plan", enrolled, default=enrolled
    )

    generate_plan_btn = st.button(
        "🧠 Generate AI Study Plan", type="primary", use_container_width=True
    )

    if generate_plan_btn:
        if not plan_subjects:
            st.error("Please select at least one subject!")
        elif not os.getenv("GROQ_API_KEY"):
            st.error("GROQ_API_KEY not found in .env file!")
        else:
            with st.spinner("🤖 Building your personalized study plan..."):
                try:
                    if "progress_data" not in st.session_state:
                        st.session_state.progress_data = get_progress_data(student["id"], enrolled)

                    plan_result = generate_study_plan(
                        st.session_state.progress_data,
                        exam_date_input,
                        plan_subjects,
                        student["name"]
                    )
                    st.session_state.study_plan = plan_result
                    st.session_state.exam_date = exam_date_input
                    st.success("✅ Study plan generated!")
                except Exception as e:
                    st.error(f"Plan generation failed: {e}")

    # Display plan
    if "study_plan" in st.session_state and st.session_state.study_plan:
        plan = st.session_state.study_plan
        exam_dt = st.session_state.get("exam_date", exam_date_input)

        # Weekly targets
        if plan.get("weekly_targets"):
            st.markdown('<div class="section-title">🎯 Weekly Targets</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(plan["weekly_targets"]), 4))
            for i, (week, target) in enumerate(plan["weekly_targets"].items()):
                with cols[i % len(cols)]:
                    st.info(f"**{week.upper()}**\n\n{target}")

        # Day-by-day plan
        st.markdown('<div class="section-title">📅 Day-by-Day Schedule</div>', unsafe_allow_html=True)

        type_colors = {
            "study":    ("#667eea", ""),
            "revision": ("#f093fb", " revision"),
            "rest":     ("#a8edea", " rest"),
            "exam":     ("#f5576c", " exam"),
        }

        pill_map = {
            "video":      "pill-video",
            "assignment": "pill-assign",
            "cheatsheet": "pill-cheat",
            "revision":   "pill-revision",
        }
        icon_map = {
            "video":      "🎬",
            "assignment": "📝",
            "cheatsheet": "📄",
            "revision":   "🔁",
        }

        # Group by week
        days = plan.get("plan", [])
        weeks = {}
        for day in days:
            try:
                d = datetime.strptime(day["date"], "%Y-%m-%d").date()
                week_num = ((d - date.today()).days // 7) + 1
                week_num = max(1, week_num)
            except:
                week_num = 1
            weeks.setdefault(week_num, []).append(day)

        for week_num, week_days in sorted(weeks.items()):
            with st.expander(f"📅 Week {week_num}  ({len(week_days)} days)", expanded=(week_num == 1)):
                for day in week_days:
                    day_type = day.get("type", "study")
                    _, extra_class = type_colors.get(day_type, ("#667eea", ""))

                    # Build tasks pills
                    tasks_html = ""
                    tasks = day.get("tasks", [])
                    if tasks:
                        for task in tasks:
                            t_type = task.get("type", "video")
                            pill_cls = pill_map.get(t_type, "pill-video")
                            t_icon = icon_map.get(t_type, "📌")
                            title = task.get("title", "").strip()
                            duration = task.get("duration", "").strip()
                            if title:
                                tasks_html += f'<span class="task-pill {pill_cls}">{t_icon} {title} · {duration}</span>'
                    else:
                        # Rest/Exam day with no tasks
                        if day_type == "exam":
                            tasks_html = '<span class="task-pill pill-assign">🎯 EXAM DAY — Good luck!</span>'
                        elif day_type == "rest":
                            tasks_html = '<span class="task-pill pill-rest">😴 Take a break and recharge!</span>'
                        elif day_type == "revision":
                            tasks_html = '<span class="task-pill pill-revision">🔁 Revision Day</span>'
                        else:
                            tasks_html = '<span class="task-pill pill-cheat">📌 Light study day</span>'

                    # Tip — only show if non-empty string
                    import re
                    tip = str(day.get("tip", "") or "").strip()
                    tip = re.sub(r'<[^>]+>', '', tip).strip()
                    tip_html = f'<div style="margin-top:6px;font-size:12px;color:#64748b;">💬 {tip}</div>' if tip else ""

                    try:
                        d_obj = datetime.strptime(day["date"], "%Y-%m-%d").date()
                        date_str = d_obj.strftime("%a, %d %b")
                        is_today = d_obj == date.today()
                        today_badge = ' <span style="background:#f5576c;color:white;font-size:11px;padding:2px 8px;border-radius:10px;">TODAY</span>' if is_today else ""
                    except:
                        date_str = day.get("date", "")
                        today_badge = ""

                    # Clean tip — strip all HTML tags
                    tip_raw = str(day.get("tip", "") or "").strip()
                    tip_raw = re.sub(r'<[^>]+>', '', tip_raw).strip()
                    tip_raw = tip_raw.replace("&nbsp;", "").strip()
                    tip_section = f'<div style="margin-top:6px;font-size:12px;color:#64748b;">💬 {tip_raw}</div>' if tip_raw else ""

                    # Clean total_time
                    total_time = str(day.get("total_time", "") or "").strip()
                    total_time = re.sub(r'<[^>]+>', '', total_time).replace("&nbsp;", "").strip()
                    if not total_time or total_time == "0 min":
                        total_time = ""

                    # Clean subject/topic
                    subj_label  = re.sub(r'<[^>]+>', '', str(day.get("subject", day_type.upper()) or "")).strip()
                    topic_label = re.sub(r'<[^>]+>', '', str(day.get("topic", "") or "")).strip()

                    time_meta = f"⏱ {total_time} &nbsp;|&nbsp; {subj_label} &nbsp;|&nbsp; 📌 {topic_label}" if total_time else f"{subj_label} &nbsp;|&nbsp; 📌 {topic_label}"

                    st.markdown(f"""
                    <div class="plan-day-card{extra_class}">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                            <div>
                                <strong>{day.get('day_label','')}</strong>{today_badge}
                                &nbsp;<span style="color:#94a3b8;font-size:13px;">{date_str}</span>
                            </div>
                            <div style="font-size:12px;color:#64748b;">{time_meta}</div>
                        </div>
                        <div style="margin-top:8px;">{tasks_html}</div>
                        {tip_section}
                    </div>
                    """, unsafe_allow_html=True)

        # Download plan as text
        plan_text = f"STUDY PLAN — Exam: {exam_dt.strftime('%d %b %Y')}\n{'='*50}\n\n"
        for day in days:
            plan_text += f"{day.get('day_label','')} ({day.get('date','')}): {day.get('topic','')} — {day.get('total_time','')}\n"
            for task in day.get("tasks", []):
                plan_text += f"  • {task.get('title','')} ({task.get('duration','')})\n"
            if day.get("tip"):
                plan_text += f"  💬 {day['tip']}\n"
            plan_text += "\n"

        st.download_button(
            "⬇️ Download Study Plan",
            data=plan_text,
            file_name="my_study_plan.txt",
            mime="text/plain"
        )