# A ideia é que os valores de phrases, phrase_positions e full_text sejam obtidos a partir de um arquivo CSV.
# O arquivo CSV é gerado a partir de um arquivo de texto (livre.txt) que contém o texto completo.
# Assim, o arquivo CSV contém as frases, as posições das frases e o texto completo.
# O texto completo é obtido a partir dos Corresponding Texts, que são as partes do texto que correspondem a cada frase.

# The idea is that the values of phrases, phrase_positions, and full_text are obtained from a CSV file.
# The CSV file is generated from a text file (livre.txt) that contains the complete text.
# Thus, the CSV file contains the phrases, the positions of the phrases, and the complete text.
# The complete text is obtained from the Corresponding Texts, which are the parts of the text that correspond to each phrase.



from flask import Flask, request, render_template, jsonify, send_from_directory
from gtts import gTTS
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import json
import unicodedata


import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

import requests
import pandas as pd
import sys


def remove_non_printable(text):
    def is_printable(char):
        return unicodedata.category(char) not in ('Cc', 'Cf')
    return ''.join(filter(is_printable, text))

def text_to_phrases_and_phrase_positions(text):
    f_text = text
    text = text.replace('...', '<e>')
    text = text.replace('"', '´')
    phrases = []
    phrase_positions = []
    for match in re.finditer(r'[^.,;()\n]+', text):
        if (len(match.group()) > 1):
            phrases.append(match.group())  # Extract the phrase and strip any surrounding whitespace
            phrase_positions.append(match.start())  # Get the starting position of the phrase

    phrases = [phrase for phrase in phrases if len(phrase) > 1]
    phrases = [phrase.replace('<e>', '...') for phrase in phrases]
    phrases = [remove_non_printable(phrase) for phrase in phrases]
    phrases = [phrase.strip() for phrase in phrases]

    return phrases, phrase_positions



def create_book_folder_from_txt(file_name):
               
    file_path = 'flask/' + file_name

    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        print(f" livre")
        content = file.read()

        phrases, phrase_positions  = text_to_phrases_and_phrase_positions(content)

        corresponding_texts = []
        for phrase_id in range(1,len(phrases)):
            corresponding_texts.append(content[phrase_positions[phrase_id-1]:phrase_positions[phrase_id]])
        corresponding_texts.append(content[phrase_positions[-1]:])
        df = pd.DataFrame(phrases, columns=['phrase'])
        df['id'] = range(len(df))
        df['position'] = phrase_positions
        df['corresponding_text'] = corresponding_texts

        directory = 'flask/static/books/' + file_name[:-4]
        if not os.path.exists(directory):
            os.makedirs(directory)


        df.to_csv('flask/static/books/' + file_name[:-4] +'/book.csv', index=False)

        # Compare the concatenated corresponding_texts with the original content
        concatenated_texts = ''.join(corresponding_texts)
        if concatenated_texts == content:
            print("The concatenated corresponding_texts match the original content.")
        else:
            print("The concatenated corresponding_texts do not match the original content.")
            for i, (c1, c2) in enumerate(zip(concatenated_texts, content)):
                if c1 != c2:
                    print(f"Difference at position {i}: '{c1}' != '{c2}'")
                    print(phrase_positions[0])
                    print(content[0:10])
                    break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_book_folder.py <book_name.txt>")
    else:
        create_book_folder_from_txt(sys.argv[1])


