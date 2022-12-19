# gpt-summarizer
### Extract text, summarize each section w/ GPT, and provide a summarized outline of a paper/article

This script extracts text from a given file or URL and splits it into sections. It then uses a tiktoken to encode the text as a sequence of tokens. It writes the extracted text to an output file and writes each section to a separate text file. It also generates a summary for each subsection and writes the summary to a summary file. If there are multiple summary files for a section, it generates a combined section summary.

The script expects a PDF or HTML file path, or an HTML URL, to be passed as a command line argument. It extracts the text from the PDF file, splits the text into sections, and uses the tiktoken.get_encoding function to encode the text as a sequence of tokens using the "gpt2" encoding. It writes the extracted text to an output file using the base_name of the file and the .txt extension.

It processes each section by first using the split_section_into_subsections function to split the section into subsections based on HTML section headings or numbered section headings. If necessary, it further splits any subsections into paragraphs and recombine adjacent ones until they exceed 1000 tokens. It processes each resulting section/part with InstructGPT (text-davinci-003) to generate a summary, and writes each section summary to a summary file. If there are multiple summary files for a section, it generates a combined section summary by concatenating the summaries of the individual subsections.

It then performs one final round of summarization across all the lower-level summaries, to produce an overall summary of the paper/article.

The intended use is that both the overall summary and the subsection summaries (in order) are worth reading to determine whether to spend the time reading the entire article/paper, or specific sections of it.

## Usage

tl;dr:
```
pip install pdfminer
pip install html2text
pip install tiktoken
pip install openai
export OPENAI_API_KEY=<your OpenAI API key>
python summarize.py paper.pdf
python summarize.py https://path/to/article
```

### Usage details:

Requires an OpenAI API key:
 - If you haven't already done so to get access to ChatGPT, sign up for an account at OpenAI.com
 - Go to https://openai.com/api/ and Log in
 - Go to https://beta.openai.com/account/api-keys
 - Create a new secret key
 
This OPENAI_API_KEY should be set as an environment variable:
`export OPENAI_API_KEY=<your OpenAI API key>`

For now, you also have to manually pip install pdfminer, html2text, tiktoken, and openai. (I'd welcome a PR to get this repo set up to use setup requirements to support `pip install -e .`)


## Examples
```
~/src/gpt-summarizer $ ./summarize.py https://ourworldindata.org/ai-impact
HTML path: /tmp/ai-impact.html
URL: https://ourworldindata.org/ai-impact
/tmp/ai-impact.html
/tmp/ai-impact
Text extracted from https://ourworldindata.org/ai-impact and written to /tmp/ai-impact.full.txt
Total token count: 8038
Header:  Title-Abstract
Title-Abstract (10563 characters, 2493 tokens) written to /tmp/ai-impact.TitleAbstract.full.txt
Summary written to /tmp/ai-impact.TitleAbstract.summary.txt
No summary files found for section TitleAbstract
Header:  ##### A future of human-level or transformative AI?
##### A future of human-level or transformative AI? (1140 characters, 258 tokens) written to /tmp/ai-impact.AfutureofhumanlevelortransformativeAI.full.txt
Summary written to /tmp/ai-impact.AfutureofhumanlevelortransformativeAI.summary.txt
No summary files found for section AfutureofhumanlevelortransformativeAI
Header:  #### What is at stake as artificial intelligence becomes more powerful?
#### What is at stake as artificial intelligence becomes more powerful? (4677 characters, 1059 tokens) written to /tmp/ai-impact.Whatisatstakeasartificialintelligencebecomesmorepowerful.full.txt
Summary written to /tmp/ai-impact.Whatisatstakeasartificialintelligencebecomesmorepowerful.summary.txt
No summary files found for section Whatisatstakeasartificialintelligencebecomesmorepowerful
Header:  #### How can we make sure that the development of AI goes well?
#### How can we make sure that the development of AI goes well? (3427 characters, 792 tokens) written to /tmp/ai-impact.HowcanwemakesurethatthedevelopmentofAIgoeswell.full.txt
Summary written to /tmp/ai-impact.HowcanwemakesurethatthedevelopmentofAIgoeswell.summary.txt
No summary files found for section HowcanwemakesurethatthedevelopmentofAIgoeswell
Header:  ### Endnotes
### Endnotes (10116 characters, 2573 tokens) written to /tmp/ai-impact.Endnotes.full.txt
Summary written to /tmp/ai-impact.Endnotes.summary.txt
No summary files found for section Endnotes
Header:  ### Reuse this work freely
### Reuse this work freely (2764 characters, 853 tokens) written to /tmp/ai-impact.Reusethisworkfreely.full.txt
Summary written to /tmp/ai-impact.Reusethisworkfreely.summary.txt
No summary files found for section Reusethisworkfreely
No abstract found for /tmp/ai-impact
Concatenated 0 summaries into a single summary with 2 characters and 1 tokens
Concatenated subsection summaries have less than 500 tokens, reading in all summaries
Overall summary written to /tmp/ai-impact.overall_summary.txt
~/src/gpt-summarizer $
```

