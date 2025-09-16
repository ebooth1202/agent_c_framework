# Mystery World Director Connectivity Investigation

## Problem Summary
The Mystery World Director (agent key: `mystery_world_director`) is trying to connect to the Shadow Pines Game Master (agent key: `shadow_pines_game_master`) but receiving the error:
> "There was an error trying to reach the shadow_pines_game_master agent. This means either the agent doesn't exist or there's a connectivity issue."

## Investigation Findings

### 1. Mystery World Director Configuration
**Location**: `//project/agent_c_config/agents/mystery_world_director.yaml`
**Status**: ✅ EXISTS and properly configured

The director references these game masters:
- `shadow_pines_game_master` - Shadow Pines Manor Victorian Gothic
- `space_station_game_master` - Kepler Space Station Sci-Fi  
- `victorian_game_master` - Victorian London Urban

### 2. Game Master Agent Files
**Status**: ✅ EXIST but are in the wrong location

Found the actual agent files at:
- `//project/mystery_world/stories/Shadow_Pines/Shadow_Pines_Game_Master.yaml`
  - Agent key: `shadow_pines_game_master` ✅ MATCHES director config
- `//project/mystery_world/stories/Space_Station/Space_Station_Game_Master.yaml`  
  - Agent key: `space_station_game_master` ✅ MATCHES director config
- `//project/mystery_world/stories/Victorian/Victorian_Game_Master.yaml`
  - Agent key: `victorian_game_master` ✅ MATCHES director config

### 3. Location Problem Identified
**Issue**: The game master agents are located in the mystery world project structure (`//project/mystery_world/stories/`) but the Agent C system expects agents to be in the main agents directory (`//project/agent_c_config/agents/`).

**Evidence**: 
- All other functional agents are in `//project/agent_c_config/agents/`
- There is a `mystery_world_test` subdirectory under agents with some mystery agents
- The main agents directory contains `Space_Station_Game_Master.yaml` which appears to be an earlier version

### 4. Agent Registration Issue
**Root Cause**: The game master agents exist but are not in the location where the Agent C system can find and register them.

## Solution Recommendations

### Option 1: Move Game Masters to Main Agents Directory
- Move all three game master YAML files from `mystery_world/stories/*/` to `agent_c_config/agents/`
- This puts them in the standard location where Agent C expects to find agents
- **Pros**: Simple, follows standard conventions
- **Cons**: Separates agents from their story context files

### Option 2: Use Symbolic Links  
- Create symbolic links in `agent_c_config/agents/` pointing to the game masters in their current locations
- This keeps agents with their story context while making them discoverable
- **Pros**: Maintains logical organization, agents stay with story files
- **Cons**: More complex, requires file system link support

### Option 3: Update Agent Registration System
- Modify Agent C to look for agents in additional directories
- **Pros**: Most flexible long-term solution
- **Cons**: Requires core system changes, more complex

## Recommended Action
**Option 1** (Move to main agents directory) is the most straightforward and immediate solution. The agent files are self-contained and don't appear to have hard dependencies on their current location within the story structure.

## Dependency Analysis

### Critical Discovery: Game Masters Need Story Data Access
After examining the Shadow Pines Game Master configuration and directory structure, I found that these agents DO need access to their story context files:

**Required Story Data Files:**
- `shadow_pines_manor.yaml` - Complete world definition with locations, characters, mystery rules
- `rooms/*.yaml` - Individual room definitions (study, hallway, garage, etc.)
- `objects/*.yaml` - Game objects (portraits, vehicles, keys, furniture)
- `game_sessions/` - Player session data and progress tracking
- `Shadow_Pines_Dialogue_Coordinator.yaml` - Specialized dialogue agent for Butler James
- `Shadow_Pines_Assistant.yaml` - Atmospheric enhancement agent

**The Challenge:**
The game masters reference files like `game_sessions/[player_id]/` for session state management and need access to the complete world definition files to properly orchestrate gameplay.

### Solution Options Reconsidered

#### Option 1: Move Game Masters + Create Workspace Configuration ✅ RECOMMENDED
- Move game master YAML files to `agent_c_config/agents/`
- Configure the "project" workspace to include the mystery_world story directories
- Game masters can then use WorkspaceToolset to access `//project/mystery_world/stories/Shadow_Pines/*` files
- **Pros**: Agents discoverable, story data accessible via workspace tools
- **Cons**: Requires workspace tool paths in agent usage

#### Option 2: Copy Everything to Agents Directory
- Copy all game master files AND their story data to `agent_c_config/agents/`  
- **Pros**: Everything in one place
- **Cons**: Duplicates a lot of data, breaks logical organization

#### Option 3: Symbolic Links ✅ ALSO VIABLE
- Create symbolic links in `agent_c_config/agents/` pointing to the game masters
- Story data stays in original location, agents can use relative paths
- **Pros**: No file duplication, maintains organization
- **Cons**: Relative path dependencies, requires symbolic link support

## Next Steps
1. **RECOMMENDED**: Move the three game master agent files to `//project/agent_c_config/agents/`
2. **Verify** the "project" workspace includes access to `mystery_world/stories/` directories
3. **Test** connectivity from Mystery World Director
4. **Test** that game masters can access their story data via workspace tools like `//project/mystery_world/stories/Shadow_Pines/shadow_pines_manor.yaml`
5. **Update** any hard-coded paths if needed