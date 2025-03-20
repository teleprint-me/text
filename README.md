# **Text**

Text is a Python package for extracting, parsing, and automating text pipelines from various file formats, including **plain text, Markdown, HTML, PDFs, and images**.

## **Getting Started**

### **Prerequisites**

Make sure you have **Tesseract OCR** installed on your system.

#### **Arch Linux**
```sh
sudo pacman -S poppler tesseract
```

#### **Ubuntu**
```sh
# TODO: Add installation instructions for Ubuntu
```

### **Setup**
Clone the repository, create a virtual environment, activate it, and install dependencies:

```sh
git clone https://github.com/teleprint-me/text
cd text
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## **Usage**
Once installed, you can use the CLI tools to extract text from different file formats:

```sh
# Extract text from an image
python -m text.cli.ocr -i <image_file> -o <text_file>

# Extract text from a PDF
python -m text.cli.pdf -i <pdf_file> -o <text_file>

# Extract text from an HTML file
python -m text.cli.html -i <file_or_dir_path>
```

## **Contributing**
Contributions are welcome!  
Feel free to submit **bug reports, feature requests, or pull requests** to help improve the package.

## **License**
This project is licensed under the **AGPL License** – see the [LICENSE](LICENSE) file for details.
