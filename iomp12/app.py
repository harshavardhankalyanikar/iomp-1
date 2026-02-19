import streamlit as st
from utils.auth import login_student, register_student
from utils.db import get_supabase
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ───────────────────────────────────────
st.set_page_config(
    page_title="Smart Study Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────
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
        transition: transform 0.2s;
    }
    .subject-card:hover { transform: translateY(-2px); }
    
    .topic-badge {
        background: #f0f4ff; color: #667eea;
        padding: 4px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 600;
        display: inline-block; margin: 4px;
    }
    .assignment-card {
        background: #fff9f0; border-radius: 12px;
        padding: 1.5rem; border: 1px solid #ffd89b;
        margin-bottom: 1rem;
    }
    .difficulty-easy { background:#d4edda; color:#155724; padding:4px 10px; border-radius:20px; font-size:12px; }
    .difficulty-medium { background:#fff3cd; color:#856404; padding:4px 10px; border-radius:20px; font-size:12px; }
    .difficulty-hard { background:#f8d7da; color:#721c24; padding:4px 10px; border-radius:20px; font-size:12px; }
    
    .stButton > button {
        border-radius: 8px; font-weight: 600;
        transition: all 0.2s;
    }
    .sidebar-logo { text-align: center; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ────────────────────────────────
if "student" not in st.session_state:
    st.session_state.student = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# ─── Auth Guard ────────────────────────────────────────
def show_auth():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }

        /* Center and constrain the auth card */
        .block-container {
            max-width: 520px !important;
            padding: 3rem 2rem !important;
            margin: 0 auto !important;
        }

        /* Style the tab buttons */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 8px 24px;
            font-weight: 600;
        }

        /* Style input fields */
        .stTextInput input {
            border-radius: 8px !important;
            padding: 10px 14px !important;
            font-size: 15px !important;
        }

        /* Style submit buttons */
        .stFormSubmitButton button {
            width: 100% !important;
            border-radius: 8px !important;
            padding: 12px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            margin-top: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1>🎓 Smart Study Planner</h1>
        <p style="opacity:0.9;font-size:1.1rem;">Master Python & C++ with structured learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="student@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            if submitted:
                student = login_student(email, password)
                if student:
                    st.session_state.student = student
                    st.success("Welcome back! 🎉")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register", use_container_width=True, type="primary")
            if submitted:
                if password != confirm:
                    st.error("Passwords don't match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    student = register_student(name, email, password)
                    if student:
                        st.session_state.student = student
                        st.success("Account created! Welcome 🎉")
                        st.rerun()
                    else:
                        st.error("Email already exists.")

# ─── Main App ───────────────────────────────────────────
def show_app():
    student = st.session_state.student
    sb = get_supabase()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f0c29, #302b63);
                min-width: 220px !important;
                max-width: 220px !important;
            }
            .nav-logo {
                text-align: center;
                padding: 1.5rem 1rem 1rem;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 1rem;
            }
            .nav-logo h2 {
                color: white;
                font-size: 1.2rem;
                margin: 0;
                font-weight: 700;
            }
            .nav-logo p {
                color: rgba(255,255,255,0.6);
                font-size: 0.8rem;
                margin: 4px 0 0;
            }
            .nav-avatar {
                width: 52px; height: 52px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.4rem; margin: 0 auto 8px;
                box-shadow: 0 4px 15px rgba(102,126,234,0.5);
            }
            div[data-testid="stSidebarNav"] { display: none; }

            .stButton button {
                background: transparent !important;
                border: none !important;
                color: rgba(255,255,255,0.7) !important;
                text-align: left !important;
                padding: 10px 16px !important;
                border-radius: 10px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                width: 100% !important;
                transition: all 0.2s !important;
            }
            .stButton button:hover {
                background: rgba(255,255,255,0.1) !important;
                color: white !important;
                transform: translateX(4px) !important;
            }
            .nav-active button {
                background: linear-gradient(135deg, #667eea, #764ba2) !important;
                color: white !important;
                box-shadow: 0 4px 12px rgba(102,126,234,0.4) !important;
            }
            .nav-section-label {
                color: rgba(255,255,255,0.35);
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                padding: 8px 16px 4px;
            }
            .logout-btn button {
                background: rgba(245,87,108,0.15) !important;
                color: #f5576c !important;
                border: 1px solid rgba(245,87,108,0.3) !important;
                margin-top: 8px !important;
            }
            .logout-btn button:hover {
                background: rgba(245,87,108,0.3) !important;
                transform: none !important;
            }
        </style>
        """, unsafe_allow_html=True)

        # Avatar & name
        initials = student['name'][0].upper()
        st.markdown(f"""
        <div class="nav-logo">
            <div class="nav-avatar">{initials}</div>
            <h2>StudyPlanner</h2>
            <p>👋 {student['name']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Init page in session
        if "nav_page" not in st.session_state:
            st.session_state.nav_page = "Dashboard"

        nav_items = [
            ("Dashboard",   "🏠", "Dashboard"),
            ("My Subjects", "📚", "My Subjects"),
            ("Videos",      "🎬", "Videos"),
            ("Assignments", "📝", "Assignments"),
            ("Cheatsheets", "📄", "Cheatsheets"),
            ("Study Plan",  "🧠", "Study Plan"),
            ("Settings",    "⚙️",  "Settings"),
        ]

        st.markdown('<div class="nav-section-label">Menu</div>', unsafe_allow_html=True)

        for key, icon, label in nav_items:
            is_active = st.session_state.nav_page == key
            css_class = "nav-active" if is_active else ""
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.nav_page = key
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="nav-section-label" style="margin-top:1rem;">Account</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
            st.session_state.student = None
            st.session_state.nav_page = "Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        page = st.session_state.nav_page

    # ── Dashboard ──────────────────────────────────────
    if page == "Dashboard":
        show_dashboard(student, sb)
    elif page == "My Subjects":
        show_subjects(student, sb)
    elif page == "Videos":
        show_videos(student, sb)
    elif page == "Assignments":
        show_assignments(student, sb)
    elif page == "Cheatsheets":
        show_cheatsheets(student, sb)
    elif page == "Study Plan":
        import importlib.util, sys, os
        spec = importlib.util.spec_from_file_location(
            "study_plan", os.path.join("pages", "Study_Plan.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    elif page == "Settings":
        show_settings(student, sb)

# ─── Dashboard ──────────────────────────────────────────
def show_dashboard(student, sb):
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome back, {student['name']}! 👋</h1>
        <p>Continue your learning journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    enrolled = student.get("enrolled_subjects", [])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Enrolled Subjects", len(enrolled))
    
    # Videos completed
    progress = sb.table("student_progress").select("*").eq(
        "student_id", student["id"]).eq("completed", True).execute()
    with col2:
        st.metric("✅ Videos Completed", len(progress.data))
    
    # Assignments submitted
    subs = sb.table("submissions").select("*").eq(
        "student_id", student["id"]).execute()
    with col3:
        st.metric("📝 Assignments Done", len(subs.data))
    
    if not enrolled:
        st.info("👉 Go to **My Subjects** to enroll in Python or C++!")
    else:
        st.subheader("Your Subjects")
        for subj_name in enrolled:
            subj = sb.table("subjects").select("*").eq("name", subj_name).execute()
            if subj.data:
                s = subj.data[0]
                topics = sb.table("topics").select("*").eq("subject_id", s["id"]).execute()
                st.markdown(f"""
                <div class="subject-card">
                    <h3>{s['icon']} {s['name']}</h3>
                    <p style="color:#666;">{s['description']}</p>
                    <p><strong>{len(topics.data)}</strong> topics available</p>
                </div>
                """, unsafe_allow_html=True)

# ─── Subjects Page ─────────────────────────────────────
def show_subjects(student, sb):
    st.title("📚 Available Subjects")
    st.caption("Enroll in subjects to access topics, videos, and assignments.")
    
    enrolled = student.get("enrolled_subjects", [])
    subjects = sb.table("subjects").select("*").execute()
    
    for s in subjects.data:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div class="subject-card">
                <h2 style="color:{'#3776AB' if s['name']=='Python' else '#00599C'}">
                    {s['icon']} {s['name']}
                </h2>
                <p>{s['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write("")
            st.write("")
            if s["name"] in enrolled:
                st.success("✅ Enrolled")
                if st.button(f"Unenroll", key=f"un_{s['id']}"):
                    updated = [x for x in enrolled if x != s["name"]]
                    sb.table("students").update(
                        {"enrolled_subjects": updated}
                    ).eq("id", student["id"]).execute()
                    st.session_state.student["enrolled_subjects"] = updated
                    st.rerun()
            else:
                if st.button(f"Enroll Now", key=f"en_{s['id']}", type="primary"):
                    from utils.auth import enroll_subject
                    updated = enroll_subject(student["id"], s["name"], enrolled)
                    st.session_state.student["enrolled_subjects"] = updated
                    st.success(f"Enrolled in {s['name']}!")
                    st.rerun()
        
        # Show topics preview
        topics = sb.table("topics").select("*").eq(
            "subject_id", s["id"]).order("order_index").execute()
        st.write("**Topics covered:**")
        cols = st.columns(4)
        for i, t in enumerate(topics.data):
            with cols[i % 4]:
                st.markdown(f'<span class="topic-badge">📌 {t["title"]}</span>', 
                           unsafe_allow_html=True)
        st.divider()

# ─── Videos Page ───────────────────────────────────────
def show_videos(student, sb):
    st.title("🎬 Video Lessons")
    enrolled = student.get("enrolled_subjects", [])
    
    if not enrolled:
        st.warning("Please enroll in a subject first!")
        return
    
    subject_choice = st.selectbox("Select Subject", enrolled)
    
    subj = sb.table("subjects").select("*").eq("name", subject_choice).execute()
    if not subj.data:
        return
    
    topics = sb.table("topics").select("*").eq(
        "subject_id", subj.data[0]["id"]).order("order_index").execute()
    
    topic_names = [t["title"] for t in topics.data]
    selected_topic = st.selectbox("Select Topic", topic_names)
    topic = next((t for t in topics.data if t["title"] == selected_topic), None)
    
    if topic:
        st.markdown(f"### 📌 {topic['title']}")
        st.caption(topic.get("description", ""))
        
        videos = sb.table("videos").select("*").eq(
            "topic_id", topic["id"]).order("order_index").execute()
        
        if not videos.data:
            st.info("No videos added yet for this topic. Admin can add videos from Supabase dashboard.")
            
            # Show sample placeholder
            st.markdown("""
            **Sample video format to add in Supabase `videos` table:**
```json
            {
              "topic_id": "<topic_uuid>",
              "title": "Introduction to Python Variables",
              "youtube_url": "https://www.youtube.com/embed/kqtD5dpn9C8",
              "duration": "12:30",
              "description": "Learn about variables and data types",
              "order_index": 1
            }
```
            """)
        else:
            for v in videos.data:
                with st.expander(f"🎥 {v['title']} ({v.get('duration','?')})", expanded=False):
                    # Embed YouTube video
                    video_id = v["youtube_url"].split("embed/")[-1] if "embed/" in v["youtube_url"] else v["youtube_url"].split("v=")[-1]
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                    st.markdown(f"""
                    <iframe width="100%" height="400" src="{embed_url}" 
                    frameborder="0" allowfullscreen></iframe>
                    """, unsafe_allow_html=True)
                    
                    st.caption(v.get("description", ""))
                    
                    # Progress tracking
                    prog = sb.table("student_progress").select("*").eq(
                        "student_id", student["id"]).eq("video_id", v["id"]).execute()
                    
                    completed = prog.data and prog.data[0]["completed"]
                    if completed:
                        st.success("✅ Completed!")
                    else:
                        if st.button("Mark as Completed ✅", key=f"vid_{v['id']}"):
                            if prog.data:
                                sb.table("student_progress").update({
                                    "completed": True, 
                                    "completed_at": "now()"
                                }).eq("id", prog.data[0]["id"]).execute()
                            else:
                                sb.table("student_progress").insert({
                                    "student_id": student["id"],
                                    "video_id": v["id"],
                                    "completed": True
                                }).execute()
                            st.rerun()

# ─── Assignments Page ───────────────────────────────────
def show_assignments(student, sb):
    st.title("📝 Assignments")
    enrolled = student.get("enrolled_subjects", [])
    
    if not enrolled:
        st.warning("Please enroll in a subject first!")
        return
    
    col1, col2 = st.columns([3, 1])
    with col1:
        subject_choice = st.selectbox("Select Subject", enrolled)
    with col2:
        st.write("")
        st.write("")
        generate_tab = st.toggle("🤖 AI Generate", value=False)
    
    subj = sb.table("subjects").select("*").eq("name", subject_choice).execute()
    if not subj.data:
        return
    
    topics = sb.table("topics").select("*").eq(
        "subject_id", subj.data[0]["id"]).order("order_index").execute()
    
    selected_topic_name = st.selectbox("Select Topic", [t["title"] for t in topics.data])
    topic = next((t for t in topics.data if t["title"] == selected_topic_name), None)
    
    if not topic:
        return
    
    # AI Generate Assignment
    if generate_tab:
        st.markdown("### 🤖 Generate AI Assignment (CCBP Style)")
        difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
        if st.button("⚡ Generate Assignment", type="primary"):
            with st.spinner("Generating CCBP-style assignment with AI..."):
                try:
                    from utils.ai_assignments import generate_assignment
                    assignment = generate_assignment(selected_topic_name, subject_choice, difficulty)
                    
                    # Save to DB
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
                    st.success("✅ Assignment generated and saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation failed: {e}")
    
    # Show existing assignments
    assignments = sb.table("assignments").select("*").eq(
        "topic_id", topic["id"]).execute()
    
    if not assignments.data:
        st.info("No assignments yet. Use the AI Generate toggle above to create one!")
        return
    
    st.markdown(f"### 📋 Assignments for: {selected_topic_name}")
    
    for a in assignments.data:
        difficulty_class = f"difficulty-{a['difficulty'].lower()}"
        with st.expander(f"🧩 {a['title']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f'<span class="{difficulty_class}">{a["difficulty"]}</span> &nbsp; <strong>🏆 {a["points"]} pts</strong>', 
                           unsafe_allow_html=True)
            
            st.markdown("#### 📋 Problem Statement")
            st.markdown(a["description"])
            
            # Test Cases
            if a.get("test_cases"):
                st.markdown("#### 🧪 Sample Test Cases")
                for i, tc in enumerate(a["test_cases"], 1):
                    st.markdown(f"""
                    **Test {i}:**
                    - **Input:** `{tc.get('input','N/A')}`
                    - **Expected Output:** `{tc.get('expected_output','N/A')}`
                    - **Explanation:** {tc.get('explanation','')}
                    """)
            
            # Hints
            if a.get("hints"):
                with st.expander("💡 Hints"):
                    for h in a["hints"]:
                        st.markdown(f"- {h}")
            
            # Code submission
            st.markdown("#### 💻 Submit Your Solution")
            
            existing = sb.table("submissions").select("*").eq(
                "student_id", student["id"]).eq("assignment_id", a["id"]).execute()
            
            default_code = existing.data[0]["code"] if existing.data else f"# Write your {subject_choice} solution here\n"
            
            lang = "python" if subject_choice == "Python" else "cpp"
            code = st.text_area("Your Code", value=default_code, height=200, key=f"code_{a['id']}")
            
            if st.button("📤 Submit", key=f"sub_{a['id']}", type="primary"):
                if existing.data:
                    sb.table("submissions").update({
                        "code": code, "status": "pending"
                    }).eq("id", existing.data[0]["id"]).execute()
                else:
                    sb.table("submissions").insert({
                        "student_id": student["id"],
                        "assignment_id": a["id"],
                        "code": code,
                        "status": "pending"
                    }).execute()
                st.success("✅ Submitted successfully!")
                st.balloons()

# ─── Cheatsheets Page ──────────────────────────────────
def show_cheatsheets(student, sb):
    st.title("📄 Cheatsheets")
    enrolled = student.get("enrolled_subjects", [])
    
    if not enrolled:
        st.warning("Please enroll in a subject first!")
        return
    
    subject_choice = st.selectbox("Select Subject", enrolled)
    subj = sb.table("subjects").select("*").eq("name", subject_choice).execute()
    if not subj.data:
        return
    
    topics = sb.table("topics").select("*").eq(
        "subject_id", subj.data[0]["id"]).order("order_index").execute()
    
    selected_topic_name = st.selectbox("Select Topic", [t["title"] for t in topics.data])
    topic = next((t for t in topics.data if t["title"] == selected_topic_name), None)
    
    if not topic:
        return
    
    cheatsheets = sb.table("cheatsheets").select("*").eq(
        "topic_id", topic["id"]).execute()
    
    if not cheatsheets.data:
        # Show built-in cheatsheets for common topics
        show_builtin_cheatsheet(subject_choice, selected_topic_name)
    else:
        for c in cheatsheets.data:
            st.markdown(f"### 📄 {c['title']}")
            st.markdown(c["content"])

def show_builtin_cheatsheet(subject, topic):
    """Display built-in cheatsheets."""
    cheatsheets = {
        "Python": {
            "Introduction to Python": """
## 🐍 Python Basics Cheatsheet

### Variables & Data Types
```python
# Integer
age = 25
# Float  
price = 19.99
# String
name = "Alice"
# Boolean
is_active = True

# Type checking
print(type(age))       # <class 'int'>
print(type(name))      # <class 'str'>
```

### Input & Output
```python
name = input("Enter your name: ")
print("Hello,", name)
print(f"Hello, {name}!")  # f-string
```

### Type Conversion
```python
x = int("42")
y = float("3.14")
z = str(100)
```
            """,
            "Control Flow": """
## 🔀 Control Flow Cheatsheet

### If-Else
```python
age = 18
if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")
```

### For Loop
```python
for i in range(5):       # 0,1,2,3,4
    print(i)

for item in ["a","b","c"]:
    print(item)
```

### While Loop
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### Loop Control
```python
for i in range(10):
    if i == 3: continue   # skip 3
    if i == 7: break      # stop at 7
    print(i)
```
            """,
            "Functions": """
## 🔧 Functions Cheatsheet

### Basic Function
```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")
```

### Default Parameters
```python
def greet(name, msg="Hello"):
    return f"{msg}, {name}!"
```

### Lambda Functions
```python
square = lambda x: x ** 2
add = lambda a, b: a + b
```

### *args and **kwargs
```python
def sum_all(*args):
    return sum(args)

def display(**kwargs):
    for k, v in kwargs.items():
        print(f"{k}: {v}")
```
            """,
            "Data Structures": """
## 📦 Data Structures Cheatsheet

### Lists
```python
lst = [1, 2, 3, 4, 5]
lst.append(6)          # add end
lst.insert(0, 0)       # add at index
lst.remove(3)          # remove value
lst.pop()              # remove last
lst.sort()             # sort in-place
```

### Dictionaries
```python
d = {"name": "Alice", "age": 25}
d["city"] = "NYC"      # add/update
del d["age"]           # delete
print(d.keys())
print(d.values())
print(d.items())
```

### Sets
```python
s = {1, 2, 3}
s.add(4)
s.remove(2)
s1 | s2   # union
s1 & s2   # intersection
```

### Tuples
```python
t = (1, 2, 3)    # immutable
a, b, c = t      # unpacking
```
            """,
        },
        "C++": {
            "C++ Basics": """
## ⚡ C++ Basics Cheatsheet

### Hello World
```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
```

### Variables & Types
```cpp
int age = 25;
float price = 19.99f;
double pi = 3.14159;
char grade = 'A';
bool isActive = true;
string name = "Alice";
```

### Input & Output
```cpp
int num;
cin >> num;
cout << "Number: " << num << endl;
```
            """,
            "Control Structures": """
## 🔀 C++ Control Structures

### If-Else
```cpp
int age = 18;
if (age >= 18) {
    cout << "Adult";
} else if (age >= 13) {
    cout << "Teenager";
} else {
    cout << "Child";
}
```

### For Loop
```cpp
for (int i = 0; i < 5; i++) {
    cout << i << " ";
}
```

### While Loop
```cpp
int i = 0;
while (i < 5) {
    cout << i++;
}
```

### Switch
```cpp
switch (grade) {
    case 'A': cout << "Excellent"; break;
    case 'B': cout << "Good"; break;
    default:  cout << "Average";
}
```
            """,
            "Pointers & References": """
## 🔗 Pointers & References Cheatsheet

### Pointers
```cpp
int x = 10;
int* ptr = &x;        // ptr stores address of x
cout << *ptr;         // dereference: prints 10
*ptr = 20;            // changes x to 20

int* arr = new int[5]; // dynamic allocation
delete[] arr;          // free memory
```

### References
```cpp
int x = 10;
int& ref = x;   // ref is alias for x
ref = 20;       // x is now 20
```

### Pass by Pointer vs Reference
```cpp
void byPointer(int* p) { *p = 100; }
void byReference(int& r) { r = 100; }

int val = 0;
byPointer(&val);    // pass address
byReference(val);   // pass directly
```
            """,
            "STL - Standard Template Library": """
## 📚 STL Cheatsheet

### Vector
```cpp
#include <vector>
vector<int> v = {1, 2, 3};
v.push_back(4);
v.pop_back();
v.size();
v[0];
```

### Map
```cpp
#include <map>
map<string,int> m;
m["Alice"] = 95;
m["Bob"] = 87;
for (auto& p : m)
    cout << p.first << ": " << p.second;
```

### Set
```cpp
#include <set>
set<int> s = {5, 3, 1, 4, 2};
// auto-sorted, unique
s.insert(6);
s.erase(3);
s.count(4); // 1 if exists
```

### Algorithm
```cpp
#include <algorithm>
sort(v.begin(), v.end());
reverse(v.begin(), v.end());
int mn = *min_element(v.begin(), v.end());
```
            """,
        }
    }
    
    if subject in cheatsheets and topic in cheatsheets[subject]:
        st.markdown(cheatsheets[subject][topic])
    else:
        st.info(f"Cheatsheet for **{topic}** coming soon! Add it via Supabase dashboard.")

# ─── Settings Page ─────────────────────────────────────
def show_settings(student, sb):
    st.title("⚙️ Settings")
    st.subheader("Profile Information")
    
    st.text_input("Name", value=student["name"], disabled=True)
    st.text_input("Email", value=student["email"], disabled=True)
    
    enrolled = student.get("enrolled_subjects", [])
    st.subheader("Enrolled Subjects")
    if enrolled:
        for s in enrolled:
            st.markdown(f"✅ **{s}**")
    else:
        st.info("Not enrolled in any subject yet.")
    
    st.subheader("Change Password")
    with st.form("change_password"):
        new_pass = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        if st.form_submit_button("Update Password", type="primary"):
            if new_pass != confirm:
                st.error("Passwords don't match!")
            elif len(new_pass) < 6:
                st.error("Password too short!")
            else:
                import hashlib
                sb.table("students").update({
                    "password_hash": hashlib.sha256(new_pass.encode()).hexdigest()
                }).eq("id", student["id"]).execute()
                st.success("Password updated!")

# ─── Main Entry ────────────────────────────────────────
if st.session_state.student is None:
    show_auth()
else:
    show_app()
