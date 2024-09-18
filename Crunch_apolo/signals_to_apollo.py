import pandas as pd
import re
from urllib.parse import urlparse

def clean_url(url):
    if not isinstance(url, str):
        return ''
    parsed = urlparse(url.lower())
    domain = parsed.netloc or parsed.path
    domain = re.sub(r'^www\.', '', domain)
    return domain.strip()

def process_data(crunchbase_file, apollo_file, output_file):
    # Read input files
    try:
        crunch_df = pd.read_excel(crunchbase_file, engine='openpyxl')
    except ValueError:
        # If openpyxl fails, try with xlrd
        crunch_df = pd.read_excel(crunchbase_file, engine='xlrd')
    
    apollo_df = pd.read_csv(apollo_file)

    # Clean website URLs
    crunch_df['Clean Website'] = crunch_df['Website'].apply(clean_url)
    apollo_df['Clean Website'] = apollo_df['Website'].apply(clean_url)

    # Prepare output dataframe
    output_df = pd.DataFrame()

    # Iterate through Crunchbase entries
    for _, crunch_row in crunch_df.iterrows():
        matching_contacts = apollo_df[apollo_df['Clean Website'] == crunch_row['Clean Website']]
        
        if matching_contacts.empty:
            # No matching contacts found
            new_row = crunch_row.copy()
            new_row['First Name'] = ''
            new_row['Last Name'] = ''
            new_row['Title'] = ''
            new_row['Email'] = ''
            new_row['Phone'] = ''
            new_row['LinkedIn URL'] = ''
            new_row['No Contacts'] = 'Yes'
            output_df = pd.concat([output_df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            # Matching contacts found
            for _, apollo_row in matching_contacts.iterrows():
                new_row = crunch_row.copy()
                new_row['First Name'] = apollo_row['First Name']
                new_row['Last Name'] = apollo_row['Last Name']
                new_row['Title'] = apollo_row['Title']
                new_row['Email'] = apollo_row['Email']
                new_row['Phone'] = apollo_row['First Phone'] or apollo_row['Work Direct Phone'] or apollo_row['Mobile Phone']
                new_row['LinkedIn URL'] = apollo_row['Person Linkedin Url']
                new_row['No Contacts'] = 'No'
                output_df = pd.concat([output_df, pd.DataFrame([new_row])], ignore_index=True)

    # Reorder columns
    columns_order = list(crunch_df.columns) + ['First Name', 'Last Name', 'Title', 'Email', 'Phone', 'LinkedIn URL', 'No Contacts']
    output_df = output_df[columns_order]

    # Export to Excel
    output_df.to_excel(output_file, index=False, engine='openpyxl')

    print(f"Processing complete. Output saved to {output_file}")

# Example usage
crunchbase_file = 'Crunch_apolo/crunch.xlsx'
apollo_file = 'Crunch_apolo/apollo.csv'
output_file = 'Crunch_apolo/merged_data.xlsx'

process_data(crunchbase_file, apollo_file, output_file)