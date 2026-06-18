#!/usr/bin/env python3

import os
import re
import shutil
import argparse
from datetime import datetime
from pypdf import PdfReader, PdfWriter

# =========================
# CONFIGURATION (DEFAULTS)
# =========================

INPUT_DIR = "change_to_your_pdf_input_directory"
OUTPUT_DIR = "change_to_your_pdf_output_directory"
BILL_START_MARKER = "ADDRESSEE:"

# Subdirectories for processed and failed originals
PROCESSED_DIR = os.path.join(INPUT_DIR, "processed")
FAILED_DIR = os.path.join(INPUT_DIR, "failed")

# =========================
# HELPERS
# =========================

def clean_filename(name: str) -> str:
    """Remove illegal characters and extra whitespace."""
    cleaned = re.sub(r"[^\w\s\.-]", "", name)
    cleaned = " ".join(cleaned.split())
    return cleaned if cleaned else "Unknown_Patient"


def calculate_days_overdue(text: str):
    """
    Isolate the activity table and find the true service date.
    Returns an aging bucket string: '0-30', '31-60', '61-90', '90+'
    or None if no date could be determined.
    """
    # Look for the block between 'Date Ref' and '0-30 Days'
    start_match = re.search(r'Date\s+Ref', text)
    end_match = re.search(r'0-30 Days', text)

    if start_match and end_match:
        table_text = text[start_match.end():end_match.start()]
    else:
        table_text = text

    # Extract dates followed by a reference number (3-6 digits).
    # Accept 1- or 2-digit months/days.
    pattern = r'(\d{1,2}/\d{1,2}/\d{4})\s+\d{3,6}'
    matches = re.findall(pattern, table_text)

    if not matches:
        return None

    service_date = datetime.strptime(matches[0], '%m/%d/%Y')
    today = datetime.now()
    delta = (today - service_date).days

    # Standard medical-billing aging buckets
    if delta >= 90:
        return "90+"
    elif delta >= 61:
        return "61-90"
    elif delta >= 31:
        return "31-60"
    else:
        return "0-30"


def extract_patient_name(text: str) -> str:
    """Pull the patient name from the line containing BILL_START_MARKER."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for i, line in enumerate(lines):
        if BILL_START_MARKER.lower() in line.lower():
            # Find the split point regardless of case
            marker_start = line.lower().find(BILL_START_MARKER.lower())
            marker_end = marker_start + len(BILL_START_MARKER)
            after = line[marker_end:].strip()

            if after:
                return after
            elif i + 1 < len(lines):
                next_line = lines[i + 1]
                # If next line starts with a number, it's probably an address
                if re.match(r'^\d+\s', next_line):
                    # Take only the part before the first comma (the name portion)
                    return next_line.split(',')[0].strip()
                return next_line

    return "Unknown_Patient"


def save_bill(writer, patient_name, dry_run):
    """Save a single patient's bill with date and bucket in filename."""
    full_text = ""
    # We can't easily get the full text here without passing it around.
    # Instead, we'll accumulate text per patient bill in process_pdf.
    # For now, this function receives the bucket from outside.
    # (We'll modify process_pdf to pass bucket)
    safe_name = clean_filename(patient_name)
    date_str = datetime.now().strftime("%-m-%-d-%Y")

    # bucket will be added by caller
    bucket_str = ""  # placeholder, will be overridden by actual call
    # This function will be updated to accept bucket as a parameter.

    # We'll actually change the signature to include bucket.
    # Let's rewrite this properly.
    return  # temporary to avoid confusion, will replace with full version


# =========================
# PROCESSING
# =========================

def process_pdf(file_path, dry_run, delete_originals):
    print(f"\nProcessing: {os.path.basename(file_path)}")

    reader = PdfReader(file_path)
    current_writer = None
    current_patient = ""
    current_full_text = ""  # accumulate text per patient

    for page in reader.pages:
        text = page.extract_text() or ""

        if BILL_START_MARKER.lower() in text.lower():
            # Save previous patient bill (if any)
            if current_writer:
                bucket = calculate_days_overdue(current_full_text)
                _save_bill(current_writer, current_patient, bucket, dry_run)

            # Start new patient
            current_writer = PdfWriter()
            current_writer.add_page(page)
            current_patient = extract_patient_name(text)
            current_full_text = text  # reset text accumulator
        else:
            if current_writer:
                current_writer.add_page(page)
                current_full_text += text

    # Save the last patient
    if current_writer:
        bucket = calculate_days_overdue(current_full_text)
        _save_bill(current_writer, current_patient, bucket, dry_run)


def _save_bill(writer, patient_name, bucket, dry_run):
    """Internal: write the PDF with proper naming, or print dry-run message."""
    safe_name = clean_filename(patient_name)
    date_str = datetime.now().strftime("%-m-%-d-%Y")

    bucket_str = f" - {bucket}" if bucket else ""
    filename = f"{safe_name} - {date_str}{bucket_str}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Handle duplicates
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
        help="Move original PDFs to 'processed/' after successful splitting, or 'failed/' if an error occurs"
    )

    args = parser.parse_args()

    if not os.path.isdir(INPUT_DIR):
        print(f"ERROR: Input directory '{INPUT_DIR}' does not exist.")
        return

    pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    if not pdfs:
        print("No PDF files found in input directory.")
        return

    # Create subdirectories if needed
    if not args.dry_run and args.delete_originals:
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        os.makedirs(FAILED_DIR, exist_ok=True)

    for pdf in pdfs:
        full_path = os.path.join(INPUT_DIR, pdf)
        try:
            process_pdf(full_path, args.dry_run, args.delete_originals)
        except Exception as e:
            print(f"ERROR processing {pdf}: {e}")
            if not args.dry_run and args.delete_originals:
                shutil.move(full_path, os.path.join(FAILED_DIR, pdf))
                print(f"  !! Moved to failed/: {pdf}")
        else:
            # Successful processing
            if args.delete_originals and not args.dry_run:
                shutil.move(full_path, os.path.join(PROCESSED_DIR, pdf))
                print(f"  !! Moved to processed/: {pdf}")

    print("\nDone.")


if __name__ == "__main__":
    main()
