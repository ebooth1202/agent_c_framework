# Reference Material Through Line Protocol

## Core Principle
**ALL participants in a task MUST receive complete reference material, requirements, and user context without filtering from other agents.**

## Critical Rule: Preserve User Voice

### ❌ **NEVER Filter or Paraphrase User Requirements**
```
BAD: "The user wants audio improvements"
GOOD: "User stated: 'The audio cuts out when switching between voice models during active conversations, especially on mobile Safari. This happens about 30% of the time and users have to refresh the page.'"
```

### ✅ **ALWAYS Include Direct User Quotes**
- Copy exact user statements into task descriptions
- Include user-provided examples, error messages, or specifications
- Preserve user context about priority, timeline, or business impact
- Include any user-provided reference materials or documentation

## Implementation Protocol

### For Package Coordinators
When receiving work from users or other coordinators:

1. **Capture Complete User Context**
   ```markdown
   ## Original User Request
   [EXACT user statement - no paraphrasing]
   
   ## User-Provided Details
   - [Any examples, error messages, or specifications]
   - [Any reference materials or documentation mentioned]
   - [Any priority or timeline context]
   
   ## Additional Context Gathered
   - [Questions you asked and user responses]
   - [Any clarifications received]
   ```

2. **Pass Through to Specialists**
   - Include the complete "Original User Request" section in ALL specialist task assignments
   - Never summarize or filter user requirements
   - Always provide direct links or copies of any reference materials the user mentioned

### For Specialists (Dev/Test)
When receiving work from coordinators:

1. **Verify Complete Context**
   - Confirm you have the original user request (unfiltered)
   - Ask coordinator if any user context is missing
   - Request direct access to any user-provided reference materials

2. **Reference User Intent in Work**
   - Keep user requirements visible during implementation
   - Test against user-stated success criteria
   - Document how your work addresses the original user request

## Quality Control

### Coordinator Checklist
Before assigning work to specialists:
- [ ] Original user request included verbatim
- [ ] All user-provided examples/details included  
- [ ] Reference materials accessible to specialist
- [ ] User priority/timeline context preserved

### Specialist Checklist
Before starting work:
- [ ] I understand the original user request
- [ ] I have access to all user-provided reference materials
- [ ] I know what success looks like from the user's perspective
- [ ] I can trace my work back to user requirements

## Cross-Package Reference Material

### When Tasks Span Multiple Packages
Each package coordinator must:
1. **Receive complete user context** (not filtered summaries from other coordinators)
2. **Share reference materials directly** (not just links or descriptions)
3. **Preserve user priority** across package boundaries

### Example: Multi-Package Task Distribution
```markdown
## User Request (Shared to ALL Package Coordinators)
User stated: "When users click the voice button in the demo app, sometimes the audio doesn't start and they get stuck in a 'connecting' state. The React hook seems to be working fine, but the UI doesn't reflect the actual state. This is blocking our client demo next week."

## Reference Materials (Shared to ALL)
- User-provided screen recording: [link]
- Browser console logs: [attachment]
- Specific demo URL where issue occurs: [link]

## Package Distribution
- Demo Coordinator: UI state reflection issue in demo app
- React Coordinator: Hook state validation and communication
- UI Components Coordinator: Voice button state handling
- Core Coordinator: Audio connection state events
```

## Anti-Patterns to Avoid

### ❌ **The Telephone Game**
```
User → Coordinator A → Coordinator B → Specialist
"Audio bug" → "Connection issue" → "WebSocket problem" → "Protocol error"
```

### ✅ **Direct Reference Line**
```
User → All Coordinators (complete context) → All Specialists (complete context)
Original user description preserved at every level
```

### ❌ **Context Loss Through Summarization**
- "The user wants better performance" (loses specific metrics, scenarios, business context)
- "There's a bug in audio" (loses reproduction steps, environment, impact)
- "Client needs this fixed" (loses actual requirements, success criteria)

### ✅ **Context Preservation Through Direct Quotes**
- User stated: "Audio latency needs to be under 200ms on mobile devices for our enterprise clients"
- User reported: "Steps to reproduce: 1) Join conversation, 2) Switch to voice mode, 3) Error occurs 40% of the time on Chrome mobile"
- User emphasized: "This is blocking our Q4 client demo - needs to be resolved by Friday"

## Documentation Trail

### Maintain Reference Integrity
- **Planning Tools**: Include original user request in all task descriptions
- **Chat Sessions**: Begin specialist chats with user context section
- **Handoff Documents**: Reference original user requirements in all deliverables
- **Test Reports**: Validate against original user success criteria

---

**Remember**: The user's voice and intent must flow unfiltered through the entire system. Every agent should be able to trace their work directly back to what the user actually said and needed.