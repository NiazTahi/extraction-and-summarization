# Filesure Form ADT-1 Data Extraction & AI Summary

This project extracts structured data from a Form ADT-1 PDF (auditor appointment filing) and generates a professional summary using Google Gemini AI.

---

## Features

- **PDF Extraction:** Extracts key fields (company, auditor, dates, etc.) from Form ADT-1 using PyMuPDF.
- **Structured Output:** Saves extracted data as JSON.
- **AI Summary:** Uses Google Gemini to generate a concise, professional summary.
- **Easy to Run:** Simple CLI workflow, environment variable support.

---

## Setup

1. **Clone the repository and enter the project directory.**

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up your Google API key:**
   - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Create a `.env` file in the project root:
     ```
     GOOGLE_API_KEY=your-google-api-key-here
     ```

---

## Usage

### 1. Extract Data from PDF

Place your Form ADT-1 PDF in the project directory (e.g., `Form ADT-1-29092023_signed.pdf`).

Run the extractor:
```sh
python extractor.py
```
- This will create `output.json` with the extracted data.

### 2. (Optional) Manually Correct Data

If needed, edit `output.json` or create `output2.json` with corrected values for better summary results.

### 3. Generate AI Summary

Run the summary generator:
```sh
python generate_summary.py
```
- By default, it reads from `output2.json` (if present) for best results.
- The summary will be printed and saved to `summary.txt`.

---

## File Overview

- `extractor.py` — Extracts structured data from the PDF.
- `output.json` — Raw extracted data.
- `output2.json` — (Optional) Manually corrected data for summary generation.
- `generate_summary.py` — Generates an AI summary using Google Gemini.
- `summary.txt` — The final summary output.

---

## Example Output

**Summary Example:**
```
ALUPA FOODS PRIVATE LIMITED has appointed MALLYA AND MALLYA (FRN: 576105) as its statutory auditor for FY 2023-24, effective from 01/04/2023 to 31/03/2024. The appointment, approved via board resolution BR001 on 29/09/2023, was disclosed via Form ADT-1, with all supporting documents submitted.
```

---

## Notes

- Only tested with the provided Form ADT-1 sample. For other forms, field extraction logic may need adjustment.
- Requires a valid Google Gemini API key for summary generation.

---