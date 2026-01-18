#!/usr/bin/env python3

import os
import re
import argparse
from pypdf import PdfReader, PdfWriter

# =========================
# CONFIGURATION (DEFAULTS)
# =========================

INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_bills"
BILL_START_MARKER = "ADDRESSEE:"

# =========================
# HELPERS
# =========================

def clean_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\s\.-]", "", name)
    cleaned = " ".join(cleaned.split())
    return cleaned if cleaned else "Unknown_Patient"


def extract_patient_name(text: str) -> str:
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for i, line in enumerate(lines):
        if BILL_START_MARKER in line:
            after = line.split(BILL_START_MARKER, 1)[1].strip()
            if after:
                return after
            elif i + 1 < len(lines):
                return lines[i + 1]

    return "Unknown_Patient"


def save_bill(writer, patient_name, dry_run):
    safe_name = clean_filename(patient_name)
    output_path = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")

    counter = 1
    base_path = output_path
    while os.path.exists(output_path):
        output_path = base_path.replace(".pdf", f"_{counter}.pdf")
        counter += 1

    if dry_run:
        print(f"  [DRY-RUN] Would save: {os.path.basename(output_path)}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"  -> Saved: {os.path.basename(output_path)}")


def process_pdf(file_path, dry_run):
    print(f"\nProcessing: {os.path.basename(file_path)}")

    reader = PdfReader(file_path)
    current_writer = None
    current_patient = ""

    for page in reader.pages:
        text = page.extract_text() or ""

        if BILL_START_MARKER in text:
            if current_writer:
                save_bill(current_writer, current_patient, dry_run)

            current_writer = PdfWriter()
            current_writer.add_page(page)
            current_patient = extract_patient_name(text)
        else:
            if current_writer:
                current_writer.add_page(page)

    if current_writer:
        save_bill(current_writer, current_patient, dry_run)


# =========================
# MAIN
# =========================

def main():
    parser = argparse.ArgumentParser(
        description="Split Valant EHR billing PDFs into individual patient bills."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing files"
    )

    parser.add_argument(
        "--delete-originals",
        action="store_true",
        help="Delete original PDFs after successful processing"
    )

    args = parser.parse_args()

    if not os.path.isdir(INPUT_DIR):
        print(f"ERROR: Input directory '{INPUT_DIR}' does not exist.")
        return

    pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    if not pdfs:
        print("No PDF files found in input directory.")
        return

    for pdf in pdfs:
        full_path = os.path.join(INPUT_DIR, pdf)
        process_pdf(full_path, args.dry_run)

        if args.delete_originals and not args.dry_run:
            os.remove(full_path)
            print(f"  !! Deleted original: {pdf}")

    print("\nDone.")


if __name__ == "__main__":
    main()
