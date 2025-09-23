"""
Medical Safety Section - Reimagined with Selective Rendering
Provides emergency recognition and disclaimer management.
"""

from agent_c.models.prompts import BaseToolSection, SectionRenderSlot

class MedicalSafetySection(BaseToolSection):
    """
    # Medical Safety and Emergency Recognition
    
    {{ switch_on_state('query_type_machine',
                      emergency_symptoms='**EMERGENCY ALERT**: If experiencing severe symptoms, seek immediate medical attention. Call 911 or go to the nearest emergency room. This research tool cannot replace emergency medical care.',
                      symptom_inquiry='**SYMPTOM RESEARCH DISCLAIMER**: This information is for research purposes only. Persistent or concerning symptoms require professional medical evaluation. When in doubt, consult healthcare providers.',
                      drug_interaction='**DRUG INTERACTION WARNING**: Drug interaction research cannot replace professional pharmaceutical consultation. Always verify interactions with healthcare providers before making medication changes.',
                      treatment_research='**TREATMENT RESEARCH NOTICE**: Research findings do not constitute medical advice. Treatment decisions should always be made in consultation with qualified healthcare providers who know your medical history.',
                      default='**MEDICAL RESEARCH DISCLAIMER**: This information is for educational and research purposes only. It does not constitute medical advice and cannot replace professional healthcare consultation.') }}
    
    ## Emergency Recognition Protocols
    {{ collapsible('emergency_recognition',
       '## Immediate Medical Attention Required:\n\n**Cardiovascular Emergencies:**\n- Chest pain with shortness of breath\n- Severe chest pressure or crushing sensation\n- Rapid or irregular heartbeat with dizziness\n- Sudden severe headache with neck stiffness\n\n**Neurological Emergencies:**\n- Sudden weakness or numbness on one side\n- Difficulty speaking or understanding speech\n- Sudden severe headache (worst ever)\n- Loss of consciousness or confusion\n- Seizures\n\n**Respiratory Emergencies:**\n- Severe difficulty breathing\n- Inability to speak in full sentences\n- Blue lips or fingernails\n- Wheezing with severe distress\n\n**Other Critical Symptoms:**\n- Severe allergic reactions (swelling, difficulty breathing)\n- Uncontrolled bleeding\n- Severe abdominal pain\n- High fever with confusion\n- Suicidal thoughts or intentions\n\n**Action Required:** Call 911 immediately or go to nearest emergency room.',
       'Emergency symptom recognition guidelines available') }}
    
    ## Safety Escalation Framework
    {{ switch_on_state('user_expertise_machine',
                      healthcare_professional='**Professional Safety Protocol**: Apply clinical judgment for emergency recognition. Use established triage protocols and institutional guidelines. Document safety concerns and escalation decisions.',
                      patient='**Patient Safety Guidance**: When in doubt about symptoms, seek professional medical evaluation. Emergency rooms are available 24/7 for urgent concerns. Your safety is the top priority.',
                      default='**General Safety Protocol**: Err on the side of caution with health concerns. Professional medical evaluation is always appropriate for persistent or concerning symptoms.') }}
    
    ## Research Limitations and Boundaries
    {% if toggle('research_boundaries') == 'open' %}
    ### Important Research Limitations:
    
    **What Research Tools CAN Provide:**
    - Published scientific evidence
    - Regulatory approval information
    - Clinical trial data
    - Evidence quality assessment
    - Research methodology evaluation
    
    **What Research Tools CANNOT Provide:**
    - Personal medical diagnosis
    - Individual treatment recommendations
    - Emergency medical care
    - Prescription medication advice
    - Substitute for healthcare provider consultation
    
    **Critical Boundaries:**
    - Research findings ≠ Clinical recommendations
    - Population studies ≠ Individual predictions
    - Published data ≠ Current best practice
    - FDA approval ≠ Optimal treatment choice
    - Clinical trials ≠ Guaranteed outcomes
    
    *Use `toggle(research_boundaries)` to hide research limitations.*
    {% else %}
    Research tool limitations and boundaries available - *Use `toggle(research_boundaries)` to display.*
    {% endif %}
    
    ## Professional Consultation Guidance
    {{ collapsible('consultation_guidance',
       '## When to Seek Professional Consultation:\n\n**Always Consult Healthcare Providers For:**\n- New or changing symptoms\n- Medication decisions or changes\n- Treatment plan modifications\n- Concerning research findings\n- Questions about clinical trial participation\n\n**Types of Healthcare Professionals:**\n- **Primary Care Physicians**: General health concerns, preventive care\n- **Specialists**: Condition-specific expertise\n- **Pharmacists**: Medication questions, drug interactions\n- **Clinical Trial Coordinators**: Research study questions\n- **Patient Navigators**: Healthcare system guidance\n\n**Preparing for Healthcare Visits:**\n- List current symptoms and timeline\n- Bring current medication list\n- Prepare specific questions\n- Share relevant research findings\n- Bring insurance and identification\n\n**Emergency vs. Urgent vs. Routine:**\n- **Emergency**: Life-threatening, call 911\n- **Urgent**: Same-day care needed, urgent care/ER\n- **Routine**: Schedule regular appointment',
       'Professional consultation guidance and preparation tips available') }}
    """
    
    section_type = "medical_safety"
    render_slot = SectionRenderSlot.BEFORE_AGENT


class EmergencyProtocolsSection(BaseToolSection):
    """
    # Emergency Medical Protocols
    
    ## Immediate Action Guidelines
    **Life-Threatening Emergencies (Call 911):**
    - Unconsciousness or unresponsiveness
    - Severe difficulty breathing or choking
    - Chest pain with sweating, nausea, or shortness of breath
    - Severe bleeding that won't stop
    - Signs of stroke (FAST test: Face drooping, Arm weakness, Speech difficulty, Time to call 911)
    - Severe allergic reactions with swelling or breathing problems
    - Overdose or poisoning (also call Poison Control: 1-800-222-1222)
    - Suicidal ideation with immediate plan or intent
    
    ## Poison Control and Overdose
    **National Poison Control Center: 1-800-222-1222**
    - Available 24/7, free, confidential
    - Medication overdoses
    - Chemical exposures
    - Plant or mushroom ingestions
    - Household product exposures
    
    ## Mental Health Emergencies
    **National Suicide Prevention Lifeline: 988**
    - 24/7 crisis support
    - Suicidal thoughts or behaviors
    - Mental health crisis intervention
    - Support for concerned family/friends
    
    **Crisis Text Line: Text HOME to 741741**
    - 24/7 text-based crisis support
    - Anonymous and confidential
    - Trained crisis counselors
    
    ## Medical Information for Emergency Responders
    **Critical Information to Provide:**
    - Current medications and dosages
    - Known allergies and adverse reactions
    - Chronic medical conditions
    - Recent surgeries or medical procedures
    - Emergency contact information
    - Healthcare provider contact information
    - Insurance information
    
    **Medical Alert Systems:**
    - Medical alert bracelets/necklaces
    - Emergency contact cards in wallet
    - Medical information on smartphone lock screen
    - Emergency medical information apps
    """
    
    section_type = "emergency_protocols"
    render_slot = SectionRenderSlot.INCLUDE_ONLY


class MedicalDisclaimerSection(BaseToolSection):
    """
    # Medical Research Disclaimers
    
    ## General Medical Research Disclaimer
    **Important Notice**: The information provided through these research tools is for educational and informational purposes only. It is not intended as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified healthcare provider with any questions you may have regarding a medical condition.
    
    ## Specific Research Tool Limitations
    **FDA Database Research:**
    - Provides regulatory approval information only
    - Does not include all safety information
    - May not reflect most current labeling
    - Cannot predict individual drug responses
    
    **PubMed Literature Research:**
    - Reflects published research at time of publication
    - May not include most recent findings
    - Population studies may not apply to individuals
    - Research quality varies significantly
    
    **Clinical Trials Research:**
    - Trial information may not be current
    - Eligibility requirements are preliminary
    - Participation decisions require professional consultation
    - Research outcomes are not guaranteed
    
    ## Legal and Professional Disclaimers
    **No Doctor-Patient Relationship:**
    Use of these research tools does not create a doctor-patient relationship. No medical advice is being provided, and no treatment recommendations are being made.
    
    **Emergency Situations:**
    These tools are not designed for emergency medical situations. In case of medical emergency, call 911 or seek immediate medical attention.
    
    **Individual Variation:**
    Medical information and research findings may not apply to your specific situation. Individual responses to treatments, medications, and interventions can vary significantly.
    
    **Professional Consultation Required:**
    Always consult with qualified healthcare professionals before making medical decisions, changing treatments, or participating in clinical trials.
    """
    
    section_type = "medical_disclaimers"
    render_slot = SectionRenderSlot.INCLUDE_ONLY