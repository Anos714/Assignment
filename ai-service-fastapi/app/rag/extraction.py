from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.rag.chunking import SourcePage


class ExtractionError(RuntimeError):
    pass


def resolve_storage_path(storage_root: Path, storage_key: str) -> Path:
    root = storage_root.resolve()
    path = (root / storage_key).resolve()
    if root not in path.parents and path != root:
        raise ExtractionError("Invalid storage key")
    return path


def extract_pages(path: Path, file_type: str) -> list[SourcePage]:
    if not path.exists():
        raise ExtractionError(f"Document file not found: {path}")

    file_type = file_type.lower().removeprefix(".")
    if file_type == "txt":
        return [SourcePage(page_number=None, text=_read_text(path))]
    if file_type == "pdf":
        return _extract_pdf(path)
    if file_type == "docx":
        return _extract_docx(path)
    raise ExtractionError("Unsupported document type")


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def _extract_pdf(path: Path) -> list[SourcePage]:
    try:
        reader = PdfReader(str(path))
        return [
            SourcePage(page_number=index + 1, text=page.extract_text() or "")
            for index, page in enumerate(reader.pages)
        ]
    except Exception as exc:
        raise ExtractionError(f"Could not extract PDF text: {exc}") from exc


def _extract_docx(path: Path) -> list[SourcePage]:
    try:
        document = DocxDocument(str(path))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        return [SourcePage(page_number=None, text=text)]
    except Exception as exc:
        raise ExtractionError(f"Could not extract DOCX text: {exc}") from exc
