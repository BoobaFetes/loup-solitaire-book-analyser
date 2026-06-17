from pathlib import Path

import main

TEST_FILE_CONTENT = "test d'écriture dans le volume monté"

# ⚠️ Pour prouver que le CI s'arrête sur un échec, décommentez le test ci-dessous :
# def test_ci_pipeline_should_fail_intentionally():
#     assert False, "Test volontairement en échec pour vérifier que la CI bloque"


def test_main_writes_expected_files_and_prints_status(monkeypatch, tmp_path, capsys):
    (tmp_path / "logs").mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.chdir(tmp_path)

    written_files = {}

    def fake_unlink(path):
        written_files[path] = path.read_text()

    monkeypatch.setattr(Path, "unlink", fake_unlink)

    main.main()

    assert written_files == {
        tmp_path / "logs" / "test.log": TEST_FILE_CONTENT,
        tmp_path / "data" / "test.json": TEST_FILE_CONTENT,
    }
    assert capsys.readouterr().out.splitlines() == [
        "le pod est lancé !",
        "tentative d'ecriture dans les volumes montés...",
        "écriture terminée !",
        "écriture terminée !",
        "suppression des fichiers de test...",
        "fichiers de test supprimés !",
        "le pod se termine !",
    ]


def test_main_removes_created_test_files_after_volume_check(monkeypatch, tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.chdir(tmp_path)

    main.main()

    assert not (tmp_path / "logs" / "test.log").exists()
    assert not (tmp_path / "data" / "test.json").exists()
