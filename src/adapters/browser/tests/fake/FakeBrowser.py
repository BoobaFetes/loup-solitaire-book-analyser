from adapters.browser.tests.fake.FakeBrowserPage import FakeBrowserPage


class FakeBrowserContext:
    def __init__(self) -> None:
        self.pages: list[FakeBrowserPage] = []

    async def new_page(self) -> FakeBrowserPage:
        page = FakeBrowserPage()
        self.pages.append(page)
        return page


class FakeBrowser:
    def __init__(self) -> None:
        self.contexts = [FakeBrowserContext()]
        self.new_context_options: list[dict[str, object]] = []

    async def new_context(self, **kwargs) -> None:
        self.new_context_options.append(kwargs)
        self.contexts.append(FakeBrowserContext())
