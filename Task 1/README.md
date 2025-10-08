# Task 1 
# Regex Extraction Task (Internship Work)  

This task was about extracting key contract information from a PDF agreement using Python and regular expressions.  

---

## Folder Structure  
Regex-task/  
├── contract_regex_extraction.py  
├── Contract_Agreement_Summary.txt  
├── requirements.txt  
├── output.txt  
└── README.md  

---

## What I did  
- Converted the PDF agreement into plain text (Contract_Agreement_Summary.txt)  
- Wrote regex patterns in Python to extract:  
  - Contract Date  
  - Effective Date  
  - Contract Value  
  - Termination Clause (days)  
  - Contract Reference Number  
- Printed results to console and also redirected output into `output.txt`  

---
  
## Requirements
1. Python standard library only
2. No external dependencies required
3. python>=3.7

## How to run
1. Install Python (>=3.7)  
2. Put the text file (`Contract_Agreement_Summary.txt`) in the same folder as the script  
3. Run the script:  
   ```bash
   python contract_regex_extraction.py