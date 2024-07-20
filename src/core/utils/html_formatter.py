class HTMLFormatter:
    @staticmethod
    def link(text: str, url: str) -> str:
        """Create a hyperlink."""
        return f'<a href="{url}">{text}</a>'

    @staticmethod
    def bold(text: str) -> str:
        """Create bold text."""
        return f'<b>{text}</b>'

    @staticmethod
    def italic(text: str) -> str:
        """Create italic text."""
        return f'<i>{text}</i>'

    @staticmethod
    def code(text: str) -> str:
        """Create code text."""
        return f'<code>{text}</code>'

    @staticmethod
    def paragraph(text: str) -> str:
        """Create a paragraph."""
        return f'<p>{text}</p>'

    @staticmethod
    def header(text: str, level: int = 1) -> str:
        """Create a header."""
        if not (1 <= level <= 6):
            raise ValueError("Header level must be between 1 and 6")

        return f'<h{level}>{text}</h{level}>'

    @staticmethod
    def unordered_list(items: list[str]) -> str:
        """Create an unordered list."""
        list_items = ''.join(f'<li>{item}</li>' for item in items)
        return f'<ul>{list_items}</ul>'

    @staticmethod
    def ordered_list(items: list[str]) -> str:
        """Create an ordered list."""
        list_items = ''.join(f'<li>{item}</li>' for item in items)
        return f'<ol>{list_items}</ol>'
