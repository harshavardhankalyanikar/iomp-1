
import streamlit as st
import os
import re
from datetime import datetime, date, timedelta
from utils.db import get_supabase
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
    * { font-family: 'DM Sans', sans-serif; }
    h1,h2,h3 { font-family: 'Syne', sans-serif; }

    .hero-banner {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.2rem 2rem; border-radius: 20px; color: white;
        margin-bottom: 1.5rem; position: relative; overflow: hidden;
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

    [data-testid="stMetricValue"] {
        color: white !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1.8rem !important; font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] { color: rgba(255,255,255,0.6) !important; font-size: 13px !important; }
    [data-testid="stMetricDelta"]  { color: #43e97b !important; }

    .subject-card {
        background: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 1.4rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border-left: 5px solid #667eea;
        margin-bottom: 1rem; color: white;
    }
    .subject-card h3  { color: white !important; margin: 0 0 6px; font-family:'Syne',sans-serif; }
    .subject-card p   { color: rgba(255,255,255,0.6) !important; margin: 4px 0; font-size:14px; }
    .subject-card strong { color: white !important; }

    .progress-track {
        background: rgba(255,255,255,0.1); border-radius: 999px;
        height: 10px; margin: 6px 0; overflow: hidden;
    }
    .progress-fill {
        height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    .section-title {
        font-family: 'Syne', sans-serif !important;
        font-size: 1.2rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 1.5rem 0 0.8rem; display: block;
    }

    .streak-card {
        background: linear-gradient(135deg, #f6d365, #fda085);
        border-radius: 14px; padding: 1.3rem;
        color: white; text-align: center;
        box-shadow: 0 6px 20px rgba(253,160,133,0.35);
    }
    .streak-number {
        font-family: 'Syne', sans-serif;
        font-size: 3rem; font-weight: 800; line-height: 1;
    }

    .calendar-grid {
        display: grid; grid-template-columns: repeat(7, 1fr);
        gap: 4px; margin-top: 8px;
    }
    .cal-day {
        aspect-ratio: 1; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 600;
    }
    .cal-active   { background: #667eea; color: white; }
    .cal-inactive { background: rgba(255,255,255,0.07); color: #94a3b8; }
    .cal-today    { background: #f5576c; color: white; }
    .cal-header   { background: transparent; color: #94a3b8; font-size:10px; }

    .insight-alert {
        border-radius: 12px; padding: 13px 16px;
        margin-bottom: 8px; display: flex;
        align-items: center; gap: 12px;
        font-size: 14px; font-weight: 500;
    }
    .insight-icon { font-size: 1.3rem; flex-shrink: 0; }
    .insight-text { font-size: 13.5px; line-height: 1.5; color: rgba(255,255,255,0.85); }

    .submission-row {
        background: #1a1a2e; border-radius: 10px;
        padding: 10px 14px; margin-bottom: 6px;
        color: white; border: 1px solid rgba(255,255,255,0.06);
        font-size: 13.5px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Auth Guard ────────────────────────────────────────
if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student = st.session_state.student
sb      = get_supabase()
enrolled = student.get("enrolled_subjects", [])

# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════
def get_progress_data(student_id, subjects):
    all_subjects    = sb.table("subjects").select("*").execute()
    all_topics      = sb.table("topics").select("*").execute()
    all_videos      = sb.table("videos").select("id, topic_id").execute()
    all_assignments = sb.table("assignments").select("id, topic_id").execute()
    all_progress    = sb.table("student_progress").select("video_id").eq(
                        "student_id", student_id).eq("completed", True).execute()
    all_submissions = sb.table("submissions").select("assignment_id").eq(
                        "student_id", student_id).execute()

    completed_video_ids  = {p["video_id"]      for p in all_progress.data}
    submitted_assign_ids = {s["assignment_id"] for s in all_submissions.data}
    subject_name_map     = {s["name"]: s       for s in all_subjects.data}

    videos_by_topic  = {}
    for v in all_videos.data:
        videos_by_topic.setdefault(v["topic_id"], []).append(v["id"])

    assigns_by_topic = {}
    for a in all_assignments.data:
        assigns_by_topic.setdefault(a["topic_id"], []).append(a["id"])

    topics_by_subject = {}
    for t in all_topics.data:
        topics_by_subject.setdefault(t["subject_id"], []).append(t)

    data = {}
    for subj_name in subjects:
        if subj_name not in subject_name_map:
            continue
        s      = subject_name_map[subj_name]
        topics = sorted(topics_by_subject.get(s["id"], []),
                        key=lambda x: x.get("order_index", 0))
        sd = {"total_videos":0,"completed_videos":0,
              "total_assignments":0,"completed_assignments":0,"topics":[]}

        for t in topics:
            vid_ids    = videos_by_topic.get(t["id"], [])
            assign_ids = assigns_by_topic.get(t["id"], [])
            cv = len([v for v in vid_ids    if v in completed_video_ids])
            ca = len([a for a in assign_ids if a in submitted_assign_ids])
            sd["total_videos"]          += len(vid_ids)
            sd["completed_videos"]      += cv
            sd["total_assignments"]     += len(assign_ids)
            sd["completed_assignments"] += ca
            sd["topics"].append({
                "title": t["title"],
                "total_videos": len(vid_ids), "completed_videos": cv,
                "total_assignments": len(assign_ids), "completed_assignments": ca,
            })
        data[subj_name] = sd
    return data


def get_streak(student_id):
    prog = sb.table("student_progress").select("completed_at").eq(
        "student_id", student_id).eq("completed", True).execute()
    subs = sb.table("submissions").select("submitted_at").eq(
        "student_id", student_id).execute()

    active_dates = set()
    for p in prog.data:
        raw = p.get("completed_at")
        if raw:
            try: active_dates.add(datetime.fromisoformat(raw.replace("Z","").split(".")[0]).date())
            except: pass
    for s in subs.data:
        raw = s.get("submitted_at")
        if raw:
            try: active_dates.add(datetime.fromisoformat(raw.replace("Z","").split(".")[0]).date())
            except: pass

    streak = 0
    check  = date.today()
    while check in active_dates:
        streak += 1; check -= timedelta(days=1)
    return streak, sorted(active_dates)


# ═══════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-banner">
    <div style="position:relative;z-index:1;">
        <h1 style="font-size:1.9rem;margin:0;font-family:'Syne',sans-serif;">
            Welcome back, {student['name']}! 👋
        </h1>
        <p style="opacity:0.85;margin:6px 0 0;font-size:1rem;">
            Here's your complete learning overview
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# LOAD ALL DATA (bulk — minimal DB calls)
# ═══════════════════════════════════════════════════════
with st.spinner("Loading dashboard..."):
    progress_data = get_progress_data(student["id"], enrolled) if enrolled else {}
    streak_val, active_dates = get_streak(student["id"])
    subs_data = sb.table("submissions").select("*").eq("student_id", student["id"]).execute()

total_v = sum(d["total_videos"]          for d in progress_data.values())
done_v  = sum(d["completed_videos"]      for d in progress_data.values())
total_a = sum(d["total_assignments"]     for d in progress_data.values())
done_a  = sum(d["completed_assignments"] for d in progress_data.values())
overall = int(((done_v+done_a)/(total_v+total_a)*100) if (total_v+total_a)>0 else 0)
passed  = len([s for s in subs_data.data if s.get("status")=="passed"])

# ═══════════════════════════════════════════════════════
# TOP METRICS ROW
# ═══════════════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("📚 Subjects",    len(enrolled))
with c2: st.metric("🎬 Videos Done", f"{done_v}/{total_v}",
                   delta=f"{int(done_v/total_v*100) if total_v else 0}%")
with c3: st.metric("📝 Assignments", f"{done_a}/{total_a}",
                   delta=f"{int(done_a/total_a*100) if total_a else 0}%")
with c4: st.metric("🏆 Passed",      passed)
with c5: st.metric("🔥 Streak",      f"{streak_val} days")

st.divider()

if not enrolled:
    st.info("👉 Go to **My Subjects** to enroll in Python or C++ to start learning!")
    st.stop()

# ═══════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Progress Overview",
    "🔥 Streaks & Activity",
    "💡 Insights",
    "🕒 Recent Activity",
])

# ──────────────────────────────────────────────────────
# TAB 1 – PROGRESS OVERVIEW
# ──────────────────────────────────────────────────────
with tab1:
    st.markdown('<span class="section-title">📊 Your Learning Progress</span>', unsafe_allow_html=True)

    for subj_name, d in progress_data.items():
        icon  = "🐍" if subj_name == "Python" else "⚡"
        color = "#3776AB" if subj_name == "Python" else "#00599C"
        pct_v = int(d["completed_videos"]      / d["total_videos"]      * 100) if d["total_videos"]      else 0
        pct_a = int(d["completed_assignments"] / d["total_assignments"] * 100) if d["total_assignments"] else 0
        ov    = int((d["completed_videos"]+d["completed_assignments"]) /
                    max(d["total_videos"]+d["total_assignments"],1) * 100)

        st.markdown(f"""
        <div class="subject-card" style="border-left-color:{color};">
            <h3>{icon} {subj_name}</h3>
            <div style="display:flex;gap:2rem;flex-wrap:wrap;">
                <div style="flex:1;min-width:180px;">
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:rgba(255,255,255,0.65);font-size:13px;">🎬 Videos</span>
                        <strong>{d['completed_videos']}/{d['total_videos']} ({pct_v}%)</strong>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width:{pct_v}%;
                             background:linear-gradient(90deg,{color},{color}88);"></div>
                    </div>
                </div>
                <div style="flex:1;min-width:180px;">
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:rgba(255,255,255,0.65);font-size:13px;">📝 Assignments</span>
                        <strong>{d['completed_assignments']}/{d['total_assignments']} ({pct_a}%)</strong>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill"
                             style="width:{pct_a}%;background:linear-gradient(90deg,#f093fb,#f5576c);"></div>
                    </div>
                </div>
            </div>
            <div style="margin-top:10px;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:rgba(255,255,255,0.65);font-size:13px;">Overall</span>
                    <strong>{ov}% Complete</strong>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{ov}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📌 Topic-wise breakdown — {subj_name}"):
            for t in d["topics"]:
                tv = int(t["completed_videos"]      / t["total_videos"]      * 100) if t["total_videos"]      else 0
                ta = int(t["completed_assignments"] / t["total_assignments"] * 100) if t["total_assignments"] else 0
                status = "✅" if tv==100 and ta==100 else ("🔄" if tv>0 or ta>0 else "🔲")
                st.markdown(f"**{status} {t['title']}** — Videos: `{t['completed_videos']}/{t['total_videos']}` &nbsp;|&nbsp; Assignments: `{t['completed_assignments']}/{t['total_assignments']}`")

    st.markdown('<span class="section-title">📈 Completion Chart</span>', unsafe_allow_html=True)
    try:
        import pandas as pd
        rows = []
        for subj_name, d in progress_data.items():
            for t in d["topics"]:
                rows.append({
                    "Topic": t["title"][:18],
                    "Videos %":      int(t["completed_videos"]      / t["total_videos"]      * 100) if t["total_videos"]      else 0,
                    "Assignments %": int(t["completed_assignments"] / t["total_assignments"] * 100) if t["total_assignments"] else 0,
                })
        if rows:
            st.bar_chart(pd.DataFrame(rows).set_index("Topic"), height=280)
    except:
        st.info("Install pandas: `pip install pandas`")


# ──────────────────────────────────────────────────────
# TAB 2 – STREAKS & ACTIVITY
# ──────────────────────────────────────────────────────
with tab2:
    st.markdown('<span class="section-title">🔥 Streaks & Activity</span>', unsafe_allow_html=True)

    longest = 0
    if active_dates:
        cur = longest = 1
        for i in range(1, len(active_dates)):
            if (active_dates[i] - active_dates[i-1]).days == 1:
                cur += 1; longest = max(longest, cur)
            else:
                cur = 1

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="streak-card">
            <div style="font-size:0.9rem;opacity:0.9;">🔥 Current Streak</div>
            <div class="streak-number">{streak_val}</div>
            <div style="font-size:0.85rem;opacity:0.85;">days in a row</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="streak-card" style="background:linear-gradient(135deg,#a18cd1,#fbc2eb);">
            <div style="font-size:0.9rem;opacity:0.9;">🏆 Longest Streak</div>
            <div class="streak-number">{longest}</div>
            <div style="font-size:0.85rem;opacity:0.85;">days record</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="streak-card" style="background:linear-gradient(135deg,#43e97b,#38f9d7);">
            <div style="font-size:0.9rem;opacity:0.9;">📅 Total Active Days</div>
            <div class="streak-number">{len(active_dates)}</div>
            <div style="font-size:0.85rem;opacity:0.85;">days studied</div>
        </div>""", unsafe_allow_html=True)

    st.write("")
    if streak_val == 0:
        st.warning("😴 No activity today! Start studying to begin your streak.")
    elif streak_val < 3:
        st.info(f"🌱 {streak_val} day streak — keep going!")
    elif streak_val < 7:
        st.success(f"🔥 {streak_val} day streak! You're building a great habit!")
    elif streak_val < 14:
        st.success(f"⚡ {streak_val} days strong! You're on fire!")
    else:
        st.success(f"🏆 LEGENDARY! {streak_val} day streak!")

    # Heatmap calendar
    st.markdown('<span class="section-title">📅 Activity Calendar (Last 4 Weeks)</span>',
                unsafe_allow_html=True)
    today      = date.today()
    start_cal  = today - timedelta(days=27)
    active_set = set(active_dates)

    header_html = "".join([f'<div class="cal-day cal-header">{d}</div>'
                           for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]])
    cells = ['<div class="cal-day"></div>'] * start_cal.weekday()
    for i in range(28):
        d = start_cal + timedelta(days=i)
        if d == today:       css, lbl = "cal-today",    "●"
        elif d in active_set: css, lbl = "cal-active",   "✓"
        else:                 css, lbl = "cal-inactive",  str(d.day)
        cells.append(f'<div class="cal-day {css}" title="{d.strftime("%b %d")}">{lbl}</div>')

    st.markdown(f"""
    <div style="background:#1a1a2e;border-radius:14px;padding:1.2rem;
                border:1px solid rgba(255,255,255,0.07);">
        <div style="display:flex;gap:12px;margin-bottom:8px;">
            <span style="font-size:12px;color:rgba(255,255,255,0.7);">
                <span style="background:#667eea;color:white;padding:2px 8px;border-radius:4px;">✓</span> Active
            </span>
            <span style="font-size:12px;color:rgba(255,255,255,0.7);">
                <span style="background:#f5576c;color:white;padding:2px 8px;border-radius:4px;">●</span> Today
            </span>
            <span style="font-size:12px;color:rgba(255,255,255,0.7);">
                <span style="background:rgba(255,255,255,0.07);color:#94a3b8;padding:2px 8px;border-radius:4px;">N</span> Inactive
            </span>
        </div>
        <div class="calendar-grid">{header_html}{"".join(cells)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="section-title">📈 Weekly Activity</span>', unsafe_allow_html=True)
    try:
        import pandas as pd
        week_data = {}
        for i in range(8):
            ws = today - timedelta(days=today.weekday() + 7*i)
            week_data[f"W-{i}"] = sum(1 for d in active_set if ws <= d < ws + timedelta(days=7))
        st.line_chart(
            pd.DataFrame({"Active Days": list(reversed(list(week_data.values())))},
                         index=list(reversed(list(week_data.keys())))),
            height=200
        )
    except: pass


# ──────────────────────────────────────────────────────
# TAB 3 – INSIGHTS
# ──────────────────────────────────────────────────────
with tab3:
    st.markdown('<span class="section-title">💡 Smart Insights</span>', unsafe_allow_html=True)

    border_map = {"red":"#ef4444","orange":"#f59e0b","green":"#22c55e","blue":"#3b82f6"}
    grad_map   = {
        "red":    "linear-gradient(135deg,rgba(239,68,68,0.12),rgba(239,68,68,0.04))",
        "orange": "linear-gradient(135deg,rgba(245,158,11,0.12),rgba(245,158,11,0.04))",
        "green":  "linear-gradient(135deg,rgba(34,197,94,0.12),rgba(34,197,94,0.04))",
        "blue":   "linear-gradient(135deg,rgba(59,130,246,0.12),rgba(59,130,246,0.04))",
    }
    insights = []

    for subj, d in progress_data.items():
        pct_v = int(d["completed_videos"]      / d["total_videos"]      * 100) if d["total_videos"]      else 0
        pct_a = int(d["completed_assignments"] / d["total_assignments"] * 100) if d["total_assignments"] else 0
        if pct_v == 0:
            insights.append(("🚨", f"You haven't watched any {subj} videos yet. Start with Topic 1!", "red"))
        elif pct_v < 30:
            insights.append(("⚠️", f"{subj}: Only {pct_v}% of videos done. Try 2 videos daily.", "orange"))
        elif pct_v >= 80:
            insights.append(("✅", f"Great job on {subj} videos! {pct_v}% done. Focus on assignments now.", "green"))
        if pct_a < pct_v - 20:
            insights.append(("📝", f"{subj}: Assignments lagging behind videos. Catch up on practice!", "orange"))
        weak = [t for t in d["topics"] if t["total_videos"]>0 and t["completed_videos"]==0]
        if weak:
            insights.append(("🎯", f"{subj}: '{weak[0]['title']}' hasn't been started. Prioritize it!", "blue"))

    if streak_val == 0:
        insights.append(("💤", "No activity today. Even 20 minutes counts!", "orange"))
    elif streak_val >= 7:
        insights.append(("🏆", f"Amazing! {streak_val}-day streak! You're in the top tier.", "green"))

    if overall >= 75:
        insights.append(("🎉", f"You're {overall}% done overall! Almost ready for the exam!", "green"))
    elif overall >= 50:
        insights.append(("💪", f"Halfway at {overall}%! Keep the momentum going.", "blue"))

    if not insights:
        insights.append(("🌟", "Keep up the great work! Stay consistent every day.", "green"))

    for icon, msg, color in insights:
        st.markdown(f"""
        <div class="insight-alert"
             style="background:{grad_map.get(color,grad_map['blue'])};
                    border-left:4px solid {border_map.get(color,'#667eea')};">
            <span class="insight-icon">{icon}</span>
            <span class="insight-text">{msg}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<span class="section-title">⏱ Estimated Completion</span>', unsafe_allow_html=True)
    for subj, d in progress_data.items():
        icon  = "🐍" if subj == "Python" else "⚡"
        rem_v = d["total_videos"]      - d["completed_videos"]
        rem_a = d["total_assignments"] - d["completed_assignments"]
        days_needed = max(rem_v // 2, rem_a)
        eta = date.today() + timedelta(days=days_needed)
        st.markdown(f"""
        <div style="background:#1a1a2e;border-radius:12px;padding:1rem 1.2rem;
                    box-shadow:0 2px 10px rgba(0,0,0,0.2);margin-bottom:0.6rem;
                    display:flex;justify-content:space-between;align-items:center;
                    border:1px solid rgba(255,255,255,0.06);">
            <div>
                <strong style="color:white;">{icon} {subj}</strong><br>
                <span style="color:rgba(255,255,255,0.4);font-size:12px;">
                    {rem_v} videos + {rem_a} assignments remaining
                </span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.2rem;font-weight:800;
                            background:linear-gradient(135deg,#667eea,#f093fb);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    ~{days_needed} days
                </div>
                <div style="font-size:11px;color:rgba(255,255,255,0.4);">
                    ETA: {eta.strftime('%d %b %Y')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# TAB 4 – RECENT ACTIVITY
# ──────────────────────────────────────────────────────
with tab4:
    st.markdown('<span class="section-title">🕒 Recent Submissions</span>', unsafe_allow_html=True)

    if not subs_data.data:
        st.info("No submissions yet. Head to **Assignments** to get started!")
    else:
        recent = sorted(subs_data.data,
                        key=lambda x: x.get("submitted_at",""), reverse=True)[:10]
        for sub in recent:
            assign = sb.table("assignments").select("title, difficulty").eq(
                "id", sub["assignment_id"]).execute()
            if assign.data:
                a = assign.data[0]
                s_icon = "✅" if sub["status"]=="passed" else ("❌" if sub["status"]=="failed" else "⏳")
                d_color = {"Easy":"#22c55e","Medium":"#f59e0b","Hard":"#ef4444"}.get(a["difficulty"],"#667eea")
                st.markdown(f"""
                <div class="submission-row">
                    <strong>{s_icon} {a['title']}</strong> &nbsp;
                    <span style="color:{d_color};font-size:11px;
                          background:rgba(255,255,255,0.08);
                          padding:2px 8px;border-radius:10px;">{a['difficulty']}</span>
                    &nbsp; Status: <code>{sub['status']}</code>
                    &nbsp; Score: <strong>{sub.get('score',0)} pts</strong>
                </div>
                """, unsafe_allow_html=True)