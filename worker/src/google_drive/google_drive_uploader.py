import logging
import re
from enum import Enum

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO


logger = logging.getLogger(__name__)


class Mode(Enum):
    W = "write"
    RW = "rewrite"


class GoogleDriveUploader:
    def __init__(
        self, credentials_path="google_drive/api_key/iconic-iridium-457212-v7-98c02dc71ba7.json"
    ):
        self.credentials_path = credentials_path
        self.service = self._authenticate()
        self.url = (
            "https://drive.google.com/drive/folders/1lcZw4lMlMww5zzeZBLCd6-cI71lKvqNg"
        )

    def _authenticate(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build("drive", "v3", credentials=credentials)

    def _parse_folder_id(self, url):
        match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
        if not match:
            raise ValueError(
                "Invalid Google Drive folder URL. Expected format: https://drive.google.com/drive/folders/{folder_id}"
            )
        return match.group(1)

    def upload_or_rewrite_file(self, folder_url, filename, file_bytes, mode: Mode):
        folder_id = self._parse_folder_id(folder_url)
        file_metadata = {"name": filename}
        media = MediaIoBaseUpload(
            BytesIO(file_bytes), mimetype="application/octet-stream", resumable=True
        )
        if mode == Mode.RW:
            query = f"name='{filename}' and '{folder_id}' in parents"
            response = self.service.files().list(q=query).execute()
            files = response.get("files", [])

            if files:
                file_id = files[0]["id"]
                updated_file = (
                    self.service.files()
                    .update(
                        fileId=file_id,
                        body=file_metadata,
                        media_body=media,
                        addParents=folder_id,
                    )
                    .execute()
                )

                return updated_file.get("id")

        file_metadata["parents"] = [folder_id]
        created_file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        return created_file.get("id")

    def get_or_create_subfolder(self, parent_folder_url, subfolder_name):
        parent_id = self._parse_folder_id(parent_folder_url)

        query = f"name='{subfolder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = (
            self.service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )

        folders = response.get("files", [])
        if folders:
            return f"https://drive.google.com/drive/folders/{folders[0]['id']}"

        return self.create_subfolder(parent_folder_url, subfolder_name)

    def create_subfolder(self, parent_folder_url, subfolder_name):
        parent_id = self._parse_folder_id(parent_folder_url)
        folder_metadata = {
            "name": subfolder_name,
            "parents": [parent_id],
            "mimeType": "application/vnd.google-apps.folder",
        }
        request = self.service.files().create(body=folder_metadata, fields="id")
        response = request.execute()
        new_folder_id = response.get("id")
        return f"https://drive.google.com/drive/folders/{new_folder_id}"
