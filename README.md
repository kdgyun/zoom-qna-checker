# zoom-qna(poll)-checker

<br>
<br>

Currently, **only the Korean version is supported**. That is, the content of the report must be in Korean. To receive the report in Korean, you can select Korean from the 'Language' option at the bottom of Zoom.

For the CSV report file, go to Zoom web > Reports > Usage Reports > Webinar and check the Poll Report. Then, select the date of the webinar you wish to grade. 
Finally, you can download the report by clicking on Generate CSV Report.

<br>
<br>

### Please note!

The qna report of a Zoom webinar is saved as a CSV file, but **it may not open correctly due to inconsistent data formats within**. 

For this issue, **just opening the "qna.csv" file in MS Excel and then saving it** without any additional actions will allow Excel to automatically convert and save the data in the appropriate format, thus resolving the problem.

It is recommended to preprocess the file using the above method before using the program.

<br>

## How to Use
To use the Zoom qna Checker, follow these steps:

### 1. Clone the Repository

Use one of the following commands to clone the repository:

```sh
git clone https://github.com/kdgyun/zoom-qna-checker.git
```
or

```sh
git clone git@github.com:kdgyun/zoom-qna-checker.git
```

<br>

### 2. Navigate to the cloned repository directory and install the required Python packages:

```sg
cd zoom-qna-checker
pip install -r requirements.txt
```

<br>

### 3. Run the Script

Navigate to the directory containing main.py and run it with the following options:

- **-h / --help**: Show help message and exit.
- **-p / --path : (Required)** Path to the CSV file.
- **-a / --answer: (Required)** Q&A Answers for Grading (One or More)


#### Examples:
**Basic usage:**
```sh
python main.py -p path-to-qna.csv -a 'answer'
```
</br>

**To consider multiple answers:**
```sh
python main.py -p path-to-qna.csv -a 'answer1' 'answer2' 'answer3'
```

<br>

The script generates an **Excel (.xlsx) file** with the qna results, including a list of attendees marked present and a section for those needing manual verification.

Contributing
We welcome contributions! If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.
