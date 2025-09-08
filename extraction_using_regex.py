import re
import pdfplumber
import warnings
warnings.filterwarnings("ignore")

#Function to standardize dates to a single format
def standard_date(date):
    day_pattern="\d{1,2}"
    month_pattern=" [A-Za-z]* "
    year_pattern="\d{4}"

    day=re.findall(day_pattern,date)
    month=re.findall(month_pattern,date)
    year=re.findall(year_pattern,date)

    standard_date=month[0].strip()+" "+day[0]+", "+year[0]
    return standard_date

#Converting pdf to .txt file
with pdfplumber.open("Alpha Technologies Pvt. Ltd.pdf") as pdf:
    with open("file_contents.txt",'w') as f:
        f.write(pdf.pages[0].extract_text())

#Reading .txt file
with open("file_contents.txt",'r') as f:
    text=f.read()

#regex patterns
entry_date_pattern = "Agreement[\w| ]*entered[\w| ]+(\d{1,2}(?:st|nd|rd|th))[day of|of ]*([\w]*), (\d{4})"
effective_date_pattern= "Agreement[\w ]+effective [\w]+ (\w+) (\d{1,2}), (\d{4})"
value_pattern="contract value is ([\w]*) ([\d,.]*),"
termination_pattern="termination clause [\w \n]* (\d{1,2})"
reference_no_pattern="Contract Reference No: ([\w-]*)"

#extracting details
#Contract Date
entry_date=''
matches=re.findall(entry_date_pattern,text)
for v in matches[0]:
    entry_date+=v
    entry_date+=" "
entry_date=standard_date(" "+entry_date)

#Effective Date
effective_date=''
matches=re.findall(effective_date_pattern,text)
for v in matches[0]:
    effective_date+=v
    effective_date+=" "
effective_date=standard_date(" "+effective_date)

#Contract Value
matches=re.findall(value_pattern,text)
currency=matches[0][0]
amount=matches[0][1]
value=currency+" "+amount

#Termination Clause duration
matches=re.findall(termination_pattern,text)
termination_clause_duration=matches[0]

#Contract Reference No
matches=re.findall(reference_no_pattern,text)
reference_no=matches[0]

output_text=f"""Contract Date : {entry_date}
Effective Date : {effective_date}
Contract Value : {value}
Termination Clause (duration in days) : {termination_clause_duration}
Contract Reference Number : {reference_no}
"""

with open("output.txt",'w') as f:
    f.write(output_text)


    



