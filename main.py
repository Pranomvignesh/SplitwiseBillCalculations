import os

from pathlib import Path
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from utils import get_all_child_folders, \
    create_store, \
    create_new_sheet, \
    open_file_in_excel,\
    get_all_excel_files,\
    get_last_modified_file

from split_bill import split_bill

BASE_PATH = Path(__file__).parent

STORES_FOLDER = BASE_PATH.joinpath('./stores').absolute()
if not STORES_FOLDER.exists():
    os.mkdir(STORES_FOLDER)

EXISTING_STORES = get_all_child_folders(STORES_FOLDER)


def add_bill():
    choices = EXISTING_STORES[::]
    choices.append(
        Choice(value='new', name="Add New Store")
    )
    store = inquirer.rawlist(
        message="Select Store",
        choices=choices
    ).execute()
    if store == 'new':
        new_store = inquirer.text(message="Enter the store name:").execute()
        create_store(folder_name=new_store, base_folder_path=STORES_FOLDER)
        store = new_store

    file_path = create_new_sheet(
        store_name=store, base_folder_path=STORES_FOLDER)
    open_file_in_excel(file_path)


def show_bill_split():
    choices = EXISTING_STORES[::]
    if (len(choices) == 0):
        raise Exception(
            "Stores not found. Add a bill using 'addBill' to create split")
    proceed_with_last_modified = inquirer.confirm(
        message="Proceed with last modified file?"
    ).execute()
    if proceed_with_last_modified:
        file = get_last_modified_file(STORES_FOLDER)
        if file is not None:
            file = Path(file)
            print(f"Splitting the bill for {file.name}")
            split_bill(Path(file))
        else:
            print("Could not find a last modified file, Add a bill using 'addBill' to create split")
    else:
        store = inquirer.rawlist(
            message="Select Store",
            choices=choices
        ).execute()
        files = get_all_excel_files(store, STORES_FOLDER)

        file = inquirer.fuzzy(
            message="Select the bill to split",
            choices=files,
            max_height=200
        ).execute()
        split_bill(Path(STORES_FOLDER).joinpath(store, file))



def publish_bill():
    choices = EXISTING_STORES[::]
    if (len(choices) == 0):
        raise Exception(
            "Stores not found. Add a bill using 'addBill' to create split")
    proceed_with_last_modified = inquirer.confirm(
        message="Proceed with last modified file?"
    ).execute()
    if proceed_with_last_modified:
        file = get_last_modified_file(STORES_FOLDER)
        split_bill(Path(STORES_FOLDER).joinpath(store, file), publish=True)
    else:
        store = inquirer.rawlist(
            message="Select Store",
            choices=choices
        ).execute()
        files = get_all_excel_files(store, STORES_FOLDER)

        file = inquirer.fuzzy(
            message="Select the bill to split",
            choices=files,
            max_height=200
        ).execute()
        split_bill(Path(STORES_FOLDER).joinpath(store, file), publish=True)
