import streamlit as st
from utils.db import get_supabase

st.set_page_config(page_title="Videos", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .video-card {
        background: white; border-radius: 12px;
        padding: 1rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
        border: 1px solid #eee;
    }
    .header-banner {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        padding: 1.5rem 2rem; border-radius: 14px; color: white;
        margin-bottom: 1.5rem;
    }
    .completed-tag {
        background: #d4edda; color: #155724;
        padding: 4px 12px; border-radius: 20px; font-size: 13px;
        font-weight: 600;
    }
    .pending-tag {
        background: #fff3cd; color: #856404;
        padding: 4px 12px; border-radius: 20px; font-size: 13px;
        font-weight: 600;
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

st.title("🎬 Video Lessons")

if not enrolled:
    st.warning("Please enroll in a subject first from **My Subjects**.")
    st.stop()

# ─── Subject & Topic Selectors ─────────────────────────
col1, col2 = st.columns(2)
with col1:
    subject_choice = st.selectbox("📚 Select Subject", enrolled)
with col2:
    subj = sb.table("subjects").select("*").eq("name", subject_choice).execute()
    if not subj.data:
        st.stop()
    
    topics = sb.table("topics").select("*").eq(
        "subject_id", subj.data[0]["id"]).order("order_index").execute()
    topic_names = [t["title"] for t in topics.data]
    selected_topic_name = st.selectbox("📌 Select Topic", topic_names)

topic = next((t for t in topics.data if t["title"] == selected_topic_name), None)
if not topic:
    st.stop()

# ─── Topic Header ──────────────────────────────────────
st.markdown(f"""
<div class="header-banner">
    <h2>🎬 {selected_topic_name}</h2>
    <p style="opacity:0.9;">{topic.get('description', '')}</p>
</div>
""", unsafe_allow_html=True)

# ─── Videos ────────────────────────────────────────────
videos = sb.table("videos").select("*").eq(
    "topic_id", topic["id"]).order("order_index").execute()

if not videos.data:
    st.info("📭 No videos added yet for this topic.")
    st.markdown("""
    **To add videos**, go to your Supabase dashboard and insert records into the `videos` table:
    ```json
    {
      "topic_id": "<topic_uuid>",
      "title": "Video Title",
      "youtube_url": "https://www.youtube.com/embed/VIDEO_ID",
      "duration": "12:30",
      "description": "What this video covers",
      "order_index": 1
    }
    ```
    > 💡 Tip: Use the **embed** URL format: `https://www.youtube.com/embed/VIDEO_ID`
    """)
else:
    # Progress summary
    total = len(videos.data)
    completed_count = 0
    for v in videos.data:
        prog = sb.table("student_progress").select("*").eq(
            "student_id", student["id"]).eq("video_id", v["id"]).eq("completed", True).execute()
        if prog.data:
            completed_count += 1
    
    pct = int((completed_count / total * 100) if total > 0 else 0)
    st.markdown(f"**Progress: {completed_count}/{total} videos completed**")
    st.progress(pct / 100)
    st.write("")
    
    # ── Video List ─────────────────────────────────────
    for idx, v in enumerate(videos.data, 1):
        prog = sb.table("student_progress").select("*").eq(
            "student_id", student["id"]).eq("video_id", v["id"]).execute()
        is_completed = prog.data and prog.data[0]["completed"]
        
        status_html = '<span class="completed-tag">✅ Completed</span>' if is_completed else '<span class="pending-tag">⏳ Not watched</span>'
        
        with st.expander(f"🎥 {idx}. {v['title']}  ({v.get('duration', '?')})", expanded=(idx == 1)):
            col_vid, col_info = st.columns([3, 1])
            
            with col_vid:
                # Handle both embed and watch URLs
                yt_url = v["youtube_url"]
                if "watch?v=" in yt_url:
                    vid_id = yt_url.split("watch?v=")[-1].split("&")[0]
                    embed_url = f"https://www.youtube.com/embed/{vid_id}"
                elif "youtu.be/" in yt_url:
                    vid_id = yt_url.split("youtu.be/")[-1]
                    embed_url = f"https://www.youtube.com/embed/{vid_id}"
                else:
                    embed_url = yt_url  # Already embed format
                
                st.markdown(f"""
                <iframe width="100%" height="380" src="{embed_url}"
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; 
                encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen style="border-radius:10px;"></iframe>
                """, unsafe_allow_html=True)
            
            with col_info:
                st.markdown(f"**Title:** {v['title']}")
                st.markdown(f"**Duration:** {v.get('duration', 'N/A')}")
                st.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
                
                if v.get("description"):
                    st.markdown(f"**About:** {v['description']}")
                
                st.write("")
                if is_completed:
                    st.success("✅ Done!")
                    if st.button("↩ Mark Incomplete", key=f"undo_{v['id']}"):
                        sb.table("student_progress").update({
                            "completed": False, "completed_at": None
                        }).eq("id", prog.data[0]["id"]).execute()
                        st.rerun()
                else:
                    if st.button("✅ Mark as Completed", key=f"done_{v['id']}", type="primary"):
                        if prog.data:
                            sb.table("student_progress").update({
                                "completed": True
                            }).eq("id", prog.data[0]["id"]).execute()
                        else:
                            sb.table("student_progress").insert({
                                "student_id": student["id"],
                                "video_id": v["id"],
                                "completed": True
                            }).execute()
                        st.success("Marked as completed! 🎉")
                        st.rerun()