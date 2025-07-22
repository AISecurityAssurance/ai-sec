# Backend Ideas 

# Colleague's ask
A couple of things we can think about adding:
For the testing arena I like the idea of testing multiple variants but I also think it could be call if you could switch the backing LLM you were testing with. Maybe we keep that as a separate option so it doesn't get confusing

In the same vein as the variants it would be cool if we had a versioning system so that the analysis could be realtime, within a couple of seconds after submitting. That way you could also version the inputs and the threat models. For that as well we would need like a beginning flow which is where you upload your architecture diagram, textual description, etc

# We want an AI agent system
The Security Analyst (SA) agent is a chat and orchestrator.  It can both respond to the user's requests as well as run all AI agents. 
- Should the SA agent have a separate agent for chat?

## What the SA Agent can do
- Launch analysis given inputs.
- Make changes to current analysis based on user requests (i.e., user asks to update a specific section or table, add to the table, etc. generate/modify/delete plots, use a specific tool for a plot/diagram.) Essentially, the SA agent must call the right tools to update the Analysis Canvas to assist the user in the analysis.


## Short-term vision--rapid prototype
- A tool that can perform a basic analysis on all selected analysis plugins.
- A tool that can answer user's questions about the analysis.
- A tool that can re-run an analysis given user's changes or requests

## Medium term vision
- SA Agent can add new context to the Analysis Canvas using user specified tools
- SA Agent can interact with external tools (via MCP) to add new contact or further analysis goal of the user
- Modify exiting analyses reports based on feedback from user.

## Long term vision 
- SA Agent can run a fully customizable security analysis, create a comprehensive report based on all anaysis plugins, suggest additional plugins, verify requirements are met given compliance-based plugins, suggest new compliance analysis or threat/security analysis plugins/additions, completely control the Analysis Canvas making changes based on the user's requests
- Run a fully automated security analysis that can be sent to another AI agent (or human) who is designing and building tools (i.e., an iterative process between AI agents that build the software and the SA Agent that analysis security and suggests improvement to re-enforce security and align with various regulations and compliance standards).
- A tool that can gather information from tickets and user feedback and integrate into the security analysis.  Provide summaries of tickets and user feedback (etc.)


# Backend
- We need a versioning system
- We need to save all artifacts, maintain artifact state, re-load saved analyses, generate summary reports (based on user request) for one or multiple analyses (human readable).

## Saving analyses
We need to figure out how to store all the analysis components so that can be used to repopulate the Analysis Canvas.  Here are some considerations.
### Diagrams
- diagrams should be drawn based on a graph database.  We expect using the same components and relationships for different types of diagrams (i.e., process flow diagrams, user friendly diagrams with appropriate icons, diagrams that contain more component information).  Entities will include additional information (for example, click on a component in a diagram, add/edt/delete information, show different types of information in the diagram).  Relationships may change.  To be useful, the user needs to be able to change relationships, updating both the diagram and the database.
- Diagrams need to be importable into other diagramming software based on user needs.
- The diagram components should come from the other analyses entities.  

### Tracing STPA-Sec
- mitigations need to be traced to stakeholder requirements for security.  The user should be able to click on a mitigation and select Show Trace to Stakeholder requirements and possibly a map of all other components (like a mind map or something.)


How do we develop a backend that does all of this?
