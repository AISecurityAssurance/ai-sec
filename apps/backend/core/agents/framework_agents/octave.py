"""
OCTAVE Agent Implementation
Operationally Critical Threat, Asset, and Vulnerability Evaluation
"""
from typing import List, Dict, Any, Optional
import re
import time
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper
from core.agents.websocket_integration import AgentWebSocketNotifier


class OctaveAgent(BaseAnalysisAgent):
    """
    OCTAVE Security Analysis Agent
    
    Analyzes organizational and technical risks:
    - Organizational view (policies, practices)
    - Technological view (infrastructure vulnerabilities)  
    - Critical asset identification
    - Threat profiles
    - Risk measurement and mitigation
    """
    
    def __init__(self):
        super().__init__(FrameworkType.OCTAVE)
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional[AgentWebSocketNotifier] = None
    ) -> AgentResult:
        """Run OCTAVE analysis"""
        start_time = time.time()
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("OCTAVE")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 9  # OCTAVE is comprehensive
        
        result = AgentResult(
            framework=self.framework,
            sections=[s.model_dump() for s in sections],
            artifacts=self._extract_artifacts(sections),
            duration=time.time() - start_time,
            token_usage={
                "input_tokens": total_tokens // 2,
                "output_tokens": total_tokens // 2,
                "total_tokens": total_tokens
            }
        )
        
        # Notify analysis complete
        if notifier:
            success = all(s.status == "completed" for s in sections)
            error = next((s.error for s in sections if s.error), None)
            await notifier.notify_analysis_complete("OCTAVE", success, error)
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "assets", "title": "Critical Assets", "template": "table"},
            {"id": "areas_of_concern", "title": "Areas of Concern", "template": "table"},
            {"id": "security_requirements", "title": "Security Requirements", "template": "table"},
            {"id": "threat_profiles", "title": "Threat Profiles", "template": "table"},
            {"id": "vulnerabilities", "title": "Vulnerabilities", "template": "table"},
            {"id": "risk_analysis", "title": "Risk Analysis", "template": "table"},
            {"id": "risk_matrix", "title": "Risk Matrix", "template": "heat_map"},
            {"id": "protection_strategy", "title": "Protection Strategy", "template": "section"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "assets":
            assets = self._parse_assets(response)
            return mapper.map_to_table(
                headers=["ID", "Asset", "Type", "Description", "Owner", "Criticality", "Impact"],
                rows=[[
                    asset["id"],
                    asset["name"],
                    asset["type"],
                    asset["description"][:50] + "...",
                    asset.get("owner", "TBD"),
                    asset["criticality"],
                    asset.get("impact", "High")
                ] for asset in assets]
            )
            
        elif section_id == "areas_of_concern":
            concerns = self._parse_areas_of_concern(response)
            return mapper.map_to_table(
                headers=["ID", "Area", "Asset", "Concern", "Impact", "Priority"],
                rows=[[
                    concern["id"],
                    concern["area"],
                    concern["asset"],
                    concern["description"],
                    concern["impact"],
                    concern["priority"]
                ] for concern in concerns]
            )
            
        elif section_id == "security_requirements":
            requirements = self._parse_security_requirements(response)
            return mapper.map_to_table(
                headers=["ID", "Requirement", "Type", "Asset", "Priority", "Status"],
                rows=[[
                    req["id"],
                    req["description"],
                    req["type"],
                    req["asset"],
                    req["priority"],
                    req.get("status", "Not Implemented")
                ] for req in requirements]
            )
            
        elif section_id == "threat_profiles":
            threats = self._parse_threat_profiles(response)
            return mapper.map_to_table(
                headers=["ID", "Actor", "Motivation", "Capability", "Assets Targeted", "Methods"],
                rows=[[
                    threat["id"],
                    threat["actor"],
                    threat["motivation"],
                    threat["capability"],
                    ", ".join(threat.get("assets_targeted", [])),
                    ", ".join(threat.get("methods", []))
                ] for threat in threats]
            )
            
        elif section_id == "vulnerabilities":
            vulns = self._parse_vulnerabilities(response)
            return mapper.map_to_table(
                headers=["ID", "Vulnerability", "Category", "Asset", "Severity", "Exploitability"],
                rows=[[
                    vuln["id"],
                    vuln["description"],
                    vuln["category"],
                    vuln["asset"],
                    vuln["severity"],
                    vuln.get("exploitability", "Medium")
                ] for vuln in vulns]
            )
            
        elif section_id == "risk_analysis":
            risks = self._parse_risk_analysis(response)
            return mapper.map_to_table(
                headers=["ID", "Risk", "Asset", "Threat", "Vulnerability", "Impact", "Probability", "Risk Level"],
                rows=[[
                    risk["id"],
                    risk["description"],
                    risk["asset"],
                    risk["threat"],
                    risk["vulnerability"],
                    risk["impact"],
                    risk["probability"],
                    risk["risk_level"]
                ] for risk in risks]
            )
            
        elif section_id == "risk_matrix":
            risks = self._parse_risk_analysis(response)
            return self._create_risk_matrix(risks, mapper)
            
        elif section_id == "protection_strategy":
            return self._parse_protection_strategy(response)
            
        else:
            return mapper.map_to_text(response, "markdown")
    
    def _parse_assets(self, response: str) -> List[Dict[str, Any]]:
        """Parse critical assets from response"""
        assets = []
        
        # Look for assets section
        assets_section = re.search(r"(?:CRITICAL\s+)?ASSETS:(.*?)(?:AREAS\s+OF\s+CONCERN|$)", response, re.IGNORECASE | re.DOTALL)
        
        if assets_section:
            content = assets_section.group(1)
            
            # Parse individual assets
            asset_pattern = r"ASSET\s*\d*:\s*(.+?)(?:Type:|Description:|$)"
            for match in re.finditer(asset_pattern, content, re.MULTILINE):
                asset_name = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+1000]
                
                # Type
                type_match = re.search(r"Type:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                asset_type = type_match.group(1).strip() if type_match else self._classify_asset_type(asset_name)
                
                # Description
                desc_match = re.search(r"Description:\s*(.+?)(?:Owner:|Criticality:|$)", details_text, re.IGNORECASE | re.DOTALL)
                description = desc_match.group(1).strip() if desc_match else "Critical business asset"
                
                # Owner
                owner_match = re.search(r"Owner:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                owner = owner_match.group(1).strip() if owner_match else "IT Department"
                
                # Criticality
                crit_match = re.search(r"Criticality:\s*(\w+)", details_text, re.IGNORECASE)
                criticality = crit_match.group(1) if crit_match else self._assess_asset_criticality(asset_name, description)
                
                # Impact
                impact_match = re.search(r"Impact.*?:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                impact = impact_match.group(1).strip() if impact_match else "High"
                
                assets.append({
                    "id": f"CA-{len(assets)+1:03d}",
                    "name": asset_name,
                    "type": asset_type,
                    "description": description,
                    "owner": owner,
                    "criticality": criticality,
                    "impact": impact
                })
                
        return assets
    
    def _parse_areas_of_concern(self, response: str) -> List[Dict[str, Any]]:
        """Parse areas of concern from response"""
        concerns = []
        
        # Look for areas of concern section
        aoc_section = re.search(r"AREAS\s+OF\s+CONCERN:(.*?)(?:SECURITY\s+REQUIREMENTS|$)", response, re.IGNORECASE | re.DOTALL)
        
        if aoc_section:
            content = aoc_section.group(1)
            
            # Parse concerns
            concern_pattern = r"AOC\d+:\s*(.+?)(?:Asset:|Impact:|AOC\d+:|$)"
            for match in re.finditer(concern_pattern, content, re.MULTILINE | re.DOTALL):
                concern_desc = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+500]
                
                # Asset
                asset_match = re.search(r"Asset:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                asset = asset_match.group(1).strip() if asset_match else "Multiple assets"
                
                # Impact
                impact_match = re.search(r"Impact:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                impact = impact_match.group(1).strip() if impact_match else "Significant"
                
                # Area and priority
                area = self._classify_concern_area(concern_desc)
                priority = self._assess_concern_priority(concern_desc, impact)
                
                concerns.append({
                    "id": f"AOC-{len(concerns)+1:03d}",
                    "area": area,
                    "asset": asset,
                    "description": concern_desc,
                    "impact": impact,
                    "priority": priority
                })
                
        return concerns
    
    def _parse_security_requirements(self, response: str) -> List[Dict[str, Any]]:
        """Parse security requirements from response"""
        requirements = []
        
        # Look for security requirements section
        req_section = re.search(r"SECURITY\s+REQUIREMENTS:(.*?)(?:THREAT\s+PROFILES|$)", response, re.IGNORECASE | re.DOTALL)
        
        if req_section:
            content = req_section.group(1)
            
            # Common requirement categories
            categories = ["Confidentiality", "Integrity", "Availability", "Authentication", "Authorization", "Audit"]
            
            for category in categories:
                # Find category requirements
                cat_pattern = rf"{category}.*?:(.*?)(?:{'|'.join(categories)}|THREAT|$)"
                cat_match = re.search(cat_pattern, content, re.IGNORECASE | re.DOTALL)
                
                if cat_match:
                    cat_content = cat_match.group(1)
                    req_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", cat_content, re.MULTILINE)
                    
                    for req_text in req_items:
                        if req_text.strip():
                            requirements.append({
                                "id": f"SR-{len(requirements)+1:03d}",
                                "description": req_text.strip(),
                                "type": category,
                                "asset": self._extract_asset_from_requirement(req_text),
                                "priority": self._assess_requirement_priority(req_text, category),
                                "status": "Not Implemented"
                            })
                            
        return requirements
    
    def _parse_threat_profiles(self, response: str) -> List[Dict[str, Any]]:
        """Parse threat profiles from response"""
        threats = []
        
        # Look for threat profiles section
        threat_section = re.search(r"THREAT\s+PROFILES:(.*?)(?:VULNERABILITIES|$)", response, re.IGNORECASE | re.DOTALL)
        
        if threat_section:
            content = threat_section.group(1)
            
            # Parse threat actors
            actor_pattern = r"(?:Threat\s+)?Actor\s*\d*:\s*(.+?)(?:Motivation:|$)"
            for match in re.finditer(actor_pattern, content, re.MULTILINE):
                actor_name = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+1000]
                
                # Motivation
                mot_match = re.search(r"Motivation:\s*(.+?)(?:Capability:|$)", details_text, re.IGNORECASE | re.DOTALL)
                motivation = mot_match.group(1).strip() if mot_match else "Unknown"
                
                # Capability
                cap_match = re.search(r"Capability:\s*(.+?)(?:Assets|Methods:|$)", details_text, re.IGNORECASE | re.DOTALL)
                capability = cap_match.group(1).strip() if cap_match else self._assess_threat_capability(actor_name)
                
                # Assets targeted
                assets_match = re.search(r"Assets.*?:\s*(.+?)(?:Methods:|Actor:|$)", details_text, re.IGNORECASE | re.DOTALL)
                assets_targeted = []
                if assets_match:
                    assets_text = assets_match.group(1)
                    assets_targeted = [a.strip() for a in re.findall(r"[-"]\s*(.+?)(?:\n|$)", assets_text)]
                
                # Methods
                methods_match = re.search(r"Methods:\s*(.+?)(?:Actor:|$)", details_text, re.IGNORECASE | re.DOTALL)
                methods = []
                if methods_match:
                    methods_text = methods_match.group(1)
                    methods = [m.strip() for m in re.findall(r"[-"]\s*(.+?)(?:\n|$)", methods_text)]
                
                threats.append({
                    "id": f"TP-{len(threats)+1:03d}",
                    "actor": actor_name,
                    "motivation": motivation,
                    "capability": capability,
                    "assets_targeted": assets_targeted,
                    "methods": methods
                })
                
        return threats
    
    def _parse_vulnerabilities(self, response: str) -> List[Dict[str, Any]]:
        """Parse vulnerabilities from response"""
        vulnerabilities = []
        
        # Look for vulnerabilities section
        vuln_section = re.search(r"VULNERABILITIES:(.*?)(?:RISK\s+ANALYSIS|$)", response, re.IGNORECASE | re.DOTALL)
        
        if vuln_section:
            content = vuln_section.group(1)
            
            # Parse vulnerability categories
            categories = ["Organizational", "Technical", "Physical"]
            
            for category in categories:
                # Find category section
                cat_pattern = rf"{category}.*?:(.*?)(?:{'|'.join(categories)}|RISK|$)"
                cat_match = re.search(cat_pattern, content, re.IGNORECASE | re.DOTALL)
                
                if cat_match:
                    cat_content = cat_match.group(1)
                    
                    # Parse individual vulnerabilities
                    vuln_pattern = r"V\d+:\s*(.+?)(?:Asset:|Severity:|V\d+:|$)"
                    for vuln_match in re.finditer(vuln_pattern, cat_content, re.MULTILINE | re.DOTALL):
                        vuln_desc = vuln_match.group(1).strip()
                        
                        # Extract details
                        details_text = cat_content[vuln_match.start():vuln_match.start()+500]
                        
                        # Asset
                        asset_match = re.search(r"Asset:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                        asset = asset_match.group(1).strip() if asset_match else "System-wide"
                        
                        # Severity
                        sev_match = re.search(r"Severity:\s*(\w+)", details_text, re.IGNORECASE)
                        severity = sev_match.group(1) if sev_match else self._assess_vulnerability_severity(vuln_desc)
                        
                        # Exploitability
                        exploit = self._assess_exploitability(vuln_desc, category)
                        
                        vulnerabilities.append({
                            "id": f"V-{len(vulnerabilities)+1:03d}",
                            "description": vuln_desc,
                            "category": category,
                            "asset": asset,
                            "severity": severity,
                            "exploitability": exploit
                        })
                        
        return vulnerabilities
    
    def _parse_risk_analysis(self, response: str) -> List[Dict[str, Any]]:
        """Parse risk analysis from response"""
        risks = []
        
        # Look for risk analysis section
        risk_section = re.search(r"RISK\s+ANALYSIS:(.*?)(?:PROTECTION\s+STRATEGY|$)", response, re.IGNORECASE | re.DOTALL)
        
        if risk_section:
            content = risk_section.group(1)
            
            # Parse individual risks
            risk_pattern = r"R\d+:\s*(.+?)(?:Asset:|Threat:|R\d+:|$)"
            for match in re.finditer(risk_pattern, content, re.MULTILINE | re.DOTALL):
                risk_desc = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+1000]
                
                # Asset
                asset_match = re.search(r"Asset:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                asset = asset_match.group(1).strip() if asset_match else "Unknown"
                
                # Threat
                threat_match = re.search(r"Threat:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                threat = threat_match.group(1).strip() if threat_match else "Various"
                
                # Vulnerability
                vuln_match = re.search(r"Vulnerability:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                vulnerability = vuln_match.group(1).strip() if vuln_match else "Multiple"
                
                # Impact
                impact_match = re.search(r"Impact:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                impact = impact_match.group(1).strip() if impact_match else self._assess_risk_impact(risk_desc)
                
                # Probability
                prob_match = re.search(r"Probability:\s*(\w+)", details_text, re.IGNORECASE)
                probability = prob_match.group(1) if prob_match else self._assess_risk_probability(threat, vulnerability)
                
                # Calculate risk level
                risk_level = self._calculate_risk_level(impact, probability)
                
                risks.append({
                    "id": f"R-{len(risks)+1:03d}",
                    "description": risk_desc,
                    "asset": asset,
                    "threat": threat,
                    "vulnerability": vulnerability,
                    "impact": impact,
                    "probability": probability,
                    "risk_level": risk_level
                })
                
        return risks
    
    def _parse_protection_strategy(self, response: str) -> Dict[str, Any]:
        """Parse protection strategy section"""
        content = "## OCTAVE Protection Strategy\n\n"
        
        # Look for protection strategy section
        strat_section = re.search(r"PROTECTION\s+STRATEGY:(.*?)$", response, re.IGNORECASE | re.DOTALL)
        
        if strat_section:
            strat_content = strat_section.group(1)
            
            # Extract organizational practices
            org_match = re.search(r"Organizational.*?:(.*?)(?:Technical:|$)", strat_content, re.IGNORECASE | re.DOTALL)
            if org_match:
                content += "### Organizational Practices\n"
                org_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", org_match.group(1), re.MULTILINE)
                for item in org_items:
                    content += f"- {item.strip()}\n"
                content += "\n"
            
            # Extract technical controls
            tech_match = re.search(r"Technical.*?:(.*?)(?:Near-term:|Long-term:|$)", strat_content, re.IGNORECASE | re.DOTALL)
            if tech_match:
                content += "### Technical Controls\n"
                tech_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", tech_match.group(1), re.MULTILINE)
                for item in tech_items:
                    content += f"- {item.strip()}\n"
                content += "\n"
            
            # Extract near-term actions
            near_match = re.search(r"Near-term.*?:(.*?)(?:Long-term:|$)", strat_content, re.IGNORECASE | re.DOTALL)
            if near_match:
                content += "### Near-term Actions (0-3 months)\n"
                near_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", near_match.group(1), re.MULTILINE)
                for item in near_items:
                    content += f"- {item.strip()}\n"
                content += "\n"
            
            # Extract long-term actions
            long_match = re.search(r"Long-term.*?:(.*?)$", strat_content, re.IGNORECASE | re.DOTALL)
            if long_match:
                content += "### Long-term Strategy (3-12 months)\n"
                long_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", long_match.group(1), re.MULTILINE)
                for item in long_items:
                    content += f"- {item.strip()}\n"
                content += "\n"
        
        # Add OCTAVE methodology recommendations
        content += """### OCTAVE Methodology Best Practices
- Regular asset criticality reviews
- Continuous threat landscape monitoring
- Vulnerability assessment cycles
- Risk-based security investment
- Business-aligned security metrics
- Cross-functional security teams
- Executive security briefings
"""
        
        mapper = TemplateMapper()
        return mapper.map_to_text(content, "markdown")
    
    def _create_risk_matrix(self, risks: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create risk matrix from risk analysis"""
        # Initialize matrix
        matrix = {
            "Low": {"Low": 0, "Medium": 0, "High": 0, "Critical": 0},
            "Medium": {"Low": 0, "Medium": 0, "High": 0, "Critical": 0},
            "High": {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        }
        
        # Populate matrix
        for risk in risks:
            probability = risk.get("probability", "Medium")
            impact = risk.get("impact", "Medium")
            
            if probability in matrix and impact in ["Low", "Medium", "High", "Critical"]:
                matrix[probability][impact] += 1
        
        # Convert to heat map format
        return mapper.map_to_heat_map(
            x_labels=["Low Impact", "Medium Impact", "High Impact", "Critical Impact"],
            y_labels=["High Probability", "Medium Probability", "Low Probability"],
            data=[
                [matrix["High"]["Low"], matrix["High"]["Medium"], matrix["High"]["High"], matrix["High"]["Critical"]],
                [matrix["Medium"]["Low"], matrix["Medium"]["Medium"], matrix["Medium"]["High"], matrix["Medium"]["Critical"]],
                [matrix["Low"]["Low"], matrix["Low"]["Medium"], matrix["Low"]["High"], matrix["Low"]["Critical"]]
            ],
            title="OCTAVE Risk Matrix"
        )
    
    def _classify_asset_type(self, name: str) -> str:
        """Classify asset type"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ["data", "database", "information"]):
            return "Information"
        elif any(word in name_lower for word in ["system", "application", "software"]):
            return "System"
        elif any(word in name_lower for word in ["service", "process", "function"]):
            return "Service"
        elif any(word in name_lower for word in ["people", "staff", "personnel"]):
            return "People"
        else:
            return "Technology"
    
    def _assess_asset_criticality(self, name: str, description: str) -> str:
        """Assess asset criticality"""
        combined = (name + " " + description).lower()
        
        if any(word in combined for word in ["critical", "essential", "vital", "core"]):
            return "Critical"
        elif any(word in combined for word in ["important", "significant", "key"]):
            return "High"
        elif any(word in combined for word in ["support", "auxiliary", "backup"]):
            return "Low"
        else:
            return "Medium"
    
    def _classify_concern_area(self, desc: str) -> str:
        """Classify area of concern"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["policy", "procedure", "governance"]):
            return "Organizational"
        elif any(word in desc_lower for word in ["technical", "system", "infrastructure"]):
            return "Technical"
        elif any(word in desc_lower for word in ["physical", "facility", "access"]):
            return "Physical"
        else:
            return "Operational"
    
    def _assess_concern_priority(self, desc: str, impact: str) -> str:
        """Assess concern priority"""
        desc_lower = desc.lower()
        impact_lower = impact.lower()
        
        if any(word in impact_lower for word in ["critical", "severe", "catastrophic"]):
            return "Critical"
        elif any(word in desc_lower for word in ["immediate", "urgent", "high"]):
            return "High"
        elif any(word in desc_lower for word in ["low", "minor", "minimal"]):
            return "Low"
        else:
            return "Medium"
    
    def _extract_asset_from_requirement(self, req: str) -> str:
        """Extract asset from requirement text"""
        # Look for asset references
        asset_match = re.search(r"(?:for|of|to)\s+(?:the\s+)?(\w+(?:\s+\w+)?)\s*(?:system|data|service)", req, re.IGNORECASE)
        if asset_match:
            return asset_match.group(1).strip()
        return "All assets"
    
    def _assess_requirement_priority(self, req: str, category: str) -> str:
        """Assess requirement priority"""
        req_lower = req.lower()
        
        # Critical categories get higher priority
        if category in ["Authentication", "Authorization"]:
            return "High"
        elif any(word in req_lower for word in ["critical", "essential", "mandatory"]):
            return "Critical"
        elif any(word in req_lower for word in ["should", "recommended"]):
            return "Medium"
        else:
            return "Low"
    
    def _assess_threat_capability(self, actor: str) -> str:
        """Assess threat actor capability"""
        actor_lower = actor.lower()
        
        if any(word in actor_lower for word in ["nation", "state", "apt"]):
            return "Very High"
        elif any(word in actor_lower for word in ["organized", "criminal", "group"]):
            return "High"
        elif any(word in actor_lower for word in ["insider", "employee"]):
            return "Medium-High"
        elif any(word in actor_lower for word in ["script", "amateur", "opportunistic"]):
            return "Low"
        else:
            return "Medium"
    
    def _assess_vulnerability_severity(self, desc: str) -> str:
        """Assess vulnerability severity"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["critical", "severe", "complete"]):
            return "Critical"
        elif any(word in desc_lower for word in ["high", "significant", "major"]):
            return "High"
        elif any(word in desc_lower for word in ["low", "minor", "minimal"]):
            return "Low"
        else:
            return "Medium"
    
    def _assess_exploitability(self, desc: str, category: str) -> str:
        """Assess vulnerability exploitability"""
        desc_lower = desc.lower()
        
        if category == "Organizational":
            return "Medium"  # Human factors
        elif any(word in desc_lower for word in ["remote", "unauthenticated", "public"]):
            return "High"
        elif any(word in desc_lower for word in ["local", "authenticated", "physical"]):
            return "Low"
        else:
            return "Medium"
    
    def _assess_risk_impact(self, desc: str) -> str:
        """Assess risk impact"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["critical", "catastrophic", "business ending"]):
            return "Critical"
        elif any(word in desc_lower for word in ["major", "significant", "serious"]):
            return "High"
        elif any(word in desc_lower for word in ["minor", "limited", "minimal"]):
            return "Low"
        else:
            return "Medium"
    
    def _assess_risk_probability(self, threat: str, vulnerability: str) -> str:
        """Assess risk probability based on threat and vulnerability"""
        combined = (threat + " " + vulnerability).lower()
        
        if any(word in combined for word in ["active", "exploited", "common", "frequent"]):
            return "High"
        elif any(word in combined for word in ["rare", "unlikely", "difficult"]):
            return "Low"
        else:
            return "Medium"
    
    def _calculate_risk_level(self, impact: str, probability: str) -> str:
        """Calculate overall risk level"""
        # Risk matrix calculation
        risk_matrix = {
            ("Critical", "High"): "Critical",
            ("Critical", "Medium"): "High",
            ("Critical", "Low"): "Medium",
            ("High", "High"): "High",
            ("High", "Medium"): "Medium",
            ("High", "Low"): "Low",
            ("Medium", "High"): "Medium",
            ("Medium", "Medium"): "Medium",
            ("Medium", "Low"): "Low",
            ("Low", "High"): "Low",
            ("Low", "Medium"): "Low",
            ("Low", "Low"): "Low"
        }
        
        return risk_matrix.get((impact, probability), "Medium")
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "assets" and section.status.value == "completed":
                artifacts.append({
                    "type": "critical_assets",
                    "name": "OCTAVE Critical Assets",
                    "data": section.content
                })
            elif section.section_id == "risk_analysis" and section.status.value == "completed":
                artifacts.append({
                    "type": "risk_assessment",
                    "name": "OCTAVE Risk Analysis",
                    "data": section.content
                })
            elif section.section_id == "threat_profiles" and section.status.value == "completed":
                artifacts.append({
                    "type": "threat_actors",
                    "name": "OCTAVE Threat Profiles",
                    "data": section.content
                })
                
        return artifacts
