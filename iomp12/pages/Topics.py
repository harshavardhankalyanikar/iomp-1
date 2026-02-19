import streamlit as st
from utils.db import get_supabase

st.set_page_config(page_title="Topics", page_icon="📌", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .topic-card {
        background: white; border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 4px solid #667eea;
        margin-bottom: 0.8rem;
        display: flex; align-items: center; gap: 1rem;
    }
    .topic-number {
        background: #667eea; color: white;
        border-radius: 50%; width: 36px; height: 36px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 15px; flex-shrink: 0;
    }
    .header-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem; border-radius: 14px; color: white;
        margin-bottom: 1.5rem;
    }
    .stat-pill {
        background: rgba(255,255,255,0.2); border-radius: 20px;
        padding: 4px 14px; font-size: 13px; display: inline-block; margin: 4px;
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

st.title("📌 Topics")

if not enrolled:
    st.warning("Please enroll in a subject first from **My Subjects**.")
    st.stop()

# Subject selector
subject_choice = st.selectbox("Select Subject", enrolled, key="topic_subject")

subj = sb.table("subjects").select("*").eq("name", subject_choice).execute()
if not subj.data:
    st.error("Subject not found.")
    st.stop()

s = subj.data[0]
topics = sb.table("topics").select("*").eq(
    "subject_id", s["id"]).order("order_index").execute()

# ─── Header Banner ─────────────────────────────────────
total_videos = 0
total_assignments = 0
for t in topics.data:
    vids = sb.table("videos").select("id").eq("topic_id", t["id"]).execute()
    assigns = sb.table("assignments").select("id").eq("topic_id", t["id"]).execute()
    total_videos += len(vids.data)
    total_assignments += len(assigns.data)

st.markdown(f"""
<div class="header-banner">
    <h2>{s['icon']} {s['name']} — Topics</h2>
    <span class="stat-pill">📌 {len(topics.data)} Topics</span>
    <span class="stat-pill">🎬 {total_videos} Videos</span>
    <span class="stat-pill">📝 {total_assignments} Assignments</span>
</div>
""", unsafe_allow_html=True)

# ─── Topics List ───────────────────────────────────────
st.subheader("All Topics")

for i, t in enumerate(topics.data, 1):
    # Count videos and assignments per topic
    vids = sb.table("videos").select("id").eq("topic_id", t["id"]).execute()
    assigns = sb.table("assignments").select("id").eq("topic_id", t["id"]).execute()
    
    # Check videos completed by student
    completed_count = 0
    for v in vids.data:
        prog = sb.table("student_progress").select("*").eq(
            "student_id", student["id"]).eq("video_id", v["id"]).eq("completed", True).execute()
        if prog.data:
            completed_count += 1
    
    vid_count = len(vids.data)
    assign_count = len(assigns.data)
    pct = int((completed_count / vid_count * 100) if vid_count > 0 else 0)
    
    with st.expander(f"📌 Topic {i}: {t['title']}", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎬 Videos", f"{completed_count}/{vid_count}")
        with col2:
            st.metric("📝 Assignments", assign_count)
        with col3:
            st.metric("✅ Progress", f"{pct}%")
        
        st.caption(t.get("description", "No description available."))
        
        if vid_count > 0:
            st.progress(pct / 100)
        
        # Show assignments for this topic
        if assigns.data:
            st.markdown("**Assignments in this topic:**")
            for a in assigns.data:
                assign_detail = sb.table("assignments").select("title, difficulty, points").eq(
                    "id", a["id"]).execute()
                if assign_detail.data:
                    ad = assign_detail.data[0]
                    diff_colors = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
                    icon = diff_colors.get(ad["difficulty"], "⚪")
                    st.markdown(f"&nbsp;&nbsp;{icon} **{ad['title']}** — {ad['difficulty']} · {ad['points']} pts")