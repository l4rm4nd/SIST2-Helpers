from sist2 import Sist2Index
import sys
import re

# Define the tag for email addresses
tag_name = "e-mail"
tag_color = "#fcb103"  # Your specified color
final_tag = f"{tag_name}.{tag_color}"

# Define allowed email domains (case-insensitive)
allowed_domains = [
    "example.com",
    "example2.com",
    "example3.com"
]

# Create regex patterns
# Primary pattern: Matches emails with @ (e.g., hans-juergen@bw.aok.de)
domain_pattern = "|".join(re.escape(domain).replace(r'\.', r'\.') for domain in allowed_domains)
email_pattern = re.compile(rf'[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.)*({domain_pattern})\b', re.IGNORECASE)
# Fallback pattern: Matches email-like strings without @ (e.g., hans-juergen bw.aok.de)
fallback_pattern = re.compile(rf'[a-zA-Z0-9._%+-]+\s+([a-zA-Z0-9.-]+\.)*({domain_pattern})\b', re.IGNORECASE)

# Load the index from the provided path
index = Sist2Index(sys.argv[1])

# Debug settings
debug_count = 0
debug_limit = 1  # Print full attributes for the first document only

# Iterate over all documents in the index
for doc in index.document_iter():
    # Debug: Print document attributes and json_data for the first document
    if debug_count < debug_limit:
        print(f"Document {doc.path}:")
        print("  Attributes:", dir(doc))
        print("  json_data contents:", doc.json_data)
        debug_count += 1

    # Get the extracted text (assuming 'content' is the key)
    text = doc.json_data.get('content')

    if text and isinstance(text, str):
        # Debug: Print the full content to verify what's extracted
        print(f"Content of {doc.path}: {text}")
        # Check for email patterns
        matches = [m.group(0) for m in email_pattern.finditer(text)]
        fallback_matches = [m.group(0) for m in fallback_pattern.finditer(text)]
        all_matches = matches + [m for m in fallback_matches if m not in matches]  # Avoid duplicates

        if all_matches:
            print(f"Tagging document {doc.path} with {final_tag} (matched: {all_matches})")
            # Check if tag key exists and is a list
            if "tag" in doc.json_data and isinstance(doc.json_data["tag"], list):
                # Only append the new tag if it's not already present
                if final_tag not in doc.json_data["tag"]:
                    doc.json_data["tag"].append(final_tag)
            else:
                # If no tag key exists, create a new list with the tag
                doc.json_data["tag"] = [final_tag]
            index.update_document(doc)
        else:
            print(f"Skipping document {doc.path}: No email addresses with allowed domains found")
    else:
        print(f"Skipping document {doc.path}: No extracted text found")

# Sync the tag table and commit changes
index.sync_tag_table()
index.commit()

print("Done!")
