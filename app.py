"""Root entrypoint for Streamlit application."""
import sys
from pathlib import Path
import runpy

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute the complete Streamlit UI application script in the runner context
target_app = str(root_dir / "src" / "ui" / "app.py")
runpy.run_path(target_app, run_name="__main__")
