"""
PubMed Tools Section - Reimagined with Selective Rendering
Provides adaptive research guidance with evidence quality assessment.
"""

from agent_c.models.prompts import BaseToolSection, SectionRenderSlot

class PubMedToolsSection(BaseToolSection):
    """
    # PubMed Research Tool
    
    You can search PubMed's database of biomedical literature for peer-reviewed research articles.
    
    ## Basic Article Search
    Use `get_articles(query="search terms", max_results=10)` to find relevant medical literature.
    
    {{ collapsible('pubmed_search_examples',
       '## Search Examples:\n- `get_articles(query="migraine prevention", max_results=5)` - Find migraine prevention studies\n- `get_articles(query="diabetes metformin efficacy", max_results=10)` - Research on metformin effectiveness\n- `get_articles(query="hypertension lifestyle interventions")` - Lifestyle approaches to blood pressure\n\n**Search Strategy Tips:**\n- Use medical terminology (MeSH terms) for precise results\n- Combine condition + intervention + outcome\n- Add "systematic review" or "meta-analysis" for highest evidence\n- Use quotation marks for exact phrases',
       'PubMed search examples and strategy tips available') }}
    
    ## Research Context Adaptation
    {{ switch_on_state('query_type_machine',
                      symptom_inquiry='**SYMPTOM RESEARCH**: Focus on diagnostic studies, prevalence data, and differential diagnosis research. Prioritize systematic reviews and clinical guidelines.',
                      treatment_research='**TREATMENT RESEARCH**: Emphasize randomized controlled trials, systematic reviews, and clinical practice guidelines. Assess study quality and clinical relevance.',
                      drug_interaction='**DRUG INTERACTION RESEARCH**: Search for pharmacokinetic studies, case reports, and drug interaction databases. Cross-reference with clinical pharmacology literature.',
                      side_effects='**ADVERSE EFFECT RESEARCH**: Focus on pharmacovigilance studies, case series, and post-market surveillance data. Include both common and rare adverse events.',
                      default='**GENERAL MEDICAL RESEARCH**: Comprehensive literature search across study types. Prioritize high-quality evidence and recent publications.') }}
    
    ## Evidence Quality Assessment
    {{ collapsible('evidence_hierarchy',
       '## Evidence Quality Hierarchy:\n1. **Systematic Reviews & Meta-analyses** - Highest quality synthesis\n2. **Randomized Controlled Trials (RCTs)** - Gold standard for interventions\n3. **Cohort Studies** - Good for outcomes and prognosis\n4. **Case-Control Studies** - Useful for rare conditions\n5. **Case Series/Reports** - Lowest quality, hypothesis-generating\n\n**Quality Indicators:**\n- Sample size and statistical power\n- Study design appropriateness\n- Conflict of interest disclosures\n- Peer review status\n- Journal impact factor and reputation',
       'Evidence quality hierarchy and assessment criteria available') }}
    
    ## User Expertise Adaptation  
    {{ switch_on_state('user_expertise_machine',
                      healthcare_professional='**Professional Research**: Focus on clinical applicability, study methodology, and practice-changing evidence. Include confidence intervals, effect sizes, and clinical significance.',
                      researcher='**Academic Research**: Emphasize methodology, statistical analysis, study limitations, and research gaps. Include bibliometric data and citation analysis.',
                      patient='**Patient-Friendly Research**: Translate findings into understandable terms. Focus on practical implications, safety data, and patient-relevant outcomes. Always emphasize professional consultation.',
                      default='Provide balanced research summary with clear methodology explanation and clinical relevance.') }}
    
    ## Advanced Research Features
    {{ collapsible_section('pubmed_advanced_search',
                           'pubmed/advanced_search_strategies',
                           'Advanced PubMed search techniques and MeSH term usage available') }}
    
    {{ collapsible_section('study_quality_assessment',
                           'research/study_quality_evaluation',
                           'Comprehensive study quality assessment frameworks available') }}
    
    {{ collapsible_section('research_synthesis',
                           'research/evidence_synthesis_methods',
                           'Evidence synthesis and research integration methods available') }}
    
    ## Research Limitations and Disclaimers
    {% if toggle('research_limitations') == 'open' %}
    ### Important Research Limitations:
    - **Publication Bias**: Positive results more likely to be published
    - **Study Populations**: Results may not generalize to all patients
    - **Temporal Factors**: Medical knowledge evolves rapidly
    - **Access Limitations**: Some studies behind paywalls
    - **Language Bias**: English-language preference in database
    - **Funding Bias**: Industry-sponsored studies may have conflicts
    
    **Critical Appraisal Checklist:**
    ☐ Study design appropriate for research question
    ☐ Sample size adequate for conclusions
    ☐ Control groups properly matched
    ☐ Outcome measures clinically relevant
    ☐ Statistical analysis appropriate
    ☐ Conflicts of interest disclosed
    ☐ Results clinically significant (not just statistically)
    
    *Use `toggle(research_limitations)` to hide research limitations.*
    {% else %}
    Research limitations and critical appraisal guidelines available - *Use `toggle(research_limitations)` to display.*
    {% endif %}
    """
    
    section_type = "pubmed_tools"
    render_slot = SectionRenderSlot.TOOL


class PubMedAdvancedSearchSection(BaseToolSection):
    """
    # Advanced PubMed Search Strategies
    
    ## MeSH Term Optimization
    - **Medical Subject Headings (MeSH)**: Use controlled vocabulary for precision
    - **Subheadings**: Narrow focus with /therapy, /diagnosis, /epidemiology
    - **Explosion**: Include narrower terms automatically with [MeSH:exp]
    - **Major Topic**: Focus on primary subject with [MeSH Major Topic]
    
    ## Search Operators and Filters
    - **Boolean Logic**: AND, OR, NOT for complex queries
    - **Field Tags**: [ti] for title, [au] for author, [dp] for publication date
    - **Publication Types**: [pt] for systematic review, randomized controlled trial
    - **Date Ranges**: ("2020"[Date - Publication] : "2024"[Date - Publication])
    
    ## Study Type Targeting
    - **Therapeutic Questions**: Add "randomized controlled trial"[pt]
    - **Diagnostic Questions**: Add "sensitivity and specificity"[MeSH]
    - **Prognostic Questions**: Add "cohort studies"[MeSH] OR "follow-up studies"[MeSH]
    - **Etiology Questions**: Add "case-control studies"[MeSH] OR "cohort studies"[MeSH]
    
    ## Quality Filters
    - **Cochrane Reviews**: Add "cochrane database syst rev"[ta]
    - **High-Impact Journals**: Add journal name filters
    - **Recent Evidence**: Limit to last 5 years for rapidly evolving fields
    - **Human Studies**: Add "humans"[MeSH] to exclude animal studies
    
    ## Search Strategy Development
    1. **PICO Framework**: Patient/Population, Intervention, Comparison, Outcome
    2. **Synonym Identification**: List alternative terms for each concept
    3. **MeSH Term Mapping**: Use PubMed's MeSH database to find optimal terms
    4. **Search Combination**: Use OR within concepts, AND between concepts
    5. **Results Refinement**: Adjust based on initial results relevance
    """
    
    section_type = "pubmed_advanced_search_strategies"
    render_slot = SectionRenderSlot.INCLUDE_ONLY


class StudyQualityAssessmentSection(BaseToolSection):
    """
    # Study Quality Evaluation Framework
    
    ## Randomized Controlled Trials (RCTs)
    **CONSORT Checklist Key Elements:**
    - Randomization method clearly described
    - Allocation concealment adequate
    - Blinding of participants and investigators
    - Intention-to-treat analysis performed
    - Complete outcome data reported
    - Selective reporting avoided
    
    ## Systematic Reviews and Meta-analyses
    **PRISMA Guidelines Assessment:**
    - Comprehensive search strategy documented
    - Study selection criteria clearly defined
    - Risk of bias assessment performed
    - Heterogeneity appropriately assessed
    - Publication bias evaluated
    - Confidence in cumulative evidence rated
    
    ## Observational Studies
    **STROBE Statement Elements:**
    - Study design clearly described
    - Setting and participants well-defined
    - Variables and data sources specified
    - Bias sources addressed
    - Statistical methods appropriate
    - Limitations acknowledged
    
    ## Critical Appraisal Questions
    **Validity Assessment:**
    - Is the research question clearly focused?
    - Is the study design appropriate?
    - Are the methods sufficiently detailed?
    - Are the results believable?
    - Are the conclusions justified?
    
    **Clinical Relevance:**
    - Are the participants representative?
    - Are the outcomes clinically important?
    - Are the results applicable to practice?
    - Are benefits worth the harms/costs?
    """
    
    section_type = "study_quality_evaluation"
    render_slot = SectionRenderSlot.INCLUDE_ONLY


class EvidenceSynthesisSection(BaseToolSection):
    """
    # Evidence Synthesis and Integration Methods
    
    ## Systematic Approach to Evidence Review
    1. **Question Formulation**: Use PICO framework for focused questions
    2. **Search Strategy**: Comprehensive, reproducible search across databases
    3. **Study Selection**: Transparent inclusion/exclusion criteria
    4. **Quality Assessment**: Standardized risk of bias evaluation
    5. **Data Extraction**: Systematic collection of relevant data
    6. **Synthesis**: Narrative or quantitative (meta-analysis) combination
    
    ## Levels of Evidence Integration
    **Individual Study Level:**
    - Internal validity assessment
    - External validity evaluation
    - Clinical significance determination
    
    **Body of Evidence Level:**
    - Consistency across studies
    - Precision of effect estimates
    - Directness of evidence
    - Publication bias assessment
    
    **Clinical Application Level:**
    - Patient population relevance
    - Intervention feasibility
    - Outcome importance to patients
    - Resource considerations
    
    ## Conflicting Evidence Resolution
    **When Studies Disagree:**
    - Examine study quality differences
    - Consider population variations
    - Assess intervention differences
    - Evaluate outcome measurement
    - Check for temporal trends
    
    **Synthesis Strategies:**
    - Weight by study quality
    - Subgroup analysis by population
    - Sensitivity analysis excluding outliers
    - Narrative synthesis when meta-analysis inappropriate
    """
    
    section_type = "evidence_synthesis_methods"
    render_slot = SectionRenderSlot.INCLUDE_ONLY