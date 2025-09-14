#!/usr/bin/env python3
"""
Run complete investigation of AgentConfigLoader issues.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_investigation():
    """Run the complete investigation."""
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("=" * 100)
    print("MYSTERY WORLD GAME MASTER CACHING INVESTIGATION")
    print("=" * 100)
    
    scripts = [
        ('.scratch/direct_investigation.py', 'Direct File System Investigation'),
        ('.scratch/test_imports.py', 'AgentConfigLoader Import and Usage Test')
    ]
    
    for script_path, description in scripts:
        print(f"\n{'=' * 50}")
        print(f"RUNNING: {description}")
        print(f"Script: {script_path}")
        print(f"{'=' * 50}")
        
        try:
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=project_root,
                                  timeout=60)
            
            print(result.stdout)
            
            if result.stderr:
                print("\nSTDERR:")
                print(result.stderr)
                
            if result.returncode != 0:
                print(f"\nScript exited with return code: {result.returncode}")
            else:
                print(f"\n✓ Script completed successfully")
                
        except subprocess.TimeoutExpired:
            print("✗ Script timed out after 60 seconds")
        except Exception as e:
            print(f"✗ Error running script: {e}")
    
    print(f"\n{'=' * 100}")
    print("INVESTIGATION COMPLETE")
    print(f"{'=' * 100}")

if __name__ == "__main__":
    run_investigation()