from pathlib import Path

class PathUtil:
    @staticmethod
    def get_project_base_path(marker: str =".git") -> Path:
        """
        Navigate up the directory tree to find the project base path by looking for a specific marker.

        :param marker: The file or directory that indicates the project base path (e.g., '.git', 'setup.py').
        :return: The path to the project base path.
        """
        current_path = Path(__file__).resolve().parent
        while current_path != current_path.root:
            if (current_path / marker).exists():
                return current_path
            current_path = current_path.parent
        raise FileNotFoundError(f"Marker '{marker}' not found in any parent directories")

    @staticmethod
    def construct_path(base_path: Path, *args) -> Path:
        """
        Construct a path relative to the given base path.

        :param base_path: The base path to start from.
        :param args: Path components to be appended to the base path.
        :return: The constructed Path object.
        """
        return base_path.joinpath(*args)

    @staticmethod
    def create_directory(path: Path) -> None:
        """
        Create a directory if it does not exist.

        :param path: The Path object for the directory to be created.
        """
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_file(file_path: Path) -> str:
        """
        Read the contents of a file.

        :param file_path: The Path object for the file to be read.
        :return: The contents of the file as a string.
        """
        with file_path.open('r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def write_file(file_path: Path, content: str) -> None:
        """
        Write content to a file.

        :param file_path: The Path object for the file to be written to.
        :param content: The content to be written to the file.
        """
        with file_path.open('w', encoding='utf-8') as file:
            file.write(content)

