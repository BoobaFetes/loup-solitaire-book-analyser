import logging

from ports.os import IFileSystem


class UnitTestCapture:
    @staticmethod
    def setup(enabled: bool, fs: IFileSystem):
        UnitTestCapture.__logging = logging.getLogger(UnitTestCapture.__name__)
        UnitTestCapture.enabled = enabled
        UnitTestCapture.fs = fs
        UnitTestCapture.__logging.warning(
            f"UnitTestCapture: enabled={enabled}, fs={'defined' if fs else 'undefined'}"
        )

    @staticmethod
    def capture(path: str, content: str):
        if UnitTestCapture.enabled:
            UnitTestCapture.__logging.warning(
                f"UnitTestCapture: capturing content to {path}"
            )
            UnitTestCapture.fs.write_file(path, content)
