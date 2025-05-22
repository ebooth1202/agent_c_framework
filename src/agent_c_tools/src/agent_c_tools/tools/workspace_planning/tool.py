from typing import Any, Dict, List, Optional, Union, cast
from datetime import datetime
import json

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c_tools.tools.workspace_planning.prompt import WorkspacePlanSection
from agent_c_tools.tools.workspace_planning.models import PlanModel, TaskModel, LessonLearnedModel, PriorityType
from agent_c_tools.tools.workspace.tool import WorkspaceTools


class WorkspacePlanningTools(Toolset):
    """
    WorkspacePlanningTools provides methods for creating and tracking plans using the metadata of a workspace.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(name='wsp', **kwargs)
        self.section = WorkspacePlanSection()
        self.workspace_tool: Optional[WorkspaceTools] = None

    async def post_init(self):
        self.workspace_tool = cast(WorkspaceTools, self.tool_chest.available_tools.get('WorkspaceTools'))
    
    def _parse_plan_path(self, plan_path: str) -> tuple[str, str]:
        """Parse a plan path into workspace name and plan ID."""
        if not plan_path.startswith("//"):
            raise ValueError(f"Invalid plan path format: {plan_path}. Must start with //")
        
        parts = plan_path.split("/")
        if len(parts) < 3:
            raise ValueError(f"Invalid plan path format: {plan_path}. Format should be //workspace/plan_id")
        
        workspace_name = parts[2]
        plan_id = "/".join(parts[3:]) if len(parts) > 3 else "default"
        
        return workspace_name, plan_id
    
    async def _get_plans_meta(self, workspace_name: str) -> Dict[str, Any]:
        """Get the plans metadata dictionary for a workspace."""
        if not self.workspace_tool:
            raise RuntimeError("WorkspaceTools not available")
        
        plans_meta = await self.workspace_tool.read_meta_value(workspace=workspace_name, key="_plans")
        return plans_meta or {}
    
    async def _save_plans_meta(self, workspace_name: str, plans_meta: Dict[str, Any]) -> None:
        """Save the plans metadata dictionary for a workspace."""
        if not self.workspace_tool:
            raise RuntimeError("WorkspaceTools not available")
        
        await self.workspace_tool.write_meta_value(workspace=workspace_name, key="_plans", value=plans_meta)
    
    async def _get_plan(self, plan_path: str) -> Optional[PlanModel]:
        """Get a plan by its path."""
        workspace_name, plan_id = self._parse_plan_path(plan_path)
        plans_meta = await self._get_plans_meta(workspace_name)
        
        if plan_id not in plans_meta:
            return None
        
        # Convert the JSON dict back to a PlanModel
        try:
            return PlanModel.model_validate(plans_meta[plan_id])
        except Exception as e:
            self._log.error(f"Error deserializing plan: {e}")
            return None
    
    async def _save_plan(self, plan_path: str, plan: PlanModel) -> None:
        """Save a plan to its path."""
        workspace_name, plan_id = self._parse_plan_path(plan_path)
        plans_meta = await self._get_plans_meta(workspace_name)
        
        # Update the plan's updated_at timestamp
        plan.updated_at = datetime.now()
        
        # Convert the PlanModel to a dict for storage
        plans_meta[plan_id] = plan.model_dump()
        await self._save_plans_meta(workspace_name, plans_meta)
    
    @json_schema(
        description="Create a new plan in a workspace",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "title": {
                "type": "string",
                "description": "Title of the plan",
                "required": True
            },
            "description": {
                "type": "string",
                "description": "Description of the plan"
            }
        }
    )
    async def create_plan(self, plan_path: str, title: str, description: str = "") -> Dict[str, Any]:
        """Create a new plan in the specified workspace."""
        workspace_name, plan_id = self._parse_plan_path(plan_path)
        plans_meta = await self._get_plans_meta(workspace_name)
        
        if plan_id in plans_meta:
            return {"success": False, "error": f"Plan with ID '{plan_id}' already exists"}
        
        new_plan = PlanModel(title=title, description=description)
        await self._save_plan(plan_path, new_plan)
        
        return {
            "success": True,
            "plan": new_plan.model_dump()
        }
    
    @json_schema(
        description="List all plans in a workspace",
        params={
            "workspace": {
                "type": "string",
                "description": "Name of the workspace",
                "required": True
            }
        }
    )
    async def list_plans(self, workspace: str) -> Dict[str, Any]:
        """List all plans in the specified workspace."""
        plans_meta = await self._get_plans_meta(workspace)
        
        plans_list = []
        for plan_id, plan_data in plans_meta.items():
            plans_list.append({
                "id": plan_id,
                "title": plan_data.get("title", ""),
                "description": plan_data.get("description", ""),
                "created_at": plan_data.get("created_at", ""),
                "updated_at": plan_data.get("updated_at", "")
            })
        
        return {
            "success": True,
            "plans": plans_list
        }
    
    @json_schema(
        description="Get details of a plan",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            }
        }
    )
    async def get_plan(self, plan_path: str) -> Dict[str, Any]:
        """Get details of a plan."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        return {
            "success": True,
            "plan": plan.model_dump()
        }
    
    @json_schema(
        description="Create a new task in a plan",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "title": {
                "type": "string",
                "description": "Title of the task",
                "required": True
            },
            "description": {
                "type": "string",
                "description": "Description of the task"
            },
            "priority": {
                "type": "string",
                "description": "Priority of the task: low, medium, or high",
                "enum": ["low", "medium", "high"]
            },
            "parent_id": {
                "type": "string",
                "description": "ID of the parent task if this is a subtask"
            },
            "context": {
                "type": "string",
                "description": "Additional context for the task"
            }
        }
    )
    async def create_task(self, plan_path: str, title: str, description: str = "", 
                        priority: PriorityType = "medium", parent_id: Optional[str] = None,
                        context: str = "") -> Dict[str, Any]:
        """Create a new task in the specified plan."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        # Validate parent task if provided
        if parent_id and parent_id not in plan.tasks:
            return {"success": False, "error": f"Parent task with ID '{parent_id}' not found"}
        
        # Create the new task
        new_task = TaskModel(
            title=title,
            description=description,
            priority=priority,
            parent_id=parent_id,
            context=context
        )
        
        # Add to parent's child tasks if applicable
        if parent_id:
            parent_task = plan.tasks[parent_id]
            parent_task.child_tasks.append(new_task.id)
        
        # Add to plan's tasks
        plan.tasks[new_task.id] = new_task
        await self._save_plan(plan_path, plan)
        
        return {
            "success": True,
            "task": new_task.model_dump()
        }
    
    @json_schema(
        description="Update an existing task",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task to update",
                "required": True
            },
            "title": {
                "type": "string",
                "description": "New title for the task"
            },
            "description": {
                "type": "string",
                "description": "New description for the task"
            },
            "priority": {
                "type": "string",
                "description": "New priority for the task: low, medium, or high",
                "enum": ["low", "medium", "high"]
            },
            "completed": {
                "type": "boolean",
                "description": "Mark the task as completed"
            },
            "context": {
                "type": "string",
                "description": "New context for the task"
            }
        }
    )
    async def update_task(self, plan_path: str, task_id: str, title: Optional[str] = None,
                         description: Optional[str] = None, priority: Optional[PriorityType] = None,
                         completed: Optional[bool] = None, context: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing task in the specified plan."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        if task_id not in plan.tasks:
            return {"success": False, "error": f"Task with ID '{task_id}' not found in the plan"}
        
        task = plan.tasks[task_id]
        
        # Update task properties if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if completed is not None:
            task.completed = completed
        if context is not None:
            task.context = context
        
        # Update the task's updated_at timestamp
        task.updated_at = datetime.now()
        
        await self._save_plan(plan_path, plan)
        
        return {
            "success": True,
            "task": task.model_dump()
        }
    
    @json_schema(
        description="Get details of a task",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task to get",
                "required": True
            }
        }
    )
    async def get_task(self, plan_path: str, task_id: str) -> Dict[str, Any]:
        """Get details of a task."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        if task_id not in plan.tasks:
            return {"success": False, "error": f"Task with ID '{task_id}' not found in the plan"}
        
        task = plan.tasks[task_id]
        
        return {
            "success": True,
            "task": task.model_dump()
        }
    
    @json_schema(
        description="List tasks in a plan",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "parent_id": {
                "type": "string",
                "description": "ID of the parent task to list subtasks for. If not provided, lists root tasks."
            }
        }
    )
    async def list_tasks(self, plan_path: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """List tasks in a plan, optionally filtered by parent task."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        tasks_list = []
        
        for task_id, task in plan.tasks.items():
            # If parent_id is provided, filter by parent_id
            # If parent_id is None, get root tasks (tasks with no parent)
            if (parent_id and task.parent_id == parent_id) or (parent_id is None and not task.parent_id):
                tasks_list.append(task.model_dump())
        
        return {
            "success": True,
            "tasks": tasks_list
        }
    
    @json_schema(
        description="Add a lesson learned to a plan",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "lesson": {
                "type": "string",
                "description": "Lesson learned text",
                "required": True
            },
            "learned_task_id": {
                "type": "string",
                "description": "ID of the task associated with this lesson",
                "required": True
            }
        }
    )
    async def add_lesson_learned(self, plan_path: str, lesson: str, learned_task_id: str) -> Dict[str, Any]:
        """Add a lesson learned to a plan."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        if learned_task_id not in plan.tasks:
            return {"success": False, "error": f"Task with ID '{learned_task_id}' not found in the plan"}
        
        # Create the new lesson learned
        new_lesson = LessonLearnedModel(
            lesson=lesson,
            learned_task_id=learned_task_id
        )
        
        # Add to plan's lessons learned
        plan.lessons_learned.append(new_lesson)
        await self._save_plan(plan_path, plan)
        
        return {
            "success": True,
            "lesson": new_lesson.model_dump()
        }
    
    @json_schema(
        description="List lessons learned in a plan",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task to filter lessons by. If not provided, lists all lessons."
            }
        }
    )
    async def list_lessons_learned(self, plan_path: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """List lessons learned in a plan, optionally filtered by task."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        lessons_list = []
        
        for lesson in plan.lessons_learned:
            # If task_id is provided, filter by task_id
            if task_id is None or lesson.learned_task_id == task_id:
                lessons_list.append(lesson.model_dump())
        
        return {
            "success": True,
            "lessons": lessons_list
        }
    
    @json_schema(
        description="Delete a task and its subtasks",
        params={
            "plan_path": {
                "type": "string",
                "description": "Path to the plan in the format //workspace/plan_id",
                "required": True
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task to delete",
                "required": True
            }
        }
    )
    async def delete_task(self, plan_path: str, task_id: str) -> Dict[str, Any]:
        """Delete a task and all its subtasks from a plan."""
        plan = await self._get_plan(plan_path)
        
        if not plan:
            return {"success": False, "error": f"Plan not found at path: {plan_path}"}
        
        if task_id not in plan.tasks:
            return {"success": False, "error": f"Task with ID '{task_id}' not found in the plan"}
        
        # Get the task and its subtasks
        deleted_tasks = self._delete_task_recursive(plan, task_id)
        
        # If the task has a parent, remove it from the parent's child_tasks
        parent_id = plan.tasks.get(task_id).parent_id
        if parent_id and parent_id in plan.tasks:
            parent_task = plan.tasks[parent_id]
            if task_id in parent_task.child_tasks:
                parent_task.child_tasks.remove(task_id)
        
        await self._save_plan(plan_path, plan)
        
        return {
            "success": True,
            "deleted_tasks": deleted_tasks
        }
    
    def _delete_task_recursive(self, plan: PlanModel, task_id: str) -> List[str]:
        """Recursively delete a task and all its subtasks."""
        deleted_tasks = [task_id]
        
        # Get the task
        task = plan.tasks.get(task_id)
        if not task:
            return deleted_tasks
        
        # Recursively delete all child tasks
        for child_id in list(task.child_tasks):  # Make a copy to avoid modifying while iterating
            deleted_tasks.extend(self._delete_task_recursive(plan, child_id))
        
        # Remove the task from the plan
        del plan.tasks[task_id]
        
        return deleted_tasks


Toolset.register(WorkspacePlanningTools, required_tools=['WorkspaceTools'])