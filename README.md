# Splitwise Bill Splitter

This is an hobby project to split the grocery expense among my roommates to easily calculate the split with tax percentages and present it in neat tabular visualization.

This expense is then published to splitwise group if `--publish` flag is added to the command.

This program accepts the input in the form of Excel which is created from prebuilt excel template.

## Setup

Run the below command to install the package locally into your OS

```bash
pip install -e .
```

## Usage

### Add Bill
To run this command, type `addBill` from any path in the terminal.
This will create a new Microsoft Excel file with the base General_Bill_Template.xlsx

This addBill is a choice like command, so you have to specify the store name or add new store before proceeding.

```bash
addBill
```

### Show Bill Split
This command will create the split based on the excel sheet.
> Don't forget to save the sheet before running this command

This showBillSplit is a fuzzy logic command, which shows the results based on your search.
There is also a handy boolean wrapper to this command, which proceeds with the last modified file, if requested.

```bash
showBillSplit
```

> Note: This Show Bill Split just shows the split locally, it does not affect the splitwise

### Publish Bill

This command will publish the bill based on the excel sheet.

This Publish Bill is also a fuzzy logic command, which shows the results based on your search.
There is also a handy boolean wrapper to this command, which proceeds with the last modified file, if requested.

```bash
publishBill
```

There are 3 things needed for publishing
1. CONSUMER_KEY
2. CONSUMER_SECRET
3. API_KEY

All of these has to be obtained from the splitwise API website.
Add all these parameters in the `.env` file

### Existing .env file

```text
CONSUMER_KEY="Dr...6"
CONSUMER_SECRET="uW...l"
API_KEY="UM...y"
```
