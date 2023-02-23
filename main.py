"""
EXPLANATION!!!

This bot ONLY works for a very specific legendary French lesson so if you want to use it
you will have to pick a lesson to use yourself and gather every question yourself.

BUT to be honest this bot was made very poorly just for my own purposes and so 
I would STRONGLY recommend just taking what I did and making something for yourself.
"""

# Dependencies and libraries
from pynput.keyboard import Key, Controller
import pyautogui
from PIL import Image
# mss is a library for taking fast screenshots
from mss.darwin import MSS as mss
import mss.tools
import pytesseract
import numpy as np
import time

# Init simulated keyboard
keyboard = Controller()

"""
When the bot reads the screen it has to take screenshots and then read from those
screenshots and so these coordinates are where the bot needs to crop the screenshot
to read the text. So, if you wanted to use it you would almost certainly have to 
re-calculate these screen-coordinates yourself to make it work.
"""
QTOPLEFT  = (410, 350)  # Question Top Left
QBOTRIGHT = (1080, 505)  # Question Bottom Right

ATOPLEFT  = (488, 572)  # Answer Top Left
ABOTRIGHT = (714, 614)  # Answer Bottom Right

"""
Sometimes the text recognition api actually reads the duolingo characters as text
So if the bot reads a question and it doesn't know what the question says, it will
look at the question again but now without the character in the screenshot, so I
needed new coordinates for that.
"""
QWCTL = (550, 350)  # Question Without Character Top Left
QWCBR = (1080, 505)  # Question Without Character Bottom Right

EXITLESSON = (244, 208)  # coordinate of exit button
STARTNEWLESSON = (660, 642)  # Isn't actually used so disregard


"""
VERY IMPORTANT!!!
This next section is quite long. In these legendary lessons there are 3 different types
of questions that duolingo will ask. 

Question type 0 is when the question gives you some
text and you just have to type in the text box to respond, these are the easiest type
of questions for the bot to answer because it simply reads the question and types the 
response and hits enter and the question is done. 

Question type 1 is when Duolingo gives you a sentence with gaps in it and you are given 
some different words and you have to fill those gaps with the provided words. These 
questions are slightly harder. Lets say I have the sentence in English "How _ you _?"
and provide you with the possible words: "are", "doing". Then obviously "are" goes first
and "doing" goes second to make "How are you doing?". The bot would answer this question
by first tpying the word "are" and hitting enter. Then typing the letter "d" and hitting 
enter. The reason, for the second word, we only type the first character is because it is
the only option available to us after typing are and so duolingo knows that's the word 
we want. 

Question type 2 is definitely the hardest question type to deal with but it's still 
possible to answer. Type 2 is when there is only one gap to fill in a sentence and
you are given 2 options for what that word may be. example: "I am _ years old." and you
are given the words "10" and "Dinosaur", obviously the word to press is "10". Now, with
type 2 questions you can only answer them by pressing 1 or 2 for the answer, but the
two words can be in different orders every time so the bot has to read what word is in 
the first answer slot and check if that is the answer, if it is then we know to press 1 
but if it isn't then we know to press 2. I realise that this might not be obvious just 
from reading this but I hope this helps anyway.
"""

# stores every combination of question that can be asked but will still probably never work 100% of the time.
# Format of dictionary: {Question from Duolingo: (Question Type(0|1|2), the answer to the question)}
TableOfQuestions = {
	"Not Sure": (0, "Not Sure"),  # don't worry about this
	"& Paris en train et je a Paris en voiture. ": (1, ["va", "v"]),
	"a Paris en train et je a Paris en voiture. ": (1, ["va", "v"]),
	"Hi! ": (0, "Salut!"),  # if Duo says "Hi! " then just type back "Salut!"
	"": (0, "Salut!"),
	"ILest et elle est ": (1, ["americain", "a"]),
	"lLest et elle est ": (1, ["americain", "a"]),
	"Hi Paul! ": (0, "Salut, Paul!"),
	"& a Hi Paul! ": (0, "Salut, Paul!"),
	"b) Hi Paul! ": (0, "Salut, Paul!"),
	"un gargon ": (2, "mexicain"),  # the answer (mexicain) is the word we are looking for
	"un garcon ": (2, "mexicain"),
	"Paul est ": (2, "étudiant"),
	"Good morning, Paul! ": (0, "Bonjour, Paul!"),
	"“0 Good morning, Paul! ": (0, "Bonjour, Paul!"),
	"© Good morning, Paul! ": (0, "Bonjour, paul"),
	"a. fae) ~~ | Sate Good morning, Paul! ": (0, "Bonjour, Paul!"),
	"a Good morning, Paul! ": (0, "Bonjour, Paul!"),
	"Hi Marie, how are you doing? ": (0, "Salut Marie, ca va?"),
	"Hi, how are you? ": (0, "Salut ca va"),
	"Maria est et Paul est ": (1, ["mexicaine", "m"]),
	"Marc est ": (2, "américain"),
	"Hello! ": (0, "Bonjour!"),
	"a Berlin. ": (2, "habite"),
	"Hi Paul, how are you doing? ": (0, "salut paul, ca va"),
	"& a Hi Paul, how are you doing? ": (0, "salut paul, ca va"),
	"a. fae) ~~ | Sate Hi Paul, how are you doing? ": (0, "salut paul, ca va"),
	"Good morning, Marie! ": (0, "bonjour marie"),
	"& a Good morning, how are you doing? ": (0, "bonjour, ca va"),
	"Good morning, how are you doing? ": (0, "bonjour, ca va"),
	". 60. Good morning, how are you doing? ": (0, "bonjour, ca va"),
	"Se Good morning, how are you doing? ": (0, "bonjour, ca va"),
	"6 ee \ Good morning, how are you doing? é ~~ | Sate ": (0, "bonjour, ca va"),
	"And you? ": (0, "et toi"),
	"& a And you? ": (0, "et toi"),
	"Very well, and you? ": (0, "tres bien et toi"),
	"Je prends le ": (2, "train"),
	"Yes, and you? ": (0, "oui, et toi"),
	"1am Paul, and you? ": (0, "je suis paul et toi"),
	"lam Paul, and you? ": (0, "je suis paul et toi"),
	"a Paris France ": (1, ["a", "e"]),
	"Paris France ": (1, ["a", "e"]),
	"He lives in Berlin. ": (0, "Il habite a berlin"),
	"the restaurant ": (0, "le restaurant"),
	"lam fine, and you? ": (0, "ca va et toi"),
	"in France ": (0, "en france"),
	"lam in Bordeaux. ": (0, "je suis dans bordeux"),
	"| am doing very well, and you? ": (0, "ca va tres bien et toi"),
	"lam doing very well, and you? ": (0, "ca va tres bien et toi"),
	"a Mexican boy ": (0, "un garcon mexicain")
}


def simulateWord(word: str) -> None:
	"""
	Type the word and then wait a short period because 
	otherwise it can be too fast and break
	"""
	for letter in word:
		keyboard.press(letter)
		keyboard.release(letter)
	time.sleep(0.01)

def simulateEnter() -> None:
	# press enter key
	keyboard.press(Key.enter)
	keyboard.release(Key.enter)
	time.sleep(0.05)

def simulateClick(xy: tuple) -> None:
	# click at a certain screen coordinate
	pyautogui.moveTo(xy[0], xy[1])
	pyautogui.click()
	time.sleep(0.05)

def simDoubleClick(xy: tuple) -> None:
	# double click can sometimes be more accurate
	pyautogui.moveTo(xy[0], xy[1])
	pyautogui.click()
	pyautogui.click()
	time.sleep(0.01)

def simulateMouseMove(xy: tuple) -> None:
	# moves the mouse so it is not in front of question
	pyautogui.moveTo(xy[0], xy[1])
	time.sleep(0.01)

def refreshPage():
	# this was experimental and was not used
	keyboard.press(Key.cmd.value)
	keyboard.press('r')
	keyboard.release('r')
	keyboard.release(Key.cmd.value)


def getTextFromScreenPortion(TL: tuple, BR: tuple) -> str:
	# This is what reads the question

	# confusing syntax but basically just takes a screenshot
	with mss.mss() as sct:
		monitor = {"top": TL[1], "left": TL[0], "width": BR[0]-TL[0], "height": BR[1]-TL[1]}
		monitorScreenshot = np.array(sct.grab(monitor))
		
		# Apply OCR on the cropped image (extract text)
		text = pytesseract.image_to_string(monitorScreenshot)

	# filtering text slightly and returning
	return text.replace('\n', ' ').replace('  ', ' ')


def type2Answer(String: str, subString: str) -> str:
	# makes sure the answer appears in what we've read
	if subString in String and String[-1] == subString[-1]: return '1'
	else: return '2'

def searchRank(search, actual):
	# sometimes the bot reads it really badly and this 
	# is a stupid simple ranking algorithm
	# I wouldn't even worry about it
	rank = 0
	for i, j in enumerate(actual):
		for b in range(-4, 5, 1):
			buff = i + b
			if 0 <= buff < len(search):
				if search[buff] == j:
					rank += 5 - abs(i - buff)
	return rank

def calcBestPhrase(text, wList):
	# again ranking algorithm that ranks what it's 
	# read to every possible question and goes with the best result
	best_phrase, best_rank = "", 0
	for _, phrase in enumerate(wList):
		new_rank = searchRank(text, phrase)
		if new_rank > best_rank:
			best_rank = new_rank
			best_phrase = phrase
	return best_phrase

def shouldStartLesson() -> None:
	# this takes screenshots during the loading screen and check to see
	# if the lesson has started yet.
	col = (0, 0, 0)
	with mss.mss() as sct:  # take screenshot
		while col != (166, 160, 248):
			monitor = {"top": 635, "left": 600, "width": 1, "height": 1}
			col = sct.grab(monitor).pixel(0, 0)
			time.sleep(0.05)  # reduces check-rate for less load on computer

def main():
	time.sleep(3)  # starting wait

	KeyList = list(TableOfQuestions.keys())
	# some stats about bots performance
	lesson_count = 0
	failed_lesson_count = 0
	time_running = 0
	lesson_errors = 0
	
	while True:
		StartTime = time.time()

		lesson_errors = 0
		isLessonOver = False
		QsAnswered = 0

		simulateEnter()  # enter lesson
		simulateEnter()  # enter lesson

		shouldStartLesson()  # blocking function

		simulateEnter()  # start lesson
		simulateEnter()  # enter lesson

		while not isLessonOver and QsAnswered < 8:  # 8 questions to reach midpoint
			time.sleep(0.28)  # wait for next question to load
			text = getTextFromScreenPortion(QTOPLEFT, QBOTRIGHT, )  # get question
			print(f'"{text}"')

			try:
				if text in KeyList:
					instruction = TableOfQuestions[text]  # get question
					instr_type = instruction[0]  # get response to question
				else:

					try:  # if couldn't get question then read again without character
						new_text = getTextFromScreenPortion(QWCTL, QWCBR)
						print(f'new text: "{new_text}"')
						if new_text in KeyList:
							instruction = TableOfQuestions[new_text]
							instr_type = instruction[0]
						else:  # if that didn't work then rank it
							best_phrase = calcBestPhrase(new_text, KeyList)
							print(f'Best-Guess: {best_phrase}')
							instruction = TableOfQuestions[best_phrase]
							instr_type = instruction[0]

					except:  # if all else fails then just get it wrong
						instruction = TableOfQuestions["Not Sure"]
						instr_type = instruction[0]

				if instr_type == 0:  # easiest question type
					simulateWord(instruction[1])
					simulateEnter()  # press enter

				elif instr_type == 1:
					simulateWord(instruction[1][0])
					simulateEnter()
					simulateWord(instruction[1][1])
					simulateEnter()
				
				elif instr_type == 2:
					# get Possible Answers
					AnswerString = getTextFromScreenPortion(ATOPLEFT, ABOTRIGHT)
					print(f'Answer: "{AnswerString}"')
				
					# type either 1 or 2 on keyboard
					simulateWord(type2Answer(AnswerString.strip(), instruction[1]))
					simulateEnter()

				simulateEnter()  # all questions require final enter to proceed
					
			except:
				input()  # pause program until I've solved manually
				time.sleep(3)  # give me time to close cmd

			QsAnswered += 1

		if lesson_errors < 3:
			lesson_count += 1
		else:
			failed_lesson_count += 1

		# some stats about lesson
		prev_lesson_time = time.time() - StartTime
		time_running += prev_lesson_time
		avg_time = time_running / lesson_count
		print(f'\n               XP: {lesson_count * 20}')
		print(f'           XP/min: {round((60 / avg_time) * 20, 3)}')
		print(f'      Lesson-Time: {round(prev_lesson_time, 3)}')
		print(f'     Average-Time: {round(avg_time, 3)}')
		print(f'Lessons-Completed: {lesson_count}')
		print(f'     Elapsed-Time: {round(time_running, 3)}\n')

		# Lesson is over so exit lesson and start a new one
		time.sleep(0.2)
		simulateClick(EXITLESSON)
		time.sleep(0.5)
		simulateEnter()
		simulateMouseMove((1200, 540))
		time.sleep(0.4)

if __name__ == "__main__":
	main()
