import glob
from PyPDF2 import PdfReader
import pandas as pd 

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

