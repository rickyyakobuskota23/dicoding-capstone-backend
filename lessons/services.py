import os
import json
from google import genai
from google.genai import types

class LessonGeneratorService:
    def __init__(self):
        self._api_key = os.environ.get("GOOGLE_API_KEY")

    def generate_lesson_plan(self, form_data):
        prompt = self._build_prompt(form_data)

        try:
            if not self._api_key:
                print("GOOGLE_API_KEY not found in environment variables")
                return self._get_fallback_plan(form_data)

            client = genai.Client(api_key=self._api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            if not response or not response.text:
                print("Empty response from Gemini API")
                return self._get_fallback_plan(form_data)

            return json.loads(response.text)
        except Exception as e:
            error_str = str(e).lower()
            print(f"Error in Gemini generation: {error_str}")

            if any(indicator in error_str for indicator in ["429", "quota", "rate_limit", "resource_exhausted"]):
                print("API limit or quota exceeded, returning fallback data")
                return self._get_fallback_plan(form_data)

            return self._get_fallback_plan(form_data)

    def _get_fallback_plan(self, data):
        """
        Provides a static fallback lesson plan when the API is unavailable.
        """
        subject = data.get('subject', 'General')
        topic = data.get('topic', 'Lesson')
        
        return {
            "overview": {
                "duration": "45-60 minutes",
                "materials": [
                    "Textbooks and notebooks",
                    "Whiteboard and markers",
                    "Reference handouts",
                    "Digital devices (optional)"
                ]
            },
            "objectives": [
                f"Understand the core concepts of {topic}",
                f"Apply knowledge of {subject} in practical exercises",
                "Demonstrate mastery through a summary activity"
            ],
            "differentiation": {
                "content": data.get('content_diff_description') or ("Provided through varied reading levels and supplemental resources." if data.get('contentDiff') else None),
                "process": data.get('process_diff_description') or ("Students work in flexible groups based on readiness and interest." if data.get('processDiff') else None),
                "product": data.get('product_diff_description') or ("Students can choose between a written summary, a visual poster, or an oral presentation." if data.get('productDiff') else None),
                "environment": data.get('environment_diff_description') or ("Strategic seating and quiet zones are established for focused work." if data.get('environmentDiff') else None)
            },
            "activities": [
                {
                    "tier": "Tier 1 (Support)",
                    "title": "Guided Practice",
                    "content": "Step-by-step walk-through of the main concept with high teacher support.",
                    "color": "blue"
                },
                {
                    "tier": "Tier 2 (Core)",
                    "title": "Independent Application",
                    "content": "Standard exercises to reinforce the learning objectives.",
                    "color": "purple"
                },
                {
                    "tier": "Tier 3 (Extension)",
                    "title": "Advanced Inquiry",
                    "content": "Complex problem-solving or research-based extension activity.",
                    "color": "green"
                }
            ],
            "is_fallback": True,
            "error_message": "Using a smart template as the AI service is currently busy or unavailable."
        }

    def _build_prompt(self, data):
        subject = data.get('subject')
        grade_level = data.get('gradeLevel')
        topic = data.get('topic')
        learning_objective = data.get('learningObjective')
        class_size = data.get('classSize')
        diversity_level = data.get('diversityLevel')
        
        diff_strategies = []
        if data.get('contentDiff'): diff_strategies.append("Content")
        if data.get('processDiff'): diff_strategies.append("Process")
        if data.get('productDiff'): diff_strategies.append("Product")
        if data.get('environmentDiff'): diff_strategies.append("Environment")
        
        diff_text = ", ".join(diff_strategies) if diff_strategies else "General instruction"

        prompt = f"""
        Expert Educator Persona: Generate a professional, concise, differentiated lesson plan.
        
        Context:
        - Subject: {subject}
        - Grade: {grade_level}
        - Topic: {topic}
        - Objective: {learning_objective}
        - Class Size: {class_size}
        - Diversity: {diversity_level}
        - Focus Differentiation: {diff_text}
        
        Strict JSON Output Format:
        {{
          "overview": {{ "duration": "string", "materials": ["string"] }},
          "objectives": ["string"],
          "differentiation": {{
            "content": "One paragraph explaining how content is differentiated for this lesson, or null if not applicable",
            "process": "One paragraph explaining how process is differentiated for this lesson, or null if not applicable",
            "product": "One paragraph explaining how product/assessment is differentiated, or null if not applicable",
            "environment": "One paragraph explaining how environment is adjusted, or null if not applicable"
          }},
          "activities": [
            {{ "tier": "Tier 1 (Support)", "title": "string", "content": "Concise activity description", "color": "blue" }},
            {{ "tier": "Tier 2 (Core)", "title": "string", "content": "Concise activity description", "color": "purple" }},
            {{ "tier": "Tier 3 (Extension)", "title": "string", "content": "Concise activity description", "color": "green" }}
          ]
        }}
        
        Instructions:
        1. Keep descriptions high-impact and brief to minimize token usage.
        2. Differentiation paragraphs MUST be present if the strategy was requested.
        3. Ensure activities clearly reflect the requested differentiation strategies.
        """
        return prompt
