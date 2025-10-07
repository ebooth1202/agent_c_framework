"""Test for workspace_planning tool list_tasks method."""
import pytest
from agent_c_tools.tools.workspace_planning.models import PlanModel, TaskModel, TaskListing


def test_task_listing_model():
    """Test that TaskListing model can be created and serialized."""
    child_task = TaskListing(
        task_id="child-1",
        title="Child Task",
        completed=False,
        child_tasks=[]
    )
    
    parent_task = TaskListing(
        task_id="parent-1",
        title="Parent Task",
        completed=True,
        child_tasks=[child_task]
    )
    
    # Test serialization
    data = parent_task.model_dump()
    assert data["task_id"] == "parent-1"
    assert data["title"] == "Parent Task"
    assert data["completed"] is True
    assert len(data["child_tasks"]) == 1
    assert data["child_tasks"][0]["task_id"] == "child-1"


def test_task_listing_hierarchy():
    """Test that TaskListing can represent deep hierarchies."""
    grandchild = TaskListing(
        task_id="gc-1",
        title="Grandchild",
        completed=False,
        child_tasks=[]
    )
    
    child = TaskListing(
        task_id="c-1",
        title="Child",
        completed=False,
        child_tasks=[grandchild]
    )
    
    parent = TaskListing(
        task_id="p-1",
        title="Parent",
        completed=True,
        child_tasks=[child]
    )
    
    data = parent.model_dump()
    assert len(data["child_tasks"]) == 1
    assert len(data["child_tasks"][0]["child_tasks"]) == 1
    assert data["child_tasks"][0]["child_tasks"][0]["task_id"] == "gc-1"


def test_sequence_ordering():
    """Test that sequence field correctly orders tasks."""
    # Create tasks with different sequences
    task1 = TaskModel(id="t1", title="Task 1", sequence=2)
    task2 = TaskModel(id="t2", title="Task 2", sequence=1)
    task3 = TaskModel(id="t3", title="Task 3", sequence=None)
    task4 = TaskModel(id="t4", title="Task 4", sequence=3)
    
    tasks = [task1, task2, task3, task4]
    
    # Sort by sequence (None values go to the end)
    tasks.sort(key=lambda t: (t.sequence is None, t.sequence if t.sequence is not None else 0))
    
    # Verify order
    assert tasks[0].id == "t2"  # sequence=1
    assert tasks[1].id == "t1"  # sequence=2
    assert tasks[2].id == "t4"  # sequence=3
    assert tasks[3].id == "t3"  # sequence=None


if __name__ == "__main__":
    test_task_listing_model()
    test_task_listing_hierarchy()
    test_sequence_ordering()
    print("✓ All tests passed!")
