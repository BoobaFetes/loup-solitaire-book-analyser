"""
Demo test — prouve que :
- pytest s'arrête (exit code ≠ 0) si un test échoue  → le CI bloque
- on peut lancer via CLI : `pytest ` (avec un environnement virtuel activé)
- on peut lancer via VS Code : extension Python Tests (pytest)
"""

import pytest


@pytest.fixture
def sample_message():
    return "hello world"


def test_hello_world(sample_message):
    assert sample_message == "hello world"


def test_addition():
    assert 1 + 1 == 2


# Pour prouver que le CI s'arrête sur un échec,
# décommentez le test ci-dessous :
# def test_should_fail():
#     assert 1 == 2, "Ce test est volontairement cassé"
