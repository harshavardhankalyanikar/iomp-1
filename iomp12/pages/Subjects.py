import streamlit as st
from utils.db import get_supabase
from utils.auth import enroll_subject

st.set_page_config(page_title="Subjects", page_icon="📚", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .subject-card {
        background: white; border-radius: 16px;
        padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem; border: 1px solid #eee;
    }
    .topic-badge {
        background: #f0f4ff; color: #667eea;
        padding: 5px 14px; border-radius: 20px;
        font-size: 13px; font-weight: 600;
        display: inline-block; margin: 4px;
    }
    .enrolled-banner {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-radius: 8px; padding: 10px 16px;
        color: #155724; font-weight: 600;
        display: inline-block; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Auth Guard ────────────────────────────────────────
if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student = st.session_state.student
sb = get_supabase()

st.title("📚 Available Subjects")
st.caption("Enroll in Python or C++ to access topics, videos, assignments, and cheatsheets.")

enrolled = student.get("enrolled_subjects", [])
subjects = sb.table("subjects").select("*").execute()

for s in subjects.data:
    is_enrolled = s["name"] in enrolled
    border_color = "#3776AB" if s["name"] == "Python" else "#00599C"
    
    st.markdown(f"""
    <div class="subject-card" style="border-left: 5px solid {border_color};">
        <h2 style="color:{border_color};">{s['icon']} {s['name']}</h2>
        <p style="color:#555;font-size:1rem;">{s['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Topics preview
    topics = sb.table("topics").select("*").eq(
        "subject_id", s["id"]).order("order_index").execute()
    
    st.write("**📌 Topics covered:**")
    topic_html = " ".join([
        f'<span class="topic-badge">{t["title"]}</span>' 
        for t in topics.data
    ])
    st.markdown(topic_html, unsafe_allow_html=True)
    
    st.write("")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if is_enrolled:
            st.success("✅ Enrolled")
        else:
            if st.button(f"🚀 Enroll in {s['name']}", key=f"en_{s['id']}", type="primary"):
                updated = enroll_subject(student["id"], s["name"], enrolled)
                st.session_state.student["enrolled_subjects"] = updated
                enrolled = updated
                st.success(f"✅ Successfully enrolled in {s['name']}!")
                st.rerun()
    
    with col2:
        if is_enrolled:
            if st.button(f"Unenroll", key=f"un_{s['id']}"):
                updated = [x for x in enrolled if x != s["name"]]
                sb.table("students").update(
                    {"enrolled_subjects": updated}
                ).eq("id", student["id"]).execute()
                st.session_state.student["enrolled_subjects"] = updated
                enrolled = updated
                st.warning(f"Unenrolled from {s['name']}.")
                st.rerun()
    
    with col3:
        st.markdown(f"**{len(topics.data)} topics** available")
    
    st.divider()

# ─── Summary ───────────────────────────────────────────
if enrolled:
    st.success(f"🎓 You are currently enrolled in: **{', '.join(enrolled)}**")
else:
    st.info("You haven't enrolled in any subject yet. Click **Enroll** above to get started!")