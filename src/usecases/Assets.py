import hashlib
import logging
from pathlib import Path
from urllib.parse import urlparse

from ports.os import IFileSystem


class Assets:
    def __init__(self, fs: IFileSystem):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__fs = fs
        self.__base_dir = "assets"

    def write_image(self, path: str, dir: str, content: bytes) -> str:
        if not path or not content:
            return ""

        self.__logger.info(f"Writing image asset for path: {path} in dir: {dir}")
        digest = hashlib.sha256(path.encode("utf-8")).hexdigest()
        extension = Path(urlparse(path).path).suffix.lower() or ".bin"

        asset_path = f"{self.__base_dir}/{dir}/{digest}{extension}"
        self.__fs.write_bytes(asset_path, content)

        return asset_path
