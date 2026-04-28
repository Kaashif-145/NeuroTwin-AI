import os
import re

from fpdf import FPDF


class IntelligencePDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(110)
            self.cell(0, 8, "NeuroTwin AI Study Intelligence", 0, 1, "R")
            self.set_draw_color(220, 224, 230)
            self.line(10, 18, 200, 18)
            self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 8, f"Page {self.page_no()}", 0, 0, "C")

    def section_title(self, text):
        self.set_font("helvetica", "B", 15)
        self.set_text_color(18, 43, 85)
        self.cell(0, 10, sanitize_text(text), 0, 1, "L")
        self.ln(1)

    def paragraph(self, text, size=11):
        self.set_font("helvetica", "", size)
        self.set_text_color(55, 55, 55)
        self.multi_cell(0, 7, sanitize_text(text))
        self.ln(1)

    def bullet_list(self, items, bullet="-"):
        self.set_font("helvetica", "", 11)
        self.set_text_color(55, 55, 55)
        available_width = max(20, self.w - self.r_margin - self.x)
        for item in items:
            self.multi_cell(available_width, 7, sanitize_text(f"{bullet} {item}"))
        self.ln(1)

    def feature_card(self, title, body, fill_color):
        x = self.get_x()
        y = self.get_y()
        self.set_fill_color(*fill_color)
        self.set_draw_color(255, 196, 112)
        self.rect(x, y, 190, 28, style="FD")
        self.set_xy(x + 4, y + 3)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(18, 43, 85)
        self.cell(0, 6, sanitize_text(title), 0, 1)
        self.set_x(x + 4)
        self.set_font("helvetica", "", 10)
        self.set_text_color(70, 70, 70)
        self.multi_cell(182, 5.5, sanitize_text(body))
        self.set_y(y + 32)


def sanitize_text(text):
    if not isinstance(text, str):
        return ""

    # Comprehensive mathematical and special character mapping for PDF compatibility
    replacements = {
        "\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2022": "-",
        "∫": "[INTEGRAL]", "∑": "[SUM]", "≈": "approx.", "≤": "<=", "≥": ">=",
        "±": "+/-", "→": "->", "∞": "INF", "π": "PI", "θ": "theta",
        "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "Δ": "Delta",
        "∇": "nabla", "∈": "belongs to", "∉": "not in", "≠": "!=", "λ": "lambda",
        "μ": "mu", "σ": "sigma", "ω": "omega", "×": "*", "÷": "/", "√": "sqrt",
        "∂": "d", "∀": "for all", "∃": "exists", "∩": "intersection", "∪": "union",
        "⊂": "subset of", "⊃": "superset of", "∠": "angle", "⊥": "perpendicular",
        "²": "^2", "³": "^3", "¹": "^1", "⁰": "^0", "⁴": "^4", "⁵": "^5",
        "⁶": "^6", "⁷": "^7", "⁸": "^8", "⁹": "^9", "½": "1/2", "¼": "1/4",
        "¾": "3/4", "≡": "equivalent to", "∝": "proportional to",
    }
    
    for search, replace in replacements.items():
        text = text.replace(search, replace)

    # Remove non-latin1 characters that weren't caught to prevent PDF crashes
    # but try to keep text readable
    text = re.sub(r"\s+", " ", text).strip()
    return text.encode("ascii", "replace").decode("ascii").replace("?", " ")


def _build_summary_sections(summary):
    clean_summary = summary or ""
    raw_sections = re.split(r"\n\s*\n", clean_summary)
    sections = []

    for block in raw_sections:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        head = lines[0].rstrip(":")
        if len(lines) == 1 and ":" in lines[0]:
            key, value = lines[0].split(":", 1)
            sections.append((key.strip(), value.strip()))
        else:
            body = " ".join(lines[1:]) if len(lines) > 1 else lines[0]
            sections.append((head, body))

    if not sections:
        sections.append(("Detailed Summary", clean_summary))

    return sections


def generate_pdf_summary(
    filename,
    summary,
    topics,
    output_path="data/summary_report.pdf",
    glossary=None,
    equations=None,
    key_features=None,
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = IntelligencePDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    clean_topics = [sanitize_text(t) for t in topics[:12]]
    clean_glossary = {sanitize_text(k): sanitize_text(v) for k, v in (glossary or {}).items()}
    clean_equations = [sanitize_text(eq) for eq in (equations or [])[:8]]
    clean_features = [sanitize_text(item) for item in (key_features or [])[:6]]
    sections = _build_summary_sections(summary)

    pdf.add_page()
    pdf.set_fill_color(255, 247, 237)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_fill_color(255, 220, 163)
    pdf.ellipse(132, -10, 85, 85, style="F")
    pdf.set_fill_color(255, 199, 120)
    pdf.ellipse(-18, 222, 95, 95, style="F")
    pdf.set_fill_color(255, 236, 214)
    pdf.rect(0, 262, 210, 35, style="F")

    hero_path = "frontend/assets/hero.png"
    concept_path = "frontend/assets/concept.png"
    if os.path.exists(hero_path):
        pdf.image(hero_path, x=10, y=20, w=190)
    if os.path.exists(concept_path):
        pdf.image(concept_path, x=145, y=201, w=48)

    pdf.set_y(150)
    # Glassmorphism/Overlay effect for readability
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(10, 148, 190, 75, style="F")
    pdf.set_draw_color(255, 199, 120)
    pdf.line(15, 148, 195, 148) # Stylish top border
    
    pdf.set_font("helvetica", "B", 26)
    pdf.set_text_color(20, 20, 20) # High contrast charcoal
    pdf.cell(0, 15, "Learning Intelligence Report", 0, 1, "C")

    pdf.set_font("helvetica", "I", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(
        0,
        8,
        sanitize_text(
            "A comprehensive cognitive analysis of major concepts, key features, and mathematical foundations."
        ),
        align="C",
    )

    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(173, 77, 31) # Vibrant accent for labels
    pdf.cell(0, 8, "KNOWLEDGE BASE TAG", 0, 1, "C")
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(10, 10, 10)
    pdf.cell(0, 10, sanitize_text(filename or "Aggregated Material"), 0, 1, "C")

    pdf.add_page()
    pdf.set_fill_color(255, 250, 244)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_fill_color(255, 231, 199)
    pdf.rect(0, 0, 210, 22, style="F")
    pdf.section_title("Main Features")
    if clean_features:
        for index, feature in enumerate(clean_features, start=1):
            fill_color = (255, 250, 244) if index % 2 else (255, 244, 232)
            pdf.feature_card(f"Feature {index}", feature, fill_color)
    else:
        pdf.paragraph("Key features will appear here after concept extraction.")

    pdf.section_title("Core Topics")
    if clean_topics:
        pdf.bullet_list(clean_topics)
    else:
        pdf.paragraph("No core topics detected.")

    pdf.add_page()
    pdf.set_fill_color(246, 250, 255)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_fill_color(209, 234, 255)
    pdf.rect(0, 0, 210, 22, style="F")
    pdf.section_title("Detailed Summary")
    for title, body in sections:
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(14, 65, 103)
        pdf.cell(0, 8, sanitize_text(title), 0, 1)
        pdf.paragraph(body)

    if clean_glossary:
        pdf.add_page()
        pdf.set_fill_color(245, 252, 248)
        pdf.rect(0, 0, 210, 297, style="F")
        pdf.set_fill_color(203, 238, 220)
        pdf.rect(0, 0, 210, 22, style="F")
        pdf.section_title("Concept Glossary")
        for topic, definition in clean_glossary.items():
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(24, 83, 62)
            pdf.cell(0, 7, topic.upper(), 0, 1)
            pdf.paragraph(definition, size=10)

    if clean_equations:
        pdf.add_page()
        pdf.set_fill_color(245, 245, 255)
        pdf.rect(0, 0, 210, 297, style="F")
        pdf.set_fill_color(218, 218, 255)
        pdf.rect(0, 0, 210, 22, style="F")
        pdf.section_title("Mathematical Equations")
        pdf.paragraph(
            "Important mathematical expressions detected from the source document are listed below in a PDF-safe format."
        )
        pdf.bullet_list(clean_equations)

    pdf.output(output_path)
    return output_path
