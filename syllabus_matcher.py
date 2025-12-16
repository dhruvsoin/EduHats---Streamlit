import os
from groq import Groq
from dotenv import load_dotenv
import json
from typing import List, Dict

load_dotenv()


class SyllabusMatcher:
    """Matches job skills with industry syllabus and creates updated curriculum"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def load_current_syllabus(self, filename: str = "current_syllabus.json") -> Dict:
        """
        Load current syllabus from JSON file
        
        Args:
            filename: Path to syllabus file
            
        Returns:
            Dictionary containing current syllabus
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                syllabus = json.load(f)
            print(f"Loaded syllabus from {filename}")
            return syllabus
        except FileNotFoundError:
            print(f"Syllabus file {filename} not found. Creating default syllabus.")
            return self.create_default_syllabus()
    
    def create_default_syllabus(self) -> Dict:
        """Create a default syllabus structure"""
        return {
            "program_name": "Software Engineering",
            "duration": "4 years",
            "modules": [
                {
                    "name": "Programming Fundamentals",
                    "topics": ["Python", "Java", "Data Structures", "Algorithms"],
                    "duration": "1 semester"
                },
                {
                    "name": "Web Development",
                    "topics": ["HTML", "CSS", "JavaScript", "React"],
                    "duration": "1 semester"
                },
                {
                    "name": "Database Systems",
                    "topics": ["SQL", "MySQL", "Database Design"],
                    "duration": "1 semester"
                },
                {
                    "name": "Software Engineering",
                    "topics": ["SDLC", "Agile", "Testing", "Version Control"],
                    "duration": "1 semester"
                }
            ]
        }
    
    def analyze_skill_gaps(self, current_syllabus: Dict, industry_skills: Dict) -> Dict:
        """
        Analyze gaps between current syllabus and industry requirements
        
        Args:
            current_syllabus: Current syllabus dictionary
            industry_skills: Extracted industry skills
            
        Returns:
            Analysis of skill gaps and recommendations
        """
        # Prepare syllabus text
        syllabus_text = json.dumps(current_syllabus, indent=2)
        
        # Prepare industry skills text
        skills_text = "Industry Skills (by frequency):\n\n"
        
        for category, skills in industry_skills.items():
            skills_text += f"\n{category.replace('_', ' ').title()}:\n"
            for skill, count in list(skills.items())[:15]:
                skills_text += f"  - {skill} (mentioned {count} times)\n"
        
        prompt = f"""
        You are an education curriculum expert. Analyze the gap between the current syllabus and industry requirements.
        
        Current Syllabus:
        {syllabus_text}
        
        {skills_text}
        
        Provide a detailed analysis including:
        1. Skills that are missing from the current syllabus but highly demanded in industry
        2. Skills that are covered but may need more emphasis
        3. Outdated topics that could be replaced
        4. Recommended new modules or topics to add
        5. Priority level for each recommendation (High/Medium/Low)
        
        Return the result as a JSON object with the following structure:
        {{
            "missing_skills": [
                {{"skill": "skill_name", "category": "category", "frequency": count, "priority": "High/Medium/Low"}}
            ],
            "needs_more_emphasis": [
                {{"skill": "skill_name", "current_coverage": "brief description", "recommendation": "what to add"}}
            ],
            "outdated_topics": [
                {{"topic": "topic_name", "reason": "why outdated", "replacement": "suggested replacement"}}
            ],
            "new_modules": [
                {{"module_name": "name", "topics": ["topic1", "topic2"], "priority": "High/Medium/Low", "rationale": "why needed"}}
            ],
            "summary": "Overall summary of the analysis"
        }}
        
        Only return the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert education curriculum analyst. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            try:
                analysis = json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = result.find('{')
                end = result.rfind('}') + 1
                if start != -1 and end != 0:
                    analysis = json.loads(result[start:end])
                else:
                    analysis = {"error": "Failed to parse analysis"}
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing skill gaps: {e}")
            return {"error": str(e)}
    
    def create_updated_syllabus(self, current_syllabus: Dict, gap_analysis: Dict) -> Dict:
        """
        Create an updated syllabus based on gap analysis
        
        Args:
            current_syllabus: Current syllabus dictionary
            gap_analysis: Gap analysis from analyze_skill_gaps
            
        Returns:
            Updated syllabus dictionary
        """
        syllabus_text = json.dumps(current_syllabus, indent=2)
        analysis_text = json.dumps(gap_analysis, indent=2)
        
        prompt = f"""
        Based on the current syllabus and gap analysis, create an updated, industry-aligned syllabus.
        
        Current Syllabus:
        {syllabus_text}
        
        Gap Analysis:
        {analysis_text}
        
        Create a comprehensive updated syllabus that:
        1. Incorporates high-priority missing skills
        2. Adds new modules for emerging technologies
        3. Updates existing modules with industry-relevant topics
        4. Maintains a logical learning progression
        5. Includes practical, hands-on components
        
        Return the result as a JSON object with the following structure:
        {{
            "program_name": "Updated Program Name",
            "duration": "duration",
            "last_updated": "date",
            "modules": [
                {{
                    "name": "Module Name",
                    "topics": ["topic1", "topic2", ...],
                    "duration": "duration",
                    "learning_outcomes": ["outcome1", "outcome2", ...],
                    "practical_components": ["project1", "project2", ...],
                    "industry_alignment": "explanation of how this aligns with industry needs"
                }}
            ],
            "changes_summary": {{
                "added_modules": ["module1", "module2"],
                "updated_modules": ["module1", "module2"],
                "removed_topics": ["topic1", "topic2"],
                "key_improvements": ["improvement1", "improvement2"]
            }}
        }}
        
        Only return the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert curriculum designer. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=2500
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            try:
                updated_syllabus = json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = result.find('{')
                end = result.rfind('}') + 1
                if start != -1 and end != 0:
                    updated_syllabus = json.loads(result[start:end])
                else:
                    updated_syllabus = current_syllabus
            
            return updated_syllabus
            
        except Exception as e:
            print(f"Error creating updated syllabus: {e}")
            return current_syllabus
    
    def save_syllabus(self, syllabus: Dict, filename: str = "updated_syllabus.json"):
        """Save syllabus to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(syllabus, f, indent=2, ensure_ascii=False)
        print(f"Syllabus saved to {filename}")
    
    def save_analysis(self, analysis: Dict, filename: str = "gap_analysis.json"):
        """Save gap analysis to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"Gap analysis saved to {filename}")


if __name__ == "__main__":
    # Example usage
    matcher = SyllabusMatcher()
    
    # Load current syllabus
    current_syllabus = matcher.load_current_syllabus()
    
    # Load industry skills
    with open("extracted_skills.json", 'r') as f:
        industry_skills = json.load(f)
    
    # Analyze gaps
    print("\nAnalyzing skill gaps...")
    gap_analysis = matcher.analyze_skill_gaps(current_syllabus, industry_skills)
    matcher.save_analysis(gap_analysis)
    
    # Create updated syllabus
    print("\nCreating updated syllabus...")
    updated_syllabus = matcher.create_updated_syllabus(current_syllabus, gap_analysis)
    matcher.save_syllabus(updated_syllabus)
    
    print("\nSyllabus matching complete!")
