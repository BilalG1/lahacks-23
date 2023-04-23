import os 
from typing import Any, List
from pydantic import BaseModel
import json

# I think this is automatically transformed into the required   
file_structure = {
  "filename": "main",
  "content": None,
  "children":[
    {
      "filename": "child 1",
      "content": "some txt",
      "children": []
    },
    {
      "filename":"subdir",
      "content": None,
      "children": [
        {
            "filename": "subdir-child",
            "content": "la hacks",
            "children": []
        }
      ]
    }
  ]
}


class FileNode(BaseModel):
    filename: str
    content: str = None
    children: List[Any] = []

def json_to_file_node(json_obj):
    filename = json_obj['filename']
    content = json_obj.get('content')
    children = [json_to_file_node(child) for child in json_obj['children']]
    return FileNode(filename=filename, content=content, children=children)

root_node = json_to_file_node(file_structure)

def process_file_node(node, current_path):
    new_path = os.path.join(current_path, node.filename)
    if node.content is None:
        os.makedirs(new_path)
    else:
        with open(new_path, "w") as f:
            f.write(node.content)
    for child in node.children:
        process_file_node(child, new_path)

local_shared_path = "./USRFILES"

process_file_node(root_node, local_shared_path)