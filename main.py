import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import dotenv_values
import io
from googleapiclient.http import MediaIoBaseDownload

config = dotenv_values(".env")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# cấu hình logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
logger = logging.getLogger(__name__)


def get_service():
    logger.info("Initializing Google Drive service...")
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    logger.info("Google Drive service initialized")
    return service


def list_files_in_folder(service, folder_id):
    logger.info(f"Listing files in folder: {folder_id}")

    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get("files", [])
    logger.info(f"Found {len(files)} files")

    return files



def main():
    logger.info("Program started")

    service = get_service()
    folder_id = config["FOLDER_ID"]

    files = list_files_in_folder(service, folder_id)

    for f in files:
        logger.info(f"File found: {f['name']} ({f['id']})")

    logger.info("Program finished")


if __name__ == "__main__":
    main()