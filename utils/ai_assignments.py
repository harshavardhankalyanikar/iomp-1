from groq import Groq
import json, os
from dotenv import load_dotenv
load_dotenv()
def evaluate_submission(code, assignment_title, description, test_cases, subject_name):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a programming assignment evaluator.

Assignment: {assignment_title}
Subject: {subject_name}
Problem: {description}

Test Cases:
{json.dumps(test_cases, indent=2)}

Student's Code:
```
{code}
```

Evaluate the code and return ONLY valid JSON:
{{
  "status": "passed" or "failed",
  "score": <number 0-10>,
  "feedback": "Detailed feedback explaining what is correct, what is wrong, and how to improve"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800
    )

    raw = response.choices[0].message.content.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    raw = raw[start:end]
    return json.loads(raw)
def generate_assignment(topic_title, subject_name, difficulty="Easy"):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file!")

    client = Groq(api_key=api_key)

    prompt = f"""You are an expert programming instructor creating assignments in the style of CCBP (NxtWave Academy).

Create a coding assignment for:
- Subject: {subject_name}
- Topic: {topic_title}
- Difficulty: {difficulty}

Return ONLY valid JSON with no markdown, no code fences, no extra text whatsoever:
{{
  "title": "Assignment title",
  "description": "Detailed CCBP-style problem statement with clear sample input/output table",
  "test_cases": [
    {{"input": "sample input", "expected_output": "expected output", "explanation": "reason"}},
    {{"input": "edge case input", "expected_output": "expected output", "explanation": "edge case reason"}}
  ],
  "hints": ["hint 1", "hint 2", "hint 3"],
  "expected_concepts": ["concept1", "concept2"],
  "points": 10
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    # Extract JSON if there's extra text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end != 0:
        raw = raw[start:end]

    return json.loads(raw)
