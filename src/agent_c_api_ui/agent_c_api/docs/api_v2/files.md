# File Management API

## Overview

The File Management API enables the uploading, retrieval, and management of files within sessions. These files can be referenced in chat messages, allowing for multimodal interactions where users can share documents, images, and other files with the agent.

Files are automatically processed for text extraction (when applicable), which helps the agent understand and reference the file content. All files are associated with specific sessions and can only be accessed within that session context.

## Key Features

- **Secure file uploads**: Upload files to be used in chat messages
- **Automatic processing**: Text extraction and analysis for supported file types
- **File metadata**: Retrieve information about uploaded files
- **Content access**: Download file content when needed
- **Lifecycle management**: Delete files when no longer needed

## Upload a File

```http
POST /api/v2/sessions/{session_id}/files
```

Uploads a file to be used in chat messages within a specific session.

### Path Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `session_id` | UUID | Required. The unique identifier of the session to upload the file to |

### Request

This endpoint accepts `multipart/form-data` with a file field named `file`.

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

(binary file data)
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

### Response

```json
{
  "file_id": "file_abc123",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "size": 1048576
}
```

### Response Fields

| Name | Type | Description |
| ---- | ---- | ----------- |
| `file_id` | String | Unique identifier for the uploaded file (use this in chat messages) |
| `filename` | String | Original filename as provided during upload |
| `content_type` | String | MIME content type of the file |
| `size` | Integer | Size of the file in bytes |

### Error Responses

| Status Code | Error | Description |
| ----------- | ----- | ----------- |
| 404 | NOT_FOUND | Specified session doesn't exist |
| 413 | REQUEST_ENTITY_TOO_LARGE | File exceeds the maximum allowed size |
| 415 | UNSUPPORTED_MEDIA_TYPE | File type is not supported |
| 500 | INTERNAL_SERVER_ERROR | Server error processing the file |

### Example Usage

#### JavaScript

```javascript
async function uploadFile(sessionId, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`/api/v2/sessions/${sessionId}/files`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  
  return await response.json();
}

// Example usage
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', async (e) => {
  try {
    const file = e.target.files[0];
    const fileInfo = await uploadFile('550e8400-e29b-41d4-a716-446655440000', file);
    console.log(`Uploaded ${fileInfo.filename} (${fileInfo.file_id})`);
    
    // You can now reference this file in chat messages
    sendChatMessage('550e8400-e29b-41d4-a716-446655440000', {
      role: 'user',
      content: [
        { type: 'text', text: 'Please analyze this document:' },
        { type: 'file', file_id: fileInfo.file_id }
      ]
    });
  } catch (error) {
    console.error('Upload error:', error);
  }
});
```

#### Python

```python
import requests

def upload_file(session_id, file_path):
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.split('/')[-1], f)}
        response = requests.post(
            f"https://api.example.com/api/v2/sessions/{session_id}/files",
            files=files
        )
    
    if response.status_code != 201:
        raise Exception(f"Upload failed: {response.text}")
    
    return response.json()

# Example usage
try:
    file_info = upload_file(
        "550e8400-e29b-41d4-a716-446655440000", 
        "./document.pdf"
    )
    print(f"Uploaded {file_info['filename']} ({file_info['file_id']})")
    
    # Reference in a chat message
    send_chat_message(
        "550e8400-e29b-41d4-a716-446655440000",
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please analyze this document:"},
                {"type": "file", "file_id": file_info["file_id"]}
            ]
        }
    )
except Exception as e:
    print(f"Error: {str(e)}")
```

## List Files

```http
GET /api/v2/sessions/{session_id}/files
```

Retrieves metadata for all files associated with a specific session.

### Path Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `session_id` | UUID | Required. The unique identifier of the session to list files for |

### Response

```json
[
  {
    "id": "file_abc123",
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "size": 1048576,
    "uploaded_at": "2025-04-04T12:00:00Z",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "processed": true,
      "processing_status": "complete",
      "page_count": 5
    }
  },
  {
    "id": "file_def456",
    "filename": "screenshot.png",
    "content_type": "image/png",
    "size": 256000,
    "uploaded_at": "2025-04-04T12:30:00Z",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "processed": true,
      "processing_status": "complete"
    }
  }
]
```

### Response Fields

| Name | Type | Description |
| ---- | ---- | ----------- |
| `id` | String | Unique identifier for the file |
| `filename` | String | Original filename as provided during upload |
| `content_type` | String | MIME content type of the file |
| `size` | Integer | Size of the file in bytes |
| `uploaded_at` | String | ISO 8601 timestamp of when the file was uploaded |
| `session_id` | UUID | UUID of the session the file belongs to |
| `metadata` | Object | Additional metadata about the file, including processing status |

### Error Responses

| Status Code | Error | Description |
| ----------- | ----- | ----------- |
| 404 | NOT_FOUND | Specified session doesn't exist |
| 500 | INTERNAL_SERVER_ERROR | Server error listing files |

### Example Usage

```javascript
async function listFiles(sessionId) {
  const response = await fetch(`/api/v2/sessions/${sessionId}/files`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list files');
  }
  
  return await response.json();
}

// Display files in the UI
async function displayFiles(sessionId) {
  try {
    const files = await listFiles(sessionId);
    const filesList = document.getElementById('files-list');
    filesList.innerHTML = '';
    
    files.forEach(file => {
      const fileItem = document.createElement('div');
      fileItem.className = 'file-item';
      fileItem.innerHTML = `
        <div class="file-name">${file.filename}</div>
        <div class="file-info">${formatFileSize(file.size)} - ${file.content_type}</div>
        <div class="file-status">Status: ${file.metadata.processing_status || 'unknown'}</div>
        <button data-file-id="${file.id}">Use in Chat</button>
      `;
      filesList.appendChild(fileItem);
    });
  } catch (error) {
    console.error('Error listing files:', error);
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' bytes';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
```

## Get File Metadata

```http
GET /api/v2/sessions/{session_id}/files/{file_id}
```

Retrieves metadata for a specific file in a session.

### Path Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `session_id` | UUID | Required. The unique identifier of the session the file belongs to |
| `file_id` | String | Required. The unique identifier of the file |

### Response

```json
{
  "id": "file_abc123",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "size": 1048576,
  "uploaded_at": "2025-04-04T12:00:00Z",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "processed": true,
    "processing_status": "complete",
    "page_count": 5
  }
}
```

### Error Responses

| Status Code | Error | Description |
| ----------- | ----- | ----------- |
| 404 | NOT_FOUND | Specified session or file doesn't exist |
| 500 | INTERNAL_SERVER_ERROR | Server error retrieving file metadata |

## Download File Content

```http
GET /api/v2/sessions/{session_id}/files/{file_id}/content
```

Downloads the actual content of a file previously uploaded to a session.

### Path Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `session_id` | UUID | Required. The unique identifier of the session the file belongs to |
| `file_id` | String | Required. The unique identifier of the file to download |

### Response

The file content with appropriate `Content-Type` and `Content-Disposition` headers.

### Error Responses

| Status Code | Error | Description |
| ----------- | ----- | ----------- |
| 404 | NOT_FOUND | Specified session or file doesn't exist |
| 500 | INTERNAL_SERVER_ERROR | Server error downloading file |

### Example Usage

```javascript
function downloadFile(sessionId, fileId, filename) {
  // Create a hidden link and click it to trigger the download
  const link = document.createElement('a');
  link.href = `/api/v2/sessions/${sessionId}/files/${fileId}/content`;
  link.download = filename || 'download';
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
```

## Delete File

```http
DELETE /api/v2/sessions/{session_id}/files/{file_id}
```

Permanently removes a file from a session. Once deleted, the file can no longer be referenced in chat messages or downloaded.

### Path Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `session_id` | UUID | Required. The unique identifier of the session the file belongs to |
| `file_id` | String | Required. The unique identifier of the file to delete |

### Response

No content is returned on successful deletion (204 status code).

### Error Responses

| Status Code | Error | Description |
| ----------- | ----- | ----------- |
| 404 | NOT_FOUND | Specified session or file doesn't exist |
| 500 | INTERNAL_SERVER_ERROR | Server error deleting file |

### Example Usage

```javascript
async function deleteFile(sessionId, fileId) {
  try {
    const response = await fetch(`/api/v2/sessions/${sessionId}/files/${fileId}`, {
      method: 'DELETE'
    });
    
    if (response.status === 204) {
      console.log('File successfully deleted');
      return true;
    } else {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete file');
    }
  } catch (error) {
    console.error('Error deleting file:', error);
    return false;
  }
}
```

## Implementation Notes

### File Processing

When files are uploaded, they are automatically processed in the background:

1. **Text Extraction**: For supported document types (PDF, TXT, etc.), the text content is extracted
2. **Image Analysis**: Image files may be analyzed for content (size, format, etc.)
3. **Metadata Generation**: Additional metadata is generated based on the file type and content

### File Retention

Files are retained according to the following rules:

- Files are associated with a specific session and cannot be accessed from other sessions
- Files may be automatically deleted when the session is deleted
- Files may have a retention period (default: 7 days) after which they are automatically deleted

### Supported File Types

The API supports various file types including, but not limited to:

- **Documents**: PDF, TXT, DOCX, XLSX, CSV
- **Images**: PNG, JPEG, GIF, SVG
- **Code**: PY, JS, TS, Java, C#, etc.

File size limitations and specific supported formats may vary based on configuration.