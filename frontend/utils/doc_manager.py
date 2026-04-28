import os
import re
from datetime import datetime

import streamlit as st


UPLOADED_DOCS_KEY = "uploaded_docs"
PROCESSED_STATE_KEYS = [
    "processed_filenames",
    "processed_filename",
    "raw_text",
    "raw_summary",
    "raw_topics",
    "raw_quiz_sets",
    "raw_flashcards",
    "raw_equations",
    "key_features",
    "summary",
    "current_quiz_sets",
    "active_quiz_name",
    "quiz_submitted",
    "user_answers",
    "current_flashcards",
    "card_index",
    "card_flipped",
    "video_recs",
    "current_glossary",
    "study_plan",
    "descriptive_paper",
    "doc_level",
    "last_ppt",
    "last_pdf",
    "process_time",
    "profile_data",
    "upload_history",
    "just_processed",
    "last_translated_lang",
]


def has_active_docs():
    return bool(st.session_state.get(UPLOADED_DOCS_KEY))


def get_uploaded_docs():
    return st.session_state.get(UPLOADED_DOCS_KEY, [])


def _safe_filename(filename):
    return re.sub(r"[^A-Za-z0-9._-]", "_", filename)


def restore_uploaded_docs(data_dir="data"):
    existing_docs = get_uploaded_docs()
    if existing_docs:
        return existing_docs

    processed_filenames = st.session_state.get("processed_filenames", [])
    if not processed_filenames or not os.path.isdir(data_dir):
        return []

    restored_docs = []
    data_files = os.listdir(data_dir)

    for original_name in processed_filenames:
        safe_name = _safe_filename(original_name)
        matching_paths = []
        for candidate in data_files:
            candidate_path = os.path.join(data_dir, candidate)
            if not os.path.isfile(candidate_path):
                continue
            if candidate == original_name or candidate.endswith(f"_{safe_name}"):
                matching_paths.append(candidate_path)

        if not matching_paths:
            continue

        best_path = max(matching_paths, key=os.path.getmtime)
        restored_docs.append(
            {
                "name": original_name,
                "path": best_path,
                "size": os.path.getsize(best_path),
                "timestamp": os.path.getmtime(best_path),
            }
        )

    if restored_docs:
        st.session_state[UPLOADED_DOCS_KEY] = restored_docs

    return restored_docs


def clear_processed_state():
    for key in PROCESSED_STATE_KEYS:
        st.session_state.pop(key, None)


def clear_all_docs(delete_files=True):
    docs = list(get_uploaded_docs())
    if delete_files:
        for doc in docs:
            path = doc.get("path")
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
    st.session_state[UPLOADED_DOCS_KEY] = []
    clear_processed_state()


def remove_doc(filename, delete_file=True):
    docs = list(get_uploaded_docs())
    removed_doc = None
    remaining_docs = []

    for doc in docs:
        if removed_doc is None and doc.get("name") == filename:
            removed_doc = doc
        else:
            remaining_docs.append(doc)

    if removed_doc and delete_file:
        path = removed_doc.get("path")
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    st.session_state[UPLOADED_DOCS_KEY] = remaining_docs

    if remaining_docs:
        clear_processed_state()
    else:
        clear_all_docs(delete_files=False)

    return removed_doc


def _format_size(size_bytes):
    size = float(size_bytes or 0)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return "0 B"


def _format_timestamp(timestamp_value):
    if not timestamp_value:
        return "Unknown time"

    try:
        timestamp = datetime.fromtimestamp(float(timestamp_value))
        return timestamp.strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError, OSError):
        return "Unknown time"


def get_active_doc_panel(
    key_prefix="doc_panel",
    show_manage_button=False,
    in_sidebar=False,
    show_action_buttons=True,
):
    docs = get_uploaded_docs()
    actions = {"remove_doc": None, "add_more": False, "replace_all": False}

    if not docs:
        return actions

    target = st.sidebar if in_sidebar else st
    target.markdown("### Active Documents" if not in_sidebar else "### Active Document")

    for index, doc in enumerate(docs):
        name = doc.get("name", f"Document {index + 1}")
        meta = f"{_format_size(doc.get('size', 0))} | {_format_timestamp(doc.get('timestamp'))}"
        col_main, col_action = target.columns([6, 1])
        with col_main:
            st.markdown(f"**{name}**")
            st.caption(meta)
        with col_action:
            if st.button("X", key=f"{key_prefix}_remove_{index}", use_container_width=True):
                actions["remove_doc"] = name

    if show_action_buttons:
        col_add, col_replace = target.columns(2)
        with col_add:
            if st.button("Add Another", key=f"{key_prefix}_add_more", use_container_width=True):
                actions["add_more"] = True
        with col_replace:
            if st.button("Replace All", key=f"{key_prefix}_replace_all", use_container_width=True):
                actions["replace_all"] = True

    if show_manage_button:
        if target.button("Manage Documents", key=f"{key_prefix}_manage", use_container_width=True):
            st.switch_page("pages/upload_page.py")

    return actions
