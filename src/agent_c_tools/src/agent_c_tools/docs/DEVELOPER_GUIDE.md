# Agent C Tools - Developer Guide

## Architecture Principles

This guide explains the **clean architecture approach** for Agent C tools that separates concerns and improves maintainability.

## Table of Contents

1. [Tool Class Architecture](#tool-class-architecture)
2. [Separation of Concerns](#separation-of-concerns)
3. [Best Practices](#best-practices)
4. [Code Examples](#code-examples)
5. [Common Patterns](#common-patterns)
6. [What to Avoid](#what-to-avoid)

---

## Tool Class Architecture

### **Core Principle: Tools Are Interfaces, Not Implementations**

Tool classes should be **thin interfaces** that collect kwargs and delegate to business logic elsewhere. They should **NOT** contain the actual implementation logic.

### **The Clean Architecture Pattern**

```
User Request → Tool Class → Business Logic Class → External APIs/Services
     ↓              ↓                ↓                    ↓
   kwargs      delegation      implementation        data/results
```

### **Tool Class Responsibilities** ✅

Tool classes should **ONLY**:

1. **Initialize** with required parameters
2. **Define JSON schema** for the tool interface
3. **Collect kwargs** from the tool call
4. **Delegate** to business logic functions/classes
5. **Return results** without modification

### **Tool Classes Should NOT** ❌

Tool classes should **almost NEVER**:

- Contain business logic or data processing
- Handle external API calls directly
- Format or transform data
- Contain complex error handling logic
- Have more than ~10 lines of code per function

---

## Separation of Concerns

### **Where Business Logic Lives**

Business logic should be implemented in:

1. **Extended existing classes** (preferred)
2. **Dedicated service functions** (when no suitable class exists)
3. **Utility modules** (for shared functionality)

### **Weather Tool Example** ✅

#### **GOOD: Clean Tool Interface**
```python
# tool.py - ONLY interface concerns
class WeatherTools(Toolset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='weather', use_prefix=False)

    @json_schema('Get weather forecast for a location', {...})
    async def get_current_weather(self, **kwargs) -> str:
        location_name = kwargs.get('location_name')
        
        # Simple delegation - NO business logic
        weather_client = Weather(locale='en', unit='imperial')
        return await weather_client.get_formatted_weather_data(location_name)
```

#### **GOOD: Business Logic in Extended Class**
```python
# util/client.py - Business logic where it belongs
class Weather:
    # ... existing methods ...
    
    async def get_formatted_weather_data(self, location: str) -> str:
        \"\"\"Business logic for formatting weather data for tool consumption.\"\"\"
        try:
            weather = await self.get_forecast(location)
            # ... data processing, formatting, error handling ...
            return yaml.dump(weather_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        except Exception as e:
            return f\"Error getting weather: {str(e)}\"
```

#### **BAD: Mixed Concerns** ❌
```python
# DON'T DO THIS - business logic mixed with tool interface
class WeatherTools(Toolset):
    async def get_current_weather(self, **kwargs) -> str:
        location_name = kwargs.get('location_name')
        
        # ❌ Business logic in tool class
        weather = await Weather(locale='en', unit='imperial').get_forecast(location_name)
        
        # ❌ Data processing in tool class
        forecasts = []
        for forecast in weather.daily_forecasts:
            forecasts.append({...})
        
        # ❌ Error handling and formatting in tool class
        try:
            results = json.dumps({...})
        except Exception as e:
            return f\"Error: {str(e)}\"
        
        return results
```

---

## Best Practices

### **1. Keep Tool Classes Minimal**

```python
class ExampleTools(Toolset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='example', use_prefix=False)
        # Only tool-specific initialization here
    
    @json_schema('Description of what the tool does', {...})
    async def tool_method(self, **kwargs) -> str:
        # Extract parameters
        param1 = kwargs.get('param1')
        param2 = kwargs.get('param2')
        
        # Delegate to business logic
        return await business_logic_function(param1, param2)
```

### **2. Extend Existing Classes When Possible**

**Preferred approach:**
```python
# Extend existing domain classes
class ExistingDomainClass:
    # ... existing methods ...
    
    def new_formatted_method_for_tool(self, params) -> str:
        \"\"\"New method for tool-friendly data format.\"\"\"
        # Business logic implementation
        pass
```

**Avoid creating unnecessary service classes:**
```python
# ❌ Don't create this unless really necessary
class ExampleService:
    def process_data(self, params):
        # This might be unnecessary abstraction
        pass
```

### **3. Use Descriptive Method Names**

```python
# ✅ Clear what the method returns
async def get_formatted_weather_data(self, location: str) -> str:
    pass

# ✅ Indicates this is for tool consumption  
async def get_user_bio_for_tool(self, user_id: str) -> str:
    pass

# ❌ Generic names don't indicate purpose
async def process(self, data):
    pass
```

### **4. Handle Errors at the Right Level**

```python
# ✅ Business logic handles errors and returns user-friendly messages
class BusinessLogicClass:
    async def get_data_for_tool(self, params) -> str:
        try:
            # Business logic implementation
            return json.dumps(result)
        except SpecificException as e:
            self.logger.error(f\"Specific error: {e}\")
            return f\"Error: {user_friendly_message}\"
        except Exception as e:
            self.logger.error(f\"Unexpected error: {e}\")
            return f\"Error: Something went wrong\"

# ✅ Tool just passes through the result
class ToolClass(Toolset):
    async def tool_method(self, **kwargs) -> str:
        return await business_logic.get_data_for_tool(kwargs.get('param'))
```

### **5. Use YAML dump for return to tool**

```python
yaml.dump(weather_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
```
---

## Code Examples

### **File Upload Tool Pattern**

```python
# tool.py
class FileUploadTools(Toolset):
    async def upload_file(self, **kwargs) -> str:
        file_path = kwargs.get('file_path')
        destination = kwargs.get('destination')
        
        # Delegate to file service
        file_service = FileService()
        return await file_service.upload_file_for_tool(file_path, destination)

# file_service.py
class FileService:
    async def upload_file_for_tool(self, file_path: str, destination: str) -> str:
        try:
            # Actual upload logic
            result = await self.upload(file_path, destination)
            return json.dumps({\"status\": \"success\", \"url\": result.url})
        except Exception as e:
            return f\"Error uploading file: {str(e)}\"
```

### **Database Query Tool Pattern**

```python
# tool.py  
class DatabaseTools(Toolset):
    async def query_data(self, **kwargs) -> str:
        query = kwargs.get('query')
        
        # Delegate to database client
        db_client = DatabaseClient()
        return await db_client.execute_query_for_tool(query)

# database_client.py (extend existing class)
class DatabaseClient:
    # ... existing methods ...
    
    async def execute_query_for_tool(self, query: str) -> str:
        try:
            results = await self.execute(query)
            return yaml.dump({"rows": results, "count": len(results)}, default_flow_style=False, sort_keys=False, allow_unicode=True)
        except Exception as e:
            return f\"Error executing query: {str(e)}\"
```

---

## Common Patterns

### **1. Parameter Extraction Pattern**

```python
async def tool_method(self, **kwargs) -> str:
    # Extract all needed parameters first
    param1 = kwargs.get('param1')
    param2 = kwargs.get('param2', 'default_value')
    param3 = kwargs.get('param3')
    
    # Single delegation call
    return await business_logic(param1, param2, param3)
```
- Recommend we always return yaml dump for tool consumption `yaml.dump({"rows": results, "count": len(results)}, default_flow_style=False, sort_keys=False, allow_unicode=True)`

### **2. Configuration Pattern**

```python
async def tool_method(self, **kwargs) -> str:
    param = kwargs.get('param')
    
    # Configuration can be in tool class
    client = BusinessLogicClass(config='tool_specific_config')
    return await client.process_for_tool(param)
```

### **3. Multiple Parameter Pattern**

```python
async def tool_method(self, **kwargs) -> str:
    # When you have many parameters, consider passing kwargs directly
    return await business_logic_function(**kwargs)

# Or extract only what's needed
async def tool_method(self, **kwargs) -> str:
    needed_params = {
        'param1': kwargs.get('param1'),
        'param2': kwargs.get('param2')
    }
    return await business_logic_function(**needed_params)
```

## Next Steps

1. **Read the [Testing Guide](TESTING_GUIDE.md)** - Learn how to test this architecture
2. **Read the [Migration Guide](MIGRATION_GUIDE.md)** - Learn how to refactor existing tools  
3. **Try the [Tool Debugger](TOOL_DEBUGGER_GUIDE.md)** - Learn manual debugging techniques
4. **Study the Weather Tool** - Perfect example of this architecture in action

This architecture ensures your tools are **clean, maintainable, and testable**! 🚀
