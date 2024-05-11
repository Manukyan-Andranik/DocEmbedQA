import re  
from docx import Document  
import pdfplumber  
import docx  
import pandas as pd  

class TextSplitter:
    def __init__(self, chunk_size=500, chunk_overlap=100, separator=["\n\n", "\n \n"], length_function=len):
        """
        Initialize the TextSplitter class with default parameters and separator.

        Parameters:
        - chunk_size: Size of each chunk to be split into.
        - chunk_overlap: Number of characters to overlap between chunks.
        - separator: List of strings to be used as separators.
        - length_function: Function to calculate the length of the text.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if isinstance(separator, list):
            self.separator = "|".join(separator)  # Convert list of separators into a regex pattern
        else:
            self.separator = separator
        self.length_function = length_function

    def read(self, input_file):
        """
        Read text content from different types of files.

        Parameters:
        - input_file: Path to the input file.

        Returns:
        - text_content: Extracted text content from the file.
        """
        text_content = ""
        if input_file.endswith(".txt"):  # Read from a text file
            with open(input_file, "r") as file:
                text_content = file.read()
        elif input_file.endswith(".pdf"):  # Read from a PDF file
            pdf = pdfplumber.open(input_file)
            for page in pdf.pages:
                text = page.extract_text()
                text_content += text + "\n"
            pdf.close()
        elif input_file.endswith(".docx"):  # Read from a Word document
            document = Document(input_file)
            for para in document.paragraphs:
                text_content += para.text
        elif input_file.endswith(".csv"):  # Read from a CSV file
            data = pd.read_csv(input_file)
            cols = data.columns.to_list()
            if "Unnamed: 0" in cols:
                cols.remove("Unnamed: 0")
                cols.remove("model")
            text_content = ""
            for _, row in data.iterrows():
                row_text = " ".join([f"{c}: {row[c]}" for c in cols])
                text_content += "\n\n" + row_text.replace("\n", " ")
        else:
            return "Uncorrect file"  # Return an error message for unsupported file types
        return text_content

    def read_splitted(self, input_file):
        """
        Read text content and split it into chunks based on predefined separator and size.

        Parameters:
        - input_file: Path to the input file.

        Returns:
        - result: List of text chunks after splitting.
        """
        text = self.read(input_file)
        splited_by_separator = re.split(self.separator, text)  # Split text by the separator
        result = []
        for chunk in splited_by_separator:
            if self.length_function(chunk) > self.chunk_size:
                start = 0
                while start < self.length_function(chunk):
                    end = start + self.chunk_size
                    if end < self.length_function(chunk):
                        if chunk[end] != " ":
                            while chunk[end] != " ":
                                end -= 1
                        result.append(chunk[start:end].strip())
                        start = end - self.chunk_overlap
                        while start < self.length_function(chunk) and chunk[start] != ' ':
                            start += 1
                    else:
                        if (chunk[start:].strip()) != "":
                            result.append(chunk[start:].strip())
                        start += self.chunk_size - self.chunk_overlap
                        if self.length_function(chunk) - start < self.chunk_overlap:
                            if start > end:
                                start = end
                            else:
                                break
            else:
                if (chunk.strip()) != "":
                    result.append(chunk.strip())
        return result
