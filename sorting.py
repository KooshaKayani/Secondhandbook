import sys
from os import uname
import pandas as pd
import csv
import smtplib
import ssl
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import Mthreading
from UImain import Ui_MainWindow
global lstTurnedIn
lstTurnedIn = []
global Yearlvl
Yearlvl = [
    '8',
    '9',
    '10',
    '11 / 12'
]
BuyEmail = """Subject: Your book 

	Hey, Good news.\nWe found the {book} you wanted. Come to to place at lunch time to buy it :) \n
	We can only hold the book[s] for you for 2 school days so make sure you remember to come!!!
	"""
SoldEmail = """Subject: Your book

	Hey, Good news.\nWe sold your{book} for you :o Come to to place at lunch time to get the money $$! \n
	just a reminder that we take a 10 percent fee ;)
	"""
# input: mixed buyer and seller data from the google forum
# output: two separate buyer and seller csv files
# splits the data to seelers and buyers so that it can be used by the rest of the software

class MainWindow(QMainWindow):
	def __init__(self, parent = None):
		QMainWindow.__init__(self,parent)

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.show()
		self.threadpool = QThreadPool()

		#minimizing multi threading to avoid bugs:
		self.threadpool.setMaxThreadCount(4)

		# connecting the ui to the code
		self.ui.btnReset.clicked.connect(self.SplittingData)
		self.ui.btnRun.clicked.connect(self.RunThread)
		self.ui.btnCheck.clicked.connect(self.Check)
		self.ui.btnTurnedIn.clicked.connect(self.TurnedIn)
		self.ui.btnBuyerEmail.clicked.connect(self.SendBuyerEmail)
		#self.ui.btnSellerEmail.clicked.connect(self.SendSellerEmail)
		


	def SplittingData(self):
		try:
			# Importing the Unsorted Data
			UnsortedData = pd.read_csv('Second Hand book-2.csv', dtype="string")

			BuyerList = UnsortedData.where(
				UnsortedData["Are you selling or buying?"] == 'Buying').dropna(subset=["Timestamp"])
			SellerList = UnsortedData.where(
				UnsortedData["Are you selling or buying?"] == 'Selling').dropna(subset=["Timestamp"])

			BuyerList.to_csv('Buyer.csv', index=False)
			SellerList.to_csv('Seller.csv', index=False)
			self.ui.dispTerminal.setText("Data has been seperated successfully :)")

		except:
			self.ui.dispTerminal.setText("there was an error while importing the MixedData :(")

	#input inpCheck
	#output list of available user or error
	#checks if a user exists and checks the books they have applied for if none returns none
	def Check(self):
		global lstTurnedIn
		IdStudent = str(self.ui.inpCheck.toPlainText())
		lstbook = []
		if len(IdStudent) <= 7:
			self.ui.dispInfo.setText("Enter a valid Id")
			return
		bookYear = IdStudent.split(",")[1]
		IdStudent = IdStudent.split(",")[0]
		
		try:
			# Importing the Unsorted Data
			Sellers = pd.read_csv('Seller.csv', dtype="string")
			#print(Sellers['Student Code'])

			data = Sellers.loc[Sellers['Student Code'] == IdStudent].reset_index(drop=True)
			exists = Sellers['Student Code'].str.contains(IdStudent, case=False)

			if exists.sum() > 0:
				self.ui.dispInfo.setText("id exists")
				count = 0
				for i in range(0,len(data.index)):
					for books in str(list(data.loc[[i]]["Year "+bookYear+" books"])[0]).split(";"):
						lstbook.append(books)
						self.ui.dispInfo.append(str(count)+'- '+ str(books))
						count+=1
				lstTurnedIn = [IdStudent,bookYear,lstbook]

			else:
				self.ui.dispInfo.setText('have to add the id')
				return
		except:
			self.ui.dispInfo.setText("there was an error while checking the data :(")

			
	# user input: student codes who have turned their books in
	# output: creates a csv file containing all the turned in books
	# checks if the user has signed up before if so it will add the book to a turned in .csv
	def TurnedIn(self):
		TurnedIn = pd.read_csv("TurnedIn.csv", dtype="string")
		BookId = str(self.ui.inpTurnedIn.toPlainText())
		global lstTurnedIn
		if len(BookId) == 0:
			self.ui.dispInfo.setText("Enter a valid Id")
			return
		try:
			BookId = BookId.split(",")
			print(BookId)
		except:
			self.ui.dispTerminal("Enter a valid number")

		
		try:
			self.ui.dispInfo.clear()
			for i in BookId:
				to_append = [lstTurnedIn[0],lstTurnedIn[1],lstTurnedIn[2][int(i)]]
				to_series = pd.Series(to_append, index=TurnedIn.columns)
				TurnedIn = TurnedIn.append(to_series, ignore_index=True)
				TurnedIn.to_csv('TurnedIn.csv', index=False)
				self.ui.dispInfo.append(lstTurnedIn[2][int(i)])

		except:
			self.ui.dispInfo.setText("there was an error while turning in the data :(")


	# input the template and the list that the email addresses
	# output sends email to the receivers
	# description this will send a set fromat of text to a list of people
	def SendBuyerEmail(Self):
		from_address = "kooshaki7@gmail.com"
		password = "Mk7769092"
		message = "text"
		context = ssl.create_default_context()

		with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:

			server.login(from_address, password)

			reader = pd.read_csv("receivers", dtype="string")
			for Id in reader["Student Code"]:
				print("sending email to {")
				server.sendmail(
					from_address,
					Id+'@gwsc.vic.edu.au',
					message.format(book="book")
				)

	# input Inprogress.csv a row of df 
	# true false
	# to check if the order is already being progressed
	def BuyProgressCheck (self,row,book,InProgress):
		if len(InProgress.index) > 0 :
			for eachrow in range(0,len(InProgress.index)):
				if list(InProgress.loc[[eachrow]]["Buyer Code"])[0] == list(row["Student Code"])[0] and list(InProgress.loc[[eachrow]]["Book"])[0] == book:
					return True
		return False

	# input Inprogress.csv a row of df 
	# true false
	# to check if the order is already being progressed

	def SellProgressCheck (self,row,book,InProgress):
		if len(InProgress.index) > 0 :
			for eachrow in range(0,len(InProgress.index)):
				if list(InProgress.loc[[eachrow]]["Seller Code"])[0] == list(row["Student Code"])[0] and list(InProgress.loc[[eachrow]]["Book"])[0] == book:
					return True
		return False

	#input none
	#output ( excutes the function whithin a thread)
	def RunThread(self):

		self.ui.dispInfo.setText('Loading')
		# adjusting the thread
		worker = Mthreading.Worker(self.FindBuyers) # Any other args, kwargs are passed to the run function
		worker.signals.result.connect(self.ResultDisplay)
		# Execute
		self.threadpool.start(worker)


	#input seller.csv book to buy 
	#output a series [True/False, sellers info]
	#it searchs to find a seller and returns the info
	# def FindSellers():

	def FindBuyers(self,progress_callback):
		global Yearlvl
		BuyerCount = 0
		SellerCount = 0
		lstError = []
		BuyerList = pd.read_csv("Buyer.csv", dtype="string")
		SellerList = pd.read_csv("Seller.csv", dtype="string")
		InProgress = pd.read_csv("InProgress.csv", dtype="string")
		try:
			for Year in Yearlvl: # for each year level that there is 
				#print(Year)
				SearchBuyerList = BuyerList.where(BuyerList["what year?"] == Year).dropna(subset=["Timestamp"]).reset_index(drop=True)
				SearchSellerList = SellerList.where(SellerList["what year?"] == Year).dropna(subset=["Timestamp"]).reset_index(drop=True)
				SearchInProgress = InProgress.where(InProgress["Year"] == Year).dropna(subset=["Year"]).reset_index(drop=True)

				#iterates through each row of th data frame and splits all the given books 
				if len(SearchBuyerList.index) > 0 and len(SearchSellerList.index) > 0:

					for Buyers in range(0,len(SearchBuyerList.index)):

						for EachBook in str(list(SearchBuyerList.loc[[Buyers]]["Year "+Year+" books"])[0]).split(";"):

							if self.BuyProgressCheck(SearchBuyerList.loc[[Buyers]], EachBook, SearchInProgress) == False:

								for Sellers in range(0,len(SearchSellerList.index)):
									for SellingItems in str(list(SearchSellerList.loc[[Sellers]]["Year "+Year+" books"])[0]).split(";"):
										
										if SellingItems == EachBook:
											if self.SellProgressCheck(SearchSellerList.loc[[Sellers]],SellingItems,SearchInProgress) == False:

												to_append = [list(SearchSellerList.loc[[Sellers]]["Student Code"])[0],list(SearchBuyerList.loc[[Buyers]]["Student Code"])[0],str(Year), EachBook]
												to_series = pd.Series(to_append, index = SearchInProgress.columns)
												SearchInProgress = SearchInProgress.append(to_series, ignore_index=True)
												InProgress = InProgress.append(to_series, ignore_index=True)
												
		except Exception as error:
			lstError.append(error)

		InProgress.to_csv('InProgress.csv', index=False)
		if len(lstError) > 0:
			return lstError
		else:
			return ["Connections were made successfully ;)"]
		
	#input (the result of the thread FindBuyers)
	#output (display info if )
	def ResultDisplay(self,s):
		if s[0] != "Connections were made successfully ;)":
			QtWidgets.QMessageBox.critical(self, 'Error', "Ticker was not found!")
		self.ui.dispTerminal.clear()
		for e in s:
			self.ui.dispTerminal.append(e)
		


if __name__ == "__main__":
	app = QApplication(sys.argv)
	win = MainWindow()
	win.show()
	sys.exit(app.exec())

