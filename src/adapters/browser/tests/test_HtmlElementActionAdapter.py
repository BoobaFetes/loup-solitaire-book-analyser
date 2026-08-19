import asyncio
from typing import cast

from playwright.async_api import Page

from adapters.browser.HtmlElementActionAdapter import HtmlElementActionAdapter
from adapters.browser.tests.fake import (
    FakeBrowserPage,
    FakeElement,
)


def test_query_selector_returns_first_locator_element():

    # Arrange
    element = FakeElement()
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    # Act
    actual = asyncio.run(action.querySelector("input"))

    # Assert
    expected = element
    assert actual is expected


def test_wait_for_delegates_state_and_timeout_to_element():

    # Arrange
    element = FakeElement()
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    # Act
    actual = asyncio.run(action.wait_for("input", timeout=1.5, state="visible"))

    # Assert
    expected = True
    assert actual is expected
    assert element.wait_calls == [("visible", 1500)]


def test_set_value_handles_text_checkbox_select_and_click():

    # Arrange
    text = FakeElement()
    text_action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(text)))
    checkbox = FakeElement(type_attr="checkbox")
    checkbox_action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(checkbox)))
    select = FakeElement(tag="select")
    select_action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(select)))

    # Act
    text_result = asyncio.run(text_action.set_value("input", "Kai"))
    checkbox_result = asyncio.run(checkbox_action.set_value("input", True))
    select_result = asyncio.run(select_action.set_value("select", "fr"))
    click_result = asyncio.run(text_action.click("button"))

    # Assert
    assert text_result == "Kai"
    assert checkbox_result == ""
    assert checkbox.checked is True
    assert select_result == "fr"
    assert click_result is True
    assert text.clicked is True


def test_query_selector_all_returns_all_locator_elements():

    # Arrange
    element = FakeElement()
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    # Act
    actual = asyncio.run(action.querySelectorAll("input"))

    # Assert
    expected = [element]
    assert actual == expected


def test_get_value_returns_input_value():

    # Arrange
    element = FakeElement(value="current")
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    # Act
    actual = asyncio.run(action.get_value("input"))

    # Assert
    expected = "current"
    assert actual == expected


def test_set_value_handles_radio_aria_combobox_and_fallback():

    # Arrange
    radio = FakeElement(type_attr="radio")
    radio_action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(radio)))
    combobox = FakeElement(tag="div", type_attr=None, role="combobox")
    combobox_action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(combobox)))
    fallback = FakeElement(tag="custom", type_attr=None)
    fallback_action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(fallback)))

    # Act
    radio_result = asyncio.run(radio_action.set_value("input", "yes"))
    combobox_result = asyncio.run(combobox_action.set_value("div", "Option"))
    fallback_result = asyncio.run(fallback_action.set_value("custom", "fallback"))

    # Assert
    assert radio_result == ""
    assert radio.checked is True
    assert combobox_result == ""
    assert combobox.clicked is True
    assert fallback_result == "fallback"


def test_set_value_raises_runtime_error_when_fallback_fill_fails():

    # Arrange
    element = FakeElement(tag="custom", type_attr=None)
    element.stub_fill_exception(ValueError("cannot fill"))
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    # Act
    try:
        asyncio.run(action.set_value("custom", "value"))
    except RuntimeError as error:
        # Assert
        assert "Unable to set value" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_click_returns_false_when_element_click_fails():

    # Arrange
    element = FakeElement()
    element.stub_click_exception(ValueError("cannot click"))
    action = HtmlElementActionAdapter(cast(Page, FakeBrowserPage(element)))

    # Act
    actual = asyncio.run(action.click("button"))

    # Assert
    expected = False
    assert actual is expected
