with open ("names.csv", "r") as file: # opens the file in read mode
    names = [line.strip() for line in file if line.strip()] # reads each line, strips whitespace, and filters out empty lines

names.sort() # sorts the names alphabetically and stores in memory

with open("names.csv", "w") as file: # opens the file in write mode
    for name in names:  # writes each name back to the file 
        file.write(name + "\n")