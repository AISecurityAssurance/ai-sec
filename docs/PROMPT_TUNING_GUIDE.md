# STPA-Sec Prompt Tuning Guide

## Overview
This guide documents best practices for tuning STPA-Sec analysis prompts while maintaining domain independence.

## Core Principle: Domain Agnosticism
The system must work equally well for ANY domain - medical drones, banking, manufacturing, space systems, etc. Avoid hard-coding domain-specific categories or examples.

## Prompt Improvement Strategies

### 1. Universal Categories Instead of Domain-Specific
**BAD (Domain-Specific):**
```
□ Navigation/Positioning (GPS, compass)
□ Power Systems (battery, charging)
□ Flight Control (motors, sensors)
```

**GOOD (Universal):**
```
□ Data/Information Integrity
□ Resource Availability
□ Control/Command Authority
```

### 2. Systematic Questions Over Prescriptive Lists
Instead of telling the system what hazards to find, ask questions that guide discovery:

- What system states could lead to each identified loss?
- What dangerous states could each component enter?
- What if each external dependency fails?
- What states would violate the primary mission?

### 3. Context Extraction
Have the system extract domain-specific elements FROM the description:
```
1. Identify PRIMARY FUNCTIONS mentioned
2. Identify CRITICAL RESOURCES described
3. Identify ENVIRONMENTAL FACTORS noted
4. Map these to hazard categories
```

### 4. Completeness Through Verification
Rather than prescriptive minimums, use verification questions:
- Does every stakeholder have relevant losses?
- Are all system functions covered by hazards?
- Are all boundaries properly defined?

### 5. Quality Metrics Without Domain Bias

**Quantitative Checks:**
- Minimum counts (12+ hazards, 8+ stakeholders)
- Coverage ratios (hazards per loss, constraints per hazard)
- Boundary completeness (elements per boundary)

**Qualitative Checks:**
- Diversity of hazard types
- Multi-stakeholder impact consideration
- Cascading effect identification

## Example Improvements

### Before (Banking-Biased):
"Consider transaction integrity, payment processing, customer data"

### After (Domain-Agnostic):
"Consider data integrity for critical system operations"

## Testing Domain Independence
To verify prompts are truly domain-agnostic:

1. Test with diverse systems:
   - Medical devices
   - Aerospace systems
   - Manufacturing plants
   - Social media platforms

2. Check for inappropriate content:
   - Banking terms in medical analysis
   - Aviation terms in financial analysis
   - Medical terms in manufacturing analysis

3. Verify appropriate adaptation:
   - Life safety prioritized for medical
   - Financial integrity prioritized for banking
   - Mission success prioritized for aerospace

## Continuous Improvement Process

1. **Collect Feedback**: Note when analyses miss domain-specific concerns
2. **Abstract the Pattern**: Find the universal principle behind the miss
3. **Update Prompts**: Add guidance using universal language
4. **Test Broadly**: Verify improvement works across domains
5. **Document Learning**: Update this guide with insights

## Red Flags to Avoid

- Hard-coded industry terms
- Prescriptive category lists
- Domain-specific examples in base prompts
- Assumptions about system type
- Fixed stakeholder roles

## Success Indicators

- Analyses accurately reflect system description
- Domain experts recognize their concerns
- No inappropriate cross-domain terminology
- Comprehensive coverage without prompting
- Natural use of system's own language