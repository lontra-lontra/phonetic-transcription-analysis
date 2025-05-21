# Open the input file in read mode and output file in write mode
with open("flask/the_fall.txt", "r") as infile, open("flask/the_fall_.txt", "w") as outfile:
    # Read the entire content of the file
    content = infile.read()
    # Remove all newline characters and replace '.' with '.\n'
    processed_content = content.replace("\n", "").replace(".", ".\n")
    # Write the processed content to the output file
    outfile.write(processed_content)