var phrase = JSON.parse('{{ phrase|tojson|safe }}');
var time_of_succes = new Array(phrase.length).fill(null);
var language = new URLSearchParams(window.location.search).get('language');
var failure_ids = [];
var failure_times = [];
var failure_chars = [];
var entered_chars = [];
var entered_times = [];
var pageLoadTime;

window.onload = function() {
    //submitSpeak(phrase);
    
    pageLoadTime = new Date().getTime();
    document.getElementById('guess').focus();
    displayAllTextBefore();
    displayPhrasesBefore();

    if (phrase[0] == '{')
    {
        const i = parseInt(new URLSearchParams(window.location.search).get('i'));
        const language = (new URLSearchParams(window.location.search).get('language'));
        const book_name = new URLSearchParams(window.location.search).get('book_name');
        const nextUrl = `${window.location.origin}/?language=${language}&book_name=${book_name}&i=${i + 1}`;
        window.location.href = nextUrl;
    }

    window.scrollTo(0, document.body.scrollHeight);
    loadSpeak(phrase,language);
    handleInput();
};

function submitDefinition() {

    //alert(document.getElementById('word').value);
    var word = document.getElementById('word').value;
    word = word.toLowerCase();

    if (!word) {
        //alert('Please enter a word');
        document.getElementById('DictPage').style.display = 'none';
        return;
    }
    else{
        document.getElementById('DictPage').style.display = 'block';
    }

    var iframe = document.getElementById('DictPage').getElementsByTagName('iframe')[0];
    iframe.src = `https://${language}.wiktionary.org/wiki/${word}`;
    
    
    //$.post('/define', $('#define-form').serialize(), function(data) {
    //    $('#definition').text(data.definition);
    //});
}

function submitSpeak(text, language) {
    $.post('/speak', { text: text , language: language}, function(data) {
        if (data.audio_url) {
            $('#audio-player').attr('src', data.audio_url);
            $('#audio-player')[0].play();
        }
    });
}
function loadSpeak(text, language) {
    $.post('/speak', { text: text , language: language}, function(data) {
        if (data.audio_url) {
            $('#audio-player').attr('src', data.audio_url);
        }
    });
}



$(document).on('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
    }
});

function maskPhrase(phrase) {
    return phrase.replace(/[a-zA-ZÀ-ÿ]/g, '#');
}

$('#masked-phrase').on('click', function() {


var selectedText = window.getSelection().toString();
 if (selectedText) {
var fullText = $('#masked-phrase').text(); // Get the full text of the div
var selection = window.getSelection();
var range = selection.getRangeAt(0);
var startOffset = range.startOffset;

// Calculate the position of the selected text in relation to the full text
var relativePosition = fullText.indexOf(selectedText, startOffset);

var selectedSubstring = phrase.substring(relativePosition, relativePosition + selectedText.length);
var MaskedSelectedSubstring = fullText.substring(relativePosition, relativePosition + selectedText.length);


if (MaskedSelectedSubstring.includes('#')) {
    submitSpeak(selectedSubstring,language);
}
else{
    var selectedWord = window.getSelection().toString();
    if (selectedWord) {
        $('#word').val(selectedWord);
        submitDefinition();
    }
}

submitDefinition();
}
});

$('#all-text-before-container').on('click', function() {
    var selectedWord = window.getSelection().toString();
    if (selectedWord) {
        $('#word').val(selectedWord);
        submitDefinition();
    }
});

$('#definition').on('click', function() {
    var selectedWord = window.getSelection().toString();
    if (selectedWord) {
        $('#word').val(selectedWord);
        submitDefinition();
    }
});
let lastGuessSize = 0;    
let isupdating = false;



$('#guess').on('input', handleInput);

function handleInput() {

if (isupdating) {
    return;
}
isupdating = true;

submitDefinition();
$('#word').val("");
let phrase_d = '';


let phrase_m = $('#masked-phrase').text();


let phrase_a = document.getElementById('guess').textContent;  
phrase_a = phrase_a.replace(/\n/g, '');  // Remove newlines
phrase_a = phrase_a.replace('  ', ' ');


// detect if the user deleted a character
let deletou = false;
if (phrase_a.length < lastGuessSize) {
    //alert('DELETOUUU');
    deletou = true;
    entered_chars.push("<");
    entered_times.push(new Date().getTime() - pageLoadTime);
    //return;
}
lastGuessSize = phrase_a.length;

// dectect if the user added a space, if so remove it 
if (phrase_a.length > 0 && (phrase_a[phrase_a.length - 1] === ' ' || phrase_a[phrase_a.length - 1] === '\n' || phrase_a[phrase_a.length - 1] === "\u00a0") )  {
    //alert('Please do not end your guess with a space');
    phrase_a = phrase_a.trimEnd();
    //return;
}


//alert('ultima letra:'+phrase_a.length);

let wrong_character = '';
for (let i = 0; i < phrase.length; i++) 
{
    let char_d;
    if (i >= phrase_a.length) 
    {
        char_d = phrase_m[i];
    } 
    else 
    {
        const char_a = phrase_a[i] || '';
        const char = phrase[i];

        const l_char = char.toLowerCase();
        const l_char_a = char_a.toLowerCase();
        if (l_char === l_char_a) 
        {
            
            if (time_of_succes[i] === null)
            {
                entered_chars.push(char);
                entered_times.push(new Date().getTime() - pageLoadTime);
                time_of_succes[i] = new Date().getTime() - pageLoadTime;
            }
            char_d = char;
        } 
        else 
        {
            wrong_character = char_a;
            char_d = phrase_m[i];
        }
    }
    phrase_d += char_d;
}
const firstHashIndex = phrase_d.indexOf('#') !== -1 ? phrase_d.indexOf('#') : phrase_d.length;
let substringUntilFirstHash = phrase_d.substring(0, firstHashIndex);

if(substringUntilFirstHash.length > phrase_a.replace('\n','').length){
    //if (substringUntilFirstHash[substringUntilFirstHash.length-1] != ' '){   
    console.log('fiz!');     
    document.getElementById('guess').focus();
    document.execCommand('selectAll', false, null);
    document.execCommand('delete', false, null);
    document.execCommand('insertText', false,substringUntilFirstHash);
//}
}
else{
    if(wrong_character != ''){
        if (deletou === false)
        {
            console.log('Error: Incorrect character entered:', wrong_character);
            console.log('Error: Incorrect character entered:', phrase_a.length);
            failure_chars.push(wrong_character);
            failure_ids.push(phrase_a.length);
            failure_times.push(new Date().getTime() - pageLoadTime);
            entered_chars.push(wrong_character);
            entered_times.push(new Date().getTime() - pageLoadTime);
        }
    }
}   


//document.execCommand('insertText', false, 'Text to insert');



// Set text preserving newlines and spaces
$('#masked-phrase').text(phrase_d);



//document.getElementById('guess').innerText = substringUntilFirstHash;  // Use innerText for setting content

// Move caret to the end
const guessDiv = document.getElementById('guess');
const range = document.createRange();
const sel = window.getSelection();
range.selectNodeContents(guessDiv);
range.collapse(false);  // false to set caret at the end of the content
sel.removeAllRanges();
sel.addRange(range);


phrase_m = $('#masked-phrase').text();
if (phrase_m === phrase) {

const i = parseInt(new URLSearchParams(window.location.search).get('i'));
const book_name = new URLSearchParams(window.location.search).get('book_name');
const language = new URLSearchParams(window.location.search).get('language');


// Submit the times_of_succes using POST request with JSON content type
const timestamp = new Date().toISOString(); // Get the current timestamp
time_of_succes.pop();

$.ajax({
    url: '/log',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
    timestamp: timestamp,
    time_of_success: time_of_succes,
    failure_ids: failure_ids,
    failure_times: failure_times,
    failure_chars: failure_chars,
    entered_chars: entered_chars,
    entered_times: entered_times,
    phrase_id: i,
    book_name: book_name,
    }),
    success: function(response) {
        console.log('Log successfully sent:', response);
        // Redirect after successful AJAX request
        const nextUrl = `${window.location.origin}/?language=${language}&book_name=${book_name}&i=${i + 1}`;
        window.location.href = nextUrl;
    },
    error: function(error) {
    console.error('Error logging data:', error);
    }
    
});
}

isupdating = false;
}



var masked_phrase = maskPhrase(phrase);
$('#masked-phrase').text(masked_phrase);

var phrases_before = [] //JSON.parse('{{ phrases_before|tojson|safe }}');




function displayPhrasesBefore() {
var container = $('#phrases-before-container');
phrases_before.forEach(function(phrase) {
    var div = $('<div></div>').text(phrase).css({
        'font-size': 'inherit',
        'padding': '5px 0'
    });
    container.append(div);
});
}

function displayAllTextBefore() {
    // Use a proper string or pass the value via templating engine
    var all_text_before = `{{ all_text_before|escapejs }}`;

    // Replace newlines with <br>
    all_text_before = all_text_before.replace(/\n/g, '<br>');

    // Replace {something} with an <img> tag
    all_text_before = all_text_before.replace(/{([^}]+)}/g, function(match, p1) {
        return `<br><img src="static/images/${p1}.png" style="display: block; margin: 0 auto;">`;
    });

    // Set the content inside the container
    var container = $('#all-text-before-container');
    container.html(all_text_before);
}




function handleGuess() {
$('#word').val("");
submitDefinition();


const phrase_m = $('#masked-phrase').text();
if (phrase === phrase_m) {
const i = parseInt(new URLSearchParams(window.location.search).get('i'));
const book_name = new URLSearchParams(window.location.search).get('book_name');
const language = new URLSearchParams(window.location.search).get('language');


// Submit the times_of_succes using POST request with JSON content type
const timestamp = new Date().toISOString(); // Get the current timestamp
time_of_succes.pop();

$.ajax({
    url: '/log',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
    timestamp: timestamp,
    time_of_success: time_of_succes,
    failure_ids: failure_ids,
    failure_times: failure_times,
    failure_chars: failure_chars,
    
    phrase_id: i,
    book_name: book_name,
    }),
    success: function(response) {
        console.log('Log successfully sent:', response);
        
        // Redirect after successful AJAX request
        const nextUrl = `${window.location.origin}/?language=${language}&book_name=${book_name}&i=${i + 1}`;
        window.location.href = nextUrl;
    },
    error: function(error) {
    console.error('Error logging data:', error);
    }
    
});
} else {

// If guess is incorrect, increment counter
if (typeof handleGuess.counter === 'undefined') {
    handleGuess.counter = 0;
}
handleGuess.counter++;
submitSpeak(phrase,language); 
}
}