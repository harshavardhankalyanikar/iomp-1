import streamlit as st
import json, os, re
from datetime import datetime, date, timedelta
from utils.db import get_supabase
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="AI Study Plan", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
* { font-family: 'DM Sans', sans-serif; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

.stApp { background: #07071a !important; }
.block-container { background: transparent !important; padding-top: 1.5rem !important; }

.hero-banner {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    border: 1px solid rgba(102,126,234,0.2);
    padding: 2rem 2.5rem; border-radius: 20px; color: white;
    margin-bottom: 1.5rem; position: relative; overflow: hidden;
}
.hero-banner::before {
    content:''; position:absolute; top:-50%; left:-20%; width:60%; height:200%;
    background: radial-gradient(ellipse, rgba(102,126,234,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-banner h1 { font-size:1.9rem; margin:0; position:relative; z-index:1; color:white !important; }
.hero-banner p  { opacity:0.8; margin:6px 0 0; position:relative; z-index:1; color:rgba(255,255,255,0.8) !important; }

.exam-countdown {
    background: linear-gradient(135deg, #7c2d92, #c026d3);
    border-radius: 14px; padding: 1.2rem;
    color: white; text-align: center;
    box-shadow: 0 6px 20px rgba(192,38,211,0.35);
}
.countdown-number { font-family:'Syne',sans-serif; font-size:2.8rem; font-weight:800; line-height:1; }

/* ── Task row with time ─────────────────────── */
.task-row {
    display: flex; align-items: flex-start; gap: 12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 10px 14px;
    margin-bottom: 6px; transition: border-color 0.2s;
}
.task-row:hover { border-color: rgba(102,126,234,0.3); }
.task-time-badge {
    background: rgba(102,126,234,0.15);
    border: 1px solid rgba(102,126,234,0.3);
    color: #a5b4fc; font-size: 11px; font-weight: 700;
    padding: 3px 8px; border-radius: 8px;
    white-space: nowrap; flex-shrink: 0; margin-top: 2px;
    font-family: 'Syne', sans-serif;
}
.task-content { flex: 1; }
.task-title { color: white; font-weight: 600; font-size: 14px; margin-bottom: 2px; }
.task-sub   { color: rgba(200,208,231,0.5); font-size: 12px; }
.task-icon  { font-size: 1.2rem; flex-shrink: 0; margin-top: 2px; }

/* ── Day card ───────────────────────────────── */
.day-header {
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; margin-bottom: 10px;
}
.day-label { font-family:'Syne',sans-serif; font-weight:800; color:white; font-size:1rem; }
.day-date  { color:rgba(200,208,231,0.5); font-size:13px; margin-left:8px; }
.day-meta  { font-size:12px; color:rgba(200,208,231,0.4); }
.today-badge { background:#f5576c; color:white; font-size:10px; padding:2px 8px; border-radius:10px; margin-left:6px; }
.done-badge  { background:rgba(34,197,94,0.2); color:#4ade80; font-size:10px; padding:2px 8px; border-radius:10px; margin-left:6px; border:1px solid rgba(34,197,94,0.3); }

/* ── Progress ───────────────────────────────── */
.plan-progress-bar  { background:rgba(255,255,255,0.08); border-radius:999px; height:10px; overflow:hidden; margin:6px 0; }
.plan-progress-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,#667eea,#22c55e); transition:width 0.6s ease; }

/* ── Summary cards ───────────────────────────── */
.summary-card  { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:14px; padding:1.2rem; text-align:center; }
.summary-num   { font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; background:linear-gradient(135deg,#667eea,#22c55e); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.summary-label { color:rgba(200,208,231,0.5); font-size:12px; margin-top:2px; }

.section-title { font-family:'Syne',sans-serif; font-size:1.15rem; font-weight:700; background:linear-gradient(135deg,#a5b4fc,#e879f9); -webkit-background-clip:text; -webkit-text-fill-color:transparent; display:block; margin:1.4rem 0 0.8rem; }

/* ── Nav link buttons ───────────────────────── */
.stButton > button {
    background: linear-gradient(135deg,#667eea,#764ba2) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 12px !important; padding: 4px 12px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 14px rgba(102,126,234,0.4) !important; }

/* ── Tabs ───────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { background:rgba(255,255,255,0.03) !important; border-radius:12px !important; padding:4px !important; border:1px solid rgba(255,255,255,0.06) !important; }
.stTabs [data-baseweb="tab"] { color:rgba(200,208,231,0.6) !important; border-radius:9px !important; font-weight:500 !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#667eea,#764ba2) !important; color:white !important; font-weight:700 !important; }

/* Alerts */
[data-testid="stAlert"] { border-radius:12px !important; }
.stSuccess { background:rgba(34,197,94,0.1) !important; border-left:4px solid #22c55e !important; color:#86efac !important; }
.stInfo    { background:rgba(99,102,241,0.1) !important; border-left:4px solid #6366f1 !important; color:#a5b4fc !important; }
.stWarning { background:rgba(245,158,11,0.1) !important; border-left:4px solid #f59e0b !important; color:#fcd34d !important; }
.stError   { background:rgba(239,68,68,0.1) !important;  border-left:4px solid #ef4444 !important; color:#fca5a5 !important; }

html, body, p, span, div, label { color: #c8d0e7 !important; }
h1 { color:#ffffff !important; } h2 { color:#e8eaf6 !important; } h3 { color:#dde1f7 !important; }
[data-testid="stMetricValue"] { color:white !important; font-family:'Syne',sans-serif !important; font-size:1.8rem !important; font-weight:800 !important; }
[data-testid="stMetricLabel"] { color:rgba(200,208,231,0.6) !important; }
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div { background:rgba(255,255,255,0.04) !important; color:#e8eaf6 !important; border:1px solid rgba(102,126,234,0.25) !important; border-radius:10px !important; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0d0b2e,#130f3f,#0a0a1f) !important; border-right:1px solid rgba(102,126,234,0.15) !important; }
hr { border-color:rgba(255,255,255,0.07) !important; }
::-webkit-scrollbar { width:5px; } ::-webkit-scrollbar-track { background:#07071a; } ::-webkit-scrollbar-thumb { background:#667eea; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ─── Auth Guard ────────────────────────────────────────
if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student  = st.session_state.student
sb       = get_supabase()
enrolled = student.get("enrolled_subjects", [])

st.markdown("""
<div class="hero-banner">
    <div>
        <h1>🧠 AI Study Plan</h1>
        <p>Generate a smart timed plan for any duration — 1 day to 30 days — with clickable tasks</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not enrolled:
    st.warning("Please enroll in a subject first from **My Subjects**.")
    st.stop()


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def get_all_content(student_id, subjects):
    """Bulk fetch all videos, assignments, topics with completion status."""
    all_subjects    = sb.table("subjects").select("*").execute()
    all_topics      = sb.table("topics").select("*").execute()
    all_videos      = sb.table("videos").select("*").execute()
    all_assignments = sb.table("assignments").select("*").execute()
    all_progress    = sb.table("student_progress").select("video_id").eq(
                        "student_id", student_id).eq("completed", True).execute()
    all_submissions = sb.table("submissions").select("assignment_id").eq(
                        "student_id", student_id).execute()

    completed_vids  = {p["video_id"]      for p in all_progress.data}
    submitted_assgn = {s["assignment_id"] for s in all_submissions.data}
    subj_name_map   = {s["name"]: s       for s in all_subjects.data}

    videos_by_topic  = {}
    for v in all_videos.data:
        videos_by_topic.setdefault(v["topic_id"], []).append(v)
    assigns_by_topic = {}
    for a in all_assignments.data:
        assigns_by_topic.setdefault(a["topic_id"], []).append(a)
    topics_by_subj   = {}
    for t in all_topics.data:
        topics_by_subj.setdefault(t["subject_id"], []).append(t)

    content = {}
    for subj_name in subjects:
        if subj_name not in subj_name_map:
            continue
        s      = subj_name_map[subj_name]
        topics = sorted(topics_by_subj.get(s["id"], []),
                        key=lambda x: x.get("order_index", 0))
        subj_content = {"topics": []}
        for t in topics:
            vids    = videos_by_topic.get(t["id"], [])
            assigns = assigns_by_topic.get(t["id"], [])
            pending_vids    = [v for v in vids    if v["id"] not in completed_vids]
            pending_assigns = [a for a in assigns if a["id"] not in submitted_assgn]
            subj_content["topics"].append({
                "id":              t["id"],
                "title":           t["title"],
                "subject":         subj_name,
                "pending_videos":  pending_vids,
                "pending_assigns": pending_assigns,
                "done_vids":       len(vids) - len(pending_vids),
                "total_vids":      len(vids),
                "done_assigns":    len(assigns) - len(pending_assigns),
                "total_assigns":   len(assigns),
            })
        content[subj_name] = subj_content
    return content


def build_content_summary(content):
    """Build a compact text summary for the AI prompt."""
    lines = []
    for subj, sc in content.items():
        for t in sc["topics"]:
            pv = len(t["pending_videos"])
            pa = len(t["pending_assigns"])
            if pv > 0 or pa > 0:
                vids_list    = [v["title"][:40] for v in t["pending_videos"][:3]]
                assigns_list = [a["title"][:40] for a in t["pending_assigns"][:2]]
                lines.append(
                    f"{subj} | {t['title']}: "
                    f"{pv} pending videos ({', '.join(vids_list)}), "
                    f"{pa} pending assignments ({', '.join(assigns_list)})"
                )
    return "\n".join(lines) if lines else "All content completed!"


def generate_study_plan(content, exam_date, subjects, student_name, days_count):
    """Generate AI plan — handles 1-day to 30-day durations with time slots."""
    from groq import Groq
    client  = Groq(api_key=os.getenv("GROQ_API_KEY"))
    today   = date.today()
    is_short = days_count <= 3
    content_summary = build_content_summary(content)

    if is_short:
        prompt = f"""Create an INTENSIVE {days_count}-day study plan for {student_name}.
Exam: {exam_date}. Today: {today}.
Available content to cover:
{content_summary}

IMPORTANT: Since only {days_count} day(s) available, create a TIMED HOURLY schedule.
Each task MUST have a specific start_time like "9:00 AM", "10:30 AM" etc.
Pack as many tasks as possible in study sessions (8 AM - 10 PM).
Prioritize incomplete/pending topics first.

Return ONLY valid JSON — no other text:
{{
  "plan": [
    {{
      "date": "{today.strftime('%Y-%m-%d')}",
      "day_label": "Day 1",
      "type": "study",
      "subject": "Python",
      "topic": "Variables & Data Types",
      "total_time": "8 hours",
      "tip": "Take 10-min breaks every hour",
      "tasks": [
        {{
          "type": "video",
          "title": "Watch: Python basics intro",
          "topic_ref": "Introduction to Python",
          "subject_ref": "Python",
          "start_time": "9:00 AM",
          "duration": "45 min",
          "description": "Watch the video on Python basics"
        }},
        {{
          "type": "assignment",
          "title": "Solve: Variables assignment",
          "topic_ref": "Introduction to Python",
          "subject_ref": "Python",
          "start_time": "9:50 AM",
          "duration": "30 min",
          "description": "Complete the assignment on variables"
        }},
        {{
          "type": "revision",
          "title": "Quick revision: OOP concepts",
          "topic_ref": "OOP in Python",
          "subject_ref": "Python",
          "start_time": "10:30 AM",
          "duration": "20 min",
          "description": "Review cheatsheet and notes"
        }}
      ]
    }}
  ],
  "strategy": "Focus on high-priority incomplete topics first. Use Pomodoro technique.",
  "weekly_targets": {{"day1": "Cover core topics", "day2": "Practice & revision"}}
}}"""
    else:
        max_days = min(days_count, 30)
        prompt = f"""Create a {max_days}-day study plan for {student_name}.
Exam: {exam_date}. Today: {today}.
Pending content:
{content_summary}

Rules:
- Rest day every 6-7 days
- Revision day every 5 days
- Last 2 days = revision only, exam day type="exam"
- Each task must have start_time (like "9:00 AM")
- Max 4 tasks per day
- Max {max_days} days total

Return ONLY valid JSON:
{{
  "plan": [
    {{
      "date": "YYYY-MM-DD",
      "day_label": "Day 1",
      "type": "study",
      "subject": "Python",
      "topic": "Topic name",
      "total_time": "3 hours",
      "tip": "short motivational tip",
      "tasks": [
        {{
          "type": "video",
          "title": "Watch: topic intro video",
          "topic_ref": "Introduction to Python",
          "subject_ref": "Python",
          "start_time": "9:00 AM",
          "duration": "45 min",
          "description": "Core video for this topic"
        }}
      ]
    }}
  ],
  "strategy": "Overall approach summary",
  "weekly_targets": {{"week1": "Basics", "week2": "Practice"}}
}}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3, max_tokens=7000
    )
    raw   = resp.choices[0].message.content.strip()
    start = raw.find("{"); end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON found in response")
    raw = raw[start:end]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        last = raw.rfind('},\n')
        if last == -1: last = raw.rfind('}')
        try:
            return json.loads(raw[:last+1] + '\n  ]\n}')
        except:
            raise


def save_plan_to_db(student_id, exam_date, plan_data):
    try:
        existing = sb.table("study_plans").select("id").eq("student_id", student_id).execute()
        if existing.data:
            sb.table("study_plans").delete().eq("student_id", student_id).execute()
        result = sb.table("study_plans").insert({
            "student_id": student_id,
            "exam_date":  str(exam_date),
            "plan_data":  plan_data
        }).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as e:
        st.warning(f"Could not save to DB: {e}")
        return None


def load_plan_from_db(student_id):
    try:
        r = sb.table("study_plans").select("*").eq(
            "student_id", student_id).order("created_at", desc=True).limit(1).execute()
        return r.data[0] if r.data else None
    except:
        return None


def get_completed_days(plan_id):
    try:
        r = sb.table("study_plan_progress").select("day_date").eq(
            "plan_id", plan_id).eq("completed", True).execute()
        return {row["day_date"] for row in r.data}
    except:
        return set()


def toggle_day(plan_id, student_id, day_date_str, currently_done):
    try:
        ex = sb.table("study_plan_progress").select("id").eq(
            "plan_id", plan_id).eq("day_date", day_date_str).execute()
        if ex.data:
            sb.table("study_plan_progress").update({
                "completed":    not currently_done,
                "completed_at": str(datetime.now()) if not currently_done else None
            }).eq("id", ex.data[0]["id"]).execute()
        else:
            sb.table("study_plan_progress").insert({
                "plan_id":      plan_id,
                "student_id":   student_id,
                "day_date":     day_date_str,
                "completed":    True,
                "completed_at": str(datetime.now())
            }).execute()
    except Exception as e:
        st.error(f"Progress update failed: {e}")


def find_nav_target(task, content):
    """Find the matching topic/video/assignment in the DB content for navigation."""
    t_type      = task.get("type", "")
    topic_ref   = re.sub(r'<[^>]+>', '', str(task.get("topic_ref", "") or "")).strip().lower()
    subject_ref = re.sub(r'<[^>]+>', '', str(task.get("subject_ref", "") or "")).strip()
    task_title  = re.sub(r'<[^>]+>', '', str(task.get("title", "") or "")).strip().lower()

    if not subject_ref or subject_ref not in content:
        # Try to find subject by scanning
        for s in content:
            if s.lower() in task_title or s.lower() in topic_ref:
                subject_ref = s
                break

    subj_content = content.get(subject_ref, {})
    topics       = subj_content.get("topics", [])

    # Find best matching topic
    best_topic = None
    for t in topics:
        if topic_ref and (topic_ref in t["title"].lower() or
                          t["title"].lower() in topic_ref):
            best_topic = t
            break
    if not best_topic and topics:
        best_topic = topics[0]

    return {
        "subject": subject_ref,
        "topic":   best_topic["title"] if best_topic else "",
        "type":    t_type,
    }


# ─── Load saved plan ───────────────────────────────────
if "plan_loaded" not in st.session_state:
    saved = load_plan_from_db(student["id"])
    if saved:
        st.session_state.study_plan = saved["plan_data"]
        st.session_state.plan_id    = saved["id"]
        try:
            st.session_state.exam_date = date.fromisoformat(saved["exam_date"])
        except:
            st.session_state.exam_date = date.today() + timedelta(days=30)
    st.session_state.plan_loaded = True


# ═══════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["🗓 My Plan & Progress", "✨ Generate New Plan"])


# ───────────────────────────────────────────────────────
# TAB 1 — VIEW + TRACK
# ───────────────────────────────────────────────────────
with tab1:
    if "study_plan" not in st.session_state or not st.session_state.study_plan:
        st.info("🧠 No study plan yet! Switch to **✨ Generate New Plan** to create one.")
    else:
        plan    = st.session_state.study_plan
        plan_id = st.session_state.get("plan_id")
        exam_dt = st.session_state.get("exam_date", date.today() + timedelta(days=30))
        days    = plan.get("plan", [])

        completed_days = get_completed_days(plan_id) if plan_id else set()
        content        = get_all_content(student["id"], enrolled)

        total_days   = len(days)
        study_days   = len([d for d in days if d.get("type") not in ("rest","exam")])
        done_count   = len(completed_days)
        pct_done     = int(done_count / max(total_days, 1) * 100)
        days_to_exam = max((exam_dt - date.today()).days, 0)
        is_short     = total_days <= 3

        # ── Strategy banner (for short plans) ─────────
        if plan.get("strategy"):
            st.markdown(f"""
            <div style="background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.25);
                        border-radius:12px;padding:12px 16px;margin-bottom:1rem;">
                <span style="font-size:12px;color:#c084fc;font-weight:700;">📋 STRATEGY</span><br>
                <span style="color:rgba(200,208,231,0.8);font-size:13px;">{plan['strategy']}</span>
            </div>
            """, unsafe_allow_html=True)

        # ── Summary metrics ────────────────────────────
        st.markdown('<span class="section-title">📊 Plan Overview</span>',
                    unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="summary-card"><div class="summary-num">{done_count}/{total_days}</div><div class="summary-label">✅ Days Completed</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="summary-card"><div class="summary-num">{pct_done}%</div><div class="summary-label">📈 Plan Progress</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="summary-card"><div class="summary-num">{study_days}</div><div class="summary-label">📚 Study Days</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="summary-card"><div class="summary-num">{days_to_exam}</div><div class="summary-label">⏰ Days to Exam</div></div>', unsafe_allow_html=True)

        st.write("")

        # Overall progress bar
        st.markdown(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);'
            'border-radius:14px;padding:1.2rem;margin-bottom:1rem;">'
            '<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
            '<span style="color:rgba(200,208,231,0.85);font-weight:600;">Overall Plan Completion</span>'
            '<span style="color:white;font-weight:700;">' + str(pct_done) + '%</span>'
            '</div>'
            '<div class="plan-progress-bar"><div class="plan-progress-fill" style="width:' + str(pct_done) + '%;"></div></div>'
            '<div style="display:flex;justify-content:space-between;margin-top:6px;">'
            '<span style="font-size:12px;color:rgba(200,208,231,0.4);">' + str(done_count) + ' days done</span>'
            '<span style="font-size:12px;color:rgba(200,208,231,0.4);">' + str(total_days - done_count) + ' remaining</span>'
            '</div></div>',
            unsafe_allow_html=True
        )

        # Weekly targets
        if plan.get("weekly_targets"):
            st.markdown('<span class="section-title">🎯 ' + ("Daily Targets" if is_short else "Weekly Targets") + '</span>', unsafe_allow_html=True)
            wt    = plan["weekly_targets"]
            wcols = st.columns(min(len(wt), 4))
            for i, (wk, tgt) in enumerate(wt.items()):
                with wcols[i % len(wcols)]:
                    st.info(f"**{wk.upper()}**\n\n{tgt}")

        st.markdown('<span class="section-title">📅 ' + ("Hourly Schedule" if is_short else "Day-by-Day Schedule") + '</span>', unsafe_allow_html=True)

        border_map = {
            "study":    "#667eea",
            "revision": "#a855f7",
            "rest":     "#22c55e",
            "exam":     "#f5576c"
        }
        type_icon_map = {
            "video":      "🎬",
            "assignment": "📝",
            "cheatsheet": "📄",
            "revision":   "🔁",
            "rest":       "😴",
            "break":      "☕",
        }
        type_color_map = {
            "video":      ("#667eea", "rgba(59,130,246,0.12)",  "rgba(59,130,246,0.3)"),
            "assignment": ("#f87171", "rgba(239,68,68,0.12)",   "rgba(239,68,68,0.3)"),
            "cheatsheet": ("#fbbf24", "rgba(245,158,11,0.12)",  "rgba(245,158,11,0.3)"),
            "revision":   ("#c084fc", "rgba(168,85,247,0.12)",  "rgba(168,85,247,0.3)"),
            "rest":       ("#4ade80", "rgba(34,197,94,0.12)",   "rgba(34,197,94,0.3)"),
            "break":      ("#94a3b8", "rgba(148,163,184,0.12)", "rgba(148,163,184,0.3)"),
        }

        # Group by week (or show flat for short plans)
        if is_short:
            day_groups = {1: days}
        else:
            day_groups = {}
            for day in days:
                try:
                    d_obj    = datetime.strptime(day["date"], "%Y-%m-%d").date()
                    week_num = max(1, ((d_obj - date.today()).days // 7) + 1)
                except:
                    week_num = 1
                day_groups.setdefault(week_num, []).append(day)

        day_index = 0
        for group_num, group_days in sorted(day_groups.items()):
            w_done  = sum(1 for d in group_days if d.get("date") in completed_days)
            w_total = len(group_days)
            w_pct   = int(w_done / max(w_total, 1) * 100)
            group_label = (f"📅 Day {group_num}" if is_short
                           else f"📅 Week {group_num}  ({w_total} days) — {w_pct}% complete")

            with st.expander(group_label, expanded=True):
                if not is_short:
                    st.markdown(
                        '<div class="plan-progress-bar" style="margin-bottom:12px;">'
                        '<div class="plan-progress-fill" style="width:' + str(w_pct) + '%;"></div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

                for day in group_days:
                    day_index += 1
                    day_type  = day.get("type", "study")
                    day_date  = day.get("date", "")
                    is_done   = day_date in completed_days
                    is_today  = False

                    try:
                        d_obj    = datetime.strptime(day_date, "%Y-%m-%d").date()
                        is_today = d_obj == date.today()
                        date_str = d_obj.strftime("%A, %d %b %Y") if is_short else d_obj.strftime("%a, %d %b")
                    except:
                        date_str = day_date

                    border_color = border_map.get(day_type, "#667eea")
                    day_label    = re.sub(r'<[^>]+>', '', str(day.get("day_label",""))).strip()
                    total_time   = re.sub(r'<[^>]+>', '', str(day.get("total_time","") or "")).replace("&nbsp;","").strip()
                    subj_label   = re.sub(r'<[^>]+>', '', str(day.get("subject", "") or "")).strip()
                    tip_raw      = re.sub(r'<[^>]+>', '', str(day.get("tip","") or "")).replace("&nbsp;","").strip()

                    # Badges
                    badges_html = ""
                    if is_today: badges_html += '<span class="today-badge">TODAY</span>'
                    if is_done:  badges_html += '<span class="done-badge">✓ DONE</span>'

                    # Card style based on state
                    if is_done:
                        card_bg     = "rgba(34,197,94,0.04)"
                        card_border = "1px solid rgba(34,197,94,0.2)"
                        text_fade   = "opacity:0.6;"
                    elif is_today:
                        card_bg     = "rgba(102,126,234,0.07)"
                        card_border = "1px solid rgba(102,126,234,0.35)"
                        text_fade   = ""
                    else:
                        card_bg     = "rgba(255,255,255,0.03)"
                        card_border = "1px solid rgba(255,255,255,0.07)"
                        text_fade   = ""

                    # Day header
                    meta_parts = []
                    if total_time: meta_parts.append("⏱ " + total_time)
                    if subj_label: meta_parts.append(subj_label)
                    meta_str = " | ".join(meta_parts)

                    header_html = (
                        '<div style="background:' + card_bg + ';border:' + card_border + ';'
                        'border-left:4px solid ' + border_color + ';'
                        'border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.8rem;">'
                        '<div class="day-header" style="' + text_fade + '">'
                        '<div>'
                        '<span class="day-label">' + day_label + '</span>'
                        + badges_html +
                        '<span class="day-date">' + date_str + '</span>'
                        '</div>'
                        '<span class="day-meta">' + meta_str + '</span>'
                        '</div>'
                    )
                    if tip_raw:
                        header_html += (
                            '<div style="font-size:12px;color:rgba(200,208,231,0.45);'
                            'margin-bottom:10px;padding-bottom:10px;'
                            'border-bottom:1px solid rgba(255,255,255,0.06);">'
                            '💬 ' + tip_raw + '</div>'
                        )
                    header_html += '</div>'
                    st.markdown(header_html, unsafe_allow_html=True)

                    # ── TASKS with time slots & nav ────────────
                    tasks = day.get("tasks", [])
                    if tasks:
                        for t_idx, task in enumerate(tasks):
                            t_type      = task.get("type", "video")
                            t_icon      = type_icon_map.get(t_type, "📌")
                            t_color, t_bg, t_bdr = type_color_map.get(
                                t_type, ("#a5b4fc", "rgba(102,126,234,0.12)", "rgba(102,126,234,0.3)"))
                            t_title     = re.sub(r'<[^>]+>', '', str(task.get("title",""))).strip()
                            t_start     = re.sub(r'<[^>]+>', '', str(task.get("start_time","") or "")).strip()
                            t_dur       = re.sub(r'<[^>]+>', '', str(task.get("duration","") or "")).strip()
                            t_desc      = re.sub(r'<[^>]+>', '', str(task.get("description","") or "")).strip()
                            t_topic_ref = str(task.get("topic_ref","") or "").strip()
                            t_subj_ref  = str(task.get("subject_ref","") or "").strip()

                            time_badge = (
                                '<span style="background:rgba(102,126,234,0.15);'
                                'border:1px solid rgba(102,126,234,0.3);'
                                'color:#a5b4fc;font-size:11px;font-weight:700;'
                                'padding:3px 8px;border-radius:8px;white-space:nowrap;'
                                'flex-shrink:0;margin-top:2px;">'
                                + (t_start if t_start else t_dur) +
                                '</span>'
                            )

                            task_row_html = (
                                '<div style="display:flex;align-items:flex-start;gap:12px;'
                                'background:' + t_bg + ';'
                                'border:1px solid ' + t_bdr + ';'
                                'border-radius:12px;padding:10px 14px;'
                                'margin-bottom:6px;">'
                                '<span style="font-size:1.1rem;flex-shrink:0;margin-top:2px;">' + t_icon + '</span>'
                                '<div style="flex:1;">'
                                '<div style="color:white;font-weight:600;font-size:14px;margin-bottom:2px;">'
                                + t_title +
                                '</div>'
                                + ('<div style="color:rgba(200,208,231,0.5);font-size:12px;">' + t_desc + '</div>' if t_desc else '') +
                                ('<div style="color:rgba(200,208,231,0.4);font-size:11px;margin-top:2px;">📌 ' + t_topic_ref + ' · ⏱ ' + t_dur + '</div>' if t_topic_ref and t_dur else '') +
                                '</div>'
                                + time_badge +
                                '</div>'
                            )
                            st.markdown(task_row_html, unsafe_allow_html=True)

                            # Navigation button
                            if t_type in ("video", "assignment", "cheatsheet") and t_topic_ref:
                                nav = find_nav_target(task, content)
                                nav_label_map = {
                                    "video":      "🎬 Go to Videos",
                                    "assignment": "📝 Go to Assignments",
                                    "cheatsheet": "📄 Go to Cheatsheets",
                                }
                                nav_page_map = {
                                    "video":      "Videos",
                                    "assignment": "Assignments",
                                    "cheatsheet": "Cheatsheets",
                                }
                                btn_label = nav_label_map.get(t_type, "➡ Go")
                                nav_page  = nav_page_map.get(t_type, "Videos")

                                btn_col, _ = st.columns([1, 4])
                                with btn_col:
                                    if st.button(
                                        btn_label,
                                        key=f"nav_{day_index}_{t_idx}",
                                        use_container_width=True
                                    ):
                                        # Store pre-selected subject/topic for the target page
                                        st.session_state["nav_subject"] = nav["subject"] or (enrolled[0] if enrolled else "")
                                        st.session_state["nav_topic"]   = nav["topic"]
                                        st.session_state["nav_page"]    = nav_page
                                        st.rerun()

                    else:
                        # Rest / Exam day
                        fallback_map = {
                            "rest":     ("😴", "Take a proper rest. Sleep well, hydrate, and recharge.", "rgba(34,197,94,0.08)", "rgba(34,197,94,0.25)"),
                            "exam":     ("🎯", "EXAM DAY! Trust your preparation. Stay calm, read questions carefully.", "rgba(239,68,68,0.08)", "rgba(239,68,68,0.3)"),
                            "revision": ("🔁", "Full revision day — review all your notes and cheatsheets.", "rgba(168,85,247,0.08)", "rgba(168,85,247,0.25)"),
                        }
                        fb_icon, fb_msg, fb_bg, fb_bdr = fallback_map.get(day_type, ("📌", "Study day.", "rgba(255,255,255,0.03)", "rgba(255,255,255,0.07)"))
                        st.markdown(
                            '<div style="background:' + fb_bg + ';border:1px solid ' + fb_bdr + ';'
                            'border-radius:12px;padding:12px 16px;display:flex;gap:10px;align-items:center;">'
                            '<span style="font-size:1.5rem;">' + fb_icon + '</span>'
                            '<span style="color:rgba(200,208,231,0.8);font-size:14px;">' + fb_msg + '</span>'
                            '</div>',
                            unsafe_allow_html=True
                        )

                    # Mark done button
                    if plan_id:
                        st.write("")
                        done_col, _ = st.columns([1, 5])
                        with done_col:
                            btn_lbl = "↩ Undo" if is_done else "✅ Mark Day Done"
                            if st.button(btn_lbl, key=f"tog_{day_index}",
                                         type="secondary" if is_done else "primary",
                                         use_container_width=True):
                                toggle_day(plan_id, student["id"], day_date, is_done)
                                st.rerun()

                    st.markdown("---")

        # Download
        plan_text = f"MY STUDY PLAN — Exam: {exam_dt.strftime('%d %b %Y')}\n{'='*50}\n\n"
        for day in days:
            tick = "✅" if day.get("date") in completed_days else "🔲"
            plan_text += f"{tick} {day.get('day_label','')} ({day.get('date','')})\n"
            for task in day.get("tasks", []):
                start = task.get("start_time","")
                dur   = task.get("duration","")
                plan_text += f"  {task.get('type','').upper():<12} {start:<10} {task.get('title','')} ({dur})\n"
            plan_text += "\n"
        st.download_button("⬇️ Download Plan", data=plan_text,
                           file_name="study_plan.txt", mime="text/plain")


# ───────────────────────────────────────────────────────
# TAB 2 — GENERATE NEW PLAN
# ───────────────────────────────────────────────────────
with tab2:
    st.markdown('<span class="section-title">✨ Generate Your AI Study Plan</span>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        plan_mode = st.radio(
            "📅 How do you want to specify duration?",
            ["Pick exam date", "Enter number of days"],
            horizontal=True
        )
        if plan_mode == "Pick exam date":
            exam_date_input = st.date_input(
                "Exam Date",
                value=date.today() + timedelta(days=30),
                min_value=date.today() + timedelta(days=1)
            )
            days_count = (exam_date_input - date.today()).days
        else:
            days_count = st.number_input(
                "How many days to prepare?",
                min_value=1, max_value=90, value=7, step=1
            )
            exam_date_input = date.today() + timedelta(days=days_count)

        plan_subjects = st.multiselect("📚 Subjects to include", enrolled, default=enrolled)

    with col2:
        st.markdown(f"""
        <div class="exam-countdown" style="margin-top:8px;">
            <div style="font-size:0.85rem;opacity:0.85;">⏰ Days to Prepare</div>
            <div class="countdown-number">{days_count}</div>
            <div style="font-size:0.8rem;opacity:0.75;">Exam: {exam_date_input.strftime('%d %b %Y')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if days_count <= 3:
            st.markdown("""
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                        border-radius:10px;padding:10px 14px;font-size:13px;color:#fca5a5;">
                ⚡ <strong>Intensive Mode</strong> — Short time detected!<br>
                Will generate an hourly timed schedule to maximize your preparation.
            </div>
            """, unsafe_allow_html=True)
        elif days_count <= 7:
            st.markdown("""
            <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);
                        border-radius:10px;padding:10px 14px;font-size:13px;color:#fcd34d;">
                🔥 <strong>Focused Mode</strong> — 1 week plan with daily goals.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);
                        border-radius:10px;padding:10px 14px;font-size:13px;color:#86efac;">
                ✅ <strong>Full Plan Mode</strong> — Structured multi-week schedule with rest days.
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    if "study_plan" in st.session_state and st.session_state.study_plan:
        st.warning("⚠️ You have an existing plan. Generating a new one will replace it and reset progress.")

    if st.button("🧠 Generate AI Study Plan", type="primary", use_container_width=True):
        if not plan_subjects:
            st.error("Please select at least one subject!")
        elif not os.getenv("GROQ_API_KEY"):
            st.error("GROQ_API_KEY not found in .env file!")
        else:
            with st.spinner("🤖 Generating your personalized plan with timings..."):
                try:
                    content = get_all_content(student["id"], enrolled)
                    result  = generate_study_plan(
                        content, exam_date_input, plan_subjects,
                        student["name"], days_count
                    )
                    new_id  = save_plan_to_db(student["id"], exam_date_input, result)
                    st.session_state.study_plan  = result
                    st.session_state.plan_id     = new_id
                    st.session_state.exam_date   = exam_date_input
                    st.session_state.plan_loaded = True
                    n = len(result.get("plan", []))
                    st.success(f"✅ {n}-day plan generated & saved!")
                    st.info("👈 Switch to **My Plan & Progress** tab to view and track it!")
                except Exception as e:
                    st.error(f"Generation failed: {e}")
