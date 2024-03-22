# Test using chps_configurator to select multiple reservoir releases.

import sys
sys.path.append('../src')

import os
import zipfile
from bs4 import BeautifulSoup
from chps_config_directory import CHPSDirectoryManager

manager = CHPSDirectoryManager()

# Setting values
manager.chps_root = "TIR-CHPS-Oper-Config"

# Getting values
print("CWD:", manager.cwd)
print("CHPS Root Directory:", manager.chps_root)

# Example usage:
directory_name = manager.chps_root
found_directory = manager.find_directory(directory_name)
if found_directory:
    print(f"Found {directory_name} at: {found_directory}")
else:
    print(f"{directory_name} not found.")

def get_relative_path(additional_path):
    # Get the path of the current file
    current_path = os.path.dirname(__file__)

    # Create a path to the test file relative to the current path
    return os.path.join(current_path, additional_path)

# Open the zip file
with zipfile.ZipFile('/gdrive/My Drive/TIR-CHPS-Oper-Config.zip', 'r') as zip_ref:
    # Find the XML file with "dlyw2" in the name
    for file_name in zip_ref.namelist():
        if 'DLYW2' in file_name and file_name.endswith('.xml'):
            # Extract the XML file
            zip_ref.extract(file_name, 'temp_folder/')

            # Open the extracted XML file
            with open('temp_folder/' + file_name, 'r') as xml_file:
                # Parse the XML file
                soup = BeautifulSoup(xml_file, 'xml')

                # Find all parent elements that contain the string "SQIN"
                parent_elements = [element.parent for element in soup.find_all(string='SQIN')]

                # Print each parent element
                for element in parent_elements:
                    print(element)

            # Delete the temporary folder
            # shutil.rmtree('temp_folder/')
            
            
if __name__ == '__main__':
    # get a path to the chps_config test environment
    path_to_config = 'test/data/'
    relative_path = get_relative_path(path_to_config)
    
    # Instatiate an object that deals with the CHPS file structure.
    


print("after __name__ guard")