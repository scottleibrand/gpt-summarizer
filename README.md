# gpt-paper-summarizer
Extract text from PDF, summarize each section w/ GPT, and provide a summarized outline of the paper

Per ChatGPT:
This script extracts text from a given PDF file and splits it into sections. It then uses a tiktoken to encode the text as a sequence of tokens. It writes the extracted text to an output file and writes each section to a separate text file. It also generates a summary for each subsection and writes the summary to a summary file. If there are multiple summary files for a section, it generates a combined section summary.

The script expects a PDF file path to be passed as a command line argument. It uses the extract_text_from_pdf function to extract the text from the PDF file, and the split_into_sections function to split the text into sections. It then uses the tiktoken.get_encoding function to encode the text as a sequence of tokens using the "gpt2" encoding. It writes the extracted text to an output file using the base_name of the PDF file and the .txt extension.

It processes each section by first using the split_section_into_subsections function to split the section into subsections. It then uses the combine_subsections function to combine adjacent tuples with less than 1000 tokens until they exceed 1000 tokens. It processes each combined subsection by using the generate_summary function to generate a summary, and writing the summary to a summary file. If there are multiple summary files for a section, it generates a combined section summary by concatenating the summaries of the individual subsections.

Usage:
```
export OPENAI_API_KEY=<your OpenAI API key>
python summarize-paper.py paper.pdf
```
