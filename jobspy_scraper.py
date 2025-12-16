from jobspy import scrape_jobs
import pandas as pd
import json
from typing import List, Dict


class JobSpyScraper:
    """Proper job scraper using JobSpy library"""
    
    def __init__(self):
        self.jobs = []
    
    def scrape_jobs(self, 
                   search_term: str,
                   location: str = "",
                   site_names: List[str] = None,
                   results_wanted: int = 10,
                   hours_old: int = 72,
                   country: str = "USA") -> List[Dict]:
        """
        Scrape jobs using JobSpy
        
        Args:
            search_term: Job title to search for
            location: Location (e.g., "San Francisco, CA" or "Remote")
            site_names: List of sites to scrape from ['indeed', 'linkedin', 'zip_recruiter', 'glassdoor']
            results_wanted: Number of jobs to fetch
            hours_old: Only get jobs posted in last X hours (72 = 3 days)
            country: Country code (USA, UK, Canada, etc.)
        
        Returns:
            List of job dictionaries
        """
        if site_names is None:
            site_names = ['indeed', 'linkedin', 'zip_recruiter']
        
        print(f"\n{'='*60}")
        print(f"Scraping jobs using JobSpy")
        print(f"Search: {search_term}")
        print(f"Location: {location if location else 'Any'}")
        print(f"Sources: {', '.join(site_names)}")
        print(f"{'='*60}\n")
        
        try:
            # Scrape jobs using JobSpy
            jobs_df = scrape_jobs(
                site_name=site_names,
                search_term=search_term,
                location=location if location else "",
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed=country,
                linkedin_fetch_description=True,  # Get full descriptions from LinkedIn
                proxies=None
            )
            
            if jobs_df is None or len(jobs_df) == 0:
                print("No jobs found")
                return []
            
            print(f"✓ Found {len(jobs_df)} jobs")
            
            # Convert DataFrame to list of dictionaries
            jobs_list = []
            
            for idx, row in jobs_df.iterrows():
                # Extract and clean data
                job = {
                    "title": str(row.get('title', '')),
                    "company": str(row.get('company', '')),
                    "location": str(row.get('location', '')),
                    "description": str(row.get('description', '')),
                    "source": str(row.get('site', '')).title(),
                    "url": str(row.get('job_url', '')),
                    "date_posted": str(row.get('date_posted', '')),
                    "job_type": str(row.get('job_type', '')),
                    "salary": str(row.get('interval', '')) if pd.notna(row.get('min_amount')) else "",
                }
                
                # Only add if we have minimum required fields
                if job['title'] and job['company']:
                    jobs_list.append(job)
                    desc_len = len(job['description'])
                    print(f"  {idx+1}. {job['title']} at {job['company']} ({desc_len} chars)")
            
            print(f"\n✓ Successfully scraped {len(jobs_list)} jobs with descriptions")
            
            # Show description stats
            desc_lengths = [len(j['description']) for j in jobs_list]
            if desc_lengths:
                avg_len = sum(desc_lengths) / len(desc_lengths)
                print(f"  Average description length: {int(avg_len)} characters")
                
                if avg_len < 100:
                    print(f"  ⚠️  Warning: Descriptions are short. Try different sources or search terms.")
                else:
                    print(f"  ✓ Good description quality!")
            
            self.jobs = jobs_list
            return jobs_list
            
        except Exception as e:
            print(f"Error scraping jobs: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_to_json(self, filename: str = "jobs.json"):
        """Save jobs to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Jobs saved to {filename}")
    
    def load_from_json(self, filename: str = "jobs.json") -> List[Dict]:
        """Load jobs from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            print(f"Loaded {len(self.jobs)} jobs from {filename}")
            return self.jobs
        except FileNotFoundError:
            print(f"File {filename} not found")
            return []


if __name__ == "__main__":
    # Test the scraper
    scraper = JobSpyScraper()
    
    # Scrape from multiple sources
    jobs = scraper.scrape_jobs(
        search_term="Software Engineer",
        location="Remote",
        site_names=['indeed', 'linkedin'],  # Can also add 'zip_recruiter', 'glassdoor'
        results_wanted=5,
        hours_old=72  # Last 3 days
    )
    
    if jobs:
        scraper.save_to_json("jobspy_jobs.json")
        
        print(f"\n{'='*60}")
        print("SAMPLE JOB:")
        print(f"{'='*60}")
        print(f"Title: {jobs[0]['title']}")
        print(f"Company: {jobs[0]['company']}")
        print(f"Location: {jobs[0]['location']}")
        print(f"Source: {jobs[0]['source']}")
        print(f"Description length: {len(jobs[0]['description'])} characters")
        print(f"Description preview: {jobs[0]['description'][:200]}...")
    else:
        print("\n✗ No jobs found")
