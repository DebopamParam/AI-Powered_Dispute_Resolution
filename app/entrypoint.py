import subprocess
import sys
import os
import threading
import time


def run_fastapi():
    print("Starting FastAPI backend...")
    subprocess.run(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])


def run_streamlit():
    print("Starting Streamlit from frontend directory...")
    # Change to the frontend directory first
    os.chdir("app/frontend")
    # Then run streamlit (note the path is now relative to the frontend directory)
    subprocess.run(["streamlit", "run", "streamlit_app.py", "--server.port", "7860", "--server.address", "0.0.0.0"])


if __name__ == "__main__":
    # Store the original directory to potentially return to it later if needed
    original_dir = os.getcwd()
    
    # Start FastAPI in a separate thread
    api_thread = threading.Thread(target=run_fastapi)
    api_thread.daemon = True
    api_thread.start()

    # Give FastAPI some time to start up
    time.sleep(3)

    # Start Streamlit in the main thread
    run_streamlit()