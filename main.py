from dataclasses import dataclass, fields
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import dotenv_values
from googleapiclient.discovery import Resource


# from downloader import download_file_from_drive

config = dotenv_values(".env")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# cấu hình logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class FileModel:
    id:str
    name:str

    @classmethod
    def to_model(cls, json: dict) -> "FileModel":
        
        # lấy danh sách field
        field_names = {f.name for f in fields(cls)}
        filtered = {}

        for k, v in json.items():

            if k in field_names:
                filtered[k] = v

        try:
            instance = cls(**filtered)
            return instance
        except Exception as e:
            logger.exception("Failed to create %s from data: %s", cls.__name__, filtered)
            raise



def get_service() -> Resource:
    logger.info("Initializing Google Drive service...")
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    logger.info("Google Drive service initialized")
    return service


# def list_files_in_folder(service, folder_id):
#     logger.info(f"Listing files in folder: {folder_id}")

#     query = f"'{folder_id}' in parents"
#     results = service.files().list(
#         q=query,
#         fields="files(id, name, mimeType)"
#     ).execute()

#     files = results.get("files", [])
#     response:list[FileModel] = []
#     for f in files:
#         logger.info(f"{f}")
#         if f["mimeType"] == 'application/vnd.google-apps.folder':
#             continue
#         response.append(FileModel.to_model(f))
#     logger.info(f"Found {len(files)} files")

#     return response

# def main():
#     logger.info("Program started")

#     service = get_service()
#     folder_id = config["FOLDER_ID"]

#     files : list[FileModel] = list_files_in_folder(service, folder_id)
#     status :bool = download_file_from_drive(service,files)
    


# if __name__ == "__main__":
#     main()
