/**
 * STPA-Sec API Service
 * Handles all API calls to the STPA-Sec backend endpoints
 */
import { apiFetch } from '../config/api';
import type {
  Loss,
  Hazard,
  Controller,
  ControlAction,
  UCA,
  CausalScenario,
  Mitigation,
  Entity,
  Relationship,
  Adversary,
  SystemDefinition
} from '../types/analysis';

export interface ControlStructure {
  entities: Entity[];
  relationships: Relationship[];
}

export interface RiskSummary {
  summary: {
    total_hazards: number;
    high_risk_scenarios: number;
    total_scenarios: number;
    total_mitigations: number;
    mitigation_coverage: number;
  };
  risk_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  top_risks: Array<{
    scenario_id: string;
    description: string;
    impact: string;
    likelihood: string;
  }>;
}

class StpaSecApiService {
  private baseUrl = '/api/v1/stpa-sec';

  async getSystemDefinition(): Promise<SystemDefinition | null> {
    try {
      const response = await apiFetch(`${this.baseUrl}/system-definition`);
      if (!response.ok) {
        console.error('Failed to fetch system definition');
        return null;
      }
      return response.json();
    } catch (error) {
      console.error('Error fetching system definition:', error);
      return null;
    }
  }

  async getLosses(stakeholderId?: string): Promise<Loss[]> {
    try {
      const url = stakeholderId 
        ? `${this.baseUrl}/losses?stakeholder_id=${stakeholderId}`
        : `${this.baseUrl}/losses`;
      
      const response = await apiFetch(url);
      if (!response.ok) {
        console.error('Failed to fetch losses');
        return [];
      }
      
      const data = await response.json();
      // Transform API response to match frontend Loss interface
      return data.map((loss: any) => ({
        id: loss.id,
        description: loss.description,
        type: loss.impact_type || 'financial',
        severity: loss.severity,
        stakeholders: loss.stakeholder_refs || []
      }));
    } catch (error) {
      console.error('Error fetching losses:', error);
      return [];
    }
  }

  async getHazards(lossId?: string): Promise<Hazard[]> {
    try {
      const url = lossId 
        ? `${this.baseUrl}/hazards?loss_id=${lossId}`
        : `${this.baseUrl}/hazards`;
      
      const response = await apiFetch(url);
      if (!response.ok) {
        console.error('Failed to fetch hazards');
        return [];
      }
      
      const data = await response.json();
      // Transform API response to match frontend Hazard interface
      return data.map((hazard: any) => ({
        id: hazard.id,
        description: hazard.description,
        losses: hazard.loss_refs || [],
        systemState: hazard.worst_case_scenario || '',
        constraints: []  // Not available in current API
      }));
    } catch (error) {
      console.error('Error fetching hazards:', error);
      return [];
    }
  }

  async getControlStructure(): Promise<ControlStructure> {
    try {
      const response = await apiFetch(`${this.baseUrl}/control-structure`);
      if (!response.ok) {
        console.error('Failed to fetch control structure');
        return { entities: [], relationships: [] };
      }
      
      const data = await response.json();
      
      // Transform entities to match frontend Controller interface
      const controllers: Controller[] = data.entities
        .filter((e: any) => e.type === 'controller')
        .map((entity: any) => ({
          id: entity.id,
          name: entity.name,
          type: 'controller' as const,
          description: entity.description || '',
          responsibilities: entity.responsibilities || []
        }));
      
      // Transform relationships to match frontend ControlAction interface
      const controlActions: ControlAction[] = data.relationships.map((rel: any, index: number) => ({
        id: rel.id || `ca-${index}`,
        from: rel.source,
        to: rel.target,
        description: rel.control_actions?.[0] || rel.type,
        type: rel.type === 'feedback' ? 'feedback' : 'control'
      }));
      
      return {
        entities: controllers,
        relationships: controlActions
      };
    } catch (error) {
      console.error('Error fetching control structure:', error);
      return { entities: [], relationships: [] };
    }
  }

  async getEntities(entityType?: string): Promise<Entity[]> {
    try {
      const url = entityType 
        ? `${this.baseUrl}/entities?entity_type=${entityType}`
        : `${this.baseUrl}/entities`;
      
      const response = await apiFetch(url);
      if (!response.ok) {
        console.error('Failed to fetch entities');
        return [];
      }
      
      return response.json();
    } catch (error) {
      console.error('Error fetching entities:', error);
      return [];
    }
  }

  async getScenarios(minImpact?: string): Promise<CausalScenario[]> {
    try {
      const url = minImpact 
        ? `${this.baseUrl}/scenarios?min_impact=${minImpact}`
        : `${this.baseUrl}/scenarios`;
      
      const response = await apiFetch(url);
      if (!response.ok) {
        console.error('Failed to fetch scenarios');
        return [];
      }
      
      const data = await response.json();
      // Transform API response to match frontend CausalScenario interface
      return data.map((scenario: any) => ({
        id: scenario.id,
        ucaId: scenario.uca_refs?.[0] || '',
        hazardId: scenario.hazard_refs?.[0] || '',
        description: scenario.description,
        causalFactors: scenario.contributing_factors || [],
        mitigations: []  // Will be populated separately
      }));
    } catch (error) {
      console.error('Error fetching scenarios:', error);
      return [];
    }
  }

  async getMitigations(effectiveness?: string): Promise<Mitigation[]> {
    try {
      const url = effectiveness 
        ? `${this.baseUrl}/mitigations?effectiveness=${effectiveness}`
        : `${this.baseUrl}/mitigations`;
      
      const response = await apiFetch(url);
      if (!response.ok) {
        console.error('Failed to fetch mitigations');
        return [];
      }
      
      const data = await response.json();
      // Transform API response to match frontend Mitigation interface
      return data.map((mitigation: any) => ({
        id: mitigation.id,
        name: mitigation.name,
        description: mitigation.description,
        type: mitigation.type,
        effectiveness: mitigation.effectiveness,
        cost: mitigation.cost_estimate || {},
        implementationDifficulty: mitigation.implementation_difficulty,
        scenarios: []  // Not directly available in API response
      }));
    } catch (error) {
      console.error('Error fetching mitigations:', error);
      return [];
    }
  }

  async getAdversaries(sophistication?: string): Promise<Adversary[]> {
    try {
      const url = sophistication 
        ? `${this.baseUrl}/adversaries?sophistication=${sophistication}`
        : `${this.baseUrl}/adversaries`;
      
      const response = await apiFetch(url);
      if (!response.ok) {
        console.error('Failed to fetch adversaries');
        return [];
      }
      
      return response.json();
    } catch (error) {
      console.error('Error fetching adversaries:', error);
      return [];
    }
  }

  async getRiskSummary(): Promise<RiskSummary | null> {
    try {
      const response = await apiFetch(`${this.baseUrl}/risk-summary`);
      if (!response.ok) {
        console.error('Failed to fetch risk summary');
        return null;
      }
      return response.json();
    } catch (error) {
      console.error('Error fetching risk summary:', error);
      return null;
    }
  }

  /**
   * Load all STPA-Sec data for initial analysis
   */
  async loadAnalysisData() {
    try {
      // Fetch all data in parallel for better performance
      const [
        systemDefinition,
        losses,
        hazards,
        controlStructure,
        scenarios,
        mitigations,
        adversaries
      ] = await Promise.all([
        this.getSystemDefinition(),
        this.getLosses(),
        this.getHazards(),
        this.getControlStructure(),
        this.getScenarios(),
        this.getMitigations(),
        this.getAdversaries()
      ]);

      // Transform control structure into controllers and control actions
      const controllers = controlStructure.entities as Controller[];
      const controlActions = controlStructure.relationships as unknown as ControlAction[];

      // Create placeholder UCAs since they're not directly available from the API
      const ucas: UCA[] = [];

      return {
        systemDefinition,
        losses,
        hazards,
        controllers,
        controlActions,
        ucas,
        causalScenarios: scenarios,
        mitigations,
        adversaries
      };
    } catch (error) {
      console.error('Error loading analysis data:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const stpaSecApiService = new StpaSecApiService();