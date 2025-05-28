"""
Integration tests for the workspace planning tool using debug_tool.
These tests call the actual WorkspacePlanningTools interface that users interact with.
"""
import uuid

import pytest
import json
import asyncio
import sys
import os
import yaml
import re

# Add the tool_debugger directory to the path to import debug_tool
tool_debugger_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    'tool_debugger'
)
sys.path.insert(0, tool_debugger_path)

from ...tool_debugger.debug_tool import ToolDebugger

class MockChatSession:
    def __init__(self):
        self.session_id = "test_session_123"


class MockSessionManager:
    def __init__(self):
        self.chat_session = MockChatSession()


class TestWSPToolsIntegration:
    """Integration tests for WorkspacePlanningTools that test the complete user interface."""
    def setup_method(self):
        """Set up test fixtures before each test method - NO test data creation."""
        self.debugger = None
        self.test_workspace = "project"  # This workspace must already exist
        self.created_plans = []  # Track plans created by this test for cleanup
        self.current_test_plan_id = None
        self.current_test_plan_path = None
        # Initialize test_plan_path for tests that need it
        unique_id = str(uuid.uuid4())[:8]
        self.test_plan_id = f"test_plan_{unique_id}"
        self.test_plan_path = f"//{self.test_workspace}/{self.test_plan_id}"


    def teardown_method(self):
        """Clean up test data created by this specific test."""
        if self.debugger and self.created_plans:
            asyncio.run(self.cleanup_created_plans())


    async def cleanup_created_plans(self):
        """Clean up plans created during this test."""
        for plan_path in self.created_plans:
            try:
                # Get the plan to find all tasks
                get_results = await self.debugger.run_tool_test(
                    tool_name='wsp_get_plan',
                    tool_params={'plan_path': plan_path}
                )

                get_content = self.debugger.extract_content_from_results(get_results)
                if "not found" not in get_content:
                    # Get all tasks and delete root tasks (cascades to children)
                    structured_content = self.debugger.extract_structured_content(get_results, format_hint='yaml')
                    if structured_content and "plan" in structured_content:
                        tasks = structured_content["plan"].get("tasks", {})
                        root_tasks = [tid for tid, tdata in tasks.items() if not tdata.get("parent_id")]

                        for task_id in root_tasks:
                            await self.debugger.run_tool_test(
                                tool_name='wsp_delete_task',
                                tool_params={'plan_path': plan_path, 'task_id': task_id}
                            )

                # TODO: Add plan deletion method to tool if needed
                print(f"Cleaned up test plan: {plan_path}")

            except Exception as e:
                print(f"Cleanup warning for {plan_path}: {e}")


    def generate_unique_plan_id(self, test_name):
        """Generate a unique plan ID for this test."""
        unique_id = str(uuid.uuid4())[:8]
        return f"{test_name}_{unique_id}"


    async def create_test_plan(self, debugger, title, description="", test_name="test"):
        """Create a unique test plan and track it for cleanup."""
        plan_id = self.generate_unique_plan_id(test_name)
        plan_path = f"//{self.test_workspace}/{plan_id}"

        results = await debugger.run_tool_test(
            tool_name='wsp_create_plan',
            tool_params={
                'plan_path': plan_path,
                'title': title,
                'description': description
            }
        )

        # Track for cleanup
        self.created_plans.append(plan_path)
        self.current_test_plan_id = plan_id
        self.current_test_plan_path = plan_path

        return results, plan_path, plan_id


    async def setup_wsp_planning_tool(self):
        """Helper method to set up the workspace planning tool for testing."""
        self.debugger = ToolDebugger(init_local_workspaces=True)
        mock_session_manager = MockSessionManager()

        await self.debugger.setup_tool(
            tool_import_path='agent_c_tools.WorkspacePlanningTools',
            tool_opts={'session_manager': mock_session_manager}
        )
        return self.debugger

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_and_get_plan(self):
        """Test creating a plan and retrieving it through the actual tool interface."""
        debugger = await self.setup_wsp_planning_tool()

        # Create a new plan
        create_results, plan_path, plan_id = await self.create_test_plan(
            debugger,
            'Integration Test Plan',
            'A test plan for integration testing',
            'create_get'
        )

        # Validate plan creation
        create_content = debugger.extract_content_from_results(create_results)
        assert create_content is not None
        assert "created successfully" in create_content
        assert not create_content.startswith("Error:")

        # Retrieve the created plan
        get_results = await debugger.run_tool_test(
            tool_name='wsp_get_plan',
            tool_params={'plan_path': plan_path}
        )

        # Validate plan retrieval
        get_content = debugger.extract_content_from_results(get_results)
        assert get_content is not None
        assert not get_content.startswith("Error:")

        # Parse and validate YAML structure
        structured_content = debugger.extract_structured_content(get_results, format_hint='yaml')
        assert structured_content is not None
        assert "plan" in structured_content

        plan = structured_content["plan"]
        assert plan["title"] == "Integration Test Plan"
        assert plan["description"] == "A test plan for integration testing"
        assert "id" in plan
        assert "created_at" in plan
        assert "updated_at" in plan
        assert isinstance(plan["tasks"], dict)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_plans(self):
        """Test listing plans in a workspace."""
        debugger = await self.setup_wsp_planning_tool()

        # First create a plan to ensure we have something to list
        _, plan_path, plan_id = await self.create_test_plan(
            debugger,
            'Test Plan for Listing',
            'A test plan',
            'list_plans'
        )

        # List plans in the workspace
        results = await debugger.run_tool_test(
            tool_name='wsp_list_plans',
            tool_params={'workspace': self.test_workspace}
        )

        # Validate results
        content = debugger.extract_content_from_results(results)
        assert content is not None
        assert not content.startswith("Error:")

        structured_content = debugger.extract_structured_content(results, format_hint='yaml')
        assert structured_content is not None
        assert "plans" in structured_content
        assert isinstance(structured_content["plans"], list)

        # Check that our test plan is in the list
        plan_found = False
        for plan in structured_content["plans"]:
            if plan["id"] == plan_id:
                plan_found = True
                assert plan["title"] == "Test Plan for Listing"
                break
        assert plan_found, "Test plan not found in list"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_and_manage_tasks(self):
        """Test creating, updating, and retrieving tasks."""
        debugger = await self.setup_wsp_planning_tool()

        # Create a unique test plan
        _, plan_path, _ = await self.create_test_plan(
            debugger,
            'Task Test Plan',
            'Plan for testing tasks',
            'task_mgmt'
        )

        # Create a parent task
        parent_task_results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Parent Task',
                'description': 'A parent task for testing',
                'priority': 'high',
                'context': 'This is test context for the parent task',
                'sequence': 1
            }
        )

        # Validate parent task creation
        parent_content = debugger.extract_content_from_results(parent_task_results)
        assert "created successfully" in parent_content

        # Extract parent task ID from the response
        import re
        parent_id_match = re.search(r"ID '([^']+)'", parent_content)
        assert parent_id_match, "Could not extract parent task ID"
        parent_task_id = parent_id_match.group(1)

        # Create a child task
        child_task_results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Child Task',
                'description': 'A child task for testing',
                'priority': 'medium',
                'parent_id': parent_task_id,
                'sequence': 1
            }
        )

        # Validate child task creation
        child_content = debugger.extract_content_from_results(child_task_results)
        assert "created successfully" in child_content

        # Get the parent task to verify hierarchy
        get_task_results = await debugger.run_tool_test(
            tool_name='wsp_get_task',
            tool_params={
                'plan_path': plan_path,
                'task_id': parent_task_id
            }
        )

        # Validate task retrieval
        task_content = debugger.extract_structured_content(get_task_results, format_hint='yaml')
        assert task_content is not None
        assert "task" in task_content

        task = task_content["task"]
        assert task["title"] == "Parent Task"
        assert task["priority"] == "high"
        assert task["sequence"] == 1
        assert len(task["child_tasks"]) == 1  # Should have one child

        # Update the parent task
        update_results = await debugger.run_tool_test(
            tool_name='wsp_update_task',
            tool_params={
                'plan_path': plan_path,
                'task_id': parent_task_id,
                'completed': True,
                'priority': 'low'
            }
        )

        # Validate task update
        update_content = debugger.extract_content_from_results(update_results)
        assert "updated successfully" in update_content

        # Verify the update
        updated_task_results = await debugger.run_tool_test(
            tool_name='wsp_get_task',
            tool_params={
                'plan_path': plan_path,
                'task_id': parent_task_id
            }
        )

        updated_task_content = debugger.extract_structured_content(updated_task_results, format_hint='yaml')
        updated_task = updated_task_content["task"]
        assert updated_task["completed"] is True
        assert updated_task["priority"] == "low"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_tasks(self):
        """Test listing tasks in a plan."""
        debugger = await self.setup_wsp_planning_tool()

        # Create a plan and tasks
        _, plan_path, plan_id = await self.create_test_plan(
            debugger,
            'Task List Test Plan',
            '',
            'list_tasks'
        )

        # Create multiple root tasks
        for i in range(3):
            await debugger.run_tool_test(
                tool_name='wsp_create_task',
                tool_params={
                    'plan_path': plan_path,
                    'title': f'Root Task {i+1}',
                    'priority': ['high', 'medium', 'low'][i],
                    'sequence': i+1
                }
            )

        # List root tasks (no parent_id filter)
        results = await debugger.run_tool_test(
            tool_name='wsp_list_tasks',
            tool_params={'plan_path': plan_path}
        )

        # Validate results
        content = debugger.extract_structured_content(results, format_hint='yaml')
        assert content is not None
        assert "tasks" in content
        assert len(content["tasks"]) == 3

        # Verify tasks are sorted by sequence
        tasks = content["tasks"]
        for i, task in enumerate(tasks):
            assert task["title"] == f"Root Task {i+1}"
            assert task["sequence"] == i+1

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_lessons_learned(self):
        """Test adding and listing lessons learned."""
        debugger = await self.setup_wsp_planning_tool()

        # Create plan and task
        _, plan_path, plan_id = await self.create_test_plan(
            debugger,
            'Lessons Test Plan',
            '',
            'lessons'
        )

        # Create a task to associate with the lesson
        task_results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Learning Task'
            }
        )

        # Extract task ID
        task_content = debugger.extract_content_from_results(task_results)
        task_id_match = re.search(r"ID '([^']+)'", task_content)
        task_id = task_id_match.group(1)

        # Add a lesson learned
        lesson_results = await debugger.run_tool_test(
            tool_name='wsp_add_lesson_learned',
            tool_params={
                'plan_path': plan_path,
                'lesson': 'Always validate input parameters thoroughly',
                'learned_task_id': task_id
            }
        )

        # Validate lesson creation
        lesson_content = debugger.extract_structured_content(lesson_results, format_hint='yaml')
        assert lesson_content is not None
        assert "lesson" in lesson_content

        lesson = lesson_content["lesson"]
        assert lesson["lesson"] == "Always validate input parameters thoroughly"
        assert lesson["learned_task_id"] == task_id

        # List lessons learned
        list_results = await debugger.run_tool_test(
            tool_name='wsp_list_lessons_learned',
            tool_params={'plan_path': plan_path}
        )

        # Validate lesson listing
        list_content = debugger.extract_structured_content(list_results, format_hint='yaml')
        assert list_content is not None
        assert "lessons" in list_content
        assert len(list_content["lessons"]) == 1
        assert list_content["lessons"][0]["lesson"] == "Always validate input parameters thoroughly"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_task(self):
        """Test deleting tasks and their subtasks."""
        debugger = await self.setup_wsp_planning_tool()

        # Create plan
        _, plan_path, plan_id = await self.create_test_plan(
            debugger,
            'Delete Test Plan',
            '',
            'delete'
        )

        # Create parent task
        parent_results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Parent to Delete'
            }
        )

        parent_id_match = re.search(r"ID '([^']+)'", debugger.extract_content_from_results(parent_results))
        parent_id = parent_id_match.group(1)

        # Create child tasks
        for i in range(2):
            await debugger.run_tool_test(
                tool_name='wsp_create_task',
                tool_params={
                    'plan_path': plan_path,
                    'title': f'Child {i+1}',
                    'parent_id': parent_id
                }
            )

        # Delete the parent task (should delete children too)
        delete_results = await debugger.run_tool_test(
            tool_name='wsp_delete_task',
            tool_params={
                'plan_path': plan_path,
                'task_id': parent_id
            }
        )

        # Validate deletion
        delete_content = debugger.extract_content_from_results(delete_results)
        assert "3 task(s) deleted successfully" in delete_content  # Parent + 2 children

        # Verify task is gone
        get_results = await debugger.run_tool_test(
            tool_name='wsp_get_task',
            tool_params={
                'plan_path': plan_path,
                'task_id': parent_id
            }
        )

        get_content = debugger.extract_content_from_results(get_results)
        assert "not found" in get_content

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_export_plan_report(self):
        """Test exporting plan reports in both markdown and HTML formats."""
        debugger = await self.setup_wsp_planning_tool()

        # Create a comprehensive plan for export testing
        _, plan_path, plan_id = await self.create_test_plan(
            debugger,
            'Export Test Plan',
            'A comprehensive plan for testing export functionality',
            'export'
        )

        # Add some tasks
        task_results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Task for Export',
                'description': 'This task will be included in the export',
                'priority': 'high'
            }
        )

        # Extract task ID and add a lesson
        task_id_match = re.search(r"ID '([^']+)'", debugger.extract_content_from_results(task_results))
        task_id = task_id_match.group(1)

        await debugger.run_tool_test(
            tool_name='wsp_add_lesson_learned',
            tool_params={
                'plan_path': plan_path,
                'lesson': 'Export functionality works well',
                'learned_task_id': task_id
            }
        )

        # Test markdown export
        md_export_results = await debugger.run_tool_test(
            tool_name='wsp_export_plan_report',
            tool_params={
                'plan_path': plan_path
            }
        )

        md_content = debugger.extract_content_from_results(md_export_results)
        assert "exported successfully" in md_content
        assert ".md" in md_content

        # Test HTML export
        html_export_results = await debugger.run_tool_test(
            tool_name='wsp_export_plan_report',
            tool_params={
                'plan_path': plan_path,
                'format': 'html'
            }
        )

        html_content = debugger.extract_content_from_results(html_export_results)
        assert "exported successfully" in html_content
        assert ".html" in html_content

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_export_plan_report_html_format(self):
        """Test exporting plan reports specifically in HTML format."""
        debugger = await self.setup_wsp_planning_tool()

        # Create a plan with comprehensive content for HTML export testing
        _, plan_path, plan_id = await self.create_test_plan(
            debugger,
            'HTML Export Test Plan',
            'A plan specifically designed to test HTML export functionality with rich content',
            'html_export'
        )

        # Add multiple tasks with different priorities and contexts
        parent_task_results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Phase 1: Foundation',
                'description': 'Set up the foundation for the project',
                'priority': 'high',
                'context': 'This phase involves setting up the basic infrastructure and dependencies',
                'sequence': 1
            }
        )

        parent_id_match = re.search(r"ID '([^']+)'", debugger.extract_content_from_results(parent_task_results))
        parent_id = parent_id_match.group(1)

        # Add child task
        await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Setup Database',
                'description': 'Configure the database schema and connections',
                'priority': 'medium',
                'parent_id': parent_id,
                'context': 'Use PostgreSQL with proper indexing for performance'
            }
        )

        # Add another root task
        task2_results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': plan_path,
                'title': 'Phase 2: Implementation',
                'description': 'Implement the core features',
                'priority': 'medium',
                'sequence': 2
            }
        )

        task2_id_match = re.search(r"ID '([^']+)'", debugger.extract_content_from_results(task2_results))
        task2_id = task2_id_match.group(1)

        # Add lessons learned
        await debugger.run_tool_test(
            tool_name='wsp_add_lesson_learned',
            tool_params={
                'plan_path': plan_path,
                'lesson': 'HTML export provides better visualization than markdown for complex plans',
                'learned_task_id': parent_id
            }
        )

        await debugger.run_tool_test(
            tool_name='wsp_add_lesson_learned',
            tool_params={
                'plan_path': plan_path,
                'lesson': 'Interactive HTML reports are more user-friendly for stakeholders',
                'learned_task_id': task2_id
            }
        )

        # Export to HTML format
        html_export_results = await debugger.run_tool_test(
            tool_name='wsp_export_plan_report',
            tool_params={
                'plan_path': plan_path,
                'format': 'html',
                'output_path': f'//{self.test_workspace}/.scratch/test_html_export_{plan_id}.html'
            }
        )

        # Validate HTML export results
        html_content = debugger.extract_content_from_results(html_export_results)
        assert "exported successfully" in html_content
        assert ".html" in html_content
        assert "test_html_export_" in html_content

        # Verify the export mentions the correct output path
        assert f"test_html_export_{plan_id}.html" in html_content

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling with invalid inputs."""
        debugger = await self.setup_wsp_planning_tool()

        # Test getting non-existent plan
        results = await debugger.run_tool_test(
            tool_name='wsp_get_plan',
            tool_params={'plan_path': '//nonexistent/plan'}
        )

        content = debugger.extract_content_from_results(results)
        assert "No workspace found with the name: nonexistent" in content

        # Test creating task in non-existent plan
        results = await debugger.run_tool_test(
            tool_name='wsp_create_task',
            tool_params={
                'plan_path': '//nonexistent/plan',
                'title': 'Test Task'
            }
        )

        content = debugger.extract_content_from_results(results)
        assert "No workspace found with the name: nonexistent" in content

        # Test missing required parameters
        results = await debugger.run_tool_test(
            tool_name='wsp_create_plan',
            tool_params={'plan_path': self.test_plan_path}  # Missing title
        )

        content = debugger.extract_content_from_results(results)
        assert "Error:" in content


    @pytest.mark.asyncio
    async def test_tool_availability(self):
        """Test that all workspace planning tools are properly set up and available."""
        debugger = await self.setup_wsp_planning_tool()

        # Check that all expected tools are available
        expected_tools = [
            'wsp_create_plan', 'wsp_list_plans', 'wsp_get_plan',
            'wsp_create_task', 'wsp_update_task', 'wsp_get_task', 'wsp_list_tasks', 'wsp_delete_task',
            'wsp_add_lesson_learned', 'wsp_list_lessons_learned',
            'wsp_export_plan_report'
        ]

        available_tools = debugger.get_available_tool_names()

        for tool in expected_tools:
            assert tool in available_tools, f"Tool '{tool}' not available"

        # Print tool info for debugging
        debugger.print_tool_info()


# Optional: Test runner for just integration tests
if __name__ == "__main__":
    print("Running Workspace Planning Tools Integration Tests...")
    pytest.main([__file__, "-v", "-m", "integration"])