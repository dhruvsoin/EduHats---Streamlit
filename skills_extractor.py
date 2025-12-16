import os
from groq import Groq
from dotenv import load_dotenv
import json
from typing import List, Dict, Set

load_dotenv()


class SkillsExtractor:
    """Extracts skills from job descriptions using Groq AI"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def extract_skills_from_job(self, job: Dict) -> Dict:
        """
        Extract skills from a single job posting
        
        Args:
            job: Job dictionary with title, company, description
            
        Returns:
            Dictionary with categorized skills
        """
        job_text = f"""
        Job Title: {job.get('title', '')}
        Company: {job.get('company', '')}
        Description: {job.get('description', '')}
        """
        
        prompt = f"""
        Analyze the following job posting and extract all skills mentioned.
        Categorize them into:
        1. Technical Skills (programming languages, frameworks, tools, technologies)
        2. Soft Skills (communication, leadership, teamwork, etc.)
        3. Domain Knowledge (industry-specific knowledge, certifications)
        4. Tools & Platforms (software, cloud platforms, databases)
        
        Job Posting:
        {job_text}
        
        Return the result as a JSON object with the following structure:
        {{
            "technical_skills": ["skill1", "skill2", ...],
            "soft_skills": ["skill1", "skill2", ...],
            "domain_knowledge": ["knowledge1", "knowledge2", ...],
            "tools_platforms": ["tool1", "tool2", ...]
        }}
        
        Only return the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR analyst specializing in extracting skills from job descriptions. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=600
            )
            
            result = response.choices[0].message.content
            print(f"\n[DEBUG] Raw API response: {result[:200]}...")  # Show first 200 chars
            
            # Remove markdown code blocks if present
            cleaned_result = result.strip()
            if cleaned_result.startswith("```"):
                # Remove ```json or ``` at start
                lines = cleaned_result.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]  # Remove first line
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]  # Remove last line
                cleaned_result = '\n'.join(lines)
            
            # Parse JSON response
            try:
                skills_data = json.loads(cleaned_result)
                print(f"[DEBUG] Successfully parsed JSON")
                print(f"[DEBUG] Found {len(skills_data.get('technical_skills', []))} technical skills")
            except json.JSONDecodeError as json_err:
                print(f"[DEBUG] JSON parse error: {json_err}")
                print(f"[DEBUG] Trying to extract JSON from response...")
                # Try to extract JSON from response
                start = cleaned_result.find('{')
                end = cleaned_result.rfind('}') + 1
                if start != -1 and end != 0:
                    try:
                        skills_data = json.loads(cleaned_result[start:end])
                        print(f"[DEBUG] Successfully extracted and parsed JSON")
                    except Exception as e2:
                        print(f"[DEBUG] Failed to parse extracted JSON: {e2}")
                        skills_data = {
                            "technical_skills": [],
                            "soft_skills": [],
                            "domain_knowledge": [],
                            "tools_platforms": []
                        }
                else:
                    print(f"[DEBUG] No JSON found in response")
                    skills_data = {
                        "technical_skills": [],
                        "soft_skills": [],
                        "domain_knowledge": [],
                        "tools_platforms": []
                    }
            
            return skills_data
            
        except Exception as e:
            print(f"\n[ERROR] Exception during API call: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "technical_skills": [],
                "soft_skills": [],
                "domain_knowledge": [],
                "tools_platforms": []
            }
    
    def extract_skills_from_jobs(self, jobs: List[Dict]) -> Dict:
        """
        Extract skills from multiple job postings in a SINGLE batch API call
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Aggregated skills with frequency counts
        """
        print(f"\n🚀 Extracting skills from {len(jobs)} jobs in ONE batch call...")
        
        # Create a concise summary of all jobs for batch processing
        jobs_summary = []
        for idx, job in enumerate(jobs[:20], 1):  # Limit to 20 jobs to avoid token limits
            jobs_summary.append(f"{idx}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}: {job.get('description', '')[:200]}")
        
        batch_text = "\n\n".join(jobs_summary)
        
        prompt = f"""
        Analyze the following {len(jobs_summary)} job postings and extract ALL unique skills mentioned across them.
        Categorize them into:
        1. Technical Skills (programming languages, frameworks, tools, technologies)
        2. Soft Skills (communication, leadership, teamwork, etc.)
        3. Domain Knowledge (industry-specific knowledge, certifications)
        4. Tools & Platforms (software, cloud platforms, databases)
        
        Job Postings:
        {batch_text}
        
        Return ONLY a JSON object with this structure (no markdown, no extra text):
        {{
            "technical_skills": {{"skill1": frequency, "skill2": frequency, ...}},
            "soft_skills": {{"skill1": frequency, "skill2": frequency, ...}},
            "domain_knowledge": {{"knowledge1": frequency, "knowledge2": frequency, ...}},
            "tools_platforms": {{"tool1": frequency, "tool2": frequency, ...}}
        }}
        
        Count how many times each skill appears across all jobs.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR analyst. Extract skills from job descriptions and return ONLY valid JSON with frequency counts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1200
            )
            
            result = response.choices[0].message.content
            print(f"✅ Received batch response")
            
            # Clean and parse JSON
            cleaned_result = result.strip()
            if cleaned_result.startswith("```"):
                lines = cleaned_result.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned_result = '\n'.join(lines)
            
            aggregated_skills = json.loads(cleaned_result)
            
            # Sort skills by frequency
            for category in aggregated_skills:
                aggregated_skills[category] = dict(
                    sorted(aggregated_skills[category].items(), 
                           key=lambda x: x[1], 
                           reverse=True)
                )
            
            print(f"✅ Extracted {sum(len(v) for v in aggregated_skills.values())} unique skills")
            return aggregated_skills
            
        except Exception as e:
            print(f"❌ Error in batch extraction: {e}")
            # Fallback to empty structure
            return {
                "technical_skills": {},
                "soft_skills": {},
                "domain_knowledge": {},
                "tools_platforms": {}
            }
    
    def get_top_skills(self, aggregated_skills: Dict, top_n: int = 20) -> Dict:
        """
        Get top N skills from each category
        
        Args:
            aggregated_skills: Aggregated skills dictionary
            top_n: Number of top skills to return
            
        Returns:
            Dictionary with top skills per category
        """
        top_skills = {}
        
        for category, skills in aggregated_skills.items():
            top_skills[category] = dict(list(skills.items())[:top_n])
        
        return top_skills
    
    def save_skills(self, skills: Dict, filename: str = "extracted_skills.json"):
        """Save extracted skills to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(skills, f, indent=2, ensure_ascii=False)
        print(f"\nSkills saved to {filename}")
    
    def load_skills(self, filename: str = "extracted_skills.json") -> Dict:
        """Load skills from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                skills = json.load(f)
            print(f"Loaded skills from {filename}")
            return skills
        except FileNotFoundError:
            print(f"File {filename} not found")
            return {}


if __name__ == "__main__":
    # Example usage
    extractor = SkillsExtractor()
    
    # Load jobs from file
    with open("jobs.json", 'r') as f:
        jobs = json.load(f)
    
    # Extract skills
    skills = extractor.extract_skills_from_jobs(jobs)
    
    # Get top skills
    top_skills = extractor.get_top_skills(skills, top_n=20)
    
    # Save skills
    extractor.save_skills(skills)
    
    print("\nTop Technical Skills:")
    for skill, count in list(top_skills['technical_skills'].items())[:10]:
        print(f"  {skill}: {count}")
