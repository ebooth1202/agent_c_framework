""" Integration tests for S3Workspace. """

import uuid
import pytest
import aiobotocore
from aiobotocore.session import get_session
from agent_c_tools.tools.workspaces.s3_storage import S3StorageWorkspace


@pytest.mark.integration
class TestS3WorkspaceIntegration:
    """
    Integration tests for S3Workspace.
    
    IMPORTANT: These tests require:
    1. Valid AWS credentials configured
    2. A test S3 bucket that the user has write access to
    3. Pytest and pytest-asyncio installed
    """

    @pytest.fixture(scope="class")
    def bucket_name(self):
        """
        Generate a unique bucket name for testing.
        In a real scenario, you'd use a pre-existing test bucket.
        """
        return "test-bucket-agentc"

    @pytest.fixture(scope="class")
    def prefix(self):
        """
        Generate a unique prefix for test files.
        """
        return f"integration-test/{uuid.uuid4().hex[:8]}/"

    @pytest.fixture(scope="class")
    def workspace(self, bucket_name, prefix):
        """
        Create a workspace instance for integration testing.
        """

        workspace = S3StorageWorkspace(
            bucket_name=bucket_name,
            prefix=prefix,
            name="integration-test-workspace"
        )

        return workspace

    @pytest.mark.asyncio
    async def test_write_and_read_text(self, workspace):
        """
        Test writing and reading text files.
        """
        # Write a text file
        text_content = "Hello, S3 Workspace Integration Test!"
        file_path = "test_file.txt"

        await workspace.write(file_path, "write", text_content)

        # Read the file back
        read_content = await workspace.read(file_path)

        assert read_content == text_content, "Written and read content should match"

    @pytest.mark.asyncio
    async def test_write_and_read_bytes(self, workspace):
        """
        Test writing and reading binary files.
        """
        # Create some binary content
        binary_content = b"Binary test content with some \x00 null bytes"
        file_path = "test_binary_file.bin"

        await workspace.write_bytes(file_path, "write", binary_content)

        # Read bytes back
        read_bytes = await workspace.read_bytes_internal(file_path)

        assert read_bytes == binary_content, "Written and read binary content should match"

    @pytest.mark.asyncio
    async def test_append_content(self, workspace):
        """
        Test appending content to a file.
        """
        file_path = "append_test.txt"

        # First write
        await workspace.write(file_path, "write", "First line\n")

        # Append
        await workspace.write(file_path, "append", "Second line\n")

        # Read and verify
        content = await workspace.read(file_path)

        assert content == "First line\nSecond line\n", "Appended content should match"

    @pytest.mark.asyncio
    async def test_list_files(self, workspace):
        """
        Test listing files in a directory.
        """
        # Create multiple test files
        files_to_create = [
            "list_test/file1.txt",
            "list_test/file2.txt",
            "list_test/subdir/file3.txt"
        ]

        # Write some content to these files
        for file_path in files_to_create:
            await workspace.write(file_path, "write", f"Content for {file_path}")

        # List files in the directory
        listed_files = await workspace.ls("list_test")

        # Split the result and check
        listed_files_set = set(listed_files.split('\n'))
        expected_files_set = {"file1.txt", "file2.txt", "subdir/file3.txt"}

        assert listed_files_set == expected_files_set, "Listed files should match expected"

    @pytest.mark.asyncio
    async def test_path_exists(self, workspace):
        """
        Test checking file and directory existence.
        """
        # Create a test file
        await workspace.write("existence_test/file.txt", "write", "Test content")

        # Check file existence
        assert await workspace.path_exists("existence_test/file.txt") is True
        assert await workspace.path_exists("existence_test/nonexistent.txt") is False

        # Check directory existence
        assert await workspace.path_exists("existence_test/") is True
        assert await workspace.path_exists("nonexistent_dir/") is False

    @pytest.mark.asyncio
    async def test_read_non_existent_file(self, workspace):
        """
        Test reading a non-existent file raises the correct exception.
        """
        with pytest.raises(FileNotFoundError):
            await workspace.read("non_existent_file.txt")

    @pytest.mark.asyncio
    async def test_read_only_workspace(self, workspace):
        """
        Test that a read-only workspace prevents writes.
        """
        # Create a read-only workspace
        ro_workspace = S3StorageWorkspace(
            bucket_name=workspace.bucket_name,
            prefix=workspace.prefix,
            read_only=True
        )
        
        with pytest.raises(ValueError, match="Cannot write to read-only workspace"):
            await ro_workspace.write("test.txt", "write", "Test content")


# Optional: Cleanup fixture to delete test files and bucket
@pytest.fixture(scope="session")
async def cleanup_s3_resources(bucket_name, prefix):
    """
    Optional cleanup of S3 resources after tests.
    Note: This is a simple implementation and might need to be expanded 
    based on your specific requirements.
    """
    yield  # Run tests first

    # Perform cleanup after all tests in the class have run
    session = self.workspace.session
    async with session.create_client('s3') as client:
        # List and delete all objects with the prefix
        paginator = client.get_paginator('list_objects_v2')
        async for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                objects = [{'Key': obj['Key']} for obj in page['Contents']]
                await client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': objects}
                )

        # Optional: Delete the bucket if you created a unique one
        # Uncomment if you want to delete the entire bucket
        # await client.delete_bucket(Bucket=bucket_name)
