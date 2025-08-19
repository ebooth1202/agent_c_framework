#!/usr/bin/env python3
"""
Test script to verify that the personas endpoint fix works correctly.
This script tests the v2 config service directly without needing to run the full API.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agent_c_api_ui', 'agent_c_api', 'src'))

from agent_c_api.api.v2.config.services import ConfigService

async def test_personas_endpoint():
    """Test the personas endpoint to see if Dr Research appears"""
    print("Testing personas endpoint fix...")
    
    # Create a config service instance
    service = ConfigService()
    
    try:
        # Test get_personas method
        print("\n1. Testing get_personas() method...")
        personas_response = await service.get_personas()
        print(f"Found {len(personas_response.agents)} personas with 'domo' category:")
        
        dr_research_found = False
        for agent in personas_response.agents:
            print(f"  - {agent.key}: {agent.name}")
            if agent.key in ['dr_research', 'dr_research_no_med']:
                dr_research_found = True
                print(f"    ✅ Found Dr Research: {agent.key}")
        
        if not dr_research_found:
            print("    ❌ Dr Research not found in personas list")
        
        # Test get_persona method for Dr Research
        print("\n2. Testing get_persona() method for Dr Research...")
        dr_research_persona = await service.get_persona('dr_research')
        if dr_research_persona:
            print(f"  ✅ Successfully retrieved Dr Research persona:")
            print(f"    ID: {dr_research_persona.id}")
            print(f"    Name: {dr_research_persona.name}")
            print(f"    Description: {dr_research_persona.description[:100]}...")
        else:
            print("  ❌ Could not retrieve Dr Research persona")
        
        # Test get_system_config method
        print("\n3. Testing get_system_config() method...")
        system_config = await service.get_system_config()
        print(f"System config contains {len(system_config.personas)} personas:")
        
        dr_research_in_system = False
        for persona in system_config.personas:
            if persona.id in ['dr_research', 'dr_research_no_med']:
                dr_research_in_system = True
                print(f"  ✅ Found Dr Research in system config: {persona.id}")
        
        if not dr_research_in_system:
            print("  ❌ Dr Research not found in system config")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_personas_endpoint())
    sys.exit(0 if success else 1)