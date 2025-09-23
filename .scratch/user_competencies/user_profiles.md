# User Competency Assessment Framework

## Overview

There are a couple of different approaches to implementing user competency levels within the Agent C platform. We start by looking at the Agent C platform itself and considering how users interact with the multi-agent ecosystem.

## Implementation Approaches

### Self-Assessment Approach (Simplest)

Firstly, we can allow users themselves to determine their own level(s) but initially start everyone out as **Novice**. We then create a user-competency assessment agent that creates challenges/assessments for users based on their current level versus their desired level and provides them an honest review as to where they currently are, making recommendations for where they should be. This could end up being routed back to an Admin that has to approve this step up, or the users themselves can upgrade their skill level accordingly.

### Automated Assessment Approach (Complex)

The second approach involves making adjustments within the agent persona categories themselves if we aren't really desiring individual users to be able to manipulate their own skill levels. This would enable us to track different parameters such as appropriate agent usage (selecting the correct agent for the task).

Aside from that, we can also track things such as error recovery, sophistication patterns, discovery patterns and others. It just depends on how complex we want to dive into the initial competency setting and the ongoing assessment.

### Hybrid Approach

Obviously the simplest approach being that we allow the user to determine their skill levels and flesh out a sort of 'scale' description for them to reference as far as content displayed, user guidance, agent feedback, etc. We can also create an agent that delivers different tests to a user and guides the user on their skill level choice, as mentioned earlier. The more complex approach involves truly tracking data on a per-user basis and creating an algorithm to consider multiple aspects, and then that system basically allows them the ability to gain or lose a certain skill level.

## Competency Level Examples

### Agent C Platform Competency

#### **Novice**
- Relies heavily on detailed instructions and examples
- Asks basic questions about Agent C functionality
- Makes single-step, simple requests
- Often tries to accomplish everything with one Agent alone
- Needs guidance on when and how to use different features

#### **Developing**
- Beginning to use more complex features with some guidance
- Occasionally asks about available agents or capabilities
- Starting to structure multi-step requests
- Shows awareness that different agents might be better for certain tasks
- Can follow suggested workflows with minimal assistance

#### **Proficient**
- Regularly uses advanced features independently
- Proactively asks about specialized agents for specific tasks
- Designs multi-step workflows effectively
- Understands agent capabilities and limitations
- Can troubleshoot common issues independently

#### **Expert**
- Leverages the full Agent C ecosystem efficiently
- Immediately recognizes optimal agent-task pairings
- Designs complex multi-agent workflows
- Serves as a resource for other users
- Innovates new approaches to problem-solving within the platform

### Agent Orchestration Competency

#### **Novice**
- Uses only one Agent for all tasks
- Unaware of specialized agents available
- Makes no delegation attempts
- Struggles with complex multi-domain problems

#### **Developing**
- Occasionally asks "is there a better agent for this?"
- Beginning to delegate with prompting
- Basic awareness of some specialist agents
- Still defaults to Agent C for most tasks

#### **Proficient**
- Regularly evaluates which agent is most appropriate
- Proactively discovers and uses specialized agents
- Understands agent handoffs and workflows
- Designs simple multi-agent processes

#### **Expert**
- Immediately identifies optimal agent for each task
- Orchestrates complex multi-agent workflows seamlessly
- Deep knowledge of the entire agent ecosystem
- Mentors others on effective agent utilization

## Directly Observable Behaviors

### Platform Usage Patterns
- **Session Management**: How effectively users manage conversation continuity
- **Feature Utilization**: Which capabilities they use versus avoid
- **Request Sophistication**: Evolution from simple to complex structured requests
- **Error Recovery**: How they handle failed requests or unexpected responses
- **Help-Seeking Behavior**: Whether they ask for guidance or try to figure things out independently

### Agent Ecosystem Interaction
- **Agent Discovery**: Frequency of exploring available agents and their capabilities
- **Delegation Patterns**: How often and appropriately they delegate tasks to specialized agents
- **Multi-Agent Coordination**: Ability to design and execute workflows across multiple agents
- **Task-Agent Matching**: Appropriateness of agent selection for specific task types
- **Workflow Complexity**: Sophistication of the processes they design and execute

### Learning and Adaptation Indicators
- **Progression Rate**: How quickly they adopt new features and capabilities
- **Pattern Recognition**: Whether they remember and reuse successful approaches
- **Innovation**: Development of novel solutions or workflow patterns
- **Mentoring Behavior**: Whether they help or guide other users

## Agent Classification Approaches

To effectively assess user competency in agent orchestration, we need to classify what each agent specializes in and when they should be used.

### Classification Methods

**Explicit Metadata Approach**: Add specialization tags directly to agent configurations, defining primary domains, secondary capabilities, complexity levels, and task types.

**Automatic Extraction**: Analyze existing agent personas and descriptions to automatically determine specializations using natural language processing and keyword matching.

**Usage Pattern Learning**: Track actual user interactions and success patterns to dynamically learn what each agent excels at over time.

**Hybrid Classification**: Combine manual tagging with automatic inference and ongoing learning from usage data.

### Specialization Dimensions

- **Primary Domains**: Core areas of expertise (coding, analysis, documentation, etc.)
- **Task Types**: Specific activities the agent handles well (implementation, planning, review, etc.)
- **Complexity Level**: The sophistication of problems the agent can handle
- **Integration Capabilities**: How well the agent works with others in multi-agent workflows

This classification system enables the competency assessment framework to evaluate whether users are making appropriate choices when selecting agents for specific tasks, providing a foundation for measuring and improving agent orchestration skills.