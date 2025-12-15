# 文檔上傳
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_text_from_word(uploaded_file) -> str:
    doc = Document(uploaded_file)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def build_user_input(text_input: str, uploaded_file) -> str:
    """
    統一使用者輸入：
    - 純文字
    - 或 文字 + Word / PDF
    """

    if uploaded_file is None:
        return text_input.strip()

    file_text = ""

    if uploaded_file.type == "application/pdf":
        file_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        file_text = extract_text_from_word(uploaded_file)
    else:
        raise ValueError("不支援的檔案格式")

    return f"""
【題目／參考資料（學生上傳）】
{file_text}

【學生的提問／說明】
{text_input.strip()}
""".strip()