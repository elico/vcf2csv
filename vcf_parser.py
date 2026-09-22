import argparse
import csv
import os
import quopri
import sys


def parse_vcf_to_csv(
    vcf_path: str,
    output_csv_path: str = None,
    input_encoding: str = None,
    output_encoding: str = "utf-8-sig",
) -> str:
    """Parses a VCF (vCard) file into a CSV file with full encoding handling."""
    # 1. Resolve default output directory to current working directory
    if not output_csv_path:
        base_name = os.path.splitext(os.path.basename(vcf_path))[0]
        output_csv_path = os.path.join(os.getcwd(), f"{base_name}.csv")

    # 2. Safely read input VCF file
    lines = []
    if input_encoding:
        # Use user-specified encoding directly
        with open(vcf_path, "r", encoding=input_encoding, errors="replace") as f:
            lines = f.readlines()
    else:
        # Auto-detect fallback: try utf-8-sig first, then latin-1
        try:
            with open(vcf_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(vcf_path, "r", encoding="latin-1", errors="replace") as f:
                lines = f.readlines()

    contacts = []
    current_contact = {}
    all_headers = set()

    # 3. Line unfolding (RFC 6350)
    unfolded_lines = []
    for line in lines:
        line_clean = line.rstrip("\r\n")
        if line_clean.startswith((" ", "\t")) and unfolded_lines:
            unfolded_lines[-1] += line_clean[1:]
        else:
            unfolded_lines.append(line_clean)

    # 4. Parse vCard contents
    for line in unfolded_lines:
        if line.startswith("BEGIN:VCARD"):
            current_contact = {}
            continue
        elif line.startswith("END:VCARD"):
            if current_contact:
                contacts.append(current_contact)
            continue

        if ":" not in line:
            continue

        header_part, value = line.split(":", 1)

        # Handle Quoted-Printable inline decoding
        if "ENCODING=QUOTED-PRINTABLE" in header_part.upper():
            try:
                raw_bytes = value.replace("=", "").encode("ascii")
                value = quopri.decodestring(raw_bytes).decode(
                    "utf-8", errors="replace"
                )
            except Exception:
                pass

        field_name = header_part.split(";")[0].strip().upper()

        if field_name in ("VERSION", "PRODID"):
            continue

        all_headers.add(field_name)

        if field_name in current_contact:
            current_contact[field_name] += f"; {value.strip()}"
        else:
            current_contact[field_name] = value.strip()

    # 5. Write CSV file
    fieldnames = sorted(list(all_headers))
    with open(
        output_csv_path,
        "w",
        newline="",
        encoding=output_encoding,
        errors="replace",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)

    return output_csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert VCF (vCard) contact files into CSV with configurable character encoding.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("vcf_file", help="Path to the input VCF file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path for output CSV file. Defaults to current working directory.",
        default=None,
    )
    parser.add_argument(
        "-i",
        "--input-encoding",
        help="Force input encoding (e.g. utf-8, latin-1, cp1252, iso-8859-1). If omitted, auto-detects utf-8-sig with latin-1 fallback.",
        default=None,
    )
    parser.add_argument(
        "-e",
        "--output-encoding",
        help="Set output CSV encoding.",
        default="utf-8-sig",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.vcf_file):
        print(f"Error: Input file '{args.vcf_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    out_path = parse_vcf_to_csv(
        vcf_path=args.vcf_file,
        output_csv_path=args.output,
        input_encoding=args.input_encoding,
        output_encoding=args.output_encoding,
    )
    print(f"Successfully converted '{args.vcf_file}' -> '{out_path}'")


if __name__ == "__main__":
    main()