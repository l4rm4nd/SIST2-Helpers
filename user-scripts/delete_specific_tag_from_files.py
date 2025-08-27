from sist2 import Sist2Index, Sist2Document
import sys

index = Sist2Index(sys.argv[1])
del_tag = "tag-to-delete"

print("Processing docs....")
for doc in index.document_iter():
    if "tag" in doc.json_data:
        if del_tag in doc.json_data["tag"]:
            doc.json_data["tag"].remove(del_tag)
            print("Removed tag from: %s" % doc.json_data["name"])

print("Syncing the tag table....")
index.sync_tag_table()

print("Committing changes....")
index.commit()
