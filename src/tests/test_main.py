from pathlib import Path

import main

TEST_FILE_CONTENT = "test d'écriture dans le volume monté"
LOG_FILE_CONTENT = f"{TEST_FILE_CONTENT}: logs/test.log"
CAPTURES_FILE_CONTENT = f"{TEST_FILE_CONTENT}: captures/captures.png"

# ⚠️ Pour prouver que le CI s'arrête sur un échec, décommentez le test ci-dessous :
# def test_ci_pipeline_should_fail_intentionally():
#     assert False, "Test volontairement en échec pour vérifier que la CI bloque"


def test_main_writes_expected_files_and_prints_status(monkeypatch, tmp_path, capsys):
    (tmp_path / "logs").mkdir()
    (tmp_path / "captures").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "write_data_with_batch_user", lambda shouldClean: None)
    monkeypatch.setattr(main, "read_books_with_webapp_user", lambda: None)

    written_files = {}

    def fake_unlink(path):
        written_files[path] = path.read_text()

    monkeypatch.setattr(Path, "unlink", fake_unlink)

    main.main()

    assert written_files == {
        tmp_path / "logs" / "test.log": LOG_FILE_CONTENT,
        tmp_path / "captures" / "captures.png": CAPTURES_FILE_CONTENT,
    }
    assert capsys.readouterr().out.splitlines() == [
        "'le pod est lancé !'",
        '"tentative d\'ecriture dans les volumes montés..."',
        "'écriture terminée !'",
        "'suppression des fichiers de test...'",
        "'fichiers de test supprimés !'",
        "'le pod se termine !'",
    ]


def test_main_removes_created_test_files_after_volume_check(monkeypatch, tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "captures").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main, "write_data_with_batch_user", lambda shouldClean: None)
    monkeypatch.setattr(main, "read_books_with_webapp_user", lambda: None)

    main.main()

    assert not (tmp_path / "logs" / "test.log").exists()
    assert not (tmp_path / "captures" / "captures.png").exists()
