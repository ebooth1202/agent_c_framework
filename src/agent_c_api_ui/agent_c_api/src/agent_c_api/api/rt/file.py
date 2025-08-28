import json
import os
import mimetypes
from pathlib import Path

from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Query
from agent_c.util.logging_utils import LoggingManager
from agent_c.util.uncish_path import UNCishPath

from fastapi.responses import FileResponse

from agent_c_tools.tools.workspace.local_project import LocalProjectWorkspace

router = APIRouter()
logger = LoggingManager(__name__).get_logger()

LOCAL_WORKSPACES_FILE = '.local_workspaces.json'

class WSResolver:
    workspaces: Optional[Dict[str, Path]] = None

    @classmethod
    def _init_workspaces(cls) -> None:
        local_project = LocalProjectWorkspace()
        cls.workspaces['project'] = local_project.workspace_root
        try:
            with open(LOCAL_WORKSPACES_FILE, 'r', encoding='utf-8') as json_file:
                local_workspaces = json.load(json_file)

            for ws in local_workspaces['local_workspaces']:
                cls.workspaces[ws['name']] =  Path(ws['workspace_path']).resolve()
        except FileNotFoundError:
            # Local workspaces file is optional
            pass

    @classmethod
    def resolve_workspace_path(cls, workspace_path: str) -> Path:
        if cls.workspaces is None:
            cls._init_workspaces()

        unc_path: UNCishPath = UNCishPath(workspace_path)
        if not unc_path.source not in cls.workspaces:
            raise ValueError(f"Workspace '{unc_path.source}' is not configured.")

        return Path.joinpath(cls.workspaces[unc_path.source], unc_path.path).resolve()



@router.get("/file/{workspace_path:path}")
async def get_workspace_file(
        workspace_path: str,
        download: bool = Query(False, description="Force download vs inline viewing")
):
    actual_path = WSResolver.resolve_workspace_path(f"//{workspace_path}")

    if not os.path.exists(actual_path) or not os.path.isfile(actual_path):
        raise HTTPException(status_code=404, detail="File not found")

    filename = os.path.basename(actual_path)

    media_type, _ = mimetypes.guess_type(actual_path)

    if media_type is None:
        media_type = 'application/octet-stream'

    headers = {}

    if download:
        headers["Content-Disposition"] = f"attachment; filename={filename}"
    else:
        headers["Content-Disposition"] = f"inline; filename={filename}"

    return FileResponse(actual_path, filename=filename, media_type=media_type, headers=headers)