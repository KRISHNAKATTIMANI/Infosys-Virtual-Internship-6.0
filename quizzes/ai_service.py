# quizzes/ai_service.py
"""
Quiz Question Generator using OpenAI GPT API.
Generates quiz questions based on topic, category, and difficulty.
"""
import json
import re
import os
import requests
from django.conf import settings


# API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


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

    if len(questions) < count:
        print(f"[AI Service] Warning: Got {len(questions)} questions, expected {count}")

    required = ["question", "option_a", "option_b", "option_c", "option_d", "correct_answer"]

    for q in questions:
        for f in required:
            if f not in q:
                raise ValueError(f"Missing field: {f}")

        if q["correct_answer"] not in ["A", "B", "C", "D"]:
            raise ValueError("correct_answer must be A/B/C/D")

    return questions


def build_prompt(topic, category, difficulty, count, concepts):
    """
    Build the prompt for quiz generation.
    """
    # Check if concepts contain document content (file upload case)
    is_document_based = concepts and len(concepts) > 0 and concepts[0].startswith("Based on the following content:")
    
    if is_document_based:
        # Document-based quiz prompt - questions MUST be from the document only
        document_content = concepts[0].replace("Based on the following content:\n", "")
        return f"""You are an expert exam question setter. You must create quiz questions ONLY from the provided document content.

DOCUMENT CONTENT:
{document_content}

TASK:
Generate exactly {count} multiple choice questions based STRICTLY on the above content.
Difficulty Level: {difficulty}

CRITICAL REQUIREMENTS:
1. ALL questions must be answerable using ONLY the information in the document above
2. Do NOT include any questions that require outside knowledge
3. Questions should test understanding of the document's content
4. Match the {difficulty} difficulty level:
   - Easy: Direct facts from the document
   - Medium: Understanding and interpreting the document
   - Hard: Analysis and inference from the document

OUTPUT FORMAT - Return ONLY a JSON array:
[
  {{
    "question": "Question based on the document?",
    "option_a": "First option",
    "option_b": "Second option", 
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_answer": "A",
    "explanation": "Brief explanation referencing the document"
  }}
]

IMPORTANT: Return ONLY the JSON array. No additional text."""
    
    else:
        # Topic-based quiz prompt
        concept_block = ""
        if concepts:
            concept_block = "\n".join(
                f"{i+1}. {concept}" for i, concept in enumerate(concepts)
            )
        else:
            concept_block = f"Generate questions about {topic} in the {category} category."

        return f"""You are an expert exam question setter for competitive exams.

Topic: {topic}
Category: {category}
Difficulty: {difficulty}

Generate exactly {count} UNIQUE multiple choice questions about {topic}.

REQUIREMENTS:
1. Each question must be clear and unambiguous
2. All 4 options must be plausible
3. Only one correct answer per question
4. Questions should match the {difficulty} difficulty level:
   - Easy: Basic recall and simple concepts
   - Medium: Application and understanding
   - Hard: Analysis, complex scenarios, edge cases

{f"Focus on these concepts: {concept_block}" if concepts else ""}

OUTPUT FORMAT - Return ONLY a JSON array with exactly {count} questions:
[
  {{
    "question": "Your question text here?",
    "option_a": "First option",
    "option_b": "Second option", 
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_answer": "A",
    "explanation": "Brief explanation of why this is correct"
  }}
]

IMPORTANT: Return ONLY the JSON array. No text before or after.
"""


def generate_quiz_questions(topic, category, difficulty, count=10, concepts=None):
    """
    Generate MCQs using OpenAI GPT API.
    """
    print(f"[AI Service] Generating {count} questions for {topic} ({category}) - {difficulty}")
    
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY not configured. Please set it in your .env file.")
    
    prompt = build_prompt(topic, category, difficulty, count, concepts)
    
    try:
        response = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an expert quiz question generator. Return only valid JSON arrays with quiz questions."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
            },
            timeout=60
        )

        if response.status_code == 401:
            raise Exception("Invalid OpenAI API key. Please check your OPENAI_API_KEY in .env file.")
        
        if response.status_code == 429:
            raise Exception("OpenAI API rate limit exceeded. Please wait a moment and try again.")
        
        if response.status_code >= 500:
            raise Exception(f"OpenAI server error ({response.status_code}). Please try again later.")

        response.raise_for_status()
        data = response.json()
        
        message_content = data["choices"][0]["message"]["content"]
        cleaned = clean_json(message_content)
        questions = json.loads(cleaned)
        
        print(f"[AI Service] Successfully generated {len(questions)} questions!")
        return validate_questions(questions, count)

    except requests.exceptions.Timeout:
        raise Exception("OpenAI API request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")


def generate_feedback(quiz_data, score, total, difficulty):
    """
    Generate feedback for quiz results.
    """
    percentage = (score / total) * 100 if total > 0 else 0
    
    if percentage >= 90:
        return {
            "overall": "Excellent performance! 🎉",
            "strengths": ["Strong understanding of concepts", "Great attention to detail"],
            "improvements": ["Keep practicing to maintain your skills"],
            "tips": ["Try harder difficulty levels", "Help others learn"],
            "score_analysis": f"You scored {score}/{total} ({percentage:.0f}%)"
        }
    elif percentage >= 70:
        return {
            "overall": "Good job! Keep it up! 👍",
            "strengths": ["Solid foundation in the subject", "Good problem-solving"],
            "improvements": ["Review the questions you got wrong", "Practice more"],
            "tips": ["Focus on understanding concepts deeply", "Take notes while studying"],
            "score_analysis": f"You scored {score}/{total} ({percentage:.0f}%)"
        }
    elif percentage >= 50:
        return {
            "overall": "Not bad, but room for improvement 📚",
            "strengths": ["You understand some basics", "You're making progress"],
            "improvements": ["Review fundamental concepts", "Practice regularly"],
            "tips": ["Start with easier topics", "Use multiple learning resources"],
            "score_analysis": f"You scored {score}/{total} ({percentage:.0f}%)"
        }
    else:
        return {
            "overall": "Keep learning, you'll get there! 💪",
            "strengths": ["You took the quiz - that's a start!", "You're willing to learn"],
            "improvements": ["Go back to basics", "Study the material again"],
            "tips": ["Don't give up", "Try easier quizzes first", "Ask for help if needed"],
            "score_analysis": f"You scored {score}/{total} ({percentage:.0f}%)"
        }

