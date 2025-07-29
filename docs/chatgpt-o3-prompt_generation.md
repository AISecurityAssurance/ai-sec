# Building the prompts for STPA-Sec


# ChatGPT-o3 prompt
I'm working on a multi agent system that performs several analyses for systems security engineering and threat model of systems, especially software systems.   

Currently, I'm focusing on structuring the STPA-Sec by generating instructions to write a prompt(s) for STPA-Sec.  It must include specific, detailed instructions for each of the four steps of the STPA-Sec analysis.  Most steps have multiple parts.  

All data collecting from the responses will be fed into a database (probably PostgresSQL and neo4j).  Read the attached files for clues on what information needs to be included.  Then, describe the information that must be obtained for each of the four steps.  Create a markdown file that I can download. 

<note-to-Claude>
The files referenced in the prompt are located in the root/documentation directory:
- STPA-Sec-Tutorial.pdf
- Young-STPA-Sec.pdf
- YoungLeveson-SystemsThinkingForSafetyAndSecurity.pdf
</note-to-Claude>


# ChatGPT-o3 response
content = """# STPA‑Sec Prompt Data Requirements

This template lists **all information your agents must collect** (or pre‑populate) to execute a complete four‑step STPA‑Sec analysis and store results in Postgres/Neo4j.  
Fields are organised by analysis step; feel free to adapt names to your schema. Every record should carry a unique identifier so downstream artefacts can be traced back to their source step/element.

---

## Step 1 – Problem Framing & Purpose Definition
| Field | Description | Notes |
|-------|-------------|-------|
| **analysis_id** | Primary key for this STPA‑Sec run | |
| **mission_purpose** | One‑sentence statement of what the system is supposed to do and why |  |
| **system_description** | High‑level narrative of the system, boundaries and operating environment |  |
| **stakeholders** | List of roles/organisations with security, safety or mission equity |  |
| **unacceptable_losses** | Enumerated list of losses/accidents (L1…Ln) the stakeholders do not tolerate | e.g. loss of life, loss of CPI fileciteturn2file2L12-L19 |
| **system_hazards** | States/conditions (H1…Hn) that can lead to the losses |  |
| **high‑level_constraints** | Preliminary safety/security constraints that must hold to prevent each hazard |  |
| **assumptions** | Known assumptions or external dependencies |  |
| **sources** | Documents, SMEs, standards referenced |  |

> *Rationale: Problem framing is required before any progress can be made* fileciteturn2file3L22-L30

---

## Step 2 – Model the Functional Control Structure
| Field | Description | Notes |
|-------|-------------|-------|
| **cs_id** | Identifier of the control‑structure model (can map to Neo4j graph) | |
| **controllers** | List of controllers (human, software, organisational) | Include internal *process model* attributes |
| **controlled_processes** | Physical/virtual processes under control | |
| **actuators & sensors** | Hardware/software interfaces for control & feedback | |
| **control_actions** | Enumerated actions each controller can issue | |
| **feedback_channels** | Signals/paths providing state info back to controllers | |
| **interface_constraints** | Known limits, protocols, timing budgets | |
| **diagrams_uri** | Link/path to architecture or HLCS diagram captured | HLCS example shows five key components fileciteturn2file4L51-L67 |

---

## Step 3 – Identify Unsafe/Unsecure Control Actions (UCAs)
For **every control action** from Step 2 capture:

| Field | Description | Notes |
|-------|-------------|-------|
| **uca_id** | Unique UCA identifier, foreign key to `control_actions` | |
| **hazard_type** | One of four patterns:<br>1. *Provided causes hazard*<br>2. *Not provided causes hazard*<br>3. *Wrong timing/order*<br>4. *Applied too long/too short* | Derived from STPA‑Sec guidance fileciteturn2file5L113-L122 |
| **context_conditions** | Specific state(s) of the system/environment that make the control action unsafe | |
| **linked_hazards** | Hazard IDs this UCA can trigger | |
| **preliminary_constraints** | Constraint statements to eliminate/mitigate the UCA | |

---

## Step 4 – Identify Loss (Causal) Scenarios
For each UCA explore how it could occur:

| Field | Description | Notes |
|-------|-------------|-------|
| **scenario_id** | Unique identifier, links back to `uca_id` | |
| **cause_category** | Control‑loop problem or vulnerability exploited (e.g., incorrect process model, missing feedback, controller algorithm flaw, comms delay, malicious code) | “Clues” list guides analysis fileciteturn2file1L47-L53 |
| **scenario_description** | Narrative of events from initiating cause to loss | Example shows operator receives wrong rupture status fileciteturn2file8L11-L19 |
| **attack_surface** | Assets/links that must be compromised (for security scenarios) | |
| **severity_estimate** | Qualitative or quantitative impact on mission | |
| **likelihood_notes** | Rationale if the scenario is plausible given current design | |
| **mitigation_candidates** | Potential controls (requirements, design features, procedures) | |
| **d4_coordinates** | If using D4 chart, X/Y values for prioritisation | |

---

## Cross‑cutting Metadata
- **traceability_links**: parent/child relationships between losses, hazards, UCAs, scenarios and resulting requirements.  
- **source_evidence**: original evidence (lines, files, interviews) supporting each entry.  
- **versioning**: timestamps & analyst IDs for auditability.

---

### How to Use This Template

1. **Instantiate** a new `analysis_id` for the system under study.  
2. **Populate Step 1** fields through stakeholder workshops and document review.  
3. **Derive HLCS** for Step 2 and record every control/feedback link.  
4. **Systematically evaluate** each control action against the four UCA patterns; store results in Step 3.  
5. **Generate scenarios** by walking control‑loop “clues”, wargaming adversary actions, and associating them with UCAs in Step 4.  
6. **Feed** constraints and mitigation candidates back into system requirements & architecture.

Keeping these tables in Postgres (for relational integrity) while mapping entities/relations into Neo4j will let your agents run graph queries to trace from a candidate attack back to mission loss, or to find all hazards mitigated by a given control.

