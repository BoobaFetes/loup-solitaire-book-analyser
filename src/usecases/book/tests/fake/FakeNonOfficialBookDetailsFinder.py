from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeNonOfficialBookDetailsFinder(SpyStubFake):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.html = html

    def stub_is_classic_version(self, returned: bool) -> None:
        self._stub("is_classic_version", returned)

    @property
    def spy_is_classic_version(self) -> list[SpyCall]:
        return self._spy("is_classic_version")

    def stub_numero(self, returned: int) -> None:
        self._stub("numero", returned)

    def stub_numero_exception(self, exception: BaseException) -> None:
        self._stub_exception("numero", exception)

    @property
    def spy_numero(self) -> list[SpyCall]:
        return self._spy("numero")

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

    def stub_authors(self, returned: list[str]) -> None:
        self._stub("authors", returned)

    @property
    def spy_authors(self) -> list[SpyCall]:
        return self._spy("authors")

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

    def stub_isbn(self, returned: str) -> None:
        self._stub("isbn", returned)

    @property
    def spy_isbn(self) -> list[SpyCall]:
        return self._spy("isbn")

    def is_classic_version(self) -> bool:
        returned = self._returned_or_default("is_classic_version", False)
        return self._record_call("is_classic_version", (), {}, returned)

    def numero(self) -> int:
        self._raise_if_stubbed_exception("numero")
        returned = self._returned_or_default(
            "numero", -1 if "negative" in self.html else 7
        )
        return self._record_call("numero", (), {}, returned)

    async def image(self, client, base_url: str = "") -> tuple[str, bytes]:
        default = (
            ("", b"") if "no-image" in self.html else (f"{base_url}cover.jpg", b"img")
        )
        returned = self._returned_or_default("image", default)
        return self._record_call("image", (client,), {"base_url": base_url}, returned)

    def title(self, default: str = "") -> str:
        returned = self._returned_or_default("title", "Titre non officiel")
        return self._record_call("title", (), {"default": default}, returned)

    def authors(self) -> list[str]:
        returned = self._returned_or_default("authors", ["Joe Dever"])
        return self._record_call("authors", (), {}, returned)

    def lastParutionDate(self, default: str = "") -> str:
        returned = self._returned_or_default("lastParutionDate", default)
        return self._record_call("lastParutionDate", (), {"default": default}, returned)

    def description(self, default: str = "") -> str:
        returned = self._returned_or_default("description", "Description")
        return self._record_call("description", (), {"default": default}, returned)

    def isbn(self, default: str = "") -> str:
        returned = self._returned_or_default("isbn", "isbn-non-officiel")
        return self._record_call("isbn", (), {"default": default}, returned)
