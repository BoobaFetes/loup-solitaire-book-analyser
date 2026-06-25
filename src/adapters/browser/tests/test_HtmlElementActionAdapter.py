import asyncio
from typing import cast

from playwright.async_api import Page

from adapters.browser.HtmlElementActionAdapter import HtmlElementActionAdapter
from adapters.browser.tests.fake import FakeBrowserPage, FakeElement


def test_query_selector_returns_first_locator_element():
    element = FakeElement()
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    assert asyncio.run(action.querySelector("input")) is element


def test_wait_for_delegates_state_and_timeout_to_element():
    element = FakeElement()
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    assert asyncio.run(action.wait_for("input", timeout=1.5, state="visible")) is True
    assert element.wait_calls == [("visible", 1500)]


def test_set_value_handles_text_checkbox_select_and_click():
    text = FakeElement()
    assert (
        asyncio.run(
            HtmlElementActionAdapter(cast(Page, FakeBrowserPage(text))).set_value(
                "input", "Kai"
            )
        )
        == "Kai"
    )

    checkbox = FakeElement(type_attr="checkbox")
    assert (
        asyncio.run(
            HtmlElementActionAdapter(
                cast(Page, FakeBrowserPage(checkbox))
            ).set_value(
                "input", True
            )
        )
        == ""
    )
    assert checkbox.checked is True

    select = FakeElement(tag="select")
    assert (
        asyncio.run(
            HtmlElementActionAdapter(cast(Page, FakeBrowserPage(select))).set_value(
                "select", "fr"
            )
        )
        == "fr"
    )

    assert asyncio.run(
        HtmlElementActionAdapter(cast(Page, FakeBrowserPage(text))).click("button")
    ) is True
    assert text.clicked is True
