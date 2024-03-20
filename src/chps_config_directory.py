# chps_config_directory
import os

class CHPSDirectoryManager:
    def __init__(self):
        self._cwd = None
        self._chps_root = None
        
    def __str__(self):
        return f'TEST'
        
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

if __name__ == "__main__":
    manager = CHPSDirectoryManager()
    
    # Setting values
    manager.cwd = os.getcwd()
    manager.chps_root = "/test/data/TIR-CHPS-Oper-Config"
    
    # Getting values
    print("CWD:", manager.cwd)
    print("CHPS Root Directory:", manager.chps_root)
