## This notebook extracts useful details from financial text like invoices, notices, and contracts.

## It can find:

Company and Bank names

Identifiers like PAN, GSTIN, CIN

Dates such as invoice date and due date

Taxes like CGST, SGST, IGST

Interest rates and late fees

Bank account numbers

Service values and other money-related details

## The output is saved in two files:

financial_data.jsonl → structured text format

financial_data_visualization.html → shows the extracted data in a simple webpage

An example input could be a text describing an invoice. The program then extracts the company details, identifiers, tax info, and dates.
