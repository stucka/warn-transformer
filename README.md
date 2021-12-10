# warn-analysis
Analysis and data quality checks related to WARN data

As of 12/2021, this is the order that files should be run in for analysis: standardize_field_names.py => standardize_dates.py

### `standardize_field_names.py`
Input: each state's WARN data `.csv` files from the `.warnscraper\exports\` directory
Output: `standardize_field_names.csv`, a single standardized & merged `.csv` file of all scraped states

### `standardize_dates.py`
Input: `standardize_field_names.csv`
Output: `standardize_dates.csv`
This program adds 5 additional columns to the data: 
+ (1) date_received_cleaned
+ (2) date_received_year
+ (3) date_received_month
+ (4) date_layoff_cleaned
+ (5) date_closing_cleaned

### `merge_warn_ppp.ipny`

### `standardize_company_names.py`
This program is not finished, but is meant to add an additional columns detailing a list of possible corporate entities that could be a match for the company name.
