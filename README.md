[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# vcf2csv

Convert VCARD x.x `.vcf` files into clean `.csv` format. Handles Apple/iCloud-specific fields, related names, dates, etc.
Not perfetc buyt works.

## Usage
```
usage: vcf_parser.py [-h] [-o OUTPUT] [-i INPUT_ENCODING] [-e OUTPUT_ENCODING] vcf_file

Convert VCF (vCard) contact files into CSV with configurable character encoding.

positional arguments:
  vcf_file              Path to the input VCF file.

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Path for output CSV file. Defaults to current working directory. (default: None)
  -i, --input-encoding INPUT_ENCODING
                        Force input encoding (e.g. utf-8, latin-1, cp1252, iso-8859-1). If omitted, auto-detects utf-8-sig with latin-1 fallback.
                        (default: None)
  -e, --output-encoding OUTPUT_ENCODING
                        Set output CSV encoding. (default: utf-8-sig)
```