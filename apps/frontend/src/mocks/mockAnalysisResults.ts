export function generateMockAnalysisResults(frameworks: string[]) {
  const results: Record<string, any> = {};
  
  // Generate mock results for each selected framework
  frameworks.forEach(framework => {
    results[framework] = {
      status: 'completed',
      summary: {
        criticalFindings: Math.floor(Math.random() * 3),
        highFindings: Math.floor(Math.random() * 5) + 2,
        mediumFindings: Math.floor(Math.random() * 10) + 5,
        lowFindings: Math.floor(Math.random() * 15) + 10
      },
      sections: [
        {
          id: 'overview',
          title: 'Overview',
          content: {
            description: `${framework.toUpperCase()} analysis completed successfully.`
          }
        }
      ]
    };
  });
  
  return results;
}