def load_names_from_csv(path):
    valid_names = {}
    suffixes = {"jr.", "sr.", "ii", "iii", "iv"}
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split()
            suffix = ""
            # Remove suffix if it's the last part and recognized
            if parts > 2:
                suffix =parts[-1]
                parts = parts[:-1] # Remove suffix
            
            first, last = parts
                
            if suffix:
                key = f"{first.upper()}_{last.upper()}_{suffix.upper()}"
                valid_names[key] = f"{first} {last} {suffix}"
            else: 
                key = f"{first.upper()}_{last.upper()}"
                valid_names[key] = f"{first} {last}"
    
    return valid_names
