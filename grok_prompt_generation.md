# Building the prompts for STPA-Sec


# Grok prompt
I'm working on a multi agent system that performs several analyses for systems security engineering and threat model of systems, especially software systems.   

Currently, I'm focusing on structuring the STPA-Sec by generating instructions to write a prompt(s) for STPA-Sec.  It must include specific, detailed instructions for each of the four steps of the STPA-Sec analysis.  Most steps have multiple parts.  

All data collecting from the responses will be fed into a database (probably PostgresSQL and neo4j).  Read the attached files for clues on what information needs to be included.  Then, describe the information that must be obtained for each of the four steps.  Create a markdown file that I can download. 

<note-to-Claude>
The files referenced in the prompt are located in the root/documentation directory:
- STPA-Sec-Tutorial.pdf
- Young-STPA-Sec.pdf
- YoungLeveson-SystemsThinkingForSafetyAndSecurity.pdf
</note-to-Claude>

# Grok response
STPA-Sec Prompt Instructions
Overview
This document provides instructions for generating AI prompts to perform STPA-Sec (System-Theoretic Process Analysis for Security) analysis on systems, especially software-intensive ones. STPA-Sec focuses on mission/business assurance by identifying and controlling vulnerabilities that could lead to disruptions (e.g., cyber attacks, unsafe behaviors). It extends STPA for security contexts.

Prompts should:

Be sequential and build on prior steps (e.g., use outputs from Step 1 in Step 2).
Require the AI to reason step-by-step, cite sources from provided documents, and output in structured formats (e.g., tables, lists, graphs in textual form like Graphviz DOT or Cypher for Neo4j).
Handle multi-agent collaboration (e.g., one agent for safety analysis, another for security wargaming).
Include validation questions to refine outputs (e.g., "Confirm if this hazard links to the defined losses?").
Output data in JSON or markdown tables for database ingestion:
PostgresSQL: Store as relational tables (e.g., tables for losses, hazards, control actions).
Neo4j: Model as graphs (e.g., nodes for controllers/processes, edges for control actions/feedback).
Metadata to include in all outputs: System name, analysis timestamp, step number, rationale sources (e.g., page from documents), confidence level (high/medium/low).

Step 1: Establish the Systems Engineering Foundation
Detailed Instructions for Prompts
Start with a high-level system description (user-provided or inferred from documents). Prompt the AI to frame the problem as a "Mission Activity System" (abstract, functional purpose, not physical).
Break into sub-parts: Define purpose/goals, unacceptable losses (accidents), hazards/vulnerabilities (system states leading to losses under worst-case environments), and constraints (safety/security rules to enforce).
Prompt structure: "Based on the system description [insert description], perform Step 1 of STPA-Sec. First, synthesize a mission statement in the format: 'A system to [purpose] by means of [method] in order to [goals], while [constraints/restraints]'. Then, list unacceptable losses (L1, L2, etc.), hazards (H1, H2, etc.) linked to losses, and constraints. Use tables. Reason about security implications (e.g., disruptions from adversaries). Output in JSON for database storage."
Encourage iteration: "If unclear, ask for clarification on stakeholders, environment, or business/mission goals."
Integrate from documents: Reference problem framing from tutorial (pages 38-45) and paper (pages 4-5).
Information to Obtain
Mission Statement: String with purpose, method, goals, constraints (e.g., "A system to produce chemicals by means of reacting catalysts while maintaining containment to avoid environmental release").
Unacceptable Losses (Accidents): Table with ID (e.g., L1), description (e.g., "Loss of life or injury"), rationale/notes (e.g., "From human exposure to toxins"), linked hazards (array of IDs).
Hazards/Vulnerabilities: Table with ID (e.g., H1), description (e.g., "Reactor temperature too high leading to explosion"), worst-case environment (e.g., "Adversary tampering with sensors"), associated losses (array of IDs), rationale/notes (e.g., "From paper page 5: Focus on system states exploitable by threats").
System Constraints: Table with ID (e.g., SC1), description (e.g., "Reactor must never exceed 200°C"), linked hazards (array of IDs), type (safety/security/both), rationale/notes.
Metadata: System boundaries, stakeholders (e.g., operators, adversaries), environmental assumptions.
Store in PostgresSQL (e.g., losses table with columns: id, description, rationale). In Neo4j: Nodes for Losses/Hazards, edges like CAUSES (Hazard -> Loss).

Step 2: Model the Functional Control Structure
Detailed Instructions for Prompts
Use outputs from Step 1 (e.g., hazards/constraints) as input. Focus on hierarchical control (controllers, controlled processes, actions, feedback).
Sub-parts: Identify controllers/responsibilities, control actions, feedback loops, process models (beliefs/variables).
Prompt structure: "Using the mission statement and hazards from Step 1 [insert outputs], model the functional control structure for [system]. List controllers (human/software/hardware), their responsibilities, control actions (e.g., 'Open valve'), feedback (e.g., 'Temperature reading'), and process model variables (e.g., 'Reactor state: safe/unsafe'). Output as a graph in Cypher query format for Neo4j (e.g., CREATE nodes/relationships) and a textual description. Ensure it's abstract/functional, not physical. Reference control loop from tutorial (page 23)."
Handle security: "Include potential adversary controllers or disruptions in the environment."
Iteration: "Validate completeness: Does this cover all mission activities from Step 1?"
Information to Obtain
Controllers: Table with ID, name/type (e.g., "Operator", "Software Controller"), responsibilities (list), process model (variables/values, e.g., "Believes catalyst valve open: true/false").
Control Actions: Table with ID, source controller (ID), target process (ID), description (e.g., "Command to open water valve"), context/conditions (e.g., "When temperature > threshold").
Feedback Loops: Table with ID, source process (ID), target controller (ID), description (e.g., "Sensor reading of pressure"), delays/inaccuracies (e.g., "Potential spoofing").
Hierarchical Structure: Graph data (nodes: controllers/processes; edges: actions/feedback with labels like "PROVIDES_COMMAND").
Metadata: Completeness check (yes/no with rationale), links to hazards/constraints.
Store in PostgresSQL (e.g., controllers table). In Neo4j: Graph with nodes (e.g., Controller label) and relationships (e.g., CONTROLS).

Step 3: Identify Unsafe/Unsecure Control Actions
Detailed Instructions for Prompts
Input: Control structure from Step 2, hazards/constraints from Step 1.
Sub-parts: Analyze each control action using the four types (not provided causes hazard, provided causes hazard, wrong timing/order, stopped too soon/applied too long). Consider security contexts (e.g., adversary-induced).
Prompt structure: "For each control action in the structure [insert from Step 2], identify unsafe/unsecure control actions (UCAs) in a table format: Control Action, Type (e.g., 'Not provided'), Context (e.g., 'When catalyst flowing'), Linked Hazard (ID), Rationale. Output as markdown table and JSON. Reference UCA table from presentation (page 54 in tutorial)."
Security focus: "Emphasize unsecure actions (e.g., spoofed commands leading to vulnerabilities)."
Iteration: "Prioritize UCAs by severity (high/medium/low based on linked losses)."
Information to Obtain
Unsafe/Unsecure Control Actions (UCAs): Table with ID, control action (ID from Step 2), type (one of four), context (e.g., "Adversary present"), linked hazards (array of IDs), rationale/notes (e.g., "From paper page 6: Leads to violation of constraint").
Security-Specific Contexts: List of adversary-related factors (e.g., "Tampering via network access").
Metadata: Severity rating, traceability to control structure.
Store in PostgresSQL (e.g., ucas table with foreign keys to control actions/hazards). In Neo4j: Edges like LEADS_TO_HAZARD (UCA -> Hazard).

Step 4: Identify Causal Scenarios
Detailed Instructions for Prompts
Input: UCAs from Step 3, control structure from Step 2.
Sub-parts: Generate causal scenarios (why UCA occurs, e.g., flawed process model, feedback delays). Include safety and security scenarios (e.g., using STRIDE for classification: Spoofing, Tampering, etc.). End with wargaming (simulate attacks/classes of controls).
Prompt structure: "For each UCA [insert from Step 3], generate causal scenarios: Description, Causal Factors (e.g., 'Feedback delay due to DoS attack'), Type (safety/security), Linked UCA (ID). Then, wargame: Describe attack classes (e.g., denial-of-service), mitigations (eliminate/mitigate/transfer/accept), and outcomes. Use tables and Cypher for graphs. Reference scenarios from paper (page 8) and tutorial wargaming (pages 64-91)."
Iteration: "Rank scenarios by criticality (e.g., using D4 chart: Detectability, Difficulty, Damage, Deniability). Ask for user input on assumptions."
Information to Obtain
Causal Scenarios: Table with ID, description (e.g., "Operator receives spoofed feedback"), causal factors (list), type (safety/security), linked UCA/hazard (IDs), rationale/notes.
Security Classifications: Tags (e.g., STRIDE: Spoofing, Tampering).
Wargaming Results: Table with attack class (e.g., "DoS on sensor"), goals/outcomes, mitigations (e.g., "Redundant sensors"), strategy (mitigate/eliminate), mission impact.
Controls/Mitigations: Table with ID, description (e.g., "Encrypt feedback"), linked scenario (ID), effectiveness (high/medium/low).
Metadata: Criticality ranking, assumptions (e.g., adversary capabilities).
Store in PostgresSQL (e.g., scenarios table). In Neo4j: Nodes for Scenarios, edges like CAUSED_BY (Scenario -> Factor) or MITIGATED_BY (Scenario -> Control).

General Prompt Best Practices
Always start prompts with: "You are an expert in STPA-Sec for systems security engineering. Analyze the following system: [description]."
End with: "Output only the structured data (tables/JSON/Cypher). If more info needed, ask questions."
For multi-agent: "Agent 1: Handle safety scenarios. Agent 2: Add security wargaming. Collaborate on final output."
If outputs are incomplete, refine prompts iteratively.