import os
import subprocess

# Define the source directory
SRC_DIR = 'src'
# SRC_DIR = '../src' # if running locally

# Initialize a list to collect all package paths and PYTHONPATH directories
package_paths = []
pythonpath_dirs = []

# Iterate over each module in the src directory
for module_name in os.listdir(SRC_DIR):
    # Skip the agent_c_realtime module
    if module_name == 'agent_c_realtime':
        # this is causing generate docs to error out
        print(f"Skipping module {module_name}")
        continue

    module_path = os.path.join(SRC_DIR, module_name)
    if os.path.isdir(module_path):
        print(f"Found module {module_name}")
        # Define the path to the package (assuming it's in src/<module>/src/<package>)
        package_src_path = os.path.join(module_path, 'src')
        package_name = module_name.replace('-', '_')
        package_path = os.path.join(package_src_path, package_name)
        # Check if the package path exists
        if os.path.exists(package_path):
            package_paths.append(package_path)
            pythonpath_dirs.append(os.path.abspath(package_src_path))
        else:
            print(f"Package path {package_path} does not exist")

# Define the docs directory
docs_path = 'docs/generated'
# Create the docs directory if it doesn't exist
os.makedirs(docs_path, exist_ok=True)

# Set the PYTHONPATH to include the source directories
env = os.environ.copy()
existing_pythonpath = env.get('PYTHONPATH', '')
env['PYTHONPATH'] = os.pathsep.join(pythonpath_dirs + [existing_pythonpath])

# Generate the documentation for all packages at once
subprocess.run([
    'pdoc',
    '--output-dir', docs_path,
    *package_paths
], env=env)
