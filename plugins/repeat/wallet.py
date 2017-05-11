import time
import re,getpass,os,time
amount = {}

from lib import Plugin, cron
plgn = Plugin('wallet')
logger = plgn.logger

def making_database():
	f = open("wallet.txt",'w')
	string  = "{'cash':0,'savings':0,'pay':{},'receive':{}}"
	f.write(string)
	f.write("\n")
	f.close()
	logger.info("Database written")

def reading_database():
	global amount
	f = open("wallet.txt",'r')
	data = f.read()
	f.close()
	amount = eval(data)
	logger.info("Database_read")

def updating_database():
	global amount
	f=open("wallet.txt",'w')
	f.write(str(amount))
	f.close()
	logger.info("database_updated")
	
def accountant(marker,amount,description=" "):
	f = open('transaction.txt','a')
	a = time.asctime(time.localtime(time.time()))
	if amount<0:
		amount = int(amount)*(-1)
	final = str(a)+ " " + str(marker) + " " + str(amount) + " " + str(description) + "\n"
	f.write(str(final))
	f.close()

@plgn.command('wallet\Z')
def wallet(data,what=None):
	final =  """
	Welcome to wallet ! Following are the commands and their descriptions:
	1) wallet (debit/credit/savings) (amount) (description of transaction)
	2) cash left 
		To check the amount left in wallet
	3) savings done
		To check the amount of money saved
	4) statement (no. of last transactions you want to see)
	5) statement (debit/credit/savings) (no.of last specific transaction you want to see)
	6) money (pay/receive) (name of the person) (amount included)
	7) check (pay/receive)
		To check how many people you owe to or owe to you 
	ENJOY !!
"""
	return final
@plgn.command('wallet (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
def transaction(data, what):
	global amount
	user = getpass.getuser()
	if not os.access("wallet.txt",os.F_OK):
		making_database()
	reading_database()
	z = what.split(" ")
	what = z[1]
	
	marker = 'cash'	
	if z[0]=='debit':
		what = int(what)*(-1)
	if z[0]=='savings' or z[0]=='saving':
		marker = 'savings'
	amount[marker]=amount[marker]+int(what)
	logger.info(amount[marker])
	updating_database()
	if len(z )>=3:
		x = " ".join(z[2:])
	else :
		x = " "
	accountant(str(z[0]),str(what),x)
	if z[0]=='debit' or z[0] == 'Debit':
		what = what*(-1)
		return "Expense of Rs.%d added to you Wallet" %what
	if z[0]=='credit' or z[0] == 'Credit':
                return "Income of Rs.%s added to you Wallet" %what
	if z[0]=='saving' or z[0] == 'savings':
                return "Savings of Rs.%s added to your Wallet" %what

@plgn.command('cash left')
def cash(data,what = None):
	global amount	
	if not os.access("wallet.txt",os.F_OK):
		return "Please initiate a wallet"
	reading_database()
	return "You have Rs.%s left in your Wallet"%amount['cash']

@plgn.command('savings done')
def savings(data,what = None):
        global amount
        if not os.access("wallet.txt",os.F_OK):
                return "Please initiate a wallet"
        reading_database()
        return "You have done savings of Rs.%s till date"%amount['savings']

@plgn.command('statement (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
def statement(data,what):
	f = open('transaction.txt','r')
	d = f.read()
	f.close()
	lines = d.split("\n")
	if len(what.split(" "))==1:
		what = int(what)*(-1)
		lines =lines[what-1:]
	else:
		final = []
		marker = (what.split(" "))[0]
		what = (what.split(" "))[1]
		what = int(what)
		logger.info(lines)
		for l in lines:
			logger.info(l)
            logger.info(what)
			if marker in l and what>0:
				final.append(l)
				what=what-1
		lines = final
	return "\n".join(lines)
@plgn.command('money (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
def pay(data,what):	
	global amount
	user = getpass.getuser()
	if not os.access("wallet.txt",os.F_OK):
		making_database()
	reading_database()
	what = what.split(" ")
	what[0]=str(what[0])
	what[1] = str(what[1])
	what[2]=int(what[2])
	if what[0]=='pay':
		logger.info(amount)
		if what[1] in (amount['pay']).keys():
			(amount['pay'])[what[1]]=amount['pay'][what[1]]+what[2]
		elif str(what[1]) in (amount['receive']).keys():
			if what[2]>int((amount['receive'])[what[1]]):
				(amount['pay'])[what[1]]=what[2]-(amount['receive'])[what[1]]
				del (amount['receive'])[what[1]]
			elif what[2]<int((amount['receive'])[what[1]]):
				((amount['receive'])[what[1]])=int((amount['receive'])[what[1]]) - what[2]
			else:
				del (amount['receive'])[what[1]]
		else:
			logger.info("HI")
			(amount['pay'])[str(what[1])]=what[2]
	elif what[0]=='receive':
		if str(what[1]) in (amount['receive']).keys():
			(amount['receive'])[what[1]]=amount['receive'][what[1]]+what[2]
		elif str(what[1]) in (amount['pay']).keys():
			if what[2]>int((amount['pay'])[what[1]]):
				(amount['receive'])[what[1]]=what[2]-(amount['pay'])[what[1]]
				del (amount['pay'])[what[1]]
			elif what[2]<int((amount['pay'])[what[1]]):
				((amount['pay'])[what[1]])=int((amount['pay'])[what[1]]) - what[2]
			else:
				del (amount['pay'])[what[1]]
		else:
			(amount['receive'])[str(what[1])]=what[2]
	updating_database()
	return "NOTED !"
@plgn.command('check (?P<what>[-a-zA-Z0-9 `,;!@#$%^&*()_=.{}:"\?\<\>/\[\'\]\\n]+)')
def check(data,what):	
	global amount
	user = getpass.getuser()
	if not os.access("wallet.txt",os.F_OK):
		return "Please initiate a wallet!"
	reading_database()
	what = str(what)
	if what=='pay':
		s =  (amount['pay']).items()
	elif what =='receive':
		s =(amount['receive']).items()
	s = map(str,s)
	return "\n".join(s)
