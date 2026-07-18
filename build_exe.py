"""
Build script to create a standalone MyNexus EXE
"""
import os
import sys
import shutil
from pathlib import Path

# Convert SVG to ICO
def convert_svg_to_ico():
    """Convert the MyNexus SVG icon to ICO format"""
    try:
        from PIL import Image
        import cairosvg
        import io
        
        print("Converting SVG icon to ICO format...")
        
        # Read SVG and convert to PNG first
        svg_path = "assets/icons/my_nexus.svg"
        png_path = "build/my_nexus.png"
        ico_path = "build/my_nexus.ico"
        
        os.makedirs("build", exist_ok=True)
        
        # Convert SVG to PNG using cairosvg
        try:
            cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=256, output_height=256)
            print(f"✓ Created PNG: {png_path}")
        except ImportError:
            print("⚠ cairosvg not available, attempting manual conversion...")
            # Fallback: use a simple approach with PIL
            # For this, we'll try to convert it manually
            pass
        
        # Convert PNG to ICO
        if os.path.exists(png_path):
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"✓ Created ICO: {ico_path}")
            return ico_path
        else:
            print("⚠ Could not create PNG, creating simple ICO from SVG...")
            # Create a simple colored ICO as fallback
            img = Image.new('RGB', (256, 256), color=(23, 32, 51))  # MyNexus blue
            img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"✓ Created fallback ICO: {ico_path}")
            return ico_path
            
    except Exception as e:
        print(f"Error converting icon: {e}")
        print("Creating simple fallback ICO...")
        try:
            from PIL import Image
            os.makedirs("build", exist_ok=True)
            img = Image.new('RGB', (256, 256), color=(23, 32, 51))
            ico_path = "build/my_nexus.ico"
            img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            return ico_path
        except Exception as e2:
            print(f"Failed to create icon: {e2}")
            return None

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        os.system(f"{sys.executable} -m pip install pyinstaller -q")
        print("✓ PyInstaller installed")

def build_exe(ico_path):
    """Build the standalone EXE using PyInstaller"""
    print("\nBuilding standalone EXE...")
    
    # Ensure the ICO path is absolute to avoid specpath doubling
    if ico_path and not os.path.isabs(ico_path):
        ico_path = os.path.abspath(ico_path)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "MyNexus",
        "--icon", ico_path if ico_path else "",
        "--add-data", f"{os.path.abspath('assets')};assets",
        "--add-data", f"{os.path.abspath('config')};config",
        "--distpath", os.path.abspath("dist"),
        "--workpath", os.path.abspath("build/.pyinstaller"),
        "--specpath", os.path.abspath("build"),
        os.path.abspath("app.py")
    ]
    
    # Filter out empty strings
    cmd = [c for c in cmd if c]
    
    print(f"Running: {' '.join(cmd)}")
    result = os.system(" ".join(cmd))
    
    if result == 0:
        print("\n✓ EXE built successfully!")
        exe_path = Path("dist/MyNexus.exe")
        if exe_path.exists():
            print(f"✓ Executable created: {exe_path}")
            print(f"  Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        return True
    else:
        print("✗ Build failed")
        return False


def build_installer():
    """Compile the Inno Setup installer if ISCC is available."""
    import shutil
    iscc = shutil.which("ISCC") or shutil.which("iscc")
    # Common Inno Setup install locations
    candidates = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    ]
    if not iscc:
        for c in candidates:
            if os.path.exists(c):
                iscc = c
                break

    if not iscc:
        print("\n⚠ Inno Setup (ISCC) not found – skipping installer build.")
        print("  Install from: https://jrsoftware.org/isinfo.php")
        print("  Then re-run this script or compile MyNexus.iss manually.")
        return False

    print(f"\nBuilding Windows installer with: {iscc}")
    os.makedirs("dist/installer", exist_ok=True)
    result = os.system(f'"{iscc}" "MyNexus.iss"')
    if result == 0:
        print("\n✓ Installer built successfully!")
        import glob
        matches = glob.glob("dist/installer/MyNexus-Setup-*.exe")
        for m in matches:
            size_mb = Path(m).stat().st_size / (1024 * 1024)
            print(f"  Location: {m}  ({size_mb:.1f} MB)")
        return True
    else:
        print("✗ Installer build failed")
        return False


def main():
    print("=" * 60)
    print("MyNexus Standalone EXE Builder")
    print("=" * 60)
    
    # Create icon
    ico_path = convert_svg_to_ico()
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build EXE
    success = build_exe(ico_path or "build/my_nexus.ico")
    
    if success:
        print("\n" + "=" * 60)
        print("EXE Build Complete!")
        print("=" * 60)
        print("  Location: dist/MyNexus.exe")
        # Try to build the installer on top of the EXE
        build_installer()
        print("\n" + "=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
