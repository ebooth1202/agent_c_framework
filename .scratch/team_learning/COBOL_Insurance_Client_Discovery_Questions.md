# COBOL Insurance System - Client Discovery Questions

*Prepared by Bobb the Agent Builder* 🧠⚡

## Meeting Objective
Gather comprehensive requirements to design and build an agentic team for extracting form data from COBOL-based insurance systems.

---

## 1. Current System Architecture 🏗️

### COBOL Environment
- **What COBOL platform are you using?**
  - [ ] IBM Mainframe (z/OS)
  - [ ] AS/400 (IBM i)
  - [ ] Micro Focus COBOL
  - [ ] Other: ___________

- **How is the COBOL data currently stored?**
  - [ ] VSAM files
  - [ ] DB2 database
  - [ ] Flat files
  - [ ] IMS database
  - [ ] Other: ___________

- **What is the approximate data volume?**
  - Number of records: ___________
  - Data growth rate: ___________
  - Historical data span: ___________

### Access Methods
- **How do you currently access this COBOL data?**
  - [ ] Direct mainframe access
  - [ ] FTP file transfers
  - [ ] API gateway
  - [ ] Database queries
  - [ ] Screen scraping (3270 emulation)
  - [ ] Other: ___________

- **What are the current access restrictions?**
  - Security requirements: ___________
  - Access frequency limitations: ___________
  - Time windows for access: ___________

---

## 2. Data Structure & Format 📊

### Record Layouts
- **Can you provide COPYBOOK definitions?**
  - [ ] Yes - Full COPYBOOKS available
  - [ ] Yes - Partial documentation
  - [ ] No - Must reverse engineer
  - [ ] Some - Need to be updated

- **What is the typical record structure?**
  - Fixed-length or variable-length records?
  - Hierarchical (parent-child) relationships?
  - Maximum record size: ___________

### The "Key" System
- **Describe your key structure in detail:**
  - Is it a single field or composite key?
  - Example key format: ___________
  - How many different key types exist?
  - Are keys sequential, random, or indexed?

- **Key components might include:**
  - [ ] State/Region code
  - [ ] Product type
  - [ ] Policy type
  - [ ] Customer ID
  - [ ] Date/Version
  - [ ] Coverage level
  - [ ] Other: ___________

### Data Types & Encoding
- **What COBOL data types are used?**
  - [ ] PIC X (Alphanumeric)
  - [ ] PIC 9 (Numeric)
  - [ ] COMP-3 (Packed decimal)
  - [ ] COMP (Binary)
  - [ ] OCCURS clauses (Arrays/Tables)
  - [ ] REDEFINES (Multiple layouts)

- **Character encoding:**
  - [ ] EBCDIC
  - [ ] ASCII
  - [ ] Mixed
  - [ ] Other: ___________

---

## 3. Business Logic & Rules 🎯

### Form Selection Logic
- **How are forms determined from the key?**
  - Simple 1-to-1 mapping (key → specific form)?
  - Complex business rules?
  - Conditional logic based on multiple factors?
  
- **Can you provide examples?**
  - Scenario 1: ___________
  - Scenario 2: ___________
  - Scenario 3: ___________

### Form Types & Variations
- **What types of forms exist?**
  - Total number of unique forms: ___________
  - Categories (auto, home, life, etc.): ___________
  - State-specific variations?: ___________
  - Version control/effective dating?: ___________

- **Form dependencies:**
  - Are some forms always paired together?
  - Conditional requirements (if Form A, then Form B)?
  - Exclusion rules (never Form X with Form Y)?

### Business Rules Complexity
- **What drives form selection?** (Check all that apply)
  - [ ] Insurance product type
  - [ ] Coverage amounts
  - [ ] Geographic location (state/region)
  - [ ] Customer type (individual/commercial)
  - [ ] Risk factors
  - [ ] Regulatory requirements
  - [ ] Effective dates
  - [ ] Underwriting decisions
  - [ ] Claims history
  - [ ] Other: ___________

---

## 4. Current Process & Pain Points 😤

### Existing Workflow
- **How is this data extraction currently handled?**
  - Manual process?
  - Existing programs/scripts?
  - Third-party tools?
  - Time required per extraction: ___________

- **Who currently performs this task?**
  - Technical team (programmers)?
  - Business users?
  - Combination?
  - Skillset required: ___________

### Challenges & Pain Points
- **What are the main problems with the current process?**
  - [ ] Too slow/time-consuming
  - [ ] Error-prone
  - [ ] Requires specialized COBOL knowledge
  - [ ] Difficult to maintain/update
  - [ ] Can't handle volume
  - [ ] Lack of documentation
  - [ ] Other: ___________

- **What errors commonly occur?**
  - Wrong forms selected?
  - Missing forms?
  - Data interpretation issues?
  - Examples: ___________

---

## 5. Desired Future State 🚀

### Output Requirements
- **What should the extracted data look like?**
  - [ ] JSON format
  - [ ] XML format
  - [ ] CSV/Excel
  - [ ] Database records
  - [ ] API response
  - [ ] PDF documents
  - [ ] Other: ___________

- **What information is needed in the output?**
  - [ ] Form IDs/names
  - [ ] Form descriptions
  - [ ] Form URLs/locations
  - [ ] Required/optional flags
  - [ ] Sequence/order
  - [ ] Instructions
  - [ ] Other: ___________

### Integration Needs
- **Where will this extracted data be used?**
  - Downstream system: ___________
  - User interface: ___________
  - Decision engine: ___________
  - Document generation: ___________

- **What systems need to consume this data?**
  - Modern web application?
  - Mobile app?
  - Another legacy system?
  - Reporting tools?

### Performance Requirements
- **What are your performance expectations?**
  - Response time per query: ___________
  - Queries per day/hour: ___________
  - Batch vs. real-time processing?
  - Peak load times: ___________

---

## 6. Technical Constraints & Governance 🔒

### Security & Compliance
- **What security requirements exist?**
  - [ ] PCI compliance
  - [ ] HIPAA compliance
  - [ ] SOC 2
  - [ ] State insurance regulations
  - [ ] Data encryption requirements
  - [ ] Audit trail requirements
  - [ ] Other: ___________

- **Access control needs:**
  - User authentication method?
  - Role-based access required?
  - Data masking/redaction needs?

### Technical Limitations
- **What technical constraints exist?**
  - Can't modify COBOL code?
  - Read-only access required?
  - Specific technology stack requirements?
  - Network/firewall restrictions?
  - Processing window constraints?

### Change Management
- **How often do things change?**
  - Form additions/removals frequency: ___________
  - Business rule updates: ___________
  - COBOL system updates: ___________
  - Regulatory changes: ___________

- **Change notification process:**
  - How are you notified of changes?
  - Lead time for changes?
  - Testing requirements?

---

## 7. Success Criteria & Metrics 📈

### Definition of Success
- **What would make this project successful?**
  - Primary goal: ___________
  - Secondary goals: ___________
  - Nice-to-haves: ___________

- **How will success be measured?**
  - [ ] Accuracy rate (% correct form selection)
  - [ ] Processing speed improvement
  - [ ] Error reduction
  - [ ] User satisfaction
  - [ ] Cost savings
  - [ ] Other: ___________

### Acceptance Criteria
- **What are the must-haves for acceptance?**
  - Minimum accuracy required: ___________
  - Maximum processing time: ___________
  - Specific scenarios that must work: ___________

### ROI Expectations
- **What value does this bring?**
  - Time savings: ___________
  - Cost reduction: ___________
  - Risk mitigation: ___________
  - Customer experience improvement: ___________

---

## 8. Project Logistics 📅

### Timeline
- **What's your desired timeline?**
  - Project start date: ___________
  - Go-live target: ___________
  - Any hard deadlines?: ___________
  - Phased rollout possible?: ___________

### Resources & Support
- **Who will be involved from your side?**
  - Business SMEs available?
  - Technical COBOL experts?
  - Testing resources?
  - Project manager?

- **What documentation exists?**
  - [ ] Business requirements
  - [ ] Technical specifications
  - [ ] COPYBOOK definitions
  - [ ] Sample data files
  - [ ] Business rule documentation
  - [ ] Current process flows
  - [ ] Test cases
  - [ ] Other: ___________

### Budget & Scope
- **Budget considerations:**
  - Fixed budget or flexible?
  - Cost constraints: ___________
  - Preferred pricing model: ___________

- **Scope boundaries:**
  - Start with specific product lines?
  - Pilot with certain states?
  - Proof of concept first?

---

## 9. Sample Data & Testing 🧪

### Data Availability
- **Can you provide sample data?**
  - [ ] Production data (sanitized)
  - [ ] Test data sets
  - [ ] Synthetic examples
  - [ ] Cannot provide data

- **What format can samples be provided in?**
  - Raw COBOL files?
  - Converted format?
  - Screenshots/documentation only?

### Test Scenarios
- **Can you provide test cases?**
  - Simple scenarios: ___________
  - Complex scenarios: ___________
  - Edge cases: ___________
  - Error conditions: ___________

### Validation Process
- **How will we validate the solution?**
  - Compare against current process?
  - Business user review?
  - Parallel run period?
  - Specific test suite?

---

## 10. Additional Considerations 💭

### Future Vision
- **Where do you see this going long-term?**
  - Full COBOL modernization?
  - Gradual migration strategy?
  - Permanent hybrid solution?

### Other Systems
- **Are there similar needs for other systems?**
  - Other COBOL systems?
  - Other data extraction needs?
  - Potential for expanded scope?

### Concerns or Risks
- **What concerns do you have about this project?**
  - Technical risks: ___________
  - Business risks: ___________
  - Organizational risks: ___________

### Questions for Us
- **What questions do you have about:**
  - Our approach?
  - AI/Agent capabilities?
  - Implementation process?
  - Support model?

---

## Action Items Post-Meeting

### For Client
- [ ] Provide COPYBOOK definitions
- [ ] Share sample data/test cases
- [ ] Identify SMEs for follow-up
- [ ] Provide existing documentation
- [ ] Define success metrics

### For Us
- [ ] Create solution design
- [ ] Develop agent team architecture
- [ ] Build proof of concept
- [ ] Provide timeline/cost estimate
- [ ] Schedule follow-up meeting

---

## Notes Section
*Use this space during the meeting to capture additional insights, concerns, or ideas that don't fit in the structured questions above.*

___________________________________________________________________________
___________________________________________________________________________
___________________________________________________________________________
___________________________________________________________________________
___________________________________________________________________________

---

*Pro Tips for the Meeting:*
1. **Start with the business problem** before diving into technical details
2. **Ask for examples** whenever they describe a process or rule
3. **Clarify acronyms and terminology** specific to their organization
4. **Draw diagrams** of data flow and system architecture
5. **Prioritize requirements** (must-have vs. nice-to-have)
6. **Identify quick wins** for early value demonstration
7. **Document assumptions** that need validation
8. **Get commitment** on who will be available for follow-up questions

---

*Remember: The more detail you gather now, the better your agent team design will be!* 🚀