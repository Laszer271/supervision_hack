from scraping.pdf_handling import pdf_to_text
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
from scraping.text_processing import get_raw_content, remove_non_ascii, split_on_newline, TextChunker
from scraping.semantic_search import SemanticSearch

import pandas as pd
import torch
import gc

verbose = True 
df_urls = pd.read_excel('Bank_list.xlsx', index_col=0)
date = '18-11-2023'

model_name = "henryk/bert-base-multilingual-cased-finetuned-polish-squad2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
pipe = pipeline("question-answering", model=model_name)

if verbose:
    print('Max context length:', tokenizer.model_max_length)

for bank_name in df_urls['Name'].unique():
    for client_type in ['Individual', 'Corporation']:
        if bank_name != 'Bank Ochrony Środowiska SA':   
            continue
        if verbose:
            print('='*50)
            print('Bank name:', bank_name)
            print('Client type:', client_type)
            print('Date:', date)

        chunker = TextChunker(tokenizer=tokenizer, max_len=400, stride_len=100)

        data = pdf_to_text(f'../bank_data/{date}/{client_type}/{bank_name}')
        if verbose:
            print('Number of files:', len(data))
        for file, text in data.items():
            if verbose:
                print('---')
                print(len(text))
            text = remove_non_ascii(text)
            if verbose:
                print(len(text))

            splitted = split_on_newline(text)
            data[file] = splitted


        urls = df_urls.loc[df_urls['Name'] == bank_name, 'Individual'].dropna().tolist()
        print('urls:', urls)
        for url in urls:
            if verbose:
                print('---')
            soup = get_raw_content(url)
            if verbose:
                print(len(soup))
            soup = remove_non_ascii(soup)
            if verbose:
                print(len(soup))

            splitted = split_on_newline(soup)
            data[url] = splitted


        all_chunks = []

        for file, splitted in data.items(): 
            if verbose:
                print('---')
            chunks = chunker.split_text(splitted)
            all_chunks.extend(chunks)

            if verbose:
                print(file[-20:], len(splitted), len(chunks))
        if verbose:
            print('All chunks:', len(all_chunks))


        semantic_search = SemanticSearch()

        semantic_search.vectorize_text(strings=all_chunks)
        result = semantic_search.search("wysokość oprocentowania promocyjnego na lokacie w %", k=5)
        if verbose:
            print(len(result))

        best_contexts = [r[0].page_content for r in result]

        question = "Jaka jest wysokość oprocentowania promocyjnego na lokacie?"
        # question = 'Do kogo jest skierowana oferta?'

        preds = []
        for context in best_contexts:
            # generate 3 answers to the question
            pred = pipe(question=question, context=context, do_sample=False, top_k=3)

            pred = [p['answer'] for p in pred]
            preds.append(pred)

        if verbose:
            print(preds)

        del semantic_search
        del result
        del best_contexts
        del pred
        torch.cuda.empty_cache()
        gc.collect()
