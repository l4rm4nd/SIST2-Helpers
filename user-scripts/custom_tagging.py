from sist2 import Sist2Index
import sys

# Define the keyword and tag
keyword = "salary"
tag_name = "salary"
tag_color = "#00FF00"
final_tag = f"{tag_name}.{tag_color}"

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

    # Try to get the extracted text from json_data
    text = None
    if doc.json_data and isinstance(doc.json_data, dict):
        for key in ['content', 'fulltext', 'text', 'text_content', 'extracted_text']:
            if key in doc.json_data and doc.json_data[key] and isinstance(doc.json_data[key], str):
                text = doc.json_data[key]
                print(f"Found extracted text data in json_data['{key}'] for document {doc.path}. Search can be applied. ")
                break

    # Check if text was found and if keyword is in it
    if text and keyword in text.lower():
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
        print(f"Skipping document {doc.path}: No text found or '{keyword}' not present")

# Sync the tag table and commit changes
index.sync_tag_table()
index.commit()
print("Done!")
