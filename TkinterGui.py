import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
from googleplaces import GooglePlaces, types, lang
import requests

intents = json.loads(open('intents.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
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
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
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
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
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
from tkinter import ttk

def Check_Symptom():
    def send():
        msg = EntryBox.get("1.0",'end-1c').strip()
        EntryBox.delete("0.0",END)

        if msg != '':
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, "You: " + msg + '\n\n')
            ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
    
            res = chatbot_response(msg)
            ChatLog.insert(END, "DoctorBot: " + res + '\n\n')
            
            ChatLog.config(state=DISABLED)
            ChatLog.yview(END)
    windows = Tk()
    windows.title("Symptom Checker")
    windows.geometry("400x500")
    windows.resizable(width=FALSE, height=FALSE)

#Create Chat window
    ChatLog = Text(windows, bd=0, bg="white", height="8", width="50", font="Arial",)

    ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
    scrollbar = Scrollbar(windows, command=ChatLog.yview, cursor="heart")
    ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message
    SendButton = Button(windows, font=("Verdana",12,'bold'), text="Send", width="12", height=5,bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff', command= send )

#Create the box to enter message
    EntryBox = Text(windows, bd=0, bg="white",width="29", height="5", font="Arial")
#EntryBox.bind("<Return>", send)


#Place all components on the screen
    scrollbar.place(x=376,y=6, height=386)
    ChatLog.place(x=6,y=6, height=386, width=370)
    EntryBox.place(x=128, y=401, height=90, width=265)
    SendButton.place(x=6, y=401, height=90)
    windows.mainloop()

def display_hospitals():
    root = Tk()
    root.geometry("400x500")
    root.resizable(width=FALSE, height=FALSE)
    root.title("Near-by Hospitals")


    API_KEY = "API_KEY"
    google_places = GooglePlaces(API_KEY)

    query_result = google_places.nearby_search(lat_lng ={'lat': 51.8787, 'lng': -0.4200},radius = 5000,types =[types.TYPE_HOSPITAL])
#for place in query_result.places:
    #place.get_details()
    #show_hospital = (place.name + '\n', place.international_phone_number, '\n', place.website, '\n', place.url )
# Insert elements into the listbox
# Creating a Listbox and
# attaching it to root window
#listbox = show_hospital
    listbox = Listbox(root)

# Adding Listbox to the left
# side of root window
#listbox.pack(side = LEFT, fill = BOTH)
    listbox.place(x=6,y=6, height=466, width=370)

# Creating a Scrollbar and
# attaching it to root window

#scrollbar = Scrollbar(root)

# Adding Scrollbar to the right
# side of root window

#scrollbar.pack(side = RIGHT, fill = BOTH)

    scrollbar =ttk.Scrollbar(root, orient='vertical', command=listbox.yview)
    listbox['yscrollcommand'] = scrollbar.set
    scrollbar.place(x=376,y=6, height=466)



    for place in query_result.places:
        place.get_details()
        listbox.insert(END, '\n', place.name, '\n', place.international_phone_number, '\n', place.website, '\n', place.url )
	
# Attaching Listbox to Scrollbar
# Since we need to have a vertical
# scroll we use yscrollcommand
    listbox.config(yscrollcommand = scrollbar.set)

# setting scrollbar command parameter
# to listbox.yview method its yview because
# we need to have a vertical view
    scrollbar.config(command = listbox.yview)

    root.mainloop()    
   
base = Tk()
base.title("DoctorBot")
Welcome_user=Label(base, font=("Verdana",10), text="Welcome user, how may I assist you today?", bg="#000000", activebackground="#3c9d9b", fg='#ffffff')
Welcome_user.grid()
Symptom_Checker= Button(base, font=("Verdana",12,'bold'), text="Check Symptoms", bg="#32de97", activebackground="#3c9d9b", fg='#ffffff', command= Check_Symptom)
Symptom_Checker.grid()
nearest_hospital= Button(base, font=("Verdana",12,'bold'), text="Find nearest hospitals", bg="#4242ff", activebackground="#3c9d9b", fg='#ffffff', command=display_hospitals)
nearest_hospital.grid()
base.mainloop()
