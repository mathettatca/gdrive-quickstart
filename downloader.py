import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import logging
import os
import threading
import time
from typing import TYPE_CHECKING
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm
import pandas as pd
import concurrent.futures
from main import FileModel, get_service

logger = logging.getLogger(__name__)

CHUNK_SIZE = 204800  # 200KB mỗi 
MAX_BUFFER_SIZE = 9830399 
file_lock = threading.Lock()

def get_file_size(service, file_id: str) -> int:
    """Lấy kích thước file từ metadata."""
    meta = service.files().get(fileId=file_id, fields="size").execute()
    return int(meta.get("size", 0))


def download_chunk(service, file_id: str, start: int, end: int) -> tuple[int, bytes]:
    """Tải 1 chunk theo byte range, trả về (start, data)."""
    request = service.files().get_media(fileId=file_id)
    
    # Set byte range header
    request.headers["Range"] = f"bytes={start}-{end}"
    logger.info(f"Handling chunk ({start},{end})")
    response = request.execute()
    logger.info(f"return value ({start},{end})")
    return start, response  # response là bytes của chunk đó


async def download_file_chunked(
    service,
    file:FileModel,
    max_workers: int = 4,
    position: int = 0,
) -> bytes |None:
    """Chia file thành chunks, tải song song, ghép lại."""
    loop = asyncio.get_event_loop()
    file_size = get_file_size(service, file.id)
    with open(f"{file.name}", "wb") as f:
        f.truncate(file_size) 


    #chia chunks
    ranges = []
    start = 0
    while start < file_size:

        ## kiểm tra điểm cuối có của chunk có nhỏ hơn dung lượng file không
        end = min(start + CHUNK_SIZE - 1, file_size - 1)
        ranges.append((start, end))
        start = end + 1

    chunks: dict[int, bytes] = {}
    logger.info(f"Total Size: {file_size}")
    current_buffer_size = 0
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_chunks = {
                ## với mỗi (start,end) trong ranges tạo 1 task
                executor.submit(download_chunk, service, file.id, s, e)
                for s, e in ranges
            }

            with open(file.name, "rb+") as f:
                for future in concurrent.futures.as_completed(future_to_chunks):
                    logger.info("Handling after download chunk")

                    try:
                        start_byte, data = future.result()
                    except Exception as e:
                        logger.exception("Chunk failed", exc_info=e)
                        continue

                    # ghi ngay lập tức, không buffer
                    with file_lock:
                        f.seek(start_byte)
                        f.write(data)

                    logger.info(f"Completed download file : {file.name}")   
    except:
        logger.error("Download file thất bại")
        if os.path.exists(file.name):
            os.remove(file.name)

    return sorted_data


async def download_all(service, files: list, chunk_workers: int = 4) -> dict:
    """Mỗi file chạy tuần tự, nhưng từng file tải chunk song song."""
    results = {}

    for i, f in enumerate(files):
        
        try:
            data = await download_file_chunked(service, f, max_workers=chunk_workers, position=i)
            results[f.id] = data
            break
        except Exception as e:
            logger.error("Failed: id=%s, error=%s", f.id, e)


    return results




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

    asyncio.run(download_all(service=get_service(),files=files_list_model))