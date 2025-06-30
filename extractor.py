import fitz  # PyMuPDF
import re
import json

PDF_PATH = "Form ADT-1-29092023_signed.pdf"
OUTPUT_JSON = "output.json"

HEADER_PATTERNS = [
    r"^\(b\)", r"FORM NO", r"Notice to the Registrar", r"Refer the instruction", r"English", r"Hindi", r"Page ", r"\*", r"^\(a\)", r"^\d+\.\(a\)", r"^\d+\.\(b\)", r"^\d+\.\(c\)", r"^\d+\.\(d\)", r"^\d+\.\(e\)", r"^\d+\.\(f\)", r"^\d+\.\(g\)", r"^\d+\.\(h\)", r"^\d+\.\(i\)", r"^\d+\.\(j\)", r"^\d+\.\(k\)", r"^\d+\.\(l\)", r"^\d+\.\(m\)", r"^\d+\.\(n\)", r"^\d+\.\(o\)", r"^\d+\.\(p\)", r"^\d+\.\(q\)", r"^\d+\.\(r\)", r"^\d+\.\(s\)", r"^\d+\.\(t\)", r"^\d+\.\(u\)", r"^\d+\.\(v\)", r"^\d+\.\(w\)", r"^\d+\.\(x\)", r"^\d+\.\(y\)", r"^\d+\.\(z\)"
]

def is_header(line):
    for pat in HEADER_PATTERNS:
        if re.search(pat, line):
            return True
    return False

def extract_text_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        full_text += text + "\n"
    doc.close()
    return full_text

def extract_fields(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    data = {}
    # CIN
    cin = re.search(r"[Uu][0-9]{5}[A-Z]{2}[0-9]{4}PTC[0-9]{6}", text)
    data["cin"] = cin.group(0) if cin else ""
    # Company name (skip headers, pick first all-uppercase after label)
    company_name = ""
    for i, line in enumerate(lines):
        if "Name of the company" in line:
            for j in range(1, 5):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l.isupper() and not is_header(l):
                        company_name = l
                        break
            break
    data["company_name"] = company_name
    # Registered office (skip headers, pick next 5 lines that look like address)
    reg_office = []
    for i, line in enumerate(lines):
        if "Address of the registered office" in line:
            count = 0
            for j in range(1, 10):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l and not is_header(l) and '@' not in l and not l.lower().startswith('email'):
                        reg_office.append(l)
                        count += 1
                    if count >= 5:
                        break
            break
    data["registered_office"] = ", ".join(reg_office)
    # Email
    email = re.search(r"[\w.-]+@[\w.-]+", text)
    data["email"] = email.group(0) if email else ""
    # Appointment type (skip headers, after label)
    appoint_type = ""
    for i, line in enumerate(lines):
        if "Nature of appointment" in line:
            for j in range(1, 4):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l and not is_header(l):
                        appoint_type = l
                        break
            break
    data["appointment_type"] = appoint_type
    # Number of auditors (skip headers, after label)
    num_aud = ""
    for i, line in enumerate(lines):
        if "Number of auditor(s) appointed" in line:
            for j in range(1, 4):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l.isdigit() and not is_header(l):
                        num_aud = l
                        break
            break
    data["number_of_auditors"] = num_aud
    # Auditor name (skip headers, all-uppercase after label)
    auditor_name = ""
    for i, line in enumerate(lines):
        if "Name of the auditor or auditor's firm" in line:
            for j in range(1, 5):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l.isupper() and not is_header(l):
                        auditor_name = l
                        break
            break
    data["auditor_name"] = auditor_name
    # Auditor FRN and PAN
    frn = re.search(r"\b[0-9]{6}[A-Z]?\b", text)
    pan = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]{1}", text)
    data["auditor_frn_or_membership"] = {
        "frn": frn.group(0) if frn else "",
        "pan": pan.group(0) if pan else ""
    }
    # Auditor address (skip headers, next 6 lines after label)
    auditor_addr = []
    for i, line in enumerate(lines):
        if "Address of the Auditor" in line:
            count = 0
            for j in range(1, 10):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l and not is_header(l) and '@' not in l and not l.lower().startswith('email'):
                        auditor_addr.append(l)
                        count += 1
                    if count >= 6:
                        break
            break
    data["auditor_address"] = ", ".join(auditor_addr)
    # Auditor email
    auditor_email = re.search(r"mallyaandmallya@[\w.-]+", text)
    data["auditor_email"] = auditor_email.group(0) if auditor_email else ""
    # Period of account (look for 'From' and 'To' lines)
    period_from = ""
    period_to = ""
    for i, line in enumerate(lines):
        if line.startswith("From"):
            match = re.search(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", line)
            if match:
                period_from = match.group(0)
        if line.startswith("To"):
            match = re.search(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", line)
            if match:
                period_to = match.group(0)
    years = ""
    for i, line in enumerate(lines):
        if "Number of financial year(s) to which appointment relates" in line:
            match = re.search(r"[0-9]+", line)
            if match:
                years = match.group(0)
            break
    data["period_of_account"] = {
        "from": period_from,
        "to": period_to,
        "years": years
    }
    # AGM and appointment date (look for date pattern after label)
    agm_date = ""
    appointment_date = ""
    for i, line in enumerate(lines):
        if "date of AGM" in line:
            for j in range(1, 3):
                if i+j < len(lines):
                    match = re.search(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", lines[i+j])
                    if match:
                        agm_date = match.group(0)
                        break
        if "Date of appointment" in line:
            for j in range(1, 3):
                if i+j < len(lines):
                    match = re.search(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", lines[i+j])
                    if match:
                        appointment_date = match.group(0)
                        break
    data["agm_date"] = agm_date
    data["appointment_date"] = appointment_date
    # Attachments
    data["attachments"] = re.findall(r"([\w .'-]+\.pdf)", text)
    # Director (after 'Digitally signed by', skip headers)
    director_name = ""
    for i, line in enumerate(lines):
        if "Digitally signed by" in line:
            for j in range(1, 3):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l and not is_header(l):
                        director_name = l
                        break
            break
    din = re.search(r"\b[0-9]{8}\b", text)
    data["director"] = {
        "name": director_name,
        "din": din.group(0) if din else ""
    }
    # Board resolution number and date (look for number/date after label, skip headers)
    board_res_no = ""
    board_res_date = ""
    for i, line in enumerate(lines):
        if "resolution number" in line:
            for j in range(1, 3):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if l.isdigit() and not is_header(l):
                        board_res_no = l
                        break
        if "dated" in line:
            for j in range(1, 3):
                if i+j < len(lines):
                    l = lines[i+j].strip()
                    if re.match(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", l) and not is_header(l):
                        board_res_date = l
                        break
    data["board_resolution_number"] = board_res_no
    data["board_resolution_date"] = board_res_date
    return data

def main():
    text = extract_text_pymupdf(PDF_PATH)
    data = extract_fields(text)
    print("\nExtracted Data (JSON):\n", json.dumps(data, indent=2))
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main() 