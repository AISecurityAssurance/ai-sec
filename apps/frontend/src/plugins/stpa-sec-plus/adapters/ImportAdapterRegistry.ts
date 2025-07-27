/**
 * Import Adapter Registry
 * 
 * Manages all import adapters for different security analysis tool formats
 */

import type { AnalysisImportAdapter } from '../types';
import { MicrosoftTMTAdapter } from './MicrosoftTMTAdapter';
import { STRIDECSVAdapter } from './STRIDECSVAdapter';
import { PASTAJSONAdapter } from './PASTAJSONAdapter';
import { GenericCSVAdapter } from './GenericCSVAdapter';

export class ImportAdapterRegistry {
  private adapters: Map<string, AnalysisImportAdapter> = new Map();
  
  constructor() {
    // Initialize with empty registry
  }
  
  // Load all built-in adapters
  async loadBuiltInAdapters(): Promise<void> {
    // Register Microsoft TMT adapter
    this.registerAdapter('microsoft-tmt', new MicrosoftTMTAdapter());
    
    // Register STRIDE CSV adapter
    this.registerAdapter('stride-csv', new STRIDECSVAdapter());
    
    // Register PASTA JSON adapter
    this.registerAdapter('pasta-json', new PASTAJSONAdapter());
    
    // Register Generic CSV adapter
    this.registerAdapter('generic-csv', new GenericCSVAdapter());
    
    // Future adapters can be added here:
    // - OCTAVE XML adapter
    // - NIST CSF Excel adapter
    // - ISO 27001 checklist adapter
    // - LINDDUN privacy adapter
    // - DREAD scoring adapter
  }
  
  // Register a new adapter
  registerAdapter(format: string, adapter: AnalysisImportAdapter): void {
    if (!format || !adapter) {
      throw new Error('Format and adapter are required');
    }
    
    this.adapters.set(format, adapter);
  }
  
  // Get adapter by format
  getAdapter(format: string): AnalysisImportAdapter | undefined {
    return this.adapters.get(format);
  }
  
  // Check if format is supported
  isFormatSupported(format: string): boolean {
    return this.adapters.has(format);
  }
  
  // Get all supported formats
  getSupportedFormats(): string[] {
    return Array.from(this.adapters.keys());
  }
  
  // Auto-detect format from file extension or content
  async detectFormat(file: File | string, content?: any): Promise<string | null> {
    // If it's a file, check extension
    if (file instanceof File) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      
      switch (extension) {
        case 'tm7':
          return 'microsoft-tmt';
        case 'csv':
          // Need to inspect content to determine CSV type
          return await this.detectCSVFormat(content);
        case 'json':
          // Need to inspect content to determine JSON type
          return await this.detectJSONFormat(content);
        case 'xml':
          return await this.detectXMLFormat(content);
        case 'xlsx':
        case 'xls':
          return await this.detectExcelFormat(content);
        default:
          return null;
      }
    }
    
    // If it's content, try to detect from structure
    if (content) {
      return await this.detectFromContent(content);
    }
    
    return null;
  }
  
  // Detect CSV format from content
  private async detectCSVFormat(content: any): Promise<string> {
    if (!content) return 'generic-csv';
    
    // Check for STRIDE-specific headers
    const strideHeaders = ['Threat', 'Category', 'Asset', 'Mitigation'];
    const hasSTRIDEHeaders = strideHeaders.every(header => 
      content.includes(header)
    );
    
    if (hasSTRIDEHeaders) {
      return 'stride-csv';
    }
    
    return 'generic-csv';
  }
  
  // Detect JSON format from content
  private async detectJSONFormat(content: any): Promise<string> {
    if (!content) return 'custom-json';
    
    try {
      const parsed = typeof content === 'string' ? JSON.parse(content) : content;
      
      // Check for PASTA structure
      if (parsed.businessObjectives && parsed.technicalScope) {
        return 'pasta-json';
      }
      
      // Check for Microsoft TMT JSON export
      if (parsed.elements && parsed.flows && parsed.threats) {
        return 'microsoft-tmt';
      }
      
      // Check for OCTAVE structure
      if (parsed.criticalAssets && parsed.containers) {
        return 'octave-json';
      }
      
      return 'custom-json';
    } catch {
      return 'custom-json';
    }
  }
  
  // Detect XML format from content
  private async detectXMLFormat(content: any): Promise<string> {
    if (!content) return 'custom-xml';
    
    // Check for OCTAVE Allegro XML
    if (content.includes('<octave-allegro>') || content.includes('<critical-assets>')) {
      return 'octave-xml';
    }
    
    return 'custom-xml';
  }
  
  // Detect Excel format from content
  private async detectExcelFormat(content: any): Promise<string> {
    // This would need to inspect the actual Excel content
    // For now, return generic Excel format
    
    // In real implementation, would check sheet names and structure
    // to detect NIST CSF, ISO 27001, etc.
    
    return 'excel-generic';
  }
  
  // Detect format from content structure
  private async detectFromContent(content: any): Promise<string | null> {
    // Try JSON detection
    if (typeof content === 'object') {
      return await this.detectJSONFormat(content);
    }
    
    // Try CSV detection
    if (typeof content === 'string' && content.includes(',')) {
      return await this.detectCSVFormat(content);
    }
    
    // Try XML detection
    if (typeof content === 'string' && content.includes('<')) {
      return await this.detectXMLFormat(content);
    }
    
    return null;
  }
  
  // Get adapter capabilities
  getAdapterCapabilities(format: string): any {
    const adapter = this.getAdapter(format);
    if (!adapter) return null;
    
    return {
      format: adapter.format,
      version: adapter.version,
      canValidate: true,
      canTransform: true,
      canMapEntities: true,
      canExtractRisks: true
    };
  }
  
  // Batch import multiple files
  async batchImport(files: Array<{file: File, format?: string}>): Promise<any[]> {
    const results = [];
    
    for (const item of files) {
      try {
        const format = item.format || await this.detectFormat(item.file);
        if (!format) {
          results.push({
            file: item.file.name,
            success: false,
            error: 'Could not detect format'
          });
          continue;
        }
        
        const adapter = this.getAdapter(format);
        if (!adapter) {
          results.push({
            file: item.file.name,
            success: false,
            error: `No adapter for format: ${format}`
          });
          continue;
        }
        
        const content = await item.file.text();
        const data = format.includes('json') ? JSON.parse(content) : content;
        
        const validation = await adapter.validate(data);
        if (!validation.isValid) {
          results.push({
            file: item.file.name,
            success: false,
            errors: validation.errors,
            warnings: validation.warnings
          });
          continue;
        }
        
        const transformed = await adapter.transform(data);
        results.push({
          file: item.file.name,
          success: true,
          data: transformed
        });
      } catch (error) {
        results.push({
          file: item.file.name,
          success: false,
          error: error.message
        });
      }
    }
    
    return results;
  }
}