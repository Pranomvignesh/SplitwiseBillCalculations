# Imports
import pandas as pd
import os
import numpy as np
import pdfkit
import datetime
import argparse

from typing import List
from dotenv import load_dotenv
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser,User

# Argument Parser
parser = argparse.ArgumentParser(
    prog="splitBill.py",
    description="A program to split the bill in a easy readable format and publish it to Splitwise",
    epilog="This program is developed by pranomvignesh"
)
parser.add_argument(
    'ExcelFileName',
    metavar="excel_file_name",
    help="Excel file name which will be used as a data source. This is a required argument for this application",
)
parser.add_argument(
    '--publish','-P',
    default=False,
    action="store_true",
    help="A switch to enable publishing to Splitwise else the program will do a dry run in local machine",
    required=False
)
args = parser.parse_args()

pd.options.mode.chained_assignment = None  # default='warn'

load_dotenv()

# Constants
CONSUMER_KEY=os.getenv('CONSUMER_KEY')
CONSUMER_SECRET=os.getenv('CONSUMER_SECRET')
API_KEY = os.getenv('API_KEY')
FOLDER = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE_NAME = args.ExcelFileName
CAN_PUBLISH = args.publish
REL_PATH = '../'
EXCEL_FILE_PATH = os.path.join(FOLDER,REL_PATH,EXCEL_FILE_NAME)
CSS_PATH = os.path.abspath(os.path.join(FOLDER,'splitBill.css'))
EXCEL_DATA = pd.read_excel(EXCEL_FILE_PATH,header=None)
SHOP_NAME = EXCEL_DATA[1][0]
DATE = EXCEL_DATA[3][0]
BILL = EXCEL_DATA[1][1]
TAX = EXCEL_DATA[3][1]
TOTAL_BILL = EXCEL_DATA[4][1]
PAID_BY = EXCEL_DATA[4][2]
NO_OF_HEADER_ROWS = 4
ADJUSTING_FOR_RANGE = 1
DATE = (datetime.datetime.fromordinal(DATE.toordinal())).strftime('%d-%b-%y')
EXCEL_DATA[3][0] = DATE
OUTPUT_PATH = REL_PATH+'-'.join([SHOP_NAME,DATE+'.pdf'])
ABSOLUTE_OUTPUT_PATH = os.path.abspath(OUTPUT_PATH)
COLUMNS = ['Item']
MEMBERS = ['Sai','Sanjay','Vaikunth','Viki','Hari','Mohit']
NAME_ALIAS = {
    'Viki' : 'Pranom',
    'Hari' : 'Haripranesh',
    'Vaikunth' : 'Lakshay'
}
COLUMNS.extend(MEMBERS)

data = np.zeros((EXCEL_DATA.shape[0]-NO_OF_HEADER_ROWS,len(COLUMNS)))
splittedData = pd.DataFrame(data,columns=COLUMNS)
splittedData[COLUMNS[0]] = np.NaN
index = 0

def expandList(boughtBy:List)->List:
    '''
    This function will expand the boughtBy list into its real form
    For example,
        Common - includes all members, so the list will be all members
        Group1 - will be first 3 members
    '''
    actualBoughtBy = []
    map = {
        'common': MEMBERS,
        'group1': MEMBERS[0:3],
        'group2': MEMBERS[3:],
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

def splitBill(item:str,amount:float,boughtBy:List) -> None:
    '''
    This function splits the amount equally among the members in the bought by list
    This will create a new entry in the output only if the item is not present in the output
    '''
    global index
    existingItems = splittedData['Item'].values.tolist()
    sharingMembers = []
    rowIndex = index
    if item in existingItems:
        rowIndex = existingItems.index(item)
        sharingMembers = expandList(boughtBy)
    else:
        index += 1
        splittedData['Item'][rowIndex] = item
        sharingMembers = expandList(boughtBy)
    
    if(len(sharingMembers) > 0):
        amtForEach = round(amount / len(sharingMembers),3)
        for member in sharingMembers:
            splittedData[member][rowIndex] = splittedData[member][rowIndex] + amtForEach
    pass

def addExpenseToUser(user:User,amountOwed:float) -> ExpenseUser:
    '''
    This function accepts a user and amount owed by the user.
    With that information creates an ExpenseUser object.
    The amount owed by the user is rounded to 3 decimal places
    Note: Paid Share of the users are set to 0 here.
    '''
    expenseUser = ExpenseUser()
    expenseUser.setId(user.getId())
    expenseUser.setOwedShare(round(amountOwed,3))
    expenseUser.setPaidShare(0)
    return expenseUser

def getUserFromMembers(members:List,name:str) -> User|None:
    '''
    This function is used to get the appropriate user object from the 
    list of members in the group.
    This function accepts the member of the group and name of the member to search in the list

    Returns None if no user is found
    '''
    if name in NAME_ALIAS.keys():
        name = NAME_ALIAS[name]
    user = [member for member in members if member.getFirstName() == name]
    if len(user) == 1:
        return user[0]
    return None

splitwise = Splitwise(CONSUMER_KEY,CONSUMER_SECRET,api_key=API_KEY)
current = splitwise.getCurrentUser()
groups = splitwise.getGroups()
TARGET_GROUP_NAME = '143 expenses' 
targetGroup = [group for group in groups if group.name == TARGET_GROUP_NAME][0]
groupMembers = targetGroup.getMembers()
expense = Expense()
expense.setCost(TOTAL_BILL)
expense.setCurrencyCode("USD")
expense.setGroupId(targetGroup.id)
expense.setReceipt(OUTPUT_PATH)

for i in range(NO_OF_HEADER_ROWS,EXCEL_DATA.shape[0]):
    item = EXCEL_DATA[0][i]
    amount = EXCEL_DATA[4][i]
    boughtBy = EXCEL_DATA[3][i].split(',')
    splitBill(item,amount,boughtBy)

splittedData = splittedData.dropna()
lastRow = ['Total']
users = []
for i in MEMBERS:
    amountOwed = splittedData[i].sum()
    lastRow.append(splittedData[i].sum())
    user = getUserFromMembers(groupMembers,i)
    if user is not None:
        expenseUser = addExpenseToUser(user,amountOwed)
        if i == PAID_BY:
            expenseUser.setPaidShare(round(TOTAL_BILL,2))
        users.append(expenseUser)

splittedData.loc[len(splittedData.index)] = lastRow

originalTable = EXCEL_DATA.to_html(classes='custom original').replace('NaN','')
splitTable = splittedData.to_html(classes='custom').replace('0.000','')
html_string = f'''
<html>
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

pdfkit.from_string(html_string,ABSOLUTE_OUTPUT_PATH,css=CSS_PATH)
os.system('open '+OUTPUT_PATH.replace(' ','\\ '))

expense.setUsers(users)
expense.setReceipt(ABSOLUTE_OUTPUT_PATH)
expense.setDescription('-'.join([SHOP_NAME,DATE]))
if CAN_PUBLISH is True:
    createdExpense, errors = splitwise.createExpense(expense)
    if errors is not None:
        print(errors.getErrors())
else:
    print('''
    Your result is not published to Splitwise,
    if you want to publish your results, run the script with `--publish` flag
    ''')