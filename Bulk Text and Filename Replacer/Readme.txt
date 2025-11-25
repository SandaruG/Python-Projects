Project Name: AITA Text Normalizer

Description:
A simple and reliable Python utility script that scans an entire directory, finds all .txt files, and replaces occurrences of a specific string both inside the file content and in the filename itself.

This version is configured to replace the keyword "aita" with the full phrase "Am I the A Hole", making it useful for bulk formatting, dataset cleaning, content normalization, and text preprocessing.

--------------------------------------------------------------------

Features:
- Scans all .txt files inside a specified directory.
- Replaces a target string inside file names.
- Replaces the same string inside the file’s text content.
- Handles Unicode text (UTF-8).
- Simple, clean, and safe file operations.
- Error handling for file read/write/rename operations.

--------------------------------------------------------------------

How It Works:
1. You set:
   - the directory path
   - the string you want to find
   - the string you want to replace it with

2. The script loops through every `.txt` file in the directory.

3. For each file:
   - If the filename contains the old string, it renames the file.
   - It opens the file, reads all content, performs replacement, and writes the updated content back.

4. Prints status messages for processed files.

--------------------------------------------------------------------

Configuration:
Inside the script, update:

directory = r"YOUR DIRECTORY PATH"
old_string = "aita"
new_string = "Am I the A Hole"

Use raw string (r"") if your path contains backslashes.

--------------------------------------------------------------------

Requirements:
No external libraries required.

This script uses only built-in Python modules:
- os

Compatible with:
- Python 3.6+
- Windows / macOS / Linux

--------------------------------------------------------------------

Usage:

Run the script:

python main.py

The script will:
- Detect all .txt files in the directory
- Replace all occurrences of “aita” with “Am I the A Hole”
- Rename files containing "aita" in their filename
- Print a confirmation message once complete

--------------------------------------------------------------------

Example:

Before:
- aita_story_01.txt
- "aita" appears inside the text multiple times

After:
- Am I the A Hole_story_01.txt
- All internal occurrences replaced

--------------------------------------------------------------------

Project Structure:

aita-text-normalizer/
│── main.py
│── README.txt

--------------------------------------------------------------------

Notes:
- Always backup your directory before running bulk text replacements.
- Filenames and text changes are irreversible unless you have backups.
- You can customize `old_string` and `new_string` for any type of batch transformation.

--------------------------------------------------------------------

Disclaimer:
Ensure you have the right to modify files in the target directory.
The developer is not responsible for data loss due to bulk changes.

--------------------------------------------------------------------

