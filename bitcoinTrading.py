#Vikram Amin
#Bitcoin Case Study
#May 25th 2017

############Import all libraries that will be needed##############
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
from re import sub
##################################################################

####################################
##########Start of Parsing##########
####################################

#helper function to find only the exchanges
def isExchange(href):
    return href and re.compile("exchanges").search(href)

#helper function to find only the Pairs
def isPair(href):
    return href and re.compile("https://").search(href)

#converts from a stirng with currency symbol to float
def convertMoney(number):
    value = float(sub(r'[^\d.]', '', number))
    return value

###########Gain information from given website############

siteUrl='coinmarketcap.com/currencies/bitcoin/#markets'
r  = requests.get("http://" + siteUrl)
site=r.text
siteSoup=BeautifulSoup(site, "lxml")

#print(siteSoup.prettify())

##########################################################

###########Parsing for pairs############

#print(siteSoup.find_all(href=isPair))
pairs=siteSoup.find_all(href=isPair)
pairList=[]
for pair in pairs:
    pairList.append(pair.text)

pairList=pairList[9:-4] #begining and end of list is not pairs as href filter was not perfect
#print(pairList)

#########################################

###########Parsing for prices############

prices=siteSoup.find_all(class_='price')
priceList=[]
for price in prices:
    #print(price.text)
    priceList.append(convertMoney(price.text))

#print(priceList)

#########################################

###########Parsing for volumes############

volumes=siteSoup.find_all(class_='volume')
volumeList=[]
for volume in volumes:
    volumeList.append(convertMoney(volume.text))

#print(volumeList)

#########################################

###########Parsing for exchanges############

exchanges=siteSoup.find_all(href=isExchange)
exchangeList=[]
for exchange in exchanges:
    exchangeList.append(exchange.text)

exchangeList=exchangeList[1:] #first tag is not an exchange so this removes it from the list

#print(exchangeList)

#########################################



minVolume=1000000
#helper function to use only markets which have a minimum amount of activity on it set by minVolume
def liquidityBound(volumeList):
    maxIndex=0
    for i in range(len(volumeList)-1):
        if (volumeList[i]<minVolume):
            maxIndex=i
            break
    return volumeList[:maxIndex]

#trimms all lists to remove illiquid markets
volumeList=liquidityBound(volumeList)
lengthOfData=len(volumeList)
exchangeList=exchangeList[:lengthOfData]
priceList=priceList[:lengthOfData]
pairList=pairList[:lengthOfData]


#test to make sure all have same length
#print(len(exchangeList))
#print(len(priceList))
#print(len(volumeList))
#print(len(pairList))

#place data in a panda (no longer need volume)
data = pd.DataFrame({   'Exchange' : exchangeList, 'Pair' : pairList, 'Price' : priceList}) 

####################################
##########End of Parsing############
####################################


####################################
##########Start of Trade############
####################################

#############Finds the biggest mismatch between markets################
def findTwoStepTrade(data, currency):
    currencyStarted = data[data['Pair'].str.contains(currency)]
    differences=currencyStarted.groupby('Pair')['Price'].agg(np.ptp)
    whatToTrade=differences[differences==differences.max()]
    whatToTrade=whatToTrade.iloc[[0,]].index.tolist()
    whatToTrade=whatToTrade[0]
    tradingCurrency = data[data['Pair'].str.contains(whatToTrade)]
    min=tradingCurrency.loc[tradingCurrency['Price'].idxmin()]
    max=tradingCurrency.loc[tradingCurrency['Price'].idxmax()]
    currencyTraded=min['Pair'].replace(currency,"")
    currencyTraded=currencyTraded.replace("/","")
    return currencyTraded, min, max



#print(findTwoStepTrade(data,'BTC'))

###############adds more than 2 step trading compounds mismatch between markets#############
def findTrade(complexity, data, currency):
    if complexity==0:
        print()
    else:
        [newCurrency, buy, sell] = findTwoStepTrade(data,currency)
        print('Buy From:')
        print(buy)
        print()
        findTrade(complexity-2,data, newCurrency)
        print('Sell To:')
        print(sell)
        print()



####################################
############End of Trade############
####################################

##########Runs the Code#############
complexity = int(input("What's your desired complexity for this trade? (must be a multiple of two currently)"))
#Assuming we have to start with dollars as currency
findTrade(complexity, data, 'USD')