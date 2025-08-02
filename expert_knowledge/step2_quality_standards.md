# STPA-Sec Step 2 Quality Standards

## Control Structure Requirements

### Minimum Requirements
- At least 3 components (typically more)
- At least 1 controller
- At least 1 controlled process
- Hierarchical organization (max 5 levels deep)

### Component Naming Convention
- Controllers: CTRL-N (e.g., CTRL-1, CTRL-2)
- Processes: PROC-N (e.g., PROC-1, PROC-2)
- Dual-role: DUAL-N (e.g., DUAL-1, DUAL-2)

### Required Attributes
- identifier: Unique component ID
- name: Human-readable name
- type: controller/process/dual-role
- description: What it does
- abstraction_level: service/subsystem/component

## Control Action Standards

### Required Structure
```json
{
  "identifier": "CA-N",
  "controller_id": "CTRL-X",
  "controlled_process_id": "PROC-Y",
  "action_name": "Descriptive Name",
  "action_type": "command/configuration/permission/monitoring",
  "timing_requirements": {}
}
```

### Specificity Requirements
- Specific enough to identify security impact
- Not so specific as to include parameters
- Must reference valid components only

### Examples by System Type

#### SD-WAN
- ✓ "Configure Traffic Policy"
- ✓ "Update Security Rules"
- ✗ "Set BGP Timer to 30s"

#### Web Application
- ✓ "Authenticate User"
- ✓ "Authorize Transaction"
- ✗ "Check Password Hash"

## Feedback Mechanism Standards

### Coverage Requirements
- Every control action must have feedback path
- Both success and failure feedback needed
- Timing characteristics must be specified

### Types Required
1. **Explicit Feedback**
   - Status reports
   - Acknowledgments
   - Telemetry data

2. **Implicit Feedback**
   - Timeout detection
   - Absence of errors
   - System behavior observation

### Required Attributes
```json
{
  "identifier": "FB-N",
  "source_process_id": "PROC-X",
  "target_controller_id": "CTRL-Y",
  "information_type": "status/measurement/alert/confirmation",
  "timing_characteristics": {
    "frequency": "continuous/periodic/event-driven",
    "latency_requirement": "time constraint"
  }
}
```

## Trust Boundary Standards

### Identification Criteria
1. Change in administrative control
2. Network security zone transitions
3. Authentication/authorization boundaries
4. Data classification changes

### Required Documentation
- Both sides of boundary clearly identified
- Trust direction specified
- Security controls documented
- Authentication methods defined

## Process Model Standards

### Controller Process Models Must Include
1. **State Variables**
   - What the controller tracks
   - How variables are updated
   - Staleness tolerance

2. **Update Sources**
   - Which feedback mechanisms update the model
   - Update frequency
   - Trust level of sources

3. **Assumptions**
   - What controller assumes about process behavior
   - Temporal validity assumptions
   - Trust assumptions

## Quality Scoring Rubric

### Excellent (90-100%)
- All control loops closed
- Appropriate abstraction throughout
- No undefined component references
- Trust boundaries comprehensive
- Process models complete

### Acceptable (70-89%)
- Most control loops closed
- Generally appropriate abstraction
- Few undefined references
- Key trust boundaries identified
- Core process models defined

### Needs Improvement (50-69%)
- Some control loops incomplete
- Mixed abstraction levels
- Multiple undefined references
- Missing critical trust boundaries
- Incomplete process models

### Unacceptable (<50%)
- Many open control loops
- Wrong abstraction level
- Pervasive undefined references
- No trust boundaries
- Missing process models