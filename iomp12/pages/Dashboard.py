import streamlit as st
from utils.db import get_supabase

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

# ─── CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 16px; color: white;
        text-align: center; margin-bottom: 2rem;
    }
    .subject-card {
        background: white; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea; margin-bottom: 1rem;
    }
    .metric-card {
        background: white; border-radius: 12px;
        padding: 1.5rem; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #667eea;
    }
    .progress-bar-bg {
        background: #f0f0f0; border-radius: 8px; height: 10px; margin-top: 8px;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 8px; height: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Auth Guard ────────────────────────────────────────
if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student = st.session_state.student
sb = get_supabase()

# ─── Header ────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1>Welcome back, {student['name']}! 👋</h1>
    <p style="opacity:0.9;font-size:1.1rem;">Continue your learning journey in Python & C++</p>
</div>
""", unsafe_allow_html=True)

# ─── Metrics ───────────────────────────────────────────
enrolled = student.get("enrolled_subjects", [])

progress_data = sb.table("student_progress").select("*").eq(
    "student_id", student["id"]).eq("completed", True).execute()

subs_data = sb.table("submissions").select("*").eq(
    "student_id", student["id"]).execute()

passed_subs = [s for s in subs_data.data if s.get("status") == "passed"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📚 Enrolled Subjects", len(enrolled), delta=None)
with col2:
    st.metric("✅ Videos Completed", len(progress_data.data))
with col3:
    st.metric("📝 Assignments Submitted", len(subs_data.data))
with col4:
    st.metric("🏆 Assignments Passed", len(passed_subs))

st.divider()

# ─── Enrolled Subjects Overview ────────────────────────
if not enrolled:
    st.info("👉 Go to **My Subjects** to enroll in Python or C++ and start learning!")
else:
    st.subheader("📚 Your Enrolled Subjects")
    
    for subj_name in enrolled:
        subj = sb.table("subjects").select("*").eq("name", subj_name).execute()
        if not subj.data:
            continue
        
        s = subj.data[0]
        topics = sb.table("topics").select("*").eq("subject_id", s["id"]).execute()
        
        # Get total videos for this subject
        total_videos = 0
        completed_videos = 0
        for topic in topics.data:
            videos = sb.table("videos").select("id").eq("topic_id", topic["id"]).execute()
            total_videos += len(videos.data)
            for v in videos.data:
                prog = sb.table("student_progress").select("*").eq(
                    "student_id", student["id"]).eq("video_id", v["id"]).eq("completed", True).execute()
                if prog.data:
                    completed_videos += 1
        
        pct = int((completed_videos / total_videos * 100) if total_videos > 0 else 0)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class="subject-card">
                <h3>{s['icon']} {s['name']}</h3>
                <p style="color:#666;">{s['description']}</p>
                <p>
                    <strong>{len(topics.data)}</strong> Topics &nbsp;|&nbsp;
                    <strong>{completed_videos}/{total_videos}</strong> Videos Completed
                </p>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{pct}%"></div>
                </div>
                <small style="color:#888;">{pct}% complete</small>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.metric("Progress", f"{pct}%")

st.divider()

# ─── Recent Activity ───────────────────────────────────
st.subheader("🕒 Recent Submissions")

if not subs_data.data:
    st.info("No submissions yet. Head to **Assignments** to get started!")
else:
    recent = sorted(subs_data.data, key=lambda x: x.get("submitted_at", ""), reverse=True)[:5]
    for sub in recent:
        assign = sb.table("assignments").select("title, difficulty").eq("id", sub["assignment_id"]).execute()
        if assign.data:
            a = assign.data[0]
            status_icon = "✅" if sub["status"] == "passed" else ("❌" if sub["status"] == "failed" else "⏳")
            diff_color = {"Easy": "#155724", "Medium": "#856404", "Hard": "#721c24"}.get(a["difficulty"], "#333")
            st.markdown(f"""
            **{status_icon} {a['title']}** &nbsp;
            <span style="color:{diff_color};font-size:12px;background:#f5f5f5;padding:2px 8px;border-radius:10px;">{a['difficulty']}</span> &nbsp;
            Status: `{sub['status']}` &nbsp; Score: **{sub.get('score', 0)} pts**
            """, unsafe_allow_html=True)