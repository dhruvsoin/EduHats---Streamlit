# 🎓 EduHats - Industry-Aligned Syllabus Matcher

**EduHats** is an intelligent AI-powered application that bridges the gap between academic curricula and industry demands. It scrapes real-time job postings, extracts required skills using AI, and provides actionable recommendations to update educational syllabi to match current market needs.

---

## 🌟 Features

### 🔍 **Job Scraping**
- Scrape job postings from multiple sources (Indeed, LinkedIn, ZipRecruiter, Glassdoor)
- Extract full job descriptions with detailed requirements
- Filter by job title, location, and recency
- Export results to JSON format

### 🎯 **Skills Analysis**
- AI-powered skill extraction using Groq LLM
- Categorizes skills into:
  - 💻 Technical Skills
  - 🤝 Soft Skills
  - 📖 Domain Knowledge
  - 🛠️ Tools & Platforms
- Frequency analysis to identify most in-demand skills

### 📚 **Syllabus Matching**
- Upload existing syllabus (PDF or JSON)
- Automated PDF-to-JSON conversion
- Gap analysis between current curriculum and industry needs
- Identifies:
  - Missing skills
  - Recommended new modules
  - Topics needing more emphasis

### 📄 **Report Generation**
- Professional PDF reports with complete analysis
- Downloadable gap analysis and updated syllabus
- Visual metrics and summaries

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EduHats
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running the Application

**Option 1: Web Interface (Recommended for Interactive Use)**

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

**Option 2: Command Line Interface (For Automation/Scripting)**

```bash
# Run full pipeline
python main.py --job-title "Software Engineer" --location "Remote" --max-jobs 10

# Use existing scraped data
python main.py --skip-scraping --syllabus-file "current_syllabus.json"

# See all options
python main.py --help
```

**CLI Options:**
- `--job-title` - Job title to search for (default: "Software Engineer")
- `--location` - Location to search in (default: empty)
- `--max-jobs` - Maximum jobs to scrape (default: 10)
- `--skip-scraping` - Use existing jobs.json
- `--syllabus-file` - Path to syllabus JSON (default: "current_syllabus.json")

---

## 📖 Usage Guide

### Step 1: Scrape Jobs
1. Navigate to **🔍 Job Scraping** page
2. Select job sources (Indeed, LinkedIn, etc.)
3. Enter job title and location
4. Click **🚀 Scrape Jobs**
5. Or use **📦 Load Demo Jobs** for testing

### Step 2: Extract Skills
1. Go to **🎯 Skills Analysis** page
2. Ensure jobs are loaded
3. Click **🔬 Extract Skills**
4. Wait for AI processing (may take a few minutes)
5. Review extracted skills by category

### Step 3: Match Syllabus
1. Navigate to **📚 Syllabus Matching** page
2. Upload your syllabus:
   - **PDF**: Upload and auto-convert
   - **JSON**: Upload existing JSON
   - **Default**: Use built-in template
3. Click **🔍 Analyze & Match**
4. Review gap analysis and updated syllabus

### Step 4: Generate Report
1. Go to **📄 Generate Report** page
2. Enter report title
3. Click **📄 Generate PDF Report**
4. Download the professional PDF report

---

## 🗂️ Project Structure

```
EduHats/
├── app.py                    # Streamlit web interface (GUI)
├── main.py                   # Command-line interface (CLI)
├── jobspy_scraper.py         # Job scraping module
├── skills_extractor.py       # AI-powered skill extraction
├── syllabus_matcher.py       # Gap analysis and syllabus matching
├── pdf_generator.py          # PDF report generation
├── pdf_to_json.py           # PDF to JSON converter
├── requirement.txt          # Python dependencies
├── .env                     # Environment variables (not in git)
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
└── README.md               # This file
```

### Generated Files (Not in Git)
- `jobs.json` - Scraped job data
- `extracted_skills.json` - Extracted skills
- `gap_analysis.json` - Gap analysis results
- `updated_syllabus.json` - Updated syllabus
- `syllabus_report.pdf` - Generated PDF report
- `temp_syllabus.pdf` - Temporary uploaded PDFs

---

## 🛠️ Technologies Used

- **[Streamlit](https://streamlit.io/)** - Web application framework
- **[Groq](https://groq.com/)** - AI/LLM for skill extraction and analysis
- **[JobSpy](https://github.com/Bunsly/JobSpy)** - Job scraping library
- **[ReportLab](https://www.reportlab.com/)** - PDF generation
- **[PyPDF2](https://pypdf2.readthedocs.io/)** - PDF processing
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation
- **[Python-dotenv](https://pypi.org/project/python-dotenv/)** - Environment management

---

## 📝 Configuration

### Job Scraping Settings
- **Sources**: Indeed, LinkedIn, ZipRecruiter, Glassdoor
- **Results**: 1-50 jobs per search
- **Recency**: Last 72 hours (configurable)

### AI Model Settings
- **Model**: Llama 3.1 70B (via Groq)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
## 🙏 Acknowledgments

- Groq for providing fast AI inference
- JobSpy for reliable job scraping
- Streamlit for the excellent web framework
- The open-source community
