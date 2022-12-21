#!/usr/bin/env python

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

This script was written by ChatGPT with direction by Scott Leibrand,
then edited by Scott Leibrand w/ CoPilot and ChatGPT.
"""

import sys
import re
import os
import openai
import glob

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
    #pattern = r'\n\n(\d+[\.:]\s+[^\n]+)\n\n'
    # Match section headers that start with a number followed by a period or colon,
    # or markdown-style headers that start with one to six hash marks followed by a space
    pattern = r'\n\n(#+\s+[^\n]+|\d+[\.:]\s+[^\n]+)\n\n'
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

    #print(headers)

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
    headers = [f"{section_header.split('.')[0]}. Section intro"]
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

def combine_subsections(subsections):
    # Initialize the list of combined subsections
    combined_subsections = []

    # Initialize the current combined subsection
    current_subsection_header = ""
    current_subsection_content = ""
    current_subsection_tokens = 0

    # Iterate through the subsections
    for header, content in subsections:
        # Encode the content as a sequence of tokens
        tokens = enc.encode(content)

        # If the current combined subsection has less than 1000 tokens and the current subsection has less than 1000 tokens, combine them
        if current_subsection_tokens + len(tokens) < 2000 and len(tokens) < 1000:
            # Update the current combined subsection header
            if current_subsection_header == "":
                current_subsection_header = header
                current_subsection_content = header + "\n"
            else:
                if current_subsection_header != header:
                    current_subsection_content += "\n\n" + header + "\n"
                #current_subsection_header += header

            # Update the current combined subsection content
            current_subsection_content += content

            # Update the current combined subsection token count
            current_subsection_tokens += len(tokens)
        else:
            # Add the current combined subsection to the list of combined subsections
            combined_subsections.append((current_subsection_header, current_subsection_content))

            # Reset the current combined subsection
            current_subsection_header = header
            current_subsection_content = header + "\n" + content
            current_subsection_tokens = len(tokens)

    # Add the final combined subsection to the list of combined subsections
    combined_subsections.append((current_subsection_header, current_subsection_content))

    return combined_subsections

import openai
import os

def generate_summary(content, prompt, model_engine="text-davinci-003", max_tokens=3000):
    # Get the API key from the environment variable
    api_key = os.environ["OPENAI_API_KEY"]
    openai.api_key = api_key

    # Set the model to use, if not specified
    if model_engine is None:
        model_engine = "text-davinci-003"

    # Set the temperature for sampling
    temperature = 0

    # Set the max token count for the summary
    if model_engine == "text-davinci-003":
        max_tokens = 1000
    else:
        max_tokens = 500

    # Generate completions
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )

    # Get the summary from the first completion
    summary = completions.choices[0].text

    return summary

import html2text



def extract_text_from_html(html_path):
    # Read the HTML file
    with open(html_path, "r") as html_file:
        html = html_file.read()
    
    # Extract the text from the HTML
    text = html2text.html2text(html)
    
    return text

def download_html(url):
    # Strip any trailing /'s from the end of the URL
    stripped_url = url.rstrip("/")

    # Get the base name of the URL
    base_name = stripped_url.split("/")[-1]

    # Download the HTML file
    html_path = "/tmp/" + base_name + ".html"
    print("HTML path: " + html_path)
    print("URL: " + url)
    os.system("curl -s -o " + html_path + " " + url)

    return html_path

if __name__ == '__main__':
    
    model_engine = "text-davinci-003"
    max_tokens = 3000
    doctype=""
    # get the base filename of the first argument without the extension
    base_name = os.path.splitext(sys.argv[1])[0]
    
    # If the command line argument starts with http, use curl to download it to an HTML file
    if sys.argv[1].startswith("http"):
        # Get the URL from the command line arguments
        url = sys.argv[1]
        doctype="article"

        # Download the HTML file
        html_path = download_html(url)
        print(html_path)

        # Strip any trailing /'s from the end of the URL
        url = url.rstrip("/")
        # Set the base_name to a /tmp file containing the last part of the URL between /'s
        base_name = "/tmp/" + url.split("/")[-1]
        print(base_name)

        # Extract the text from the HTML file
        text = extract_text_from_html(html_path)
    # If the command line argument references a pdf file
    elif sys.argv[1].endswith(".pdf"):
        # Get the PDF file path from the command line arguments
        pdf_path = sys.argv[1]
        doctype="paper"

        # Extract the text from the PDF file
        text = extract_text_from_pdf(pdf_path)
    elif sys.argv[1].endswith(".html") or sys.argv[1].endswith(".htm"):

        # Get the HTML file path from the command line arguments
        html_path = sys.argv[1]
        doctype="article"

        # Extract the text from the HTML file
        text = extract_text_from_html(html_path)
    else:
        # Get the text file path from the command line arguments
        text_path = sys.argv[1]

        # Read the text file
        with open(text_path, "r") as text_file:
            text = text_file.read()

    # Checking if output language is set, if not set to english as default
    try:
        arg = sys.argv[2]
        output_language_prompt = "Please use "+sys.argv[2]+" language for the output."
    except IndexError:
        output_language_prompt = ""

    # Split the text into sections
    sections = split_into_sections(text)

    # Use tiktoken to encode the text as a sequence of tokens
    enc = tiktoken.get_encoding("gpt2")
    tokens = enc.encode(text)

    # Get the base name of the output file
    #base_name, _ = os.path.splitext(pdf_path)

    # Write the extracted text to the output file
    with open(base_name + ".full.txt", 'w') as f:
        f.write(text)

    print(f"Text extracted from {sys.argv[1]} and written to {base_name}.full.txt")


    print(f"Total token count: {len(tokens)}")

    # Write each section to a separate text file
    for header, content in sections:
        print("Header: ", header)
        # Split the section into subsections if necessary
        subsections = split_section_into_subsections(header, content, enc)

        # Combine adjacent tuples with less than 1000 tokens until they exceed 1000 tokens
        combined_subsections = combine_subsections(subsections)

        # Initialize the counter for numbering sequential identical subheaders
        subheader_count = 1

        # Process each combined subsection
        for subheader, subcontent in combined_subsections:
            # Update the subheader if there are multiple sequential identical subheaders
            if subheader_count > 1:
                subheader += f"-part{subheader_count}"
            subheader_count += 1

            # Use tiktoken to encode the subsection content as a sequence of tokens
            subcontent_tokens = enc.encode(subcontent)


            # Get the name of the output file
            #print("Subheader: ",subheader)
            section_name = re.sub(r'[^a-zA-Z0-9]', '', subheader.replace('/','-'))
            
            #print("Section name: ",section_name)
            output_path = f"{base_name}.{section_name}.full.txt"

            if (len(subcontent) == 0):
                subheader_count = subheader_count - 1            
            else:
                # Write the content to the output file
                with open(output_path, 'w') as f:
                    f.write(subcontent)
                print(f"{subheader} ({len(subcontent)} characters, {len(subcontent_tokens)} tokens) written to {output_path}")
                # Get the name of the summary file
                summary_path = f"{base_name}.{section_name}.summary.txt"
                # If the summary file does not exist, generate a summary
                if os.path.exists(summary_path):
                    print(f"Summary already exists at {summary_path}")
                else:
                    # Set the prompt for the summary
                    prompt = f"Please provide a detailed summary of the following section, but if the section content is mostly website context/description, just return 'Section has no content':\n{subcontent}\nPlease provide a detailed summary of the section above. If the section content is mostly website context/description, just return 'Section has no content'.{output_language_prompt}"
                    # Generate a summary for the subsection
                    summary = generate_summary(subcontent, prompt, model_engine, max_tokens)
                    # Write the summary to a summary file
                    with open(summary_path, 'w') as f:
                        f.write(summary)
                    print(f"Summary written to {summary_path}")
        
        # If there is more than one summary file matching {base_name}.*{section_number}.summary.txt, generate a combined section summary
        section_number = section_name.split('.')[0]
        if len(glob.glob(f"{base_name}.{section_number}.*.summary.txt")) < 1:
            print(f"No summary files found for section {section_number}")
        elif len(glob.glob(f"{base_name}.{section_number}.*.summary.txt")) == 1:

            print(f"Only one summary file found for section {section_number}, promoting it to section summary")
            # Get the path of the summary file
            #print(glob.glob(f"{base_name}.{section_number}.*.summary.txt"))
            summary_path = glob.glob(f"{base_name}.{section_number}.*.summary.txt")[0]
            # Get the path of the section summary file
            section_summary_path = f"{base_name}.{section_name}.section_summary.txt"
            # Read the summary file and write it to the section summary file
            with open(summary_path, 'r') as f:
                summary = f.read()
            with open(section_summary_path, 'w') as f:
                f.write(summary)

            print(f"Summary promoted to section summary at {section_summary_path}")

        else:
            # Read in the section summaries
            summaries = []
            
            summary_pattern = f"{base_name}.*{section_number}.summary.txt"
            print(f"Reading summary from {summary_pattern}")
            summary_paths = glob.glob(summary_pattern)
            summary_paths.sort(key=os.path.getmtime)  # sort file names by modification time, oldest first
            for summary_path in summary_paths:
                print(f"Reading summary from {summary_path}")
                with open(summary_path, 'r') as f:
                    summaries.append(f.read())
            # Concatenate the summaries into a single string
            subcontent = "\n\n".join(summaries)
            # Tokenize the concatenated summaries
            subcontent_tokens = enc.encode(subcontent)
            print(f"Concatenated {len(summaries)} summaries into a single summary with {len(subcontent)} characters and {len(subcontent_tokens)} tokens")
            if len(subcontent_tokens) == 0:
                summary_pattern = f"{base_name}.*.summary.txt"
                print(f"Reading summary from {summary_pattern}")
                summary_paths = glob.glob(summary_pattern)
                summary_paths.sort(key=os.path.getmtime)  # sort file names by modification time, oldest first

                summaries = []
                subcontent_tokens = []
                for summary_path in summary_paths:
                    print(f"Reading summary from {summary_path}")
                    with open(summary_path, 'r') as f:
                        summary = f.read()
                    summary_tokens = enc.encode(summary)
                    if len(subcontent_tokens) + len(summary_tokens) > max_tokens:
                        break
                    summaries.append(summary)
                    subcontent_tokens += summary_tokens
                # Concatenate the summaries into a single string
                subcontent = "\n\n".join(summaries)
                # Tokenize the concatenated summaries
                subcontent_tokens = enc.encode(subcontent)
                print(f"Concatenated {len(summaries)} out of {len(summary_paths)} section summaries into a single summary with {len(subcontent)} characters and {len(subcontent_tokens)} tokens")

            # Set the prompt for the overall section summary
            prompt = f"Please provide a detailed summary of the following sections:\n{subcontent}\nPlease provide a detailed summary of the sections above.{output_language_prompt}"
            # Get the path of the overall section summary file
            section_summary_path = f"{base_name}.{section_number}.section_summary.txt"
            # If the overall section summary file does not exist, generate a summary
            if os.path.exists(section_summary_path):
                print(f"Overall section summary already exists at {section_summary_path}")
            else:
                # Generate the overall section summary
                section_summary = generate_summary(content, prompt, model_engine, max_tokens)
                # Write the overall section summary to a file
                with open(section_summary_path, 'w') as f:
                    f.write(section_summary)
                print(f"Overall section summary written to {section_summary_path}")



            
    # Check if the overall summary file already exists
    overall_summary_path = f"{base_name}.overall_summary.txt"
    if os.path.exists(overall_summary_path):
        print(f"Overall summary already exists at {overall_summary_path}")
    else:
        # Read in the abstract, if it exists
        try:
            abstract_filename=glob.glob(f"{base_name}.Title-Abstract*.full.txt")[0]
            with open(f"{abstract_filename}", 'r') as f:
                abstract = f.read()
        except IndexError:
            print(f"No abstract found for {base_name}")
            abstract = ""
        # Read in the section summaries
        summaries = []
        summary_pattern = f"{base_name}.*.section_summary.txt"
        for summary_path in glob.glob(summary_pattern):
            with open(summary_path, 'r') as f:
                summaries.append(f.read())
        # Concatenate the abstract and summaries into a single string
        subcontent = abstract + "\n\n" + "\n\n".join(summaries)
        # Tokenize the concatenated abstract and summaries
        subcontent_tokens = enc.encode(subcontent)
        for summary in summaries:
            summary_tokens = enc.encode(summary)
            if len(subcontent_tokens) + len(summary_tokens) > max_tokens:
                print(f"Exceeded {max_tokens} tokens, stopping concatenation of summaries")
                break
            subcontent += summary + "\n\n"
            subcontent_tokens += summary_tokens
        print(f"Concatenated {len(summaries)} summaries into a single summary with {len(subcontent)} characters and {len(subcontent_tokens)} tokens")
        if len(subcontent_tokens) < 500:
            print(f"Concatenated subsection summaries have less than 500 tokens, reading in all summaries")
            summary_pattern = f"{base_name}.*.summary.txt"
            for summary_path in glob.glob(summary_pattern):
                with open(summary_path, 'r') as f:
                    summaries.append(f.read())
            for summary in summaries:
                summary_tokens = enc.encode(summary)
                if len(subcontent_tokens) + len(summary_tokens) > max_tokens:
                    print(f"Exceeded {max_tokens} tokens, stopping concatenation of summaries")
                    break
                subcontent += summary + "\n\n"
                subcontent_tokens += summary_tokens


        # Set the prompt for the overall summary
        prompt = f"Please provide a detailed summary of the following {doctype}, based on its abstract and summaries of each section:\n{subcontent}\nPlease provide a detailed summary of the {doctype} described above, based on the provided abstract/introduction and summaries of each section.{output_language_prompt}"
                #
        # Generate the overall summary
        overall_summary = generate_summary(subcontent, prompt, model_engine, max_tokens)
        # Append a newline to the overall summary
        overall_summary += "\n"
        # Write the overall summary to a file
        with open(overall_summary_path, 'w') as f:
            f.write(overall_summary)
        print(f"Overall summary written to {overall_summary_path}")
