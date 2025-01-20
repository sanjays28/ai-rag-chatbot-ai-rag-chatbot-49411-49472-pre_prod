import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import time
from app import app

def is_ci_environment():
    """Check if running in a CI environment."""
    return os.environ.get('CI') == 'true' or os.environ.get('CONTINUOUS_INTEGRATION') == 'true'

@pytest.fixture(scope="module")
def driver():
    """Setup Chrome WebDriver in headless mode for testing."""
    if is_ci_environment():
        pytest.skip("Skipping UI tests in CI environment")
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        yield driver
    except Exception as e:
        pytest.skip(f"Skipping UI tests due to WebDriver setup error: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

@pytest.fixture(scope="module")
def server_url():
    """Start Flask server for testing."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Get port that Flask will use
        port = 5000
        url = f'http://localhost:{port}'
        yield url

def test_page_load(driver, server_url):
    """Test that the page loads correctly."""
    driver.get(server_url)
    assert "PDF Chat Assistant" in driver.title
    
    # Check main UI elements are present
    upload_section = driver.find_element(By.ID, "upload-section")
    assert upload_section.is_displayed()
    
    chat_section = driver.find_element(By.CLASS_NAME, "chat-section")
    assert chat_section.is_displayed()
    
    welcome_message = driver.find_element(By.CLASS_NAME, "welcome-message")
    assert "Upload a PDF" in welcome_message.text

def test_file_upload_button(driver, server_url, sample_pdf):
    """Test the file upload button functionality."""
    driver.get(server_url)
    
    # Find and interact with file input
    file_input = driver.find_element(By.ID, "file-input")
    file_input.send_keys(sample_pdf)
    
    # Wait for upload status
    upload_status = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "upload-status"))
    )
    assert "uploaded successfully" in upload_status.text.lower()

def test_invalid_file_upload(driver, server_url):
    """Test uploading an invalid file type."""
    driver.get(server_url)
    
    # Create a temporary text file
    with open("test.txt", "w") as f:
        f.write("test content")
    
    # Try to upload invalid file
    file_input = driver.find_element(By.ID, "file-input")
    file_input.send_keys(os.path.abspath("test.txt"))
    
    # Check for error message
    error_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "error-container"))
    )
    assert "invalid file type" in error_container.text.lower()
    
    # Cleanup
    os.remove("test.txt")

def test_chat_interaction(driver, server_url, sample_pdf):
    """Test chat message interaction."""
    driver.get(server_url)
    
    # Upload PDF first
    file_input = driver.find_element(By.ID, "file-input")
    file_input.send_keys(sample_pdf)
    
    # Wait for upload to complete
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, "upload-status"),
            "uploaded successfully"
        )
    )
    
    # Find chat input and send button
    chat_input = driver.find_element(By.ID, "user-input")
    send_button = driver.find_element(By.ID, "send-btn")
    
    # Verify send button is enabled after PDF upload
    assert send_button.is_enabled()
    
    # Send a test message
    test_message = "What is in the PDF?"
    chat_input.send_keys(test_message)
    send_button.click()
    
    # Wait for response in chat messages
    chat_messages = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "chat-messages"))
    )
    
    # Verify message appears in chat
    assert test_message in chat_messages.text

def test_loading_states(driver, server_url, sample_pdf):
    """Test loading indicators during operations."""
    driver.get(server_url)
    
    # Check loading indicator during file upload
    file_input = driver.find_element(By.ID, "file-input")
    file_input.send_keys(sample_pdf)
    
    loading_indicator = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "loading-indicator"))
    )
    assert loading_indicator.is_displayed()
    
    # Wait for upload to complete
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "loading-indicator"))
    )

def test_responsive_layout(driver, server_url):
    """Test responsive behavior of the layout."""
    driver.get(server_url)
    
    # Test different viewport sizes
    viewports = [
        (375, 667),  # Mobile
        (768, 1024), # Tablet
        (1920, 1080) # Desktop
    ]
    
    for width, height in viewports:
        driver.set_window_size(width, height)
        
        # Check if main container adjusts
        container = driver.find_element(By.CLASS_NAME, "container")
        container_width = container.size['width']
        
        # Container should be responsive to viewport
        assert container_width <= width
        
        # Check if chat input container is visible
        chat_input = driver.find_element(By.CLASS_NAME, "chat-input-container")
        assert chat_input.is_displayed()
