
from flask import Flask, request, render_template, jsonify, send_from_directory
from gtts import gTTS
import os
import re
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from urllib.parse import quote

app = Flask(__name__)

# Path to save audio files
AUDIO_DIR = 'static/audio'
os.makedirs(AUDIO_DIR, exist_ok=True)


def text_to_speech(text, audio_path, language):
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(audio_path)


def add_to_df(times_of_success, phrase_id, time):
    # Define the path to the CSV file
    csv_file_path = 'flask/zsuccess_times.csv'

    # Convert the list of times_of_success to a string
    times_of_success_str = str(times_of_success)

    # Create a DataFrame from the times_of_success and phrase_id
    new_data = {'phrase_id': [phrase_id], 'times_of_success': [times_of_success_str], 'time': [time]}
    new_df = pd.DataFrame(new_data)

    # Check if the CSV file already exists
    if os.path.exists(csv_file_path):
        # If it exists, read the existing data
        try:
            existing_df = pd.read_csv(csv_file_path)
        except pd.errors.EmptyDataError:
            existing_df = pd.DataFrame(columns=['phrase_id', 'times_of_success', 'time'])

        # Append the new data
        existing_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Save the updated DataFrame back to the CSV file
        existing_df.to_csv(csv_file_path, mode='w', header=True, index=False)
    else:
        # If it doesn't exist, create a new file with the header
        new_df.to_csv(csv_file_path, mode='w', header=True, index=False)



def get_phrases_phrase_positions_and_full_text_from_csv(csv_file_path):

    df = pd.read_csv(csv_file_path)
    phrases = df['phrase'].tolist()
    phrase_positions = df['position'].tolist()
    full_text = ''.join(df['corresponding_text'].tolist())
    return phrases, phrase_positions, full_text


#phrases, phrase_positions, full_text = get_phrases_phrase_positions_and_full_text_from_csv()
class Book:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.phrases, self.phrase_positions, self.full_text , self.corresponding_texts = self._load_data_from_csv()


    def _load_data_from_csv(self):
        df = pd.read_csv(self.csv_file_path)
        phrases = df['phrase'].tolist()
        #phrase_positions = df['position'].tolist()
        phrase_positions = 0
        full_text = ''.join(df['corresponding_text'].tolist())
        return phrases, phrase_positions, full_text , df['corresponding_text'].tolist()

books = {}
books_dir = 'flask/static/books'
for book_name in os.listdir(books_dir):
    book_path = os.path.join(books_dir, book_name, 'book.csv')
    if os.path.isfile(book_path):
        books[book_name] = Book(book_path)


@app.route('/book_list')
def books_list():
    book_names = books.keys()
    book_list_html = "<ul>"
    for book_name in book_names:
        book_list_html += f'<li><a href="/?i=0&language={book_name[-2:]}&book_name={book_name}">{book_name}</a></li>'
    book_list_html += "</ul>"


    return f"<html><body><h1>Book List</h1>{book_list_html}</body></html>"
    return "<html><body><h1>Hello, World!</h1></body></html>"
@app.route('/')
def index():
    phrase_id = request.args.get('i', default=0, type=int)
    # http://127.0.0.1:5000/?i=100?livre=pp
    book_name = request.args.get('book_name', type=str)

    book = books[book_name]
    phrases = book.phrases
    corresponding_texts = book.corresponding_texts
    phrase_positions = book.phrase_positions
    full_text = book.full_text


    phrase = phrases[phrase_id] if 0 <= phrase_id < len(phrases) else f"Phrase not found.{len(phrases)}"
    text = full_text
    text = text.replace('"', '´')

    

    print(corresponding_texts[:phrase_id])
    all_text_before = json.dumps(''.join(corresponding_texts[:phrase_id]))
    
    return render_template('index.html', phrase=phrase, all_text_before = all_text_before,phrases_before = [], phrases_after = phrases[phrase_id+1:], phrase_id=phrase_id, total_phrases=len(phrases), book_name=book_name)

@app.route('/define', methods=['POST'])
def define():
    french_word = request.form.get('word', '').strip()
    definition = get_french_definition(french_word)
    return jsonify({'definition': definition})



@app.route('/log', methods=['POST'])
def log():
    data = request.get_json()
    timestamp = data.get('timestamp')
    time_of_success = data.get('time_of_success')
    entered_chars = data.get('entered_chars')
    entered_times = data.get('entered_times')
    book_name = data.get('book_name')
    print(f"Book Name: {book_name}")
    failure_ids = data.get('failure_ids', [])
    failure_times = data.get('failure_times', [])
    failure_chars = data.get('failure_chars', [])
    phrase_id = data.get('phrase_id')

    print(f"Entered Chars: {entered_chars}")
    print(f"Entered Times: {entered_times}")
    print(f"Timestamp: {timestamp}")
    print(f"Time of Success: {time_of_success}")
    print(f"Failure IDs: {failure_ids}")
    print(f"Failure Times: {failure_times}")
    print(f"Failure Chars: {failure_chars}")
    print(f"phrase_id: {phrase_id}")


    log_data = {
        'timestamp': timestamp,
        'time_of_success': time_of_success,
        'failure_ids': failure_ids,
        'failure_times': failure_times,
        'failure_chars': failure_chars,
        'entered_chars': entered_chars,
        'entered_times': entered_times,
        'phrase_id': phrase_id
    }

    json_file_path = f'flask/static/books/{book_name}/data.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.append(log_data)

    with open(json_file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

    return jsonify({'status': 'success'})


@app.route('/speak', methods=['POST'])
def speak():
    try:
        print("creating audio")
        text = request.form.get('text', '')
        language = request.form.get('language', '')
        audio_filename = language+quote(text.replace(' ', '_') + '.mp3')  # Create a unique filename based on the text and encode it
        audio_path = os.path.join("flask/"+AUDIO_DIR, audio_filename)
        text_to_speech(text, audio_path,language)
        return jsonify({'audio_url': f'/audio/{audio_filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory(AUDIO_DIR, quote(filename))

def get_french_definition__(french_word):
    try:
        url = f"https://www.larousse.fr/dictionnaires/francais/{quote(french_word)}"
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Unable to fetch the definition. Status code: {response.status_code}"
        soup = BeautifulSoup(response.content, 'html.parser')
        definition_block = soup.find('article', class_="BlocDefinition")
        if definition_block:
            definition = definition_block.get_text(separator=' ').strip()
            return definition
        else:
            return f"No definition found for '{french_word}' on Larousse."
    except Exception as e:
        return f"An error occurred: {e}"



def get_french_definition(french_word):
    french_word = french_word.lower()
    url = f"https://fr.wiktionary.org/w/api.php"

    params = {
        'action': 'query',
        'prop': 'extracts',
        'titles': french_word,
        'format': 'json',
        'explaintext': False
        ,'exsectionformat': 'raw'
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Error fetching the definition for {french_word}"

    data = response.json()
    pages = data.get('query', {}).get('pages', {})
    if not pages:
        return f"No definition found for {french_word}"

    for page_id, page_info in pages.items():
        definition = page_info.get('extract', '')
        return definition

if __name__ == '__main__':
    app.run(debug=True)