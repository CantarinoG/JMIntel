import json
from src.ai_services.base_ai_service import BaseAIService
from src.models.job import Job

class JobProcessor:
    '''
    Processes job descriptions extracting data from them.
    '''

    def __init__(self, ai_service: BaseAIService):
        self.ai_service = ai_service

    def process(self, job: Job) -> bool:
        """
        Process a job description, using the AI service to extract data from it.
        """
        prompt = self._build_prompt(job)
        try:
            response_text = self.ai_service.process(prompt)
            clean_json = response_text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_json)

            job.job_category = data.get("job_category")
            job.seniority_level = data.get("seniority_level")
            job.employment_type = data.get("employment_type")
            job.contract_duration = data.get("contract_duration")
            job.remote_type = data.get("remote_type")
            job.language = data.get("language")
            job.monthly_salary_min_brl = data.get("monthly_salary_min_brl")
            job.monthly_salary_max_brl = data.get("monthly_salary_max_brl")
            job.experience_years_min = data.get("experience_years_min")
            job.hard_skills = data.get("hard_skills")

            return True
        except Exception as e:
            print(f"Error processing job: {e}")
            return False
        
    def _build_prompt(self, job: Job) -> str:
        """
        Construct the high-density prompt for the AI service.
        """
        return f"""
        You are an expert Job Market Data Analyst. Your task is to extract structured information from the following job listing.

        ### JOB TITLE:
        {job.title}

        ### JOB DESCRIPTION:
        {job.description}

        ### EXTRACTION RULES:
        1. **JSON FORMAT**: Return ONLY a valid JSON object. No markdown, no conversational text.
        2. **NULL VALUES**: Use null if the information is not explicitly or implicitly mentioned.
        3. **SALARY**: 
           - Convert all values to Monthly BRL (Brazilian Real).
           - If a range is provided, fill both min and max. 
           - If hourly, assume 160 hours/month.
           - If USD/EUR, convert using current average rates (~5.5 for USD, ~6.0 for EUR).
        4. **SENIORITY**: Strictly choose one: Intern, Junior, Mid-Level, Senior, Lead, Executive.
        5. **REMOTE**: Strictly choose one: Remote, Hybrid, On-site.
        6. **SKILLS**: Extract a list of specific technical skills/tools (e.g., ["Python", "AWS", "SQL"]).

        ### SCHEMA TO FOLLOW:
        {{
            "job_category": "Short identifier (e.g., Backend, Frontend, Data Science, DevOps, HR)",
            "seniority_level": "Strictly Internship, Junior, Mid-Level, Senior, Lead, or Executive",
            "employment_type": "Full-time, Part-time, Freelance, or Internship",
            "contract_duration": "Permanent or Temporary",
            "remote_type": "Remote, Hybrid, or On-site",
            "language": "Primary language required for the job",
            "monthly_salary_min_brl": float or null,
            "monthly_salary_max_brl": float or null,
            "experience_years_min": float or null,
            "hard_skills": ["skill1", "skill2", ...]
        }}
        """