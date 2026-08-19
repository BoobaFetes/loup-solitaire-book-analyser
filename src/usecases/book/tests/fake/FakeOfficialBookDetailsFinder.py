from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeOfficialBookDetailsFinder(SpyStubFake):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.html = html

    def stub_authors(self, returned: list[str]) -> None:
        self._stub("authors", returned)

    def stub_authors_exception(self, exception: BaseException) -> None:
        self._stub_exception("authors", exception)

    @property
    def spy_authors(self) -> list[SpyCall]:
        return self._spy("authors")

    def stub_numero(self, returned: int) -> None:
        self._stub("numero", returned)

    @property
    def spy_numero(self) -> list[SpyCall]:
        return self._spy("numero")

    def stub_isbn(self, returned: str) -> None:
        self._stub("isbn", returned)

    @property
    def spy_isbn(self) -> list[SpyCall]:
        return self._spy("isbn")

    def stub_image(self, returned: tuple[str, bytes]) -> None:
        self._stub("image", returned)

    @property
    def spy_image(self) -> list[SpyCall]:
        return self._spy("image")

    def stub_title(self, returned: str) -> None:
        self._stub("title", returned)

    @property
    def spy_title(self) -> list[SpyCall]:
        return self._spy("title")

    def stub_lastParutionDate(self, returned: str) -> None:
        self._stub("lastParutionDate", returned)

    @property
    def spy_lastParutionDate(self) -> list[SpyCall]:
        return self._spy("lastParutionDate")

    def stub_description(self, returned: str) -> None:
        self._stub("description", returned)

    @property
    def spy_description(self) -> list[SpyCall]:
        return self._spy("description")

    def authors(self) -> list[str]:
        self._raise_if_stubbed_exception("authors")
        default = [] if "no-joe" in self.html else ["Joe Dever"]
        returned = self._returned_or_default("authors", default)
        return self._record_call("authors", (), {}, returned)

    def numero(self) -> int:
        returned = self._returned_or_default(
            "numero", -1 if "negative" in self.html else 4
        )
        return self._record_call("numero", (), {}, returned)

    def isbn(self, default: str = "") -> str:
        returned = self._returned_or_default("isbn", "isbn-officiel")
        return self._record_call("isbn", (), {"default": default}, returned)

    async def image(self, client) -> tuple[str, bytes]:
        returned = self._returned_or_default(
            "image", ("https://img.test/cover.jpg", b"img")
        )
        return self._record_call("image", (client,), {}, returned)

    def title(self, default: str = "") -> str:
        returned = self._returned_or_default("title", "Titre officiel")
        return self._record_call("title", (), {"default": default}, returned)

    def lastParutionDate(self, default: str = "") -> str:
        returned = self._returned_or_default("lastParutionDate", default)
        return self._record_call("lastParutionDate", (), {"default": default}, returned)

    def description(self, default: str = "") -> str:
        returned = self._returned_or_default("description", "Description")
        return self._record_call("description", (), {"default": default}, returned)
