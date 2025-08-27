from sist2 import Sist2Index
import sys
import re

# Define the tag for email addresses
tag_name = "e-mail"
tag_color = "#fcb103"  # Red for visibility
final_tag = f"{tag_name}.{tag_color}"

# Define allowed email domains (case-insensitive)
# will also tag any subdomains like test@admin.example.com
allowed_domains = [
    "example.com",
    "company.org",
    "test.net"
]

# Create regex pattern for email addresses with specific domains and subdomains
# Escape dots in domains and join with | for regex
domain_pattern = "|".join(re.escape(domain).replace(r'\.', r'\.') for domain in allowed_domains)
email_pattern = re.compile(rf'[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.)*({domain_pattern})\b', re.IGNORECASE)

# Load the index from the provided path
index = Sist2Index(sys.argv[1])

# Debug settings
debug_count = 0
debug_limit = 1  # Print debug info for the first document only

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
        # Check if the email pattern matches in the text
        if email_pattern.search(text):
            print(f"Tagging document {doc.path} with {final_tag}")
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
