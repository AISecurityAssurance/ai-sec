"""
Stakeholder Analyst Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List, Optional
import re
import json
from uuid import uuid4

from .base_step1 import BaseStep1Agent, CognitiveStyle


class StakeholderAnalystAgent(BaseStep1Agent):
    """
    Analyzes stakeholders and their mission perspectives
    
    Responsibilities:
    - Identify all stakeholders (including adversaries)
    - Capture mission perspectives
    - Map stakeholder loss exposure
    - Analyze influence/interest dynamics
    """
    
    def get_agent_type(self) -> str:
        return "stakeholder_analyst"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stakeholders and their perspectives"""
        await self.log_activity("Starting stakeholder analysis")
        
        system_description = context.get('system_description', '')
        prior_results = await self.get_prior_results(['mission_analyst', 'loss_identification'])
        
        mission_context = prior_results.get('mission_analyst', {}).get('mission_context', {})
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        
        # Always use LLM for analysis
        stakeholder_data = await self._analyze_stakeholders_with_llm(system_description, mission_context, losses)
        
        # Extract stakeholders
        all_stakeholders = stakeholder_data.get('stakeholders', [])
        adversaries = stakeholder_data.get('adversaries', [])
        
        # Create stakeholder analysis
        stakeholder_matrix = await self._create_stakeholder_matrix(all_stakeholders)
        adversary_analysis = await self._analyze_adversary_profiles(adversaries, mission_context)
        
        # Define mission success criteria based on stakeholder perspectives
        success_criteria = await self._define_mission_success_criteria(
            all_stakeholders, adversaries, losses
        )
        
        results = {
            "stakeholders": all_stakeholders,
            "stakeholder_count": len(all_stakeholders),
            "stakeholder_types": self._summarize_types(all_stakeholders),
            "adversaries": adversaries,
            "adversary_count": len(adversaries),
            "stakeholder_matrix": stakeholder_matrix,
            "adversary_analysis": adversary_analysis,
            "mission_success_criteria": success_criteria,
            "critical_relationships": await self._identify_critical_relationships(
                all_stakeholders, adversaries
            )
        }
        
        await self.save_results(results)
        await self.log_activity("Completed stakeholder analysis", {
            "stakeholder_count": len(all_stakeholders),
            "adversary_count": len(adversaries)
        })
        
        return results
    
    async def _identify_user_stakeholders(self, description: str, 
                                         mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify user stakeholders"""
        stakeholders = []
        
        # Common user patterns
        user_patterns = [
            (r"customer", "Customer", "Primary users of the system"),
            (r"user", "End User", "Individuals who interact with the system"),
            (r"patient", "Patient", "Recipients of system services"),
            (r"citizen", "Citizen", "Members of the public served by the system")
        ]
        
        desc_lower = description.lower()
        for pattern, name, description_text in user_patterns:
            if re.search(pattern, desc_lower):
                stakeholders.append({
                    "name": name,
                    "stakeholder_type": "user",
                    "description": description_text,
                    "criticality": "primary"
                })
        
        # Domain-specific users based on system description
        # Note: Domain-specific identification should be based on 
        # actual system description content, not hardcoded domains
        
        return stakeholders
    
    async def _identify_operator_stakeholders(self, description: str, 
                                            mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify operator stakeholders"""
        stakeholders = []
        
        # Always include system operators
        stakeholders.append({
            "name": "System Operators",
            "stakeholder_type": "operator",
            "description": "Personnel responsible for system operation and maintenance",
            "criticality": "essential"
        })
        
        # Specific operator types
        if "employee" in description.lower():
            stakeholders.append({
                "name": "Employees",
                "stakeholder_type": "operator",
                "description": "Staff members who use the system for work",
                "criticality": "important"
            })
        
        if "administrator" in description.lower() or "admin" in description.lower():
            stakeholders.append({
                "name": "System Administrators",
                "stakeholder_type": "operator",
                "description": "Technical staff with elevated system privileges",
                "criticality": "essential"
            })
        
        if "security" in description.lower():
            stakeholders.append({
                "name": "Security Team",
                "stakeholder_type": "operator",
                "description": "Personnel responsible for system security",
                "criticality": "essential"
            })
        
        return stakeholders
    
    async def _identify_regulator_stakeholders(self, description: str, 
                                              mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify regulatory stakeholders"""
        stakeholders = []
        
        # Check for regulatory indicators
        regulatory_constraints = mission_context.get('operational_constraints', {}).get('regulatory', {})
        frameworks = regulatory_constraints.get('frameworks', [])
        
        if frameworks or "regulat" in description.lower() or "complian" in description.lower():
            stakeholders.append({
                "name": "Regulatory Bodies",
                "stakeholder_type": "regulator",
                "description": "Government agencies overseeing compliance",
                "criticality": "required"
            })
        
        # Specific regulators based on frameworks
        regulator_map = {
            "PCI-DSS": "Payment Card Industry Security Standards Council",
            "HIPAA": "Department of Health and Human Services",
            "GDPR": "Data Protection Authorities",
            "SOX": "Securities and Exchange Commission",
            "NERC-CIP": "North American Electric Reliability Corporation"
        }
        
        for framework in frameworks:
            if framework in regulator_map:
                stakeholders.append({
                    "name": regulator_map[framework],
                    "stakeholder_type": "regulator",
                    "description": f"Enforces {framework} compliance",
                    "criticality": "required"
                })
        
        return stakeholders
    
    async def _identify_beneficiary_stakeholders(self, description: str, 
                                               mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify beneficiary stakeholders"""
        stakeholders = []
        
        # Shareholders/owners
        if any(word in description.lower() for word in ["business", "corporate", "company"]):
            stakeholders.append({
                "name": "Shareholders",
                "stakeholder_type": "owner",
                "description": "Owners expecting return on investment",
                "criticality": "important"
            })
        
        # Partners
        if "partner" in description.lower() or "integration" in description.lower():
            stakeholders.append({
                "name": "Business Partners",
                "stakeholder_type": "partner",
                "description": "Organizations with integrated services",
                "criticality": "important"
            })
        
        # Society (for critical infrastructure)
        if mission_context.get('criticality') == 'mission_critical':
            stakeholders.append({
                "name": "Society",
                "stakeholder_type": "society",
                "description": "Broader community depending on system services",
                "criticality": "contextual"
            })
        
        return stakeholders
    
    async def _analyze_mission_perspective(self, stakeholder: Dict[str, Any], 
                                         mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stakeholder's mission perspective"""
        perspective = {
            "success_means": "",
            "failure_means": "",
            "tolerance_level": "moderate",
            "alternatives": "Limited"
        }
        
        name = stakeholder['name'].lower()
        s_type = stakeholder['stakeholder_type']
        
        # User perspectives
        if s_type == 'user':
            if 'customer' in name:
                perspective['success_means'] = "I can reliably access and use services when needed"
                perspective['failure_means'] = "I cannot access services or suffer harm from system failure"
                perspective['tolerance_level'] = "very_low"
                perspective['alternatives'] = "Other service providers available"
            else:
                perspective['success_means'] = "The system helps me achieve my goals"
                perspective['failure_means'] = "The system prevents me from achieving my goals"
                perspective['tolerance_level'] = "low"
        
        # Operator perspectives
        elif s_type == 'operator':
            if 'security' in name:
                perspective['success_means'] = "System remains secure and threats are managed"
                perspective['failure_means'] = "Security is compromised or unmanageable"
                perspective['tolerance_level'] = "very_low"
                perspective['alternatives'] = "None - responsible for this system"
            else:
                perspective['success_means'] = "I can effectively perform my duties"
                perspective['failure_means'] = "System issues prevent job performance"
                perspective['tolerance_level'] = "low"
                perspective['alternatives'] = "Manual processes (inefficient)"
        
        # Regulator perspectives
        elif s_type == 'regulator':
            perspective['success_means'] = "Organization operates within legal boundaries"
            perspective['failure_means'] = "Violations occur requiring enforcement action"
            perspective['tolerance_level'] = "zero"
            perspective['alternatives'] = "N/A - compliance is mandatory"
        
        # Owner perspectives
        elif s_type == 'owner':
            perspective['success_means'] = "System generates expected returns"
            perspective['failure_means'] = "System causes financial losses"
            perspective['tolerance_level'] = "moderate"
            perspective['alternatives'] = "Divest or replace management"
        
        # Partner perspectives
        elif s_type == 'partner':
            perspective['success_means'] = "System provides expected benefits"
            perspective['failure_means'] = "System fails to deliver value"
            perspective['tolerance_level'] = "moderate"
            perspective['alternatives'] = "Find alternative partners"
        
        # Society perspectives
        elif s_type == 'society':
            perspective['success_means'] = "System operates safely and reliably"
            perspective['failure_means'] = "System causes societal harm"
            perspective['tolerance_level'] = "very_low"
            perspective['alternatives'] = "Regulatory intervention"
        
        return perspective
    
    async def _analyze_loss_exposure(self, stakeholder: Dict[str, Any], 
                                   losses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze stakeholder exposure to losses"""
        exposure = {
            "direct_impact": [],
            "severity_perception": {},
            "primary_concerns": []
        }
        
        name = stakeholder['name'].lower()
        s_type = stakeholder['stakeholder_type']
        
        for loss in losses:
            loss_id = loss['identifier']
            impact = loss.get('mission_impact', {}).get('stakeholder_harm', {})
            
            # Check if stakeholder is directly impacted
            stakeholder_impacted = False
            severity = "moderate"
            
            if s_type == 'user' and 'customer' in name:
                if loss['loss_category'] in ['financial', 'privacy', 'mission']:
                    stakeholder_impacted = True
                    severity = "catastrophic" if loss['loss_category'] == 'financial' else "major"
            
            elif s_type == 'operator':
                if loss['loss_category'] in ['reputation', 'mission']:
                    stakeholder_impacted = True
                    severity = "major"
            
            elif s_type == 'regulator':
                if loss['loss_category'] in ['regulatory', 'privacy']:
                    stakeholder_impacted = True
                    severity = "catastrophic"
            
            elif s_type == 'beneficiary':
                if loss['loss_category'] in ['financial', 'reputation']:
                    stakeholder_impacted = True
                    severity = "major"
            
            if stakeholder_impacted:
                exposure['direct_impact'].append(loss_id)
                exposure['severity_perception'][loss_id] = severity
        
        # Identify primary concerns
        if exposure['direct_impact']:
            if s_type == 'user':
                exposure['primary_concerns'] = ["Personal harm", "Service availability"]
            elif s_type == 'operator':
                exposure['primary_concerns'] = ["Job security", "Workload"]
            elif s_type == 'regulator':
                exposure['primary_concerns'] = ["Compliance violations", "Public harm"]
            elif s_type == 'beneficiary':
                exposure['primary_concerns'] = ["Financial returns", "Reputation"]
        
        return exposure
    
    async def _analyze_influence_interest(self, stakeholder: Dict[str, Any], 
                                        mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stakeholder influence and interest"""
        analysis = {
            "influence_level": "medium",
            "interest_level": "medium",
            "engagement_strategy": "keep_informed"
        }
        
        s_type = stakeholder['stakeholder_type']
        criticality = stakeholder.get('criticality', 'important')
        
        # Determine influence level
        if s_type == 'regulator':
            analysis['influence_level'] = "very_high"
        elif criticality == 'primary':
            analysis['influence_level'] = "high"
        elif criticality == 'essential':
            analysis['influence_level'] = "high"
        elif s_type == 'beneficiary' and 'shareholder' in stakeholder['name'].lower():
            analysis['influence_level'] = "high"
        
        # Determine interest level
        if criticality in ['primary', 'essential', 'required']:
            analysis['interest_level'] = "high"
        elif s_type == 'user':
            analysis['interest_level'] = "high"
        elif s_type == 'regulator':
            analysis['interest_level'] = "high"
        
        # Determine engagement strategy
        influence = analysis['influence_level']
        interest = analysis['interest_level']
        
        if influence in ['high', 'very_high'] and interest == 'high':
            analysis['engagement_strategy'] = "manage_closely"
        elif influence in ['high', 'very_high']:
            analysis['engagement_strategy'] = "keep_satisfied"
        elif interest == 'high':
            analysis['engagement_strategy'] = "keep_informed"
        else:
            analysis['engagement_strategy'] = "monitor"
        
        return analysis
    
    async def _identify_adversaries(self, description: str, 
                                  mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential adversaries"""
        adversaries = []
        
        domain = mission_context.get('domain', '')
        criticality = mission_context.get('criticality', '')
        
        # Common adversary types based on system value and exposure
        if any(term in description.lower() for term in ['valuable', 'critical', 'sensitive', 'high-value']):
            adversaries.append({
                "adversary_class": "organized_crime",
                "profile": {
                    "sophistication": "high",
                    "resources": "significant",
                    "persistence": "long_term",
                    "primary_interest": "financial_gain",
                    "geographic_scope": "global"
                },
                "mission_targets": {
                    "interested_in": ["valuable_assets", "operational_capability", "sensitive_data"],
                    "value_perception": "high_value_target",
                    "historical_interest": "known_targeting"
                }
            })
        
        # Insider threats are relevant to most systems
        adversaries.append({
            "adversary_class": "insider",
            "profile": {
                "sophistication": "moderate",
                "resources": "limited",
                "persistence": "opportunistic",
                "primary_interest": "personal_gain",
                "geographic_scope": "local"
            },
            "mission_targets": {
                "interested_in": ["privileged_access", "sensitive_data", "system_capabilities"],
                "value_perception": "target_of_opportunity",
                "historical_interest": "common_threat"
            }
        })
        
        # Nation-state for critical systems
        if criticality == 'mission_critical':
            adversaries.append({
                "adversary_class": "nation_state",
                "profile": {
                    "sophistication": "advanced",
                    "resources": "unlimited",
                    "persistence": "persistent",
                    "primary_interest": "strategic_advantage",
                    "geographic_scope": "global"
                },
                "mission_targets": {
                    "interested_in": ["system_disruption", "intelligence_gathering", "strategic_data"],
                    "value_perception": "strategic_target",
                    "historical_interest": "active_reconnaissance"
                }
            })
        
        # Hacktivists for high-profile or public-facing systems
        if any(term in description.lower() for term in ['public', 'high-profile', 'visible', 'consumer']):
            adversaries.append({
                "adversary_class": "hacktivist",
                "profile": {
                    "sophistication": "moderate",
                    "resources": "crowd_sourced",
                    "persistence": "campaign_based",
                    "primary_interest": "ideological",
                    "geographic_scope": "international"
                },
                "mission_targets": {
                    "interested_in": ["public_embarrassment", "service_disruption", "data_exposure"],
                    "value_perception": "symbolic_target",
                    "historical_interest": "periodic_campaigns"
                }
            })
        
        # Always include opportunists
        adversaries.append({
            "adversary_class": "opportunist",
            "profile": {
                "sophistication": "low",
                "resources": "minimal",
                "persistence": "short_term",
                "primary_interest": "easy_gains",
                "geographic_scope": "global"
            },
            "mission_targets": {
                "interested_in": ["low_hanging_fruit", "automated_attacks", "mass_exploitation"],
                "value_perception": "volume_target",
                "historical_interest": "constant_scanning"
            }
        })
        
        return adversaries
    
    async def _create_stakeholder_matrix(self, stakeholders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create stakeholder analysis matrix"""
        matrix = {
            "high_influence_high_interest": [],
            "high_influence_low_interest": [],
            "low_influence_high_interest": [],
            "low_influence_low_interest": []
        }
        
        for stakeholder in stakeholders:
            influence = stakeholder.get('influence_interest', {}).get('influence_level', 'medium')
            interest = stakeholder.get('influence_interest', {}).get('interest_level', 'medium')
            
            high_influence = influence in ['high', 'very_high']
            high_interest = interest == 'high'
            
            entry = {
                "name": stakeholder['name'],
                "type": stakeholder['stakeholder_type'],
                "strategy": stakeholder.get('influence_interest', {}).get('engagement_strategy', 'monitor')
            }
            
            if high_influence and high_interest:
                matrix['high_influence_high_interest'].append(entry)
            elif high_influence and not high_interest:
                matrix['high_influence_low_interest'].append(entry)
            elif not high_influence and high_interest:
                matrix['low_influence_high_interest'].append(entry)
            else:
                matrix['low_influence_low_interest'].append(entry)
        
        return matrix
    
    async def _analyze_adversary_profiles(self, adversaries: List[Dict[str, Any]], 
                                        mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze adversary profiles and capabilities"""
        analysis = {
            "threat_landscape": {
                "sophistication_range": self._assess_sophistication_range(adversaries),
                "resource_availability": self._assess_resource_availability(adversaries),
                "persistence_patterns": self._assess_persistence_patterns(adversaries)
            },
            "mission_attractiveness": self._assess_mission_attractiveness(adversaries, mission_context),
            "combined_threat_level": self._assess_combined_threat_level(adversaries)
        }
        
        return analysis
    
    def _assess_sophistication_range(self, adversaries: List[Dict[str, Any]]) -> str:
        """Assess range of adversary sophistication"""
        sophistications = [adv['profile']['sophistication'] for adv in adversaries]
        
        if 'advanced' in sophistications:
            return "Low to Advanced (full spectrum)"
        elif 'high' in sophistications:
            return "Low to High"
        else:
            return "Low to Moderate"
    
    def _assess_resource_availability(self, adversaries: List[Dict[str, Any]]) -> str:
        """Assess adversary resource levels"""
        resources = [adv['profile']['resources'] for adv in adversaries]
        
        if 'unlimited' in resources:
            return "Unlimited resources available (nation-state)"
        elif 'significant' in resources:
            return "Well-funded adversaries present"
        else:
            return "Limited to moderate resources"
    
    def _assess_persistence_patterns(self, adversaries: List[Dict[str, Any]]) -> List[str]:
        """Assess adversary persistence patterns"""
        patterns = []
        
        persistence_types = {adv['profile']['persistence'] for adv in adversaries}
        
        if 'persistent' in persistence_types:
            patterns.append("Advanced Persistent Threats (APT) expected")
        if 'long_term' in persistence_types:
            patterns.append("Long-term campaigns likely")
        if 'opportunistic' in persistence_types:
            patterns.append("Opportunistic attacks constant")
        
        return patterns
    
    def _assess_mission_attractiveness(self, adversaries: List[Dict[str, Any]], 
                                     mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how attractive the mission is to adversaries"""
        attractiveness = {
            "overall_rating": "moderate",
            "factors": [],
            "most_interested_adversaries": []
        }
        
        # High-value indicators
        high_value_count = sum(
            1 for adv in adversaries 
            if adv['mission_targets']['value_perception'] in ['high_value_target', 'strategic_target']
        )
        
        if high_value_count >= len(adversaries) / 2:
            attractiveness['overall_rating'] = "high"
            attractiveness['factors'].append("Multiple adversaries see high value")
        
        # Known targeting
        if any(adv['mission_targets']['historical_interest'] == 'known_targeting' for adv in adversaries):
            attractiveness['overall_rating'] = "high"
            attractiveness['factors'].append("Historical evidence of targeting")
        
        # Most interested
        for adv in adversaries:
            if adv['mission_targets']['value_perception'] in ['high_value_target', 'strategic_target']:
                attractiveness['most_interested_adversaries'].append(adv['adversary_class'])
        
        return attractiveness
    
    def _assess_combined_threat_level(self, adversaries: List[Dict[str, Any]]) -> str:
        """Assess overall threat level from all adversaries"""
        # Score each adversary
        threat_scores = {
            'advanced': 5,
            'high': 4,
            'moderate': 3,
            'low': 2
        }
        
        total_score = sum(
            threat_scores.get(adv['profile']['sophistication'], 1) 
            for adv in adversaries
        )
        
        avg_score = total_score / len(adversaries) if adversaries else 0
        
        if avg_score >= 4:
            return "severe"
        elif avg_score >= 3:
            return "elevated"
        elif avg_score >= 2:
            return "moderate"
        else:
            return "low"
    
    async def _define_mission_success_criteria(self, stakeholders: List[Dict[str, Any]], 
                                             adversaries: List[Dict[str, Any]], 
                                             losses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Define mission success criteria from stakeholder perspectives"""
        criteria = {
            "success_states": {},
            "success_indicators": {
                "behavioral_indicators": [],
                "performance_indicators": [],
                "external_indicators": []
            }
        }
        
        # Define success states by stakeholder type
        user_stakeholders = [s for s in stakeholders if s['stakeholder_type'] == 'user']
        if user_stakeholders:
            criteria['success_states']['user_success'] = {
                "description": "Users can reliably achieve their goals through the system",
                "violated_by_losses": [
                    loss['identifier'] for loss in losses 
                    if loss['loss_category'] in ['mission', 'privacy', 'financial']
                ],
                "evidence_of_success": "High usage rates, positive feedback, goal achievement metrics"
            }
        
        operator_stakeholders = [s for s in stakeholders if s['stakeholder_type'] == 'operator']
        if operator_stakeholders:
            criteria['success_states']['operational_success'] = {
                "description": "System operates efficiently within defined parameters",
                "violated_by_losses": [
                    loss['identifier'] for loss in losses 
                    if loss['loss_category'] == 'mission'
                ],
                "evidence_of_success": "Stable operations, manageable workload, effective controls"
            }
        
        regulator_stakeholders = [s for s in stakeholders if s['stakeholder_type'] == 'regulator']
        if regulator_stakeholders:
            criteria['success_states']['regulatory_success'] = {
                "description": "System maintains continuous compliance with all regulations",
                "violated_by_losses": [
                    loss['identifier'] for loss in losses 
                    if loss['loss_category'] in ['regulatory', 'privacy']
                ],
                "evidence_of_success": "Clean audits, no violations, proactive compliance"
            }
        
        # Define success indicators
        criteria['success_indicators']['behavioral_indicators'] = [
            "Users actively choose to use the system",
            "Stakeholders express confidence in the system",
            "No abnormal user behavior patterns"
        ]
        
        criteria['success_indicators']['performance_indicators'] = [
            "System meets defined performance targets",
            "Error rates within acceptable thresholds",
            "Recovery objectives consistently met"
        ]
        
        criteria['success_indicators']['external_indicators'] = [
            "Positive stakeholder assessments",
            "Regulatory approval maintained",
            "Market position stable or improving"
        ]
        
        # Add adversary-related success criteria
        if adversaries:
            criteria['success_states']['security_success'] = {
                "description": "System successfully resists adversary attempts",
                "violated_by_losses": [loss['identifier'] for loss in losses],
                "evidence_of_success": "No successful compromises, threats detected and mitigated"
            }
        
        return criteria
    
    async def _identify_critical_relationships(self, stakeholders: List[Dict[str, Any]], 
                                             adversaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify critical stakeholder relationships"""
        relationships = []
        
        # User-Operator relationships
        users = [s for s in stakeholders if s['stakeholder_type'] == 'user']
        operators = [s for s in stakeholders if s['stakeholder_type'] == 'operator']
        
        if users and operators:
            relationships.append({
                "relationship": "User-Operator",
                "nature": "Service delivery and support",
                "criticality": "essential",
                "failure_impact": "Users cannot achieve goals, operators cannot fulfill duties"
            })
        
        # Operator-Regulator relationships
        regulators = [s for s in stakeholders if s['stakeholder_type'] == 'regulator']
        
        if operators and regulators:
            relationships.append({
                "relationship": "Operator-Regulator",
                "nature": "Compliance and oversight",
                "criticality": "required",
                "failure_impact": "Regulatory violations and enforcement actions"
            })
        
        # Adversary-Target relationships
        if adversaries and users:
            relationships.append({
                "relationship": "Adversary-User",
                "nature": "Threat and target",
                "criticality": "hostile",
                "failure_impact": "Direct harm to users through system compromise"
            })
        
        return relationships
    
    def _summarize_types(self, stakeholders: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize stakeholder types"""
        types = {}
        for stakeholder in stakeholders:
            s_type = stakeholder['stakeholder_type']
            types[s_type] = types.get(s_type, 0) + 1
        return types
    
    async def _analyze_stakeholders_hardcoded(self, description: str, mission_context: Dict[str, Any], 
                                             losses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback hardcoded stakeholder analysis"""
        # Identify different stakeholder types
        users = await self._identify_user_stakeholders(description, mission_context)
        operators = await self._identify_operator_stakeholders(description, mission_context)
        regulators = await self._identify_regulator_stakeholders(description, mission_context)
        beneficiaries = await self._identify_beneficiary_stakeholders(description, mission_context)
        
        # Combine all non-adversary stakeholders
        all_stakeholders = users + operators + regulators + beneficiaries
        
        # Identify adversaries
        adversaries = await self._identify_adversaries(description, mission_context)
        
        return {
            "stakeholders": all_stakeholders,
            "adversaries": adversaries
        }
    
    async def _analyze_stakeholders_with_llm(self, description: str, mission_context: Dict[str, Any], 
                                           losses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use LLM to analyze stakeholders based on cognitive style"""
        # Get cognitive style prompt modifier
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Format losses for prompt
        losses_summary = "\n".join([f"- {loss['identifier']}: {loss['description']}" for loss in losses[:10]])
        
        # Build the prompt
        prompt = f"""{style_modifier}

You are a security analyst performing STPA-Sec Step 1 stakeholder analysis.

System Description:
{description}

Mission Context:
{json.dumps(mission_context, indent=2)}

Identified Losses:
{losses_summary}

Analyze all stakeholders and adversaries for this system.

STAKEHOLDER IDENTIFICATION CHECKLIST - You MUST identify AT LEAST 8-10 stakeholders covering:
□ PRIMARY USERS (2-3 types minimum):
  - Retail customers/Individual users
  - Business/Corporate users
  - Internal users (if applicable)
  
□ OPERATORS (2-3 types minimum):
  - System administrators
  - Security operations team
  - Support/Help desk staff
  - Data management team
  - Maintenance technicians (for physical systems)
  - Control room operators (for critical infrastructure)
  
□ OWNERS/INVESTORS (1-2 types minimum):
  - Shareholders/Investors
  - Board of directors
  - Executive management
  
□ REGULATORS (1-2 types minimum):
  - Primary industry regulator
  - Data protection authorities
  - Financial oversight bodies (if applicable)
  - Safety regulators (FAA for aviation, FDA for medical, etc.)
  - Environmental protection agencies (if applicable)
  
□ PARTNERS & SUPPLIERS (2-3 types minimum):
  - Technology vendors/Cloud providers
  - Integration partners
  - Payment processors (for financial systems)
  - Data providers/consumers
  
□ SOCIETY (1-2 types minimum):
  - Local community
  - General public
  - Consumer advocacy groups

For STAKEHOLDERS (legitimate users of the system), identify:
1. Name and type (MUST be one of: user, operator, owner, regulator, partner, society, supplier)
2. Description of their relationship to the system
3. Mission perspective (what they need from the system)
4. Loss exposure (which losses affect them)
5. Influence/interest analysis (influence_level, interest_level, engagement_strategy)
6. Criticality (primary, essential, important, secondary)

For ADVERSARIES (threat actors), identify:
1. Adversary class (nation_state, organized_crime, insider, hacktivist, opportunist)
2. Profile (sophistication, resources, persistence, primary_interest, geographic_scope)
3. Mission targets (what they're interested in, value perception, historical interest)

Provide your response as a JSON object with the following structure:
{{
  "stakeholders": [
    {{
      "name": "Stakeholder Name",
      "stakeholder_type": "user|operator|owner|regulator|partner|society|supplier",
      "description": "Their relationship to the system",
      "criticality": "primary|essential|important|secondary",
      "mission_perspective": {{
        "primary_needs": ["need1", "need2"],
        "value_derived": "What value they get from the system",
        "success_criteria": "What constitutes success for them"
      }},
      "loss_exposure": [
        {{
          "loss_id": "L-X",
          "impact": "catastrophic|major|moderate|minor",
          "description": "How this loss affects them"
        }}
      ],
      "influence_interest": {{
        "influence_level": "very_high|high|medium|low",
        "interest_level": "high|medium|low",
        "engagement_strategy": "manage_closely|keep_satisfied|keep_informed|monitor"
      }}
    }}
  ],
  "adversaries": [
    {{
      "adversary_class": "adversary_type",
      "profile": {{
        "sophistication": "advanced|high|moderate|low",
        "resources": "unlimited|significant|moderate|limited|minimal",
        "persistence": "persistent|long_term|campaign_based|opportunistic|short_term",
        "primary_interest": "strategic_advantage|financial_gain|ideological|personal_gain|easy_gains",
        "geographic_scope": "global|international|regional|local"
      }},
      "mission_targets": {{
        "interested_in": ["target1", "target2"],
        "value_perception": "strategic_target|high_value_target|symbolic_target|target_of_opportunity|volume_target",
        "historical_interest": "active_reconnaissance|known_targeting|periodic_campaigns|common_threat|constant_scanning"
      }}
    }}
  ]
}}

IMPORTANT: 
1. Consider all types of stakeholders and realistic adversary profiles for this system type.
2. Identify AT LEAST 8-10 different stakeholders from the checklist above to ensure comprehensive coverage.
3. Use ONLY these stakeholder types: user, operator, owner, regulator, partner, society, supplier
4. Do NOT use "beneficiary" or "vendor" as stakeholder types - map them to allowed types (e.g., shareholders → owner, vendors → supplier).
5. Each stakeholder category in the checklist should be represented.
6. Be specific with stakeholder names based on the system (e.g., "Individual System Users" not just "Users").

MINIMUM REQUIREMENT: Fewer than 8 stakeholders will be considered incomplete. Ensure you have:
- At least 2-3 different user types
- At least 2-3 different operator roles
- At least 1-2 owners/investors
- At least 1-2 regulators
- At least 2-3 partners/suppliers
- At least 1 societal stakeholder"""
        
        try:
            # Call LLM
            response = await self.call_llm(prompt)
            
            # Parse JSON response using robust parser
            stakeholder_data = await self.parse_llm_json_response(response)
            
            # Validate structure
            if "stakeholders" not in stakeholder_data or "adversaries" not in stakeholder_data:
                raise ValueError("Response must contain 'stakeholders' and 'adversaries' keys")
            
            return stakeholder_data
            
        except Exception as e:
            await self.log_activity(f"LLM stakeholder analysis failed: {e}", {"error": str(e)})
            # Re-raise the exception - analysis should fail if LLM fails
            raise
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate stakeholder content maintains mission-level abstraction"""
        # Stakeholder descriptions should focus on mission relationships
        return not self.is_implementation_detail(content)