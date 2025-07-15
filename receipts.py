import os
import re
from PIL import Image
import pytesseract
from name_loader import load_names_from_csv
pytesseract.pytesseract.tesseract_cmd = "C:/Users/bjere/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
folder_path = "C:/Users/bjere/Texas A&M University/HR & Administrative Services - Documents/Foster, Tonya D - Training - Beverly/Receipts"
foldername = 'Receipts'
valid_names = load_names_from_csv("names.csv")

# Helper Functions

def normalize_candidate_name(parts):
    suffixes = {"jr.", "sr.", "ii", "iii", "iv"}
    suffix = ""
    if parts[-1].lower().strip(".") in suffixes:
        suffix = parts[-1]
        parts = parts[:-1]

    if len(parts) == 3:
        first, _, last = parts
    elif len(parts) == 2:
        first, last = parts
    else:
        return None

    if suffix != "":
        return f"{first.upper()}_{last.upper()}_{suffix.upper()}"
    else:
        return f"{first.upper()}_{last.upper()}"

def extract_valid_names_from_text(text, valid_names):
    matches = {}
    words = text.split()

    for i in range(len(words)):
        if i + 1 < len(words):
            candidate = normalize_candidate_name(words[i:i+2])
            if candidate and candidate in valid_names:
                matches[candidate] = valid_names[candidate]

        if i + 2 < len(words):
            candidate = normalize_candidate_name(words[i:i+3])
            if candidate and candidate in valid_names:
                matches[candidate] = valid_names[candidate]

    return matches

# Main Loop

for filename in os.listdir(folder_path):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    full_path = os.path.join(folder_path, filename)

    try:
        image = Image.open(full_path)
        ocr_text = pytesseract.image_to_string(image).upper()

        # --- Extract name ---
        name_matches = extract_valid_names_from_text(ocr_text, valid_names)
        if name_matches:
            name = list(name_matches.keys())[0]
        else:
            name = "UNKNOWN"

        # --- Extract price ---
        if "purchase order transaction log" in ocr_text.lower() or "texas water utilies association" in ocr_text.lower():
            match = re.search(r'\bAmount[:\s]*\$?([\d,]+\.\d{2})', ocr_text, re.IGNORECASE)
            price = match.group(1).replace(",", "") if match else "0.00"
        else:
            matches = re.findall(r'\bTOTAL\b[\s:.]*\$?\s*([\d,]+\.\d{2})', ocr_text, re.IGNORECASE)
            if matches:
                price = matches[-1].replace(",", "")
            else:
                match = re.search(
                    r'\b(?:Total|TUITION\s*&\s*TECHNICAL\s*ASSISTANCE|Transaction\s*Amount|Payment\s*Amount|Total\s*Amount\s*Paid|Total\s*Amount|Total\s*Payment|TotalPaid|Texas.gov\s*Price|paid\s*to\s*TDLR\s*is)\b[\s:.]*\$?\s*([\d,]+\.\d{2})',
                    ocr_text, re.IGNORECASE | re.MULTILINE
                )
                if match:
                    price = match.group(1).replace(",", "")
                else:
                    all_numbers = re.findall(r'\$?([\d,]+\.\d{2})', ocr_text)
                    price = all_numbers[-1].replace(",", "") if all_numbers else "0.00"

        # --- Create new filename ---
        ext = os.path.splitext(filename)[1]
        base_filename = f"{name}_{price}"
        new_filename = f"{base_filename}{ext}"
        new_path = os.path.join(folder_path, new_filename)

        counter = 1
        while os.path.exists(new_path):
            new_filename = f"{base_filename}_{counter}{ext}"
            new_path = os.path.join(folder_path, new_filename)
            counter += 1

        # --- Rename file ---
        os.rename(full_path, new_path)
        print(f"Renamed {filename} to {new_filename}")

    except Exception as e:
        print(f"ERROR processing {filename}: {e}")