import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables from .env file in backend directory
def load_env():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    # Load .env from backend directory
    env_path = os.path.join(backend_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Warning: No .env file found at {env_path}")
    
    # Also check for .env in parent directory
    parent_env_path = os.path.join(os.path.dirname(backend_dir), '.env')
    if os.path.exists(parent_env_path):
        load_dotenv(parent_env_path)
        print(f"Loaded environment variables from {parent_env_path}")

def build_frontend():
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    print("Building frontend...")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Check if node_modules exists, if not run npm install
    if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], check=True)
    
    # Build the project
    print("Running webpack build...")
    subprocess.run(["npm", "run", "build"], check=True)
    
    # Verify the build directory exists
    dist_dir = os.path.join(frontend_dir, 'dist')
    if os.path.exists(dist_dir):
        print(f"Frontend build completed successfully at {dist_dir}")
        # List files in the dist directory to verify
        print("Build directory contents:")
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                print(f"  {os.path.join(root, file).replace(dist_dir, '')}")
    else:
        print(f"ERROR: Build directory {dist_dir} does not exist. Build may have failed.")
        sys.exit(1)

def start_server():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Load environment variables
    load_env()
    
    # Verify environment variables loaded
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print("DATABASE_URL is set")
    else:
        print("Warning: DATABASE_URL environment variable is not set")
    
    from app import app
    print("Starting Flask server on http://localhost:8000")
    app.run(debug=True, port=8000, host='0.0.0.0')

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--skip-build":
            print("Skipping frontend build...")
        else:
            build_frontend()
        
        start_server()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
