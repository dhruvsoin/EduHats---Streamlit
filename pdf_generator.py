from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import json
from typing import Dict, List


class PDFGenerator:
    """Generates professional PDF reports for syllabus updates"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#3949ab'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#212121'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Bullet points
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#424242'),
            leftIndent=20,
            spaceAfter=6,
            bulletIndent=10
        ))
    
    def create_cover_page(self, story: List, title: str = "Industry-Aligned Syllabus Report"):
        """Create a cover page for the PDF"""
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(title, self.styles['CustomTitle']))
        
        # Subtitle
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "Comprehensive Analysis & Updated Curriculum",
            self.styles['CustomSubtitle']
        ))
        
        # Date
        story.append(Spacer(1, 0.5*inch))
        current_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(
            f"Generated on: {current_date}",
            self.styles['CustomBody']
        ))
        
        story.append(PageBreak())
    
    def create_executive_summary(self, story: List, gap_analysis: Dict, updated_syllabus: Dict):
        """Create executive summary section"""
        story.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary text
        if 'summary' in gap_analysis:
            story.append(Paragraph(gap_analysis['summary'], self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Key statistics
        story.append(Paragraph("Key Findings", self.styles['CustomSubtitle']))
        
        stats = []
        if 'missing_skills' in gap_analysis:
            stats.append(f"• Missing Skills Identified: {len(gap_analysis['missing_skills'])}")
        if 'new_modules' in gap_analysis:
            stats.append(f"• New Modules Recommended: {len(gap_analysis['new_modules'])}")
        if 'changes_summary' in updated_syllabus and 'added_modules' in updated_syllabus['changes_summary']:
            stats.append(f"• Modules Added: {len(updated_syllabus['changes_summary']['added_modules'])}")
        
        for stat in stats:
            story.append(Paragraph(stat, self.styles['CustomBullet']))
        
        story.append(PageBreak())
    
    def create_gap_analysis_section(self, story: List, gap_analysis: Dict):
        """Create gap analysis section"""
        story.append(Paragraph("Gap Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Missing Skills
        if 'missing_skills' in gap_analysis and gap_analysis['missing_skills']:
            story.append(Paragraph("Missing Skills", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.1*inch))
            
            # Create table for missing skills
            table_data = [['Skill', 'Category', 'Frequency', 'Priority']]
            
            for skill in gap_analysis['missing_skills'][:20]:  # Top 20
                table_data.append([
                    skill.get('skill', ''),
                    skill.get('category', ''),
                    str(skill.get('frequency', '')),
                    skill.get('priority', '')
                ])
            
            table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
        
        # New Modules Recommended
        if 'new_modules' in gap_analysis and gap_analysis['new_modules']:
            story.append(Paragraph("Recommended New Modules", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.1*inch))
            
            for module in gap_analysis['new_modules']:
                story.append(Paragraph(
                    f"<b>{module.get('module_name', '')}</b> (Priority: {module.get('priority', '')})",
                    self.styles['SectionHeading']
                ))
                
                story.append(Paragraph(
                    f"<b>Rationale:</b> {module.get('rationale', '')}",
                    self.styles['CustomBody']
                ))
                
                if 'topics' in module and module['topics']:
                    story.append(Paragraph("<b>Topics:</b>", self.styles['CustomBody']))
                    for topic in module['topics']:
                        story.append(Paragraph(f"• {topic}", self.styles['CustomBullet']))
                
                story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
    
    def create_updated_syllabus_section(self, story: List, updated_syllabus: Dict):
        """Create updated syllabus section"""
        story.append(Paragraph("Updated Syllabus", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Program information
        if 'program_name' in updated_syllabus:
            story.append(Paragraph(
                f"<b>Program:</b> {updated_syllabus['program_name']}",
                self.styles['CustomBody']
            ))
        
        if 'duration' in updated_syllabus:
            story.append(Paragraph(
                f"<b>Duration:</b> {updated_syllabus['duration']}",
                self.styles['CustomBody']
            ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Modules
        if 'modules' in updated_syllabus:
            story.append(Paragraph("Curriculum Modules", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.1*inch))
            
            for idx, module in enumerate(updated_syllabus['modules'], 1):
                # Module name
                story.append(Paragraph(
                    f"Module {idx}: {module.get('name', '')}",
                    self.styles['SectionHeading']
                ))
                
                # Duration
                if 'duration' in module:
                    story.append(Paragraph(
                        f"<b>Duration:</b> {module['duration']}",
                        self.styles['CustomBody']
                    ))
                
                # Topics
                if 'topics' in module and module['topics']:
                    story.append(Paragraph("<b>Topics Covered:</b>", self.styles['CustomBody']))
                    for topic in module['topics']:
                        story.append(Paragraph(f"• {topic}", self.styles['CustomBullet']))
                
                # Learning outcomes
                if 'learning_outcomes' in module and module['learning_outcomes']:
                    story.append(Paragraph("<b>Learning Outcomes:</b>", self.styles['CustomBody']))
                    for outcome in module['learning_outcomes']:
                        story.append(Paragraph(f"• {outcome}", self.styles['CustomBullet']))
                
                # Practical components
                if 'practical_components' in module and module['practical_components']:
                    story.append(Paragraph("<b>Practical Components:</b>", self.styles['CustomBody']))
                    for component in module['practical_components']:
                        story.append(Paragraph(f"• {component}", self.styles['CustomBullet']))
                
                # Industry alignment
                if 'industry_alignment' in module:
                    story.append(Paragraph(
                        f"<b>Industry Alignment:</b> {module['industry_alignment']}",
                        self.styles['CustomBody']
                    ))
                
                story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
    
    def create_changes_summary_section(self, story: List, updated_syllabus: Dict):
        """Create summary of changes section"""
        if 'changes_summary' not in updated_syllabus:
            return
        
        story.append(Paragraph("Summary of Changes", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        changes = updated_syllabus['changes_summary']
        
        # Added modules
        if 'added_modules' in changes and changes['added_modules']:
            story.append(Paragraph("Added Modules", self.styles['CustomSubtitle']))
            for module in changes['added_modules']:
                story.append(Paragraph(f"• {module}", self.styles['CustomBullet']))
            story.append(Spacer(1, 0.2*inch))
        
        # Updated modules
        if 'updated_modules' in changes and changes['updated_modules']:
            story.append(Paragraph("Updated Modules", self.styles['CustomSubtitle']))
            for module in changes['updated_modules']:
                story.append(Paragraph(f"• {module}", self.styles['CustomBullet']))
            story.append(Spacer(1, 0.2*inch))
        
        # Removed topics
        if 'removed_topics' in changes and changes['removed_topics']:
            story.append(Paragraph("Removed/Deprecated Topics", self.styles['CustomSubtitle']))
            for topic in changes['removed_topics']:
                story.append(Paragraph(f"• {topic}", self.styles['CustomBullet']))
            story.append(Spacer(1, 0.2*inch))
        
        # Key improvements
        if 'key_improvements' in changes and changes['key_improvements']:
            story.append(Paragraph("Key Improvements", self.styles['CustomSubtitle']))
            for improvement in changes['key_improvements']:
                story.append(Paragraph(f"• {improvement}", self.styles['CustomBullet']))
    
    def generate_pdf(self, 
                     gap_analysis: Dict, 
                     updated_syllabus: Dict,
                     filename: str = "syllabus_report.pdf"):
        """
        Generate complete PDF report
        
        Args:
            gap_analysis: Gap analysis dictionary
            updated_syllabus: Updated syllabus dictionary
            filename: Output PDF filename
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Create sections
        self.create_cover_page(story)
        self.create_executive_summary(story, gap_analysis, updated_syllabus)
        self.create_gap_analysis_section(story, gap_analysis)
        self.create_updated_syllabus_section(story, updated_syllabus)
        self.create_changes_summary_section(story, updated_syllabus)
        
        # Build PDF
        doc.build(story)
        print(f"\nPDF report generated: {filename}")
        
        return filename


if __name__ == "__main__":
    # Example usage
    generator = PDFGenerator()
    
    # Load data
    with open("gap_analysis.json", 'r') as f:
        gap_analysis = json.load(f)
    
    with open("updated_syllabus.json", 'r') as f:
        updated_syllabus = json.load(f)
    
    # Generate PDF
    generator.generate_pdf(gap_analysis, updated_syllabus, "syllabus_report.pdf")
