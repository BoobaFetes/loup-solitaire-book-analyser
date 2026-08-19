from adapters.os.FileSystemAdapter import FileSystemAdapter


def test_write_read_list_exists_and_clear_files(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))

    fs.write_file("one.html", "<p>one</p>")
    fs.write_file("two.txt", "two")

    # Act
    actual = fs.is_file_exists("one.html")

    # Assert
    expected = True
    assert actual is expected
    actual = fs.read_file("one.html")

    expected = "<p>one</p>"
    assert actual == expected
    assert [path.name for path in fs.list_files(".", "*.html")] == ["one.html"]

    fs.clear(".", "*.html")

    actual = fs.is_file_exists("one.html")

    expected = False
    assert actual is expected
    actual = fs.is_file_exists("two.txt")

    expected = True
    assert actual is expected


def test_write_file_rejects_path_without_suffix(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))

    # Act
    try:
        fs.write_file("directory", "content")
    except ValueError as error:
        # Assert
        assert "Invalid file path" in str(error)
    else:
        raise AssertionError("ValueError was not raised")


def test_clear_rejects_empty_pattern(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))

    # Act
    try:
        fs.clear(".", "")
    except ValueError as error:
        # Assert
        assert "Pattern cannot be empty" in str(error)
    else:
        raise AssertionError("ValueError was not raised")


def test_create_get_path_read_and_write_bytes(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))

    fs.create("nested")
    fs.write_bytes("nested/image.bin", b"content")

    # Act
    actual = fs.is_dir_exists("nested")

    # Assert
    expected = True
    assert actual is expected
    assert fs.get_path("nested").is_absolute()
    actual = fs.is_file_exists("nested/image.bin")

    expected = True
    assert actual is expected
    actual = fs.read_bytes("nested/image.bin")

    expected = b"content"
    assert actual == expected
    assert [path.name for path in fs.list_files("nested", "*.bin")] == ["image.bin"]


def test_read_file_and_read_bytes_raise_for_missing_files(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))

    # Act
    try:
        fs.read_file("missing.txt")
    except FileNotFoundError:
        # Assert
        pass
    else:
        raise AssertionError("FileNotFoundError was not raised")

    # Act
    try:
        fs.read_bytes("missing.bin")
    except FileNotFoundError:
        # Assert
        pass
    else:
        raise AssertionError("FileNotFoundError was not raised")


def test_write_bytes_rejects_path_without_suffix(tmp_path):

    # Arrange
    fs = FileSystemAdapter(str(tmp_path))

    # Act
    try:
        fs.write_bytes("directory", b"content")
    except ValueError as error:
        # Assert
        assert "Invalid file path" in str(error)
    else:
        raise AssertionError("ValueError was not raised")
