from sist2 import Sist2Index
import sys
import re

# Define the base tag name and color
tag_base = "sensitive"
tag_color = "#FF0000"  # Red for warning

# Define keywords to search for with their corresponding subtypes
keywords = [
    ("passwort", "passwort"),
    ("password", "password"),
    ("key", "key"),
    ("secret", "secret"),
    ("kennwort", "kennwort")
]

# Define regex patterns with associated tag subtypes
patterns = [
    # Keyword patterns (e.g., password = "something", key: abc123)
    *( (re.compile(rf'(?i)\b({keyword})\b["\'\s:=]+[^\s\'"]{{8,100}}'), subtype) for keyword, subtype in keywords),
    *( (re.compile(rf'(?i)\b({keyword})\b\s+[a-zA-Z0-9\-_.]{{8,100}}'), subtype) for keyword, subtype in keywords),
    # Specific credential patterns
    (re.compile(r'AKIA[0-9A-Z]{16}'), "aws_key"),
    (re.compile(r'Bearer\s+[a-zA-Z0-9\-._~+/]+=*'), "bearer_token"),
    (re.compile(r'eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+'), "jwt_token")
]

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
        tagged = False
        # Check each pattern and assign appropriate tag
        for pattern, subtype in patterns:
            if pattern.search(text):
                tag_type = "credential" if subtype in ["aws_key", "bearer_token", "jwt_token"] else "keyword"
                final_tag = f"{tag_base}_{tag_type}_{subtype}.{tag_color}"
                print(f"Tagging document {doc.path} with {final_tag}")

                # Check if tag key exists and is a list
                if "tag" in doc.json_data and isinstance(doc.json_data["tag"], list):
                    # Only append the new tag if it's not already present
                    if final_tag not in doc.json_data["tag"]:
                        doc.json_data["tag"].append(final_tag)
                else:
                    # If no tag key exists, create a new list with the tag
                    doc.json_data["tag"] = [final_tag]
                tagged = True

        if tagged:
            index.update_document(doc)
        else:
            print(f"Skipping document {doc.path}: No sensitive information found")
    else:
        print(f"Skipping document {doc.path}: No extracted text found")

# Sync the tag table and commit changes
index.sync_tag_table()
index.commit()

print("Done!")
