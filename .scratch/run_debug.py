#!/usr/bin/env python3
"""
Simple runner for the debug script.
"""
import os
import sys
import subprocess

# Change to project directory
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_dir)

# Run the debug script
debug_script = os.path.join(project_dir, '.scratch', 'debug_agent_config_loader.py')
print(f"Running debug script from: {project_dir}")
print(f"Debug script path: {debug_script}")

try:
    result = subprocess.run([sys.executable, debug_script], 
                          capture_output=True, text=True, cwd=project_dir)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
        
    print(f"Return code: {result.returncode}")
    
except Exception as e:
    print(f"Error running script: {e}")