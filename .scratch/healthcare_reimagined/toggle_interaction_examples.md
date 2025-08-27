# Toggle Interaction Examples - Healthcare Tools

This document provides detailed examples of how toggles work in practice with the reimagined healthcare tools, showing the actual trigger mechanisms and user interactions.

## Understanding Toggle Mechanisms

### **1. User-Initiated Toggles (Manual Control)**
Users can type toggle commands directly in their messages to control information density.

### **2. Agent-Initiated Toggles (Programmatic Control)**  
The agent can decide to expand or collapse content based on the situation.

### **3. State-Based Rendering (Automatic Context)**
Content appears automatically based on query analysis and user expertise level.

---

## Example 1: Basic Drug Research Query

### **Initial User Request:**
*"Can you help me research information about ibuprofen?"*

### **Step 1: Agent's Initial Prompt State**
```
# FDA Drug Information Tool
You can search the FDA's National Drug Code (NDC) database for official drug information.

## Basic Drug Search
Use `get_drug_info(generic_name="drug_name", limit=5)` to find FDA-registered drug information.

FDA search examples and best practices available - *Use `toggle(fda_search_examples)` to display.*

## Safety Information
**GENERAL DRUG RESEARCH**: FDA database provides official drug registration and labeling information.

FDA database field explanations available - *Use `toggle(fda_data_fields)` to display.*
Emergency drug safety protocols available - *Use `toggle(emergency_drug_protocols)` to display.*
```

**Token Count**: ~800 tokens (collapsed state)

### **Step 2: Agent Searches FDA Database**
Agent calls: `get_drug_info(generic_name="ibuprofen", limit=5)`

### **Step 3: Agent Provides Results and Offers More Detail**
*"I found FDA information about ibuprofen products. Here are the key findings... Would you like me to show you more detailed search examples or explain what these FDA data fields mean? You can use `toggle(fda_search_examples)` or `toggle(fda_data_fields)` for more information."*

---

## Example 2: User Requests More Detail

### **User Follow-up:**
*"That's helpful, but I'd like to understand what all these FDA fields mean. toggle(fda_data_fields)"*

### **Step 4: Content Expansion via Toggle**
The agent's prompt now includes:
```
## FDA Data Fields Explained:
- **Generic Name**: Official drug ingredient name
- **Brand Name**: Commercial product name  
- **NDC Number**: National Drug Code (unique identifier)
- **Dosage Form**: Tablet, capsule, injection, etc.
- **Route**: How drug is administered (oral, IV, topical)
- **Marketing Status**: Active, discontinued, etc.
- **DEA Schedule**: Controlled substance classification
- **Labeler**: Company that markets the drug

*Use `toggle(fda_data_fields)` to hide field explanations.*
```

**Token Count**: ~1,200 tokens (expanded with field explanations)

### **Agent Response:**
*"Now I can explain these FDA fields in detail. Looking at the ibuprofen data I found... [detailed explanation using the expanded field information]*

---

## Example 3: Emergency Symptom Query (Automatic State Change)

### **User Request:**
*"I'm having severe chest pain and shortness of breath. What could this be?"*

### **Step 1: Automatic State Machine Activation**
```python
# System automatically sets:
query_type_machine.set_state('emergency_symptoms')
user_expertise_machine.set_state('patient')  # assumed
```

### **Step 2: Emergency Content Automatically Renders**
```
# Medical Safety and Emergency Recognition
**EMERGENCY ALERT**: If experiencing severe symptoms, seek immediate medical attention. Call 911 or go to the nearest emergency room. This research tool cannot replace emergency medical care.

## Emergency Recognition Protocols
Emergency symptom recognition guidelines available - *Use `toggle(emergency_recognition)` to display.*
```

### **Step 3: Agent Immediately Activates Emergency Protocol**
The agent recognizes this as a potential emergency and automatically expands emergency content:

```python
# Agent programmatically activates:
toggle_open('emergency_recognition')
```

### **Step 4: Emergency Content Expands Automatically**
```
## Immediate Medical Attention Required:

**Cardiovascular Emergencies:**
- Chest pain with shortness of breath ← MATCHES USER SYMPTOMS
- Severe chest pressure or crushing sensation
- Rapid or irregular heartbeat with dizziness
- Sudden severe headache with neck stiffness

**Action Required:** Call 911 immediately or go to nearest emergency room.
```

### **Agent Response:**
*"⚠️ **EMERGENCY ALERT** ⚠️ Your symptoms of severe chest pain and shortness of breath require immediate medical attention. Please call 911 or go to the nearest emergency room right now. Do not wait for research information - this could be a medical emergency requiring immediate care."*

**Token Count**: ~2,000 tokens (emergency protocols automatically expanded)

---

## Example 4: Professional User vs Patient User

### **Same Query, Different User Types:**
*"I need information about metformin for diabetes research."*

### **Healthcare Professional User:**
**Automatic State**: `user_expertise_machine.set_state('healthcare_professional')`

**Rendered Content:**
```
## Professional vs Patient Guidance
**Professional Note**: FDA NDC data includes DEA schedules, NDC numbers, and regulatory classifications. Cross-reference with FDA Orange Book for therapeutic equivalence.

## User Expertise Adaptation  
**Professional Research**: Focus on clinical applicability, study methodology, and practice-changing evidence. Include confidence intervals, effect sizes, and clinical significance.
```

### **Patient User:**
**Automatic State**: `user_expertise_machine.set_state('patient')`

**Rendered Content:**
```
## Professional vs Patient Guidance
**Patient-Friendly**: This tool searches official FDA drug registration data. Information found here represents what the FDA has approved, but always consult healthcare providers for personal medical decisions.

## User Expertise Adaptation
**Patient-Friendly Research**: Translate findings into understandable terms. Focus on practical implications, safety data, and patient-relevant outcomes. Always emphasize professional consultation.
```

---

## Example 5: Complex Research Query with Multiple Toggles

### **User Request:**
*"I'm researching migraine treatments and want to understand the research methodology. Can you show me your detailed approach? toggle(research_methodology) toggle(evidence_hierarchy)"*

### **Step 1: Multiple Toggle Processing**
Both toggles activate simultaneously:
- `research_methodology` expands detailed research process
- `evidence_hierarchy` expands evidence quality information

### **Step 2: Content Expansion**
**Token Count**: ~3,500 tokens (multiple expanded sections)

### **Step 3: User Realizes Too Much Information**
*"This is too detailed for what I need right now. toggle(research_methodology)"*

### **Step 4: Selective Collapse**
The `research_methodology` section collapses back to hint text, but `evidence_hierarchy` remains expanded.

**Token Count**: ~2,200 tokens (one section collapsed, one still expanded)

---

## Toggle Trigger Summary

### **Manual Triggers (User Types):**
- `toggle(section_name)` - User types this in their message
- Agent processes the command and updates prompt accordingly

### **Programmatic Triggers (Agent Decides):**
```python
# Agent thinks: "This is an emergency, I need safety protocols"
toggle_open('emergency_recognition')

# Agent thinks: "User seems overwhelmed, let me simplify"  
toggle_close('advanced_features')
```

### **Automatic Triggers (System Responds):**
```python
# Query analysis triggers state changes:
if "chest pain" and "shortness of breath" in query:
    query_type_machine.set_state('emergency_symptoms')
    
if user_role == "doctor":
    user_expertise_machine.set_state('healthcare_professional')
```

---

## Context Window Management Benefits

### **Traditional Approach:**
- **All content always visible**: ~15,000 tokens
- **Agent overwhelmed** with irrelevant information
- **Poor attention** to current task

### **Selective Rendering Approach:**
- **Baseline state**: ~2,000 tokens
- **Task-relevant expansion**: ~5,000 tokens  
- **Full detail when needed**: ~8,000 tokens
- **Emergency mode**: ~3,000 tokens (focused on safety)

### **Result:**
- **60-70% token reduction** in most scenarios
- **Focused agent attention** on relevant information
- **User-controlled information density**
- **Context-aware adaptation** to expertise and situation