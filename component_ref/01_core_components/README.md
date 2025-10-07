# Core Components

This directory contains the foundational instruction patterns that can be used when building agents. Each component follows a **binary decision model** - agents either USE a component or DO NOT USE it.

## What's in This Directory

The core components are organized into tiers based on reuse value and decision clarity:

### Tier 1: Universal Components
High reuse patterns with clear binary decisions, excellent component candidates:

- **critical_interaction_guidelines_component.md** - Path verification and workspace safety rules
- **reflection_rules_component.md** - Think tool usage patterns for different agent focuses  
- **workspace_organization_component.md** - File and directory management patterns
- **code_quality_python_component.md** - Python development standards and practices
- **code_quality_csharp_component.md** - C# development standards and practices

### Tier 2: Capability Components
Patterns for specific agent capabilities with focused variants:

- **planning_coordination_component.md** - Multi-step work coordination using planning tools
- **clone_delegation_component.md** - Task delegation framework for clone agents
- **human_pairing_general_component.md** - General purpose human collaboration patterns
- **human_pairing_development_component.md** - Development-focused human collaboration patterns
- **critical_working_rules_component.md** - Methodical work approach for complex tasks

### Tier 3: Specialized Components
Focused usage patterns with variant approaches:

- **context_management_component.md** - Context window management for complex workflows
- **team_collaboration_component.md** - Multi-agent team coordination patterns
- **quality_gates_component.md** - Formal validation and signoff frameworks
- **domain_knowledge_template_component.md** - Structural template for specialist expertise

## How to Use Components

**Binary Decision Process**:
1. **Decide**: "Does this agent need [capability]?" → YES/NO
2. **Choose**: If YES, use the appropriate component variant
3. **Customize**: Adapt the component for specific agent needs
4. **Compose**: Combine selected components with custom expertise

**Component Selection Criteria**:
- Each component has clear "When to Use" guidance
- Components work independently (no conditional logic)
- Focused variants available for different agent roles
- All components are fully-formed, proven patterns

## Component Format

Each component includes:
- **Binary Decision**: Clear YES/NO criteria
- **Who Uses This**: Target agent types and scenarios  
- **Component Pattern**: The proven instruction block text
- **Usage Notes**: Customization guidance
- **Examples in Use**: Real agents implementing this component

This approach preserves the craft of agent building while providing proven patterns as building blocks.