#!/usr/bin/env python3
import os
import re


def remove_comments_from_file(file_path):
    """Remove comments from a Python file while preserving functionality."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        cleaned_lines = []

        in_triple_quote = False
        quote_type = None

        for line_num, line in enumerate(lines):
            original_line = line

            # Handle triple quoted strings
            if '"""' in line or "'''" in line:
                # Count triple quotes in the line
                triple_double = line.count('"""')
                triple_single = line.count("'''")

                if triple_double > 0:
                    if triple_double % 2 == 1:
                        in_triple_quote = not in_triple_quote
                        quote_type = '"""'
                elif triple_single > 0:
                    if triple_single % 2 == 1:
                        in_triple_quote = not in_triple_quote
                        quote_type = "'''"

                # If this line starts a docstring and it's at the beginning of file/function/class
                stripped = line.strip()
                if (
                    stripped.startswith('"""') or stripped.startswith("'''")
                ) and line_num < 5:
                    # This might be a module docstring, skip it
                    if not in_triple_quote:  # End of docstring
                        continue
                    else:  # Start of docstring
                        continue
                else:
                    cleaned_lines.append(line)
                continue

            # Skip lines inside triple quotes
            if in_triple_quote:
                continue

            # Process line to remove comments
            if "#" in line:
                # Handle strings and comments properly
                result = ""
                in_string = False
                string_char = None
                i = 0

                while i < len(line):
                    char = line[i]

                    if not in_string:
                        if char in ['"', "'"]:
                            # Check if it's not an escaped quote
                            if i == 0 or line[i - 1] != "\\":
                                in_string = True
                                string_char = char
                        elif char == "#":
                            # Found comment, remove everything from here
                            break
                    else:
                        # We're inside a string
                        if char == string_char and (i == 0 or line[i - 1] != "\\"):
                            in_string = False
                            string_char = None

                    result += char
                    i += 1

                line = result.rstrip()

            # Add the line if it's not empty or if it's an intentional blank line
            if line.strip() or (not line.strip() and original_line == ""):
                cleaned_lines.append(line)

        # Remove consecutive empty lines
        final_lines = []
        prev_empty = False
        for line in cleaned_lines:
            if line.strip() == "":
                if not prev_empty:
                    final_lines.append(line)
                prev_empty = True
            else:
                final_lines.append(line)
                prev_empty = False

        # Write back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines))

        print(f"✓ Processed: {file_path}")

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")


def main():
    zenith_dir = "/home/shdy/Zenith/zenith"

    if not os.path.exists(zenith_dir):
        print(f"Directory {zenith_dir} does not exist!")
        return

    processed_count = 0

    # Walk through all Python files in zenith directory
    for root, dirs, files in os.walk(zenith_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                remove_comments_from_file(file_path)
                processed_count += 1

    print(f"\nFinished! Processed {processed_count} Python files in zenith folder.")


if __name__ == "__main__":
    main()
