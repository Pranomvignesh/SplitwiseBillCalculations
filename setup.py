from setuptools import setup, find_packages

setup(
    name="split_bill",
    version="0.0.1",
    packages=['main'],
    install_requires = [
        'InquirerPy',
        'pdfkit',
        'splitwise',
        'openpyxl',
        'dotenv'
    ],
    entry_points='''
    [console_scripts]
        addBill=main:add_bill
        showBillSplit=main:show_bill_split
        publishBill=main:publish_bill
    '''
)