# Text Extraction

Text Extraction is a Python package for extracting text from various file formats such as images, PDFs, and HTML documents.

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
git clone https://github.com/teleprint-me/text-extraction
cd text-extraction
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Once the package and its dependencies are installed, you can use the command-line tools provided by the package to extract text from different file formats.

```sh
# Example command for extracting text from an image
python -m text_extraction.cli.ocr --path_image <image_path>

# Example command for extracting text from a PDF
python -m text_extraction.cli.pdf --path_input <pdf_path>

# Example command for extracting text from an HTML file
python -m text_extraction.cli.html --dir-path <directory_path>
```

## Contributions

Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests to help improve the package.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
