import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SERVICE_ACCOUNT_FILE = 'core/credentials.json'
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build("drive", "v3", credentials=credentials)

def upload_file_to_drive(file, filename, folder_id):
    """
    Upload a Django InMemoryUploadedFile to Google Drive Shared Drive
    and return the shareable link.
    """
    file_metadata = {
        "name": filename,
        "parents": [folder_id]  # Shared Drive folder ID
    }

    media = MediaIoBaseUpload(file, mimetype=file.content_type, resumable=True)

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True  # ✅ Important for Shared Drives
    ).execute()

    file_id = uploaded_file.get("id")

    # Make file shareable
    drive_service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
        supportsAllDrives=True  # ✅ Also required here
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
