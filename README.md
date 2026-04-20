# Google Drive Download

Script Python để kết nối Google Drive bằng service account, lấy danh sách file trong một thư mục và tải các file đó về thông qua Google Drive API.

## Tính năng hiện có

- Kết nối Google Drive bằng `credentials.json`
- Đọc cấu hình thư mục từ file `.env`
- Liệt kê file trong một folder Google Drive
- Bỏ qua các item là folder
- Chuyển dữ liệu API sang model bằng `@dataclass`
- Tải file từ Google Drive

## Yêu cầu

- Python `>= 3.10`
- Google Cloud service account có quyền đọc Google Drive
- Folder Google Drive đã được chia sẻ cho service account

## Cài đặt

### 1. Clone project

```bash
git clone <your-repo-url>
cd gdrive-download
```

### 2. Cài dependency

Nếu dùng `uv`:

```bash
uv sync
```

Hoặc dùng `pip`:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv tqdm
```

## Cấu hình

### 1. Tạo service account

Trong Google Cloud:

1. Tạo project hoặc dùng project có sẵn
2. Enable Google Drive API
3. Tạo Service Account
4. Tải file JSON key về
5. Đổi tên thành `credentials.json` và đặt ở thư mục root của project

### 2. Chia sẻ quyền truy cập folder

Lấy email của service account trong file JSON, sau đó share folder Google Drive cho email đó với quyền đọc.

### 3. Tạo file `.env`

Tạo file `.env` ở thư mục root:

```env
FOLDER_ID=your_google_drive_folder_id
```

Bạn có thể lấy `FOLDER_ID` từ URL của folder:

```text
https://drive.google.com/drive/folders/<FOLDER_ID>
```

## Cách chạy

Nếu dùng `uv`:

```bash
uv run python main.py
```

Hoặc dùng Python trực tiếp:

```bash
python main.py
```

## Cấu trúc chính

- `main.py`: logic kết nối Google Drive, đọc danh sách file và tải file
- `credentials.json`: khóa service account
- `.env`: cấu hình `FOLDER_ID`
- `pyproject.toml`: khai báo dependency của project

## Luồng hoạt động

1. Đọc biến môi trường từ `.env`
2. Khởi tạo Google Drive service bằng service account
3. Liệt kê toàn bộ file trong folder được cấu hình
4. Bỏ qua các item có kiểu folder
5. Convert dữ liệu sang `FileModel`
6. Tải từng file qua Google Drive API

## Lưu ý

- Service account phải được cấp quyền truy cập vào folder cần đọc
- Project hiện đang dùng quyền `drive.readonly`
- Nếu thiếu `credentials.json` hoặc `FOLDER_ID`, chương trình sẽ không chạy được
- File log được in ra console để tiện debug

## Dependency chính

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`
- `python-dotenv`
- `tqdm`

## Hướng phát triển tiếp

- Lưu file tải về ra thư mục local
- Hiển thị progress download rõ ràng hơn
- Xử lý lỗi chi tiết hơn khi tải file
- Thêm test cho phần map dữ liệu sang `FileModel`
