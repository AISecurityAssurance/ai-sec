#!/usr/bin/env python3
"""
Test script for Step 1 agents
"""
import asyncio
import asyncpg
import os
import json
from datetime import datetime

from core.agents.step1_agents import Step1Coordinator

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')

# Test system description
TEST_SYSTEM_DESCRIPTION = """
The Digital Banking Platform is a comprehensive financial services system that enables retail and 
business customers to manage their finances through web and mobile applications. The platform 
provides account management, payment processing, fund transfers, and financial reporting capabilities 
while ensuring regulatory compliance with PCI-DSS, GDPR, and SOX requirements.

The system operates 24/7 with a 99.99% availability SLA, processing over 10 million transactions 
daily for 5 million retail customers and 50,000 business customers. It integrates with core banking 
systems, payment networks, and third-party financial services through secure APIs.

Key capabilities include multi-factor authentication, real-time fraud detection using AI/ML models, 
encrypted data storage, and comprehensive audit logging. The platform operates in a hybrid cloud 
environment (AWS and on-premise) with multiple security zones and redundancy mechanisms.

The system must protect customer financial assets and personal information while providing reliable 
access to banking services. It faces threats from organized cybercrime groups, nation-state actors, 
and potential insider threats, all while maintaining strict regulatory compliance and customer trust.
"""


async def test_step1_agents():
    """Test Step 1 agents with sample banking system"""
    
    # Don't use a shared connection - let coordinator create its own
    
    try:
        print("Testing Step 1 Agents")
        print("=" * 80)
        print(f"System: Digital Banking Platform")
        print(f"Timestamp: {datetime.now()}")
        print("=" * 80)
        
        # Create coordinator without connection (it will create its own)
        coordinator = Step1Coordinator()
        
        # Perform analysis
        print("\nStarting Step 1 analysis...")
        results = await coordinator.perform_analysis(
            system_description=TEST_SYSTEM_DESCRIPTION,
            analysis_name="Digital Banking Platform - Step 1 Test"
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        
        # Executive Summary
        summary = results['executive_summary']
        print(f"\nAnalysis ID: {results['analysis_id']}")
        print(f"Status: {results['status']}")
        print(f"Duration: {results['duration']:.2f} seconds")
        print(f"\nSystem: {summary['analysis_scope']['system']}")
        print(f"Domain: {summary['analysis_scope']['domain']}")
        print(f"Criticality: {summary['analysis_scope']['criticality']}")
        
        # Key Findings
        findings = summary['key_findings']
        print(f"\nKey Findings:")
        print(f"  - Losses identified: {findings['losses_identified']} ({findings['critical_losses']} critical)")
        print(f"  - Hazards identified: {findings['hazards_identified']}")
        print(f"  - Adversary classes: {findings['adversary_classes']}")
        print(f"  - Highest threat: {findings['highest_threat']}")
        
        # Quality Assessment
        quality = summary['quality_assessment']
        print(f"\nQuality Assessment:")
        print(f"  - Overall quality: {quality['overall_quality']}")
        print(f"  - Quality score: {quality['quality_score']}/100")
        print(f"  - Strengths: {', '.join(quality['strengths'])}")
        if quality['improvement_areas']:
            print(f"  - Improvement areas: {', '.join(quality['improvement_areas'])}")
        
        # Problem Statement
        mission = results['results']['mission_analysis']['problem_statement']
        print(f"\nProblem Statement:")
        print(f"  {mission['full_statement']}")
        
        # Losses
        losses = results['results']['loss_identification']['losses']
        print(f"\nIdentified Losses:")
        for loss in losses[:5]:  # Show first 5
            severity = loss['severity_classification']['magnitude']
            print(f"  - {loss['identifier']}: {loss['description']} [{severity}]")
        
        # Hazards
        hazards = results['results']['hazard_identification']['hazards']
        print(f"\nIdentified Hazards:")
        for hazard in hazards[:5]:  # Show first 5
            temporal = hazard['temporal_nature']['existence']
            print(f"  - {hazard['identifier']}: {hazard['description']} [{temporal}]")
        
        # Stakeholders
        stakeholders = results['results']['stakeholder_analysis']['stakeholders']
        print(f"\nKey Stakeholders:")
        for stake in stakeholders[:5]:  # Show first 5
            print(f"  - {stake['name']} ({stake['stakeholder_type']})")
        
        # Adversaries
        adversaries = results['results']['stakeholder_analysis']['adversaries']
        print(f"\nAdversary Profiles:")
        for adv in adversaries:
            sophistication = adv['profile']['sophistication']
            print(f"  - {adv['adversary_class']}: {sophistication} sophistication")
        
        # Validation Results
        validation = results['results']['validation']
        val_results = validation['validation_results']
        print(f"\nValidation Results:")
        print(f"  - Abstraction: {val_results['abstraction']['status']} (score: {val_results['abstraction']['abstraction_score']})")
        print(f"  - Completeness: {val_results['completeness']['status']} (score: {val_results['completeness']['completeness_score']})")
        print(f"  - Consistency: {val_results['consistency']['status']} (score: {val_results['consistency']['consistency_score']})")
        print(f"  - Coverage: {val_results['coverage']['status']} (score: {val_results['coverage']['coverage_score']})")
        
        # Recommendations
        recommendations = validation['recommendations']
        if recommendations:
            print(f"\nTop Recommendations:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"  - [{rec['priority']}] {rec['recommendation']}")
        
        # Step 2 Bridge
        bridge = validation['step2_bridge']
        print(f"\nStep 2 Bridge - Control Needs:")
        for need_name, need_def in bridge['control_needs'].items():
            print(f"  - {need_name}: {need_def['need']}")
        
        # Next Steps
        print(f"\nNext Steps:")
        for step in summary['next_steps']:
            print(f"  - {step}")
        
        # Check if we can query the views
        print("\n" + "=" * 80)
        print("DATABASE VIEWS TEST")
        print("=" * 80)
        
        # Create a connection for testing views
        test_conn = await asyncpg.connect(DATABASE_URL)
        try:
            # Test completeness view
            completeness = await test_conn.fetchrow("""
                SELECT * FROM problem_framing_completeness 
                WHERE analysis_id = $1
            """, results['analysis_id'])
            
            if completeness:
                print(f"\nProblem Framing Completeness:")
                print(f"  - Completeness level: {completeness.get('completeness_level', 'N/A')}")
                if 'total_elements' in completeness:
                    print(f"  - Total elements: {completeness['total_elements']}")
                if 'missing_elements' in completeness:
                    print(f"  - Missing elements: {completeness['missing_elements']}")
            
            # Test executive summary view
            exec_summary = await test_conn.fetchrow("""
                SELECT * FROM step1_executive_summary
                WHERE analysis_id = $1
            """, results['analysis_id'])
            
            if exec_summary:
                print(f"\nDatabase Executive Summary:")
                print(f"  - Quality score: {exec_summary['quality_score']}")
                print(f"  - Completion status: {exec_summary['completion_status']}")
        finally:
            await test_conn.close()
        
        print("\n" + "=" * 80)
        print("✓ Step 1 agents test completed successfully!")
        print("=" * 80)
        
        # Save full results to file
        with open('step1_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results saved to step1_test_results.json")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_step1_agents())