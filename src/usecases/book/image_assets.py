import hashlib
from pathlib import Path
from urllib.parse import urlparse

from ports.os import IFileSystem


def write_book_cover_asset(fs: IFileSystem, source_url: str, content: bytes) -> str:
    if not source_url or not content:
        return ""

    digest = hashlib.sha256(source_url.encode("utf-8")).hexdigest()
    extension = Path(urlparse(source_url).path).suffix.lower() or ".bin"
    asset_path = f"assets/book-covers/{digest}{extension}"
    fs.write_bytes(asset_path, content)
    return asset_path
