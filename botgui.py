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
import threading
import tkinter
from tkinter import *
import helpers as helpers
import pyaudio
import wave
import speech_recognition as sr

from PIL import ImageTk, Image

class GUI(Frame):

	chunk = 1024 
	sample_format = pyaudio.paInt16 
	channels = 2
	fs = 44100  

	def __init__(self) -> None:

		# int resources
		self.intents = json.loads(open('intents.json').read())
		self.user = json.loads(open('user.json').read())
		self.words = pickle.load(open('words.pkl','rb'))
		self.classes = pickle.load(open('classes.pkl','rb'))
		self.model = keras.models.load_model('chatbot_model.h5')
		self.YEARLY_EVENT_DICT = {
			'christmas': '2000/12/25',
			'birthday': self.user['birthday'],
			'work_aniversary': self.user['work_aniversary']
		}
		self.DAILY_EVENT_DICT = {
			'ask_employee': '21:50'
		}
		self.REMINDER_DICT = {
			'drink_water': 0.5,
			'stand_up': 60.0,
			'walk': 60.0,
			'do_exercise': 60.0
		}
		self.p = pyaudio.PyAudio()
		self.frames = []

		# chat window which is currently hidden
		self.chat_window = Tk()
		self.chat_window.withdraw()

		# hello window
		self.hellow_window = Toplevel()
	
		# set hello window as midle screen
		w = 400 
		h = 400
		ws = self.hellow_window.winfo_screenwidth() # width of the screen
		hs = self.hellow_window.winfo_screenheight() # height of the screen
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		self.hellow_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

		bg = ImageTk.PhotoImage(Image.open("./resources/images/Background2.jpg"))

		# Show image using label
		label1 = Label(self.hellow_window, image = bg)
		label1.place(x = 0, y = 0)
	
		# set the title
		self.hellow_window.title("CareU")
		self.hellow_window.resizable(width = False,
							height = False)
		self.hellow_window.configure(width = w,
							height = h)

		# create a hello string user Label and place it
		hello_str = "Greetings to you, " + helpers.get_user_name()
		# hello_str = self.getResponseFromTag('inspiration', self.intents)
		self.pls = Label(self.hellow_window,
					text = hello_str,
					justify = CENTER,
					font = "Helvetica 14 bold")
		self.pls.place(relheight = 0.15,
					relx = 0.2,
					rely = 0.07)

		# BotGui image say hi
		bot_say_hi_img = ImageTk.PhotoImage(Image.open("./resources/images/ava.jpg"))
		bot_say_hi_label = Label(
			self.hellow_window,
			image=bot_say_hi_img,
		)
		bot_say_hi_label.place(
			relheight = 0.50,
			relwidth = 0.60,
			relx = 0.2,
			rely = 0.25
		)

		# create a Miss You Button
		# along with action
		self.go = Button(
			self.hellow_window,
			text = "Let's talk!",
			font = "Helvetica 14 bold",
			command = lambda: self.goAhead(helpers.get_user_name()),
		)

		self.go.place(
			relx = 0.4,
			rely = 0.8
		)

		# chat window run
		self.chat_window.mainloop()

		#auto event

	def call_str(self, str):
		self.textCons.config(state=NORMAL)
		self.textCons.config(foreground="#442265", font=("Verdana", 12))

		self.textCons.insert(END, str)

		self.textCons.config(state=DISABLED)
		self.textCons.yview(END)


	def goAhead(self, name):
		self.hellow_window.destroy()
		self.layout_chat_window(name)

	# The main layout of the chat
	def layout_chat_window(self, name):
	
		self.name = name
		# to show chat window123
		self.chat_window.deiconify()

		# set hello window as midle screen
		w = 500 
		h = 550
		ws = self.chat_window.winfo_screenwidth() # width of the screen
		hs = self.chat_window.winfo_screenheight() # height of the screen
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		self.chat_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
		self.chat_window.title("CareU3000")
		self.chat_window.resizable(width = False,
							height = False)
		self.chat_window.configure(width = 470,
							height = 550,
							bg = "#17202A")

		# Show user name
		self.labelHead = Label(
			self.chat_window,
			text = self.name ,
			font = "Helvetica 13 bold",
			pady = 5
		)
		self.labelHead.place(relwidth = 1)

		# Line
		self.line = Label(self.chat_window,
						width = 450,
						bg = "#ABB2B9")
		self.line.place(relwidth = 1,
						rely = 0.07,
						relheight = 0.012)
		
		# ChatLog
		self.textCons = Text(self.chat_window,
							width = 20,
							height = 2,
							font = "Helvetica 14",
							padx = 5,
							pady = 5)
		
		self.textCons.place(relheight = 0.745,
							relwidth = 1,
							rely = 0.08)
		
		self.labelBottom = Label(self.chat_window,
								bg = "#ABB2B9",
								height = 80)
		
		self.labelBottom.place(relwidth = 1,
							rely = 0.825)
		
		self.entryMsg = Text(self.labelBottom,
							font = "Helvetica 13")
		
		# place the given widget
		# into the gui window
		self.entryMsg.place(relwidth = 0.74,
							relheight = 0.06,
							rely = 0.008,
							relx = 0.011)
		
		self.entryMsg.focus()

		# create record Button
		self.record_button = Button(
			self.labelBottom,
			text = "Record",
			font = "Helvetica 10 bold",
			width = 10,
			bg = "#ABB2B9",
			command = lambda : self.startrecording()
		)

		self.record_button.place(
			relx = 0.70,
			rely = 0.008,
			relheight = 0.06,
			relwidth = 0.16
		)

		# create stop record Button
		self.stop_record_button = Button(
			self.labelBottom,
			text = "Stop",
			font = "Helvetica 10 bold",
			width = 10,
			bg = "#ABB2B9",
			command = lambda : self.stop_record()
		)

		# currently, we will hide stop record  button
		# when click record button, stop record will unhide
		self.stop_record_button.pack_forget()
		# self.record_button.place(
		# 	relx = 0.70,
		# 	rely = 0.008,
		# 	relheight = 0.06,
		# 	relwidth = 0.16
		# )
		
		# create a Send Button
		self.buttonMsg = Button(self.labelBottom,
								text = "Send",
								font = "Helvetica 10 bold",
								width = 10,
								bg = "#ABB2B9",
								command = lambda : self.send())
		
		self.buttonMsg.place(relx = 0.85,
							rely = 0.008,
							relheight = 0.06,
							relwidth = 0.16)
		
		self.textCons.config(cursor = "arrow")
		
		# create a scroll bar
		scrollbar = Scrollbar(self.textCons)
		
		# place the scroll bar
		# into the gui window
		scrollbar.place(relheight = 1,
						relx = 0.974)
		
		scrollbar.config(command = self.textCons.yview)
		
		self.textCons.config(state = DISABLED)

		#auto call inspiration event
		self.call_event("inspiration")

		# auto call event
		for event in list(self.YEARLY_EVENT_DICT.keys()):
			if (datetime.strptime(self.YEARLY_EVENT_DICT[event], '%Y/%m/%d').day == date.today().day and 
				datetime.strptime(self.YEARLY_EVENT_DICT[event], '%Y/%m/%d').month == date.today().month):
				self.call_event(event)
		
		# auto call reminder
		reminder_list = []
		for reminder in list(self.REMINDER_DICT.keys()):
			t = Thread(target=self.call_reminder, args=(self.REMINDER_DICT[reminder], reminder,))
			reminder_list.append(t)
			reminder_list[-1].start()
		
		for reminder in list(self.DAILY_EVENT_DICT.keys()):
			t = Thread(target=self.call_daily, args=(self.DAILY_EVENT_DICT[reminder], reminder,))
			reminder_list.append(t)
			reminder_list[-1].start()

	def call_event(self, event):
		try:
			self.textCons.config(state=NORMAL)
			self.textCons.config(foreground="#442265", font=("Verdana", 12 ))

			res = self.getResponseFromTag(event, self.intents)
			self.textCons.insert(END, "Bot: " + res + '\n\n')

			self.textCons.config(state=DISABLED)
			self.textCons.yview(END)
		except: 
			pass

	def call_reminder(self, sleep_time, event):
		while 1:
			time.sleep(sleep_time * 60) # Sleep_time is in minute
			self.call_event(event)

	def call_daily(self, time_call, event):
		while 1:
			time.sleep(60)
			if datetime.strptime(time_call, '%H:%M').strftime('%H:%M') == datetime.now().strftime('%H:%M'):
				self.call_event(event)

	def send(self):
		msg = self.entryMsg.get("1.0",'end-1c').strip()
		self.entryMsg.delete("0.0",END)

		if msg != '':
			self.textCons.config(state=NORMAL)
			self.textCons.insert(END, "You: " + msg + '\n\n')
			self.textCons.config(foreground="#442265", font=("Verdana", 12 ))

			res = self.chatbot_response(msg)
			self.textCons.insert(END, "Bot: " + res + '\n\n')

			self.textCons.config(state=DISABLED)
			self.textCons.yview(END)
	
	def send_message(self, message):
		if message != '':
			self.textCons.config(state=NORMAL)
			self.textCons.insert(END, "You: " + message + '\n\n')
			self.textCons.config(foreground="#442265", font=("Verdana", 12 ))

			res = self.chatbot_response(message)
			self.textCons.insert(END, "Bot: " + res + '\n\n')

			self.textCons.config(state=DISABLED)
			self.textCons.yview(END)
	

	def chatbot_response(self, msg):
		ints = self.predict_class(msg, self.model)
		res = self.getResponse(ints, self.intents)
		return res

	def predict_class(self, sentence, model):
		# filter out predictions below a threshold
		p = self.bow(sentence, self.words, show_details=False)
		print(p)
		if not np.any(p):
			return [{"intent": 'noanswer', "probability": 1.0}]
		res = model.predict(np.array([p]))[0]
		ERROR_THRESHOLD = 0.25
		results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
		# sort by strength of probability
		results.sort(key=lambda x: x[1], reverse=True)
		return_list = []
		for r in results:
			return_list.append({"intent": self.classes[r[0]], "probability": str(r[1])})
		return return_list

	def getResponse(self, ints, intents_json):
		tag = ints[0]['intent']
		list_of_intents = intents_json['intents']
		result = ''
		for i in list_of_intents:
			if i['tag'] == tag:
				result = random.choice(i['responses'])
				break
		return result

	def bow(self, sentence, words, show_details=True):
		# tokenize the pattern
		sentence_words = self.clean_up_sentence(sentence)
		# bag of words - matrix of N words, vocabulary matrix
		bag = [0]*len(words)
		for s in sentence_words:
			for i, w in enumerate(words):  
				if w == s:
					# assign 1 if current word is in the vocabulary position
					bag[i] = 1
					if show_details:
						print("found in bag: %s" % w)
		return(np.array(bag))

	def clean_up_sentence(self, sentence):
		sentence_words = nltk.word_tokenize(sentence)
		sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
		return sentence_words
	
	def getResponseFromTag(self, tag, intents_json):
		list_of_intents = intents_json['intents']
		result = ''
		for i in list_of_intents:
			if i['tag'] == tag:
				result = random.choice(i['responses'])
				break
		return result
		
	def startrecording(self):
		self.stream = self.p.open(format=self.sample_format,channels=self.channels,rate=self.fs,frames_per_buffer=self.chunk,input=True)
		self.isrecording = True
		
		print('Recording')
		t = threading.Thread(target=self.record)
		t.start()

		# hide record button
		self.record_button.pack_forget()
		# unhide stop record button
		self.stop_record_button.place(
			relx = 0.70,
			rely = 0.008,
			relheight = 0.06,
			relwidth = 0.16
		)

	def record(self):
		while self.isrecording:
			# data = self.stream.read(self.chunk)
			# self.frames.append(data)

			# file_name = "./resources/records/record.wav"
			# r = sr.Recognizer()
			# with sr.AudioFile(file_name) as source:
			# 	# listen for the data (load audio to memory)
			# 	audio_data = r.record(source)
			# 	# recognize (convert from speech to text)
			# 	text = r.recognize_google(audio_data, language = 'fr-CA', show_all=True)
			# 	print(f"-----------text: {text}")
			# 	self.call_str(text)
			r = sr.Recognizer()  
			with sr.Microphone() as source:  
				print("Please wait. Calibrating microphone...")  
				# listen for 5 seconds and create the ambient noise energy level  
				r.record(source, duration=2)
				# r.adjust_for_ambient_noise(source, duration=5)  
				print("Say something!")
				audio = r.listen(source)
				text = r.recognize_google(audio, language = 'en-IN', show_all = True)
				for i in text["alternative"]:
					trans = i["transcript"]
					print(f"I thinks you said: {trans}")
					# self.call_str("You: " + trans + "\n\n")
					self.send_message(trans)
				

	def stop_record(self):
		print("Stop record")
		# hide stop record button
		self.stop_record_button.place_forget()
		# unhide record button
		self.record_button.place(
			relx = 0.70,
			rely = 0.008,
			relheight = 0.06,
			relwidth = 0.16
		)
		# self.buttonMsg.place(
		# 	relx = 0.85,
		# 	rely = 0.008,
		# 	relheight = 0.06,
		# 	relwidth = 0.16
		# )
		
		self.isrecording = False
		print('recording complete')
		self.filename = "record.wav"
		wf = wave.open("./resources/records/" + self.filename, 'wb')
		wf.setnchannels(self.channels)
		wf.setsampwidth(self.p.get_sample_size(self.sample_format))
		wf.setframerate(self.fs)
		wf.writeframes(b''.join(self.frames))
		wf.close()

gui = GUI()