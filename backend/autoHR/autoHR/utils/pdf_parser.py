import fitz # PyMuPDF
import re

def extract_text_from_pdf(file_stream):
    content = file_stream.read()
    doc = fitz.open(stream=content, filetype="pdf")  # Ensure the filetype is "pdf" if you're reading a PDF
    text = ""
    for page in doc:
        text += page.get_text()
    return text  # Return the entire text as a single string for simplicity


def parse_equipment_details(equipment_text):
    results = []
    lines = equipment_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Skipping known non-equipment lines more robustly
        if any(prefix in line for prefix in ["Time:", "Date:", "Page", "From:", "To:", "FE:", "UIC:", "MPO", "SysNo", "UI", "CIIC", "DLA", "BUoM", "OH Qty"]):
            i += 1
            continue

        # NSN validation adjusted to be more strict
        if line.startswith("NSN"):
            nsn = lines[i+7].strip()
            name = lines[i + 8].strip() 
            quantity = lines[i + 13].strip()

            # Collect serial numbers, accounting for multiple lines
            serial_numbers = []
            j = i + 20 
            expected_length = None

            while j< len(lines) and not (lines[j].strip().startswith('NSN')):
                candidate = lines[j].strip()
                if len(candidate) > 4 and " " not in candidate and not candidate.startswith(("NSN", "MPO", "Time:", "Date:", "SerNo", "From")):
                    if expected_length is None:
                        expected_length = len(candidate)
                        serial_numbers.append(candidate)
                    elif len(candidate) == expected_length:
                        serial_numbers.append(candidate)
                j += 1
            
            results.append({
                "nsn": nsn,
                "name": name,
                "quantity": quantity or "Unknown",  # Fallback if quantity isn't found
                "serial numbers": serial_numbers,
            })
            i = j
        else:
            i += 1

    return results



#THIS ONE WORKS BUT DOES NOT RETURN THE SERIAL NUMBERS CORRECTLY
# def parse_equipment_details(equipment_text):
#     results = []
#     # Pattern to extract the desired information
#     i = 0 
#     lines = equipment_text.split('\n')
#     while i< len(lines):
#         line = lines[i].strip()
#         if len(line) == 13 and line[len(line)-1].isdigit():
#             nsn = line
#             name = lines[i+1].strip()
#             quantity = lines[i+3].strip()

#             serial_numbers = []
#             j = i+4
#             while j < len(lines) and not (len(lines[j].strip()) == 13 and lines[j].strip()[0].isdigit()):
#                 if lines[j].strip() == "SerNo/RegNo/LotNo":
#                     serial_number = lines[j + 1].strip()
#                     serial_numbers.append(serial_number)
#                     j += 1  # Skip the next line as it's already processed as a serial number
#                 j += 1
#             results.append({
#                 "nsn": nsn,
#                 "name": name,
#                 "quantity": quantity, 
#                 "serial numbers": serial_numbers,
#             })
#             i = j
#         else:
#             i += 1
#     return results


           
def debug_parse_equipment_details(equipment_text):
    # Start simple: Match only NSN to ensure basic regex functionality
    pattern = re.compile(r"\b[a-zA-Z0-9]{12}\d\b")
    nsn_matches = pattern.findall(equipment_text)
    print(nsn_matches)
    
    return [{"nsn": nsn} for nsn in nsn_matches]