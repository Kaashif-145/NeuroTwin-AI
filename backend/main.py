# NeuroTwin AI Backend Service
# FastAPI app — loaded by uvicorn as backend.main:app

import os
import sys

# Add project root to sys.path for proper module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.services.pdf_extractor import extract_text_from_pdf
from backend.services.summarizer import generate_summary
from backend.services.topic_extractor import extract_topics
from backend.services.digital_twin import update_student_profile

# ── FastAPI app instance (required by uvicorn) ──────────────────────────────
app = FastAPI(
    title="NeuroTwin AI API",
    description="Backend API for NeuroTwin AI learning platform",
    version="1.0.0",
)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "NeuroTwin API"}


@app.get("/", tags=["Health"])
def root():
    return {"message": "NeuroTwin AI API is running. Visit /docs for API docs."}


# ── Request schema ────────────────────────────────────────────────────────────
class DocumentRequest(BaseModel):
    file_path: str


# ── Document processing endpoint ──────────────────────────────────────────────
@app.post("/process-document", tags=["Documents"])
def process_document(request: DocumentRequest):
    """
    Standard workflow to process a document and update the digital twin.
    """
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    text = extract_text_from_pdf(request.file_path)
    summary = generate_summary(text)
    topics = extract_topics(text)
    profile = update_student_profile(topics)

    return {
        "summary": summary,
        "topics": topics,
        "profile": profile,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

