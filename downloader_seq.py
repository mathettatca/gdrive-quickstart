import logging
from dataclasses import dataclass
from time import sleep
from typing import List, Dict

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

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
# DOWNLOAD (SEQUENTIAL)
# =========================
def download_file(service, file: FileModel, position: int = 0) -> str:
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

                # optional: giảm tải network
                sleep(0.1)

    logger.info(f"Completed: {file.name}")
    return file.name


# =========================
# DOWNLOAD ALL (SEQUENTIAL)
# =========================
def download_all(service, files: List[FileModel]) -> Dict[str, str]:
    results = {}

    for i, file in enumerate(files):
        try:
            result = download_file(service, file, position=i)
            results[file.id] = result
        except Exception as e:
            logger.error(f"Failed file {file.id}: {e}")

    return results


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    files_list = [
        {"id": "1LS3rnSCEmLMi4yEXj8k15xIpcErFMHMW", "name": "detail_Vietnam_import_hs63.xlsx"},
        {"id": "13sGoDLJ5uUbPLuF-jGGyfe380fdi1HCP", "name": "FINALIZED_import_54.xlsx"},
        {"id": "1F07Ct3ohjB9Td5nXGR6r6m9WKEJ-3c5e", "name": "FINALIZED_export_54.xlsx"},
    ]

    files_models = [FileModel.to_model(f) for f in files_list]

    service = get_service()

    results = download_all(service, files_models)

    logger.info(f"Downloaded files: {results}")