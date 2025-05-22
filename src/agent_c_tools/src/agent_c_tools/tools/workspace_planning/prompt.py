from typing import Any, Optional, cast

from agent_c.prompting.prompt_section import PromptSection, property_bag_item



class WorkspacePlanSection(PromptSection):

    def __init__(self, **data: Any):
        TEMPLATE = (
            "The Workspace Planning Tools (wsp) allow you to create and manage plans, tasks, and lessons learned using the metadata of a workspace.\n\n"
            
            "## Plan and Task Structure\n"
            "- Plans: A plan is a collection of tasks and lessons learned\n"
            "- Tasks: A task is a unit of work within a plan. Tasks can have subtasks for breaking down complex work\n"
            "- Lessons Learned: Insights or knowledge gained from working on tasks\n\n"
            
            "## Path Format\n"
            "- Use a UNC style path of `//[workspace]/[plan_id]` to reference plans\n"
            "- Example: `//project/my_plan` refers to a plan named 'my_plan' in the 'project' workspace\n\n"
            
            "## Core Features\n"
            "- Create and manage plans across workspaces\n"
            "- Create hierarchical tasks with parent-child relationships\n"
            "- Add context to tasks to capture important information\n"
            "- Track lessons learned from tasks for future reference\n"
            "- Set task priorities (low, medium, high)\n"
            "- Mark tasks as completed\n\n"
            
            "## Recommended Usage\n"
            "1. Create a plan for the current project\n"
            "2. Break down work into top-level tasks\n"
            "3. Further break down complex tasks into subtasks\n"
            "4. Add context to tasks as you work on them\n"
            "5. Record lessons learned as you complete tasks\n"
            "6. Use the plan to track progress and document the project journey\n"
        )
        super().__init__(template=TEMPLATE, required=True, name="Workspace Planning", render_section_header=True, **data)