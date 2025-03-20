"""
Script: tests.sentence
Description: Parses paragraphs and sentences incrementally.
NOTE:
- suppress() seems to have no effect.
- allow_trailing_delim=True seems to have no effect.
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


# === Define Basic Sentence Grammar ===
# Define a basic grammar for sentences and paragraphs
eos = pp.oneOf(". ! ?")  # End of sentence terminator
word = pp.Word(pp.printables + " ", excludeChars=".!?")
space = pp.Optional(pp.White(" "))
sentence = pp.original_text_for(pp.OneOrMore(word + space) + eos)

eop = pp.Regex(r"\n{2,}")  # End of paragraph terminator
paragraph = pp.original_text_for(pp.OneOrMore(sentence + pp.Optional(pp.White())))

document = pp.ZeroOrMore(paragraph + pp.Optional(eop)) + pp.StringEnd()

# === Read and Parse the File ===
text = read_and_normalize("data/owl.md")

try:
    result = document.parse_string(text, parse_all=True)
except pp.ParseException as e:
    print(f"Parsing error: {e}")
    exit(1)

# === Display Structured Output ===
print(result)  # DO NOT MODIFY THIS! I need to see the raw output!
