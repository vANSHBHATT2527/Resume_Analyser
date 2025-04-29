# Resume Analyzer

A web application that analyzes resumes using Google's Gemini API and PaddleOCR. The application provides:
- Resume scoring (0-100)
- Contact information extraction (name, email, phone)
- Detailed analysis of strengths and weaknesses
- Personalized course recommendations
- Modern, responsive UI with drag-and-drop support

## Features

- PDF resume upload with drag-and-drop interface
- Automatic extraction of contact information using regex patterns
- Resume scoring based on multiple criteria:
  - Content completeness
  - Professional presentation
  - Skills and experience relevance
  - Grammar and formatting
- Detailed analysis of resume content
- Personalized course recommendations based on analysis
- Markdown support for formatted analysis display
- Responsive design that works on all devices
- Real-time feedback and loading states

## Prerequisites

- Python 3.7 or higher
- Google Gemini API key
- Poppler (for PDF processing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd resume-analyzer
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Poppler (required for PDF processing):
- On Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils
```
- On macOS:
```bash
brew install poppler
```
- On Windows:
Download and install from: http://blog.alivate.com.au/poppler-windows/

4. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload your resume PDF and wait for the analysis.

## Technical Details

### Frontend
- HTML5 with semantic markup
- CSS3 with modern styling and animations
- JavaScript for interactive features
- Marked.js for markdown parsing
- Highlight.js for code syntax highlighting

### Backend
- Python Flask server
- PaddleOCR for PDF text extraction
- Google Gemini API for resume analysis
- Regex patterns for contact information extraction
- PDF processing with pdf2image

### Features Implementation
- Resume scoring: Extracts numerical score from Gemini API analysis
- Contact extraction: Uses regex patterns for email, phone, and name detection
- Course recommendations: Parses structured data from Gemini API response
- Error handling: Comprehensive error handling and logging
- File processing: Secure file handling with size limits and cleanup

## Project Structure
```
resume-analyzer/
├── app.py              # Flask backend application
├── index.html          # Main frontend page
├── styles.css          # CSS styles
├── script.js           # Frontend JavaScript
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── uploads/           # Temporary upload directory
```

## Error Handling
- File type validation (PDF only)
- File size limits (16MB max)
- Empty file checks
- OCR failure handling
- API error handling
- Invalid response handling

## Security Features
- Secure filename handling
- Temporary file cleanup
- Environment variable protection
- File size restrictions
- Input validation

"# Resume_Analyser" 
"# Resume_Analyser" 
"# Resume_Analyser" 
