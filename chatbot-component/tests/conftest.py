import pytest
from app import app as flask_app
import os
import tempfile
import threading
from werkzeug.serving import make_server

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    # Create a temporary directory for uploads
    with tempfile.TemporaryDirectory() as temp_dir:
        flask_app.config['TESTING'] = True
        flask_app.config['UPLOAD_FOLDER'] = temp_dir
        yield flask_app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    pdf_content = b"%PDF-1.3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000254 00000 n\n0000000332 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n427\n%%EOF"
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(pdf_content)
        f.flush()
        yield f.name
    os.unlink(f.name)

class FlaskServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()

@pytest.fixture(scope='session')
def flask_server():
    """Start Flask server for UI testing."""
    server = FlaskServerThread(flask_app)
    server.start()
    yield server
    server.shutdown()
    server.join()
