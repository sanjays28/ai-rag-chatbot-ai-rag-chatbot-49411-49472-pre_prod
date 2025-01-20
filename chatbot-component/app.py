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
    """Handle PDF file upload.
    
    Validates:
    - File is present in request
    - File has a valid name
    - File is a valid PDF
    - PDF can be processed and text extracted
    
    Returns:
        JSON response with either:
        - success: {'message': success_message}
        - error: {'error': error_message, 'status': status_code}, with appropriate status code
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'status': 400
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 400
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type. Only PDF files are allowed',
                'status': 400
            }), 400
        
        # Validate PDF
        is_valid, error = pdf_processor.validate_pdf(file)
        if not is_valid:
            return jsonify({
                'error': error,
                'status': 400
            }), 400
        
        # Extract text
        text, error = pdf_processor.extract_text(file)
        if error:
            return jsonify({
                'error': error,
                'status': 500
            }), 500
        
        # Set context for chat service
        chat_service.set_context(text)
        
        return jsonify({'message': 'File uploaded and processed successfully'})
    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 500
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat interactions with input validation.
    
    Validates:
    - Request format is valid JSON
    - Query field is present in request
    - Query is not empty or whitespace
    - Query length is within limits (1000 characters)
    
    Returns:
        JSON response with either:
        - success: {'response': response_text}
        - error: {'error': error_message, 'status': status_code}, with appropriate status code
    """
    try:
        # Validate request format
        try:
            data = request.get_json()
        except Exception:
            return jsonify({
                'error': 'Invalid request format. JSON body required',
                'status': 400
            }), 400

        if not data:
            return jsonify({
                'error': 'No query provided',
                'status': 400
            }), 400
        
        # Validate query presence
        if 'query' not in data:
            return jsonify({
                'error': 'No query provided',
                'status': 400
            }), 400
        
        query = data['query']
        
        # Validate query is not empty or whitespace
        if not query or not query.strip():
            return jsonify({
                'error': 'Query cannot be empty or whitespace',
                'status': 400
            }), 400
        
        # Validate query length
        if len(query) > 1000:
            return jsonify({
                'error': 'Query exceeds maximum length of 1000 characters',
                'status': 400
            }), 400
        
        # Process valid query
        response, error = chat_service.get_response(query.strip())
        if error:
            if error == "Rate limit exceeded. Please try again later.":
                return jsonify({
                    'error': error,
                    'status': 429
                }), 429
            return jsonify({
                'error': error,
                'status': 500
            }), 500
        
        return jsonify({'response': response})
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 500
        }), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """Handle user feedback.
    
    Validates:
    - Request format is valid JSON
    - Feedback field is present in request
    
    Returns:
        JSON response with either:
        - success: {'message': success_message}
        - error: {'error': error_message, 'status': status_code}, with appropriate status code
    """
    try:
        data = request.get_json()
        if not data or 'feedback' not in data:
            return jsonify({
                'error': 'No feedback provided',
                'status': 400
            }), 400
        
        success, error = chat_service.save_feedback(data['feedback'])
        if not success:
            return jsonify({
                'error': error,
                'status': 500
            }), 500
        
        return jsonify({'message': 'Feedback received successfully'})
    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 500
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
