import logging
import re
from datetime import date
from typing import cast

from bs4 import BeautifulSoup, Tag

from ports.http import HttpClientBase
from ports.usecase import BookDetailsFinderBase


class BiblioAventurierBookDetailsFinder(BookDetailsFinderBase):
    __isbn_matchers = [
        # should match ISBN 13: 978-2-07-064302-7
        re.compile(r"([\d]{3}-[\d]{1}-[\d]{2}-[\d]{6}-[\d]{1})"),
        # should match ISBN 10: 2-07-064302-7, 2-07-057492-X (X can be a digit or a letter, X is used as 10 in ISBN 10 see official documentation for more details)
        re.compile(r"([\d]{1}-[\d]{2}-[\d]{6}-[\dX]{1})"),
    ]

    @staticmethod
    def __find_first_isbn(text: str) -> str:
        for matcher in BiblioAventurierBookDetailsFinder.__isbn_matchers:
            regexp_match = matcher.search(text)
            if regexp_match:
                value = regexp_match.group(1)
                if value:
                    return value.replace("-", "")

        return ""

    __date_matcher = re.compile(
        r"((\d{0,2})[ \t]*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre) (\d{4}))"
    )
    __month_mapping = {
        "janvier": 1,
        "février": 2,
        "mars": 3,
        "avril": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "août": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "décembre": 12,
    }

    @staticmethod
    def __find_parution_date(text: str) -> date | None:
        # if no match return None
        regexp_match = BiblioAventurierBookDetailsFinder.__date_matcher.search(text)
        if regexp_match:
            # if match cut the date part from the text and convert it to iso format date string (YYYY-MM-DD), if day is missing default to 1, if month is missing default to January, if year is missing default to 1900
            # extract from matcher the day, month and year parts
            day_str = regexp_match.group(2)
            month_str = regexp_match.group(3)
            year_str = regexp_match.group(4)

            # convert month name to month number then other details
            day = int(day_str) if day_str else 1
            month = BiblioAventurierBookDetailsFinder.__month_mapping.get(
                month_str.lower(), 1
            )
            year = int(year_str) if year_str else 1900

            # some regex match can have invalid day number (e.g. 31/02/2022), in this case we default to 1 to avoid crashing the app, we want to keep the month and year information even if the day is invalid
            try:
                result = date(year, month, day)
            except Exception:
                # silent catch : if the day part is not a valid integer, default to 1
                result = date(year, month, 1)
                # if this instruction launch an exception, it means that the month or year part is invalid, in this case we raise the exception because we can't parse the date at all and we want to log this case to fix the regex or the month mapping if needed

            return result

        return None

    def __init__(self, html: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__soup = BeautifulSoup(html, "html.parser")

    def isbn(self, default: str) -> str:
        root = self.__soup.select_one(
            "table#AutoNumber2 tr:nth-child(2) > td:nth-child(2)"
        )
        if not root:
            self.__logger.error("No potential ISBN information found in the page.")
            return default

        # les details du livre sur ce site est sois directement dans le <td /> soit dans un 'p' (<td><p></td>)
        children = list([e for e in root.children if not isinstance(e, str)])
        if len(children) == 1 and cast(Tag, children[0]).name == "p":
            root = cast(Tag, children[0])

        isbn_list: list[str] = []
        texts = [
            e.get_text(strip=True) for e in root.children if not isinstance(e, str)
        ]
        valid_texts = [t for t in texts if t.count("-")]

        for text in valid_texts:
            value: str = BiblioAventurierBookDetailsFinder.__find_first_isbn(text)
            if value:
                isbn_list.append(value.replace("-", ""))

        return isbn_list[-1] if len(isbn_list) and isbn_list[-1] else default

    def numero(self) -> int:
        # arrange
        text_prefix = "loup solitaire n° "
        selector = "table#AutoNumber2 tr:nth-child(2) > td:nth-child(2) a"

        # action
        element = self.__soup.select_one(selector)
        if element:
            text = element.get_text(strip=True)
            if text.lower().startswith(text_prefix):
                numero = text[len(text_prefix) :]
                if numero.isdigit():
                    return int(numero)

        return self._get_invalid_numero()

    def title(self, default: str) -> str:
        element = self.__soup.select_one("table#AutoNumber1 p:nth-child(1)")
        if not element:
            self.__logger.error("No potential title information found in the page.")
            return default

        titre = element.get_text(strip=True)
        # retire les parenthèses et le texte "Voir..." qui suit, présent dans les titres du premier tome qui a 2 versions: "classique" et "augmentée"
        titre = re.sub(r"\(.*\)|Voir.*$", "", titre, flags=re.DOTALL)

        # gère \r\n\t et doubles espaces
        titre = re.sub(r"\s+", " ", titre).strip()

        return titre

    def authors(self) -> list[str]:
        # Note:
        # authors are mixed with other details (such like translators and original title) in the same html structure but fortunately there is a pattern we can use to extract authors
        root = self.__soup.select_one(
            "table#AutoNumber2 tr:nth-child(2) > td:nth-child(2) font:first-child"
        )

        # pattern : step 1 : keep only string, anchor tags and italic tags, italic tags are used for original title
        elements = (
            [
                e
                for e in root.children
                if (isinstance(e, str) and e.strip() and e.strip() != "\n")
                or (isinstance(e, Tag) and e.name in ["a", "i", "span"])
            ]
            if root
            else []
        )
        if not elements:
            self.__logger.error("No potential author information found in the page.")
            return []

        # pattern : step 2 : remove number of book wich is get from numero method (selector seem different but target the same element)
        elements = elements[1:]
        if not elements:
            return []

        # pattern : step 3 : parse anchor tags until we reach the original title marked by italic tags.
        def is_span_with_lang_en(element: Tag) -> bool:
            return (
                element.name == "span"
                and "en-" in cast(str, element.attrs.get("lang", "")).lower()
            )

        def is_italic(element: Tag) -> bool:
            return element.name == "i"

        results: list[str] = []
        for elt in elements:
            is_tag = isinstance(elt, Tag)
            if is_tag and (is_italic(elt) or is_span_with_lang_en(elt)):
                break
            # At this point, we should only target authors.
            str_value = elt.get_text(strip=True) if is_tag else str(elt).strip()
            value = " ".join(str_value.split())
            if len(value) > 2:
                results.append(value)

        return results

    def lastParutionDate(self, default: str) -> str:
        elements = [
            *list(
                self.__soup.select(
                    "table#AutoNumber2 tr:nth-child(2) > td:nth-child(2) font"
                )
            ),
            self.__soup.select_one(  # for book n°22
                "table#AutoNumber2 tr:nth-child(2) > td:nth-child(2) > span"
            ),
        ]
        if not elements:
            self.__logger.error("No potential publication date found in the page.")
            return default

        try:
            results: list[date] = []
            # book from 1 to 21 have the dates in the "td" but after the dates are in "td > font" as string
            items = [
                *elements,  # for book 1 to 20 and 29 and after
                *elements[0].children,  # for book 21 to 28
            ]
            for element in items:
                value = ""
                if isinstance(element, Tag):
                    value = element.get_text(strip=True)
                elif isinstance(element, str):
                    value = element.strip()

                value = value.replace("\r\n", "")
                if not value or value.lower().startswith("loup solitaire n°"):
                    continue  # we don't care about the book number or not valid text

                parution_date = BiblioAventurierBookDetailsFinder.__find_parution_date(
                    value
                )
                if parution_date:
                    results.append(parution_date)

            # Keep the most recent publication date when several dates are present.
            return max(results).isoformat() if results else default
        except Exception as e:
            self.__logger.warning(
                f"Failed to parse publication date - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )
        return default

    def description(self, default: str) -> str:
        element = self.__soup.select_one(
            "table#AutoNumber2 tr:nth-child(3) td p:nth-child(5)"
        )
        if not element:
            self.__logger.error(
                "No potential description information found in the page."
            )
            return default

        description = element.get_text(strip=True)  # type: ignore
        description = re.sub(r"\s+", " ", description).strip()
        return description

    def official(self) -> bool:
        return False

    async def image(self, client: HttpClientBase, **kwargs) -> str:
        # check parameters
        base_url = kwargs.get("base_url", "")
        if not base_url:
            raise ValueError(
                "'base_url' property of type 'str' must be provided in kwargs for image extraction."
            )
        elif not isinstance(base_url, str):
            raise ValueError("'base_url' is not of type 'str' for image extraction.")

        # action
        elements = self.__soup.select("table#AutoNumber1 a")
        if not elements:
            self.__logger.error("No potential image information found in the page.")
            return ""

        urls = [
            cast(str, element.attrs["href"]).replace("../..", base_url)
            for element in elements
            if element.name == "a" and "href" in element.attrs
        ]

        url = urls[-1].replace("../..", base_url) if len(urls) else ""
        if not url:
            return ""

        try:
            return await self._fetch_image(client, url)
        except Exception as e:
            self.__logger.warning(
                f"Failed to fetch or encode image from URL: {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )
            return ""

    def is_classic_version(self) -> bool:
        element = self.__soup.select_one("table#AutoNumber1 p:nth-child(1)")
        if not element:
            return False

        titre = element.get_text(strip=True)
        return "classique)" in titre.lower()
