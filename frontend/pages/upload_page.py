import os
import re
import sys
import time

import pandas as pd
import streamlit as st

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from backend.services.digital_twin import log_upload_history, update_student_profile
from backend.services.document_loader import load_document
from backend.services.flashcard_generator import generate_flashcards
from backend.services.keypoint_extractor import extract_key_details
from backend.services.level_classifier import classify_level
from backend.services.pdf_summary_generator import generate_pdf_summary
from backend.services.ppt_generator import generate_presentation
from backend.services.quiz_generator import generate_descriptive_paper, generate_quiz
from backend.services.study_planner import generate_study_structure
from backend.services.summarizer import clean_text_symbols, extract_equations, extract_key_features, generate_glossary, generate_summary
from backend.services.topic_extractor import extract_topics
from backend.services.translator import translate_text
from backend.services.youtube_service import get_youtube_recommendations
from frontend.utils.doc_manager import (
    clear_all_docs,
    get_active_doc_panel,
    get_uploaded_docs,
    has_active_docs,
    remove_doc,
    restore_uploaded_docs,
)
from frontend.utils.i18n import _t
from frontend.utils.ui_components import set_page_config


DATA_DIR = "data"


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _safe_filename(filename):
    return re.sub(r"[^A-Za-z0-9._-]", "_", filename)


def _persist_uploaded_files(uploaded_files):
    _ensure_data_dir()
    persisted_docs = []

    for uploaded_file in uploaded_files:
        timestamp = time.time()
        safe_name = _safe_filename(uploaded_file.name)
        stored_name = f"{int(timestamp * 1000)}_{safe_name}"
        file_path = os.path.join(DATA_DIR, stored_name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        persisted_docs.append(
            {
                "name": uploaded_file.name,
                "path": file_path,
                "size": int(uploaded_file.size or 0),
                "timestamp": timestamp,
            }
        )

    return persisted_docs


def _apply_translation():
    target_lang = st.session_state.get("target_lang", "en")

    if target_lang != "en":
        if st.session_state.get("last_translated_lang") != target_lang:
            with st.spinner(f"Translating to {target_lang}..."):
                st.session_state.summary = translate_text(
                    st.session_state.raw_summary,
                    target_lang=target_lang,
                )

                translated_quiz = {}
                for set_name, q_list in st.session_state.raw_quiz_sets.items():
                    trans_q_list = []
                    for q in q_list:
                        trans_q_list.append(
                            {
                                "question": translate_text(q["question"], target_lang),
                                "options": [
                                    translate_text(opt, target_lang) for opt in q["options"]
                                ],
                                "answer": translate_text(q["answer"], target_lang),
                            }
                        )
                    translated_quiz[set_name] = trans_q_list
                st.session_state.current_quiz_sets = translated_quiz

                st.session_state.current_flashcards = [
                    {
                        "front": translate_text(f["front"], target_lang),
                        "back": translate_text(f["back"], target_lang),
                    }
                    for f in st.session_state.raw_flashcards
                ]
                st.session_state.last_translated_lang = target_lang
    else:
        st.session_state.summary = st.session_state.raw_summary
        st.session_state.current_quiz_sets = st.session_state.raw_quiz_sets
        st.session_state.current_flashcards = st.session_state.raw_flashcards
        st.session_state.last_translated_lang = "en"


def _process_docs(doc_records, show_status=True):
    if not doc_records:
        clear_all_docs(delete_files=False)
        return

    aggregated_text = ""
    progress_bar = st.progress(0, text="Initializing processing engines...")

    for index, doc in enumerate(doc_records):
        step_progress = (index / len(doc_records)) * 0.2
        progress_bar.progress(step_progress, text=f"Reading file {index + 1}/{len(doc_records)}: {doc['name']}...")
        text = load_document(doc["path"])
        # Aggressive cleaning for mathematical symbols and technical artifacts
        text = clean_text_symbols(text)
        aggregated_text += f"\n--- Source: {doc['name']} ---\n{text}\n"

    st.session_state.raw_text = aggregated_text

    progress_bar.progress(0.25, text="Detecting content level and proficiency...")
    level = classify_level(aggregated_text)
    st.session_state.doc_level = level

    progress_bar.progress(0.40, text="Generating intelligent summary and mastery roadmap...")
    raw_summary = generate_summary(aggregated_text)
    st.session_state.raw_summary = raw_summary

    topics = extract_topics(aggregated_text)
    st.session_state.raw_topics = topics
    st.session_state.key_features = extract_key_details(aggregated_text)
    st.session_state.raw_equations = extract_equations(aggregated_text)

    progress_bar.progress(0.60, text="Creating AI quizzes and interactive flashcards...")
    quiz_sets = generate_quiz(aggregated_text)
    st.session_state.raw_quiz_sets = quiz_sets
    st.session_state.current_quiz_sets = quiz_sets
    st.session_state.active_quiz_name = None
    st.session_state.quiz_submitted = False

    flashcards = generate_flashcards(aggregated_text)
    st.session_state.raw_flashcards = flashcards
    st.session_state.current_flashcards = flashcards
    st.session_state.card_index = 0
    st.session_state.card_flipped = False

    progress_bar.progress(0.75, text="Extracting key terminology and definitions...")
    video_recs = get_youtube_recommendations(topics)
    st.session_state.video_recs = video_recs
    glossary = generate_glossary(topics, aggregated_text)
    st.session_state.current_glossary = glossary

    progress_bar.progress(0.85, text="Generating study roadmap and Descriptive Paper...")
    study_plan = generate_study_structure(topics, level)
    st.session_state.study_plan = study_plan
    descriptive_paper = generate_descriptive_paper(aggregated_text)
    st.session_state.descriptive_paper = descriptive_paper

    progress_bar.progress(0.95, text="Creating premium study deck and visual PDF report...")
    timestamp = int(time.time())
    base_name = _safe_filename(doc_records[0]["name"].rsplit(".", 1)[0] or "knowledge_base")
    ppt_name = f"{base_name}_{timestamp}.pptx"
    pdf_name = f"{base_name}_{timestamp}.pdf"

    ppt_path = generate_presentation(
        "Aggregated Knowledge Base",
        raw_summary,
        topics,
        glossary=glossary,
        equations=st.session_state.raw_equations,
        key_features=st.session_state.key_features,
        output_path=os.path.join(DATA_DIR, ppt_name),
    )
    pdf_path = generate_pdf_summary(
        base_name,
        raw_summary,
        topics,
        glossary=glossary,
        equations=st.session_state.raw_equations,
        key_features=st.session_state.key_features,
        output_path=os.path.join(DATA_DIR, pdf_name),
    )

    st.session_state.last_ppt = ppt_path
    st.session_state.last_pdf = pdf_path
    st.session_state.process_time = timestamp

    file_names = [doc["name"] for doc in doc_records]
    user_email = st.session_state.get("user_email", "guest")
    profile = update_student_profile(topics)
    history = log_upload_history(file_names, ppt_path=ppt_path, pdf_path=pdf_path, user_email=user_email)
    st.session_state.profile_data = profile
    st.session_state.upload_history = history
    st.session_state.processed_filenames = file_names
    st.session_state.processed_filename = ", ".join(file_names[:2]) + ("..." if len(file_names) > 2 else "")
    st.session_state.just_processed = True
    st.session_state.docs_need_reprocess = False
    st.session_state.uploaded_docs = doc_records

    _apply_translation()

    progress_bar.progress(1.0, text="Your Digital Twin has been updated!")
    time.sleep(1)
    progress_bar.empty()


def _handle_new_uploads(uploaded_files, append=False):
    if not uploaded_files:
        return

    new_docs = _persist_uploaded_files(uploaded_files)
    existing_docs = list(get_uploaded_docs()) if append else []

    if append:
        existing_names = {doc["name"]: doc for doc in existing_docs}
        for new_doc in new_docs:
            if new_doc["name"] in existing_names:
                remove_doc(new_doc["name"])
        existing_docs = list(get_uploaded_docs())

    updated_docs = existing_docs + new_docs
    st.session_state.uploaded_docs = updated_docs
    _process_docs(updated_docs, show_status=True)
    st.session_state.show_add_doc_uploader = False


def _render_results():
    display_title = "Knowledge Base" if len(st.session_state.processed_filenames) > 1 else _t("nav_upload")
    st.markdown(f"## {display_title}: {st.session_state.processed_filename}")

    if st.session_state.get("just_processed", False):
        st.success("Summary, presentation, and PDF report are ready.")
        st.session_state.just_processed = False

    # Document Mastery Tracker
    history_file = "database/upload_history.json"
    is_done = False
    if os.path.exists(history_file):
        import json
        with open(history_file, "r") as f:
            history = json.load(f)
        for fname in st.session_state.processed_filenames:
            if any(item["name"] == fname and item.get("completed", False) for item in history):
                is_done = True
                break
    
    if is_done:
        st.write("### 🏆 Mastery Achievement")
        st.progress(1.0, text="✨ 100% - This knowledge is officially part of your Digital Twin!")
    else:
        st.write("### 📖 Study Momentum")
        st.progress(0.45, text="45% - Initial processing complete. Take the quiz to reach 100%!")

    st.markdown("---")
    col_toolbox, col_content = st.columns([1, 2])

    with col_toolbox:
        st.markdown("<div class='toolbox-container'>", unsafe_allow_html=True)
        st.subheader(f"🛠️ {_t('toolbox_title')}")
        st.write("Recommended next steps for mastery:")

        if st.button(f"🎯 {_t('take_quiz')}", use_container_width=True, key="toolbox_quiz"):
            st.switch_page("pages/quiz_page.py")

        if st.button("📝 AI Exam Builder", use_container_width=True, key="toolbox_exam"):
            st.switch_page("pages/exam_builder.py")

        if st.button("📊 AI Deck Creator", use_container_width=True, key="toolbox_deck"):
            st.switch_page("pages/presentation_creator.py")

        if st.button("🗺️ View Study Roadmap", use_container_width=True, key="toolbox_roadmap"):
            # We can still keep simple expansion for roadmap if desired, 
            # or move it to recommendations
            st.markdown("### 🗺️ 7-Day Study Roadmap")
            roadmap = st.session_state.get("study_plan", {}).get("roadmap", {})
            for day, topics_in_day in roadmap.items():
                st.write(f"**{day}:** {', '.join(topics_in_day)}")
            for advice in st.session_state.get("study_plan", {}).get("advice", []):
                st.caption(f"💡 {advice}")

        if st.button(f"🎴 {_t('study_flash')}", use_container_width=True, key="toolbox_flash"):
            st.switch_page("pages/flashcard_ui.py")

        btn_ts = st.session_state.get("process_time", 0)

        if "last_ppt" in st.session_state and os.path.exists(st.session_state.last_ppt):
            with open(st.session_state.last_ppt, "rb") as f:
                st.download_button(
                    f"📥 {_t('download_ppt')}",
                    f,
                    file_name=f"Study_Guide_{btn_ts}.pptx",
                    use_container_width=True,
                    key=f"dl_ppt_{btn_ts}",
                )

        if "last_pdf" in st.session_state and os.path.exists(st.session_state.last_pdf):
            with open(st.session_state.last_pdf, "rb") as f:
                st.download_button(
                    f"📥 {_t('download_pdf')}",
                    f,
                    file_name=f"Insights_Report_{btn_ts}.pdf",
                    use_container_width=True,
                    key=f"dl_pdf_{btn_ts}",
                )

        if st.button(f"🔋 {_t('optimize_twin')}", use_container_width=True, key="toolbox_train"):
            st.switch_page("pages/train_ui.py")

        if st.session_state.get("video_recs"):
            st.markdown("---")
            st.subheader(f"🎥 {_t('video_lessons')}")
            for rec in st.session_state.video_recs:
                st.markdown(f"🔗 [{rec['display_name']}]({rec['url']})")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_content:
        st.markdown(f"### 📝 {_t('intel_summary')}")
        st.info(st.session_state.summary)

        topics_html = "".join(
            [
                f"<span class='action-card' style='display:inline-block; margin-right:10px;'>{topic}</span>"
                for topic in st.session_state.raw_topics
            ]
        )
        st.markdown(topics_html, unsafe_allow_html=True)
        
        st.markdown(f"### 💎 Key Knowledge Details")
        st.write("Fundamental insights extracted from your material:")
        for detail in st.session_state.get("key_features", []):
            st.markdown(f"✅ **{detail}**")

        if st.button(f"📊 {_t('open_insights')}", use_container_width=True):
            st.switch_page("pages/digital_twin_dashboard.py")


def _render_library():
    st.markdown("---")

    col_lib1, col_lib2 = st.columns([3, 1])
    with col_lib1:
        st.subheader("📂 Your Academic Library")
        st.markdown(
            "Persistent history of documents uploaded and processed. Select a row and press `Delete` to remove it."
        )

    history_file = "database/upload_history.json"

    with col_lib2:
        if os.path.exists(history_file):
            if st.button("🗑️ Clear Library", use_container_width=True, key="clear_lib"):
                os.remove(history_file)
                st.rerun()

    if not os.path.exists(history_file):
        st.info("No upload history found yet. Start uploading to build your library!")
        return

    import json
    with open(history_file, "r") as f:
        history = json.load(f)

    if isinstance(history, list) and len(history) > 0:
        df = pd.DataFrame(history)
        # Filter for current user only (Admin sees everything)
        user_email = st.session_state.get("user_email", "guest")
        is_admin = user_email == "mattokaasif145@gmail.com"
        
        if not is_admin:
            df = df[df.get("user_email") == user_email]
        
        # Auto-detect and clean existing duplicates (keep most recent)
        if not df.empty and "name" in df.columns:
            df = df.sort_values("timestamp", ascending=False).drop_duplicates("name", keep="first")
        
        # Ensure columns exist
        for col in ["completed", "ppt_path", "pdf_path"]:
            if col not in df.columns:
                df[col] = None

        st.markdown("#### 📚 Document Inventory")
        
        for i, row in df.iterrows():
            filename = row['name']
            is_completed = row.get("completed", False)
            
            # Premium Document Card
            with st.container(border=True):
                # Row 1: Document Logo + Name + Status
                cols = st.columns([0.5, 4, 1.5, 2.5])
                
                with cols[0]:
                    # Status Checkbox (Interactive)
                    new_status = st.checkbox(" ", value=is_completed, key=f"cb_card_{i}", label_visibility="collapsed")
                    if new_status != is_completed:
                        for item in history:
                            if item["name"] == filename:
                                item["completed"] = new_status
                                break
                        with open(history_file, "w") as f:
                            json.dump(history, f, indent=4)
                        st.session_state.docs_need_reprocess = True 
                        st.rerun()

                with cols[1]:
                    # Document Title (Clickable Button)
                    if st.button(f"📄 {filename}", key=f"btn_card_name_{i}", use_container_width=True):
                        import glob
                        file_pattern = os.path.join(DATA_DIR, f"*_{_safe_filename(filename)}")
                        matches = glob.glob(file_pattern)
                        if matches:
                            doc_record = {"name": filename, "path": matches[0], "size": 0, "timestamp": time.time()}
                            st.session_state.last_restudied = filename
                            _process_docs([doc_record], show_status=True)
                            st.rerun()

                with cols[2]:
                    # Processing Date
                    st.caption("📅 Processed")
                    st.write(f"<small>{row.get('date', 'N/A')}</small>", unsafe_allow_html=True)

                with cols[3]:
                    # Action Bar (Downloads + Delete)
                    st.caption("⚡ Actions")
                    act_cols = st.columns([1, 1, 1])
                    
                    ppt_file = row.get("ppt_path")
                    pdf_file = row.get("pdf_path")
                    
                    if isinstance(ppt_file, str) and ppt_file and os.path.exists(ppt_file):
                        with open(ppt_file, "rb") as f:
                            act_cols[0].download_button("📊", f, file_name=os.path.basename(ppt_file), key=f"dl_ppt_c_{i}", help="Presentation")
                    
                    if isinstance(pdf_file, str) and pdf_file and os.path.exists(pdf_file):
                        with open(pdf_file, "rb") as f:
                            act_cols[1].download_button("📄", f, file_name=os.path.basename(pdf_file), key=f"dl_pdf_c_{i}", help="Report")
                    
                    if act_cols[2].button("🗑️", key=f"btn_del_c_{i}", help="Delete from library"):
                        new_history = [item for item in history if item["name"] != filename]
                        with open(history_file, "w") as f:
                            json.dump(new_history, f, indent=4)
                        st.rerun()

            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

        # Navigation Footer
        st.markdown("---")
        st.caption("💡 TIP: Click on a document name to instantly set it as your active Digital Twin focus.")
    else:
        st.info("No upload history found yet. Start uploading to build your library!")


def show_upload_page():
    if not st.session_state.get("authenticated", False):
        st.warning("Please login to access this page.")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        return

    st.title(f"📄 {_t('upload_title')}")
    st.markdown(_t("upload_desc"))

    st.session_state.setdefault("uploaded_docs", [])
    st.session_state.setdefault("show_add_doc_uploader", False)
    restore_uploaded_docs(DATA_DIR)

    if st.session_state.get("docs_need_reprocess") and has_active_docs():
        _process_docs(get_uploaded_docs(), show_status=True)

    if has_active_docs():
        actions = get_active_doc_panel(key_prefix="upload_page_docs")

        if actions["remove_doc"]:
            removed = remove_doc(actions["remove_doc"])
            if removed and has_active_docs():
                _process_docs(get_uploaded_docs(), show_status=True)
            elif removed:
                st.success(f"Removed {removed['name']}.")
                st.session_state.show_add_doc_uploader = False
                st.rerun()

        if actions["replace_all"]:
            clear_all_docs(delete_files=True)
            st.session_state.show_add_doc_uploader = False
            st.rerun()

        if actions["add_more"]:
            st.session_state.show_add_doc_uploader = True

        if st.session_state.get("show_add_doc_uploader"):
            additional_files = st.file_uploader(
                "Add more documents",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                key="add_docs_uploader",
            )
            if additional_files:
                _handle_new_uploads(additional_files, append=True)

    else:
        uploaded_files = st.file_uploader(
            _t("nav_upload"),
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="fresh_docs_uploader",
        )
        if uploaded_files:
            _handle_new_uploads(uploaded_files, append=False)

    if has_active_docs() and st.session_state.get("raw_summary"):
        _apply_translation()
        _render_results()

    _render_library()


if __name__ == "__main__":
    set_page_config(title="Upload Documents - NeuroTwin AI")
    show_upload_page()
