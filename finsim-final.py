import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

# starting variables 
startingBalance = 100000
canTradeLong = True
canTradeShort = False
currentCash = startingBalance
longStockOnHand = 0
shortStockOnHand = 0
longTrades=[]
timesTradedLong = 0
notYetTradedMACD = True
notYetTradedTurtle = True
notYetTradedVortex = True
stopLoss = .009
sharpeRatio = 0
simMACD = False
simTurtle = False
simVortex = False
balanceTrades=[]
balanceEnter = []
balanceExit = []
balanceOpen = 0 
takeProfit = .12
amountStopLoss = 0
turtleStopLoss = .05
turtleTakeProfit = .05
balanceClose = 0
#balanceTrades.append(startingBalance)
##enter stock data here from csv file
#stockData = pd.read_csv("EA.csv", header = 0, index_col = 0, parse_dates = True)
#stockData = pd.read_csv("MSFT.csv", header= 0, index_col = 0, parse_dates = True)
stockData = pd.read_csv("GE.csv", header = 0, index_col = 0, parse_dates = True)
#stockData = pd.read_csv("MacDcsv.csv", header = 0, index_col = 0, parse_dates = True)
#stockData = pd.read_csv("ATVI.csv", header = 0, index_col = 0, parse_dates = True)

stockData["OHLC"] = (stockData.Open + stockData.Close + stockData.High + stockData.Low)/4
priceGraph = stockData['OHLC'].plot(grid=True)

plt.show(priceGraph)

exitsMACD = pd.Series()
exitsTurtle = pd.Series()
exitsVortex = pd.Series()

def MACDsim():
	#balanceTrades.append(startingBalance)
	print("Start of MACD sim")
	priceBought = 0
	global notYetTradedMACD, currentCash, stopLoss, sharpeRatio, simMACD, amountStopLoss
	balanceTrades.append(startingBalance)
	balanceEnter.append(startingBalance)
	balanceExit.append(startingBalance)
	simMACD = True
	MACDdata = stockData.copy()
	#MACD with ema 26 and ema 12
	MACDdata["EMA12"] = MACDdata.rolling(window=12).mean()['OHLC']
	MACDdata["EMA26"] = MACDdata.rolling(window=26).mean()['OHLC']
	MACDdata["MACDLINE"] = (MACDdata.EMA12 - MACDdata.EMA26)
	MACDdata["SIGNAL"] = MACDdata.rolling(window=9).mean()['MACDLINE']
	
	a = MACDdata['MACDLINE']
	b = MACDdata['SIGNAL']
	plt.plot(a,'b')
	plt.plot(b ,'r')
	plt.show()	
	MACDlineGraph = plt.plot(MACDdata['MACDLINE'],'b', MACDdata['SIGNAL'],'r',)
	plt.show(MACDlineGraph)		
	#print(MACDdata.head(50))
# trade sim 
	for i, r in MACDdata.iterrows():
		if(r['MACDLINE']>r['SIGNAL'] and canTradeLong == True): #buy here
			if(notYetTradedMACD == True):
				print("entering first trade")
				print("date: ", i)
				notYetTradedMACD = False
				currentCash = startingBalance
				longTradeEnter(currentCash, r['OHLC'], i)
				priceBought = r['OHLC']
			else:
				if(canTradeLong == True and currentCash > 1):
					print("normal buy") 
					longTradeEnter(currentCash, r['OHLC'], i)
					priceBought = r['OHLC']

		if(canTradeLong == False and r['MACDLINE'] < r['SIGNAL'] and longStockOnHand > 0): #sell at signal
			longTradeExit(currentCash, r['OHLC'], i)
			#print("date normal exit: ", i)	

		if(canTradeLong == False and r['OHLC'] < (priceBought-(priceBought*stopLoss))): # sell at stop loss
			print(r['OHLC'])
			print(priceBought-(priceBought*stopLoss))
			print("Selling at StopLoss")
			longTradeExit(currentCash, r['OHLC'], i)
			amountStopLoss += 1

	if(longStockOnHand > 0):
		print("offloading remaining stock")
		longTradeExit(currentCash, MACDdata.iloc[-1,-5], MACDdata.iloc[0, -1])


	def MACDreport():
		MACDSharpe = sharpeRatio
		print("")
		print("MACD Report")
		print("Starting Cash: ", startingBalance)
		print("Ending: ", currentCash)

		if currentCash > startingBalance:
			print("Increase by: ",currentCash - startingBalance)
			print("Percent Increase: ", ((currentCash - startingBalance)/startingBalance)*100)
			print("Sharpe Ratio:", MACDSharpe)
			print("")
		elif currentCash < startingBalance:
			print("Decrease by: ",startingBalance - currentCash)
			print("Percent decrease: ", ((currentCash-startingBalance)/startingBalance)*100)
		else:
			print("Breakeven")

			#print(balanceTrades)
		print("Long Trades: ", timesTradedLong)
		print("Stop Loss exits:", amountStopLoss)
			#print(balanceTrades)
		print("Peak: ", np.amax(balanceExit))
		print("Min: ", np.amin(balanceExit))
		print("Relative Drawdown: ", ((np.amax(balanceExit)-np.amin(balanceExit))/np.amax(balanceExit))*100)
		priceGraph = MACDdata['OHLC'].plot(grid=True)
		plt.show(priceGraph)		
		balanceGraph = plt.plot(balanceTrades)
		plt.show(balanceGraph)

	MACDreport()
	# clear the needed things for other simulation
	clearGlobal()

def turtleSim():
	print("Start of Turtle Sim")
	global notYetTradedTurtle, currentCash, stopLoss, sharpeRatio, simTurtle, amountStopLoss, turtleStopLoss, turtleTakeProfit
	simTurtle = True
	balanceTrades.append(startingBalance)
	balanceEnter.append(startingBalance)
	balanceExit.append(startingBalance)
	priceBought = 0
	turtleData  = stockData.copy()
	turtleData["BUY PRICE"] = turtleData.rolling(window = 20).max()['OHLC']	
	turtleData["SELL PRICE"] = turtleData.rolling(window = 10).min()['OHLC']	
	a = turtleData['BUY PRICE']
	b = turtleData['SELL PRICE']
	c = turtleData['OHLC']
	plt.plot(a,'b')
	plt.plot(b ,'r')
	plt.plot(c,'g')
	plt.show() 
	lastSoldPrice = 0	
	for i, r in turtleData.iterrows():
		#buy
		#print(r.loc['OHLC'], r.loc["BUY PRICE"])
		if(r.loc["OHLC"] == r.loc["BUY PRICE"] and r.loc["BUY PRICE"] > 0 and canTradeLong == True and notYetTradedTurtle == True):
			notYetTradedTurtle = False #^^ np where np select
			print("Entering First Trade")
			print(r['OHLC'])
			print(r["BUY PRICE"])
			print("Date: ", i)
			currentCash = startingBalance
			longTradeEnter(currentCash, r["OHLC"],i)
			priceBought = r["OHLC"]		
		if(r.loc["OHLC"] == r.loc["BUY PRICE"] and r.loc["BUY PRICE"] > 0 and canTradeLong == True):
			print("normal buy")
			longTradeEnter(currentCash, r['OHLC'], i)
			priceBought = r['OHLC']	
		if(canTradeLong == False and r['OHLC'] > (priceBought + (priceBought*turtleTakeProfit))):
			print("last price bought: ", priceBought)
			print("take profit at: ", priceBought + priceBought*takeProfit)
			print(r['OHLC'])
			longTradeExit(currentCash, r['OHLC'], i)		#sell
		if(r.loc["OHLC"] == r.loc['SELL PRICE'] and canTradeLong == False and longStockOnHand > 0):
			longTradeExit(currentCash, r["SELL PRICE"], i)
			lastSoldPrice = r['SELL PRICE']		#stoploss
		if(canTradeLong == False and r['OHLC'] < (priceBought-(priceBought*turtleStopLoss))): # sell at stop loss
			print(priceBought-(priceBought*stopLoss))
			print("Selling at StopLoss")
			longTradeExit(currentCash, r['SELL PRICE'], i)
			lastSoldPrice = r['SELL PRICE']
			amountStopLoss += 1	
	if(longStockOnHand > 0):
		print("offloading remaining stock")
		longTradeExit(currentCash, turtleData.iloc[-1,-1], turtleData.iloc[0, -1])	

	def turtleReport():
		turtleSharpe = sharpeRatio
		print("")
		print("Turtle Report")
		print("Starting Cash: ", startingBalance)
		print("Ending: ", currentCash)		

		if currentCash > startingBalance:
			print("Increase by: ",currentCash - startingBalance)
			print("Percent Increase: ", ((currentCash - startingBalance)/startingBalance)*100)
			print("Sharpe Ratio:", turtleSharpe)
			print("")
		elif currentCash < startingBalance:
			print("Decrease by: ",startingBalance - currentCash)
			print("Percent decrease: ", ((currentCash-startingBalance)/startingBalance)*100)
		else:
			print("Breakeven")
		#print(balanceTrades)
		print("Long Trades: ", timesTradedLong)
		print("Stop Less exits: ", amountStopLoss)
		print("Peak: ", np.amax(balanceExit))
		print("Min: ", np.amin(balanceExit))
		print("Relative Drawdown: ", ((np.amax(balanceExit)-np.amin(balanceExit))/np.amax(balanceExit))*100)
		priceGraph = turtleData['OHLC'].plot(grid=True)
		plt.show(priceGraph)
		#print(balanceTrades)
		balanceGraph = plt.plot(balanceTrades)
		plt.show(balanceGraph)	

	turtleReport()	
	clearGlobal()

def vortexSim():
	# long when vi+ goes above vi- exit when switch
	#ohlc of day ohlc today - ohlc yesterday
	print("Start of Vortex Sim")
	global notYetTradedVortex, currentCash, stopLoss, sharpeRatio, simVortex, amountStopLoss
	simVortex = True
	balanceTrades.append(startingBalance)
	balanceEnter.append(startingBalance)
	balanceExit.append(startingBalance)
	vortexData  = stockData.copy()
	vortexData["+VI"] = abs(vortexData["High"].shift(1) - vortexData["Low"])
	vortexData["-VI"] = abs(vortexData["Low"].shift(1) - vortexData["High"])
	#smooth data
	vortexData["+VISmooth"] = vortexData.rolling(window = 14).sum()['+VI']
	vortexData["-VISmooth"] = vortexData.rolling(window = 14).sum()['-VI']
	
	a = vortexData['+VISmooth']
	b = vortexData['-VISmooth']
	c = vortexData['OHLC']

	plt.plot(a,'b')
	plt.plot(b ,'r')
	plt.plot(c,'g')
	plt.show() 	
	lastSoldPrice = 0	
	for i, r in vortexData.iterrows():
		if(r['+VISmooth']>r['-VISmooth'] and canTradeLong == True): #buy here
			if(notYetTradedVortex == True):
				print("entering first trade")
				print("date: ", i)
				notYetTradedVortex = False
				currentCash = startingBalance
				longTradeEnter(currentCash, r['OHLC'], i)
				priceBought = r['OHLC']
			else:
				if(canTradeLong == True and currentCash > 1):
					print("normal buy") 
					longTradeEnter(currentCash, r['OHLC'], i)
					priceBought = r['OHLC']		

		if(canTradeLong == False and r['OHLC'] > (priceBought + (priceBought*takeProfit))):
			print("last price bought: ", priceBought)
			print("take profit at: ", priceBought + priceBought*takeProfit)
			print(r['OHLC'])
			longTradeExit(currentCash, r['OHLC'], i)		
		if(canTradeLong == False and r['+VISmooth'] < r['-VISmooth'] and longStockOnHand > 0): #sell at signal
			longTradeExit(currentCash, r['OHLC'], i)
			#print("date normal exit: ", i)			

		if(canTradeLong == False and r['OHLC'] < (priceBought-(priceBought*stopLoss))): # sell at stop loss
			print(r['OHLC'])
			print(priceBought-(priceBought*stopLoss))
			print("Selling at StopLoss")
			longTradeExit(currentCash, r['OHLC'], i)
			amountStopLoss += 1
			#print("sell stoploss exit date: ", i)	
	if(longStockOnHand > 0):
		print("offloading remaining stock")
		longTradeExit(currentCash, vortexData.iloc[-1,-5], vortexData.iloc[0, -1])	

	def vortexReport():
		vortexSharpe = sharpeRatio
		print("")
		print("Vortex Report")		
		print("Starting Cash: ", startingBalance)
		print("Ending: ", currentCash)
		if currentCash > startingBalance:
			print("Increase by: ",currentCash - startingBalance)
			print("Percent Increase: ", ((currentCash - startingBalance)/startingBalance)*100)
			print("Sharpe Ratio:", vortexSharpe)
			print("")
		elif currentCash < startingBalance:
			print("Decrease by: ",startingBalance - currentCash)
			print("Percent decrease: ", ((currentCash-startingBalance)/startingBalance)*100)
			print("Sharpe Ratio:", vortexSharpe)
			print("")
		else:
			print("Breakeven")
		#print(balanceTrades)

		print("Long Trades: ", timesTradedLong)
		print("Stop loss exits: ", amountStopLoss)
		print("Peak: ", np.amax(balanceExit))
		print("Min: ", np.amin(balanceExit))
		print("Relative Drawdown: ", ((np.amax(balanceExit)-np.amin(balanceExit))/np.amax(balanceExit))*100)
		priceGraph = vortexData['OHLC'].plot(grid=True)
		plt.show(priceGraph)
		#print(balanceTrades)
		balanceGraph = plt.plot(balanceTrades)
		plt.show(balanceGraph)	

	vortexReport()	
	clearGlobal()

def longTradeEnter(x, y, d): #x is current cash, y is price at iteration
	global timesTradedLong, longStockOnHand, currentCash, canTradeLong, balanceOpen, balanceEnter, balanceExit
	tradeFactor = .5
	balanceOpen = x
	#balanceTrades.append(x)
	print("==BUYING==")
	print("buy date: ", d)
	print("entering balance: ", x)
	print("stock on hand: ", longStockOnHand)
	print("Buying at price: ", 	y)
	print("stock bought: ",(x*tradeFactor)/y)
	longStockOnHand += (x*tradeFactor)/y
	x -= (x*tradeFactor)
	canTradeLong = False
	print("stock on hand: ",longStockOnHand)
	currentCash = x
	balanceEnter.append(balanceOpen)
	balanceTrades.append(currentCash)
	print("Balance: ", currentCash)

def longTradeExit(x, a, d):
	global sharpeRatio, timesTradedLong, longStockOnHand, currentCash, balanceTrades, canTradeLong, balanceOpen, balanceExit, balanceEnter
	riskFreeRate = .00128
	print("")
	print("==SELLING==")
	print("sell date: ", d)
	print("before exit balance: ", x)
	opening = x
	print(opening)
	print("stock on hand for exit: ", longStockOnHand)
	print("selling price: ",a)
	print("gained from trade: ", longStockOnHand*a)
	timesTradedLong += 1
	x += (longStockOnHand*a)
	longStockOnHand = 0
	canTradeLong = True
	currentCash = x	
	balanceExit.append(currentCash)
	balanceTrades.append(currentCash)

	if simMACD == True:
		exitsMACD.at[len(exitsMACD.index)] = currentCash / balanceOpen
		if timesTradedLong > 1:	
			#balanceTrades.append(currentCash)
			
			#sharpeRatio = (exitsMACD.mean()-(1+(riskFreeRate/np.sqrt(250))))/exitsMACD.std()
			#sharpeRatio = (exitsMACD.mean()-(1+(riskFreeRate/62.5)))/exitsMACD.std()
			sharpeRatio = (exitsMACD.mean() - (1 + riskFreeRate/65))/ exitsMACD.std()
			
	if simTurtle == True:
		exitsTurtle.at[len(exitsTurtle.index)] = currentCash / balanceOpen
		if timesTradedLong > 1:	
			#balanceTrades.append(currentCash)
			
			sharpeRatio = (exitsTurtle.mean()-(1+(riskFreeRate/np.sqrt(65))))/exitsTurtle.std()
			#print(exitsTurtle)
			#print(exitsTurtle.mean())
			#print(exitsTurtle.std())
			#print(1+(.01/np.sqrt(250)))	

	if simVortex == True:
		exitsVortex.at[len(exitsVortex.index)] = currentCash / balanceOpen
		if timesTradedLong > 1:	
			#balanceTrades.append(currentCash)
			
			sharpeRatio = (exitsVortex.mean()-(1+(riskFreeRate/np.sqrt(65))))/exitsVortex.std()
			#print(exitsVortex)
			#print(exitsVortex.mean())
			#print(exitsVortex.std())
			#print(1+(.01/np.sqrt(250)))	print("times traded: ", timesTradedLong)

	print("stock on hand: ",longStockOnHand)
	print("balance after exit: ", currentCash)
	print("Trade exited")
	print("")

def clearGlobal():
	global canTradeLong, sharpeRatio, timesTradedLong, simMACD, simTurtle, simVortex, balanceTrades, amountStopLoss, balanceExit, balanceEnter
	balanceExit = []
	canTradeLong = True
	sharpeRatio = 0
	timesTradedLong = 0
	simMACD = False
	simVortex = False
	simTurtle = False
	balanceTrades = []
	amountStopLoss = 0
	balanceEnter = []
	balanceExit = []


MACDsim()
turtleSim()
vortexSim()



