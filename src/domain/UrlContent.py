class URLContent:
    def __init__(self, url: str, text: str = ""):
        self.url: str = url
        self.text: str = text

    def __repr__(self):
        """Represents the URLContent instance as a string.

        Returns:
            str: A string representation of the URLContent instance.
        """
        return f"URLContent(url='{self.url}', content='{self.text[:30]}...')"

    # endregion
