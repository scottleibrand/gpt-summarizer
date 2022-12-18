#!/usr/bin/python

"""
This script contains functions for extracting text from a PDF file, splitting
the text into sections, and splitting sections into subsections. The
extract_text_from_pdf() function takes in a file path to a PDF and returns a
string of the extracted text. The split_into_sections() function takes in a
string of text and uses a regular expression to split it into a list of tuples,
where each tuple contains a section header and the corresponding text. The
split_section_into_subsections() function takes in a section header, the
corresponding text, and an encoder object and splits the section into smaller
parts, each of which is returned as a tuple containing a subsection header and
the corresponding text. The split_subsection_into_paragraphs() function takes
in a subsection header, the corresponding text, the encoder object, and a
maximum number of tokens and splits the subsection into smaller parts, each of
which is returned as a tuple containing a paragraph header and the
corresponding text.
"""

import sys
import re
import os


import tiktoken
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

def extract_text_from_pdf(pdf_path):
    """Extracts the text from a PDF file and returns it as a string.

    Parameters:
    pdf_path (str): The file path to the PDF file.

    Returns:
    str: The extracted text.
    """
    with open(pdf_path, 'rb') as fh:
        # Create a PDF resource manager object that stores shared resources
        rsrcmgr = PDFResourceManager()

        # Create a StringIO object to store the extracted text
        output = StringIO()

        # Create a TextConverter object to convert PDF pages to text
        device = TextConverter(rsrcmgr, output, laparams=LAParams())

        # Create a PDF page interpreter object
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Process each page contained in the PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            interpreter.process_page(page)

        # Get the extracted text as a string and close the StringIO object
        text = output.getvalue()
        output.close()

        # Close the PDF file and text converter objects
        device.close()

    # Remove ^L page breaks from the text
    text = text.replace('\x0c', '\n')

    return text


def split_into_sections(text):
    """Splits a string of text into a list of tuples, where each tuple contains a section header and the corresponding text.

    Parameters:
    text (str): The input text to split into sections.

    Returns:
    list: A list of tuples, where each tuple contains a section header and the corresponding text.
    """
    # Use a regular expression to match the "References" section
    pattern = r'(References[^\n]*)\n'
    match = re.search(pattern, text)
    if match:
        # Remove the "References" section and everything that follows
        text = text[:match.start()]

    # Use a regular expression to split the text into sections
    #pattern = r'\n\n((?:\d+[\.:]|(?:Introduction|Methods|Materials and Methods|Results|Discussion|References))\s+[^\n]+)\n\n'
    pattern = r'\n\n(\d+[\.:]\s+[^\n]+)\n\n'
    sections = re.split(pattern, text)

    # Extract the section headers and their corresponding text
    headers = ["Title-Abstract"]
    content = []
    for i, section in enumerate(sections):
        if i % 2 == 0:
            # This is a section of content
            content.append(section)
        else:
            # This is a section header
            headers.append(section)

    # Zip the section headers and content together
    sections = list(zip(headers, content))

    print(headers)

    return sections

def split_section_into_subsections(section_header, section_content, enc, max_tokens=3000):
    """Splits a section of text into smaller parts, each of which is returned
    as a tuple containing a subsection header and the corresponding text.

    Parameters:
    section_header (str): The header for the section to be split.
    section_content (str): The content of the section to be split.
    enc (object): An encoder object used to encode the section content as a sequence of tokens.
    max_tokens (int, optional): The maximum number of tokens allowed in each subsection. Default is 3000.

    Returns:
    list: A list of tuples, where each tuple contains a subsection header and the corresponding text.
    """
    # Encode the section content as a sequence of tokens
    tokens = enc.encode(section_content)

    if len(tokens) <= max_tokens:
        # The section does not need to be split into subsections
        return [(section_header, section_content)]

    # Split the section into numbered subsections
    pattern = r'\n\n(\d+\.\d+[\.:]\s+[^\n]+)\n\n'
    subsections = re.split(pattern, section_content)

    # Extract the subsection headers and their corresponding text
    headers = [f"{section_header.split('.')[0]}. Section summary"]
    content = []
    for i, subsection in enumerate(subsections):
        if i % 2 == 0:
            # This is a subsection of content
            content.append(subsection)
        else:
            # This is a subsection header
            headers.append(subsection)

    # Zip the subsection headers and content together
    subsections = list(zip(headers, content))


    # Split any subsections that are still too long into smaller parts
    result = []
    for header, content in subsections:
        parts = split_subsection_into_paragraphs(header, content, enc, max_tokens)
        result.extend(parts)

    return result

    #return subsections

def split_subsection_into_parts_broken(subsection_header, subsection_content, enc, max_tokens=3000):
    # Encode the subsection content as a sequence of tokens
    tokens = enc.encode(subsection_content)

    if len(tokens) <= max_tokens:
        # The subsection does not need to be split into parts
        return [(subsection_header, subsection_content)]

    # Split the subsection into parts
    start = 0
    parts = []
    while start < len(tokens):
        # Calculate the size of the next part
        end = start + max_tokens

        # Find the nearest newline boundary within the part
        print(enc)
        while end < len(tokens) and tokens[end] != enc.encoder['\n']:
            end += 1

        # Extract the part
        part_tokens = tokens[start:end]
        part_content = enc.decode(part_tokens)

        # Add the part to the list of parts
        parts.append((subsection_header, part_content))

        # Update the start index
        start = end + 1

    return parts

def split_subsection_into_paragraphs(subsection_header, subsection_content, enc, max_tokens=3000):
    # Encode the subsection content as a sequence of tokens
    tokens = enc.encode(subsection_content)

    if len(tokens) <= max_tokens:
        # The subsection does not need to be split into parts
        return [(subsection_header, subsection_content)]

    # Split the subsection into parts
    start = 0
    parts = []
    while start < len(tokens):
        # Calculate the size of the next part
        end = start + max_tokens

        # Find the nearest newline boundary within the part
        newline_pos = subsection_content[start:end].find('\n\n')
        if newline_pos != -1:
            end = start + newline_pos

        # Extract the part
        part_tokens = tokens[start:end]
        part_content = enc.decode(part_tokens)

        # Add the part to the list of parts
        parts.append((subsection_header, part_content))

        # Update the start index
        start = end + 2

    return parts



if __name__ == '__main__':
    # Get the PDF file path from the command line arguments
    pdf_path = sys.argv[1]

    # Extract the text from the PDF file
    text = extract_text_from_pdf(pdf_path)

    # Split the text into sections
    sections = split_into_sections(text)

    # Use tiktoken to encode the text as a sequence of tokens
    enc = tiktoken.get_encoding("gpt2")
    tokens = enc.encode(text)

    # Get the base name of the output file
    base_name, _ = os.path.splitext(pdf_path)

    # Write the extracted text to the output file
    with open(base_name + ".txt", 'w') as f:
        f.write(text)

    print(f"Text extracted from {pdf_path} and written to {base_name}.txt")


    print(f"Total token count: {len(tokens)}")


    # Write each section to a separate text file
    for header, content in sections:
        # Split the section into subsections if necessary
        subsections = split_section_into_subsections(header, content, enc)

        # Process each subsection
        for subheader, subcontent in subsections:
            # Use tiktoken to encode the content as a sequence of tokens
            tokens = enc.encode(subcontent)

            # Get the name of the output file
            section_name = subheader.lower().replace(' ', '').replace('/','')
            output_path = f"{base_name}.{section_name}.txt"

            # Write the content to the output file
            with open(output_path, 'w') as f:
                f.write(subcontent)

            print(f"{subheader} ({len(subcontent)} characters, {len(tokens)} tokens) written to {output_path}")

