import streamlit as st
import os
import sys
import re

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.utils.ui_components import set_page_config
from backend.services.code_checker import check_code_quality, evaluate_code_score, local_offline_analysis
from backend.services.youtube_service import get_youtube_recommendations
from frontend.utils.i18n import _t



def show_code_hub():
    st.title("💻 Intelligence Code Hub")
    st.markdown("Analyze, optimize, and safely refactor your code with expert AI feedback.")

    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this page.")
        return

    # IDE-style Toolbar
    toolbar_col1, toolbar_col2, toolbar_col3 = st.columns([2, 2, 1])
    
    with toolbar_col1:
        languages = [
            "C", "C++", "Java", "Python", "JavaScript", "TypeScript", "C#", 
            "Go", "Rust", "Swift", "Kotlin", "Ruby", "PHP", "SQL", "HTML/CSS", "Other"
        ]
        language = st.selectbox("🌐 Select Language", languages, index=0, label_visibility="collapsed")
    
    with toolbar_col2:
        st.write("") # Spacer

    with toolbar_col3:
        run_analysis = st.button("🚀 RUN ANALYSIS", use_container_width=True)

    # Editor and Results Layout
    editor_container = st.container()
    with editor_container:
        code_input = st.text_area(
            "Editor",
            placeholder=f"// Write your {language} code here...",
            height=350,
            label_visibility="collapsed"
        )

    if run_analysis:
        if code_input.strip():
            # 🧹 Clear old results immediately
            st.session_state.last_code_analysis = None
            st.session_state.last_ats_score = None
            
            with st.spinner("🧠 AI is analyzing your code architecture..."):
                analysis = check_code_quality(code_input, language)
                
                # If AI failed, use local fallback
                if "All AI Services Unavailable" in analysis or "Quota reached" in analysis or "Error during" in analysis:
                    local_remarks, local_score = local_offline_analysis(code_input, language)
                    st.session_state.last_code_analysis = local_remarks
                    st.session_state.last_ats_score = local_score
                else:
                    st.session_state.last_code_analysis = analysis
                    st.session_state.last_ats_score = evaluate_code_score(code_input, language)
        else:
            st.error("Please provide some code to analyze.")

    # Results Section
    if st.session_state.get("last_code_analysis"):
        st.markdown("---")
        
        analysis_text = st.session_state.last_code_analysis
        is_ai_error = "Local Analysis" in analysis_text # Fallback detected
        
        # 🚩 Check for Language Mismatch
        if "LANGUAGE_MISMATCH" in analysis_text:
            detected = analysis_text.split("LANGUAGE_MISMATCH:")[1].split("\n")[0].strip()
            st.error(f"⚠️ **Language Mismatch Detected!** You selected **{language}** but the code looks like **{detected}**.")
            st.info("Please select the correct language from the dropdown and try again.")
            return

        # 📟 Extract Expected Output
        output_match = re.search(r'Expected Output.*?\n(.*?)(?=###|🛠️|$)', analysis_text, re.DOTALL | re.IGNORECASE)
        expected_output = output_match.group(1).strip() if output_match else None
        
        # 🔄 Local Fallback Simulator
        if not expected_output and language.lower() == "python":
            prints = re.findall(r'print\s*\(\s*["\'](.*?)["\']\s*\)', code_input)
            if prints:
                expected_output = "\n".join(prints)

        st.subheader("📟 Predicted Terminal Output")
        if expected_output:
            formatted_output = expected_output.replace('\n', '<br>')
            st.markdown(f"""
                <div style="background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 10px; font-family: 'Consolas', monospace; border: 1px solid #333; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <div style="color: #6a9955; margin-bottom: 10px; font-size: 0.8rem;">// {"AI Predicted" if not is_ai_error else "Local Simulation (AI Offline)"}...</div>
                    <div style="font-size: 1rem; line-height: 1.5;">{formatted_output}</div>
                    <div style="color: #6a9955; margin-top: 10px; font-size: 0.8rem;"><br>--- Code Execution Successful ---</div>
                </div>
            """, unsafe_allow_html=True)
        elif is_ai_error:
            st.warning("📡 Simulation Unavailable: Terminal preview requires AI connection. Currently running in Local Offline Mode.")
        else:
            st.info("Simulation pending. The AI didn't provide a terminal output.")

        res_col1, res_col2 = st.columns([1, 2])
        
        with res_col1:
            st.subheader("📊 Metrics")
            score = st.session_state.get('last_ats_score', 0)
            
            # Display Score
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 30px; border-radius: 20px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                    <p style="margin: 0; color: #888; font-size: 0.9rem;">{ "Local Grade" if is_ai_error else "Quality Score"}</p>
                    <h1 style="margin: 10px 0; font-size: 4rem; font-family: 'Outfit'; color: {'#00D2D3' if score > 85 else '#FF9F43' if score > 65 else '#FF6B6B'};">
                        {score}<span style="font-size: 1.5rem; color: #555;">/100</span>
                    </h1>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.progress(score / 100)
            
            # 🔗 Subject-Based YouTube Recommendation (FIXED)
            st.markdown("### 🎥 Recommended Courses")
            # Improved regex to find the actual function name
            subject_match = re.search(r'(?:int|void|float|char|double|def|function)\s*\*?\s*([a-zA-Z0-9_]+)\s*\(', code_input)
            subject = subject_match.group(1) if subject_match else "Programming Concept"
            
            if subject.lower() in ["int", "main", "void", "if", "for", "while"]:
                subject = "General Logic"
            
            with st.spinner(f"Finding {subject} courses..."):
                recs = get_youtube_recommendations([f"{language} {subject} masterclass", f"explain {subject} in {language}"])
                for rec in recs[:2]:
                    st.markdown(f"📺 **Lesson**: [{rec['display_name']}]({rec['url']})")

        with res_col2:
            st.subheader("🧠 Expert Analysis & Refactoring")
            st.markdown(analysis_text)

if __name__ == "__main__":
    set_page_config(title="Intelligence Code Hub - NeuroTwin AI")
    show_code_hub()
