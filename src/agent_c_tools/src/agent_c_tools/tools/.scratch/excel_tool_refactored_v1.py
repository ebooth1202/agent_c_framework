"""
Excel Tools for Agent C Framework - Refactored

Provides comprehensive Excel file manipulation capabilities with proper separation
of business logic and tool interface. This is a thin interface layer that delegates
to business logic components.
"""

import json
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, cast

from agent_c.toolsets import Toolset, json_schema
from agent_c_tools.helpers.validate_kwargs import validate_required_fields
from agent_c_tools.helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path
from agent_c_tools.helpers.media_file_html_helper import get_file_html
from agent_c_tools.tools.workspace.tool import WorkspaceTools

from agent_c_tools.tools.excel.business_logic.workbook_manager import WorkbookManager
from agent_c_tools.tools.excel.business_logic.concurrency_manager import ConcurrencyManager
from agent_c_tools.tools.excel.business_logic.excel_operations import ExcelOperations
from agent_c_tools.tools.excel.models import ReadResult


class ExcelTools(Toolset):
    """
    Gives your agent comprehensive Excel file manipulation capabilities designed for high-volume operations
    and multi-agent workflows. Your agent can create, read, write, and modify Excel files with support for
    thousands to millions of records, concurrent writing by multiple agents, and memory-efficient processing
    of large datasets from any data source.
    """
    
    DEFAULT_EXCEL_FOLDER = 'excel_data'
    MAX_EXCEL_TOKEN_SIZE = 35000
    MAX_ROWS_PER_SHEET = 1000000  # Stay under Excel's 1,048,576 limit
    DEFAULT_CHUNK_SIZE = 10000    # Process data in chunks for memory efficiency
    
    def __init__(self, **kwargs):
        """Initialize the ExcelTools."""
        super().__init__(**kwargs, name='excel')
        
        # Dependencies
        self.workspace_tool: Optional[WorkspaceTools] = None
        
        # Business logic components
        self.workbook_manager = WorkbookManager()
        self.concurrency_manager = ConcurrencyManager()
        self.excel_operations = ExcelOperations()
        
    async def post_init(self):
        """Initialize dependencies after tool chest is available."""
        self.workspace_tool = cast(WorkspaceTools, self.tool_chest.available_tools.get('WorkspaceTools'))
        if not self.workspace_tool:
            self.logger.error("WorkspaceTools dependency not available")

    def _is_response_too_big(self, response: str) -> bool:
        """Check if response exceeds token limit."""
        if not hasattr(self.tool_chest, 'agent'):
            return len(response) > self.MAX_EXCEL_TOKEN_SIZE * 4  # Rough estimate
        
        token_count = self.tool_chest.agent.count_tokens(response)
        return token_count > self.MAX_EXCEL_TOKEN_SIZE

    async def _progress_callback(self, message: str, tool_context: Dict[str, Any]):
        """Callback for progress updates during long operations."""
        await self._raise_text_delta_event(message + '\\n', tool_context=tool_context)

    @json_schema(
        description='Create a new Excel workbook in memory',
        params={}
    )
    async def create_workbook(self, **kwargs) -> str:
        """Create a new Excel workbook in memory."""
        try:
            result = self.workbook_manager.create_workbook()
            
            # Reset concurrency tracking for new workbook
            self.concurrency_manager.sheet_row_counts.clear()
            self.concurrency_manager.row_reservations.clear()
            
            return json.dumps(result.to_dict())
            
        except Exception as e:
            self.logger.error(f"Error in create_workbook: {str(e)}")
            return json.dumps({
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            })

    @json_schema(
        description='Load an Excel workbook from workspace using UNC path',
        params={
            'path': {
                'type': 'string',
                'description': 'UNC-style path to the Excel file (e.g., //workspace/path/file.xlsx)',
                'required': True
            },
            'read_only': {
                'type': 'boolean', 
                'description': 'Open workbook in read-only mode for better performance with large files',
                'required': False,
                'default': False
            }
        }
    )
    async def load_workbook(self, **kwargs) -> str:
        """Load an Excel workbook from workspace."""
        try:
            # Validate required fields
            success, message = validate_required_fields(kwargs, ['path'])
            if not success:
                return json.dumps({'success': False, 'error': message})
            
            unc_path = kwargs.get('path')
            read_only = kwargs.get('read_only', False)
            
            self.logger.info(f"Loading workbook from {unc_path}")
            
            # Validate workspace path and get OS path
            error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
            if error:
                return json.dumps({'success': False, 'error': error})
            
            os_path = os_file_system_path(self.workspace_tool, unc_path)
            if not os_path:
                return json.dumps({'success': False, 'error': 'Could not resolve file path'})
            
            # Load workbook using business logic
            result = self.workbook_manager.load_workbook(os_path, read_only)
            
            if result.success:
                # Reset concurrency tracking for new workbook
                self.concurrency_manager.sheet_row_counts.clear()
                self.concurrency_manager.row_reservations.clear()
                
                # Update concurrency manager with sheet row counts
                for sheet_info in result.sheets:
                    self.concurrency_manager.update_sheet_row_count(
                        sheet_info.name, sheet_info.max_row
                    )
            
            response_data = result.to_dict()
            response_data['message'] = 'Excel workbook loaded successfully' if result.success else result.error
            
            return json.dumps(response_data)
            
        except Exception as e:
            error_msg = f"Error loading workbook: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Save the current workbook to workspace using UNC path',
        params={
            'path': {
                'type': 'string',
                'description': 'UNC-style path where to save the Excel file (e.g., //workspace/path/file.xlsx)',
                'required': True
            },
            'create_backup': {
                'type': 'boolean',
                'description': 'Create a backup of existing file before overwriting',
                'required': False,
                'default': False
            }
        }
    )
    async def save_workbook(self, **kwargs) -> str:
        """Save the current workbook to workspace."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False, 
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            # Validate required fields
            success, message = validate_required_fields(kwargs, ['path'])
            if not success:
                return json.dumps({'success': False, 'error': message})
            
            unc_path = kwargs.get('path')
            create_backup = kwargs.get('create_backup', False)
            tool_context = kwargs.get('tool_context', {})
            
            self.logger.info(f"Saving workbook to {unc_path}")
            
            # Ensure .xlsx extension
            unc_path = ensure_file_extension(unc_path, 'xlsx')
            
            # Create backup if requested
            if create_backup:
                error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
                if not error:
                    os_path = os_file_system_path(self.workspace_tool, unc_path)
                    if os_path and os_path.exists():
                        backup_path = unc_path.replace('.xlsx', f'_backup_{int(time.time())}.xlsx')
                        await self.workspace_tool.cp(src_path=unc_path, dest_path=backup_path)
                        self.logger.info(f"Backup created: {backup_path}")
            
            # Save workbook using business logic
            save_result, workbook_bytes = self.workbook_manager.save_workbook(unc_path)
            
            if not save_result.success or not workbook_bytes:
                return json.dumps(save_result.to_dict())
            
            # Write to workspace
            write_result = await self.workspace_tool.internal_write_bytes(
                path=unc_path,
                data=workbook_bytes,
                mode='write'
            )
            
            # Check for write errors
            result_data = json.loads(write_result)
            if 'error' in result_data:
                return json.dumps({
                    'success': False,
                    'error': f"Failed to save workbook: {result_data['error']}"
                })
            
            # Get OS path for media event
            os_path = os_file_system_path(self.workspace_tool, unc_path)
            
            # Raise media event
            if os_path:
                await self._raise_render_media(
                    sent_by_class=self.__class__.__name__,
                    sent_by_function='save_workbook',
                    content_type="text/html",
                    content=get_file_html(
                        os_path=str(os_path),
                        unc_path=unc_path,
                        additional_html="Excel workbook saved successfully"
                    ),
                    tool_context=tool_context
                )
            
            response_data = save_result.to_dict()
            response_data['message'] = 'Excel workbook saved successfully'
            response_data['backup_created'] = create_backup
            
            return json.dumps(response_data)
            
        except Exception as e:
            error_msg = f"Error saving workbook: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='List all sheets in the current workbook with basic information',
        params={}
    )
    async def list_sheets(self, **kwargs) -> str:
        """List all sheets in the current workbook."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False,
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            result = self.workbook_manager.get_workbook_info()
            
            if not result.success:
                return json.dumps(result.to_dict())
            
            # Add tracked row counts from concurrency manager
            sheets_data = result.data.get('sheets', [])
            for sheet_data in sheets_data:
                sheet_name = sheet_data['name']
                if sheet_name in self.concurrency_manager.sheet_row_counts:
                    sheet_data['tracked_row_count'] = self.concurrency_manager.sheet_row_counts[sheet_name]
            
            return json.dumps({
                'success': True,
                'sheets': sheets_data,
                'total_sheets': result.data.get('total_sheets', 0),
                'active_sheet': result.data.get('active_sheet', '')
            })
            
        except Exception as e:
            error_msg = f"Error listing sheets: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Create a new sheet in the current workbook',
        params={
            'sheet_name': {
                'type': 'string',
                'description': 'Name for the new sheet',
                'required': True
            },
            'index': {
                'type': 'integer',
                'description': 'Position where to insert the sheet (0-based). If not provided, adds at the end.',
                'required': False
            }
        }
    )
    async def create_sheet(self, **kwargs) -> str:
        """Create a new sheet in the current workbook."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False,
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            # Validate required fields
            success, message = validate_required_fields(kwargs, ['sheet_name'])
            if not success:
                return json.dumps({'success': False, 'error': message})
            
            sheet_name = kwargs.get('sheet_name')
            index = kwargs.get('index')
            
            # Create sheet using business logic
            result = self.workbook_manager.create_sheet(sheet_name, index)
            
            if result.success:
                # Initialize row tracking for new sheet
                self.concurrency_manager.sheet_row_counts[sheet_name] = 0
                self.logger.info(f"Created sheet: {sheet_name}")
            
            response_data = result.to_dict()
            response_data['message'] = f'Sheet "{sheet_name}" created successfully' if result.success else result.error
            
            return json.dumps(response_data)
            
        except Exception as e:
            error_msg = f"Error creating sheet: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Reserve a range of rows for concurrent writing by multiple agents',
        params={
            'row_count': {
                'type': 'integer',
                'description': 'Number of rows to reserve',
                'required': True
            },
            'sheet_name': {
                'type': 'string',
                'description': 'Name of the sheet to reserve rows in',
                'required': False,
                'default': 'Sheet'
            },
            'agent_id': {
                'type': 'string',
                'description': 'Unique identifier for the agent requesting the reservation',
                'required': False
            }
        }
    )
    async def reserve_rows(self, **kwargs) -> str:
        """Reserve a range of rows for exclusive writing by an agent."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False,
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            # Validate required fields
            success, message = validate_required_fields(kwargs, ['row_count'])
            if not success:
                return json.dumps({'success': False, 'error': message})
            
            row_count = kwargs.get('row_count')
            sheet_name = kwargs.get('sheet_name', 'Sheet')
            agent_id = kwargs.get('agent_id')
            
            if row_count <= 0:
                return json.dumps({
                    'success': False,
                    'error': 'row_count must be greater than 0'
                })
            
            workbook = self.workbook_manager.get_workbook()
            
            # Ensure sheet exists
            if sheet_name not in workbook.sheetnames:
                create_result = self.workbook_manager.create_sheet(sheet_name)
                if not create_result.success:
                    return json.dumps(create_result.to_dict())
                self.concurrency_manager.sheet_row_counts[sheet_name] = 0
            
            # Get current sheet max row
            sheet = workbook[sheet_name]
            current_max_row = sheet.max_row
            
            # Reserve rows using business logic
            result = await self.concurrency_manager.reserve_rows(
                row_count=row_count,
                sheet_name=sheet_name,
                current_max_row=current_max_row,
                agent_id=agent_id
            )
            
            if result.success:
                self.logger.info(f'Reserved rows for agent {result.data["agent_id"]}: '
                               f'{result.data["start_row"]}-{result.data["end_row"]} in sheet "{sheet_name}"')
            
            return json.dumps(result.to_dict())
            
        except Exception as e:
            error_msg = f'Error reserving rows: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Append records to the end of a sheet - safe for concurrent operations',
        params={
            'records': {
                'type': 'array',
                'description': 'Array of records to append. Each record should be an array of values.',
                'required': True,
                'items': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            },
            'sheet_name': {
                'type': 'string',
                'description': 'Name of the sheet to append to',
                'required': False,
                'default': 'Sheet'
            },
            'headers': {
                'type': 'array',
                'description': 'Column headers to add if sheet is empty',
                'required': False,
                'items': {'type': 'string'}
            },
            'agent_id': {
                'type': 'string',
                'description': 'Unique identifier for the agent performing the operation',
                'required': False
            },
            'chunk_size': {
                'type': 'integer',
                'description': 'Number of records to process in each batch for memory efficiency',
                'required': False,
                'default': 10000
            }
        }
    )
    async def append_records(self, **kwargs) -> str:
        """Append records to the end of a sheet."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False,
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            # Validate required fields
            success, message = validate_required_fields(kwargs, ['records'])
            if not success:
                return json.dumps({'success': False, 'error': message})
            
            records = kwargs.get('records')
            sheet_name = kwargs.get('sheet_name', 'Sheet')
            headers = kwargs.get('headers')
            agent_id = kwargs.get('agent_id', f'agent_{uuid.uuid4().hex[:8]}')
            chunk_size = kwargs.get('chunk_size', self.DEFAULT_CHUNK_SIZE)
            tool_context = kwargs.get('tool_context', {})
            client_wants_cancel: threading.Event = tool_context.get('client_wants_cancel', threading.Event())
            
            if not records:
                return json.dumps({
                    'success': False,
                    'error': 'No records provided to append'
                })
            
            self.logger.info(f'Starting append operation for agent {agent_id}: {len(records)} records to sheet "{sheet_name}"')
            
            async with self.concurrency_manager.get_write_lock():
                workbook = self.workbook_manager.get_workbook()
                
                # Append records using business logic
                result = await self.excel_operations.append_records(
                    workbook=workbook,
                    records=records,
                    sheet_name=sheet_name,
                    headers=headers,
                    agent_id=agent_id,
                    chunk_size=chunk_size,
                    client_wants_cancel=client_wants_cancel,
                    progress_callback=lambda msg: self._progress_callback(msg, tool_context)
                )
                
                if result.success:
                    # Update concurrency manager row tracking
                    self.concurrency_manager.update_sheet_row_count(sheet_name, result.end_row)
                    
                    self.logger.info(f'Append operation completed: wrote {result.records_written} records '
                                   f'to rows {result.start_row}-{result.end_row}')
                
                # Handle cancellation
                if client_wants_cancel.is_set():
                    await self._render_media_markdown(
                        '**Append operation cancelled by user**',
                        'append_records',
                        tool_context=tool_context
                    )
                    # Still return partial results
                
                response_data = result.to_dict()
                response_data['message'] = (f'Successfully appended {result.records_written} records to sheet "{sheet_name}"'
                                          if result.success else result.error)
                
                return json.dumps(response_data)
                
        except Exception as e:
            error_msg = f'Error appending records: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Write data to a previously reserved row range - guaranteed conflict-free',
        params={
            'reservation_id': {
                'type': 'string',
                'description': 'ID of the row reservation returned by reserve_rows',
                'required': True
            },
            'records': {
                'type': 'array',
                'description': 'Array of records to write. Each record should be an array of values.',
                'required': True,
                'items': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            }
        }
    )
    async def write_to_reservation(self, **kwargs) -> str:
        """Write data to a previously reserved row range."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False,
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            # Validate required fields
            success, message = validate_required_fields(kwargs, ['reservation_id', 'records'])
            if not success:
                return json.dumps({'success': False, 'error': message})
            
            reservation_id = kwargs.get('reservation_id')
            records = kwargs.get('records')
            
            # Get reservation
            reservation = self.concurrency_manager.get_reservation(reservation_id)
            if not reservation:
                return json.dumps({
                    'success': False,
                    'error': f'Reservation {reservation_id} not found or expired'
                })
            
            if reservation.status.value != 'active':
                return json.dumps({
                    'success': False,
                    'error': f'Reservation {reservation_id} is not active (status: {reservation.status.value})'
                })
            
            # Validate record count fits in reservation
            if len(records) > reservation.row_count:
                return json.dumps({
                    'success': False,
                    'error': f'Too many records ({len(records)}) for reservation ({reservation.row_count} rows)'
                })
            
            workbook = self.workbook_manager.get_workbook()
            
            # Write to reserved rows using business logic
            result = await self.excel_operations.write_to_reserved_rows(
                workbook=workbook,
                records=records,
                sheet_name=reservation.sheet_name,
                start_row=reservation.start_row,
                max_rows=reservation.row_count
            )
            
            if result.success:
                # Mark reservation as completed
                self.concurrency_manager.complete_reservation(reservation_id, len(records))
                
                self.logger.info(f'Wrote {len(records)} records to reserved rows '
                               f'{reservation.start_row}-{result.end_row} in sheet "{reservation.sheet_name}"')
            
            response_data = result.to_dict()
            response_data.update({
                'reservation_id': reservation_id,
                'agent_id': reservation.agent_id,
                'message': (f'Successfully wrote {len(records)} records to reserved rows'
                           if result.success else result.error)
            })
            
            return json.dumps(response_data)
            
        except Exception as e:
            error_msg = f'Error writing to reservation: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Read data from a sheet with optional range specification',
        params={
            'sheet_name': {
                'type': 'string',
                'description': 'Name of the sheet to read from',
                'required': False,
                'default': 'Sheet'
            },
            'start_row': {
                'type': 'integer',
                'description': 'Starting row (1-based). If not provided, reads from row 1.',
                'required': False
            },
            'end_row': {
                'type': 'integer',
                'description': 'Ending row (1-based). If not provided, reads to last row with data.',
                'required': False
            },
            'start_column': {
                'type': 'string',
                'description': 'Starting column (e.g., "A"). If not provided, starts from column A.',
                'required': False
            },
            'end_column': {
                'type': 'string',
                'description': 'Ending column (e.g., "Z"). If not provided, reads to last column with data.',
                'required': False
            },
            'include_headers': {
                'type': 'boolean',
                'description': 'Whether to treat first row as headers',
                'required': False,
                'default': False
            },
            'max_rows': {
                'type': 'integer',
                'description': 'Maximum number of rows to read (for large sheets)',
                'required': False,
                'default': 10000
            }
        }
    )
    async def read_sheet_data(self, **kwargs) -> str:
        """Read data from a sheet with optional range specification."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False,
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            sheet_name = kwargs.get('sheet_name', 'Sheet')
            start_row = kwargs.get('start_row', 1)
            end_row = kwargs.get('end_row')
            start_column = kwargs.get('start_column', 'A')
            end_column = kwargs.get('end_column')
            include_headers = kwargs.get('include_headers', False)
            max_rows = kwargs.get('max_rows', 10000)
            
            workbook = self.workbook_manager.get_workbook()
            
            # Read data using business logic
            result = self.excel_operations.read_sheet_data(
                workbook=workbook,
                sheet_name=sheet_name,
                start_row=start_row,
                end_row=end_row,
                start_column=start_column,
                end_column=end_column,
                include_headers=include_headers,
                max_rows=max_rows
            )
            
            if not result.success:
                return json.dumps(result.to_dict())
            
            # Check if response is too big for direct return
            response_data = {
                'data': result.data,
                'headers': result.headers
            }
            response_json = json.dumps(response_data)
            
            response_dict = result.to_dict()
            response_dict['sheet_name'] = sheet_name
            
            if self._is_response_too_big(response_json):
                # Cache the data and return cache key
                cache_key = f'excel_data_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}'
                self.tool_cache.set(cache_key, response_data, expire=3600)  # 1 hour
                
                response_dict.update({
                    'cached': True,
                    'cache_key': cache_key,
                    'message': 'Data cached due to size. Use cache key to access full dataset.'
                })
                
                # Remove data from response
                if 'data' in response_dict:
                    del response_dict['data']
                if 'headers' in response_dict:
                    del response_dict['headers']
                
                self.logger.info(f'Cached sheet data with key {cache_key}: {result.rows_read} rows')
            
            return json.dumps(response_dict)
            
        except Exception as e:
            error_msg = f'Error reading sheet data: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Load cached sheet data using a cache key',
        params={
            'cache_key': {
                'type': 'string',
                'description': 'Cache key returned by read_sheet_data when data was too large',
                'required': True
            }
        }
    )
    async def load_cached_data(self, **kwargs) -> str:
        """Load cached sheet data using a cache key."""
        try:
            # Validate required fields
            success, message = validate_required_fields(kwargs, ['cache_key'])
            if not success:
                return json.dumps({'success': False, 'error': message})
            
            cache_key = kwargs.get('cache_key')
            
            # Retrieve cached data
            cached_data = self.tool_cache.get(cache_key)
            
            if cached_data is None:
                return json.dumps({
                    'success': False,
                    'error': f'No cached data found for key {cache_key} (may have expired)'
                })
            
            return json.dumps({
                'success': True,
                'message': 'Cached data retrieved successfully',
                'cache_key': cache_key,
                **cached_data
            })
            
        except Exception as e:
            error_msg = f'Error loading cached data: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Get the next available row number in a sheet for coordination between agents',
        params={
            'sheet_name': {
                'type': 'string',
                'description': 'Name of the sheet to check',
                'required': False,
                'default': 'Sheet'
            }
        }
    )
    async def get_next_available_row(self, **kwargs) -> str:
        """Get the next available row number in a sheet."""
        try:
            if not self.workbook_manager.has_workbook():
                return json.dumps({
                    'success': False,
                    'error': 'No workbook is currently loaded. Create or load a workbook first.'
                })
            
            sheet_name = kwargs.get('sheet_name', 'Sheet')
            workbook = self.workbook_manager.get_workbook()
            
            # Account for active reservations
            reserved_rows = sum(
                res.row_count for res in self.concurrency_manager.get_active_reservations(sheet_name).values()
            )
            
            # Get next available row using business logic
            result = self.excel_operations.get_next_available_row_info(
                workbook=workbook,
                sheet_name=sheet_name,
                reserved_rows=reserved_rows
            )
            
            return json.dumps(result.to_dict())
            
        except Exception as e:
            error_msg = f'Error getting next available row: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})

    @json_schema(
        description='Get operation status and statistics for monitoring large operations',
        params={
            'operation_id': {
                'type': 'string',
                'description': 'Operation ID returned by write operations',
                'required': False
            }
        }
    )
    async def get_operation_status(self, **kwargs) -> str:
        """Get status and statistics for operations."""
        try:
            operation_id = kwargs.get('operation_id')
            
            # Get workbook info
            workbook_info = {
                'loaded': self.workbook_manager.has_workbook(),
                'path': self.workbook_manager.get_workbook_path(),
                'metadata': (self.workbook_manager.get_workbook_metadata().to_dict() 
                           if self.workbook_manager.get_workbook_metadata() else {})
            }
            
            if self.workbook_manager.has_workbook():
                workbook = self.workbook_manager.get_workbook()
                workbook_info['sheets'] = len(workbook.sheetnames)
            else:
                workbook_info['sheets'] = 0
            
            # Get concurrency status
            concurrency_status = self.concurrency_manager.get_operation_status()
            
            result = {
                'success': True,
                'current_workbook': workbook_info,
                **concurrency_status
            }
            
            return json.dumps(result)
            
        except Exception as e:
            error_msg = f'Error getting operation status: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'success': False, 'error': error_msg})


# Register the toolset
Toolset.register(ExcelTools, required_tools=['WorkspaceTools'])