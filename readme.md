# 🧠 NeuroTwin AI: Your Digital Academic Twin

NeuroTwin AI is a high-fidelity, AI-powered learning ecosystem designed to revolutionize how students and researchers interact with educational materials. By transforming static documents into a **Digital Twin**, it tracks your mastery, provides personalized recommendations, and offers brutal career insights to bridge the gap between academia and industry.

---

## ✨ Key Features

### 🌌 Quantum Deep Space UI
- **Premium Aesthetics**: A stunning dark-mode interface featuring vibrant gradients (Neon Pink, Electric Purple, Cyan) and glassmorphic cards.
- **Dynamic Navigation**: A streamlined "Top Navigation" layout for seamless switching between the Research, Learning, and Career modules.
- **Fluid Micro-animations**: High-end transitions and interactive elements designed for a premium user experience.

### 🔐 Adaptive Authentication & Security
- **Cloudflare Turnstile Simulation**: Premium human verification challenge screen for added security.
- **Smart Session Management**: Intelligent session persistence saves your identity and OTP phase reliably, preventing you from getting locked out or stuck in loops.
- **Multi-method Security**: Support for standard credentials, OTP-based email verification, and Google OAuth SSO simulation.

### 💻 Intelligence Code Hub (New!)
- **Universal Local Offline Engine**: When AI APIs are exhausted, the app seamlessly falls back to a powerful local static analysis engine.
- **Advanced Python AST Parsing**: The offline engine tracks infinite recursion, logic errors, missing base cases, and infinite loops for Python *without* the internet.
- **Multi-Language Structural Checks**: C, C++, Java, and C# are thoroughly verified offline for missing return types (e.g., `static mergesort`), absent algorithm recursion, unbalanced braces, and missing semicolons.
- **Strict Academic Grading**: Code isn't just checked for syntax—you are graded on a harsh 0-100 rubric that penalizes poor performance, logic failures, and bad architecture.

### 🔥 The Resume Roast
- **Brutally Honest Analysis**: Get unfiltered feedback on your CV from an "AI Recruiter" perspective. No sugarcoating, just the hard truth about your profile.
- **ATS Compatibility Score**: Real-time scoring against industry-standard Applicant Tracking Systems.
- **Corporate Matching**: Automatic recommendation of companies where your profile would stand out most.

### 📄 Intelligent Document Processing
- **High-Fidelity Extraction**: Deep-parsing of PDFs and Word documents using `PyMuPDF`.
- **AI-Driven Insights**: State-of-the-art summarization and concept extraction.
- **Multi-language Support**: Real-time translation and chat assistance in over 6 languages (English, Hindi, Punjabi, Spanish, French, etc.).

### 📊 Digital Twin Mastery Dashboard
- **Mastery Visualization**: Interactive `Plotly` charts tracking your knowledge evolution across subjects.
- **Concept Mapping**: A detailed breakdown of unique concepts identified from your personal study library.
- **Automated Study Tools**: Instantly generate Quizzes and Flashcards from your uploaded materials.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (Python 3.10 recommended)
- Streamlit

### Installation & Run

1. **Clone and Enter**:
   ```bash
   git clone https://github.com/your-repo/neurotwin-ai.git
   cd neurotwin-ai
   ```

2. **Setup Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .\.venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Launch the Intelligence**:
   ```bash
   streamlit run frontend/app.py
   ```

---

## 🛠️ Project Architecture

- **`frontend/`**: The visual core of NeuroTwin.
  - **`pages/`**: Modular logic for "Intelligence Code Hub," "The Resume Roast," "Digital Twin Dashboard," "AI Quiz," and more.
  - **`utils/`**: Internationalization (i18n) and shared UI components.
- **`backend/`**: The cognitive engine.
  - **`services/`**: Custom AST Code Analyzers, Document Loaders, and AI Summary generators.
  - **`utils/`**: LLM API key rotation, User Database (JSON-based with normalization), and Session Management.
- **`database/`**: Persistent storage for user profiles, upload history, and session data.

---

## 🤖 Tech Stack

- **UI Framework**: [Streamlit](https://streamlit.io/)
- **Core Intelligence**: Google Gemini API & Offline Regex/AST Parsers
- **Data Visuals**: [Plotly](https://plotly.com/)
- **PDF Engine**: [PyMuPDF](https://pymupdf.readthedocs.io/)
- **Styling**: Vanilla CSS with Advanced CSS Gradients & Filters

---

## 🤝 Community
Contributions are what make the open-source world such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

© 2026 NeuroTwin AI Platform - The Future of Academic Intelligence.
