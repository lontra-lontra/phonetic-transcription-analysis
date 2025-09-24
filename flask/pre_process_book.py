# Open the input file in read mode and output file in write mode
with open("flask/toefl_trainning_.txt", "r", encoding="utf-8") as infile, open("flask/toefl_trainning.txt", "w", encoding="utf-8") as outfile:
    # Read the entire content of the file
    content = infile.read()
    # Remove all newline characters and replace '.' with '.\n'
    processed_content = content.replace("\n", "").replace(".", ".\n")
    # Write the processed content to the output file
    outfile.write(processed_content)
