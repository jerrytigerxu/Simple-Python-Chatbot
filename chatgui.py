
import nltk
from nltk.stem import WordNetLemmatizer
from numpy.lib.arraysetops import isin
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from tensorflow import keras
from datetime import date, datetime
import json
import random
import time
from threading import Thread
#from keras.models import load_model


model = keras.models.load_model('chatbot_model.h5')

intents = json.loads(open('intents.json').read())
user = json.loads(open('user.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


EVENT_DICT = {
    'christmas': '2000/12/25',
    'birthday': user['birthday'],
    'work_aniversary': user['work_aniversary']
}

REMINDER_DICT = {
    'drink_water': 0.5,
    'stand_up': 2.0,
    'walk': 3.0,
    'do_exercise': 4.0
}

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):  
            if w[:-1] == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent'][:-1]
    list_of_intents = intents_json['intents']
    result = ''
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

def getResponseFromTag(tag, intents_json):
    list_of_intents = intents_json['intents']
    result = ''
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res


#Creating GUI with tkinter
import tkinter
from tkinter import *


def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

        res = chatbot_response(msg)
        ChatLog.insert(END, "Bot: " + res + '\n\n')

        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)

def call_event(event):
    try:
        ChatLog.config(state=NORMAL)
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

        res = getResponseFromTag(event, intents)
        ChatLog.insert(END, "Bot: " + res + '\n\n')

        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
    except: 
        pass

def call_reminder(sleep_time, event):
    time.sleep(sleep_time * 60) # Sleep_time is in minute
    call_event(event)

def call_str(str):
    ChatLog.config(state=NORMAL)
    ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

    ChatLog.insert(END, str)

    ChatLog.config(state=DISABLED)
    ChatLog.yview(END)

isInit = True
reminder_list = []
base = Tk()
base.title("CareU")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)

ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message
SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
                    command = send )

#Create the box to enter message
EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial")
#EntryBox.bind("<Return>", send)


#Place all components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)

if isInit:
    temp_str = 'Bot: Greetings to you, ' + user['username'].split()[-1] + '\n\n'
    call_str(temp_str)
    
    for reminder in list(REMINDER_DICT.keys()):
        t = Thread(target=call_reminder, args=(REMINDER_DICT[reminder], reminder,))
        reminder_list.append(t)
        reminder_list[-1].start()

    isInit = False

for event in list(EVENT_DICT.keys()):
    if (datetime.strptime(EVENT_DICT[event], '%Y/%m/%d').day == date.today().day and 
        datetime.strptime(EVENT_DICT[event], '%Y/%m/%d').month == date.today().month):
        call_event(event)

EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

base.mainloop()
