import json
import os
import re
import logging
import datetime
import pandas as pd

from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, cast

from agent_c.toolsets import json_schema, Toolset
from agent_c_tools.tools.dynamics.prompt import DynamicsCRMPrompt
from agent_c_tools.tools.dynamics.util.dynamics_api import DynamicsAPI, InvalidODataQueryError
from agent_c_tools.tools.workspace import WorkspaceTools
from agent_c_tools.tools.dynamics.util.dataframe_in_memory import create_excel_in_memory



class DynamicsTools(Toolset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='dynamics_crm', required_tools=['workspace'],
                         needed_keys=['DYNAMICS_ENDPOINT', 'DYNAMICS_CLIENT_ID', 'DYNAMICS_SCOPE',
                                      'REDIRECT_URI', 'TOKEN_ENDPOINT', 'CENTRIC_ID', 'CENTRIC_PW'])
        if not self.tool_valid:
            return

        # Various environment needsHel;
        self.base_url: str = kwargs.get('DYNAMICS_ENDPOINT', os.getenv('DYNAMICS_ENDPOINT'))
        self.client_id: str = kwargs.get('DYNAMICS_CLIENT_ID', os.getenv('DYNAMICS_CLIENT_ID'))
        self.dynamics_scope: str = kwargs.get('DYNAMICS_SCOPE', os.getenv('DYNAMICS_SCOPE'))
        self.redirect_uri: str = kwargs.get('REDIRECT_URI', os.getenv('REDIRECT_URI'))
        self.token_endpoint: str = kwargs.get('TOKEN_ENDPOINT', os.getenv('TOKEN_ENDPOINT'))
        self.access_token: str = kwargs.get('access_token', '')
        self.user_id: str = kwargs.get('CENTRIC_ID', os.getenv('CENTRIC_ID'))
        self.user_pw: str = kwargs.get('CENTRIC_PW', os.getenv('CENTRIC_PW'))
        # Workspace tool set up
        self.workspace_tool: WorkspaceTools = cast(WorkspaceTools, self.tool_chest.active_tools['workspace'])
        # Main Dynamics API object to work with
        self.dynamics_object = DynamicsAPI(base_url=self.base_url, client_id=self.client_id,
                                           dynamics_scope=self.dynamics_scope, redirect_uri=self.redirect_uri,
                                           token_endpoint=self.token_endpoint, access_token=self.access_token,
                                           user_id=self.user_id, user_pw=self.user_pw)
        # Special Tool prompt inclusion
        self.section = DynamicsCRMPrompt()

        # Constants for class
        self.ENTITY_CLEAN_FIELDS = {
            'annotations': ('notetext', 'html.parser'),
            'posts': ('text', 'xml'),
            'emails': ('description', 'html.parser'),
            'phonecalls': ('description', 'html.parser'),
            'appointments': ('description', 'html.parser')
        }
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def clean_html_xml(text, parser='html.parser'):
        soup = BeautifulSoup(text, parser)
        if parser == 'xml':
            return ''.join(soup.findAll(text=True))
        else:
            return soup.get_text()

    @json_schema(
        description="Get one or more entities from Dynamics CRM.  "
                    "Entities include 'accounts', 'leads', 'opportunities', 'contacts', 'annotations', 'appointments', "
                    "'tasks', 'emails', 'posts', 'phonecalls'.\n"
                    "This enables you to retrieve data and analyze it from an CRM system.  All query_params must be "
                    "Dynamics compatible odata queries or they will not work.  There are custom entities in this instance:\n"
                    "cen_serviceofferingcapabilitieses are service offering names like Data & Analytics, Modern Software Delivery, "
                    "cen_industryverticalsubs are sub-categories of service offerings Software Quality Assurance and Testing, Agile, "
                    "businessunits are geographic city office locations like Boston, Columbus, Chicago,  "
                    "cen_industryverticals are industry verticals like Healthcare, Financial Services, Retail.",
        params={
            'entity_type': {
                'type': 'string',
                'description': 'The type of Dynamics entity to retrieve.  Common values are "accounts", "leads", "opportunities',
                'enum': ['accounts', 'leads', 'opportunities', 'contacts', 'annotations', 'appointments', 'tasks',
                         'emails', 'posts', 'phonecalls', 'cen_serviceofferingcapabilitieses', 'businessunits', 'cen_industryverticalsubs', 'cen_industryverticals'],
                'required': True,
                'default': 'opportunities'
            },
            'entity_id': {
                'type': 'string',
                'description': 'The unique ID assigned by Dynamics to the entity record',
                'required': False
            },
            'query_params': {
                'type': 'string',
                'description': 'Dynamics compatible query to filter the entity list.  Include $filter= when your query is a filter.',
                'required': False,
            },
            'limit': {
                'type': 'integer',
                'description': 'The maximum number of entities to return',
                'required': False,
            },
            'workspace_name': {
                'type': 'string',
                'description': 'Workspace name to use for saving files',
                'required': False,
                'default': 'project'
            },
            'force_save': {
                'type': 'boolean',
                'description': 'If user specifically requests the data be saved to a file',
                'required': False,
                'default': False
            },
        },

    )
    async def get_entities(self, **kwargs):
        entity_id = kwargs.get('entity_id', None)
        workspace_name = kwargs.get('workspace_name', 'project')
        query_params = kwargs.get('query_params', '')
        limit = kwargs.get('limit', 0)
        entity_type = kwargs.get('entity_type', 'opportunities')
        statecode_filter = "statecode eq 0"  # we only want active entities
        force_save = kwargs.get('force_save', False)
        _OVERSIZE_ENTITY_CAP = 5

        # get core lookups
        if self.dynamics_object.common_lookups is None:
            await self.dynamics_object.one_time_lookups()

        if query_params:
            # I don't love this, but we have a ton of closed accounts that nearly mirrors our open accounts in our CRM
            if "$filter" in query_params and ("accounts" in query_params):
                # Regex for checking if statecode is already in the filter.
                # Statecode determines if record is active or not
                filter_part = re.search(r'\$filter=([^&]*)', query_params)

                if filter_part:
                    filter_content = filter_part.group(1)
                    if 'statecode' not in filter_content:
                        # Add statecode filter if it's not already there
                        new_filter = f"({statecode_filter}) and ({filter_content})"
                        query_params = query_params.replace(filter_part.group(0), f"$filter={new_filter}")
                else:
                    # if no query params were passed, at least only pull the active entities
                    query_params += f"&$filter={statecode_filter}"

        if "$top" not in query_params and limit > 0:
            query_params += f"&$top={limit}"

        try:
            if entity_id:
                entities = await self.dynamics_object.get_entities(entity_type=entity_type, entity_id=entity_id)
            else:
                entities = await self.dynamics_object.get_entities(entity_type=entity_type, query_params=query_params)
        except InvalidODataQueryError as e:
            return json.dumps({"error": f"Invalid OData query: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Error fetching entities: {str(e)}"})

        # this is to clean fields like notes, annotations that contain either html or xml, reduce token consumption
        if entities is not None and entity_type in self.ENTITY_CLEAN_FIELDS:
            field, parser = self.ENTITY_CLEAN_FIELDS[entity_type]
            for entity in entities:
                if field in entity:
                    entity[field] = self.clean_html_xml(entity[field], parser)

        # deal with overly large datasets.
        response_size = self.tool_chest.agent.count_tokens(json.dumps(entities))
        if response_size > 25000 or len(entities) > _OVERSIZE_ENTITY_CAP or force_save:
            # Response is too large, user requested save, or the response is too many records to deal with save it.
            self.logger.info(f"User requested local save: ({force_save})")
            self.logger.info(f"Dataset token size: ({response_size})")
            self.logger.info(f"Number of records: ({len(entities)})")

            workspace_obj = self.workspace_tool.find_workspace_by_name(workspace_name)
            if workspace_obj is None:
                return f"Error loading workspace {self.workspace_tool.name}"

            # Create unique file name based on date/time
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f'{entity_type}_{timestamp}.xlsx'

            # to use workspace toolsets, I need to write to memory and pass in the bytes to the write tool.
            try:
                # if the entities are not a list of dictionaries, this will fail, usually because dynamics returns
                # an error message, but a 200 status code like query has unbalanced brackets
                excel_buffer = create_excel_in_memory(pd.DataFrame(entities))
            except Exception as e:
                return json.dumps({"error": f"Error creating excel buffer bytes: {str(e)}\n\n{entities}"})
            result = await workspace_obj.write_bytes(file_path=file_name, mode='write', data=excel_buffer.getvalue())
            self.logger.debug(result)
            self.logger.info(f'Saved data to workspace: {workspace_obj.name} with file name: {file_name}')

            if entity_id is None:
                if len(entities) > _OVERSIZE_ENTITY_CAP:
                    entity_data = entities[_OVERSIZE_ENTITY_CAP]
                else:
                    entity_data = entities
            else:
                entity_data = entities[0]

            return json.dumps({
                'user_message': f"Display this message to the user.  The response was saved to a file {file_name}. Here are the first {_OVERSIZE_ENTITY_CAP} of "
                                f"{len(entities)} entities.  The dataset size {response_size} tokens. The query_params used was: {query_params}"
                                f"{'The $top query_param limited records' if '$top' in query_params else ''}",
                'file_name': file_name,
                'workspace_name': workspace_obj.name,
                'entity_data': entity_data,
                'entity_count': len(entities)
            })
        else:
            return json.dumps(entities)

    @json_schema(
        description="Force re-logging into Dynamics at user request only.",
        params={}
    )
    async def force_login(self):
        """force re-login on dynamics"""
        try:
            self.dynamics_object.access_token = None
            await self.dynamics_object.authorize_dynamics()
        except Exception as e:
            self.logger.error(f"Error fetching WhoAmI data: {str(e)}")
            raise e

    @json_schema(
        description="Get the Dynamics ID for the user making the request.",
        params={}
    )
    async def dynamics_user_id(self):
        """Get the whoami Dyanmics ID, if not available, re-authorize"""
        if self.dynamics_object.whoami_id is None:
            await self.dynamics_object.authorize_dynamics()

        if self.dynamics_object.common_lookups is None:
            await self.dynamics_object.one_time_lookups()

        return json.dumps({'whoami_id': f'{self.dynamics_object.whoami_id}'})

    @json_schema(
        description="Create a new entity in Dynamics CRM",
        params={
            'entity_type': {
                'type': 'string',
                'description': 'The type of entity to create (e.g., "accounts", "contacts")',
                'required': True
            },
            'entity_data': {
                'type': 'object',
                'description': 'A dictionary containing the data for the new entity',
                'required': True,
                'enum': ['annotations', 'appointments', 'tasks', 'phonecalls'],  # Limiting for now
                'default': 'tasks'
            }
        }
    )
    async def create_entity(self, **kwargs):
        entity_type = kwargs.get('entity_type', None)
        entity_data = kwargs.get('entity_data', None)
        if entity_data is None or entity_type is None:
            return json.dumps({"error": "Missing required parameters: entity_type, entity_data"})

        if entity_type not in ['annotations', 'appointments', 'tasks', 'phonecalls']:
            return json.dumps({"error": "Only allowing select entities to be created. "
                                        "Must be one of: 'annotations', 'appointments', 'tasks', 'phonecalls'"})

        new_entity = await self.dynamics_object.create_entity(entity_type, entity_data)

        if new_entity:
            return json.dumps(new_entity)
        else:
            return json.dumps({"error": "Failed to create entity"})


Toolset.register(DynamicsTools)
