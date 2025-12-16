import argparse
import json
from job_scraper import JobScraper
from skills_extractor import SkillsExtractor
from syllabus_matcher import SyllabusMatcher
from pdf_generator import PDFGenerator


def main():
    """Main application flow"""
    
    parser = argparse.ArgumentParser(description='Job Scraper and Syllabus Matcher')
    parser.add_argument('--job-title', type=str, default='Software Engineer', 
                        help='Job title to search for')
    parser.add_argument('--location', type=str, default='', 
                        help='Location to search in')
    parser.add_argument('--max-jobs', type=int, default=10, 
                        help='Maximum number of jobs to scrape per source')
    parser.add_argument('--skip-scraping', action='store_true', 
                        help='Skip scraping and use existing jobs.json')
    parser.add_argument('--syllabus-file', type=str, default='current_syllabus.json',
                        help='Path to current syllabus JSON file')
    
    args = parser.parse_args()
    
    print("="*70)
    print("JOB SCRAPER & SYLLABUS MATCHER")
    print("="*70)
    
    # Step 1: Scrape jobs
    if not args.skip_scraping:
        print("\n[STEP 1] Scraping job postings...")
        print("-"*70)
        
        scraper = JobScraper()
        jobs = scraper.scrape_all(
            job_title=args.job_title,
            location=args.location,
            max_jobs_per_source=args.max_jobs
        )
        
        if not jobs:
            print("No jobs found. Exiting.")
            return
        
        scraper.save_to_json("jobs.json")
    else:
        print("\n[STEP 1] Loading existing jobs from jobs.json...")
        print("-"*70)
        scraper = JobScraper()
        jobs = scraper.load_from_json("jobs.json")
        
        if not jobs:
            print("No jobs found in jobs.json. Please run without --skip-scraping.")
            return
    
    # Step 2: Extract skills
    print("\n[STEP 2] Extracting skills from job descriptions...")
    print("-"*70)
    
    extractor = SkillsExtractor()
    aggregated_skills = extractor.extract_skills_from_jobs(jobs)
    extractor.save_skills(aggregated_skills, "extracted_skills.json")
    
    # Display top skills
    print("\n--- Top Skills by Category ---")
    for category, skills in aggregated_skills.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for skill, count in list(skills.items())[:5]:
            print(f"  • {skill}: {count} mentions")
    
    # Step 3: Match with syllabus
    print("\n[STEP 3] Analyzing syllabus and matching with industry skills...")
    print("-"*70)
    
    matcher = SyllabusMatcher()
    current_syllabus = matcher.load_current_syllabus(args.syllabus_file)
    
    # Analyze gaps
    print("\nAnalyzing skill gaps...")
    gap_analysis = matcher.analyze_skill_gaps(current_syllabus, aggregated_skills)
    matcher.save_analysis(gap_analysis, "gap_analysis.json")
    
    # Create updated syllabus
    print("\nCreating updated syllabus...")
    updated_syllabus = matcher.create_updated_syllabus(current_syllabus, gap_analysis)
    matcher.save_syllabus(updated_syllabus, "updated_syllabus.json")
    
    # Step 4: Generate PDF
    print("\n[STEP 4] Generating PDF report...")
    print("-"*70)
    
    generator = PDFGenerator()
    pdf_filename = generator.generate_pdf(
        gap_analysis=gap_analysis,
        updated_syllabus=updated_syllabus,
        filename="syllabus_report.pdf"
    )
    
    # Summary
    print("\n" + "="*70)
    print("PROCESS COMPLETE!")
    print("="*70)
    print(f"\nGenerated files:")
    print(f"  • jobs.json - Scraped job postings")
    print(f"  • extracted_skills.json - Extracted skills with frequencies")
    print(f"  • gap_analysis.json - Gap analysis between syllabus and industry")
    print(f"  • updated_syllabus.json - Updated industry-aligned syllabus")
    print(f"  • {pdf_filename} - Professional PDF report")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
