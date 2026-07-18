"""
Build script to create a standalone MyNexus EXE - Simplified Version
"""
import os
import sys
import subprocess

# First, ensure PyInstaller is installed
print("Installing PyInstaller...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
print("✓ PyInstaller installed")

# Create build directory
os.makedirs("build", exist_ok=True)

# Create a simple ICO file
from PIL import Image
print("Creating icon...")
img = Image.new('RGB', (256, 256), color=(23, 32, 51))  # MyNexus blue
ico_path = os.path.abspath("build/my_nexus.ico")
img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
print(f"✓ Icon created: {ico_path}")

# Build the EXE
print("\nBuilding EXE with PyInstaller...")
print("This may take a few minutes...")

cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "MyNexus",
    "--icon", ico_path,
    "--add-data", f"{os.path.abspath('assets')}:assets",
    "--add-data", f"{os.path.abspath('config')}:config",
    "--distpath", os.path.abspath("dist"),
    "--buildpath", os.path.abspath("build/.pyinstaller"),
    "--specpath", os.path.abspath("build"),
    "--clean",
    os.path.abspath("src/main.py")
]

result = subprocess.run(cmd, capture_output=False)

if result.returncode == 0:
    exe_path = os.path.join(os.path.abspath("dist"), "MyNexus.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024*1024)
        print("\n" + "="*60)
        print("✓ SUCCESS! MyNexus.exe created!")
        print("="*60)
        print(f"\nLocation: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")
        print("\nUsage:")
        print("  • Double-click MyNexus.exe to run")
        print("  • Copy to any Windows system (no Python needed!)")
        print("  • Create shortcuts anywhere")
        print("  • No additional files required")
    else:
        print("✗ EXE file not found in dist directory")
        sys.exit(1)
else:
    print("✗ Build failed")
    sys.exit(1)
