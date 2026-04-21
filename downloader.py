import asyncio
import logging
from dataclasses import dataclass
from time import sleep
from typing import List, Dict, Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from pprint import pformat


from tqdm import tqdm


# =========================
# CONFIG
# =========================
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "credentials.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================
# MODEL
# =========================
@dataclass
class FileModel:
    id: str
    name: str

    @staticmethod
    def to_model(data: dict) -> "FileModel":
        return FileModel(
            id=data["id"],
            name=data["name"]
        )


# =========================
# GOOGLE DRIVE SERVICE
# =========================
def get_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


# =========================
# GET FILE SIZE
# =========================
def get_file_size(service, file_id: str) -> int:
    meta = service.files().get(fileId=file_id, fields="size").execute()
    return int(meta.get("size", 0))


# =========================
# BLOCKING DOWNLOAD + TQDM
# =========================
def download_file_stream(service, file: FileModel, position: int = 0) -> str:
    request = service.files().get_media(fileId=file.id)
    file_size = get_file_size(service, file.id)

    with open(file.name, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=file.name,
            position=position,
            leave=True
        ) as pbar:

            done = False
            last_progress = 0

            while not done:
                status, done = downloader.next_chunk()

                if status:
                    current = int(status.progress() * file_size)
                    delta = current - last_progress
                    pbar.update(delta)
                    last_progress = current

                sleep(0.1)

    logger.info(f"Completed: {file.name}")
    return file.name


# =========================
# ASYNC WRAPPER
# =========================
async def download_file_async(service, file: FileModel, position: int) -> Optional[str]:
    loop = asyncio.get_running_loop()

    try:
        return await loop.run_in_executor(
            None,
            download_file_stream,
            service,
            file,
            position
        )
    except Exception as e:
        logger.error(f"Failed file {file.id}: {e}")
        return None
    
def list_files_in_folder(service, folder_id):
    logger.info(f"Listing files in folder: {folder_id}")

    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q=query,
        fields="files(id, name,size,fileExtension)"
    ).execute()
    logger.info(pformat(results))
    files = results.get("files", [])
    logger.info(f"Found {len(files)} files")

    return files

# =========================
# DOWNLOAD MULTIPLE FILES
# =========================
async def download_all(
    service,
    files: List[FileModel],
    max_concurrent: int = 3
) -> Dict[str, str]:

    semaphore = asyncio.Semaphore(max_concurrent)

    async def sem_task(file: FileModel, pos: int):
        async with semaphore:
            return await download_file_async(service, file, pos)

    tasks = [
        sem_task(f, i) for i, f in enumerate(files)
    ]

    results = await asyncio.gather(*tasks)

    return {
        f.id: result
        for f, result in zip(files, results)
        if result is not None
    }


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    # files_list = [
    #     {"id": "1LS3rnSCEmLMi4yEXj8k15xIpcErFMHMW", "name": "detail_Vietnam_import_hs63.xlsx"},
    #     {"id": "13sGoDLJ5uUbPLuF-jGGyfe380fdi1HCP", "name": "FINALIZED_import_54.xlsx"},
    #     {"id": "1F07Ct3ohjB9Td5nXGR6r6m9WKEJ-3c5e", "name": "FINALIZED_export_54.xlsx"},
    # ]

    # files_models = [FileModel.to_model(f) for f in files_list]

    service = get_service()

    # results = asyncio.run(
    #     download_all(service, files_models, max_concurrent=3)
    # )

    # logger.info(f"Downloaded files: {results}")

    list_files_in_folder(service=service,folder_id='1s65CZOPLT-WMGxbxMTKXl72aIBf14Kqn')