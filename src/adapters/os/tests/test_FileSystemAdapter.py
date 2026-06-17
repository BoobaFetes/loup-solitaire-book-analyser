from adapters.os.FileSystemAdapter import FileSystemAdapter


def test_write_read_list_exists_and_clear_files(tmp_path):
    fs = FileSystemAdapter(str(tmp_path))

    fs.write_file("one.html", "<p>one</p>")
    fs.write_file("two.txt", "two")

    assert fs.is_file_exists("one.html") is True
    assert fs.read_file("one.html") == "<p>one</p>"
    assert fs.list() == ["one.html"]

    fs.clear("*.html")

    assert fs.is_file_exists("one.html") is False
    assert fs.is_file_exists("two.txt") is True


def test_write_file_rejects_path_without_suffix(tmp_path):
    fs = FileSystemAdapter(str(tmp_path))

    try:
        fs.write_file("directory", "content")
    except ValueError as error:
        assert "Invalid file path" in str(error)
    else:
        raise AssertionError("ValueError was not raised")


def test_clear_rejects_empty_pattern(tmp_path):
    fs = FileSystemAdapter(str(tmp_path))

    try:
        fs.clear("")
    except ValueError as error:
        assert "Pattern cannot be empty" in str(error)
    else:
        raise AssertionError("ValueError was not raised")
