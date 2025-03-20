# Text

Text is a Python package for extracting, parsing, and automating text pipelines from various file formats such as plain text, html, images, and pdf documents.

## Getting Started

### Prerequisites

Make sure you have Tesseract OCR installed on your system.

#### Arch Linux

```sh
sudo pacman -S tesseract
```

#### Ubuntu

```sh
# Todo: Add installation instructions for Ubuntu
```

### Setup

Clone the repository, create a virtual environment, activate it, and install the required dependencies using pip.

```sh
git clone https://github.com/teleprint-me/text
cd text
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Once the package and its dependencies are installed, you can use the command-line tools provided by the package to extract text from different file formats.

```sh
# Example command for extracting text from an image
python -m text.cli.ocr --path_image <image_path>

# Example command for extracting text from a PDF
python -m text.cli.pdf --path_input <pdf_path>

# Example command for extracting text from an HTML file
python -m text.cli.html --dir-path <directory_path>
```

## Contributions

Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests to help improve the package.

## License

This project is licensed under the AGPL License - see the [LICENSE](LICENSE) file for details.
