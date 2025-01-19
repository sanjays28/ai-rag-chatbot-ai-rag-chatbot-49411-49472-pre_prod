"""Main Flask application for the chatbot component."""
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from config import Config
from services.pdf_processor import PDFProcessor
from services.chat_service import ChatService

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
pdf_processor = PDFProcessor()
chat_service = ChatService()

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
    # Validate PDF
    is_valid, error = pdf_processor.validate_pdf(file)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # Extract text
    text, error = pdf_processor.extract_text(file)
    if error:
        return jsonify({'error': error}), 500
    
    # Set context for chat service
    chat_service.set_context(text)
    
    return jsonify({'message': 'File uploaded and processed successfully'})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat interactions."""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400
    
    response, error = chat_service.get_response(data['query'])
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({'response': response})

@app.route('/feedback', methods=['POST'])
def feedback():
    """Handle user feedback."""
    data = request.get_json()
    if not data or 'feedback' not in data:
        return jsonify({'error': 'No feedback provided'}), 400
    
    success, error = chat_service.save_feedback(data['feedback'])
    if not success:
        return jsonify({'error': error}), 500
    
    return jsonify({'message': 'Feedback received successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)