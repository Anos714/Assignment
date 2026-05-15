from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from docx import Document as DocxDocument
import httpx
from pypdf import PdfReader

from app.core.settings import settings
from app.rag.chunking import SourcePage


class ExtractionError(RuntimeError):
    pass


def resolve_storage_path(storage_root: Path, storage_key: str) -> Path:
    root = storage_root.resolve()
    path = (root / storage_key).resolve()
    if root not in path.parents and path != root:
        raise ExtractionError("Invalid storage key")
    return path


def download_remote_file(file_url: str, *, filename: str | None = None) -> Path:
    parsed_url = urlparse(file_url)
    if parsed_url.scheme not in {"http", "https"}:
        raise ExtractionError("Remote file URL must use http or https")

    temp_dir = Path("/tmp/documindai_ingest")
    temp_dir.mkdir(parents=True, exist_ok=True)
    suffix = _safe_suffix(filename) or _safe_suffix(Path(parsed_url.path).name)
    try:
        with httpx.stream("GET", file_url, follow_redirects=True, timeout=60) as response:
            if response.status_code != 200:
                raise ExtractionError(f"Could not download document: HTTP {response.status_code}")
            total = 0
            with NamedTemporaryFile(delete=False, dir=temp_dir, suffix=suffix) as temp_file:
                temp_path = Path(temp_file.name)
                for chunk in response.iter_bytes():
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > settings.max_document_upload_bytes:
                        raise ExtractionError("Downloaded file exceeds the maximum upload size")
                    temp_file.write(chunk)
    except ExtractionError:
        if "temp_path" in locals():
            temp_path.unlink(missing_ok=True)
        raise
    except httpx.HTTPError as exc:
        if "temp_path" in locals():
            temp_path.unlink(missing_ok=True)
        raise ExtractionError(f"Could not download document: {exc}") from exc
    return temp_path


def _safe_suffix(filename: str | None) -> str:
    if not filename:
        return ""
    suffix = Path(filename).suffix.lower()
    return suffix if suffix in {".pdf", ".docx", ".txt"} else ""


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
