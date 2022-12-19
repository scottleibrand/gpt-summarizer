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

### Summary of OurWorldInData AI Impact
https://ourworldindata.org/ai-impact

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

https://github.com/scottleibrand/gpt-summarizer/blob/main/examples/ai-impact.overall_summary.txt

#### Overall Summary

This article discusses the potential implications of artificial intelligence (AI) becoming a reality. It explains why it is difficult to take the prospect of a world transformed by AI seriously, and how to develop an idea of what the future of AI might look like. It compares the potential of transformative AI to the agricultural and industrial revolutions, and suggests that it could represent the introduction of a similarly significant general-purpose technology. The article also looks at the advantages and disadvantages of comparing machine and human intelligence, and introduces the concept of transformative AI, which is defined by the impact this technology would have on the world. It is noted that transformative AI could be developed before human-level AI, and that the timeline for when either of these levels of AI might be achieved is difficult to predict.

The article also looks at the potential risks and benefits of AI becoming more powerful. It is clear that AI can already cause harm when used maliciously, such as in politically-motivated disinformation campaigns or to enable mass surveillance. AI can also cause unintended harm, such as when an AI system falsely accused 26,000 parents of making fraudulent claims for child care benefits in the Netherlands. As AI becomes more powerful, the potential negative impacts could become much larger, such as mass labor displacement, extreme concentrations of power and wealth, and totalitarianism. Additionally, there is the risk of an AI system escaping human control and harming humans, known as the alignment problem. This risk is difficult to foresee and prevent, and could lead to an extreme catastrophe. On the other hand, AI could lead to positive developments such as cleaner energy, the replacement of unpleasant work, and better healthcare. The stakes are high with this technology, and reducing the negative risks and solving the alignment problem could mean the difference between a healthy, flourishing, and wealthy future for humanity – and the destruction of the same.

The article also looks at the difference between human-level AI and transformative AI, and the potential timeline for when either of these levels of AI might be achieved. It is noted that transformative AI could be developed before human-level AI, and that the timeline for when either of these levels of AI might be achieved is difficult to predict. Additionally, the article provides information about the licenses and permissions associated with Our World in Data's visualizations, data, code, and articles. Finally, the article looks at the concept of human-level AI, which is defined as a software system that can carry out at least 90% or 99% of all economically relevant tasks that humans carry out. It also looks at the closely related terms Artificial General Intelligence, High-Level Machine Intelligence, Strong AI, or Full AI, which are sometimes defined in similar, yet different ways. The section also looks at the difficulty of comparing machine and human intelligence, and the potential risks of AI systems, such as AI-enabled disinformation campaigns and mass surveillance by governments. It also looks at the incentives for developing powerful AI, and the potential for it to lead to positive developments. Finally, the section looks at the early warnings of Alan Turing and Norbert Wiener about the alignment problem, and Toby Ord's projection that AI could be developed by 2040.

#### Section Summaries

`ls -rt *summary.txt | while read file; do echo -n $file; cat $file; echo; echo; done`

ai-impact.AfutureofhumanlevelortransformativeAI.summary.txt

This section discusses the difference between human-level AI and transformative AI, and the potential timeline for when either of these levels of AI might be achieved. It is noted that transformative AI could be developed before human-level AI, and that the timeline for when either of these levels of AI might be achieved is difficult to predict. The article provides a link to a companion article which gives an overview of what researchers in this field currently believe about the timeline for AI development.

ai-impact.Endnotes.summary.txt

This section discusses the concept of human-level AI, which is defined as a software system that can carry out at least 90% or 99% of all economically relevant tasks that humans carry out. It also looks at the closely related terms Artificial General Intelligence, High-Level Machine Intelligence, Strong AI, or Full AI, which are sometimes defined in similar, yet different ways. The section also looks at the difficulty of comparing machine and human intelligence, and the potential risks of AI systems, such as AI-enabled disinformation campaigns and mass surveillance by governments. It also looks at the incentives for developing powerful AI, and the potential for it to lead to positive developments. Finally, the section looks at the early warnings of Alan Turing and Norbert Wiener about the alignment problem, and Toby Ord's projection that AI could be developed by 2040.

ai-impact.HowcanwemakesurethatthedevelopmentofAIgoeswell.summary.txt
Making sure that the development of artificial intelligence (AI) goes well is a crucial question for humanity. Currently, resources dedicated to AI are mostly focused on speeding up its development, while efforts to increase its safety are under-resourced. This neglect of AI safety work means that individuals have a good chance to make a positive difference if they dedicate themselves to this problem. However, it needs more than individual efforts; society needs to become knowledgeable about the technology and understand what is at stake. Our World in Data is doing its part to enable a better informed public conversation on AI and the future we want to live in.

ai-impact.Reusethisworkfreely.summary.txt

This section provides information about the licenses and permissions associated with Our World in Data's visualizations, data, code, and articles. All of Our World in Data's work is open access under the Creative Commons BY license, and all software and code is open source under the MIT license. Data produced by third parties is subject to the license terms from the original third-party authors. Additionally, Our World in Data's charts can be embedded in any site, and the project is a part of the Global Change Data Lab, a registered charity in England and Wales. A full legal disclaimer is also provided.

ai-impact.TitleAbstract.summary.txt

This section discusses the potential implications of artificial intelligence (AI) becoming a reality. It explains why it is difficult to take the prospect of a world transformed by AI seriously, and how to develop an idea of what the future of AI might look like. It also looks at the advantages and disadvantages of comparing machine and human intelligence, and introduces the concept of transformative AI, which is defined by the impact this technology would have on the world. It compares the potential of transformative AI to the agricultural and industrial revolutions, and suggests that it could represent the introduction of a similarly significant general-purpose technology.

ai-impact.Whatisatstakeasartificialintelligencebecomesmorepowerful.summary.txt

This section discusses the potential risks and benefits of artificial intelligence (AI) becoming more powerful. It is clear that AI can already cause harm when used maliciously, such as in politically-motivated disinformation campaigns or to enable mass surveillance. AI can also cause unintended harm, such as when an AI system falsely accused 26,000 parents of making fraudulent claims for child care benefits in the Netherlands. As AI becomes more powerful, the potential negative impacts could become much larger, such as mass labor displacement, extreme concentrations of power and wealth, and totalitarianism. Additionally, there is the risk of an AI system escaping human control and harming humans, known as the alignment problem. This risk is difficult to foresee and prevent, and could lead to an extreme catastrophe. On the other hand, AI could lead to positive developments such as cleaner energy, the replacement of unpleasant work, and better healthcare. The stakes are high with this technology, and reducing the negative risks and solving the alignment problem could mean the difference between a healthy, flourishing, and wealthy future for humanity – and the destruction of the same.

ai-impact.overall_summary.txt

This article discusses the potential implications of artificial intelligence (AI) becoming a reality. It explains why it is difficult to take the prospect of a world transformed by AI seriously, and how to develop an idea of what the future of AI might look like. It compares the potential of transformative AI to the agricultural and industrial revolutions, and suggests that it could represent the introduction of a similarly significant general-purpose technology. The article also looks at the advantages and disadvantages of comparing machine and human intelligence, and introduces the concept of transformative AI, which is defined by the impact this technology would have on the world. It is noted that transformative AI could be developed before human-level AI, and that the timeline for when either of these levels of AI might be achieved is difficult to predict.

The article also looks at the potential risks and benefits of AI becoming more powerful. It is clear that AI can already cause harm when used maliciously, such as in politically-motivated disinformation campaigns or to enable mass surveillance. AI can also cause unintended harm, such as when an AI system falsely accused 26,000 parents of making fraudulent claims for child care benefits in the Netherlands. As AI becomes more powerful, the potential negative impacts could become much larger, such as mass labor displacement, extreme concentrations of power and wealth, and totalitarianism. Additionally, there is the risk of an AI system escaping human control and harming humans, known as the alignment problem. This risk is difficult to foresee and prevent, and could lead to an extreme catastrophe. On the other hand, AI could lead to positive developments such as cleaner energy, the replacement of unpleasant work, and better healthcare. The stakes are high with this technology, and reducing the negative risks and solving the alignment problem could mean the difference between a healthy, flourishing, and wealthy future for humanity – and the destruction of the same.

The article also looks at the difference between human-level AI and transformative AI, and the potential timeline for when either of these levels of AI might be achieved. It is noted that transformative AI could be developed before human-level AI, and that the timeline for when either of these levels of AI might be achieved is difficult to predict. Additionally, the article provides information about the licenses and permissions associated with Our World in Data's visualizations, data, code, and articles. Finally, the article looks at the concept of human-level AI, which is defined as a software system that can carry out at least 90% or 99% of all economically relevant tasks that humans carry out. It also looks at the closely related terms Artificial General Intelligence, High-Level Machine Intelligence, Strong AI, or Full AI, which are sometimes defined in similar, yet different ways. The section also looks at the difficulty of comparing machine and human intelligence, and the potential risks of AI systems, such as AI-enabled disinformation campaigns and mass surveillance by governments. It also looks at the incentives for developing powerful AI, and the potential for it to lead to positive developments. Finally, the section looks at the early warnings of Alan Turing and Norbert Wiener about the alignment problem, and Toby Ord's projection that AI could be developed by 2040.
