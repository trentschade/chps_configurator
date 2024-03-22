# chps_config_directory
import os

class CHPSDirectoryManager:
    def __init__(self):
        self._cwd = os.getcwd()
        self._chps_root = None
        
    def __str__(self):
        return f'CHPSDirectoryManager - chps_root: {self.__chps_root}'
        
    @property
    def cwd(self):
        return self._cwd
    
    @cwd.setter
    def cwd(self, value):
        self._cwd = self._normalize_path(value)

    @property
    def chps_root(self):
        return self._chps_root
        
    @chps_root.setter
    def chps_root(self, value):
        self._chps_root = self._normalize_path(value)

    def _normalize_path(self, path):
        return os.path.normpath(path)

    def find_directory(self, name, start=None):
        """
        Search for a directory both upwards and downwards from the current working directory.

        Args:
            name (str): The name of the directory to search for.
            start (str, optional): The directory path to start the search from. If not provided, starts from the current working directory.

        Returns:
            str or None: Returns the path of the found directory if found, else None.
        """
        # Start from the provided directory or the current working directory
        if start is None:
            start = os.getcwd()
            print(f"start: {start}")

        # Search upwards one level from the start directory
        parent_dir = os.path.dirname(start)
        print(f"parent_dir: {parent_dir}")
        for root, dirs, _ in os.walk(parent_dir):
            if '.git' in dirs:
                dirs.remove('.git')
            for directory in dirs:
                print(f"directory: {directory}")
                if name in os.path.join(root, directory):
                    return os.path.join(root,name)

        # Search downwards from the start directory
        for root, dirs, _ in os.walk(start):
            if name in dirs:
                return os.path.join(root, name)

        # If not found, return None
        return None

if __name__ == "__main__":
    manager = CHPSDirectoryManager()
    
    # Setting values
    manager.cwd = os.getcwd()
    manager.chps_root = "/test/data/TIR-CHPS-Oper-Config"
    
    # Getting values
    print("CWD:", manager.cwd)
    print("CHPS Root Directory:", manager.chps_root)
