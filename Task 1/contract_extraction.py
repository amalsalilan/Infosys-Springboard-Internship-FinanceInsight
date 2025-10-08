import re

# open the text file (already converted from pdf)
with open("Contract_Agreement_Summary.txt", "r", encoding="utf-8") as f:
    text = f.read()

# regex patterns I tried
# contract date looks like "entered into on the 5th day of July, 2024"
contract_date_pattern = r"entered into on the\s+([A-Za-z0-9\s,]+)"

# effective date -> "effective on August 1, 2024"
effective_date_pattern = r"effective on\s+([A-Za-z0-9\s,]+)"

# contract value usually written as USD 125,000.00
contract_value_pattern = r"(USD\s[0-9,]+\.\d{2})"

# termination clause, mostly like "30 days’ notice"
termination_clause_pattern = r"(\d+)\s+days"

# contract reference number -> something like CON-ALD-20240705
reference_number_pattern = r"Contract Reference No:\s*([A-Z0-9\-]+)"

# now search in the text
contract_date = re.search(contract_date_pattern, text, re.IGNORECASE)
effective_date = re.search(effective_date_pattern, text, re.IGNORECASE)
contract_value = re.search(contract_value_pattern, text, re.IGNORECASE)
termination_clause = re.search(termination_clause_pattern, text, re.IGNORECASE)
reference_number = re.search(reference_number_pattern, text, re.IGNORECASE)

# printing results
print("Extracted Contract Information:")
print("Contract Date:", contract_date.group(1).strip() if contract_date else "Not found")
print("Effective Date:", effective_date.group(1).strip() if effective_date else "Not found")
print("Contract Value:", contract_value.group(1).strip() if contract_value else "Not found")
print("Termination Clause (days):", termination_clause.group(1).strip() if termination_clause else "Not found")
print("Contract Reference Number:", reference_number.group(1).strip() if reference_number else "Not found")