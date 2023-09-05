import os
import openpyxl
import subprocess
import platform
import glob

from pathlib import Path
from typing import List
from datetime import datetime

TEMPLATE_PATH = Path('./General_Bill_Template.xlsx')
OS = platform.system()


def get_all_child_folders(folder_path: Path, level: int = 1) -> List[str]:
    contents = os.listdir(folder_path)
    folders = [content for content in contents if folder_path.joinpath(
        content).is_dir()]
    return folders


def create_store(folder_name: str, base_folder_path: Path) -> None:
    os.mkdir(base_folder_path.joinpath(folder_name))


def create_new_sheet(store_name: str, base_folder_path: Path) -> str:
    workbook = openpyxl.load_workbook(TEMPLATE_PATH.absolute())
    file_name = f'{store_name}_{datetime.now().strftime("%b-%d-%y[%I-%M-%S %p]")}.xlsx'
    sheet = workbook.active
    sheet['B1'] = store_name
    sheet['D1'] = datetime.now().strftime("%B %d, %Y")
    output_path = base_folder_path.joinpath(store_name, file_name)
    workbook.save(output_path)
    workbook.close()
    return output_path


def open_file_in_excel(file_path: str) -> None:
    if OS == 'Windows':
        subprocess.Popen(['start', file_path], shell=True)
    elif OS == 'Darwin':
        subprocess.Popen(['open', file_path])
    else:
        raise Exception('Unknown OS')


def get_all_excel_files(store_name: str, base_folder_path: Path) -> List[str]:
    folder_path = base_folder_path.joinpath(store_name)
    sheets = [
        content for content in os.listdir(folder_path.absolute())
        if not folder_path.joinpath(content).is_dir()
        and content.endswith('.xlsx')
        and not content.startswith('~$')
    ]
    return sheets


def get_members(config: dict) -> List[str]:
    members = []
    for member, nick_names in config['firstname_nickname_map'].items():
        if len(nick_names) == 0:
            members.append(member)
        else:
            members.append(nick_names[0])
    return members


def get_alias_map(config: dict) -> dict:
    alias = {}
    for member, nick_names in config['firstname_nickname_map'].items():
        if len(nick_names) != 0:
            for nick_name in nick_names:
                alias[nick_name] = member
    return alias


def get_last_modified_file(base_folder_path: Path) -> str:
    pattern_to_include = './**/*.xlsx'
    pattern_to_exclude = './**/~$*.xlsx'

    file_list_to_include = glob.glob(
        str(base_folder_path.joinpath(pattern_to_include)))
    file_list_to_exclude = glob.glob(
        str(base_folder_path.joinpath(pattern_to_exclude)))
    last_modified_file = None
    last_modified_time = None
    for file in file_list_to_include:
        if file not in file_list_to_exclude:
            modified_time = os.path.getmtime(file)
            if last_modified_file is None or last_modified_time > modified_time:
                last_modified_file = file
                last_modified_time = modified_time
    return last_modified_file
