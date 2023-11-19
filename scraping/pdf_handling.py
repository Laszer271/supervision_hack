import os
import glob
from PyPDF2 import PdfReader
import pandas as pd 
import requests

def pdf_to_text(path=None):
    data = {}
    configfiles = glob.glob(f'{path}/*.pdf', recursive=True)
    for file in configfiles:
        try:
            reader = PdfReader(file)
        except:
            continue
        page = reader.pages[0]
        pdf_text = page.extract_text()
        data[file] = pdf_text
    return data


def get_pdf_text_from_url(url):
    with open('temp.pdf', 'wb') as f:
        pdf_content = requests.get(url).content
        f.write(pdf_content)
    data = pdf_to_text('temp.pdf')
    os.remove('temp.pdf')
    return data

    
