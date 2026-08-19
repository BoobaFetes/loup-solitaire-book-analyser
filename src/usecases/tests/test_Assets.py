import hashlib

from adapters.os.tests.fake import FakeFileSystem
from usecases import Assets


def test_write_image_writes_content_to_hashed_asset_path_with_lowercase_extension():

    # Arrange
    fs = FakeFileSystem()
    assets = Assets(fs)
    source_path = "https://images.test/covers/Book.JPG?width=300"
    content = b"image-content"

    # Act
    asset_path = assets.write_image(source_path, "covers", content)

    # Assert
    digest = hashlib.sha256(source_path.encode("utf-8")).hexdigest()
    assert asset_path == f"assets/covers/{digest}.jpg"
    assert fs.files[asset_path] == content


def test_write_image_uses_bin_extension_when_source_path_has_no_extension():

    # Arrange
    fs = FakeFileSystem()
    assets = Assets(fs)
    source_path = "https://images.test/covers/book"

    # Act
    asset_path = assets.write_image(source_path, "covers", b"raw")

    # Assert
    digest = hashlib.sha256(source_path.encode("utf-8")).hexdigest()
    assert asset_path == f"assets/covers/{digest}.bin"
    assert fs.files[asset_path] == b"raw"


def test_write_image_returns_empty_path_without_writing_when_source_or_content_is_missing():

    # Arrange
    fs = FakeFileSystem()
    assets = Assets(fs)

    # Act
    actual = assets.write_image("", "covers", b"raw")

    # Assert
    expected = ""
    assert actual == expected
    actual = assets.write_image("https://images.test/book.jpg", "covers", b"")

    expected = ""
    assert actual == expected
    assert fs.files == {}
