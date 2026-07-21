import os
import json
import requests

XAI_ENDPOINT = "https://api.x.ai/v1/chat/completions"

# Comprehensive list of standard tech skills for multi-select options
STANDARD_SKILLS_CATALOG = [
    "Python", "SQL", "Git", "Streamlit", "Flask", "Pandas", "NumPy",
    "PyTorch", "TensorFlow", "LangChain", "LlamaIndex", "AWS", "Docker",
    "Kubernetes", "React", "TypeScript", "JavaScript", "C++", "Java",
    "Scikit-Learn", "PostgreSQL", "MongoDB", "Vector DBs", "REST APIs",
    "FastAPI", "Agile", "CI/CD", "Prompt Engineering", "OpenAI API"
]

def generate_role_from_grok(topic: str, api_key: str = None) -> dict:
    """
    Queries the xAI API (Grok) to analyze real-time market trends on X (Twitter)
    and returns a structured JSON dictionary containing title, summary, skills list,
    requirements, and full description string.
    
    Parameters:
        topic (str): The domain or role title to research.
        api_key (str): Optional xAI API Key.
        
    Returns:
        dict: Structured role object containing:
            - 'title': str
            - 'summary': str
            - 'skills': list[str]
            - 'requirements': str
            - 'full_description': str
    """
    key = api_key or os.environ.get("XAI_API_KEY")
    
    if key and key.strip():
        try:
            headers = {
                "Authorization": f"Bearer {key.strip()}",
                "Content-Type": "application/json"
            }
            prompt = (
                f"You are Grok analyzing real-time tech discussions and industry trends on X (Twitter).\n"
                f"Generate a structured Job Description and skill set for an emerging role in: '{topic}'.\n\n"
                f"You MUST respond ONLY with a valid JSON object matching this schema:\n"
                f"{{\n"
                f'  "title": "Senior {topic} Specialist",\n'
                f'  "summary": "Short 2-sentence summary of emerging X/Twitter trends for this role.",\n'
                f'  "skills": ["Python", "SQL", "Git", "Streamlit", "Docker"],\n'
                f'  "requirements": "Key responsibilities and background requirements...",\n'
                f'  "full_description": "Full structured job description text..."\n'
                f"}}\n"
            )
            payload = {
                "model": "grok-beta",
                "messages": [
                    {"role": "system", "content": "You are Grok, an expert AI analyst returning strictly valid JSON output for career and tech trend queries."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            response = requests.post(XAI_ENDPOINT, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Extract JSON block if wrapped in markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                parsed_json = json.loads(content)
                return parse_and_validate_role_dict(parsed_json, topic)
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                return generate_fallback_trend_dict(topic, f"xAI API Notice ({response.status_code}): {error_msg}")
        except Exception as e:
            return generate_fallback_trend_dict(topic, f"Parsing Exception: {str(e)}")
    else:
        return generate_fallback_trend_dict(topic, "Using AI Trend Watcher mode. (Enter an xAI API Key in the sidebar for live Grok API calls)")

def parse_and_validate_role_dict(data: dict, topic: str) -> dict:
    """
    Validates and ensures all required keys are present in the JSON dictionary.
    """
    title = data.get("title", f"Senior {topic} Specialist")
    summary = data.get("summary", f"High market demand detected on X (Twitter) for {topic}.")
    skills = data.get("skills", ["Python", "SQL", "Git", "Streamlit", "Pandas", "AWS", "Docker"])
    requirements = data.get("requirements", f"- Strong expertise in {topic}.\n- Experience with modern software stacks.\n- Proven background in team collaboration.")
    
    full_desc = data.get("full_description")
    if not full_desc:
        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        full_desc = f"# Job Title: {title}\n\n## Market Summary\n{summary}\n\n## Core Skills & Tools\n{skills_str}\n\n## Requirements\n{requirements}"
        
    return {
        "title": title,
        "summary": summary,
        "skills": list(skills) if isinstance(skills, list) else ["Python", "SQL", "Git"],
        "requirements": requirements,
        "full_description": full_desc
    }

def generate_fallback_trend_dict(topic: str, note: str = "") -> dict:
    """
    Generates a structured fallback role dictionary with extracted skills.
    """
    topic_clean = topic.strip().title() if topic else "Emerging Technology Specialist"
    
    # Intelligently select skills based on topic
    if "ai" in topic.lower() or "machine learning" in topic.lower() or "llm" in topic.lower():
        extracted_skills = ["Python", "PyTorch", "LangChain", "LlamaIndex", "Streamlit", "Pandas", "Vector DBs", "Git", "SQL"]
    elif "cloud" in topic.lower() or "devops" in topic.lower():
        extracted_skills = ["Docker", "Kubernetes", "AWS", "Python", "CI/CD", "Git", "REST APIs"]
    elif "full stack" in topic.lower() or "web" in topic.lower():
        extracted_skills = ["Python", "TypeScript", "React", "Flask", "Streamlit", "SQL", "Git", "REST APIs"]
    else:
        extracted_skills = ["Python", "SQL", "Git", "Streamlit", "Pandas", "AWS", "Docker", "Agile"]
        
    summary_text = f"Recent discussions across X (Twitter) highlight rapid adoption and high demand for {topic_clean} specialists."
    req_text = f"- Proven hands-on experience developing solutions in {topic_clean}.\n- Experience deploying applications to cloud infrastructure (AWS/Docker).\n- Strong communication skills in Agile team environments."
    
    full_desc = f"""# Job Title: Senior {topic_clean} Engineer

## Industry Market Summary (X/Twitter Trend Analysis)
*Status: {note}*
{summary_text}

## Core Technical Skills & Tooling
- **Primary Technologies**: {', '.join(extracted_skills)}

## Requirements & Key Responsibilities
{req_text}
"""

    return {
        "title": f"Senior {topic_clean} Engineer",
        "summary": summary_text,
        "skills": extracted_skills,
        "requirements": req_text,
        "full_description": full_desc
    }
