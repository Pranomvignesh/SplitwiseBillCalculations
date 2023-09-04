from setuptools import setup, find_packages

setup(
    name="split-bill",
    version="0.0.1",
    packages=find_packages(),
    install_requires = [
        'InquirerPy',
        'pdfkit',
        'splitwise',
        'openpyxl'
    ],
    entry_points='''
    [console_scripts]
        addBill=main:addBill
        showBillSplit=main:showBillSplit
        publishBill=main:publishBill
    '''
)
