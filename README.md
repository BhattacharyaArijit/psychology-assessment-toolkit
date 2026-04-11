# Psychological Assessment Toolkit

A **Python-based GUI system** for administering psychological questionnaires digitally in research studies.
The toolkit dynamically loads questionnaires from **JSON configuration files**, allowing researchers to easily add, modify, or customize assessments without changing the program code.

The system supports **multiple questionnaire formats, reverse scoring, subscale scoring, and automatic data export**, making it suitable for experimental research, surveys, and psychological assessments.


# Key Features

### Dynamic Questionnaire Loading

Questionnaires are loaded from JSON files, new assessments can be added without any need of modification of the python code.

### Multiple Scale Formats

The system supports:

* Standard Likert scales
* Multi-statement questions (e.g., Beck Depression Inventory style)
* Custom response scales

### Reverse Scoring

Items that require reverse scoring can be specified in the questionnaire JSON.

### Subscale Scoring

Questionnaires can define multiple **subcategories or subscales**, and the program automatically calculates their scores.

### Automatic Data Export

Responses and scores are automatically exported as **CSV files**, making them easy to analyze in software such as:

* SPSS
* R
* Python
* Excel
* JASP

### Master Score File

All participants' scores are collected in a single dataset for analysis.

### Scrollable GUI

Long questionnaires are displayed in a **scrollable interface**, ensuring usability for large assessments.

### About / Credits Page

A built-in page for:

* questionnaire references
* scale citations
* research credits


# Installation

Clone the repository:

```
git clone https://github.com/BhattacharyaArijit/psychology-assessment-toolkit
```

Navigate to the project folder:

```
cd psych-assessment-toolkit
```
Install tkinter for the GUI

```
sudo apt install python3-tk  # Debian/Ubuntu
```
Refer to the tkinter for additional information: https://docs.python.org/3/library/tkinter.html

Install required dependencies:

```
pip install -r requirements.txt
```
If the above installation fails, then try "conda install pandas pyyaml numpy"

# Running the Application

Start the questionnaire system using:

```
python main.py
```

This will open the graphical interface where participants can complete the questionnaires.


# Repository Structure

```
psych-assessment-toolkit/
│
├── main.py
├── gui_engine.py
├── scorer.py
├── utils.py
│
├── config.json
│
├── questionnaires/
│   ├── panas.json
│   ├── bdi.json
│   ├── custom_simple.json
│   └── custom_subscale.json
│
├── static_pages/
│   └── about.json
│
├── output/
│
│
├── requirements.txt
├── README.md
└── LICENSE
```

### File Description

**main.py**

Application engine.
Loads configuration and launches the GUI.

**gui_engine.py**

Responsible for:

* building questionnaire pages
* rendering questions
* collecting responses
* navigating between questionnaires

**scorer.py**

Handles scoring logic such as:

* total scores
* reverse scoring
* subscale calculations

**utils.py**

Utility functions including:

* JSON loading
* response validation
* output file management

**config.json**

Controls which questionnaires are loaded and general application settings.


# Questionnaires

All questionnaires are stored as **JSON files** inside the `questionnaires/` directory.

Each questionnaire file defines:

* instructions
* questions
* response scale
* reverse scoring items
* subscales (optional)

The program automatically loads these files and builds the interface.


# Creating a New Questionnaire

To add a new questionnaire:

### Step 1

Create a JSON file in the `questionnaires/` folder.

Example:

```
questionnaires/sleep_quality.json
```

### Step 2

Add the questionnaire name to `config.json`.

Example:

```
"questionnaires": [
  "panas",
  "bdi",
  "sleep_quality"
]
```

### Step 3

Run the application again.

The new questionnaire will automatically appear in the interface.


# Simple Questionnaire Example

Example structure for a basic Likert questionnaire:

```
{
  "name": "Example Questionnaire",

  "instructions": "Please indicate how much you agree with each statement.",

  "scale": [1,2,3,4,5],

  "scale_labels": {
    "1": "Strongly Disagree",
    "2": "Disagree",
    "3": "Neutral",
    "4": "Agree",
    "5": "Strongly Agree"
  },

  "questions": [
    {
      "id": "Q1",
      "text": "I enjoy solving complex problems."
    },
    {
      "id": "Q2",
      "text": "I feel confident when learning new skills."
    }
  ],

  "reverse_items": []
}
```


# Questionnaire with Subscales

The system also supports **subcategories or subscales**.

Example:

```
{
  "name": "Personality Example",

  "scale": [1,2,3,4,5],

  "questions": [
    {
      "id": "Q1",
      "text": "I can talk to anyone I just met.",
      "subscale": "Extraversion"
    },
    {
      "id": "Q2",
      "text": "I can't talk to anyone I just met.",
      "subscale": "Extraversion"
    }
  ],

  "reverse_items": ["Q2"],

  "subscales": {
    "Extraversion": ["Q1","Q2"]
  }
}
```

The program will automatically compute:

* Extraversion score
* Total score (if enabled)


# Reverse Scoring

Reverse scoring is specified using the `reverse_items` field.

Example:

```
"reverse_items": ["Q2","Q5","Q9"]
```

If the scale is:

```
1–5
```

the reverse score is calculated as:

```
new_score = (max + 1) − original_score
```


# Multi-Statement Question Format

Some questionnaires (such as BDI) contain multiple statements per item.

Example format:

```
{
  "id": "Q1",
  "options": [
    "I do not feel sad",
    "I feel sad",
    "I am sad most of the time",
    "I am extremely sad"
  ]
}
```

The GUI automatically displays these as **radio button options**.


# Output Files

All responses are saved in the `output/` folder.

Two types of files are generated.

### Participant Response File

Example:

```
P001_responses.csv
```

Contains:

* participant ID
* question responses
* timestamps

---

### Master Score File

Example:

```
Master_scores.csv
```

Contains summarized scores for all participants.

Example:

```
SubjectID,PANAS_positive,PANAS_negative,BDI_total
P001,21,12,9
P002,17,15,14
```

This file can be directly imported into statistical software.


# Customization Options

Researchers can customize the toolkit by modifying:

### Questionnaires

Add or edit JSON files.

### Scales

Define any response range (e.g., 1–4, 1–7).

### Subscales

Group items into categories.

### Reverse Scoring

Specify items to reverse score.

### GUI Layout

Modify `gui_engine.py` to change the interface.

### Output Format

Modify `scorer.py` or `utils.py` to adjust scoring or export format.


# Example Questionnaires Included

The repository can include examples such as:

* PANAS (Positive and Negative Affect Schedule)
* BDI (Beck Depression Inventory)
* STAI (State–Trait Anxiety Inventory)
* Neuroticism Scales
* Custom questionnaires

These examples demonstrate how to structure questionnaire JSON files.


# Intended Use

This toolkit is designed for:

* psychological research
* behavioral experiments
* student research projects
* survey-based studies

It provides a **flexible platform for administering multiple psychological scales within a single interface**.


# License

This project is released under the **MIT License**.

Researchers are free to modify and extend the toolkit for academic or research purposes with proper citation to both the toolkit as well as the source of questionnaires.

## Citation

Bhattacharya, A. (2026).
Psychological Assessment Toolkit: A modular Python system
for administering psychological questionnaires.
https://github.com/BhattacharyaArijit/psychology-assessment-toolkit.

## BibTeX version:

@software{bhattacharya_psych_toolkit_2026,
  author = {Bhattacharya, Arijit},
  title = {Psychological Assessment Toolkit},
  year = {2026},
  url = {https://github.com/BhattacharyaArijit/psychology-assessment-toolkit},
  note = {Python-based toolkit for administering psychological questionnaires}
}
## Contribution

Arijit Bhattacharya, Ashoka University

## Collaboration

Contributions and collaborations are welcome. This project is intended to grow as an open, research-oriented toolkit for administering psychological questionnaires and behavioral assessments. If you are interested in collaborating, contributing code, or using this toolkit for research projects, please feel free to reach out.

**Contact:**
Arijit Bhattacharya
Ph.D. Candidate, Department of Psychology and Cognitive Sciences
Ashoka University

[arijit.bhattacharya_phd23@ashoka.edu.in](mailto:arijit.bhattacharya_phd23@ashoka.edu.in)

Before submitting major changes, it is recommended to first open an issue describing the proposed feature or improvement so that it can be discussed and aligned with the project roadmap.




#### Research Use & Ethics Disclaimer

This toolkit is provided as a **general-purpose digital framework for administering psychological questionnaires**. It is intended to assist researchers by replacing traditional paper-and-pencil assessments with a digital interface that facilitates **data collection, response storage, and automated score calculation**.

The software itself **does not grant permission to use any specific psychological questionnaire, scale, or instrument**. Many psychological assessments are **copyrighted, licensed, or require formal permission from the original authors or publishers** before they can be used in research or clinical contexts.

Users of this toolkit are **solely responsible** for ensuring that they:

* Obtain the necessary **permissions or licenses** from the creators or copyright holders of any questionnaire they administer.
* Follow all **ethical guidelines, institutional policies, and research regulations** governing psychological assessments.
* Ensure proper **informed consent and data protection procedures** when collecting participant responses.

The author of this toolkit **does not provide authorization to use any psychological instruments included as examples**, and **assumes no responsibility or liability for the misuse of copyrighted or restricted questionnaires**.

This toolkit simply provides a **technical platform for digital administration of assessments** and should be treated as a **software tool rather than a source of licensed psychological instruments**.



## Clinical Use Disclaimer

This software is provided **for research and educational purposes only**.

The Psychological Assessment Toolkit is **not intended to be used as a clinical diagnostic tool**, nor should it be used to make medical, psychological, or treatment decisions. Any interpretation of questionnaire results must be performed by **qualified professionals using appropriate clinical judgment and validated assessment procedures**.

The author of this toolkit **assumes no responsibility for clinical decisions, diagnoses, or treatments** based on the use of this software.


