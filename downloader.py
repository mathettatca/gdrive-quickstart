import io
import logging
from typing import TYPE_CHECKING

from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm

from main import FileModel, get_service

logger = logging.getLogger(__name__)

def download_file_from_drive(service, files: list["FileModel"]) -> bool:
    



if __name__ == "__main__":
    files_list = [
        {"id": "1LS3rnSCEmLMi4yEXj8k15xIpcErFMHMW", "name": "detail_Vietnam_import_hs63.xlsx"},
        {"id": "13sGoDLJ5uUbPLuF-jGGyfe380fdi1HCP", "name": "FINALIZED_import_54.xlsx"},
        {"id": "1F07Ct3ohjB9Td5nXGR6r6m9WKEJ-3c5e", "name": "FINALIZED_export_54.xlsx"},
        {"id": "1cPdkz7SIOQUtX3g90VAmHCN7qEBZ4j8k", "name": "FINALIZED_export_53.xlsx"},
        {"id": "1OBBaOsB320mggvqsB5r44N9BfCw6txT9", "name": "FINALIZED_export_52.xlsx"},
        {"id": "1kjrKLEpwVoEnzWTj1BkaUSZD9FbLl12y", "name": "FINALIZED_detail_Vietnam_export_hs58.xlsx"},
        {"id": "1viVwUl_BbdK9IG72Lp4XFJluW8vMkaLh", "name": "FINALIZED_detail_Vietnam_export_hs34.xlsx"},
        {"id": "1J0Bgkv5IIe5HGiBL5drlShdQalTAmvLI", "name": "FINALIZED_import_51.xlsx"},
        {"id": "1pZ6HnV959L19NC04T104Rv5K1RJVulTU", "name": "FINALIZED_import_52.xlsx"},
        {"id": "1q3Jvf62v9cl5z4iukKBLF9i-gpAuoNgl", "name": "FINALIZED_import_53.xlsx"}
    ]

    files_list_model :list[FileModel] = []
    for file in files_list:
        files_list_model.append(FileModel.to_model(file))

    download_file_from_drive(service=get_service(),files=files_list_model)