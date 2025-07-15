
import os
import re
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:/Users/bjere\AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
folder_path = "C:/Users/bjere/Texas A&M University/HR & Administrative Services - Documents/Foster, Tonya D - Training - Beverly/Receipts"
foldername = 'Receipts'

#read worker first names from text file
with open ('C:/Users/bjere/Texas A&M University/HR & Administrative Services - Documents/Foster, Tonya D - Training - Beverly/Worker_first.txt',newline='') as f:
    Worker_first = [line.strip() for line in f]

#read worker last names from text file
with open (r'C:/Users/bjere/Texas A&M University/HR & Administrative Services - Documents/Foster, Tonya D - Training - Beverly/Worker_last.txt',newline='') as f:
    Worker_last = [line.strip() for line in f]

#Convert first and last names to uppercase and remove extra spaces
Worker_first_upper = [name.strip('\n').upper() for name in Worker_first]
Worker_last_upper = [name.strip('\n').upper() for name in Worker_last]

#loop through receipt files
for foldername in os.listdir(folder_path):
    
    if foldername.lower().endswith(('.png', '.jpg','jpeg')):
        full_path = os.path.join(folder_path, foldername)
        
        try:
            #loading image
            image = Image.open(full_path)
            
            #OCR the image
            ocr_text = pytesseract.image_to_string(image).upper()

            #find first name match
            matched_first = None
            for name in Worker_first_upper:
                #single substring match
                if name in ocr_text:
                    if name == " BEVERLY":
                        beverly = "BEVERLY"
                        continue
                    matched_first = name
                    #.replace(" ","_")
                    break
            
            #find last name match
            matched_last = None
            if matched_first == "SCOTT":
                matched_last = "BRATSEN"
            else:
                for name in Worker_last_upper:
                    #single substring match
                    if name in ocr_text:
                        if name == " HUGGINS":
                            huggins = "HUGGINS"
                            continue
                        matched_last = name
                        break
            
            if matched_first == None and matched_last == None and beverly == "BEVERLY":
                matched_first = "BEVERLY_"
                matched_last = "HUGGINS"
            
            #extracting price using "Total: | extracting price using TUITION TECHNICAL ASSISTANCE"
            if "purchase order transaction log" in ocr_text.lower() or "texas water utilies association" in ocr_text.lower():
                match = re.search(r'\bAmount[:\s]*\$?([\d,]+\.\d{2})', ocr_text, re.IGNORECASE)
            else:
                matches = re.findall(r'\bTOTAL\b[\s:.]*\$?\s*([\d,]+\.\d{2})', ocr_text, re.IGNORECASE)
                #keyword fall back
                if matches:
                    price = matches[-1].replace(",", "")  # Use the last TOTAL match
                else:
                    match = re.search(
                        r'\b(?:Total|TUITION\s*&\s*TECHNICAL\s*ASSISTANCE|Transaction\s*Amount|Payment\s*Amount|Total\s*Amount\s*Paid|Total\s*Amount|Total\s*Payment|TotalPaid|Texas.gov\s*Price|paid\s*to\s*TDLR\s*is)\b[\s:.]*\$?\s*([\d,]+\.\d{2})', 
                        ocr_text, 
                        re.IGNORECASE | re.MULTILINE
                    )
                    if match:
                        price = match.group(1).replace("'","")
                    else:
                        #last number in receipt
                        all_numbers = re.findall(r'\$?([\d,]+\.\d{2})', ocr_text)
                        price = all_numbers[-1].replace(",","") if all_numbers else "UNKNOWN"

            #creating file names
            name_part1 = matched_first if matched_first else "UNKNOWN"
            name_part2 = matched_last if matched_last else "UNKNOWN"
            
            if name_part1 == "UNKNOWN" or name_part2 == "UNKNOWN":
                new_filename = f"UNKNOWN_{price}{os.path.splitext(foldername)[1]}"
                new_path = os.path.join(folder_path, new_filename)
                
                #Ensuring file name is unique
                counter = 1
                while os.path.exists(new_path):
                    new_filename = f"UNKNOWN_{price}_{counter}{os.path.splitext(foldername)[1]}"
                    new_path = os.path.join(folder_path, new_filename)
                    counter += 1
            else:
                new_filename = f"{name_part1}_{name_part2}_{price}{os.path.splitext(foldername)[1]}"
                new_path = os.path.join(folder_path, new_filename)
                
                #Ensuring file name is unique
                counter = 1
                while os.path.exists(new_path):
                    new_filename = f"{name_part1}_{name_part2}_{price}_{counter}{os.path.splitext(foldername)[1]}"
                    new_path = os.path.join(folder_path, new_filename)
                    counter += 1


            # Rename the file
            os.rename(full_path, new_path)
            print(f"Renamed {foldername} to {new_filename}")
            #print(f"Total not found in {foldername}. OCR output: {ocr_text.strip()}")
            #print(repr(ocr_text))
            #print(f"OCR output: {ocr_text.strip()}")
        except Exception as e:
            print(f"ERROR processing {foldername}: {e}")       
