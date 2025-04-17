import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO


class GoogleDriveUploader:
    def __init__(self, credentials_path='./api_key/agrohack-92ac54ea0f5e.json'):
        self.credentials_path = credentials_path
        self.service = self._authenticate()
        self.url = "https://drive.google.com/drive/folders/1_9w8N3t1--tbkYRLm5_ZBcJ95hf6zw-h?usp=sharing" ##TEST
        self.subfolder_url = self.create_subfolder(self.url, "SlovarikDB")

    def _authenticate(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        return build('drive', 'v3', credentials=credentials)

    def _parse_folder_id(self, url):
        match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
        if not match:
            raise ValueError("Invalid Google Drive folder URL. Expected format: https://drive.google.com/drive/folders/{folder_id}")
        return match.group(1)

    def upload_file(self, folder_url, filename, file_bytes):
        """
        Upload a file to the specified Google Drive folder.

        Args:
            folder_url (str): URL of the Google Drive folder where the file will be uploaded.
            filename (str): Name of the file to be saved in Google Drive.
            file_bytes (bytes): The content of the file as bytes.

        Returns:
            str: The ID of the uploaded file.

        Raises:
            googleapiclient.errors.HttpError: If an error occurs during the API request.
        """
        folder_id = self._parse_folder_id(folder_url)
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(
            BytesIO(file_bytes),
            mimetype='application/octet-stream',
            resumable=True
        )
        request = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )
        response = request.execute()
        return response.get('id')

    def create_subfolder(self, parent_folder_url, subfolder_name):
        """
        Creates a subfolder in the specified Google Drive folder and returns its URL.

        Args:
            parent_folder_url (str): URL of the parent Google Drive folder.
            subfolder_name (str): Name of the new subfolder to create.

        Returns:
            str: The URL of the newly created subfolder.

        Raises:
            googleapiclient.errors.HttpError: If an error occurs during the API request.
            ValueError: If the parent folder URL is invalid.
        """
        parent_id = self._parse_folder_id(parent_folder_url)
        folder_metadata = {
            'name': subfolder_name,
            'parents': [parent_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        request = self.service.files().create(
            body=folder_metadata,
            fields='id'
        )
        response = request.execute()
        new_folder_id = response.get('id')
        return f'https://drive.google.com/drive/folders/{new_folder_id}'
