#!/usr/bin/env python3
"""
Simple validation script to check if the refactored Excel tool has any import or syntax issues.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all modules can be imported without errors."""
    print("🔍 Testing Excel Tool Import Validation...")
    
    # Get the tools directory
    tools_dir = Path(__file__).parent.parent / "src" / "agent_c_tools" / "tools" / "excel"
    
    print(f"📁 Testing files in: {tools_dir}")
    
    # Check that files exist
    expected_files = [
        "models.py",
        "tool.py", 
        "business_logic/__init__.py",
        "business_logic/workbook_manager.py",
        "business_logic/concurrency_manager.py", 
        "business_logic/excel_operations.py"
    ]
    
    missing_files = []
    for file_path in expected_files:
        full_path = tools_dir / file_path
        if not full_path.exists():
            missing_files.append(str(full_path))
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    # Test Python syntax by compiling each file
    syntax_errors = []
    for file_path in expected_files:
        if not file_path.endswith('.py'):
            continue
            
        full_path = tools_dir / file_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            compile(source, str(full_path), 'exec')
            print(f"✅ Syntax valid: {file_path}")
            
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"❌ Syntax error in {file_path}: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"❌ Error reading {file_path}: {e}")
    
    if syntax_errors:
        print(f"\n❌ Syntax errors found:")
        for error in syntax_errors:
            print(f"  - {error}")
        return False
    
    print("\n🎉 All files have valid Python syntax!")
    return True

def check_model_structures():
    """Check that model classes have proper structure."""
    print("\n🏗️  Checking Model Structures...")
    
    tools_dir = Path(__file__).parent.parent / "src" / "agent_c_tools" / "tools" / "excel"
    models_file = tools_dir / "models.py"
    
    try:
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for expected classes
        expected_classes = [
            "ReservationInfo", 
            "WorkbookMetadata", 
            "SheetInfo", 
            "OperationResult",
            "WriteResult",
            "ReadResult", 
            "SaveResult",
            "LoadResult"
        ]
        
        missing_classes = []
        for class_name in expected_classes:
            if f"class {class_name}" in content:
                print(f"✅ Found class: {class_name}")
            else:
                missing_classes.append(class_name)
                print(f"❌ Missing class: {class_name}")
        
        if missing_classes:
            print(f"\n❌ Missing model classes: {missing_classes}")
            return False
        
        # Check for to_dict methods
        to_dict_count = content.count("def to_dict(")
        print(f"✅ Found {to_dict_count} to_dict methods")
        
        print("✅ Model structures look good!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def check_business_logic_structure():
    """Check business logic classes."""
    print("\n⚙️  Checking Business Logic Structure...")
    
    tools_dir = Path(__file__).parent.parent / "src" / "agent_c_tools" / "tools" / "excel" / "business_logic"
    
    checks = [
        ("workbook_manager.py", "WorkbookManager"),
        ("concurrency_manager.py", "ConcurrencyManager"), 
        ("excel_operations.py", "ExcelOperations")
    ]
    
    for file_name, class_name in checks:
        file_path = tools_dir / file_name
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if f"class {class_name}" in content:
                print(f"✅ Found {class_name} in {file_name}")
            else:
                print(f"❌ Missing {class_name} in {file_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error reading {file_name}: {e}")
            return False
    
    print("✅ Business logic structure looks good!")
    return True

def check_tool_registration():
    """Check that tool registration is present."""
    print("\n📝 Checking Tool Registration...")
    
    tools_dir = Path(__file__).parent.parent / "src" / "agent_c_tools" / "tools" / "excel"
    tool_file = tools_dir / "tool.py"
    
    try:
        with open(tool_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Toolset.register(ExcelTools" in content:
            print("✅ Found tool registration")
            return True
        else:
            print("❌ Missing tool registration")
            return False
            
    except Exception as e:
        print(f"❌ Error checking tool registration: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🧪 Excel Tool Refactoring Validation\n")
    
    checks = [
        ("Import/Syntax", test_imports),
        ("Model Structures", check_model_structures),
        ("Business Logic", check_business_logic_structure), 
        ("Tool Registration", check_tool_registration)
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*50}")
        print(f"Running: {check_name}")
        print(f"{'='*50}")
        
        try:
            result = check_func()
            results.append((check_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results.append((check_name, False))
            all_passed = False
    
    # Summary
    print(f"\n{'='*50}")
    print("VALIDATION SUMMARY")
    print(f"{'='*50}")
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL" 
        print(f"{status} - {check_name}")
    
    if all_passed:
        print(f"\n🎉 All validation checks passed!")
        print("The refactored Excel tool appears to be structurally sound.")
    else:
        print(f"\n❌ Some validation checks failed.")
        print("The refactored Excel tool needs attention before use.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)