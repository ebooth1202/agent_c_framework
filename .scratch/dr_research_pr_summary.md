# Dr Research - Medical Research Advisor

## Overview
Dr Research is a sophisticated medical research assistant that specializes in evidence-based medical information. He acts as a brilliant medical librarian with access to clinical trials and FDA databases, helping users navigate complex medical research while maintaining strict accuracy and appropriate medical disclaimers.

## Key Capabilities

### 🔍 **Symptom Triage Intelligence**
- Recognizes when symptoms are too vague for meaningful research
- Asks targeted clarifying questions to gather specific medical information
- Only proceeds with research once sufficient specificity is achieved

### 📊 **Evidence-Based Research**
- **Clinical Trials**: Searches current and completed studies for treatment protocols
- **FDA Database**: Looks up drug information, warnings, and contraindications  
- **PubMed Literature**: Accesses peer-reviewed medical research
- **Drug Interactions**: Analyzes medication interactions and safety profiles

### 🛡️ **Medical Disclaimer Compliance**
- Always includes appropriate medical disclaimers
- Clearly distinguishes between research information and medical advice
- Emphasizes the importance of professional medical consultation
- Maintains strict boundaries as a research assistant, not a medical practitioner

## Technical Implementation

### Tools Configured
- `FDANDCTools` - FDA drug database access
- `ClinicalTrialsTools` - Clinical trials research
- `PubMedTools` - Medical literature search
- Standard agent tools (Workspace, Planning, Think, etc.)

### API Requirements
- **NCBI API Key** - Required for PubMed and Clinical Trials access
- **FDA API Key** - Required for FDA drug database queries

## Agent Configuration
- **Key**: `dr_research`
- **Model**: Claude Sonnet 4
- **Category**: `domo` (UI accessible)
- **Budget**: 20k tokens, 64k max

## Changes Made
- ✅ Added essential health research tools to agent configuration
- ✅ Configured comprehensive medical research persona

## Usage Example
```
User: "I have rheumatoid arthritis and I'm taking methotrexate"
Dr Research: "I can help you research the current evidence for rheumatoid arthritis 
treatment protocols. Let me search for recent clinical trials on methotrexate 
effectiveness and look up the FDA information for this medication..."
```

---
**⚠️ Important**: This agent provides research information only, not medical advice. Users should always consult qualified healthcare professionals for medical decisions.