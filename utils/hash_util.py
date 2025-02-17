import hashlib
from typing import Dict, Any, Optional, List

class HashUtil:
    @staticmethod
    def compute_hash(text: str) -> str:
        """Compute the SHA-256 hash of the given text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def should_update(existing_hash: str, new_hash: str) -> bool:
        """Determine if an update is needed based on hash comparison."""
        return existing_hash != new_hash

    @staticmethod
    def compute_dict_hash(data: Dict[str, Any], exclude_fields: Optional[List[str]] = None) -> str:
        """Compute the SHA-256 hash of the given dictionary, excluding specified fields."""
        if exclude_fields is None:
            exclude_fields = []

        hasher = hashlib.sha256()
        for key, value in sorted(data.items()):
            if key not in exclude_fields:
                hasher.update(str(key).encode('utf-8'))
                hasher.update(str(value).encode('utf-8'))
        return hasher.hexdigest()

    @staticmethod
    def add_hash_to_field(data: Dict[str, Any], field_name: str = "metadata",
                          fields_to_hash: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Add hash of the specified fields to the specified field in the data dictionary.
        If no fields are specified, use all fields at the same level excluding the specified field.
        """
        if fields_to_hash is None:
            # Use all fields in data except the specified field
            fields_to_hash = [key for key in data.keys() if key != field_name]

        content = {field: data.get(field) for field in fields_to_hash}
        hashed_content = HashUtil.compute_dict_hash(content)
        if field_name not in data:
            data[field_name] = {}
        data[field_name]["hash"] = hashed_content
        return data

    @staticmethod
    def save_hash_to_store(hash_store, id: str, hash: str) -> None:
        """
        Save the hash to the hash store with the given ID.
        """
        hash_store.save_hash(id, hash)

    @staticmethod
    def load_hash_from_store(hash_store, id: str) -> Optional[str]:
        """
        Load the hash from the hash store with the given ID.
        """
        return hash_store.load_hash(id)

    @staticmethod
    def update_hash_in_store_if_needed(hash_store, id: str, new_hash: str) -> bool:
        """
        Update the hash store if the new hash differs from the existing hash.
        Returns True if an update is needed and was successful, otherwise False.
        """
        try:
            existing_hash = HashUtil.load_hash_from_store(hash_store, id)
            if existing_hash is None or HashUtil.should_update(existing_hash, new_hash):
                try:
                    HashUtil.save_hash_to_store(hash_store, id, new_hash)
                    return True
                except Exception as e:
                    print(f"An error occurred while saving the hash: {e}")
                    raise e
            return False
        except Exception as e:
            print(f"An error occurred while loading the hash: {e}")
            raise e
