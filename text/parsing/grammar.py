"""
Module: text.grammar
Description: Defines the rules for parsing English text.

BNF Grammar for English (WIP)
=============================
<document> ::= <paragraph>+
<paragraph> ::= <sentence>+
<sentence> ::= <clause> <terminator> | <quote> | <single-quote>
<quote> ::= '"' <sentence>+ '"'
<single-quote> ::= "'" <sentence>+ "'"
<clause> ::= <expression> (',' <expression>)*
<expression> ::= <phrase> | <expression> <conjunction> <expression>
<phrase> ::= <word> | <number> | <possession> | <contraction> | <prepositional-phrase> | <phrase> <punctuation> <phrase>
<possession> ::= <word> "'s" | <word> "s'" | <word> "'" <sentence> "'"
<contraction> ::= <contracted-form> | "'" <word>
<number> ::= <digit>+ | <digit>+ '.' <digit>*
<word> ::= [a-zA-Z]+
<punctuation> ::= ',' | ';' | ':' | '-' | '(' <expression> ')' | '[' <expression> ']' | '{' <expression> '}'
<conjunction> ::= 'and' | 'or' | 'but' | 'because'
<preposition> ::= 'in' | 'on' | 'at' | 'between' | 'with' | 'under' | 'over' | 'into' | 'through'
<terminator> ::= '.' | '?' | '!'
<contracted-form> ::= <word> "'" <contraction-suffix>
<contraction-suffix> ::= 'm' | 're' | 've' | 'll' | 'd' | 's' | 't'
<digit> ::= '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
"""

import string
import unicodedata

import regex as re


class TextPattern:
    # Enable reusable expressions
    PARAGRAPH = r"\n{2,}"
    SENTENCE = r"(?<!\b(?:Dr|Mr|Ms|etc|vs|p|a)\.)([.!?])(\s+|$)"
    WORD = rf"\w+(?:'\w+)?|\d+(?:\.\d+)?|[{re.escape(string.punctuation)}]+"

    QUOTE = r"(['\"])(?:(?=(\\?))\2.)*?\1"
    APOSTROPHE = r"^(?!')[A-Za-z]+(?:'[A-Za-z]+)+$"
    ABBREVIATION = r"\b(?:Dr|Mr|Ms|Mrs|St|etc|e\.g|i\.e|vs|p\.m|a\.m)\.\b"

    PARENTHESIS = r"\(([^)]+)\)|\[[^\]]+\]"

    NUMBER = r"(?<!\w)(?:\d{1,3}(?:,\d{3})*|\d+\.\d+|\$\d+)(?!\w)"
    ROMAN = r"(?i)\b[IVXLCDM]+\b"
    PAGE = r"^\s*\S+\s+(\d+|[ivxlcdm]+)\s*$"

    # Enable compiling reusable expressions
    def __call__(self, attr: str) -> re.Pattern:
        try:
            return re.compile(getattr(self, attr.upper()))
        except AttributeError:
            print(f"TextPattern has no attribute named {attr}.")

    def is_toc(self, paragraph: str) -> bool:
        """Heuristic: Determines if a paragraph is likely a Table of Contents entry."""
        keywords = {"contents", "table of contents", "page", "act", "scene", "prologue", "chapter"}
        words = paragraph.split()

        # Too short or all uppercase
        if len(words) < 5 and paragraph.isupper():
            return True

        # Contains key ToC words
        if any(word.lower() in keywords for word in words):
            return True

        # Matches "CHAPTER X." format
        if re.match(r"^\s*CHAPTER\s+[IVXLCDM\d]+\.?$", paragraph, re.IGNORECASE):
            return True

        # Matches "Page 10" or similar
        if self("page").match(paragraph):
            return True

        return False


class TextUnicode:
    @staticmethod
    def normalize_newlines(text: str) -> str:
        """Normalize newlines while preserving paragraph breaks."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
        return text.lstrip("\ufeff")  # Remove BOM if present

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Apply Unicode normalization and replace fancy punctuation with ASCII."""
        quotes = {"‘": "'", "’": "'", "“": '"', "”": '"'}
        text = unicodedata.normalize("NFKC", text)
        for old, new in quotes.items():
            text = text.replace(old, new)
        return text

    @classmethod
    def read_and_normalize(cls, file: str) -> str:
        # === Read and Parse the File ===
        with open(file, "r", encoding="utf-8") as file:
            text = file.read().strip()
        text = cls.normalize_unicode(text)
        text = cls.normalize_newlines(text)
        return text


# Example usage in main script
if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--file", default="data/owl.md", help="The plain text corpus to be parsed.")
    args = parser.parse_args()

    pattern = TextPattern()

    def get_paragraphs(text: str) -> list[str]:
        """Splits text into paragraphs based on double newlines."""
        return [p.strip() for p in pattern("paragraph").split(text) if p.strip()]

    text = TextUnicode.read_and_normalize(args.file)
    paragraphs = get_paragraphs(text)

    # Debug Output
    for i, paragraph in enumerate(paragraphs[:10]):
        print(f"Sentence {i+1}: {repr(paragraph)}")
