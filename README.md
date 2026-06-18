<h1>Valant EHR PDF Bill Splitter – Complete Source &amp; Documentation</h1>

<p>
  This page bundles all files needed for the project, along with the full README.
  You can save it as <code>.html</code> and open locally.
</p>

<!-- ============ README ============ -->
<h2>README.md</h2>
<div class="file-header">📄 README.md</div>
<pre><code># Valant EHR PDF Bill Splitter

A Python tool that takes a single combined‑patient billing PDF (or multiple PDFs) exported from Valant EHR and splits them into individual patient‑facing bills. Each output file is named with the patient name, the current date, and the actual aging bucket based on the service date—bypassing the known Valant bug where all columns display “0‑30”.

## Features

- **Cross‑platform** – works on Linux, macOS, and Windows
- **Multi‑page bills** – correctly reassembles bills that span several pages
- **Automatic aging** – reads the real service date from the activity table, ignores the buggy “0‑30 Days” header
- **Four standard buckets** – 0‑30, 31‑60, 61‑90, 90+ (configurable)
- **Smart filename sanitisation** – removes characters unsafe for the file system
- **Duplicate handling** – appends a counter (`_1`, `_2`, …) if a file already exists
- **Dry‑run mode** – preview results without writing any files
- **Optional deletion** – move original PDFs to a `processed/` folder after successful splitting, or a `failed/` folder if the PDF is unreadable
- **Concurrency safety** – the provided launcher scripts (`run.sh`/`run.bat`) use a file lock to prevent overlapping executions
- **Privacy‑friendly** – no network access, all processing local

## Requirements

- Python 3.9 or newer
- pip (Python package manager)

## Installing Python

<details>
<summary>Linux (Ubuntu / Debian)</summary>

<pre><code>sudo apt update
sudo apt install python3 python3-venv python3-pip</code></pre>

</details>

<details>
<summary>macOS</summary>

<pre><code>brew install python</code></pre>

</details>

<details>
<summary>Windows</summary>

Download the installer from [python.org](https://www.python.org/downloads/) and **check “Add Python to PATH”** during installation.
</details>

## Setup

1. Clone the repository
<pre><code>git clone https://github.com/upmcplanetracker/valant-bill-splitter.git
cd valant-bill-splitter</code></pre>

2. Create a virtual environment
<pre><code>python -m venv venv</code></pre>

3. Activate the virtual environment

- Linux / macOS: `source venv/bin/activate`
- Windows: `venv\Scripts\Activate.ps1` (or `venv\Scripts\activate.bat` in Command Prompt)

4. Install dependencies
<pre><code>pip install -r requirements.txt</code></pre>

5. Configure directories

Edit `split_bills.py` and set the two variables near the top:

<pre><code>INPUT_DIR = "input_pdfs"          # where you drop the Valant export(s)
OUTPUT_DIR = "output_bills"       # where individual PDFs will appear</code></pre>

You may use relative paths (recommended) or absolute paths like `/home/user/bills_in`.

## Usage

1. Place your Valant‑exported PDF(s) inside the **input directory** (default `input_pdfs/`).  
   You can put one huge PDF with all patients, or multiple files.

2. Run the script:

### Standard run (files saved)
<pre><code>python split_bills.py</code></pre>

### Dry run (preview only)
<pre><code>python split_bills.py --dry-run</code></pre>

### Delete originals after splitting
<pre><code>python split_bills.py --delete-originals</code></pre>

When `--delete-originals` is used, each input PDF is moved to a `processed/` subfolder after it has been successfully split (or to `failed/` if an error occurs). Without the flag, the original files are left untouched.

### Shortcut launchers (Linux / macOS / Windows)

Use the provided launcher scripts – they automatically activate the virtual environment and pass any arguments to `split_bills.py`.

- Linux / macOS:
  <pre><code>./run.sh --dry-run
./run.sh --delete-originals</code></pre>

- Windows:
  <pre><code>run.bat --dry-run
run.bat --delete-originals</code></pre>

**Note:** The launcher scripts include a file lock so only one instance can run at a time.

## Configuration Reference

The following constants in `split_bills.py` control the behaviour. **You must edit them directly in the script** (there is no config file).

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_DIR` | `"input_pdfs"` | Directory containing the raw Valant PDFs |
| `OUTPUT_DIR` | `"output_bills"` | Directory where split bills are saved |
| `BILL_START_MARKER` | `"ADDRESSEE:"` (case‑insensitive) | Text that marks the first page of a new patient bill |
| `DATE_REF_PATTERN` | *internal* | Regex used to locate service dates in the activity table |

If Valant changes their layout in the future, you may need to adjust `BILL_START_MARKER`.

## How It Works

1. The script scans `INPUT_DIR` for `.pdf` files.
2. For each PDF, it reads page by page looking for `BILL_START_MARKER`.
3. When the marker is found, the current patient’s bill is finalised and a new bill starts.
4. The entire text of the patient’s bill is collected.
5. The script isolates the **activity table** by looking for the block between `Date Ref` and `0‑30 Days`.
6. Inside that block, it extracts the first occurrence of a date followed by a reference number – this is the **true service date**.
7. The days overdue are calculated and mapped to a standard aging bucket:
   - **0‑30 days** → `0-30`
   - **31‑60 days** → `31-60`
   - **61‑90 days** → `61-90`
   - **91+ days** → `90+`
8. The output filename is formed as:  
   `Patient Name - MM-DD-YYYY - Bucket.pdf`  
   (the date is the current date, not the service date).
9. If a file with the same name already exists, a counter is appended (`_1`, `_2`, …).

## Output Example

<pre><code>output_bills/
├── John Doe - 6-18-2026 - 31-60.pdf
├── Jane Smith - 6-18-2026 - 0-30.pdf
├── Unknown Patient - 6-18-2026 - 90+.pdf
└── John Doe - 6-18-2026 - 31-60_1.pdf   (duplicate avoided)</code></pre>

## Troubleshooting

| Symptom | Likely cause | Solution |
|---------|--------------|----------|
| `No PDF files found` | Input directory is empty or path is wrong | Check `INPUT_DIR`; place PDFs inside it |
| `Another instance is running` | A previous run is still active or crashed | Remove the lock file: `rm /tmp/splitbills.lock` (Linux/macOS) or delete `%TEMP%\splitbills.lock` (Windows) |
| Error processing a PDF | Corrupted PDF or unexpected format | The file is moved to `failed/`; open it manually and re‑save as PDF |
| Bucket always `0-30` | Table markers not found | Try running with a single small PDF and inspect the extracted text. Ensure `BILL_START_MARKER` matches |
| Patient name contains an address | The line after `ADDRESSEE:` is a street address | The script attempts to strip house numbers; if it fails, adjust the regex inside `process_pdf()` |
| `ModuleNotFoundError: No module named 'pypdf'` | Dependencies not installed | Run `pip install -r requirements.txt` inside the activated venv |

## FAQ

**Can I process multiple PDFs at once?**  
Yes. All PDF files found in `INPUT_DIR` are processed sequentially.

**Does this tool send any data over the internet?**  
No. Everything runs offline on your machine.

**What if a patient has more than one bill in the same PDF?**  
Each time `ADDRESSEE:` appears, a new bill is started. Multiple bills for the same patient will generate separate files (with duplication counters if the exact same filename would occur).

**Is the aging bucket based on today’s date or the export date?**  
Today’s date (the moment you run the script). If you need a different reference date, modify the `today` variable in `calculate_days_overdue()`.

**Can I change the aging buckets?**  
Absolutely. Edit the thresholds inside `calculate_days_overdue()` – the logic is straightforward.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Disclaimer

This tool is **not** affiliated with or endorsed by Valant EHR. It is an independent utility designed to aid in bill processing. You are solely responsible for ensuring HIPAA compliance when handling patient data. Always follow your organisation’s security and privacy policies.</code></pre>

<hr>

<!-- ============ split_bills.py ============ -->
<h2>split_bills.py</h2>
<div class="file-header">🐍 split_bills.py</div>
<pre><code>import os
import re
import shutil
from datetime import datetime
from pypdf import PdfReader, PdfWriter

# --- CONFIGURATION (edit these paths) ---
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_bills"
BILL_START_MARKER = "ADDRESSEE:"  # case-insensitive
PROCESSED_DIR = os.path.join(INPUT_DIR, "processed")
FAILED_DIR = os.path.join(INPUT_DIR, "failed")

# --- Flags passed via command line ---
DELETE_ORIGINALS = False
DRY_RUN = False


def clean_filename(name):
    """Removes illegal characters and extra whitespace."""
    cleaned = re.sub(r'[^\w\s\.-]', '', name)
    cleaned = " ".join(cleaned.split())
    return cleaned if cleaned else "Unknown_Patient"


def calculate_days_overdue(text):
    """
    Specifically targets the first column of the activity table to find
    the true service date, ignoring later payment/adjustment dates.
    """
    # Isolate the table data between 'Date Ref' and '0-30 Days'
    start_match = re.search(r'Date\s+Ref', text)
    end_match = re.search(r'0-30 Days', text)

    if start_match and end_match:
        table_text = text[start_match.end():end_match.start()]
    else:
        table_text = text

    # Match dates followed by a reference number (3-6 digits).
    # Accept 1- or 2-digit months/days to cover single-digit outputs.
    pattern = r'(\d{1,2}/\d{1,2}/\d{4})\s+\d{3,6}'
    matches = re.findall(pattern, table_text)

    if not matches:
        return None

    # First date is the service date
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


def process_pdf(file_path):
    print(f"Processing: {os.path.basename(file_path)}")
    reader = PdfReader(file_path)
    current_writer = None
    current_patient_name = ""
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        full_text += text

        if BILL_START_MARKER.lower() in text.lower():
            # Save previous bill if any
            if current_writer is not None:
                bucket = calculate_days_overdue(full_text)
                save_bill(current_writer, current_patient_name, bucket)
                full_text = text   # start accumulating text for the new patient

            current_writer = PdfWriter()
            current_writer.add_page(page)

            # Name extraction
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for i, line in enumerate(lines):
                if BILL_START_MARKER.lower() in line.lower():
                    # Try the part after the label first
                    split_parts = line.split(BILL_START_MARKER, 1)
                    after_label = split_parts[1].strip() if len(split_parts) > 1 else ""
                    if after_label:
                        current_patient_name = after_label
                    elif i + 1 < len(lines):
                        next_line = lines[i + 1]
                        # If the next line looks like a street address (starts with a number),
                        # extract only the name part before the comma.
                        if re.match(r'^\d+\s', next_line):
                            current_patient_name = next_line.split(',')[0].strip()
                        else:
                            current_patient_name = next_line
                    break
        else:
            if current_writer:
                current_writer.add_page(page)

    # Save the final bill
    if current_writer:
        bucket = calculate_days_overdue(full_text)
        save_bill(current_writer, current_patient_name, bucket)


def save_bill(writer, name, bucket):
    if DRY_RUN:
        date_str = datetime.now().strftime("%-m-%-d-%Y")
        bucket_str = f" - {bucket}" if bucket else ""
        filename = f"{clean_filename(name)} - {date_str}{bucket_str}.pdf"
        print(f"  [DRY RUN] Would save: {filename}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    safe_name = clean_filename(name)
    date_str = datetime.now().strftime("%-m-%-d-%Y")

    # Append bucket only if it was determined
    bucket_str = f" - {bucket}" if bucket else ""
    filename = f"{safe_name} - {date_str}{bucket_str}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Handle duplicate filenames
    counter = 1
    original_path = output_path
    while os.path.exists(output_path):
        output_path = original_path.replace(".pdf", f"_{counter}.pdf")
        counter += 1

    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"  -> Saved: {os.path.basename(output_path)}")


def main():
    global DELETE_ORIGINALS, DRY_RUN
    import sys
    if "--delete-originals" in sys.argv:
        DELETE_ORIGINALS = True
    if "--dry-run" in sys.argv:
        DRY_RUN = True

    if not os.path.exists(INPUT_DIR):
        print(f"Error: Directory {INPUT_DIR} does not exist.")
        return

    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found.")
        return

    # Create output & safeguard directories (unless dry run)
    if not DRY_RUN:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        os.makedirs(FAILED_DIR, exist_ok=True)

    for pdf_file in pdf_files:
        full_path = os.path.join(INPUT_DIR, pdf_file)
        try:
            process_pdf(full_path)
        except Exception as e:
            print(f"ERROR processing {pdf_file}: {e}")
            if not DRY_RUN:
                os.makedirs(FAILED_DIR, exist_ok=True)
                shutil.move(full_path, os.path.join(FAILED_DIR, pdf_file))
            continue

        if DELETE_ORIGINALS and not DRY_RUN:
            shutil.move(full_path, os.path.join(PROCESSED_DIR, pdf_file))
            print(f"  !! Moved original to processed: {pdf_file}")
        elif not DELETE_ORIGINALS:
            print(f"  (original kept: {pdf_file})")

    print("\nAll done!")


if __name__ == "__main__":
    main()</code></pre>

<hr>

<!-- ============ run.sh ============ -->
<h2>run.sh (Linux / macOS launcher)</h2>
<div class="file-header">🐧 run.sh</div>
<pre><code>#!/bin/bash
set -e

# ==============================
#  Valant Bill Splitter Launcher
# ==============================

LOCKFILE=/tmp/splitbills.lock

# ---- Prevent overlapping runs ----
exec 200>"$LOCKFILE"
if ! flock -n 200; then
    echo "Another instance is running. Exiting."
    exit 1
fi

# ---- Activate virtual environment ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source "$SCRIPT_DIR/venv/bin/activate"

# ---- Run the Python script with all arguments ----
if python3 "$SCRIPT_DIR/split_bills.py" "$@"; then
    deactivate
else
    deactivate 2>/dev/null || true
    exit 1
fi</code></pre>

<p><em>Make it executable:</em> <code>chmod +x run.sh</code></p>

<hr>

<!-- ============ run.bat ============ -->
<h2>run.bat (Windows launcher)</h2>
<div class="file-header">🪟 run.bat</div>
<pre><code>@echo off
setlocal enabledelayedexpansion

REM ==============================
REM  Valant Bill Splitter Launcher
REM ==============================

REM Change to the script's directory
cd /d "%~dp0"

REM ---- File lock (simple check) ----
set LOCKFILE=%TEMP%\splitbills.lock
if exist "%LOCKFILE%" (
    echo Another instance is running. Exiting.
    exit /b 1
)
type nul > "%LOCKFILE%"

REM ---- Activate virtual environment ----
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run: python -m venv venv
    del "%LOCKFILE%"
    exit /b 1
)
call venv\Scripts\activate.bat

REM ---- Run the Python script with all arguments ----
python split_bills.py %*
set PYTHON_EXIT=%ERRORLEVEL%

REM ---- Cleanup ----
call deactivate 2>nul
del "%LOCKFILE%"

exit /b %PYTHON_EXIT%</code></pre>

<hr>

<!-- ============ requirements.txt ============ -->
<h2>requirements.txt</h2>
<div class="file-header">📦 requirements.txt</div>
<pre><code>pypdf>=4.0.0</code></pre>

<hr>

<!-- ============ LICENSE ============ -->
<h2>LICENSE (MIT)</h2>
<div class="file-header">⚖️ LICENSE</div>
<pre><code>MIT License

Copyright (c) 2026 [Your Name or Organisation]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.</code></pre>

<p class="note"><strong>Note:</strong> Save this page as <code>valant-splitter.html</code>, open in a browser, and you have a fully documented offline reference for the whole project. You can copy the code blocks directly from here.</p>

</body>
</html>
