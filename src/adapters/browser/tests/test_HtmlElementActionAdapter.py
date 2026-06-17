import asyncio
from typing import cast

from playwright.async_api import Page

from adapters.browser.HtmlElementActionAdapter import HtmlElementActionAdapter


class FakeElement:
    def __init__(self, tag="input", type_attr="text", role=None, value=""):
        self.tag = tag
        self.type_attr = type_attr
        self.role = role
        self.value = value
        self.clicked = False
        self.checked = False
        self.wait_calls = []

    async def evaluate(self, expression: str):
        if "tagName" in expression:
            return self.tag
        if "type" in expression:
            return self.type_attr
        if "role" in expression:
            return self.role
        return None

    async def fill(self, value: str):
        self.value = value

    async def input_value(self):
        return self.value

    async def click(self):
        self.clicked = True

    async def check(self):
        self.checked = True

    async def uncheck(self):
        self.checked = False

    async def select_option(self, value: str):
        self.value = value

    async def wait_for(self, *, state, timeout):
        self.wait_calls.append((state, timeout))


class FakeLocator:
    def __init__(self, elements: list[FakeElement]):
        self.elements = elements
        self.first = elements[0]

    async def all(self):
        return self.elements

    async def check(self):
        await self.first.check()


class FakePage:
    def __init__(self, element: FakeElement):
        self.element = element
        self.url = "https://example.test"

    def locator(self, css: str, **kwargs):
        return FakeLocator([self.element])

    def get_by_role(self, role: str, name: str):
        return self.element

    async def content(self):
        return "<html></html>"

    async def title(self):
        return "Titre"


def test_query_selector_returns_first_locator_element():
    element = FakeElement()
    action = HtmlElementActionAdapter(cast(Page, FakePage(element)))

    assert asyncio.run(action.querySelector("input")) is element


def test_wait_for_delegates_state_and_timeout_to_element():
    element = FakeElement()
    action = HtmlElementActionAdapter(cast(Page, FakePage(element)))

    assert asyncio.run(action.wait_for("input", timeout=1.5, state="visible")) is True
    assert element.wait_calls == [("visible", 1500)]


def test_set_value_handles_text_checkbox_select_and_click():
    text = FakeElement()
    assert (
        asyncio.run(
            HtmlElementActionAdapter(cast(Page, FakePage(text))).set_value(
                "input", "Kai"
            )
        )
        == "Kai"
    )

    checkbox = FakeElement(type_attr="checkbox")
    assert (
        asyncio.run(
            HtmlElementActionAdapter(cast(Page, FakePage(checkbox))).set_value(
                "input", True
            )
        )
        == ""
    )
    assert checkbox.checked is True

    select = FakeElement(tag="select")
    assert (
        asyncio.run(
            HtmlElementActionAdapter(cast(Page, FakePage(select))).set_value(
                "select", "fr"
            )
        )
        == "fr"
    )

    assert (
        asyncio.run(HtmlElementActionAdapter(cast(Page, FakePage(text))).click("button"))
        is True
    )
    assert text.clicked is True
