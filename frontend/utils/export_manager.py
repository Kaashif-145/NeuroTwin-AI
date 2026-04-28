import os
import zipfile
import io
import streamlit as st

def create_project_zip(project_root):
    """Creates a ZIP file of the project, excluding unnecessary directories."""
    exclude_dirs = {'.venv', '.git', '__pycache__', '.gemini', 'node_modules'}
    exclude_files = {'.env', 'database.sqlite'} # Exclude sensitive or local DBs
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(project_root):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                
                file_path = os.path.join(root, file)
                # Create archive name relative to project root
                archive_name = os.path.relpath(file_path, project_root)
                z.write(file_path, archive_name)
                
    return buf.getvalue()
