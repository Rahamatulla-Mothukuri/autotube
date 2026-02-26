import os
import json
import asyncio
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SCRIPT_PROMPT = """You are an expert YouTube video scriptwriter. Based on the research data provided, create a compelling video script.

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Catchy YouTube video title",
  "description": "YouTube video description (2-3 sentences)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "narration": "Full narration text that will be converted to speech. Should be 200-400 words, engaging, educational, and flow naturally when spoken. No stage directions, just the spoken words.",
  "scenes": [
    {{
      "id": 1,
      "text": "Short scene description for stock footage search (3-5 words)",
      "search_query": "pexels search query for this scene",
      "duration": 5
    }}
  ]
}}

Create 6-8 scenes. Each scene should have a duration of 4-7 seconds.
The total narration should match the total scene duration (roughly 150 words per minute speaking rate).

Topic: {topic}

Research Data:
{research}

Remember: Return ONLY the JSON object, no other text."""

async def generate_script(topic: str, research_data: dict) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")

    prompt = SCRIPT_PROMPT.format(
        topic=topic,
        research=research_data.get("combined_text", "")[:4000]
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000,
            }
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"].strip()
    
    # Clean up JSON if wrapped in markdown
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    script = json.loads(content)
    
    # Validate required fields
    required = ["title", "description", "narration", "scenes", "tags"]
    for field in required:
        if field not in script:
            raise ValueError(f"Missing field in script: {field}")

    return script
