Valant EHR PDF Bill Splitter
============================
Splits a single combined-patient billing PDF exported from Valant EHR into individual, patient-named billing PDFs.
* * *

Features
--------
*   Linux, macOS, and Windows support
*   Automatically handles 1- or multi-page bills
*   Clean, filesystem-safe filenames
*   Dry-run mode (no file writes)
*   Optional deletion of original PDFs
* * *

Requirements
------------
*   Python 3.9+
* * *

Installing Python
-----------------
### Linux (Ubuntu / Debian)

sudo apt install python3 python3-venv python3-pip

### macOS

brew install python

### Windows

Download from https://www.python.org/downloads/  
**Check “Add Python to PATH”**

* * *

Setup
-----
git clone https://github.com/upmcplanetracker/valant-bill-splitter.git
cd valant-bill-splitter
python -m venv venv

### Activate Virtual Environment

#### Linux / macOS

source venv/bin/activate

#### Windows

venv\\Scripts\\Activate.ps1

### Install Dependencies

pip install -r requirements.txt

* * *

Usage
-----
Place Valant-exported PDFs into `input_pdfs/`

### Standard Run

python split\_bills.py

### Dry Run (no files written)

python split\_bills.py --dry-run

### Delete Originals After Splitting

python split\_bills.py --delete-originals

### Linux / macOS Shortcut

./run.sh --dry-run
./run.sh --delete-originals

### Windows Shortcut

run.bat --delete-originals
run.bat --dry-run

* * *

Configuration
-------------
These values are defined at the top of `split_bills.py` and control where files are read from, where output is written, and how new bills are detected.

### INPUT\_DIR

The directory containing the original, combined PDF files exported from Valant. Every PDF in this folder will be processed.
This can be either a relative path (recommended) or an absolute path.

**Examples:**

*   Windows: `C:\bills_in`
*   macOS: `/Users/yourname/Documents/bills_in`
*   Linux: `/home/yourname/bills_in`
* * *

### OUTPUT\_DIR

The directory where individual patient billing PDFs will be written.
If the directory does not exist, it will be created automatically. Each output file is named after the patient listed on the bill.

**Examples:**

*   Windows: `C:\bills_out`
*   macOS: `/Users/yourname/Documents/bills_out`
*   Linux: `/home/yourname/bills_out`
* * *

### BILL\_START\_MARKER

A text string that appears on the **first page of every patient bill**.
When this text is detected, the script knows a new bill begins on that page.
For Valant EHR, the correct value is:
ADDRESSEE:

If your PDF format differs or Valant changes their layout in the future, this value may need to be adjusted.
* * *

Disclaimer
----------
Not affiliated with or endorsed by Valant EHR. Ensure HIPAA compliance when handling patient data.
