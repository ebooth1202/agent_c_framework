"""
FDA Tools Section - Reimagined with Selective Rendering
Provides progressive disclosure for FDA drug information searches.
"""

from agent_c.models.prompts import BaseToolSection, SectionRenderSlot

class FDAToolsSection(BaseToolSection):
    """
    # FDA Drug Information Tool
    
    You can search the FDA's National Drug Code (NDC) database for official drug information.
    
    ## Basic Drug Search
    Use `get_drug_info(generic_name="drug_name", limit=5)` to find FDA-registered drug information.
    
    {{ collapsible('fda_search_examples',
       '## Search Examples:\n- `get_drug_info(generic_name="ibuprofen", limit=3)` - Find ibuprofen products\n- `get_drug_info(generic_name="metformin", limit=5)` - Find metformin formulations\n- `get_drug_info(generic_name="lisinopril")` - Find all lisinopril products\n\n**Search Tips:**\n- Use generic names (not brand names) for best results\n- Limit results for focused searches\n- Check multiple spellings if no results found',
       'FDA search examples and best practices available') }}
    
    ## Safety Information
    {{ switch_on_state('query_type_machine',
                      drug_interaction='**DRUG INTERACTION RESEARCH**: Cross-reference with other medications. FDA data shows official formulations but may not include all interaction warnings.',
                      side_effects='**SIDE EFFECT RESEARCH**: FDA database contains official labeling information. Always cross-reference with clinical literature for comprehensive adverse event data.',
                      dosage_inquiry='**DOSAGE INFORMATION**: FDA data provides official dosing from drug labels. Individual dosing should always be determined by healthcare providers.',
                      default='**GENERAL DRUG RESEARCH**: FDA database provides official drug registration and labeling information.') }}
    
    ## Advanced FDA Features
    {{ collapsible_section('fda_advanced_search',
                           'fda/advanced_search_techniques',
                           'Advanced FDA search techniques and data interpretation available') }}
    
    {{ collapsible_section('fda_data_interpretation',
                           'fda/data_quality_assessment', 
                           'FDA data interpretation and quality assessment guidelines available') }}
    
    ## Professional vs Patient Guidance
    {{ switch_on_state('user_expertise_machine',
                      healthcare_professional='**Professional Note**: FDA NDC data includes DEA schedules, NDC numbers, and regulatory classifications. Cross-reference with FDA Orange Book for therapeutic equivalence.',
                      researcher='**Research Note**: FDA database provides regulatory approval data, labeling information, and manufacturing details useful for drug research.',
                      patient='**Patient-Friendly**: This tool searches official FDA drug registration data. Information found here represents what the FDA has approved, but always consult healthcare providers for personal medical decisions.',
                      default='FDA database contains official U.S. drug registration and approval information.') }}
    
    {{ collapsible('fda_data_fields',
       '## FDA Data Fields Explained:\n- **Generic Name**: Official drug ingredient name\n- **Brand Name**: Commercial product name\n- **NDC Number**: National Drug Code (unique identifier)\n- **Dosage Form**: Tablet, capsule, injection, etc.\n- **Route**: How drug is administered (oral, IV, topical)\n- **Marketing Status**: Active, discontinued, etc.\n- **DEA Schedule**: Controlled substance classification\n- **Labeler**: Company that markets the drug\n\n*Use `toggle(fda_data_fields)` to hide field explanations.*',
       'FDA database field explanations available') }}
    
    ## Emergency and Safety Protocols
    {% if toggle('emergency_drug_protocols') == 'open' %}
    ### Emergency Drug Situations:
    - **Overdose Concerns**: FDA data alone insufficient - direct to poison control (1-800-222-1222)
    - **Severe Reactions**: FDA adverse event reporting exists but emergency care takes priority
    - **Drug Recalls**: Check FDA recalls database separately from NDC database
    - **Contamination**: FDA maintains separate databases for drug quality issues
    
    *Use `toggle(emergency_drug_protocols)` to hide emergency protocols.*
    {% else %}
    Emergency drug safety protocols available - *Use `toggle(emergency_drug_protocols)` to display.*
    {% endif %}
    """
    
    section_type = "fda_tools"
    render_slot = SectionRenderSlot.TOOL


class FDAAdvancedSearchSection(BaseToolSection):
    """
    # Advanced FDA Search Techniques
    
    ## Search Strategy Optimization
    - **Generic Name Variations**: Try both salt forms (e.g., "metformin" vs "metformin hydrochloride")
    - **Partial Matching**: FDA search supports partial generic names
    - **Combination Drugs**: Search individual components separately
    
    ## Data Quality Assessment
    - **Marketing Status**: Check if drug is currently marketed
    - **Approval Date**: Consider recency of FDA approval
    - **Labeler Information**: Verify manufacturer credibility
    
    ## Cross-Reference Strategies
    - **Orange Book**: For therapeutic equivalence (generic substitution)
    - **Purple Book**: For biosimilar products
    - **FDA Recalls**: For safety alerts and recalls
    - **Adverse Event Reports**: For post-market safety data
    
    ## Research Integration
    - Use FDA data as regulatory baseline
    - Cross-reference with PubMed for clinical evidence
    - Check clinical trials for ongoing research
    - Verify with professional drug references
    """
    
    section_type = "fda_advanced_search_techniques"
    render_slot = SectionRenderSlot.INCLUDE_ONLY


class FDADataQualitySection(BaseToolSection):
    """
    # FDA Data Quality Assessment
    
    ## Understanding FDA Database Limitations
    - **Regulatory Focus**: FDA data reflects approval status, not clinical effectiveness
    - **Labeling Lag**: Package inserts may not reflect latest research
    - **Generic Variations**: Multiple manufacturers may have different inactive ingredients
    
    ## Data Reliability Indicators
    - **Marketing Status**: "Active" indicates currently marketed
    - **Recent Updates**: Check when labeling was last revised
    - **Multiple Entries**: Compare across different manufacturers
    
    ## Professional Interpretation Guidelines
    - FDA approval ≠ clinical superiority
    - NDC numbers change with formulation changes
    - Discontinued status may indicate safety concerns or market factors
    - DEA schedules reflect abuse potential, not clinical efficacy
    
    ## Integration with Clinical Decision-Making
    - Use FDA data for regulatory compliance
    - Cross-reference with clinical guidelines
    - Consider patient-specific factors beyond FDA labeling
    - Verify current prescribing information with healthcare providers
    """
    
    section_type = "fda_data_quality_assessment"
    render_slot = SectionRenderSlot.INCLUDE_ONLY