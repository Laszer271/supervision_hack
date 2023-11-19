import requests
from bs4 import BeautifulSoup
import re
import math

def get_raw_content(url, verbose=False):
    resp = requests.get(url)
    if verbose:
        print(resp.encoding)
    resp = resp.text

    soup = BeautifulSoup(resp, 'lxml').text
    if verbose:
        print(len(soup))

    return soup


def remove_non_ascii(text):
    soup = ''.join(letter for letter in text if letter.isascii() or letter.lower() in {'ś', 'ż', 'ź', 'ć', 'ą', 'ę', 'ł', 'ń', 'ó'})
    return soup


def split_on_newline(text):
    splitted = re.split('\n', text)
    splitted = [s for s in splitted if s != '' and not s.isspace()]
    return splitted


class TextChunker():
    def __init__(self, tokenizer, max_len, stride_len):
        self.max_len = max_len
        self.stride_len = stride_len
        self.tokenizer = tokenizer

    def split_text(self, splitted_text):
        # 3. Split it into chunks of N tokens
        enc_splitted = [self.tokenizer.encode(s) for s in splitted_text]

        # Ensure that the chunks are not longer than the model's max length
        enc_splitted_processed = []
        for s in enc_splitted:
            n_splits = 1
            while math.ceil(len(s) / n_splits) > self.max_len:
                n_splits += 1
            
            l = len(s)
            len_per_split = l // n_splits
            for i in range(n_splits):
                idx = i * len_per_split
                if i == n_splits - 1:
                    assert len(s[idx:]) <= self.max_len
                    enc_splitted_processed.append(s[idx:])
                else:
                    enc_splitted_processed.append(s[idx: idx + len_per_split])

        chunks = []
        buffer = []
        buffer_len = 0
        for i, current in enumerate(enc_splitted_processed):
            assert len(current) <= self.max_len, f"Current chunk is too long: {len(current)}"
            # is_last = i == len(enc_splitted_processed) - 1

            if (buffer_len + len(current) <= self.max_len):
                # Add current to the buffer as long as it fits in self.max_len
                buffer.append(current)
                buffer_len += len(current)
            else:
                current_chunk = '\n'.join(self.tokenizer.decode(b) for b in buffer)
                current_chunk = current_chunk.replace('[CLS]', '').replace('[SEP]', '')
                current_chunk = re.sub('(?<=\d), (?=\d)', ',', current_chunk)
                current_chunk = current_chunk.strip()
                chunks.append(current_chunk)

                # delete appropriate number of tokens from the buffer from left
                to_delete = max(self.stride_len, buffer_len + len(current) - self.max_len)
                deleted = 0
                while len(buffer) and (deleted < to_delete):
                    deleted += len(buffer[0])
                    buffer = buffer[1:]
                buffer_len -= deleted

                buffer.append(current)
                buffer_len += len(current)

        # additionally append the last chunk
        assert sum([len(current) for current in buffer]) <= self.max_len, f"Current chunk is too long: {len(current)}"
        current_chunk = '\n'.join(self.tokenizer.decode(b) for b in buffer)
        current_chunk = current_chunk.replace('[CLS]', '').replace('[SEP]', '')
        current_chunk = re.sub('(?<=\d), (?=\d)', ',', current_chunk)
        current_chunk = current_chunk.strip()
        chunks.append(current_chunk)

        return chunks

    
