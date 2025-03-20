"""
Script: tests.paragraph
Description: A simple grammar for detecting paragraphs.
"""

import unicodedata

import pyparsing as pp
import regex as re

# === Unicode Normalization Helpers ===
UNICODE_QUOTES = {"‘": "'", "’": "'", "“": '"', "”": '"'}


def normalize_newlines(text: str) -> str:
    """Normalize newlines while preserving paragraph breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # Normalize CRLF → LF
    text = re.sub(
        r"(?<!\n)\n(?!\n)", " ", text
    )  # Replace single newlines with spaces (handle line wrapping)
    return text.lstrip("\ufeff")  # Remove BOM if present


def normalize_unicode(text: str) -> str:
    """Apply Unicode normalization and replace fancy punctuation with ASCII."""
    text = unicodedata.normalize("NFKC", text)
    for old, new in UNICODE_QUOTES.items():
        text = text.replace(old, new)
    return text


# === Define Paragraph Grammar ===
paragraph_separator = pp.Regex(
    r"\n{2,}"
).suppress()  # Match two or more newlines (paragraph breaks)
paragraph = pp.OneOrMore(pp.Word(pp.printables + " "))  # Match text within a paragraph

# **Parse full document as a list of paragraphs**
document = (
    pp.DelimitedList(paragraph, delim=paragraph_separator, allow_trailing_delim=True)
    + pp.StringEnd()
)

# === Read and Parse the File ===
with open("data/owl.md", "r", encoding="utf-8") as file:
    text = file.read().strip()

text = normalize_unicode(text)
text = normalize_newlines(text)

try:
    result = document.parseString(text)
except pp.ParseException as e:
    print(f"Parsing error: {e}")
    exit(1)

# === Display Structured Output ===
print("\n=== Parsed Paragraphs ===\n")
for i, para in enumerate(result, 1):
    print(f"Paragraph {i}:")
    print(para)
    print("-" * 40)
