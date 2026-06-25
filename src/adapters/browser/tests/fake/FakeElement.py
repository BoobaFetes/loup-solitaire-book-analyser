from typing import Literal


class FakeElement:
    def __init__(
        self,
        tag: str = "input",
        type_attr: str = "text",
        role: str | None = None,
        value: str = "",
    ) -> None:
        self.tag = tag
        self.type_attr = type_attr
        self.role = role
        self.value = value
        self.clicked = False
        self.checked = False
        self.wait_calls: list[
            tuple[Literal["attached", "detached", "hidden", "visible"] | None, int]
        ] = []

    async def evaluate(self, expression: str) -> str | None:
        if "tagName" in expression:
            return self.tag
        if "type" in expression:
            return self.type_attr
        if "role" in expression:
            return self.role
        return None

    async def fill(self, value: str) -> None:
        self.value = value

    async def input_value(self) -> str:
        return self.value

    async def click(self) -> None:
        self.clicked = True

    async def check(self) -> None:
        self.checked = True

    async def uncheck(self) -> None:
        self.checked = False

    async def select_option(self, value: str) -> None:
        self.value = value

    async def wait_for(
        self,
        *,
        state: Literal["attached", "detached", "hidden", "visible"] | None,
        timeout: int,
    ) -> None:
        self.wait_calls.append((state, timeout))


class FakeLocator:
    def __init__(self, elements: list[FakeElement]) -> None:
        self.elements = elements
        self.first = elements[0]

    async def all(self) -> list[FakeElement]:
        return self.elements

    async def check(self) -> None:
        await self.first.check()
