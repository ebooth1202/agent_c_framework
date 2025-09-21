# Coordinator to Specialist Workflow Protocol

## Core Principle
**Each unit of work is equivalent to a Scrum card and is handled in a dedicated chat session with complete context.**

## Work Unit Sizing

### Definition: Scrum Card Equivalent
A work unit should be:
- **Completable in 1-3 days** by a specialist
- **Single focused objective** (not multiple unrelated tasks)  
- **Clear completion criteria** (definition of done)
- **Testable outcome** (can be validated by test specialist)

### ✅ **Good Work Unit Examples**
- "Implement audio mute button state persistence across browser refresh"
- "Add validation for new event type `conversation_turn_interrupted`"
- "Create responsive mobile layout for chat message components"
- "Fix memory leak in WebSocket reconnection manager"

### ❌ **Bad Work Unit Examples** (Too Large/Complex)
- "Improve the entire audio system" (too broad)
- "Implement new voice mode AND fix existing bugs" (multiple objectives)
- "Refactor authentication and add new features" (scope creep)

## Chat Session Protocol

### Rule: New Chat for Each Work Unit
**NEVER reuse chat sessions between different work units.**

**Rationale**:
- Prevents context pollution between different tasks
- Enables clean handoffs between coordinators and specialists
- Maintains clear audit trail for each work unit
- Allows specialists to focus on single objective without confusion

### Chat Session Initialization

#### Coordinator's Opening Message Template
```markdown
## Work Unit: [Clear, Specific Title]

### Original User Request
[Complete unfiltered user statement - see Reference Material Protocol]

### Work Unit Scope
**Objective**: [Single, clear objective]
**Package**: [Which package this affects]  
**Domain**: [Which domain within the package]
**Estimated Effort**: [1-3 days]

### Context & Requirements
[All relevant context the specialist needs to start work immediately]

### Reference Materials
- [Links to relevant documentation]
- [User-provided examples or specifications]
- [Related previous work or decisions]

### Definition of Done
- [ ] [Specific completion criterion 1]
- [ ] [Specific completion criterion 2]  
- [ ] [Specific completion criterion 3]
- [ ] Ready for test specialist handoff

### Success Criteria
[How will we know this work meets user requirements]

**Ready to begin? Please confirm you have everything needed to start this work unit.**
```

## Work Assignment Process

### Phase 1: Coordinator Preparation
1. **Break Down Feature/Request**
   - Decompose larger requests into Scrum card-sized work units
   - Each work unit gets its own chat session
   - Ensure each unit has clear completion criteria

2. **Context Package Preparation**
   - Gather ALL relevant context for the work unit
   - Include original user request (unfiltered)
   - Collect reference materials and documentation
   - Identify any cross-package dependencies

3. **Specialist Selection**
   - Choose appropriate dev specialist based on domain
   - Consider specialist current workload
   - Note any required coordination with other packages

### Phase 2: Work Unit Assignment
1. **Initiate New Chat Session**
   - Create new chat with selected specialist
   - Use coordinator opening message template
   - Ensure ALL context is provided upfront

2. **Specialist Confirmation**
   - Specialist reviews complete work unit context
   - Asks any clarifying questions
   - Confirms understanding and readiness to proceed
   - Estimates completion timeline

3. **Work Commencement**
   - Specialist begins implementation
   - Coordinator available for clarification/coordination
   - Regular progress check-ins as needed

### Phase 3: Work Unit Completion
1. **Completion Notification**
   ```markdown
   ## Work Unit Completion Summary
   
   **Objective**: [Restate original objective]
   **Status**: COMPLETE
   
   ### Work Completed
   - [Specific items implemented/fixed/changed]
   - [Files modified or created]
   - [Any design decisions made]
   
   ### Definition of Done Verification
   - [x] [Completion criterion 1] - [How verified]
   - [x] [Completion criterion 2] - [How verified]
   - [x] [Completion criterion 3] - [How verified]
   
   ### Handoff Package for Testing
   [See Dev-to-Test Handoff Protocol]
   
   **Ready for test specialist assignment.**
   ```

2. **Coordinator Review**
   - Review completion summary
   - Verify definition of done criteria met
   - Approve handoff to test specialist

## Cross-Package Coordination During Work Units

### When Work Unit Affects Multiple Packages
1. **Primary Package Assignment**
   - One coordinator "owns" the work unit
   - Other coordinators are "consulted" as needed

2. **Consultation Protocol**
   ```markdown
   ## Cross-Package Consultation Request
   
   **From**: [Requesting Coordinator]
   **To**: [Consulted Coordinator] 
   **Work Unit**: [Title and link to chat session]
   
   **Consultation Needed**:
   [Specific question or coordination need]
   
   **Context**: 
   [Brief context - full context available in work unit chat]
   
   **Timeline**: [When response needed]
   ```

3. **Coordination Response**
   - Consulted coordinator reviews work unit context
   - Provides specific guidance or raises concerns
   - May assign their own specialist for coordination

## Quality Control

### Work Unit Quality Checklist
- [ ] Work unit is appropriately sized (1-3 days)
- [ ] Single focused objective
- [ ] Clear completion criteria defined
- [ ] All context provided to specialist upfront
- [ ] Original user request included (unfiltered)
- [ ] New chat session created
- [ ] Cross-package dependencies identified

### Coordinator Effectiveness Metrics
- **Work Unit Sizing Accuracy**: How often work units complete within estimated timeframe
- **Context Completeness**: How often specialists need to ask for additional context
- **Handoff Quality**: How smoothly work units transition to testing phase
- **Rework Rate**: How often work units require significant changes after completion

## Anti-Patterns to Avoid

### ❌ **Chat Session Reuse**
```
BAD: Using same chat for multiple work units
RESULT: Context pollution, confusion, audit trail problems
```

### ❌ **Scope Creep During Work Unit**
```
BAD: "While you're working on the audio bug, can you also..."
RESULT: Work unit becomes too large, timeline increases, focus lost
```

### ❌ **Incomplete Context Handoff**
```
BAD: "Fix the authentication issue" (no user context, no specifics)
RESULT: Specialist wastes time investigating, may solve wrong problem
```

### ✅ **Proper Work Unit Management**
- New chat per work unit
- Complete context upfront
- Clear scope boundaries
- Single focused objective
- Clean completion and handoff

---

**Remember**: Clean work unit management enables specialists to be maximally effective by providing clear focus, complete context, and manageable scope. Quality coordination multiplies specialist effectiveness.