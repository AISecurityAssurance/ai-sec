# STPA-Sec Core Principles

## 1. Control Structure Hierarchy
- Higher levels have authority over lower levels
- Controllers make decisions and issue commands
- Controlled processes execute actions
- Dual-role components both control and are controlled

## 2. Control Loop Completeness
**Every control action MUST have corresponding feedback**
- Explicit feedback: Status reports, telemetry, confirmations
- Implicit feedback: Absence of expected response, timeouts
- Both positive and error signals required

## 3. Abstraction Level Guidelines

### Service-Level Abstraction (Correct)
- SD-WAN Controller (not individual policy engines)
- Edge Gateway (not routing modules)
- Authentication Service (not user database)

### Too Detailed (Avoid)
- Individual policy rules
- Specific routing algorithms
- TCP timeout settings
- Database tables

### Too Generic (Avoid)
- "Network"
- "Security System"
- "Management"

## 4. Control Action Specificity

### Good Examples
- "Configure Traffic Routing Policy"
- "Update Security Policy Rules"
- "Authorize Network Access"
- "Deploy Configuration Update"

### Bad Examples
- "Configure Network" (too generic)
- "Manage Security" (too broad)
- "Update Routing Table Entry 192.168.1.0/24" (too specific)

## 5. Trust Boundary Identification

### Primary Criteria
1. Administrative domains - different organizations/authorities
2. Security zones - different privilege levels
3. Network segmentation - different security perimeters

### Secondary Criteria
4. Data classification levels - when data sensitivity changes
5. Authentication boundaries - where identity verification occurs

## 6. Process Model Requirements

### Essential Elements
- State variables the controller tracks
- Update mechanisms and frequencies
- Assumptions about the controlled process

### Security-Critical Additions
- Trust assumptions about information sources
- Authority scope beliefs
- Temporal validity of information

## 7. Component Inference Rules

### Permitted Inference
- Components clearly implied by control actions
- Missing controllers for identified processes
- Implied feedback sources

### Required Documentation
- Inference must be documented and justified
- Inferred components validated in next iteration
- Cannot exceed system scope from Step 1
- Must maintain appropriate abstraction level