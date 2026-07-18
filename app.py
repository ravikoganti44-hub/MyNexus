#!/usr/bin/env python3
"""
MyNexus Application Launcher
Entry point for the desktop application
"""
import sys
import os

if __name__ == "__main__":
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    # --seed-once: called by installer on first run to populate sample data.
    # The seeder itself guards against overwriting existing user data.
    if '--seed-once' in sys.argv:
        try:
            from seed_sample_data import seed_sample_data
            ok = seed_sample_data(force=False)
            sys.exit(0 if ok else 1)
        except Exception as e:
            print(f"Seeding error: {e}")
            sys.exit(1)

    try:
        from src.main import main
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
