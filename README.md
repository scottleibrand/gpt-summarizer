# gpt-summarizer
### Extract text, summarize each section w/ GPT, and provide a summarized outline of a paper/article

This script extracts text from a given file or URL and splits it into sections. It then uses OpenAI's tokenizer to encode the text as a sequence of tokens. It writes the extracted text to an output file and writes each section to a separate text file. It also generates a summary for each subsection and writes the summary to a summary file. If there are multiple summary files for a section, it generates a combined section summary.

The script expects a PDF or HTML file path, or an HTML URL, to be passed as a command line argument. It extracts the text from the PDF file, splits the text into sections, and uses the tiktoken.get_encoding function to encode the text as a sequence of tokens using the "gpt2" encoding. It writes the extracted text to an output file using the base_name of the file and the .txt extension.

It processes each section by first using the split_section_into_subsections function to split the section into subsections based on HTML section headings or numbered section headings. If necessary, it further splits any subsections into paragraphs and recombine adjacent ones until they exceed 1000 tokens. It processes each resulting section/part with InstructGPT (text-davinci-003) to generate a summary, and writes each section summary to a summary file. If there are multiple summary files for a section, it generates a combined section summary by concatenating the summaries of the individual subsections.

It then performs one final round of summarization across all the lower-level summaries, to produce an overall summary of the paper/article.

The intended use is that both the overall summary and the subsection summaries (in order) are worth reading to determine whether to spend the time reading the entire article/paper, or specific sections of it.

You can also specify an optional second positional argument to have the summaries generated in the specified language: to do so it adds `" Please use "+sys.argv[2]+" language for the output."` to the prompt if the argument is present.

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
python summarize.py https://path/to/article Spanish
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

https://github.com/scottleibrand/gpt-summarizer/tree/main/examples

### Summary of OurWorldInData AI Impact article
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

#### OWID Overall Summary

This article discusses the potential implications of artificial intelligence (AI) becoming a reality. It explains why it is difficult to take the prospect of a world transformed by AI seriously, and how to develop an idea of what the future of AI might look like. It compares the potential of transformative AI to the agricultural and industrial revolutions, and suggests that it could represent the introduction of a similarly significant general-purpose technology. The article also looks at the advantages and disadvantages of comparing machine and human intelligence, and introduces the concept of transformative AI, which is defined by the impact this technology would have on the world. It is noted that transformative AI could be developed before human-level AI, and that the timeline for when either of these levels of AI might be achieved is difficult to predict.

The article also looks at the potential risks and benefits of AI becoming more powerful. It is clear that AI can already cause harm when used maliciously, such as in politically-motivated disinformation campaigns or to enable mass surveillance. AI can also cause unintended harm, such as when an AI system falsely accused 26,000 parents of making fraudulent claims for child care benefits in the Netherlands. As AI becomes more powerful, the potential negative impacts could become much larger, such as mass labor displacement, extreme concentrations of power and wealth, and totalitarianism. Additionally, there is the risk of an AI system escaping human control and harming humans, known as the alignment problem. This risk is difficult to foresee and prevent, and could lead to an extreme catastrophe. On the other hand, AI could lead to positive developments such as cleaner energy, the replacement of unpleasant work, and better healthcare. The stakes are high with this technology, and reducing the negative risks and solving the alignment problem could mean the difference between a healthy, flourishing, and wealthy future for humanity – and the destruction of the same.

The article also looks at the difference between human-level AI and transformative AI, and the potential timeline for when either of these levels of AI might be achieved. It is noted that transformative AI could be developed before human-level AI, and that the timeline for when either of these levels of AI might be achieved is difficult to predict. Additionally, the article provides information about the licenses and permissions associated with Our World in Data's visualizations, data, code, and articles. Finally, the article looks at the concept of human-level AI, which is defined as a software system that can carry out at least 90% or 99% of all economically relevant tasks that humans carry out. It also looks at the closely related terms Artificial General Intelligence, High-Level Machine Intelligence, Strong AI, or Full AI, which are sometimes defined in similar, yet different ways. The section also looks at the difficulty of comparing machine and human intelligence, and the potential risks of AI systems, such as AI-enabled disinformation campaigns and mass surveillance by governments. It also looks at the incentives for developing powerful AI, and the potential for it to lead to positive developments. Finally, the section looks at the early warnings of Alan Turing and Norbert Wiener about the alignment problem, and Toby Ord's projection that AI could be developed by 2040.

#### OWID Section Summaries

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

### Summary of NEJM Open Source AID paper

```
~/src/gpt-summarizer $ ./summarize.py examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.pdf
Text extracted from examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.pdf and written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.full.txt
Total token count: 23722
Header:  Title-Abstract
Title-Abstract. Section intro (4545 characters, 1502 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintro.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintro.summary.txt
Title-Abstract. Section intro-part2 (4111 characters, 1133 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart2.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart2.summary.txt
Title-Abstract. Section intro-part3 (5247 characters, 1534 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart3.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart3.summary.txt
Title-Abstract. Section intro-part4 (6224 characters, 1969 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart4.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart4.summary.txt
Title-Abstract. Section intro-part5 (4477 characters, 1704 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart5.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart5.summary.txt
Title-Abstract. Section intro-part6 (3400 characters, 1181 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart6.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart6.summary.txt
Title-Abstract. Section intro-part7 (2354 characters, 1334 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart7.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart7.summary.txt
Title-Abstract. Section intro-part8 (1150 characters, 1110 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart8.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart8.summary.txt
Title-Abstract. Section intro-part9 (1898 characters, 1843 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart9.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart9.summary.txt
Title-Abstract. Section intro-part10 (1436 characters, 1317 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart10.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart10.summary.txt
Title-Abstract. Section intro-part11 (1894 characters, 1839 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart11.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart11.summary.txt
Title-Abstract. Section intro-part12 (677 characters, 634 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart12.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart12.summary.txt
Title-Abstract. Section intro-part13 (2072 characters, 1857 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart13.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart13.summary.txt
Title-Abstract. Section intro-part14 (4243 characters, 1645 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart14.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart14.summary.txt
Title-Abstract. Section intro-part15 (4297 characters, 1382 tokens) written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart15.full.txt
Summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart15.summary.txt
No summary files found for section TitleAbstractSectionintropart15
No abstract found for examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy
Concatenated 0 summaries into a single summary with 2 characters and 1 tokens
Concatenated subsection summaries have less than 500 tokens, reading in all summaries
Overall summary written to examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.overall_summary.txt
```

#### NEJM AID Overall Summary

This paper describes the results of a clinical trial that tested the efficacy of an automated insulin delivery (AID) system in patients with type 1 diabetes. A total of 100 patients were enrolled, 97 of whom (48 children and 49 adults) underwent randomization to either the AID group (44 patients) or the control group (53 patients). The characteristics of the patients at baseline were similar in the two trial groups. The primary analysis showed that the mean time in range increased from 61.2% at baseline to 71.2% in the AID group and decreased from 57.7% to 54.5% in the control group. Among the children, the mean time in range increased from 57.4% at baseline to 67.5% in the AID group and decreased from 55.1% to 52.5% in the control group. During a 24-hour period, the percentage of time that patients had a glucose reading of less than 70 mg per deciliter was 2.1% in the AID group and 2.7% in the control group. The use of AID was most effective at night, when the mean time in range was 76.8% in the AID group and 57.2% in the control group. Among the adults, the mean time in range increased from 64.7% at baseline to 74.5% in the AID group and decreased from 61.2% to 58.2% in the control group. The trial also found that the AID system was safe and had a high level of patient retention. The results indicate that the AID group had a higher percentage of time in the target glucose range than the control group, and that the group differences are partly attributable to a decrease in the percentage of time in range in the control group after the run-in period.

#### NEJM AID Section Summaries
`ls -rt examples/NEJM*summary.txt | while read file; do echo -n $file; cat $file; echo; echo; done`

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintro.summary.txt

Section has no content.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart2.summary.txt

This section discusses two widely used open-source AID systems, AndroidAPS and Loop, and the barriers to their uptake. It also introduces the CREATE (Community Derived Automated Insulin Delivery) trial, which was conducted at four sites in New Zealand to evaluate the efficacy and safety of an open-source AID system compared to sensor-augmented insulin-pump therapy in children and adults with type 1 diabetes. The trial was approved by the Southern Health and Disability Ethics Committee of New Zealand and funded by the Health Research Council of New Zealand. Hardware support was provided by SOOIL Development, Dexcom, and Vodafone New Zealand. The trial protocol has been published previously and an independent data and safety monitoring committee and medical monitor provided trial oversight. Eligible patients were between the ages of 7 and 70 years, had received a diagnosis of type 1 diabetes at least 1 year earlier, had at least 6 months of experience with insulin-pump therapy, and had a mean glycated hemoglobin level of less than 10.5%. Patients in the two trial groups were invited to join separate closed online communities that provided ongoing peer support.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart3.summary.txt

This section describes the trial design for a study on Automated Insulin Delivery in Type 1 Diabetes. The study included a 4-week run-in phase, during which patients became familiar with the trial devices functioning as sensor-augmented insulin-pump therapy. Patients were then randomly assigned in a 1:1 ratio to the AID group or the control group. The AID group used an open-source system, which was a modified version of AndroidAPS paired with a preproduction DANA-i insulin pump and Dexcom G6 CGM. The primary outcome was percentage of time in the target glucose range of 70 to 180 mg per deciliter between day 155 and day 168. Secondary outcomes included metrics for continuous glucose monitoring, glycated hemoglobin level, and performance of the AID system. Adverse events that were evaluated included adverse device effects, serious adverse events, and serious adverse device effects. At approximately 3 months into the trial, a battery problem in a preproduction DANA-i insulin pump was identified. Patients in the control group had the option of returning to their usual insulin pump, and those in the AID group used refurbished preproduction DANA-i insulin pumps. The study had 90% power with a two-sided alpha of 0.05 to reject the null hypothesis of no between-group difference in the time in range.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart4.summary.txt

This section describes the data capture and management processes, data cleaning and analyses, and primary and secondary outcomes of a clinical trial that tested the efficacy of an automated insulin delivery (AID) system in patients with type 1 diabetes. A total of 100 patients were enrolled, 97 of whom (48 children and 49 adults) underwent randomization to either the AID group (44 patients) or the control group (53 patients). The characteristics of the patients at baseline were similar in the two trial groups. The final patient completed the trial in November 2021. In the primary analysis, the mean time in range increased from 61.2% at baseline to 71.2% in the AID group and decreased from 57.7% to 54.5% in the control group. Among the children, the mean time in range increased from 57.4% at baseline to 67.5% in the AID group and decreased from 55.1% to 52.5% in the control group. During a 24-hour period, the percentage of time that patients had a glucose reading of less than 70 mg per deciliter was 2.1% in the AID group and 2.7% in the control group. The use of AID was most effective at night, when the mean time in range was 76.8% in the AID group and 57.2% in the control group. Among the adults, the mean time in range increased from 64.7% at baseline to 74.5% in the AID group and decreased from 61.2% to 58.2% in the control group.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart5.summary.txt

This section provides information on the safety outcomes and system performance of a trial that tested the use of an automated insulin delivery (AID) system in adults and children with type 1 diabetes. The AID system was found to be most effective at night, when the time in range was 85.2±12.7% in the AID group, compared to 70.9±12.7% during the day. In the control group, the mean time in range at night (53.5±20.1%) was similar to that during the day (57.5±14.4%). Neither severe hypoglycemia nor diabetic ketoacidosis occurred in either trial group, and no adverse events were related to the algorithm or automation of insulin delivery. Ten adverse events that were related to a device (nonserious adverse device effects) were reported among 8 patients in the AID group, and 8 events were reported among 8 patients in the control group. Two serious adverse events occurred in the AID group, and 5 serious adverse events occurred in the control group. The median percentage of time that the system was automating insulin delivery was 94.2% (IQR, 87.3 to 95.7) in the AID group.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart6.summary.txt

This section provides a comparison of the characteristics of patients in the Automated Insulin Delivery (AID) group and the control group in the CREATE trial. The characteristics include the quintile of the New Zealand Deprivation Index, diabetes history, glycated hemoglobin, previous use of continuous glucose monitoring (CGM) and automated insulin delivery, and time in target glucose range. The AID group had a mean percent glycated hemoglobin of 7.6 mmol/mol, 15 patients (65%) had previously used CGM, and 4 patients (17%) had previously used automated insulin delivery. The control group had a mean percent glycated hemoglobin of 7.8 mmol/mol, 17 patients (65%) had previously used CGM, and 5 patients (19%) had previously used automated insulin delivery. The time in target glucose range was 64.7±12.9% for the AID group and 60.3±15.6% for the control group. The section also provides information on device deficiencies, which were more common in the AID group (46 events) than in the control group (39 events).

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart7.summary.txt

This section discusses the findings of a trial that evaluated the effect of an artificial intelligence-based (AID) therapy on glycemic control. The results showed that the AID therapy improved glycemic control, with the greatest improvement seen overnight. Adults had a higher percentage of time in the target range than children, possibly due to differences in glycemic variability, likelihood of administration of an insulin bolus before a meal, activity level, and dietary factors. The absolute differences in the percentage of time in range between the trial groups were similar to between-group differences for commercially available AID systems. The results showed that patients with the lowest baseline time in the target range gained the most from the use of AID.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart8.summary.txt
Section has no content.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart9.summary.txt

Section has no content.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart10.summary.txt

Section has no content.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart11.summary.txt
Section has no content.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart12.summary.txt

Section has no content.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart13.summary.txt

Section has no content.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart14.summary.txt

This section describes the results of a trial comparing the use of open-source automated insulin delivery (AID) and sensor-augmented insulin-pump therapy (control group) in children (7 to 15 years of age) and adults (16 to 70 years of age). The results are presented in two figures, which show the percentage of time that patients were in the target glucose range (70 to 180 mg per deciliter [3.9 to 10.0 mmol per liter]) during contiguous 4-week periods from 4 weeks before randomization to 24 weeks after randomization. The results indicate that the AID group had a higher percentage of time in the target glucose range than the control group, and that the group differences are partly attributable to a decrease in the percentage of time in range in the control group after the run-in period. The trial also had a high level of patient retention, a lack of remote monitoring, and broad inclusion criteria, which resulted in a population of diverse ages and ethnic backgrounds.

examples/NEJM-OpenSourceAID-DanaMLewis-AuthorCopy.TitleAbstractSectionintropart15.summary.txt

This section provides information about the limitations of the trial and the generalizability of the findings. It was noted that the control group did not have an automated system for predicting low-glucose levels or suspending insulin administration, which have been shown to reduce the incidence of hypoglycemia. The trial patients were more diverse than those enrolled in previous studies, but the generalizability of the findings may be limited by the enrollment of patients with a relatively low glycated hemoglobin level at baseline, by the underrepresentation of patients with reduced economic resources, and by the increased familiarity with insulin-pump therapy and continuous glucose monitoring among the patients at baseline. In addition, a variety of insulin pumps were used in the control group, although the stable time in the target range throughout the trial suggests that this factor had a minimal effect. The section also provides information about the study's funding and disclosure forms.
