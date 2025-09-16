# Transportation & Logistics Multi-Agent System

This directory contains a comprehensive multi-agent system designed for trucking and logistics operations. The system demonstrates advanced agent coordination, delegation, and specialized domain expertise.

## Agent Hierarchy

### Level 1: Main Supervising Agent
- **Primary Interface**: Business strategy and financial focus
- **Key Role**: Request clarification, financial document prioritization, team delegation

### Level 2: Specialized Supervisors
- **Operations Supervisor**: Coordinates operational data gathering and quality assurance
- **Reports Specialist**: Expert in creating financial, operational, and vehicle reports

### Level 3: Domain Specialists (Under Operations Supervisor)
- **ELD Specialists**: Motive, Samsara agents for vehicle tracking and health
- **TMS Specialist**: Alvys, Oracle, Ascend system integration
- **Fuel Card Specialist**: Fuel system management
- **Mechanical/Maintenance Specialist**: Preventive maintenance and safety

## Design Philosophy

All agents are built using the Agent C selective rendering system with:
- Progressive disclosure through collapsible sections
- Context-aware adaptation
- Proper delegation and handoff protocols
- Assumed full API/database connectivity for demonstration purposes

## Usage

These agents are designed as templates to demonstrate capabilities and can be extended with real API connections and tools as needed.