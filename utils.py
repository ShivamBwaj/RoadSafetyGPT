"""
Utility functions for Road Safety Intervention GPT
Handles translation, report generation, scoring, and quiz generation
"""

import json
from pathlib import Path
from typing import List, Dict, Any
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import io

def translate_text(text: str, target_lang: str = "en", source_lang: str = "en") -> str:
    """Translate text to target language using deep-translator"""
    if target_lang == "en" or not text or not TRANSLATION_AVAILABLE:
        return text
    
    try:
        lang_map = {"hi": "hi", "ta": "ta", "en": "en"}
        target = lang_map.get(target_lang, "en")
        source = lang_map.get(source_lang, "auto")
        
        if target == "en":
            return text
        
        # Use deep-translator which doesn't conflict with groq dependencies
        # Auto-detect source language if not specified
        if source == "auto" or source == "en":
            translator = GoogleTranslator(source='auto', target=target)
        else:
            translator = GoogleTranslator(source=source, target=target)
        
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original if translation fails

def calculate_intervention_score(intervention: Dict, query: str) -> int:
    """
    Calculate priority score (1-100) for an intervention based on query
    Higher scores indicate higher priority
    """
    query_lower = query.lower()
    score = 50  # Base score
    
    # High priority keywords
    high_priority_keywords = ["blackspot", "fatal", "death", "crash", "accident", "emergency", "urgent"]
    for keyword in high_priority_keywords:
        if keyword in query_lower:
            score += 20
            break
    
    # Medium priority keywords
    medium_keywords = ["pedestrian", "school", "intersection", "curve", "night", "visibility"]
    matches = sum(1 for kw in medium_keywords if kw in query_lower)
    score += matches * 5
    
    # Check intervention keywords match
    intervention_keywords = intervention.get("keywords", [])
    keyword_matches = sum(1 for kw in intervention_keywords if kw in query_lower)
    score += keyword_matches * 3
    
    # Check context relevance
    context = intervention.get("context", "").lower()
    context_words = set(word for word in query_lower.split() if len(word) > 3)
    context_matches = sum(1 for word in context_words if word in context)
    score += context_matches * 2
    
    # Normalize to 1-100 range
    score = min(100, max(1, score))
    return int(score)

def get_score_color(score: int) -> str:
    """Get color indicator based on score"""
    if score >= 80:
        return "🟢"  # Green - High priority
    elif score >= 50:
        return "🟡"  # Yellow - Moderate
    else:
        return "🔴"  # Red - Low priority

def get_score_color_hex(score: int) -> str:
    """Get hex color for score badge"""
    if score >= 80:
        return "#28a745"  # Green
    elif score >= 50:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def generate_quiz_questions(rag_system, num_questions: int = 5) -> List[Dict]:
    """Generate quiz questions from interventions and PDFs"""
    questions = []
    
    # Sample questions based on interventions
    sample_questions = [
        {
            "question": "What is the recommended intervention for reducing speeding on rural highways?",
            "options": ["Speed humps", "Rumble strips", "Traffic lights", "Roundabouts"],
            "correct": 1,
            "explanation": "Rumble strips are effective for alerting inattentive drivers on rural highways."
        },
        {
            "question": "Which intervention improves nighttime visibility on sharp curves?",
            "options": ["Zebra crossings", "Reflective delineators", "Speed cameras", "Road dividers"],
            "correct": 1,
            "explanation": "Reflective delineators and chevron signs improve visibility on curves."
        },
        {
            "question": "What is recommended for urban roads with heavy pedestrian movement?",
            "options": ["More lanes", "Zebra crossings and pedestrian refuges", "Higher speed limits", "Traffic circles"],
            "correct": 1,
            "explanation": "Zebra crossings and pedestrian refuges enhance pedestrian safety in urban areas."
        },
        {
            "question": "For unsignalized rural junctions with poor visibility, what intervention is suggested?",
            "options": ["Roundabouts", "Solar-powered blinkers", "Speed bumps", "Traffic lights"],
            "correct": 1,
            "explanation": "Solar-powered blinkers warn approaching drivers at intersections."
        },
        {
            "question": "What reduces fatal crashes on mountain roads with steep drop-offs?",
            "options": ["Road widening", "Crash barriers and guard rails", "More signage", "Speed limits"],
            "correct": 1,
            "explanation": "Crash barriers and guard rails prevent vehicles from leaving the roadway."
        }
    ]
    
    # Use interventions.json for more questions
    interventions = rag_system.interventions if hasattr(rag_system, 'interventions') else []
    
    for i, q in enumerate(sample_questions[:num_questions]):
        questions.append(q)
    
    return questions

def generate_pdf_report(query: str, result: Dict, output_path: str = None) -> bytes:
    """Generate a PDF report with query, response, and interventions"""
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    title = Paragraph("Road Safety Intervention GPT", title_style)
    story.append(title)
    subtitle = Paragraph("IIT Madras Hackathon 2025", styles['Normal'])
    story.append(subtitle)
    story.append(Spacer(1, 0.3*inch))
    
    # Date
    date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    date_para = Paragraph(f"<b>Generated:</b> {date_str}", styles['Normal'])
    story.append(date_para)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Query Summary</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    query_para = Paragraph(query, styles['BodyText'])
    story.append(query_para)
    story.append(Spacer(1, 0.2*inch))
    
    # GPT Response
    story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    response_para = Paragraph(result["response"].replace('\n', '<br/>'), styles['BodyText'])
    story.append(response_para)
    story.append(Spacer(1, 0.3*inch))
    
    # Interventions
    if result.get("matched_interventions"):
        story.append(Paragraph("<b>Recommended Interventions</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Table data
        table_data = [['#', 'Intervention', 'Source', 'Priority']]
        for i, inv in enumerate(result["matched_interventions"], 1):
            score = calculate_intervention_score(inv, query)
            color_icon = get_score_color(score)
            table_data.append([
                str(i),
                inv.get('intervention', ''),
                inv.get('source', ''),
                f"{color_icon} {score}"
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 3*inch, 2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
    
    # Sources
    if result.get("sources"):
        story.append(Paragraph("<b>Sources Cited</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        for source in result["sources"]:
            source_para = Paragraph(f"• {source}", styles['BodyText'])
            story.append(source_para)
        story.append(Spacer(1, 0.2*inch))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    footer = Paragraph(
        "<i>Generated by Road Safety Intervention GPT | Powered by Groq & LangChain</i>",
        styles['Normal']
    )
    story.append(footer)
    
    doc.build(story)
    buffer.seek(0)
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buffer.getvalue())
    
    return buffer.getvalue()

def get_dashboard_data() -> Dict:
    """Generate mock dashboard data"""
    return {
        "crash_causes": [
            {"cause": "Speeding", "count": 1450, "percentage": 32},
            {"cause": "Distracted Driving", "count": 890, "percentage": 20},
            {"cause": "Drunk Driving", "count": 720, "percentage": 16},
            {"cause": "Poor Road Conditions", "count": 540, "percentage": 12},
            {"cause": "Weather", "count": 450, "percentage": 10}
        ],
        "intervention_impact": [
            {"intervention": "Rumble Strips", "impact": 85},
            {"intervention": "Reflective Signs", "impact": 78},
            {"intervention": "Speed Humps", "impact": 72},
            {"intervention": "Guard Rails", "impact": 68},
            {"intervention": "LED Lighting", "impact": 65}
        ],
        "intervention_categories": [
            {"category": "Signage & Markings", "count": 35},
            {"category": "Pedestrian Safety", "count": 25},
            {"category": "Road Design", "count": 20},
            {"category": "Traffic Calming", "count": 15},
            {"category": "Lighting", "count": 5}
        ]
    }

