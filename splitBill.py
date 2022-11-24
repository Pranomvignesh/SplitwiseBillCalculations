import pandas as pd
import os
import sys
import numpy as np
import pdfkit
import datetime

FOLDER=os.getcwd()
EXCEL_FILE_NAME = sys.argv[1]
EXCEL_FILE_PATH = os.path.join(FOLDER,EXCEL_FILE_NAME)

pd.options.mode.chained_assignment = None  # default='warn'
df = pd.read_excel(EXCEL_FILE_PATH,header=None)
SHOP_NAME = df[1][0]
DATE = df[3][0]
BILL = df[1][1]
TAX = df[3][1]
TOTAL_BILL = df[1][2]
NO_OF_HEADER_ROWS = 4
ADJUSTING_FOR_RANGE = 1
DATE = (datetime.datetime.fromordinal(DATE.toordinal())).strftime('%d-%b-%y')
df[3][0] = DATE
OUTPUT_PATH = '-'.join([SHOP_NAME,DATE+'.pdf'])
columns = ['Item']
members = ['Sai','Sanjay','Vaikunth','Viki','Hari','Mohit']
columns.extend(members)
data = np.zeros((df.shape[0]-NO_OF_HEADER_ROWS,len(columns)))
split = pd.DataFrame(data,columns=columns)
split[columns[0]] = np.NaN
index = 0

def expandList(boughtBy):
    actualBoughtBy = []
    map = {
        'common': members,
        'group1': members[0:3],
        'group2': members[3:],
#         Aliases
        'lakshay': ['Vaikunth'],
        'vignesh' : ['Viki']
    }
    for i in boughtBy:
        if i.lower() in map.keys():
            actualBoughtBy.extend(map[i.lower()])
        else:
            actualBoughtBy.append(i)
    return list(set(actualBoughtBy))
            

def splitBill(item,amount,boughtBy):
    global index
    existingItems = split['Item'].values.tolist()
    sharingMembers = []
    rowIndex = index
    if item in existingItems:
        rowIndex = existingItems.index(item)
        sharingMembers = expandList(boughtBy)
    else:
        index += 1
        split['Item'][rowIndex] = item
        sharingMembers = expandList(boughtBy)
    
    if(len(sharingMembers) > 0):
        amtForEach = round(amount / len(sharingMembers),3)
        for member in sharingMembers:
            split[member][rowIndex] = split[member][rowIndex] + amtForEach
    
for i in range(NO_OF_HEADER_ROWS,df.shape[0]):
    item = df[0][i]
    amount = df[4][i]
    boughtBy = df[3][i].split(',')
    splitBill(item,amount,boughtBy)

split = split.dropna()
LAST_ROW_INDEX = split.shape[0]
LAST_ROW_VALUES = ['Total']
for i in members:
    LAST_ROW_VALUES.append(split[i].sum())
split.loc[len(split.index)] = LAST_ROW_VALUES


originalTable = df.to_html(classes='custom original').replace('NaN','')
splitTable = split.to_html(classes='custom').replace('0.000','')
html_string = f'''
<html>
  <head>
    <!-- <link rel="stylesheet" href="splitBill.css"/> -->
  </head>
  <body>
    <h4> Bill </h4>
    {originalTable}
    <br/>
    <br/>
    <h4> Bill Split Across Members </h4>
    {splitTable}
  </body>
</html>
'''
file = open('sample.html','w')
file.write(html_string)
file.close()

pdfkit.from_string(html_string,OUTPUT_PATH,css='splitBill.css')
os.system('open '+OUTPUT_PATH)