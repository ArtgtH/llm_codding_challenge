# Google Drive Integration

This document describes the Google Drive integration functionality used to store documents generated from agricultural reports.

## Overview

The application saves two types of documents to Google Drive:

1. **Word Documents**: Original message texts converted to Word format
2. **Excel Spreadsheets**: Structured agricultural data extracted from messages

## Components

### Google Drive Uploader

The `GoogleDriveUploader` class (`google_drive_uploader.py`) handles all interactions with Google Drive:

1. Authenticates with Google Drive using service account credentials
2. Creates folders and subfolders for organizing documents
3. Uploads new files and updates existing files
4. Provides file and folder URLs for reference

### Utilities

The `utils.py` file provides helper functions for the Google Drive integration:

1. `text_to_word_bytes()`: Converts text messages to Word document bytes
2. `get_document_name()`: Generates standardized filenames for Word documents
3. `get_table_name()`: Generates standardized filenames for Excel spreadsheets

## Authentication

Authentication with Google Drive uses a service account:

1. A JSON credentials file is stored in `google_drive/api_key/`
2. The service account must have access to the target Google Drive folders
3. The path to the credentials file is configured in `google_drive_uploader.py`

## Folder Structure

Documents in Google Drive are organized in a hierarchical structure:

```
[Root Folder]
├── [Team Folder 1]
│   ├── word_document_1.docx
│   ├── word_document_2.docx
│   └── excel_report.xlsx
└── [Team Folder 2]
    ├── word_document_1.docx
    ├── word_document_2.docx
    └── excel_report.xlsx
```

Team folders are created automatically if they don't exist.

## File Naming

Files are named using standardized conventions:

### Word Documents

Word documents use the naming convention:
```
{sender_name}_{message_number}_{formatted_date}.docx
```

For example:
```
John_Doe_3_2023-04-15.docx
```

### Excel Spreadsheets

Excel spreadsheets use the naming convention:
```
{team_name}_operations_log.xlsx
```

For example:
```
SlovarikDB_operations_log.xlsx
```

## Upload Modes

The uploader supports different upload modes:

- **W (Write)**: Creates a new file, fails if the file already exists
- **RW (Read-Write)**: Updates an existing file if it exists, otherwise creates a new file

## Error Handling

The Google Drive integration includes error handling for:

1. Authentication failures
2. Network connectivity issues
3. Permission problems
4. File creation and update failures 