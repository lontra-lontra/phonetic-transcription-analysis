#get_pseudo_code(bubble_sorte)
import os
import subprocess
import sys
import inspect
all_variables_at_all_instants = []
code = ""
def snapshot(line):
    caller_frame = inspect.currentframe().f_back  # Get the caller's frame
    all_variables = {**caller_frame.f_locals}  # Merge global and local variables

    # Create a filtered dictionary with type, name, and value
    filtered_variables = {
        var_name: {"type": type(var_value).__name__, "value": var_value if var_name in caller_frame.f_locals else "global"}
        for var_name, var_value in all_variables.items()
        if not (var_name.startswith('__') or var_name in sys.modules)
    }
    filtered_variables["__code_line"] = {"type": "int", "value": line}
    all_variables_at_all_instants.append(filtered_variables) 




def bubble_sorte(array):
    n = len(array) # n <- len(array) 
    for i in range(n): # for i \in {0,1...n} :
        for j in range(0, n-i-1): # for j \in {0,1,...,n-i-1} :
            if array[j] > array[j+1]: # asfd
                array[j], array[j+1] = array[j+1], array[j] # skgçskfgçl
                aaaaaaaaaaaaaa = 0    
                a = aaaaaaaaaaaaaa+1   
                array[0] = array[0]*a  
    return array 

def get_pseudo_code(source_lines):
    """
    Extracts the pseudo code from a given function.
    
    Parameters:
    - func (function): The function to extract pseudo code from.
    
    Returns:
    - str: The pseudo code as a string.
    """
    pseudo_code = []
    
    for line in source_lines:
        # if thre is a #, ignore all that was written before
        line = line.split("#")[1] if "#" in line else line
        pseudo_code.append(line)
    return "\n".join(pseudo_code)

# Example usage
if 0==0:
    sample_list = [1,2]
    print("Source code of bubble_sort function:")
    # Insert snapshot calls between each line of the bubble_sort function
    source_lines = inspect.getsource(bubble_sorte).splitlines()
    modified_function = []
    for i, line in enumerate(source_lines, start=1):
        modified_function.append(line)
        if line.strip() and not line.strip().startswith("def") and not line.strip().startswith("return"):
            indent = len(line) - len(line.lstrip())  # Preserve indentation
            next_indent = len(source_lines[i]) - len(source_lines[i].lstrip()) if i < len(source_lines) else 0
            modified_function.append(" " * max(next_indent,indent) + f"snapshot({i})")
    print("\n".join(modified_function))

    # Change the function name to include "modified_"
    modified_function[0] = modified_function[0].replace("def ", "def modified_")
    exec("\n".join(modified_function))
    print(all_variables_at_all_instants)
    # Call the modified bubble_sort function
    print("Calling the modified bubble_sort function:")
    sorted_list_modified = modified_bubble_sorte(sample_list)
    print(get_pseudo_code(source_lines))
    print(all_variables_at_all_instants)
    import json2latex
    with open('out.tex', 'w') as f:
        json2latex.dump('data', all_variables_at_all_instants, f)