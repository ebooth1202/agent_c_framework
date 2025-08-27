"""
Clinical Trials Tools Section - Reimagined with Selective Rendering
Provides context-aware trial search with eligibility guidance.
"""

from agent_c.models.prompts import BaseToolSection, SectionRenderSlot

class ClinicalTrialsToolsSection(BaseToolSection):
    """
    # Clinical Trials Research Tool
    
    You can search ClinicalTrials.gov for ongoing and completed clinical research studies.
    
    ## Basic Trial Search
    Use `get_trials(condition="medical condition", location="geographic area")` to find relevant clinical trials.
    
    {{ collapsible('trials_search_examples',
       '## Search Examples:\n- `get_trials(condition="diabetes", location="California")` - Find diabetes trials in California\n- `get_trials(condition="migraine")` - Find all migraine trials globally\n- `get_trials(condition="breast cancer", location="New York")` - Find breast cancer trials in NY\n\n**Search Strategy Tips:**\n- Use specific medical conditions for focused results\n- Include location to find geographically accessible trials\n- Try both common and medical terms (e.g., "heart attack" and "myocardial infarction")\n- Search without location first to see all available trials',
       'Clinical trials search examples and strategy tips available') }}
    
    ## Trial Context Adaptation
    {{ switch_on_state('query_type_machine',
                      treatment_research='**TREATMENT TRIALS**: Focus on interventional studies testing new treatments. Prioritize Phase II and III trials with clinical endpoints.',
                      drug_research='**DRUG TRIALS**: Emphasize pharmaceutical interventions. Include Phase I safety studies through Phase IV post-market studies.',
                      device_research='**DEVICE TRIALS**: Focus on medical device studies. Consider FDA approval pathway and device classification.',
                      prevention_research='**PREVENTION TRIALS**: Look for primary and secondary prevention studies. Include lifestyle and pharmaceutical interventions.',
                      diagnostic_research='**DIAGNOSTIC TRIALS**: Search for studies validating new diagnostic tests or screening methods.',
                      default='**GENERAL TRIAL RESEARCH**: Comprehensive search across all trial types. Focus on study phase and recruitment status.') }}
    
    ## Trial Eligibility Guidance
    {{ collapsible('eligibility_assessment',
       '## Understanding Trial Eligibility:\n\n**Inclusion Criteria** (Must meet ALL):\n- Age requirements\n- Specific diagnosis or condition\n- Disease stage or severity\n- Previous treatment history\n- Geographic accessibility\n\n**Exclusion Criteria** (Cannot have ANY):\n- Certain medical conditions\n- Concurrent medications\n- Previous treatments\n- Pregnancy status\n- Other ongoing trials\n\n**Pre-Screening Questions:**\n- Do you meet the basic age and diagnosis requirements?\n- Are you taking any medications that might exclude you?\n- Do you have access to the trial location?\n- Are you willing to comply with study requirements?\n\n*Use `toggle(eligibility_assessment)` to hide eligibility guidance.*',
       'Trial eligibility assessment guidance available') }}
    
    ## User Expertise Adaptation
    {{ switch_on_state('user_expertise_machine',
                      healthcare_professional='**Professional Trial Review**: Focus on study design, endpoints, statistical power, and regulatory pathway. Include investigator qualifications and institutional reputation.',
                      researcher='**Research Analysis**: Emphasize methodology, biostatistics, study innovation, and contribution to scientific knowledge. Include funding sources and collaboration networks.',
                      patient='**Patient-Friendly Information**: Explain trial phases, risks/benefits, time commitments, and patient rights. Emphasize informed consent and voluntary participation.',
                      default='Provide balanced trial information with clear explanation of study purpose, requirements, and patient considerations.') }}
    
    ## Trial Phase Understanding
    {{ collapsible('trial_phases',
       '## Clinical Trial Phases Explained:\n\n**Phase I** (Safety Testing):\n- Small groups (20-100 people)\n- Test safety and dosage\n- Determine side effects\n- Usually for new treatments\n\n**Phase II** (Efficacy Testing):\n- Larger groups (100-300 people)\n- Test effectiveness\n- Further safety monitoring\n- May compare to standard treatment\n\n**Phase III** (Comparative Effectiveness):\n- Large groups (300-3,000 people)\n- Compare to current standard treatment\n- Multi-center studies\n- Basis for FDA approval\n\n**Phase IV** (Post-Market Surveillance):\n- After FDA approval\n- Long-term effects monitoring\n- Real-world effectiveness\n- Rare side effect detection',
       'Clinical trial phases and their purposes explained') }}
    
    ## Advanced Trial Features
    {{ collapsible_section('trials_advanced_search',
                           'trials/advanced_search_strategies',
                           'Advanced clinical trials search techniques and filters available') }}
    
    {{ collapsible_section('trial_evaluation',
                           'trials/study_quality_assessment',
                           'Clinical trial quality evaluation and risk assessment available') }}
    
    {{ collapsible_section('patient_advocacy',
                           'trials/patient_rights_advocacy',
                           'Patient rights, advocacy resources, and trial participation guidance available') }}
    
    ## Safety and Ethical Considerations
    {% if toggle('trial_safety_ethics') == 'open' %}
    ### Clinical Trial Safety and Ethics:
    
    **Patient Rights:**
    - Voluntary participation (can withdraw anytime)
    - Informed consent (understand risks/benefits)
    - Privacy protection (HIPAA compliance)
    - Access to study results
    - Compensation for participation (if applicable)
    
    **Safety Monitoring:**
    - Data Safety Monitoring Board (DSMB) oversight
    - Adverse event reporting requirements
    - Regular safety reviews
    - Trial stopping rules for safety concerns
    
    **Ethical Oversight:**
    - Institutional Review Board (IRB) approval
    - Ethics committee review
    - Regulatory compliance (FDA, ICH-GCP)
    - Conflict of interest management
    
    **Red Flags to Watch For:**
    - Pressure to enroll quickly
    - Promises of guaranteed outcomes
    - Requests for payment to participate
    - Lack of informed consent process
    - No clear contact for questions
    
    *Use `toggle(trial_safety_ethics)` to hide safety and ethics information.*
    {% else %}
    Clinical trial safety, ethics, and patient rights information available - *Use `toggle(trial_safety_ethics)` to display.*
    {% endif %}
    """
    
    section_type = "clinical_trials_tools"
    render_slot = SectionRenderSlot.TOOL


class TrialsAdvancedSearchSection(BaseToolSection):
    """
    # Advanced Clinical Trials Search Strategies
    
    ## Search Optimization Techniques
    **Condition Terminology:**
    - Use both common names and medical terms
    - Include synonyms and related conditions
    - Try broader and narrower condition terms
    - Consider disease subtypes and stages
    
    **Geographic Considerations:**
    - Search by city, state, or country
    - Consider travel distance for regular visits
    - Look for multi-site trials with local locations
    - Check for remote/virtual trial components
    
    ## Trial Status Filtering
    **Recruitment Status:**
    - "Recruiting" - Currently enrolling participants
    - "Not yet recruiting" - Approved but not started
    - "Active, not recruiting" - Ongoing but full
    - "Completed" - Finished enrollment and follow-up
    
    **Study Type Filtering:**
    - Interventional vs. Observational
    - Treatment vs. Prevention vs. Diagnostic
    - Single-arm vs. Randomized controlled
    - Open-label vs. Blinded studies
    
    ## Advanced Search Parameters
    **Sponsor and Funding:**
    - NIH-funded studies
    - Industry-sponsored trials
    - Academic medical centers
    - International collaborations
    
    **Study Design Elements:**
    - Primary endpoint type
    - Study duration
    - Number of participants
    - Age group restrictions
    - Gender/sex requirements
    
    ## Trial Database Cross-References
    **Additional Resources:**
    - EU Clinical Trials Register (European studies)
    - WHO International Clinical Trials Registry
    - Company-specific trial databases
    - Disease-specific trial registries
    """
    
    section_type = "trials_advanced_search_strategies"
    render_slot = SectionRenderSlot.INCLUDE_ONLY


class TrialQualityAssessmentSection(BaseToolSection):
    """
    # Clinical Trial Quality Evaluation
    
    ## Study Design Assessment
    **Randomization Quality:**
    - Method of randomization clearly described
    - Allocation concealment adequate
    - Stratification factors appropriate
    - Randomization ratio justified
    
    **Blinding Evaluation:**
    - Participant blinding feasible and maintained
    - Investigator blinding appropriate
    - Outcome assessor blinding implemented
    - Blinding success monitoring planned
    
    ## Statistical Considerations
    **Sample Size and Power:**
    - Primary endpoint clearly defined
    - Effect size clinically meaningful
    - Statistical power adequate (≥80%)
    - Dropout rate assumptions reasonable
    
    **Analysis Plan:**
    - Primary analysis method pre-specified
    - Multiple comparison adjustments planned
    - Interim analysis rules defined
    - Missing data handling strategy described
    
    ## Regulatory and Ethical Quality
    **Regulatory Compliance:**
    - FDA IND (if drug/device study)
    - IRB approval documented
    - Good Clinical Practice (GCP) compliance
    - Data monitoring plan adequate
    
    **Transparency Indicators:**
    - Protocol publicly available
    - Primary endpoint registration before enrollment
    - Conflict of interest disclosures
    - Data sharing commitments
    
    ## Risk-Benefit Assessment
    **Safety Monitoring:**
    - Safety run-in phase if appropriate
    - Adverse event reporting plan
    - Data Safety Monitoring Board (DSMB) oversight
    - Stopping rules for safety/futility
    
    **Participant Burden:**
    - Visit frequency reasonable
    - Procedure invasiveness justified
    - Time commitment clearly communicated
    - Compensation appropriate for burden
    """
    
    section_type = "study_quality_assessment"
    render_slot = SectionRenderSlot.INCLUDE_ONLY


class PatientAdvocacySection(BaseToolSection):
    """
    # Patient Rights and Trial Advocacy
    
    ## Fundamental Patient Rights
    **Informed Consent Rights:**
    - Receive complete study information
    - Understand risks and benefits
    - Ask questions before deciding
    - Take time to consider participation
    - Discuss with family/healthcare providers
    
    **Participation Rights:**
    - Voluntary participation (no coercion)
    - Withdraw at any time without penalty
    - Continue regular medical care
    - Receive study results when available
    - Privacy and confidentiality protection
    
    ## Advocacy Resources
    **Patient Advocacy Organizations:**
    - Disease-specific advocacy groups
    - Clinical trial education organizations
    - Patient navigator programs
    - Peer support networks
    
    **Educational Resources:**
    - ClinicalTrials.gov educational materials
    - FDA patient information guides
    - NIH clinical trial information
    - Academic medical center resources
    
    ## Questions to Ask Investigators
    **About the Study:**
    - What is the purpose of this research?
    - What are the potential risks and benefits?
    - What procedures are involved?
    - How long will participation last?
    - What are the alternatives to participation?
    
    **About Practical Matters:**
    - How often are study visits required?
    - Will transportation be provided/reimbursed?
    - What costs will I be responsible for?
    - How will my privacy be protected?
    - Who can I contact with questions or concerns?
    
    ## Red Flags and Warning Signs
    **Concerning Practices:**
    - Pressure to enroll immediately
    - Promises of cure or guaranteed benefits
    - Requests for payment to participate
    - Inadequate informed consent process
    - Lack of contact information for questions
    - No mention of risks or side effects
    - Unrealistic claims about study benefits
    
    **When to Seek Additional Help:**
    - Contact study ombudsman
    - Reach out to IRB/ethics committee
    - Consult with independent healthcare provider
    - Contact patient advocacy organizations
    - Report concerns to regulatory authorities
    """
    
    section_type = "patient_rights_advocacy"
    render_slot = SectionRenderSlot.INCLUDE_ONLY