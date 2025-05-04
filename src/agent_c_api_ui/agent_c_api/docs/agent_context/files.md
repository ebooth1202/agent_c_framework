# Files API

> **Documentation generated**: May 1, 2025

Endpoints for managing files that can be used in agent sessions.

## Upload File

```
POST /api/v1/upload_file
```

Uploads a file for use in chat.

### Form Data Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |
| `file` | file | Yes | The file to upload |

#### Request Example

```
POST /api/v1/upload_file
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="ui_session_id"

ses_1234567890abcdef
--boundary
Content-Disposition: form-data; name="file"; filename="example.pdf"
Content-Type: application/pdf

[Binary data]
--boundary--
```

### Response

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | File ID for referencing in chat |
| `filename` | string | Original filename |
| `mime_type` | string | MIME type of the file |
| `size` | number | File size in bytes |

#### Response Example

```json
{
  "id": "file_7890abcdef1234",
  "filename": "example.pdf",
  "mime_type": "application/pdf",
  "size": 12345
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found |
| 500 | Internal Server Error - Error uploading file |

## List Session Files

```
GET /api/v1/files/{ui_session_id}
```

Lists all files uploaded for a specific session.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `files` | array | List of files in the session |
| `files[].id` | string | File ID |
| `files[].filename` | string | Original filename |
| `files[].mime_type` | string | MIME type of the file |
| `files[].size` | number | File size in bytes |
| `files[].upload_time` | string | ISO 8601 timestamp of when the file was uploaded |
| `files[].processed` | boolean | Whether the file has been processed |
| `files[].processing_status` | string | Processing status (e.g., "completed", "failed", "pending") |
| `files[].processing_error` | string | Error message if processing failed (null if no error) |

#### Response Example

```json
{
  "files": [
    {
      "id": "file_7890abcdef1234",
      "filename": "example.pdf",
      "mime_type": "application/pdf",
      "size": 12345,
      "upload_time": "2025-04-30T08:40:00.000Z",
      "processed": true,
      "processing_status": "completed",
      "processing_error": null
    },
    {
      "id": "file_5678abcdef9012",
      "filename": "data.csv",
      "mime_type": "text/csv",
      "size": 5432,
      "upload_time": "2025-04-30T09:15:00.000Z",
      "processed": true,
      "processing_status": "completed",
      "processing_error": null
    }
  ]
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session not found |
| 500 | Internal Server Error - Error listing files |

## Get File

```
GET /api/v1/files/{ui_session_id}/{file_id}
```

Retrieves metadata for a specific file.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |
| `file_id` | string | Yes | The file ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | File ID |
| `filename` | string | Original filename |
| `mime_type` | string | MIME type of the file |
| `size` | number | File size in bytes |

#### Response Example

```json
{
  "id": "file_7890abcdef1234",
  "filename": "example.pdf",
  "mime_type": "application/pdf",
  "size": 12345
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session or file not found |
| 500 | Internal Server Error - Error retrieving file |

## Delete File

```
DELETE /api/v1/files/{ui_session_id}/{file_id}
```

Deletes a specific file.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ui_session_id` | string | Yes | The UI session ID |
| `file_id` | string | Yes | The file ID |

### Response

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Confirmation message |

#### Response Example

```json
{
  "message": "File example.pdf deleted successfully"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 404 | Not Found - Session or file not found |
| 500 | Internal Server Error - Error deleting file |