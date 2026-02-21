import streamlit as st
from utils.db import get_supabase
st.set_page_config(page_title="Assignments", page_icon="📝", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .assignment-header {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        padding: 1.5rem 2rem; border-radius: 14px; color: white;
        margin-bottom: 1.5rem;
    }
    .assignment-card {
        background: #fff9f0; border-radius: 12px;
        padding: 1.5rem; border: 1px solid #ffd89b;
        margin-bottom: 1rem;
    }
    .difficulty-easy {
        background:#d4edda; color:#155724;
        padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600;
    }
    .difficulty-medium {
        background:#fff3cd; color:#856404;
        padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600;
    }
    .difficulty-hard {
        background:#f8d7da; color:#721c24;
        padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600;
    }
    .test-case-box {
        background: #1e1e1e; color: #d4d4d4;
        border-radius: 8px; padding: 12px 16px;
        font-family: monospace; font-size: 13px;
        margin: 6px 0;
    }
    .hint-box {
        background: #e8f4fd; border-left: 4px solid #3498db;
        border-radius: 0 8px 8px 0; padding: 10px 14px;
        margin: 4px 0; color: #1a5276;
    }
    .submission-passed { background:#d4edda; border-radius:8px; padding:10px 14px; color:#155724; }
    .submission-failed { background:#f8d7da; border-radius:8px; padding:10px 14px; color:#721c24; }
    .submission-pending { background:#fff3cd; border-radius:8px; padding:10px 14px; color:#856404; }
</style>
""", unsafe_allow_html=True)

# ─── Auth Guard ────────────────────────────────────────
if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student = st.session_state.student
sb = get_supabase()
enrolled = student.get("enrolled_subjects", [])

st.title("📝 Assignments")

if not enrolled:
    st.warning("Please enroll in a subject first from **My Subjects**.")
    st.stop()

# ─── Selectors ─────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    subject_choice = st.selectbox("📚 Select Subject", enrolled)
with col2:
    subj = sb.table("subjects").select("*").eq("name", subject_choice).execute()
    if not subj.data:
        st.stop()
    topics = sb.table("topics").select("*").eq(
        "subject_id", subj.data[0]["id"]).order("order_index").execute()
    selected_topic_name = st.selectbox("📌 Select Topic", [t["title"] for t in topics.data])
with col3:
    st.write("")
    ai_generate = st.toggle("🤖 AI Generate")

topic = next((t for t in topics.data if t["title"] == selected_topic_name), None)
if not topic:
    st.stop()

# ─── Header ────────────────────────────────────────────
st.markdown(f"""
<div class="assignment-header">
    <h2>📝 {selected_topic_name}</h2>
    <p style="opacity:0.9;">{subject_choice} Assignments</p>
</div>
""", unsafe_allow_html=True)

# ─── AI Generate Section ───────────────────────────────
if ai_generate:
    st.markdown("### 🤖 Generate AI Assignment")
    
    col_d, col_b = st.columns([2, 1])
    with col_d:
        difficulty = st.select_slider(
            "Select Difficulty", options=["Easy", "Medium", "Hard"], value="Easy"
        )
    with col_b:
        st.write("")
        generate_btn = st.button("⚡ Generate Assignment", type="primary", use_container_width=True)
    
    if generate_btn:
        with st.spinner("🤖 Generating assignment with AI..."):
            try:
                from utils.ai_assignments import generate_assignment
                assignment = generate_assignment(selected_topic_name, subject_choice, difficulty)
                
                sb.table("assignments").insert({
                    "topic_id": topic["id"],
                    "title": assignment["title"],
                    "description": assignment["description"],
                    "difficulty": difficulty,
                    "points": assignment.get("points", 10),
                    "test_cases": assignment.get("test_cases", []),
                    "hints": assignment.get("hints", []),
                    "expected_concepts": assignment.get("expected_concepts", [])
                }).execute()
                
                st.success("✅ Assignment generated and saved to database!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Generation failed: {e}")
    
    st.divider()

# ─── Assignments List ──────────────────────────────────
assignments = sb.table("assignments").select("*").eq(
    "topic_id", topic["id"]).execute()

if not assignments.data:
    st.info("📭 No assignments yet for this topic.")
    if not ai_generate:
        st.markdown("👆 Toggle **🤖 AI Generate** above to create a CCBP-style assignment!")
else:
    st.markdown(f"### 📋 {len(assignments.data)} Assignment(s) for: **{selected_topic_name}**")
    
    for a in assignments.data:
        diff_class = f"difficulty-{a['difficulty'].lower()}"
        
        # Check existing submission
        existing = sb.table("submissions").select("*").eq(
            "student_id", student["id"]).eq("assignment_id", a["id"]).execute()
        sub = existing.data[0] if existing.data else None
        
        sub_icon = "✅" if sub and sub["status"] == "passed" else (
            "❌" if sub and sub["status"] == "failed" else (
            "⏳" if sub else "🆕"))
        
        with st.expander(f"{sub_icon} {a['title']}", expanded=False):
            
            # Meta info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<span class="{diff_class}">{a["difficulty"]}</span>', 
                           unsafe_allow_html=True)
            with col2:
                st.markdown(f"🏆 **{a['points']} points**")
            with col3:
                if a.get("expected_concepts"):
                    st.caption(f"Concepts: {', '.join(a['expected_concepts'])}")
            
            st.divider()
            
            # Problem Statement
            st.markdown("#### 📋 Problem Statement")
            st.markdown(a["description"])
            
            # Test Cases
            if a.get("test_cases") and len(a["test_cases"]) > 0:
                st.markdown("#### 🧪 Sample Test Cases")
                for i, tc in enumerate(a["test_cases"], 1):
                    st.markdown(f"""
                    <div class="test-case-box">
                    <strong>Test Case {i}:</strong><br>
                    📥 Input: <code>{tc.get('input', 'N/A')}</code><br>
                    📤 Expected Output: <code>{tc.get('expected_output', 'N/A')}</code><br>
                    💬 Explanation: {tc.get('explanation', '')}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Hints
            if a.get("hints") and len(a["hints"]) > 0:
                with st.expander("💡 Show Hints"):
                    for h in a["hints"]:
                        st.markdown(f"""
                        <div class="hint-box">💡 {h}</div>
                        """, unsafe_allow_html=True)
            
            # Previous submission status
            if sub:
                status_class = f"submission-{sub['status']}"
                status_icons = {"passed": "✅", "failed": "❌", "pending": "⏳"}
                icon = status_icons.get(sub["status"], "⏳")
                st.markdown(f"""
                <div class="{status_class}">
                    {icon} <strong>Submission Status:</strong> {sub['status'].title()} 
                    &nbsp;|&nbsp; Score: <strong>{sub.get('score', 0)} pts</strong>
                    {f"<br>💬 Feedback: {sub['feedback']}" if sub.get('feedback') else ""}
                </div>
                """, unsafe_allow_html=True)
                st.write("")
            
            # Code Editor
            st.markdown("#### 💻 Your Solution")
            lang_hint = "# Python solution" if subject_choice == "Python" else "// C++ solution\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your code here\n    return 0;\n}"
            default_code = sub["code"] if sub else lang_hint
            
            # Use session state value if exists, else default
            area_key = f"code_{a['id']}"
            if area_key not in st.session_state:
                st.session_state[area_key] = default_code

            code = st.text_area(
                "Write your code here:",
                height=250,
                key=area_key,
                help="Write your solution in the box above"
            )
            
            col_sub, col_clr = st.columns([3, 1])
            with col_sub:
                if st.button("📤 Submit & Evaluate", key=f"submit_{a['id']}", type="primary", use_container_width=True):
                    if not code.strip() or code.strip() == lang_hint.strip():
                        st.error("Please write your solution before submitting!")
                    else:
                        with st.spinner("🤖 Evaluating your code with AI..."):
                            try:
                                from utils.ai_assignments import evaluate_submission
                                result = evaluate_submission(
                                    code,
                                    a["title"],
                                    a["description"],
                                    a.get("test_cases", []),
                                    subject_choice
                                )
                                status   = result.get("status", "pending")
                                score    = result.get("score", 0)
                                feedback = result.get("feedback", "")

                                if sub:
                                    sb.table("submissions").update({
                                        "code": code,
                                        "status": status,
                                        "score": score,
                                        "feedback": feedback
                                    }).eq("id", sub["id"]).execute()
                                else:
                                    sb.table("submissions").insert({
                                        "student_id": student["id"],
                                        "assignment_id": a["id"],
                                        "code": code,
                                        "status": status,
                                        "score": score,
                                        "feedback": feedback
                                    }).execute()

                                if status == "passed":
                                    st.success(f"✅ Passed! Score: {score}/10")
                                    st.balloons()
                                else:
                                    st.error(f"❌ Failed. Score: {score}/10")

                                st.info(f"💬 Feedback: {feedback}")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Evaluation failed: {e}")
            with col_clr:
                if st.button("🗑 Clear", key=f"clear_{a['id']}", use_container_width=True):
                    # Delete the key first before rerun so widget reinitializes cleanly
                    if f"code_{a['id']}" in st.session_state:
                        del st.session_state[f"code_{a['id']}"]
                    st.rerun()