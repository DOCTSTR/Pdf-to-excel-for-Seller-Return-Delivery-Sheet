import streamlit as st
import tabula as tb
import pandas as pd
import pdfplumber
import re 
from io import BytesIO
import base64

def extract_data(file):
    datetime_regex = r"\b(\d{1,2}\s+\w+,\s+\d{4})\b"
    with pdfplumber.open(file) as pdf:
        # Loop through all the pages in the PDF
        for page in pdf.pages:
            # Extract text from the page
            text = page.extract_text()
            # Extract datetime from the page and write to the Excel sheet
            datetime = re.search(datetime_regex, text)
            if datetime:
                finalDate = datetime.group()

    table = tb.read_pdf(file, pages='all')

    # csv file
    csv_table = tb.convert_into(file, 'pdf_convert.csv', output_format='csv', pages='all')

    # for excel extraction, we have to export the data to the dataframe
    # Select only the columns you need

    # we are using pandas library
    df = pd.concat(table)
    # extract the part in parentheses as a separate column
    df['AWB Number2'] = df['AWB Number'].str.extract(r'\((.*)\)')
    df['Order ID1'] = df['COID'].str.extract(r'(.*)_\d+_\w+$')
    df = df[['AWB Number', 'AWB Number2', 'Order ID1', 'Remarks']]
    df = df.rename(columns={'AWB Number': 'AWB Number1', 'Order ID1': 'Order ID'})
    df['AWB Number'] = df['AWB Number1'].str.extract(r'^(\S+)')
    df['Date'] = finalDate
    df = df[['AWB Number', 'AWB Number2', 'Order ID', 'Remarks', 'Date']]
    return df

st.title("PDF Data Extraction")

# File uploader
file = st.file_uploader("Upload a PDF file", type="pdf")

if file is not None:
    # Extract data and display in a table
    df = extract_data(file)
    st.write(df)

    # Download button for Excel file
    output = BytesIO()
    excel_file = df.to_excel(output, index=False)
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="pdf_convert.xlsx">Download Excel file</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.write("Please upload a PDF file.")
