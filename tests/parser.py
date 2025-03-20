"""
Script: tests.parser
Description: Implements a simple test bed for experimenting with pyparsing.
"""

import string
import unicodedata

import pyparsing as pp
import regex as re


def normalize_newlines(text: str) -> str:
    """Normalize newlines while preserving paragraph breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # Normalize CRLF → LF
    text = re.sub(
        r"(?<!\n)\n(?!\n)", " ", text
    )  # Replace single newlines with spaces (handle line wrapping)
    return text.lstrip("\ufeff")  # Remove BOM if present


def normalize_unicode(text: str) -> str:
    """Apply Unicode normalization and replace fancy punctuation with ASCII."""
    quotes = {"‘": "'", "’": "'", "“": '"', "”": '"'}
    text = unicodedata.normalize("NFKC", text)
    for old, new in quotes.items():
        text = text.replace(old, new)
    return text


def read_and_normalize(file: str) -> str:
    # === Read and Parse the File ===
    with open(file, "r", encoding="utf-8") as file:
        text = file.read().strip()
    text = normalize_unicode(text)
    text = normalize_newlines(text)
    return text


# === Tokens ===
word = pp.Word(pp.alphas + "'")  # Words, including contractions
number = pp.Word(pp.nums)  # Numbers
punctuation = pp.Regex(r"[.,;:!?]")  # Sentence-ending punctuation
quote = pp.Regex(r'"[^"]*"') | pp.Regex(r"'[^']*'")  # Handles quoted text
markdown = pp.Regex(r"[-#*_`~]+")  # Headers, lists, formatting
html_tag = pp.Regex(r"</?\w+[^>]*>")  # Matches HTML-like tags (e.g., <p>, <img>)

# === Sentences ===
sentence_end = pp.Suppress(pp.Regex(r"(?<=[a-zA-Z0-9])([.!?]+)")) | pp.StringEnd()
sentence = pp.OneOrMore(markdown | html_tag | quote | word | number | punctuation) + sentence_end

# === Paragraphs ===
# **Define paragraph separator as a true divider**
paragraph_separator = pp.Regex(r"\n{2,}")

# **Paragraphs are now properly defined as separate groups**
paragraph = pp.OneOrMore(sentence)

# === Documents ===
# **Ensure paragraphs are correctly separated**
document = (
    pp.DelimitedList(paragraph, delim=paragraph_separator, allow_trailing_delim=True)
    + pp.StringEnd()
)


# === Read and Parse the File ===
try:
    text = read_and_normalize("data/owl.md")
    result = document.parseString(text)
except pp.ParseException as e:
    print(f"Parsing error: {e}")
    exit(1)

# === Display Structured Output ===
print(result)
