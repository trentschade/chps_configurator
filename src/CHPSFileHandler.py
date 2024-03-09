import os
import re
import xml.etree.ElementTree as ET

class XMLOperation:
    def __init__(self, function, **kwargs):
        """
        Initialize an XMLOperation instance.

        :param function: The operation function to be executed.
        :param kwargs: Keyword arguments for the operation function.
        """
        self.function = function
        self.kwargs = kwargs

    def execute(self, xml_handler):
        """Execute the operation function with the provided XMLHandler instance."""
        self.function(xml_handler, **self.kwargs)

class XMLHandler:
    def __init__(self):
        self.tree = None
        self.root = None

    def open(self, filepath):
        """Open an XML file and parse its structure."""
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()

    def search(self, tag):
        """Search for elements by tag."""
        return self.root.findall(tag)

    def add_element(self, parent_tag, element_tag, element_text):
        """Add a new element to a parent element."""
        parents = self.search(parent_tag)
        for parent in parents:
            new_element = ET.Element(element_tag)
            new_element.text = element_text
            parent.append(new_element)

    def update_element(self, tag, new_text):
        """Update the text of elements by tag."""
        elements = self.search(tag)
        for element in elements:
            element.text = new_text

    def remove_element(self, tag):
        """Remove elements by tag."""
        for parent in self.root.findall('.//'):
            for element in parent.findall(tag):
                parent.remove(element)

    def write(self, filepath):
        """Write the XML structure back to a file."""
        self.tree.write(filepath)

    @staticmethod
    def search_files(directory, pattern):
        """Search for files in a directory that match a regular expression."""
        matched_files = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if re.search(pattern, filename):
                    matched_files.append(os.path.join(root, filename))
        return matched_files

    def process_files(self, directory, pattern, operations):
        """Process all files matching the pattern in the given directory with a list of operations."""
        matched_files = self.search_files(directory, pattern)
        for filepath in matched_files:
            self.open(filepath)
            for operation in operations:
                operation.execute(self)  # Execute each operation's function
            self.write(filepath)

# Example operation functions
def add_element(xml_handler, parent_tag, element_tag, element_text):
    xml_handler.add_element(parent_tag, element_tag, element_text)

def update_element(xml_handler, tag, new_text):
    xml_handler.update_element(tag, new_text)

def remove_element(xml_handler, tag):
    xml_handler.remove_element(tag)

# Example usage
if __name__ == "__main__":
    xml_handler = XMLHandler()
    directory = '/path/to/directory'
    pattern = r'.*\.xml$'  # Regular expression to match XML files

    operations = [
        XMLOperation(add_element, parent_tag='parentTag', element_tag='newChild', element_text='Child text'),
        XMLOperation(update_element, tag='childToUpdate', new_text='New text value'),
        XMLOperation(remove_element, tag='childToRemove')
    ]

    xml_handler.process_files(directory, pattern, operations)
