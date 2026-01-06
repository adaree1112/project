code_text = ''''''

lines = code_text.splitlines()

code = 0
docstring_text = 0
blank_outside = 0
blank_inside = 0

in_docstring = False

for line in lines:
    stripped = line.strip()

    # Handle docstring boundary lines
    if stripped.startswith('"""'):
        # Toggle docstring state
        in_docstring = not in_docstring

        # Count the """ line itself
        if stripped == '"""':
            blank_inside += 1
        else:
            docstring_text += 1
        continue

    if in_docstring:
        if stripped == "":
            blank_inside += 1
        else:
            docstring_text += 1
    else:
        if stripped == "":
            blank_outside += 1
        else:
            code += 1

print("Code:", code)
print("Text in docstring (not blank):", docstring_text)
print("Blank (outside docstring):", blank_outside)
print("Blank (inside docstring):", blank_inside)