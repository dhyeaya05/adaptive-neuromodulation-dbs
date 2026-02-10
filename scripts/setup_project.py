#!/usr/bin/env python3
"""
Automated Project Setup Script
Initializes the adaptive neuromodulation project environment
"""

import os
import sys
import subprocess
from pathlib import Path
import urllib.request
import zipfile
import shutil

def print_section(text):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Ensure Python version is compatible"""
    print_section("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print("✅ Python version is compatible")

def create_virtual_environment():
    """Create Python virtual environment"""
    print_section("Creating Virtual Environment")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️  Virtual environment already exists. Skipping creation.")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        sys.exit(1)

def get_pip_command():
    """Get the appropriate pip command for the platform"""
    if sys.platform == "win32":
        return str(Path("venv/Scripts/pip"))
    else:
        return str(Path("venv/bin/pip"))

def install_dependencies():
    """Install required Python packages"""
    print_section("Installing Dependencies")
    
    pip_cmd = get_pip_command()
    
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        print("\nInstalling project dependencies...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        # Install package in development mode
        print("\nInstalling package in development mode...")
        subprocess.run([pip_cmd, "install", "-e", "."], check=True)
        
        print("✅ All dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\n💡 Try running manually:")
        print(f"   {pip_cmd} install -r requirements.txt")
        sys.exit(1)

def download_sample_data():
    """Download sample connectivity matrices and data"""
    print_section("Downloading Sample Data")
    
    data_dir = Path("data/connectivity_matrices")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("📥 Sample data will be generated during first notebook run")
    print("✅ Data directories created")

def create_example_config():
    """Create example configuration file"""
    print_section("Creating Configuration Files")
    
    config = """# Adaptive Neuromodulation Configuration
# Edit these parameters to customize your simulation

[simulation]
duration = 60.0  # seconds
sampling_rate = 1000  # Hz
dt = 0.001  # time step

[brain_model]
num_regions = 76  # Default atlas
connectivity_matrix = "data/connectivity_matrices/default_76.npz"
parkinsonian_mode = true

[controller]
type = "PID"  # Options: PID, LQR, MPC, RL
target_beta_power = 0.3  # Normalized target (0-1)

[pid_params]
kp = 2.0
ki = 0.5
kd = 0.1

[safety]
max_stimulation = 5.0  # mA
min_stimulation = 0.0  # mA
max_rate = 2.0  # mA/s
constraint_violations_allowed = 0

[visualization]
real_time_plot = true
save_figures = true
output_dir = "data/simulation_results"
"""
    
    config_path = Path("config.ini")
    if not config_path.exists():
        config_path.write_text(config)
        print("✅ Configuration file created: config.ini")
    else:
        print("⚠️  Configuration file already exists. Skipping.")

def create_gitignore():
    """Create .gitignore file"""
    print_section("Creating .gitignore")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Jupyter
.ipynb_checkpoints
*.ipynb_checkpoints

# Data
data/simulation_results/*.png
data/simulation_results/*.npy
data/simulation_results/*.h5
*.hdf5

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Models
models/*.pt
models/*.pth
models/*.h5
checkpoints/

# Secrets
.env
secrets.yaml
"""
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content)
        print("✅ .gitignore created")
    else:
        print("⚠️  .gitignore already exists. Skipping.")

def initialize_git():
    """Initialize git repository"""
    print_section("Initializing Git Repository")
    
    if Path(".git").exists():
        print("⚠️  Git repository already initialized. Skipping.")
        return
    
    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit: Project structure"],
            check=True,
            capture_output=True
        )
        print("✅ Git repository initialized and initial commit created")
    except subprocess.CalledProcessError:
        print("⚠️  Git not found. Skipping git initialization.")
        print("   Install git and run: git init")
    except Exception as e:
        print(f"⚠️  Git initialization failed: {e}")

def create_license():
    """Create MIT license file"""
    print_section("Creating License")
    
    license_text = """MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    license_path = Path("LICENSE")
    if not license_path.exists():
        license_path.write_text(license_text)
        print("✅ MIT License created")
    else:
        print("⚠️  License already exists. Skipping.")

def print_next_steps():
    """Print next steps for the user"""
    print_section("Setup Complete! 🎉")
    
    print("Next steps:")
    print("\n1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Start with the first notebook:")
    print("   jupyter notebook notebooks/01_brain_model_setup.ipynb")
    
    print("\n3. Or launch the interactive dashboard:")
    print("   python src/visualization/dashboard.py")
    
    print("\n4. Run tests:")
    print("   pytest tests/ -v")
    
    print("\n5. View documentation:")
    print("   Open README.md in your browser")
    
    print("\n📚 Resources:")
    print("   - The Virtual Brain: https://www.thevirtualbrain.org/")
    print("   - EBRAINS: https://ebrains.eu/")
    print("   - Project Documentation: docs/")
    
    print("\n💡 Tips:")
    print("   - Edit config.ini to customize simulation parameters")
    print("   - Check out notebooks/ for step-by-step tutorials")
    print("   - Use 'black' and 'isort' to format code before committing")

def main():
    """Main setup routine"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   Adaptive Neuromodulation System Setup                  ║
    ║   Closed-Loop DBS for Parkinson's Disease                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run setup steps
    check_python_version()
    create_virtual_environment()
    install_dependencies()
    download_sample_data()
    create_example_config()
    create_gitignore()
    create_license()
    initialize_git()
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
