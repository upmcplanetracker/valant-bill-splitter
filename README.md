Valant EHR PDF Bill Splitter
============================

A Python tool that takes a single combined‑patient billing PDF (or multiple PDFs) exported from Valant EHR and splits them into individual patient‑facing bills. Each output file is named with the patient name, the current date, and the actual aging bucket based on the service date—bypassing the known Valant bug where all columns display “0‑30”.

Features
--------

*   **Cross‑platform** – works on Linux, macOS, and Windows
*   **Multi‑page bills** – correctly reassembles bills that span several pages
*   **Automatic aging** – reads the real service date from the activity table, ignores the buggy “0‑30 Days” header
*   **Four standard buckets** – 0‑30, 31‑60, 61‑90, 90+ (configurable)
*   **Smart filename sanitisation** – removes characters unsafe for the file system
*   **Duplicate handling** – appends a counter (`_1`, `_2`, …) if a file already exists
*   **Dry‑run mode** – preview results without writing any files
*   **Optional deletion** – move original PDFs to a `processed/` folder after successful splitting, or a `failed/` folder if the PDF is unreadable
*   **Concurrency safety** – the provided launcher scripts (`run.sh`/`run.bat`) use a file lock to prevent overlapping executions
*   **Privacy‑friendly** – no network access, all processing local

Requirements
------------

*   Python 3.9 or newer
*   pip (Python package manager)

Installing Python
-----------------

### Linux (Ubuntu / Debian)

    sudo apt update
    sudo apt install python3 python3-venv python3-pip

### macOS

    brew install python

### Windows

Download the installer from [python.org](https://www.python.org/downloads/) and **check “Add Python to PATH”** during installation.

Setup
-----

1.  **Clone the repository**
    
        git clone https://github.com/upmcplanetracker/valant-bill-splitter.git
        cd valant-bill-splitter
    
2.  **Create a virtual environment**
    
        python -m venv venv
    
3.  **Activate the virtual environment**
    *   Linux / macOS: `source venv/bin/activate`
    *   Windows: `venv\Scripts\Activate.ps1` (or `venv\Scripts\activate.bat` in Command Prompt)
4.  **Install dependencies**
    
        pip install -r requirements.txt
    
5.  **Configure directories**
    
    Edit `split_bills.py` and set the two variables near the top:
    
        INPUT_DIR = "input_pdfs"          # where you drop the Valant export(s)
        OUTPUT_DIR = "output_bills"       # where individual PDFs will appear
    
    You may use relative paths (recommended) or absolute paths like `/home/user/bills_in`.
    

Usage
-----

1.  Place your Valant‑exported PDF(s) inside the **input directory** (default `input_pdfs/`).  
    You can put one huge PDF with all patients, or multiple files.
2.  Run the script:

### Standard run (files saved)

    python split_bills.py

### Dry run (preview only)

    python split_bills.py --dry-run

### Delete originals after splitting

    python split_bills.py --delete-originals

When `--delete-originals` is used, each input PDF is moved to a `processed/` subfolder after it has been successfully split (or to `failed/` if an error occurs). Without the flag, the original files are left untouched.

### Shortcut launchers (Linux / macOS / Windows)

Use the provided launcher scripts – they automatically activate the virtual environment and pass any arguments to `split_bills.py`.

*   **Linux / macOS:**
    
        ./run.sh --dry-run
        ./run.sh --delete-originals
    
*   **Windows:**
    
        run.bat --dry-run
        run.bat --delete-originals
    

**Note:** The launcher scripts include a file lock so only one instance can run at a time.

Configuration Reference
-----------------------

The following constants in `split_bills.py` control the behaviour. **You must edit them directly in the script** (there is no config file).

Variable

Default

Description

`INPUT_DIR`

`"input_pdfs"`

Directory containing the raw Valant PDFs

`OUTPUT_DIR`

`"output_bills"`

Directory where split bills are saved

`BILL_START_MARKER`

`"ADDRESSEE:"` (case‑insensitive)

Text that marks the first page of a new patient bill

`DATE_REF_PATTERN`

_internal_

Regex used to locate service dates in the activity table

If Valant changes their layout in the future, you may need to adjust `BILL_START_MARKER`.

How It Works
------------

1.  The script scans `INPUT_DIR` for `.pdf` files.
2.  For each PDF, it reads page by page looking for `BILL_START_MARKER`.
3.  When the marker is found, the current patient’s bill is finalised and a new bill starts.
4.  The entire text of the patient’s bill is collected.
5.  The script isolates the **activity table** by looking for the block between `Date Ref` and `0‑30 Days`.
6.  Inside that block, it extracts the first occurrence of a date followed by a reference number – this is the **true service date**.
7.  The days overdue are calculated and mapped to a standard aging bucket:
    *   **0‑30 days** → `0-30`
    *   **31‑60 days** → `31-60`
    *   **61‑90 days** → `61-90`
    *   **91+ days** → `90+`
8.  The output filename is formed as:  
    `Patient Name - MM-DD-YYYY - Bucket.pdf`  
    (the date is the current date, not the service date).
9.  If a file with the same name already exists, a counter is appended (`_1`, `_2`, …).

Output Example
--------------

    output_bills/
    ├── John Doe - 6-18-2026 - 31-60.pdf
    ├── Jane Smith - 6-18-2026 - 0-30.pdf
    ├── Unknown Patient - 6-18-2026 - 90+.pdf
    └── John Doe - 6-18-2026 - 31-60_1.pdf   (duplicate avoided)

Troubleshooting
---------------

Symptom

Likely cause

Solution

`No PDF files found`

Input directory is empty or path is wrong

Check `INPUT_DIR`; place PDFs inside it

`Another instance is running`

A previous run is still active or crashed

Remove the lock file: `rm /tmp/splitbills.lock` (Linux/macOS) or delete `%TEMP%\splitbills.lock` (Windows)

Error processing a PDF

Corrupted PDF or unexpected format

The file is moved to `failed/`; open it manually and re‑save as PDF

Bucket always `0-30`

Table markers not found

Try running with a single small PDF and inspect the extracted text. Ensure `BILL_START_MARKER` matches

Patient name contains an address

The line after `ADDRESSEE:` is a street address

The script attempts to strip house numbers; if it fails, adjust the regex inside `process_pdf()`

`ModuleNotFoundError: No module named 'pypdf'`

Dependencies not installed

Run `pip install -r requirements.txt` inside the activated venv

FAQ
---

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

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for details.

Disclaimer
----------

This tool is **not** affiliated with or endorsed by Valant EHR. It is an independent utility designed to aid in bill processing. You are solely responsible for ensuring HIPAA compliance when handling patient data. Always follow your organisation’s security and privacy policies.

* * *

Save this page as `README.html` to view it offline.
