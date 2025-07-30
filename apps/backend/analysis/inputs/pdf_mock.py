"""Mock PDF content for testing when PDF libraries are not available."""

MOCK_PDF_CONTENT = """
SD-WAN Deployment Models Reference Architecture

Executive Summary
This document provides a comprehensive reference architecture for Software-Defined Wide Area Network (SD-WAN) deployment models. SD-WAN technology enables organizations to leverage multiple types of network connections—including MPLS, broadband internet, and LTE—to securely connect users to applications.

1. Introduction
SD-WAN represents a transformational approach to simplifying branch office networking and assuring optimal application performance over any transport. Unlike traditional WANs, SD-WAN delivers increased network agility and cost reduction.

2. Architecture Overview
The SD-WAN architecture consists of several key components:

2.1 SD-WAN Edge Devices
- Physical or virtual appliances deployed at branch locations
- Provide secure connectivity and traffic steering
- Support zero-touch provisioning

2.2 SD-WAN Controller
- Centralized management and orchestration platform
- Policy definition and distribution
- Real-time monitoring and analytics

2.3 SD-WAN Gateway
- Cloud or data center hosted component
- Provides optimized access to cloud applications
- Enables hub-and-spoke topologies

3. Deployment Models

3.1 Internet-based SD-WAN
- Leverages broadband internet connections
- Cost-effective for small to medium branches
- Requires robust security mechanisms

3.2 Hybrid SD-WAN
- Combines MPLS and internet connections
- Provides guaranteed performance for critical applications
- Enables gradual migration from legacy WAN

3.3 Cloud-first SD-WAN
- Direct internet breakout at branch locations
- Optimized for SaaS and IaaS connectivity
- Reduces backhaul traffic to data centers

4. Security Considerations
- End-to-end encryption across all transport types
- Integrated firewall and intrusion prevention
- Microsegmentation for lateral movement prevention
- Cloud security service chaining

5. High Availability and Redundancy
- Active-active link utilization
- Sub-second failover capabilities
- Geographic redundancy for controllers
- Automatic path selection based on application SLA

6. Management and Operations
- Single pane of glass management
- Role-based access control
- RESTful APIs for automation
- Integration with existing IT service management tools

This reference architecture provides the foundation for organizations to design and implement SD-WAN solutions that meet their specific business and technical requirements.
"""

def get_mock_pdf_content(filename: str) -> str:
    """Return mock content based on filename"""
    if 'sd-wan' in filename.lower():
        return MOCK_PDF_CONTENT
    else:
        # Generic technical document content
        return """
Technical Architecture Document

1. System Overview
This document describes the architecture of a distributed system designed for high availability and scalability.

2. Components
- Application Layer: Handles user requests and business logic
- Service Layer: Provides reusable services and APIs
- Data Layer: Manages data persistence and caching
- Infrastructure Layer: Handles deployment, monitoring, and scaling

3. Security Architecture
- Authentication and authorization mechanisms
- Data encryption at rest and in transit
- Network security controls
- Audit logging and monitoring

4. Deployment Architecture
- Container-based deployment using Kubernetes
- Multi-region deployment for disaster recovery
- Auto-scaling based on load metrics
- Blue-green deployment strategy

5. Integration Points
- RESTful APIs for external integrations
- Message queuing for asynchronous processing
- Event streaming for real-time data flow
- Batch processing for data synchronization
"""