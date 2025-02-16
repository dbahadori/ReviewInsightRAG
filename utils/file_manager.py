import json
import os


class FileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_records(self):
        # Load records from file
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON from {self.file_path}.")
                    return []
        else:
            print(f"File {self.file_path} does not exist.")
            return []
