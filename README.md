# gpt-paper-summarizer
Extract text from PDF, summarize each section w/ GPT, and provide a summarized outline of the paper

Currently, per ChatGPT:
Here's what the main block of your script does:

It gets the path to a PDF file from the command line arguments.
It extracts the text from the PDF file.
It splits the text into sections based on the split_into_sections function.
It encodes the text as a sequence of tokens using the tiktoken library's get_encoding function.
It writes the extracted text to a text file with the same name as the PDF file, but with a .txt extension.
It prints the total number of tokens in the text.
For each section in the sections list, it does the following:
It splits the section into subsections using the split_section_into_subsections function.
It combines adjacent tuples (subsections) with less than 1000 tokens until they exceed 1000 tokens using the combine_subsections function.
It initializes a counter for numbering sequential identical subheaders.
For each combined subsection in the combined_subsections list, it does the following:
If the counter is greater than 1, it updates the subheader by appending "-partX", where X is the value of the counter.
It increments the counter.
It encodes the content of the subsection as a sequence of tokens using the tiktoken library's encode function.
It removes spaces and forward slashes from the subheader to create the name of the output file for the subsection.
If the content of the subsection is not empty, it writes the content to the output file and prints a message.
It creates the name of the summary file for the subsection.
If the summary file already exists, it prints a message.
If the summary file does not exist, it generates a summary for the subsection using the generate_summary function, writes the summary to the summary file, and prints a message.
