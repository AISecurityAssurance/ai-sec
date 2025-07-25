# LLM Notebook Proposal Ideas
24 July 2025

https://notebooklm.google.com/notebook/f284f345-1867-4ef5-b0b1-c5910ce807ac

# Summary
The provided text, "AI in Systems Security Analysis: Pain Points and Capabilities," delves into the significant challenges faced in systems security analysis and how artificial intelligence, particularly large language models, can offer solutions. It highlights "pain points" such as the exponential growth of artifacts, limitations of traditional analysis methods that often miss software-related issues, and strategic gaps where security is addressed too late in the development lifecycle. The document also emphasizes human factors like confirmation bias and difficulties in information management as major hurdles. Conversely, the text details how AI and automation provide powerful "capabilities," including the automated generation and linking of analysis artifacts, enhanced analysis and insights through pattern recognition, strategic integration of security early in design, and improved information management for better traceability. Ultimately, the source argues that AI can transform security analysis from a laborious, manual process into a more efficient, objective, and proactive endeavor, significantly aiding in regulatory compliance and fostering "security by design."

# AI in Systems Security Analysis: Pain Points and Capabilities
Building an application that leverages AI to assist and automate systems security analysis methods like STPA-Sec, STRIDE, HAZOP, and others is a highly relevant endeavor, given the inherent complexities and challenges in these domains. Drawing on the provided sources, here's an overview of common pain points for users and how AI and automation can offer significant capabilities to alleviate them.
Pain Points in Systems Security Analysis
Users of systems security analysis methods often encounter several difficulties that make these tasks time-consuming, prone to error, and less effective than desired:
• Complexity and Scale of Artifacts [1, 2]:
    ◦ The number of artifacts, such as Unsafe/Unsecure Control Actions (UCAs) and loss scenarios, can grow exponentially, making them costly to produce and maintain for human engineers [1-3]. For instance, even a small system might generate 80 UCAs and 320 loss scenarios, representing a major limitation in completing STPA [1, 2].
    ◦ Managing traceability between the origins of requirements (e.g., from STPA) and the software implementation is challenging and often missing [4]. Traditional tools like Microsoft Word or Excel exacerbate this issue [4].
    ◦ Programmatically analyzing existing STPA applications and artifacts, which are often encoded in free text within PDF documents, is a time-consuming endeavor for researchers [5].
• Limitations of Traditional Analysis Methods [6]:
    ◦ Traditional hazard analysis methods like Fault Tree Analysis (FTA), Failure Modes and Effects Criticality Analysis (FMECA), Event Tree Analysis (ETA), and Hazard and Operability Analysis (HAZOP) often miss software-related and non-failure causal scenarios [6-8]. They also tend to find fewer causal scenarios overall [6, 7].
    ◦ These methods are typically more costly in terms of time and resources compared to newer approaches like STPA [6, 7].
    ◦ Traditional decompositional analysis assumes direct and known interactions between components, which does not hold true for today's complex, software-intensive systems [9-11]. This approach struggles with "unknown unknowns" [8, 12].
    ◦ Traditional methods often assume accidents are caused by component failure and rely on calculating probabilities, an assumption that does not apply to software and human behavior [8, 10, 13]. They often require a fairly detailed design, making them inappropriate for early concept analysis when functional safety/security requirements are most needed [14].
    ◦ There is a surprising lack of dedicated tools or frameworks in the STPA ecosystem, largely due to its recency [15]. Similarly, no security analysis method has been standardized or widely adopted in the development field [16].
• Strategic vs. Tactical Gaps in Security Engineering [17-20]:
    ◦ Cybersecurity is often framed as a "tactics problem," focusing on defending networks and assets, which misses the higher objective of securing system functions and services [17, 18, 20, 21].
    ◦ The vast majority of current security engineering practice addresses security late in the lifecycle, specifically after architecture is well defined, leading to costly and less effective "bolt-on" solutions [19, 22, 23].
    ◦ Security is a "wicked problem," where even defining and framing the problem is inherently complex and difficult [24-26]. This can lead designers to protect the wrong things or protect the right things in the wrong way [27].
    ◦ Traditional threat-based approaches rely on predicting adversary actions and motives, which is difficult given rapidly evolving and little-understood adversaries [28-30]. They also suffer from "failures of imagination" and cognitive biases that limit foresight [31, 32].
• Human Factors and Biases [33-35]:
    ◦ Human requirement engineers are prone to confirmation bias, leading them to miss many potential failures in system safety [33, 34, 36].
    ◦ Humans are generally poor at estimating the probability or likelihood of unusual events [37, 38].
    ◦ Mode confusion and loss of situational awareness are common human errors that can lead to hazards, often influenced by system design [39, 40].
    ◦ There is often an inadequate recording of design intent and rationale, leading to rework and suggested solutions that were previously discarded [41].
    ◦ Analysts often rely on their creativity to generate a full list of scenarios, which is inefficient and incomplete for complex systems [42, 43].
• Information Management and Feedback Loops [44, 45]:
    ◦ Automated monitoring systems can collect overwhelming amounts of data, making it difficult to analyze and detect problems [44].
    ◦ Raw quantitative data can be misleading; data is not the same as information [46].
    ◦ Disseminating information in a useful, timely, and adaptable form is challenging [45, 47].
    ◦ Reporting systems are often unused or ineffective because they are difficult to use, or employees believe their reports go into a "black hole" or fear repercussions [48, 49].

# How AI and Automation Can Help (Capabilities)
AI and automation, particularly Large Language Models (LLMs), offer powerful capabilities to address these pain points and enhance security analysis:
• Automated Generation and Linking of Artifacts [33, 50, 51]:
    ◦ LLMs can automate the generation of UCAs and loss scenarios (Steps 3 and 4 of STPA) with a high degree of accuracy, significantly saving time and effort for human engineers [2, 33, 50].
    ◦ They can also automatically link related artifacts (e.g., losses to hazards), improving traceability and suggesting missing connections that human engineers might overlook [33, 51, 52].
    ◦ LLMs are capable of generating other STPA artifacts beyond UCAs and loss scenarios [3].
• Enhanced Analysis and Insight [2, 33, 53]:
    ◦ LLMs, with their strengths in pattern recognition, contextual reasoning, and structured text generation, are well-suited for systematic, rule-based analyses like STPA [2]. They can process and structure large amounts of information at scale, helping to reduce cognitive load and ensure consistency in hazard identification [2].
    ◦ They can be effective in bypassing human confirmation bias, providing a more objective view of potential failures [33, 54].
    ◦ AI can analyze unstructured data from incident reports, audit logs, and operator feedback using Natural Language Processing (NLP) to reveal latent hazards, link real-world failures to existing STPA artifacts, extract relevant failure patterns, and prioritize hazards [53].
    ◦ AI-powered tools can support real-time safety monitoring by analyzing live system logs to detect emerging hazards and UCAs, and even filter incorrect outputs and duplicates while dynamically updating STPA artifacts [53, 55].
    ◦ Integrating vision models (e.g., GPT-4o) allows LLMs to process control structure diagrams as images, providing a holistic context of the system (entities, control actions, feedback loops, labels) during output generation [56].
• Strategic Integration and Early Stage Support [57, 58]:
    ◦ STPA-Sec, enhanced by AI, enables a strategic, top-down approach to security by beginning at the concept stage [57, 59]. It helps define secure functionality and security concepts to guide architectural development, preventing late-stage "bolt-on" security solutions [57, 60].
    ◦ AI can aid in problem framing, facilitating meaningful dialogue and learning that sets a solid foundation for subsequent analysis, especially crucial for "wicked problems" in security [24, 58].
    ◦ AI-assisted wargaming capabilities can act as a "pen-test" for security concepts early in the design lifecycle, introducing a human adversary into the process [31, 61]. This helps combat cognitive bias and "failures of imagination" by assessing attack feasibility, countermeasure effectiveness, and operational risk [31, 32, 62].
• Improved Information Management and Traceability [47, 63, 64]:
    ◦ The framework forces users to express each STPA artifact (losses, hazards, UCAs) with defined parts (source, type, links) in a programmatic idiom (e.g., Python), allowing artifacts to be reliably accessed and analyzed as a concrete, traceable package [4].
    ◦ This approach supports standard software engineering practices like version control and type/style checks for STPA artifacts [4].
    ◦ AI can help in tailoring information provided and presentation format to the needs of specific users, ensuring decision-makers have the right information at the right time [47].

# Regulations and Compliance Analyses/Documentation
AI and automation can significantly benefit the creation and management of documentation required for regulatory compliance:
• Eliciting Requirements for Compliance: Systematic safety analyses are required by safety compliance standards to elicit requirements [7]. Tools supporting STPA (and its security variants) can help generate these initial requirements.
• Support for Hazard Assessment & Risk Analysis (HARA): Tools like LASAR, which supports HARA for automotive systems under ISO 26262-3.6, can take inputs generated by systematic hazard analysis techniques like FMEA or STPA [65]. An AI-integrated STPA framework can directly produce these crucial inputs and artifacts [66].
• Functional Safety Standards: The outputs generated or artifacts stored by an AI-integrated STPA framework can serve as crucial inputs to tools that support compliance with standards [66].
• Integrated Security by Design: AI-enhanced STPA-Sec aligns with calls to institutionalize "security by design" for federal IT modernization, as seen in recommendations for DevSecOps approaches and by organizations like Akamai and Embraer [67, 68]. Embraer, for example, found STPA-Sec to be an alternative means of compliance to ED-202A/DO-326A and it is now included as Appendix G of DO-356A Aircraft Airworthiness Security [68, 69].
• NIST and ISO Standards: NIST SP 800-160 (Systems Security Engineering) and IEEE/IEC/ISO 15288 (System Engineering Standards) emphasize business/mission analysis and requirements definition [70]. AI can facilitate the generation and maintenance of the documentation and analysis artifacts required by these standards.
• Traceability for Audits and Change Management: STPA-Sec inherently promotes traceability from identified hazards to causal scenarios and design features [63, 64, 71-73]. This is invaluable for Management of Change (MOC) policies, enabling efficient evaluation of changes' impact on safety and security, and helping to avoid skipping MOC procedures [72, 74]. AI can help manage this complex web of trace links.
• Leading Indicators and Risk Management: AI can assist in identifying assumption-based leading indicators from STPA analyses, which are crucial for monitoring system degradation and increasing risk over time [75-77]. This can provide data for ongoing risk management programs and audits [76, 78].

# Conclusions
In essence, AI and automation can serve as a powerful magnifying glass and an efficient assistant for security analysts. Imagine trying to navigate a vast, intricate city where every street, building, and person is connected in complex ways. Traditional methods might give you a paper map, but AI could provide a real-time, interactive 3D model, highlighting potential traffic jams or unsafe areas, and even suggesting alternative routes before problems even arise. This allows analysts to shift their focus from the laborious task of manually mapping the city to strategically designing safer, more secure pathways and mitigating risks more effectively.
