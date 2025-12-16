import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import Dict
import PyPDF2

load_dotenv()


class PDFToJSONConverter:
    """Converts PDF syllabus to structured JSON format using AI"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                print(f"Extracting text from {num_pages} pages...")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            print(f"Extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise
    
    def convert_to_json(self, pdf_text: str) -> Dict:
        """
        Convert PDF text to structured JSON syllabus format using AI
        
        Args:
            pdf_text: Extracted text from PDF
            
        Returns:
            Structured syllabus dictionary
        """
        prompt = f"""
        You are an expert at analyzing educational syllabi. Convert the following syllabus text into a structured JSON format.
        
        Syllabus Text:
        {pdf_text[:8000]}  # Limit to avoid token limits
        
        Extract and structure the information into the following JSON format:
        {{
            "program_name": "Name of the program/course",
            "duration": "Duration (e.g., '4 years', '2 semesters')",
            "institution": "Institution name if mentioned",
            "modules": [
                {{
                    "name": "Module/Course Name",
                    "topics": ["topic1", "topic2", "topic3"],
                    "duration": "Duration of this module",
                    "credits": "Credits if mentioned",
                    "description": "Brief description if available"
                }}
            ],
            "learning_outcomes": ["outcome1", "outcome2"],
            "prerequisites": ["prerequisite1", "prerequisite2"],
            "assessment_methods": ["method1", "method2"]
        }}
        
        Guidelines:
        1. Extract all modules/courses mentioned
        2. List all topics covered in each module
        3. Capture learning outcomes if mentioned
        4. Include any prerequisites
        5. Note assessment methods if specified
        6. If information is not available, use null or empty array
        7. Be comprehensive and capture all educational content
        
        Only return the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing and structuring educational syllabi. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            try:
                syllabus_json = json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = result.find('{')
                end = result.rfind('}') + 1
                if start != -1 and end != 0:
                    syllabus_json = json.loads(result[start:end])
                else:
                    raise ValueError("Failed to parse JSON from AI response")
            
            return syllabus_json
            
        except Exception as e:
            print(f"Error converting to JSON: {e}")
            raise
    
    def process_pdf(self, pdf_path: str, output_json_path: str = None) -> Dict:
        """
        Complete pipeline: Extract text from PDF and convert to JSON
        
        Args:
            pdf_path: Path to PDF file
            output_json_path: Optional path to save JSON output
            
        Returns:
            Structured syllabus dictionary
        """
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text
        pdf_text = self.extract_text_from_pdf(pdf_path)
        
        # Convert to JSON
        print("Converting to structured JSON format...")
        syllabus_json = self.convert_to_json(pdf_text)
        
        # Save if output path provided
        if output_json_path:
            self.save_json(syllabus_json, output_json_path)
        
        return syllabus_json
    
    def save_json(self, data: Dict, filename: str):
        """Save JSON data to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON to {filename}")


if __name__ == "__main__":
    # Example usage
    converter = PDFToJSONConverter()
    
    # Process a PDF file
    pdf_file = "sample_syllabus.pdf"  # Replace with your PDF file
    
    if os.path.exists(pdf_file):
        syllabus = converter.process_pdf(pdf_file, "converted_syllabus.json")
        print("\nConversion complete!")
        print(json.dumps(syllabus, indent=2))
    else:
        print(f"PDF file '{pdf_file}' not found")
