# Shadow Pines Manor Cloning Request

## Target World File
`//project/mystery_worlds/shadow_pines_manor.yaml`

## Agent Team Architecture

### Coordinator Agent: `victorian_mystery_coordinator`
**Base Template:** Game Master / Orchestrator pattern
**Category:** ["domo"] (UI available)
**Tools Required:** 
- WorkspaceTools
- AgentTeamTools
- WorkspacePlanning

**Core Responsibilities:**
- Parse player input and determine delegation target
- Maintain master game state in workspace planning tool
- Coordinate responses from specialist clones
- Handle narrative flow and atmospheric continuity
- Provide fallback processing when clones unavailable

### Clone Agent 1: `world_navigator_clone`
**Base Template:** Exploration/Location specialist
**Category:** ["victorian_mystery_coordinator"] (team member)
**Domain:** Location management and movement
**Context Window:** Medium (world structure + current location)

**Specialized Instructions:**
- Process location-based commands (go, enter, leave, look around)
- Generate atmospheric location descriptions using world data
- Validate movement requests against connection rules
- Track and enforce access requirements
- Maintain immersion through consistent environmental storytelling

**Expected Token Usage:** 800-1,500 per invocation

### Clone Agent 2: `mystery_logic_clone`
**Base Template:** Puzzle/Logic specialist  
**Category:** ["victorian_mystery_coordinator"] (team member)
**Domain:** Clue discovery and mystery progression
**Context Window:** Large (full mystery state required)

**Specialized Instructions:**
- Evaluate clue discovery conditions against player actions
- Track mystery progression through multi-stage gates
- Distinguish between valid clues and red herrings
- Calculate victory condition fulfillment
- Generate contextual hints based on player struggle detection
- Maintain logical consistency in mystery revelation

**Expected Token Usage:** 1,200-2,500 per invocation

### Clone Agent 3: `interactive_object_clone`
**Base Template:** Object interaction specialist
**Category:** ["victorian_mystery_coordinator"] (team member)  
**Domain:** Object examination and manipulation
**Context Window:** Small (current location + object states)

**Specialized Instructions:**
- Process examine, take, use, search commands for objects
- Generate detailed object descriptions with discovery potential
- Track object state changes and availability
- Handle hidden item revelation mechanics
- Provide object-specific interaction feedback

**Expected Token Usage:** 600-1,200 per invocation

### Clone Agent 4: `vehicle_systems_clone`
**Base Template:** Mechanical systems specialist
**Category:** ["victorian_mystery_coordinator"] (team member)
**Domain:** Vehicle and fuel management  
**Context Window:** Small (vehicle states only)

**Specialized Instructions:**
- Track ATV and dirtbike fuel levels and condition
- Handle vehicle start attempts and failure conditions
- Manage fuel transfer operations from gas can
- Validate vehicle-based location access requirements
- Provide mechanical feedback and realistic system responses

**Expected Token Usage:** 400-800 per invocation (highest efficiency)

### Clone Agent 5: `character_dialogue_clone`
**Base Template:** NPC interaction specialist
**Category:** ["victorian_mystery_coordinator"] (team member)
**Domain:** Butler James personality and dialogue
**Context Window:** Medium (character state + player progress)

**Specialized Instructions:**
- Generate Butler James dialogue consistent with personality traits
- Reveal information based on player discovery progress  
- Maintain character secrets and knowledge boundaries
- Handle character-specific hint delivery
- Preserve Victorian-era speech patterns and manor atmosphere

**Expected Token Usage:** 1,000-2,000 per invocation

## Implementation Requirements

### State Management Schema
```yaml
game_state:
  player_location: "location_id"
  discovered_objects: ["object_id_list"] 
  found_clues: ["clue_id_list"]
  vehicle_states:
    red_atv: {fuel: "empty", condition: "excellent"}
    black_dirtbike: {fuel: "empty", condition: "excellent"}
  inventory: ["item_id_list"]
  character_interactions: ["interaction_id_list"]
  mystery_progress: "stage_identifier"
```

### Delegation Logic
1. **Movement commands** (`go`, `enter`, `move`, `travel`) → World Navigator Clone
2. **Object commands** (`examine`, `look at`, `take`, `use`, `search`) → Interactive Object Clone  
3. **Vehicle commands** (`start`, `fuel`, `ride`, `drive`) → Vehicle Systems Clone
4. **Character commands** (`talk to`, `ask`, `speak with`) → Character Dialogue Clone
5. **Mystery analysis** (progress checks, hint triggers) → Mystery Logic Clone
6. **Ambiguous/complex** → Coordinator handles directly

### Recovery Patterns
- **Clone timeout:** Coordinator processes request with reduced specialization
- **State corruption:** Reload from last planning tool checkpoint
- **Invalid delegation:** Route to most applicable available clone
- **Context overflow:** Compress state data and retry with essential information only

## Testing Protocol

### Smoke Tests
1. **Basic Navigation:** Player moves through all locations successfully
2. **Object Discovery:** Player finds all hidden items and keys  
3. **Vehicle Operations:** Player successfully refuels and uses vehicles
4. **Character Interaction:** Player has meaningful dialogue with Butler James
5. **Mystery Completion:** Player achieves victory conditions

### Load Tests  
1. **Rapid Input:** High-frequency player commands testing delegation speed
2. **Context Stress:** Complex multi-domain actions testing state management
3. **Error Recovery:** Deliberate clone failures testing fallback systems

### Efficiency Measurement
- Track total tokens per game session completion
- Compare against single-agent baseline performance
- Measure response time and player satisfaction correlation

## Expected Outcomes

**Token Efficiency Gain:** 8-17% vs monolithic agent
**Response Quality:** Improved through domain specialization  
**Maintainability:** Enhanced through separation of concerns
**Scalability:** Better handling of complex multi-domain interactions

**Risk Mitigation:** Robust fallback ensures degraded but functional experience even with clone failures.