import requests
from django.conf import settings

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-3.5-turbo"


def generate_ai_feedback(summary_data):
    """
    Generate concept-level, resource-backed AI feedback
    in guaranteed bullet-point format.
    """

    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        raise Exception("OPENAI_API_KEY not configured in settings.")

    prompt = f"""
You are an expert computer science mentor.

Generate learning feedback in STRICT BULLET POINT FORMAT.

MANDATORY RULES:
- EACH line MUST start with "• "
- Output ONLY bullet points
- 6 to 10 bullet points
- Natural, clear, and student-friendly
- Mention specific weak CONCEPTS by name
- Suggest WHAT to study and WHERE (GeeksforGeeks, TutorialsPoint, YouTube, Courses)
- Do NOT write paragraphs
- Do NOT number points
- Do NOT use emojis
- Do NOT include headings or titles
- If possible add urls of the resources so that user can directly jump and learn wherever user is lacking behind.
STUDENT PERFORMANCE DATA:
{summary_data}

OUTPUT EXAMPLE (FOLLOW EXACTLY):
• You are comfortable with basic OS concepts but struggle with advanced topics.
• Revise Deadlock Prevention and Deadlock Avoidance from GeeksforGeeks.
• Practice Process Scheduling algorithms like FCFS and Round Robin.
• Watch a short tutorial on CPU Scheduling to improve conceptual clarity.
• Focus on medium-level quizzes before attempting hard difficulty.
• Take concept-based quizzes after revision to reinforce learning.

OUTPUT ONLY BULLET POINTS.
"""

    response = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=30,
    )

    response.raise_for_status()

    # ---------------------------
    # 🔐 SAFETY POST-PROCESSING
    # ---------------------------
    text = response.json()["choices"][0]["message"]["content"].strip()

    lines = text.split("\n")
    bullets = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("•"):
            bullets.append(line)
        else:
            # Force bullet if model slips
            bullets.append("• " + line.lstrip("- ").strip())

    return "\n".join(bullets)
