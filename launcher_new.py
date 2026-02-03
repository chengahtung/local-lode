"""
Unified Launcher for Local Lode
Starts FastAPI backend and opens browser automatically
"""
import subprocess
import time
import webbrowser
import sys
import signal
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print application header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  🗂️  Local Lode - Note Search Tool{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        print(f"{Colors.GREEN}✓{Colors.ENDC} Dependencies found")
        return True
    except ImportError as e:
        print(f"{Colors.FAIL}✗{Colors.ENDC} Missing dependencies: {e}")
        print(f"{Colors.WARNING}Please run: pip install -r requirements.txt{Colors.ENDC}")
        return False

def start_backend():
    """Start FastAPI backend server"""
    print(f"{Colors.CYAN}Starting backend server...{Colors.ENDC}")
    
    # Start uvicorn server
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", 
         "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return process

def wait_for_server(url="http://127.0.0.1:8000", timeout=30):
    """Wait for server to be ready"""
    import urllib.request
    import urllib.error
    
    print(f"{Colors.CYAN}Waiting for server to start...{Colors.ENDC}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            print(f"{Colors.GREEN}✓{Colors.ENDC} Server is ready!")
            return True
        except (urllib.error.URLError, ConnectionRefusedError):
            time.sleep(0.5)
    
    print(f"{Colors.FAIL}✗{Colors.ENDC} Server failed to start within {timeout} seconds")
    return False

def open_browser(url="http://127.0.0.1:8000"):
    """Open browser to application URL"""
    print(f"{Colors.CYAN}Opening browser...{Colors.ENDC}")
    webbrowser.open(url)
    print(f"{Colors.GREEN}✓{Colors.ENDC} Browser opened to {url}")

def main():
    """Main launcher function"""
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    
    try:
        # Wait for server to be ready
        if wait_for_server():
            # Open browser
            open_browser()
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}🚀 Local Lode is running!{Colors.ENDC}")
            print(f"{Colors.CYAN}   URL: http://127.0.0.1:8000{Colors.ENDC}")
            print(f"{Colors.WARNING}   Press Ctrl+C to stop the server{Colors.ENDC}\n")
            print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")
            
            # Stream backend logs
            for line in backend_process.stdout:
                print(line, end='')
        else:
            print(f"{Colors.FAIL}Failed to start server{Colors.ENDC}")
            backend_process.terminate()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Shutting down...{Colors.ENDC}")
        backend_process.terminate()
        backend_process.wait()
        print(f"{Colors.GREEN}✓{Colors.ENDC} Server stopped")
        print(f"\n{Colors.HEADER}Thank you for using Local Lode!{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
