# Cross-Package Coordination Protocol

## Core Principle
**When work spans multiple packages or domains, coordination must be explicit, documented, and involve the appropriate coordinators.**

## Package Hierarchy & Dependencies

### Dependency Flow
```
External Applications
         ↓
    Demo Package (integration showcase)
         ↓
UI Components Package (React components)
         ↓
    React Package (React hooks)  
         ↓
    Core Package (foundational WebSocket/Audio)
```

### Coordination Rules by Dependency
- **Upstream Changes**: Packages can break downstream dependents, require careful coordination
- **Downstream Changes**: Usually don't affect upstream packages, but should validate assumptions
- **Peer Changes**: Demo and UI Components are peers, may need coordination for consistency

## Cross-Package Coordination Triggers

### When Cross-Package Coordination is Required

#### 🚨 **Mandatory Coordination Scenarios**
1. **Breaking API Changes**: Any change that affects public interfaces between packages
2. **New Package Dependencies**: When one package needs new capabilities from another
3. **Shared Component Changes**: Changes to components used by multiple packages  
4. **Cross-Package Features**: Features that require implementation across multiple packages
5. **Performance Changes**: Changes that could affect performance in dependent packages

#### 💡 **Recommended Coordination Scenarios**
1. **Major Refactoring**: Significant internal changes that might affect integration patterns
2. **Error Handling Changes**: Changes to error flows that cross package boundaries
3. **Testing Strategy Changes**: Changes that affect how other packages mock or test integration
4. **Documentation Updates**: Changes that affect how other packages document integration

## Coordination Initiation Protocol

### Phase 1: Cross-Package Impact Assessment
When any coordinator identifies potential cross-package impact:

```markdown
## Cross-Package Impact Assessment

**Initiating Package**: [Core/React/UI-Components/Demo]
**Work Unit**: [Title and link to work unit]  
**Coordinator**: [Name]

### Change Summary
**Type**: [Breaking Change / New Feature / Enhancement / Bug Fix]
**Scope**: [Brief description of what's changing]

### Package Impact Analysis
**Affected Packages**: [List all packages that might be affected]

For each affected package:
- **Impact Level**: [High / Medium / Low]
- **Impact Type**: [API Change / Behavior Change / Performance / Testing]
- **Specific Impact**: [What specifically will be affected]
- **Coordination Needed**: [What type of coordination is required]

### Timeline
**Implementation Timeline**: [When changes will be made]
**Coordination Deadline**: [When coordination must be complete]
```

### Phase 2: Coordinator Consultation  
1. **Send Impact Assessment** to all affected package coordinators
2. **24-hour Response Window** for coordinators to review and respond
3. **Coordination Meeting** if multiple packages are significantly affected

## Cross-Package Coordination Patterns

### Pattern 1: Sequential Package Updates
For changes that must propagate through the dependency chain:

```markdown
## Sequential Update Plan: [Feature/Change Name]

### Update Sequence
1. **Core Package** (Foundation changes)
   - Changes: [Specific changes needed]
   - Timeline: [Completion date]
   - Dependencies: [What other packages are waiting for]

2. **React Package** (Hook layer changes)  
   - Changes: [Specific changes needed]
   - Dependencies: [Depends on Core Package completion]
   - Timeline: [Completion date]

3. **UI Components Package** (Component layer changes)
   - Changes: [Specific changes needed]  
   - Dependencies: [Depends on React Package completion]
   - Timeline: [Completion date]

4. **Demo Package** (Integration showcase)
   - Changes: [Specific changes needed]
   - Dependencies: [Depends on UI Components completion]  
   - Timeline: [Completion date]

### Coordination Points
- [Checkpoint 1]: Core Package API finalized
- [Checkpoint 2]: React Package hooks tested with Core
- [Checkpoint 3]: UI Components tested with React hooks
- [Checkpoint 4]: Demo integration validated
```

### Pattern 2: Parallel Package Development
For changes that can be developed in parallel with coordination:

```markdown
## Parallel Development Plan: [Feature/Change Name]

### Coordination Requirements
**API Contract**: [Agreed interface between packages]
**Mock Strategy**: [How packages will mock dependencies during development]
**Integration Points**: [Where packages will integrate]

### Package Development Plans
Each package coordinator defines:
- Implementation approach within agreed API contract
- Mock strategy for dependent package functionality  
- Testing approach including integration test plans
- Timeline aligned with integration milestones

### Integration Milestones  
- **Mock Integration**: [Date] - All packages working with mocks
- **Real Integration**: [Date] - Packages integrate with real implementations
- **End-to-End Testing**: [Date] - Complete feature testing across packages
```

### Pattern 3: Emergency Cross-Package Fixes
For urgent issues that span multiple packages:

```markdown
## Emergency Cross-Package Fix: [Issue Description]

### Issue Summary
**Severity**: [Critical / High / Medium]
**User Impact**: [Description of user impact]
**Affected Packages**: [List all affected packages]

### Immediate Response Plan
**Lead Coordinator**: [Which coordinator takes point]
**Response Team**: [Coordinators from each affected package]
**Communication Channel**: [Dedicated chat or meeting]

### Fix Strategy
1. **Root Cause**: [Which package contains the root issue]
2. **Immediate Mitigation**: [Quick fixes to reduce user impact]
3. **Proper Fix**: [Coordinated fix across packages]
4. **Testing Strategy**: [How fix will be validated across packages]

### Timeline
- **Immediate Response**: [Within 1-2 hours]
- **Mitigation Deployed**: [Within 4-8 hours]  
- **Proper Fix**: [Within 24-48 hours]
- **Full Validation**: [Within 2-3 days]
```

## Cross-Package Communication Channels

### Formal Communication
1. **Cross-Package Impact Assessments**: Formal document shared among coordinators
2. **Coordination Meeting Notes**: Documented decisions and agreements
3. **Integration Test Reports**: Results of cross-package testing
4. **API Change Notifications**: Formal notice of breaking changes

### Informal Communication
1. **Coordinator Chat Channel**: Ongoing coordination discussions
2. **Specialist Consultations**: Direct specialist-to-coordinator questions
3. **Daily Sync Updates**: Brief status on cross-package work
4. **Issue Escalations**: Quick escalation of blocking issues

## Quality Gates for Cross-Package Work

### Pre-Implementation Quality Gates
- [ ] Cross-package impact assessment completed
- [ ] All affected coordinators consulted and agreed to plan
- [ ] API contracts defined and agreed upon
- [ ] Testing strategy defined for each package and integration points
- [ ] Timeline coordinated across packages

### Implementation Quality Gates  
- [ ] Regular progress updates shared among coordinators
- [ ] Integration points tested as they become available
- [ ] Any deviations from plan communicated and approved
- [ ] Cross-package testing completed successfully

### Post-Implementation Quality Gates
- [ ] All affected packages updated and tested
- [ ] Integration testing passes across all package combinations
- [ ] Documentation updated in all affected packages
- [ ] Rollback plan defined and tested if needed

## Escalation Protocols

### When Cross-Package Coordination Fails
1. **Technical Disagreement**: Coordinators can't agree on approach
   - Escalate to: Technical lead or architecture review
   - Timeline: 24-48 hours for resolution

2. **Resource Conflict**: Timeline or resource conflicts between packages
   - Escalate to: Product owner or project manager  
   - Timeline: 48-72 hours for prioritization decision

3. **Quality Concerns**: One package has concerns about another's approach
   - Escalate to: Joint technical review with specialists
   - Timeline: 24 hours for review, 48 hours for resolution

## Success Metrics

### Cross-Package Coordination Effectiveness
- **Coordination Coverage**: Percentage of cross-package work that gets proper coordination
- **Issue Prevention**: Reduction in cross-package bugs due to coordination
- **Timeline Accuracy**: How often cross-package work completes on estimated timeline
- **Rework Reduction**: Reduction in rework due to package integration issues

### Communication Quality  
- **Response Time**: How quickly coordinators respond to coordination requests
- **Decision Quality**: How often coordination decisions prevent downstream issues
- **Documentation Completeness**: Quality of cross-package coordination documentation

## Anti-Patterns to Avoid

### ❌ **Silent Cross-Package Changes**
```
BAD: Making changes that affect other packages without notification
RESULT: Breaking changes discovered late, emergency fixes required
```

### ❌ **Assumptions About Other Packages** 
```
BAD: "I assume the React package will handle this correctly"
RESULT: Integration failures, finger-pointing, timeline delays
```

### ❌ **Last-Minute Coordination**
```
BAD: Discovering cross-package impacts during implementation
RESULT: Rushed coordination, suboptimal solutions, quality issues
```

### ✅ **Proactive Cross-Package Management**
- Early impact assessment and coordination
- Clear API contracts and integration points
- Regular communication and progress updates
- Quality gates at each integration milestone

---

**Remember**: Cross-package coordination prevents expensive integration problems and ensures all packages work together seamlessly. Proactive coordination is always more efficient than reactive problem-solving.