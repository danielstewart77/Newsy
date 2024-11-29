# Define a utility function to sanitize filenames
import re

def sanitize_filename(filename: str) -> str:
    # Remove any character that is not alphanumeric, a space, or an underscore
    filename = re.sub(r'[^a-zA-Z0-9_\-\s]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    return filename