# quizzes/ai_service.py
import json
import re
import requests
from django.conf import settings


ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY
ANTHROPIC_MODEL = "claude-opus-4-20250514"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"



def clean_json(text: str) -> str:
    """
    Removes markdown code fences and extracts JSON array from text.
    """
    text = text.strip()

    # Remove ```json or ``` fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    # Extract JSON array using regex
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, flags=re.DOTALL)
    if match:
        return match.group(1)

    return text


def validate_questions(questions, count):
    """
    Ensures JSON array is valid.
    """
    if not isinstance(questions, list):
        raise ValueError("AI did not return a JSON array.")

    if len(questions) != count:
        raise ValueError(f"Expected {count} questions, got {len(questions)}.")

    required = ["question", "option_a", "option_b", "option_c", "option_d", "correct_answer"]

    for q in questions:
        for f in required:
            if f not in q:
                raise ValueError(f"Missing field: {f}")

        if q["correct_answer"] not in ["A", "B", "C", "D"]:
            raise ValueError("correct_answer must be A/B/C/D")

    return questions


def generate_quiz_questions(
    topic,
    category,
    difficulty,
    count=10,
    concepts=None
):
    """
    Generate MCQs using Anthropic Claude Opus 4.5
    """

    if not ANTHROPIC_API_KEY:
        raise Exception("ANTHROPIC_API_KEY not found in settings.")

    # 🔹 CONCEPT AWARE PROMPT ADDITION
    concept_block = ""
    if concepts:
        concept_block = "\n".join(
            f"{i+1}. {concept}" for i, concept in enumerate(concepts)
        )

    prompt = f"""
You are an expert exam question setter for competitive exams.

Topic: {topic}
Category: {category}
Difficulty: {difficulty}

CRITICAL INSTRUCTIONS:
1. Generate exactly {count} UNIQUE multiple choice questions.
2. Each question must TEST KNOWLEDGE about a concept, NOT ask what the concept is called.
3. Questions should test UNDERSTANDING, APPLICATION, or ANALYSIS of the concept.

❌ BAD QUESTION TYPES (DO NOT GENERATE THESE):
- "What concept describes...?" 
- "Which term refers to...?"
- "What is the name of...?"
- "Which of the following is/describes...?"

✅ GOOD QUESTION TYPES (GENERATE THESE):
- Scenario-based: "Given this situation, what would happen?"
- Application: "How would you solve this problem?"
- Analysis: "What is the output/result of...?"
- Calculation: "Calculate/Find the value of..."
- Comparison: "What is the difference between X and Y in this case?"

CONCEPTS TO TEST (one question per concept):
{concept_block}

For each concept, create a question that requires the student to APPLY or UNDERSTAND the concept, not just remember its name.

DIFFICULTY GUIDELINES:
- Easy: Basic application, straightforward scenarios
- Medium: Multi-step problems, edge cases
- Hard: Complex scenarios, tricky edge cases, optimization

OUTPUT FORMAT - Return ONLY this JSON array:
[
  {{
    "question": "A practical question testing the concept...",
    "option_a": "plausible answer",
    "option_b": "plausible answer", 
    "option_c": "plausible answer",
    "option_d": "plausible answer",
    "correct_answer": "A",
    "explanation": "Detailed explanation of why this is correct and others are wrong"
  }}
]

Return ONLY the JSON array. No text outside JSON.
"""

    try:
        response = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": ANTHROPIC_MODEL,
                "max_tokens": 4096,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                # 🔹 IMPORTANT: INCREASE TEMPERATURE FOR VARIETY
                "temperature": 0.85,
            },
            timeout=45
        )

        response.raise_for_status()
        data = response.json()

        # Extract text from model response
        message = data["content"][0]["text"]

        # Clean and extract JSON
        cleaned = clean_json(message)

        # Parse JSON array
        questions = json.loads(cleaned)

        # Validate structure
        return validate_questions(questions, count)

    except Exception as e:
        raise Exception(f"Failed to generate quiz questions: {e}")

