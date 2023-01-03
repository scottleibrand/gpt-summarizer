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

import argparse
import glob
import os
import pathlib
import re
from io import StringIO

import html2text
import magic
import openai
import requests
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
# import tiktoken
from transformers import GPT2TokenizerFast

API_KEY = ''
model_engine = "text-davinci-003"
max_tokens = 3000

def main():

    # step 0: setup argument handling
    argparser = argparse.ArgumentParser()

    type_parser = argparser.add_mutually_exclusive_group(required=True)
    type_parser.add_argument('-f', '--file', help='expects single argument [path].[pdf|html]')
    type_parser.add_argument('-u', '--url', help='expects a reachable URL')

    argparser.add_argument('-l', '--language', help='expects spelled out language designator (e.g. Spanish)')
    argparser.add_argument('-b', '--base', help='specify a name to use for the output summary [omit for automatic]')
    args = argparser.parse_args()

    # STEP 0a [language stuff]:
    # i didn't really know how your language stuff worked so I just copied the functionality :)
    if args.language:
        output_language_prompt = args.language
    else:
        output_language_prompt = ''

    # STEP 1 [content acquisition]:
    # if we have a URL, go get the content and save that content locally. as mentioned in the writeup, this is a bit
    # janky because the return from download_html won't be the content itself but rather the location to the content
    # but it's not the end of the world. this will all look a lot cleaner once/if we Object-ify it. at this point
    # we do not care whether the URL takes us to a PDF or text; we let libraries figure that out both when we collect
    # and then when we open the resultant file
    # OUTCOME: saved_content

    if args.url:
        # doctype = 'article'
        saved_content = download_html(args.url, args.base)
    else: # assume we have a local file now since the arguments are mutually exclusive
        saved_content = pathlib.Path("args.file")
        if not saved_content.exists():
            raise Exception("Input file not present")

    # STEP 2 [content normalization]:
    # no matter the source format, we have our content stored, now we need to get it to text for analysis
    # OUTCOME: content

    file_type = magic.from_file(saved_content)

    if 'PDF' in file_type:
        doctype = 'paper'
        content = extract_text_from_pdf(saved_content)
    elif 'html' in file_type:
        doctype = 'article'
        content = extract_text_from_html(saved_content)
    else: # should probably make this a function call too but whatever, and i got too cute by using pathlib
        doctype = 'article'
        content = saved_content.read_text()

    output_file = str(saved_content) + '.full.txt'

    with open(output_file, 'w') as f:
        f.write(content)

    print(f"Text extracted from {saved_content} and written to {output_file}")

    # STEP 3 [tokenize text]:
    # now we have a flat text file, start to do token magic on it
    # OUTCOME: we'll take back the tokenizer object [enc] after it's applied against the content

    enc = tokenize_text(content)

    # STEP 4 [all the sections]:

    sectionize_content(content, saved_content, enc, output_language_prompt)

    # STEP 5 [construct summaries]:

    concatenate_summaries(saved_content, enc, doctype, output_language_prompt)

    # STEP 6 [generate result]:

    # Call create_html_file() to create an HTML file with the overall summary
    create_html_file(saved_content)



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
    pattern = r'(\n\nReferences[^\n]*)\n'
    match = re.search(pattern, text)
    if match:
        # Remove the "References" section and everything that follows
        text = text[:match.start()]

    # Use a regular expression to split the text into sections
    # pattern = r'\n\n(\d+[\.:]\s+[^\n]+)\n\n'
    # Match section headers that start with a number followed by a period or colon,
    # or markdown-style headers that start with one to six hash marks followed by a space
    pattern = r'\n\n(#+\s+[^\n]+|\d+[\.:]\s+[^\n]+)\n\n'
    sections = re.split(pattern, text)
    print("Found", len(sections), "sections.")

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
            # print(section)

    # Zip the section headers and content together
    sections = list(zip(headers, content))

    # print(headers)

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


def combine_subsections(subsections, enc):
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
                # current_subsection_header += header

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


def generate_summary(content, prompt, model_engine="text-davinci-003", max_tokens=3000):
    # Get the API key from the environment variable
    # ptb: if it's not set earlier in the program for convenience ;), or probably a configuration JSON if this was prod
    if not API_KEY:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    else:
        openai.api_key = API_KEY

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

def concatenate_summaries(saved_content, enc, doctype, output_language_prompt):
    # Check if the overall summary file already exists
    overall_summary_path = f"{saved_content}.overall_summary.txt"
    if os.path.exists(overall_summary_path):
        print(f"Overall summary already exists at {overall_summary_path}")
    else:
        # Read in the abstract, if it exists
        try:
            abstract_filename = glob.glob(f"{saved_content}.Title-Abstract*.full.txt")[0]
            with open(f"{abstract_filename}", 'r') as f:
                abstract = f.read()
        except IndexError:
            print(f"No abstract found for {saved_content}")
            abstract = ""
        # Read in the section summaries
        summaries = []
        summary_pattern = f"{saved_content}.*.section_summary.txt"
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
        print(
            f"Concatenated {len(summaries)} summaries into a single summary with {len(subcontent)} characters and {len(subcontent_tokens)} tokens")
        if len(subcontent_tokens) < 500:
            print(f"Concatenated subsection summaries have less than 500 tokens, reading in all summaries")
            summary_pattern = f"{saved_content}.*.summary.txt"
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
        # Generate the overall summary
        overall_summary = generate_summary(subcontent, prompt, model_engine, max_tokens)
        # Append a newline to the overall summary
        overall_summary += "\n"
        # Write the overall summary to a file
        with open(overall_summary_path, 'w') as f:
            f.write(overall_summary)
        print(f"Overall summary written to {overall_summary_path}")

def extract_text_from_html(html_path):
    # Read the HTML file
    with open(html_path, "r") as html_file:
        html = html_file.read()

    # Extract the text from the HTML
    text = html2text.html2text(html)

    return text


def create_html_file(basename):
    # Create the HTML file
    html_file = open(str(basename) + ".summary.html", "w")

    # Strip the path from the basename to get the filename
    filename = os.path.basename(basename)

    # Write the HTML header
    html_file.write("<html>\n")
    html_file.write("<head>\n")
    html_file.write("<title>" + filename + "</title>\n")
    # html_file.write("<link rel='stylesheet' type='text/css' href='style.css'>\n")
    html_file.write("</head>\n")
    html_file.write("<body>\n")
    html_file.write("<article id='" + filename + "'>\n")
    # html_file.write("<h1>" + filename + "</h1>\n")
    #html_file.write("<h1>" + "<a href='" + url + "'>" + filename + "</h1></a>\n")

    # Write the overall summary section
    html_file.write("<h2>Overall Summary</h2>\n")
    overall_summary_file = open(str(basename) + ".overall_summary.txt", "r")
    overall_summary_content = overall_summary_file.read()
    html_file.write("<p>" + overall_summary_content + "</p>\n")
    overall_summary_file.close()

    # Write the subsection summary section
    html_file.write("<h2>Subsection Summary</h2>\n")
    subsection_summary_files = glob.glob(str(basename) + ".*.summary.txt")
    subsection_summary_files.sort()
    for subsection_summary_file in subsection_summary_files:
        subsection_summary_file_handle = open(subsection_summary_file, "r")
        subsection_summary_content = subsection_summary_file_handle.read()
        html_file.write("<p>" + subsection_summary_content + "</p>\n")
        subsection_summary_file_handle.close()

    # Write the HTML footer

    #html_file.write("<a href='" + url + "'>Original URL</a>\n")  ;;killed this because I got tired
    html_file.write("</article>\n")
    html_file.write("</body>\n")
    html_file.write("</html>\n")

    # Print a message indicating that the HTML file was created
    print("Created HTML file: " + str(basename) + ".summary.html")
    # Close the HTML file
    html_file.close()


def download_html(url, base):
    base_name = base

    # validate correctly formed URL and also strip out query parameters at the same time
    url_pattern = re.compile(r"^(https?:\/\/\S+\/[^?#\s]*)")
    cleaned_url = url_pattern.search(url)
    base_from_url = cleaned_url.group(1)

    if not base_from_url:
        raise Exception("Improperly Formatted URL")

    # Get the base name from the URL, or use what the user specified (NB: this is janky, should do it correctly later
    # by using an Object and accessing its state)
    if not base:
        base_name = base_from_url.rstrip('/').split('/')[-1]
        base_name = base_name.rstrip('.pdf')

    # decide if we're going to write the output as a text file or a binary (in the case of PDF or other encoded format)
    # i changed the destination path to a user's home directory in case /tmp is not writeable by the user, feel free
    # to change, Pathlib makes things super easy and you can even verify perms etc

    source_page = requests.get(url)
    source_page_saved = pathlib.Path.home() / base_name
    source_page_saved.touch()

    if 'application' in source_page.headers['content-type']:
        source_page_saved.write_bytes(source_page.content)
    else:
        source_page_saved.write_text(source_page.text)

    # i think these are debugging only perhaps?
    print("Saved file path: " + str(source_page_saved))
    print("URL: " + url)

    return source_page_saved

def sectionize_content(text, saved_content, enc, output_language_prompt):
    text = text
    saved_content = saved_content
    enc = enc

    # Split the text into sections
    sections = split_into_sections(text)

    # Write each section to a separate text file
    for header, content in sections:
        print("Header: ", header)
        # Split the section into subsections if necessary
        subsections = split_section_into_subsections(header, content, enc)

        # Combine adjacent tuples with less than 1000 tokens until they exceed 1000 tokens
        combined_subsections = combine_subsections(subsections, enc)

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
            # print("Subheader: ",subheader)
            section_name = re.sub(r'[^a-zA-Z0-9]', '', subheader.replace('/', '-'))

            # print("Section name: ",section_name)
            output_path = str(saved_content) + "." + section_name + ".full.txt"

            if len(subcontent) == 0:
                subheader_count = subheader_count - 1
            else:
                # Write the content to the output file
                with open(output_path, 'w') as f:
                    f.write(subcontent)
                print(
                    f"{subheader} ({len(subcontent)} characters, {len(subcontent_tokens)} tokens) written to {output_path}")
                # Get the name of the summary file
                summary_path = f"{saved_content}.{section_name}.summary.txt"
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
        if len(glob.glob(f"{saved_content}.{section_number}.*.summary.txt")) < 1:
            print(f"No summary files found for section {section_number}")
        elif len(glob.glob(f"{saved_content}.{section_number}.*.summary.txt")) == 1:

            print(f"Only one summary file found for section {section_number}, promoting it to section summary")
            # Get the path of the summary file
            # print(glob.glob(f"{base_name}.{section_number}.*.summary.txt"))
            summary_path = glob.glob(f"{saved_content}.{section_number}.*.summary.txt")[0]
            # Get the path of the section summary file
            section_summary_path = f"{saved_content}.{section_name}.section_summary.txt"
            # Read the summary file and write it to the section summary file
            with open(summary_path, 'r') as f:
                summary = f.read()
            with open(section_summary_path, 'w') as f:
                f.write(summary)

            print(f"Summary promoted to section summary at {section_summary_path}")

        else:
            # Read in the section summaries
            summaries = []

            summary_pattern = f"{saved_content}.*{section_number}.summary.txt"
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
            print(
                f"Concatenated {len(summaries)} summaries into a single summary with {len(subcontent)} characters and {len(subcontent_tokens)} tokens")
            if len(subcontent_tokens) == 0:
                summary_pattern = f"{saved_content}.*.summary.txt"
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
                print(
                    f"Concatenated {len(summaries)} out of {len(summary_paths)} section summaries into a single summary with {len(subcontent)} characters and {len(subcontent_tokens)} tokens")

            # Set the prompt for the overall section summary
            prompt = f"Please provide a detailed summary of the following sections:\n{subcontent}\nPlease provide a detailed summary of the sections above.{output_language_prompt}"
            # Get the path of the overall section summary file
            section_summary_path = f"{saved_content}.{section_number}.section_summary.txt"
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

def tokenize_text(text):
    text = text

    # encode the text as a sequence of tokens
    # enc = tiktoken.get_encoding("gpt2")
    enc = GPT2TokenizerFast.from_pretrained("gpt2")

    tokens = enc.encode(text)

    print(f"Total token count: {len(tokens)}")

    return enc

if __name__ == '__main__':

    main()
