import streamlit as st
import json
import os
import sys
import importlib
from dotenv import load_dotenv

# Force reload of our modules to get latest code (fixes Streamlit caching issue)
for module_name in ['skills_extractor', 'syllabus_matcher', 'pdf_generator', 'jobspy_scraper', 'pdf_to_json']:
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])

from skills_extractor import SkillsExtractor
from syllabus_matcher import SyllabusMatcher
from pdf_generator import PDFGenerator
from pdf_to_json import PDFToJSONConverter
import pandas as pd
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Clear Streamlit cache to ensure fresh data
st.cache_data.clear()
st.cache_resource.clear()


# Page configuration
st.set_page_config(
    page_title="Job Scraper & Syllabus Matcher",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1a237e;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3949ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #3949ab;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 2rem;
    }
    .stButton>button:hover {
        background-color: #1a237e;
    }
    .success-box {
        padding: 1rem;
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'skills' not in st.session_state:
    st.session_state.skills = {}
if 'gap_analysis' not in st.session_state:
    st.session_state.gap_analysis = {}
if 'updated_syllabus' not in st.session_state:
    st.session_state.updated_syllabus = {}
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None


def main():
    # Header
    st.markdown('<div class="main-header">📊 Job Scraper & Syllabus Matcher</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check if API key is already in environment
        existing_key = os.getenv("GROQ_API_KEY")
        
        if existing_key:
            st.success("✅ API Key loaded from .env file")
            st.info(f"Key: {existing_key[:10]}...{existing_key[-4:]}")
            
            # Option to override
            if st.checkbox("Override with different key"):
                api_key = st.text_input("Groq API Key", type="password", 
                                        help="Enter a different Groq API key")
                if api_key:
                    os.environ["GROQ_API_KEY"] = api_key
                    st.success("✅ Using custom API key")
        else:
            st.warning("⚠️ No API key found in .env file")
            api_key = st.text_input("Groq API Key", type="password", 
                                    help="Enter your Groq API key for AI processing")
            
            if api_key:
                os.environ["GROQ_API_KEY"] = api_key
                st.success("✅ API key set for this session")
            else:
                st.info("💡 Add GROQ_API_KEY to your .env file to avoid entering it each time")
        
        st.markdown("---")
        
        # Cache control
        if st.button("🔄 Clear Cache & Reload", help="Click if you're seeing old data or no skills"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ Cache cleared! Page will reload...")
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        st.header("📋 Navigation")
        page = st.radio("Select Page", 
                       ["🔍 Job Scraping", 
                        "🎯 Skills Analysis", 
                        "📚 Syllabus Matching", 
                        "📄 Generate Report"])
    
    # Main content
    if page == "🔍 Job Scraping":
        job_scraping_page()
    elif page == "🎯 Skills Analysis":
        skills_analysis_page()
    elif page == "📚 Syllabus Matching":
        syllabus_matching_page()
    elif page == "📄 Generate Report":
        generate_report_page()


def job_scraping_page():
    st.header("🔍 Job Scraping")
    st.write("Extract job postings using JobSpy (proper scraper for Indeed, LinkedIn, ZipRecruiter, Glassdoor)")
    
    # Source selection
    st.subheader("📡 Select Job Sources")
    st.info("💡 Using JobSpy - a proper scraping library that gets FULL job descriptions!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        use_indeed = st.checkbox("Indeed", value=True,
                                 help="Scrape from Indeed.com")
    with col2:
        use_linkedin = st.checkbox("LinkedIn", value=True,
                                   help="Scrape from LinkedIn (with full descriptions)")
    with col3:
        use_ziprecruiter = st.checkbox("ZipRecruiter", value=False,
                                      help="Scrape from ZipRecruiter")
    with col4:
        use_glassdoor = st.checkbox("Glassdoor", value=False,
                                   help="Scrape from Glassdoor")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        job_title = st.text_input("Job Title", value="Software Engineer",
                                  help="Enter the job title to search for")
    
    with col2:
        location = st.text_input("Location", value="Remote",
                                help="Enter location (e.g., 'Remote', 'San Francisco, CA', 'New York')")
    
    with col3:
        max_jobs = st.number_input("Results Wanted", min_value=1, max_value=50, value=10,
                                   help="Total number of jobs to fetch across all sources")
    
    if st.button("🚀 Scrape Jobs", key="scrape_btn"):
        if not job_title:
            st.error("Please enter a job title")
            return
        
        # Build site list
        site_names = []
        if use_indeed:
            site_names.append('indeed')
        if use_linkedin:
            site_names.append('linkedin')
        if use_ziprecruiter:
            site_names.append('zip_recruiter')
        if use_glassdoor:
            site_names.append('glassdoor')
        
        if not site_names:
            st.error("Please select at least one job source")
            return
        
        st.info(f"⏱️ Scraping from {len(site_names)} source(s)... This will take 20-40 seconds.")
        
        with st.spinner(f"Scraping jobs from {', '.join(site_names)}..."):
            try:
                from jobspy_scraper import JobSpyScraper
                
                scraper = JobSpyScraper()
                jobs = scraper.scrape_jobs(
                    search_term=job_title,
                    location=location,
                    site_names=site_names,
                    results_wanted=max_jobs,
                    hours_old=72  # Last 3 days
                )
                
                if jobs:
                    st.session_state.jobs = jobs
                    scraper.save_to_json("jobs.json")
                    
                    st.markdown('<div class="success-box">✅ Successfully scraped {} jobs!</div>'.format(len(jobs)), 
                              unsafe_allow_html=True)
                    
                    # Display jobs
                    st.subheader("Scraped Jobs")
                    df = pd.DataFrame(jobs)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Jobs JSON",
                        data=json.dumps(jobs, indent=2),
                        file_name=f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No jobs found. Try different search criteria.")
                    
            except Exception as e:
                st.error(f"Error during scraping: {str(e)}")
    
    # Load existing jobs
    st.markdown("---")
    st.subheader("Or Use Demo/Existing Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Load Demo Jobs (Recommended)", key="load_demo_btn"):
            try:
                # Try to load demo jobs
                if os.path.exists("demo_jobs.json"):
                    with open("demo_jobs.json", 'r', encoding='utf-8') as f:
                        jobs = json.load(f)
                    st.session_state.jobs = jobs
                    st.success(f"✅ Loaded {len(jobs)} demo jobs with detailed descriptions!")
                    st.info("💡 Demo jobs have full descriptions and will extract 20-30+ skills!")
                    
                    df = pd.DataFrame(jobs)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("demo_jobs.json not found. Run 'py demo.py' first to generate it.")
            except Exception as e:
                st.error(f"Error loading demo jobs: {str(e)}")
    
    with col2:
        uploaded_file = st.file_uploader("Upload jobs JSON file", type=['json'], key="upload_jobs")
        if uploaded_file is not None:
            try:
                jobs = json.load(uploaded_file)
                st.session_state.jobs = jobs
                st.success(f"Loaded {len(jobs)} jobs from file")
                
                df = pd.DataFrame(jobs)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")


def skills_analysis_page():
    st.header("🎯 Skills Analysis")
    st.write("Extract and analyze skills from job descriptions using AI")
    
    # Auto-load demo jobs if no jobs are present
    if not st.session_state.jobs:
        if os.path.exists("demo_jobs.json"):
            st.info("💡 No jobs loaded. Auto-loading demo jobs...")
            try:
                with open("demo_jobs.json", 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                st.session_state.jobs = jobs
                st.success(f"✅ Loaded {len(jobs)} demo jobs automatically!")
            except:
                pass
    
    if not st.session_state.jobs:
        st.error("❌ No jobs loaded!")
        st.markdown("""
        ### How to load jobs:
        
        **Option 1: Use Demo Data (Recommended)**
        1. Go to "🔍 Job Scraping" page
        2. Click "📦 Load Demo Jobs" button
        3. Come back here
        
        **Option 2: Scrape Jobs**
        1. Go to "🔍 Job Scraping" page  
        2. Enter job title
        3. Check "Get Full Descriptions"
        4. Click "Start Scraping"
        5. Come back here
        
        **Option 3: Run Demo Script**
        ```
        py demo.py
        ```
        Then restart this app.
        """)
        return
    
    if not os.getenv("GROQ_API_KEY"):
        st.error("❌ Please enter your Groq API key in the sidebar")
        return
    
    st.success(f"✅ Ready to analyze {len(st.session_state.jobs)} jobs")
    
    # Show job info
    with st.expander("📋 View Loaded Jobs"):
        df = pd.DataFrame(st.session_state.jobs)
        st.dataframe(df[['title', 'company', 'location']], use_container_width=True)
        
        # Show description length
        avg_desc_len = sum(len(j.get('description', '')) for j in st.session_state.jobs) / len(st.session_state.jobs)
        st.info(f"Average description length: {int(avg_desc_len)} characters")
        
        if avg_desc_len < 100:
            st.warning("⚠️ Descriptions are very short! You may not get many skills. Consider using demo data or scraping with 'Get Full Descriptions' enabled.")
    
    if st.button("🔬 Extract Skills", key="extract_btn"):
        with st.spinner("Extracting skills using AI... This may take a few minutes."):
            try:
                extractor = SkillsExtractor()
                skills = extractor.extract_skills_from_jobs(st.session_state.jobs)
                
                st.session_state.skills = skills
                extractor.save_skills(skills, "extracted_skills.json")
                
                st.markdown('<div class="success-box">✅ Skills extracted successfully!</div>', 
                          unsafe_allow_html=True)
                
                # Display skills
                display_skills(skills, key_prefix="new_")
                
            except Exception as e:
                st.error(f"Error extracting skills: {str(e)}")
    
    # Display existing skills
    if st.session_state.skills:
        st.markdown("---")
        st.subheader("Extracted Skills")
        display_skills(st.session_state.skills, key_prefix="existing_")


def display_skills(skills, key_prefix=""):
    """Display skills in a formatted way"""
    tabs = st.tabs(["💻 Technical Skills", "🤝 Soft Skills", "📖 Domain Knowledge", "🛠️ Tools & Platforms"])
    
    categories = ["technical_skills", "soft_skills", "domain_knowledge", "tools_platforms"]
    
    for tab, category in zip(tabs, categories):
        with tab:
            if category in skills and skills[category]:
                # Create DataFrame
                skill_data = [{"Skill": skill, "Frequency": count} 
                             for skill, count in list(skills[category].items())[:20]]
                df = pd.DataFrame(skill_data)
                
                # Display as table
                st.dataframe(df, use_container_width=True)
                
                # Download button with unique key
                st.download_button(
                    label=f"📥 Download {category.replace('_', ' ').title()}",
                    data=json.dumps(skills[category], indent=2),
                    file_name=f"{category}.json",
                    mime="application/json",
                    key=f"{key_prefix}download_{category}"
                )
            else:
                st.info("No skills found in this category")


def syllabus_matching_page():
    st.header("📚 Syllabus Matching")
    st.write("Match extracted skills with current syllabus and create updated curriculum")
    
    if not st.session_state.skills:
        st.warning("⚠️ No skills extracted. Please complete skills analysis first.")
        return
    
    if not os.getenv("GROQ_API_KEY"):
        st.error("❌ Please enter your Groq API key in the sidebar")
        return
    
    # Upload or create syllabus
    st.subheader("Current Syllabus")
    
    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📄 Upload PDF", "📋 Upload JSON", "📝 Use Default"])
    
    with tab1:
        st.write("Upload a PDF syllabus - it will be automatically converted when you click 'Analyze & Match'")
        uploaded_pdf = st.file_uploader("Upload syllabus PDF", type=['pdf'], key="pdf_upload")
        
        if uploaded_pdf is not None:
            # Save uploaded PDF temporarily
            temp_pdf_path = "temp_syllabus.pdf"
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            
            # Store PDF path in session state for later conversion
            st.session_state.pdf_path = temp_pdf_path
            st.session_state.pdf_uploaded = True
            
            st.success(f"✅ PDF uploaded: {uploaded_pdf.name}")
            st.info("💡 Click 'Analyze & Match' below to automatically convert and analyze")
            
            # Optional: Show preview button
            if st.button("👁️ Preview Converted JSON", key="preview_pdf_btn"):
                with st.spinner("Converting PDF to JSON..."):
                    try:
                        converter = PDFToJSONConverter()
                        syllabus_json = converter.process_pdf(temp_pdf_path, "current_syllabus.json")
                        st.session_state.current_syllabus = syllabus_json
                        
                        st.markdown('<div class="success-box">✅ PDF converted successfully!</div>', 
                                  unsafe_allow_html=True)
                        
                        with st.expander("View Converted Syllabus", expanded=True):
                            st.json(syllabus_json)
                        
                        # Download option
                        st.download_button(
                            label="📥 Download Converted JSON",
                            data=json.dumps(syllabus_json, indent=2),
                            file_name=f"converted_syllabus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                        
                    except Exception as e:
                        st.error(f"Error converting PDF: {str(e)}")
                        st.info("💡 Make sure your PDF contains readable text (not scanned images)")
    
    with tab2:
        st.write("Upload an existing syllabus JSON file")
        uploaded_syllabus = st.file_uploader("Upload current syllabus JSON", type=['json'], key="json_upload")
        
        if uploaded_syllabus is not None:
            try:
                current_syllabus = json.load(uploaded_syllabus)
                st.session_state.current_syllabus = current_syllabus
                st.success("✅ Syllabus loaded successfully")
                
                with st.expander("View Loaded Syllabus"):
                    st.json(current_syllabus)
            except Exception as e:
                st.error(f"Error loading syllabus: {str(e)}")
    
    with tab3:
        st.write("Use a default software engineering syllabus template")
        if st.button("📝 Load Default Syllabus", key="default_syllabus_btn"):
            matcher = SyllabusMatcher()
            current_syllabus = matcher.create_default_syllabus()
            st.session_state.current_syllabus = current_syllabus
            st.success("✅ Default syllabus loaded")
            
            with st.expander("View Default Syllabus"):
                st.json(current_syllabus)
    
    # Display current syllabus
    if 'current_syllabus' in st.session_state:
        with st.expander("View Current Syllabus"):
            st.json(st.session_state.current_syllabus)
    
    # Analyze and match
    if st.button("🔍 Analyze & Match", key="match_btn"):
        # Check if PDF was uploaded but not converted yet
        if st.session_state.get('pdf_uploaded', False) and 'current_syllabus' not in st.session_state:
            with st.spinner("Converting PDF to JSON..."):
                try:
                    converter = PDFToJSONConverter()
                    syllabus_json = converter.process_pdf(
                        st.session_state.pdf_path, 
                        "current_syllabus.json"
                    )
                    st.session_state.current_syllabus = syllabus_json
                    st.success("✅ PDF converted to JSON successfully!")
                except Exception as e:
                    st.error(f"Error converting PDF: {str(e)}")
                    st.info("💡 Make sure your PDF contains readable text (not scanned images)")
                    return
        
        if 'current_syllabus' not in st.session_state:
            st.error("Please upload or create a syllabus first")
            return
        
        with st.spinner("Analyzing gaps and creating updated syllabus..."):
            try:
                matcher = SyllabusMatcher()
                
                # Analyze gaps
                gap_analysis = matcher.analyze_skill_gaps(
                    st.session_state.current_syllabus,
                    st.session_state.skills
                )
                st.session_state.gap_analysis = gap_analysis
                matcher.save_analysis(gap_analysis, "gap_analysis.json")
                
                # Create updated syllabus
                updated_syllabus = matcher.create_updated_syllabus(
                    st.session_state.current_syllabus,
                    gap_analysis
                )
                st.session_state.updated_syllabus = updated_syllabus
                matcher.save_syllabus(updated_syllabus, "updated_syllabus.json")
                
                st.markdown('<div class="success-box">✅ Analysis complete!</div>', 
                          unsafe_allow_html=True)
                
                # Display results
                display_gap_analysis(gap_analysis)
                display_updated_syllabus(updated_syllabus)
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
    
    # Display existing results
    if st.session_state.gap_analysis and st.session_state.updated_syllabus:
        st.markdown("---")
        display_gap_analysis(st.session_state.gap_analysis)
        display_updated_syllabus(st.session_state.updated_syllabus)


def display_gap_analysis(gap_analysis):
    """Display gap analysis results"""
    st.subheader("📊 Gap Analysis")
    
    if 'summary' in gap_analysis:
        st.markdown(f'<div class="info-box">{gap_analysis["summary"]}</div>', 
                   unsafe_allow_html=True)
    
    tabs = st.tabs(["❌ Missing Skills", "➕ New Modules", "📈 Needs Emphasis"])
    
    with tabs[0]:
        if 'missing_skills' in gap_analysis and gap_analysis['missing_skills']:
            df = pd.DataFrame(gap_analysis['missing_skills'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No missing skills identified")
    
    with tabs[1]:
        if 'new_modules' in gap_analysis and gap_analysis['new_modules']:
            for module in gap_analysis['new_modules']:
                with st.expander(f"📦 {module.get('module_name', 'Unknown')} - Priority: {module.get('priority', 'N/A')}"):
                    st.write(f"**Rationale:** {module.get('rationale', '')}")
                    if 'topics' in module:
                        st.write("**Topics:**")
                        for topic in module['topics']:
                            st.write(f"- {topic}")
        else:
            st.info("No new modules recommended")
    
    with tabs[2]:
        if 'needs_more_emphasis' in gap_analysis and gap_analysis['needs_more_emphasis']:
            for item in gap_analysis['needs_more_emphasis']:
                st.write(f"**{item.get('skill', '')}**")
                st.write(f"Current: {item.get('current_coverage', '')}")
                st.write(f"Recommendation: {item.get('recommendation', '')}")
                st.markdown("---")
        else:
            st.info("No emphasis changes needed")


def display_updated_syllabus(updated_syllabus):
    """Display updated syllabus"""
    st.subheader("📚 Updated Syllabus")
    
    if 'program_name' in updated_syllabus:
        st.write(f"**Program:** {updated_syllabus['program_name']}")
    if 'duration' in updated_syllabus:
        st.write(f"**Duration:** {updated_syllabus['duration']}")
    
    if 'modules' in updated_syllabus:
        st.write(f"**Total Modules:** {len(updated_syllabus['modules'])}")
        
        for idx, module in enumerate(updated_syllabus['modules'], 1):
            with st.expander(f"Module {idx}: {module.get('name', 'Unknown')}"):
                if 'duration' in module:
                    st.write(f"**Duration:** {module['duration']}")
                
                if 'topics' in module:
                    st.write("**Topics:**")
                    for topic in module['topics']:
                        st.write(f"- {topic}")
                
                if 'learning_outcomes' in module:
                    st.write("**Learning Outcomes:**")
                    for outcome in module['learning_outcomes']:
                        st.write(f"- {outcome}")


def generate_report_page():
    st.header("📄 Generate PDF Report")
    st.write("Create a professional PDF report with all analysis and recommendations")
    
    if not st.session_state.gap_analysis or not st.session_state.updated_syllabus:
        st.warning("⚠️ Please complete the syllabus matching process first.")
        return
    
    report_title = st.text_input("Report Title", value="Industry-Aligned Syllabus Report")
    
    if st.button("📄 Generate PDF Report", key="pdf_btn"):
        with st.spinner("Generating PDF report..."):
            try:
                generator = PDFGenerator()
                pdf_filename = generator.generate_pdf(
                    gap_analysis=st.session_state.gap_analysis,
                    updated_syllabus=st.session_state.updated_syllabus,
                    filename="syllabus_report.pdf"
                )
                
                st.markdown('<div class="success-box">✅ PDF report generated successfully!</div>', 
                          unsafe_allow_html=True)
                
                # Provide download
                with open(pdf_filename, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_file,
                        file_name=f"syllabus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    # Summary
    st.markdown("---")
    st.subheader("📋 Process Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Jobs Scraped", len(st.session_state.jobs))
    
    with col2:
        total_skills = sum(len(skills) for skills in st.session_state.skills.values())
        st.metric("Skills Extracted", total_skills)
    
    with col3:
        missing_skills = len(st.session_state.gap_analysis.get('missing_skills', []))
        st.metric("Missing Skills", missing_skills)
    
    with col4:
        new_modules = len(st.session_state.gap_analysis.get('new_modules', []))
        st.metric("New Modules", new_modules)


if __name__ == "__main__":
    main()
