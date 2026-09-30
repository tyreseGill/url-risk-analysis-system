# System Architecture

## Network Topology
![Network Topology Map](../assets/png/network-topology-diagram.drawio.png)

This diagram presents the overall architecture and workflow of the URL Risk Analysis System. User-submitted URLs pass through a series of analysis stages that gather information from external intelligence sources.

## Risk Analysis Hierarchy
![Image Depicting Order of Risk Analysis](../assets/svg/order_of_risk_analysis.drawio.svg)

The system carries out multiple data gathering techniques to be used in determining whether a URL poses a phishing risk. Analyses requiring direct interaction with the target website are considered higher risk than passive information gathering techniques.

## Multi-Stage Evaluation Pipeline
![Image Depicting Finite Automata Structure](../assets/svg/detection-system-finite-automata.drawio.svg)

The URL passes through a sequence of security checkpoints of a finite automata structure. Each stage contributes additional information used in the final risk assessment.

Upon reaching each checkpoint, the system determines with its current knowledge of the target's risk indicators whether to proceed to the next stage of analysis or stop early. This risk-conscious architecture minimizes unnecessary interaction with potentially malicious websites while prioritizing safer, lower-risk intelligence gathering techniques whenever possible.

## Analysis Methods
![Image Depicting Analysis Methods](../assets/svg/analysis-methods.drawio.svg)
