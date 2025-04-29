import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import google.generativeai as genai
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import re
import numpy as np
from dotenv import load_dotenv
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize PaddleOCR
try:
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    logger.info("PaddleOCR initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
    raise

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PaddleOCR"""
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # Extract text from each page
    text = ""
    for image in images:
        # Convert PIL image to numpy array
        image_array = np.array(image)
        result = ocr.ocr(image_array)
        if result is not None:  # Check if result exists
            for line in result[0]:  # Access the first element of result
                if line is not None and len(line) >= 2:  # Check if line exists and has enough elements
                    text += line[1][0] + "\n"  # Access the text content
    
    return text

def extract_contact_info(text):
    """Extract name, email, and phone from text"""
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else None

    # Phone pattern (various formats)
    phone_pattern = r'(?:\+\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}'
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else None

    # Name extraction (first line or after "Name:" or similar)
    name = None
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        if line.strip() and not any(char.isdigit() for char in line):
            name = line.strip()
            break

    return {
        'name': name,
        'email': email,
        'phone': phone
    }

def analyze_resume(text):
    """Analyze resume using Gemini API"""
    try:
        prompt = f"""
        Analyze the following resume text and provide:
        1. A score out of 100 based on:
           - Content completeness
           - Professional presentation
           - Skills and experience relevance
           - Grammar and formatting
        2. Detailed analysis of strengths and weaknesses
        3. Areas for improvement

        Resume text:
        {text}

        Provide the response in the following format:
        Score: [number]
        Analysis: [detailed analysis]
        Areas for Improvement: [specific areas]
        """

        response = model.generate_content(prompt)
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        return response.text
    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        raise

def extract_score_from_analysis(analysis_text):
    """Extract score from analysis text"""
    try:
        # Look for score in the format "Score: [number]"
        score_match = re.search(r'Score:\s*(\d+)', analysis_text)
        if score_match:
            return int(score_match.group(1))
        return 0
    except Exception as e:
        logger.error(f"Error extracting score: {str(e)}")
        return 0

def get_course_recommendations(analysis):
    """Get course recommendations based on resume analysis"""
    try:
        prompt = f"""
        Based on the following resume analysis, recommend 3 specific online courses that would help improve the candidate's skills and address their areas for improvement.

        Analysis:
        {analysis}

        Provide the recommendations in the following format:
        Course 1:
        Title: [course title]
        Description: [brief description]
        Link: [course URL]

        Course 2:
        Title: [course title]
        Description: [brief description]
        Link: [course URL]

        Course 3:
        Title: [course title]
        Description: [brief description]
        Link: [course URL]
        """

        response = model.generate_content(prompt)
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Parse the response into structured format
        recommendations = []
        current_course = {}
        lines = response.text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('Course'):
                if current_course:
                    recommendations.append(current_course)
                current_course = {}
            elif line.startswith('Title:'):
                current_course['title'] = line.replace('Title:', '').strip()
            elif line.startswith('Description:'):
                current_course['description'] = line.replace('Description:', '').strip()
            elif line.startswith('Link:'):
                current_course['link'] = line.replace('Link:', '').strip()
        
        # Add the last course if exists
        if current_course:
            recommendations.append(current_course)
        
        # Only add fallback recommendations if we have no valid recommendations
        if not recommendations:
            recommendations = [
                {
                    'title': 'Professional Development Course',
                    'description': 'Enhance your professional skills with this comprehensive course.',
                    'link': 'https://www.coursera.org/learn/professional-development'
                },
                {
                    'title': 'Technical Skills Training',
                    'description': 'Improve your technical expertise with hands-on projects.',
                    'link': 'https://www.udemy.com/courses/development/'
                },
                {
                    'title': 'Soft Skills Workshop',
                    'description': 'Develop essential soft skills for career growth.',
                    'link': 'https://www.linkedin.com/learning/'
                }
            ]
        
        return recommendations[:3]  # Return only the first 3 recommendations

    except Exception as e:
        logger.error(f"Error in get_course_recommendations: {str(e)}")
        raise

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"File saved successfully: {filepath}")

        # Extract text from PDF
        logger.info("Starting text extraction from PDF")
        text = extract_text_from_pdf(filepath)
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        logger.info(f"Extracted text length: {len(text)}")

        # Extract contact information
        logger.info("Extracting contact information")
        contact_info = extract_contact_info(text)
        logger.info(f"Contact info extracted: {contact_info}")

        # Analyze resume
        logger.info("Starting resume analysis")
        analysis = analyze_resume(text)
        logger.info("Resume analysis completed")

        # Extract score from analysis
        score = extract_score_from_analysis(analysis)
        logger.info(f"Extracted score: {score}")

        # Get course recommendations
        logger.info("Getting course recommendations")
        recommendations = get_course_recommendations(analysis)
        logger.info("Course recommendations generated")

        # Clean up uploaded file
        os.remove(filepath)
        logger.info("Temporary file removed")

        return jsonify({
            'name': contact_info['name'],
            'email': contact_info['email'],
            'phone': contact_info['phone'],
            'score': score,  # Use the extracted score instead of hardcoded value
            'analysis': analysis,
            'recommendations': recommendations
        })

    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 