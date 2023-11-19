from scraping.pdf_handling import pdf_to_text
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
from scraping.text_processing import get_raw_content, remove_non_ascii, split_on_newline, TextChunker
from scraping.semantic_search import SemanticSearch
from scraping.html_parser import HTMLBankParser, proces_links

import pandas as pd
import torch
import re
import gc

def choose_best_data(segments, tables, links, account_type):
    all_splitted = []
    if segments:
        for segment in segments:
            if verbose:
                print('---')
                print(len(segment))
            segment = remove_non_ascii(segment)
            if verbose:
                print(len(segment))

            splitted = split_on_newline(segment)
            all_splitted.append(splitted)
    elif tables:
        for table in tables:
            if verbose:
                print('---')
                print(len(table))
            table = remove_non_ascii(table)
            if verbose:
                print(len(table))

            all_splitted.append(table)
    elif links:
        pass
    else:
        print(f'No data found for {account_type} type account')

    return all_splitted


def get_chunks(all_splitted, chunker, verbose=False):
    all_chunks = []

    for splitted in all_splitted: 
        if verbose:
            print('---')
        chunks = chunker.split_text(splitted)
        all_chunks.extend(chunks)

        if verbose:
            print(len(splitted), len(chunks))

    if verbose:
        print('All chunks:', len(all_chunks))
    return all_chunks


def do_qa(all_chunks, sim_phrase, question, postprocess_pattern, replace_patterns, output_type, verbose=False):
    semantic_search = SemanticSearch()
    semantic_search.vectorize_text(strings=all_chunks)
    result = semantic_search.search(sim_phrase, k=1)

    del semantic_search

    if verbose:
        print(len(result))

    context = result[0][0].page_content
    assert any(context in chunk for chunk in all_chunks)

    pred = pipe(question=question, context=context, do_sample=False, top_k=1)
    pred = pred['answer']

    print('---')
    print('Question:', question)
    print('Context:', context)
    print('Answer:', pred)
    print('postprocess_pattern:', postprocess_pattern)
    print('replace_patterns:', replace_patterns)
    print('output_type:', output_type)

    if postprocess_pattern is not None:
        pred = re.match(postprocess_pattern, pred)
        if pred:
            pred = pred.group(0)
        else:
            pred = None

    print('Answer after postprocessing:', pred)

    if pred is not None:
        for pattern in replace_patterns:
            pred = re.sub(pattern[0], pattern[1], pred)
        
    print('Answer after replacing:', pred)

    if output_type == 'float':
        if pred is not None:
            pred = float(pred)
        else:
            pred = -1
    elif output_type == 'int':
        if pred is not None:
            pred = int(pred)
        else:
            pred = -1
    elif output_type == 'str':
        if pred is not None:
            pred = str(pred)
    else:
        raise ValueError(f'Unknown output type: {output_type}')

    return pred

    # best_contexts = [r[0].page_content for r in result]

    # preds = []
    # for context in best_contexts:
    #     # generate 3 answers to the question
    #     pred = pipe(question=question, context=context, do_sample=False, top_k=3)

    #     pred = [p['answer'] for p in pred]
    #     preds.append(pred)
    # return preds


QUESTIONS_LOKATA = {
    'HihgestInterest': {
        'sim_phrase': "wysokość najwyższego oprocentowania promocyjnego na lokacie w %",
        'question': 'Jaka jest najwyższa wysokość oprocentowania promocyjnego na lokacie w %?',
        'postprocess_pattern': '\d+\s*((,|\.)\s*\d+)?\s*%',
        'replace_patterns': [(',', '.'), ('%', ''), ('\s+', '')],
        'output_type': 'float'
    },
    'Length': {
        'sim_phrase': 'długość trawania lokaty w miesiącach',
        'question': 'ile miesięcy trwa lokata?',
        'postprocess_pattern': '(\d+)',
        'replace_patterns': [(',', '.'), ('%', '')],
        'output_type': 'int',
    },
    'MaxPLN': {
        'sim_phrase': 'od ilu do ilu PLN można założyć lokatę z oprocentowaniem {}%',
        'question': 'jaka jest maksymalna kwota depozytu dla lokaty z oprocentowaniem {}%?',
        'postprocess_pattern': '[\d ]+',
        'replace_patterns': [('\s+', '')],
        'output_type': 'int'
    },
    'OfferType': {
        'sim_phrase': 'warunki skorzystania z lokaty o oprocentowaniu {}% (np. dla nowych klientów, na nowe środki)',
        'question': 'jakie są dodatkowe warunki skorzystania z lokaty o oprocentowaniu {}% (np. tylko dla nowych klientów, na nowe środki)?',
        'postprocess_pattern': None,
        'replace_patterns': [],
        'output_type': 'str'
    },
    # 'OfferType': {},
}

QUESTIONS_OSZCZED = {
    'HihgestInterest': {
        'sim_phrase': "wysokość najwyższego oprocentowania promocyjnego na koncie oszczędnościowym w %",
        'question': 'Jaka jest najwyższa wysokość oprocentowania promocyjnego na koncie oszczędnościowym w %?',
        'postprocess_pattern': '\d+\s*((,|\.)\s*\d+)?\s*%',
        'replace_patterns': [(',', '.'), ('%', ''), ('\s+', '')],
        'output_type': 'float'
    },
    'Length': {
        'sim_phrase': 'długość trawania promocyjnego oprocentowania na koncie oszczędnościowym w miesiącach',
        'question': 'ile miesięcy trwa promocyjne oprocentowanie na koncie oszczędnościowym?',
        'postprocess_pattern': '(\d+)',
        'replace_patterns': [(',', '.'), ('%', '')],
        'output_type': 'int'
    },
    'MaxPLN': {
        'sim_phrase': 'od ilu do ilu PLN można założyć konto oszczędnościowe z oprocentowaniem {}%',
        'question': 'jaka jest maksymalna kwota depozytu dla konta oszczędnościowego z oprocentowaniem {}%?',
        'postprocess_pattern': '[\d ]+',
        'replace_patterns': [('\s+', '')],
        'output_type': 'int'
    },
    'OfferType': {
        'sim_phrase': 'warunki skorzystania z konta oszczędnościowego o oprocentowaniu {}% (np. dla nowych klientów, na nowe środki)',
        'question': 'jakie są dodatkowe warunki skorzystania z konta oszczędnościowego o oprocentowaniu {}% (np. tylko dla nowych klientów, na nowe środki)?',
        'postprocess_pattern': None,
        'replace_patterns': [],
        'output_type': 'str'
    },
    # 'OfferType': {},
}


verbose = True 
df_urls = pd.read_excel('Bank_list.xlsx', index_col=0)
date = '18-11-2023'

model_name = "henryk/bert-base-multilingual-cased-finetuned-polish-squad2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
pipe = pipeline("question-answering", model=model_name)

chunker = TextChunker(tokenizer=tokenizer, max_len=400, stride_len=100)

if verbose:
    print('Max context length:', tokenizer.model_max_length)

all_results = []

for bank_name in df_urls['Name'].unique():
    for client_type in ['Individual', 'Corporation']:
        # if bank_name != 'Toyota Bank Polska SA':   
        #     continue
        if verbose:
            print('='*50)
            print('Bank name:', bank_name)
            print('Client type:', client_type)
            print('Date:', date)

        urls = df_urls.loc[df_urls['Name'] == bank_name, 'Individual'].dropna().tolist()
        print('urls:', urls)
        lokata_data_all = []
        oszczed_data_all = []
        for url in urls:
            base_url = '/'.join(url[:3])
            parser = HTMLBankParser(url)
            lokata_data, oszczed_data, lokata_table, oszczed_table, lokata_links, oszczed_links = parser.get_outputs()

            lokata_links = proces_links(lokata_links, base_url, only_pdfs=True)
            oszczed_links = proces_links(oszczed_links, base_url, only_pdfs=True)

            lokata_data_all.extend(choose_best_data(lokata_data, lokata_table, lokata_links, 'lokata'))
            oszczed_data_all.extend(choose_best_data(oszczed_data, oszczed_table, oszczed_links, 'oszczędnościowe'))


        lokata_chunks = get_chunks(lokata_data_all, chunker, verbose=verbose)
        oszczed_chunks = get_chunks(oszczed_data_all, chunker, verbose=verbose)

        sim_phrase = "wysokość oprocentowania promocyjnego na lokacie w %"
        question = 'Jakie lokaty oferuje bank?'

        d = {}
        d['Bank'] = bank_name
        d['Client type'] = client_type
        d['Date'] = date

        print('chunks:', oszczed_chunks)

        if lokata_chunks:
            d_lokata = dict(d) # copy
            questions_copy = dict(QUESTIONS_LOKATA)
            for key, args in questions_copy.items():
                if key in ['MaxPLN', 'OfferType']:
                    args = dict(args)
                    perc = d_lokata['HihgestInterest']
                    if perc == -1:
                        perc = 'największym'
                    perc = str(perc).replace('.', ',')

                    args['sim_phrase'] = args['sim_phrase'].format(perc)
                    args['question'] = args['question'].format(perc)
                d_lokata[key] = do_qa(lokata_chunks, **args)
            all_results.append(d_lokata)

        if oszczed_chunks:
            d_oszczed = dict(d) # copy
            questions_copy = dict(QUESTIONS_OSZCZED)
            for key, args in questions_copy.items():
                if key in ['MaxPLN', 'OfferType']:
                    args = dict(args)
                    perc = d_lokata['HihgestInterest']
                    if perc == -1:
                        perc = 'największym'
                    perc = str(perc).replace('.', ',')

                    args['sim_phrase'] = args['sim_phrase'].format(perc)
                    args['question'] = args['question'].format(perc)
                d_oszczed[key] = do_qa(oszczed_chunks, **args)
            all_results.append(d_oszczed)

        torch.cuda.empty_cache()
        gc.collect()

    df_results = pd.DataFrame(all_results)
    df_results.to_csv('results.csv', index=False)

    
