export function getSectionUrl(id: string): string {
  // Handle IDs like 'stpa-sec-control-diagram' where 'stpa-sec' is the analysis type
  // and 'control-diagram' is the section ID
  
  // Known analysis types
  const analysisTypes = ['stpa-sec', 'stride', 'pasta', 'dread', 'maestro', 'linddun', 'hazop', 'octave'];
  
  // Find which analysis type this ID starts with
  const analysisType = analysisTypes.find(type => id.startsWith(type + '-'));
  
  if (!analysisType) {
    // Fallback to old logic if no known analysis type found
    const parts = id.split('-');
    if (parts.length < 2) return '#';
    return `/analysis/template/${parts[0]}/${parts.slice(1).join('-')}`;
  }
  
  // Extract section ID by removing the analysis type prefix
  const sectionId = id.substring(analysisType.length + 1);
  
  return `/analysis/template/${analysisType}/${sectionId}`;
}