# Example Systems

This directory contains example system configurations for STPA-Sec Step 1 analysis.

## Available Examples

### aws-ref-arch
AWS reference architecture example with configuration file.

### databricks
Databricks deployment on AWS with architecture diagram.
- `MWS_AWS_Architecture.png` - System architecture diagram
- `config.yaml` - Analysis configuration

### ecommerce-multi-file
E-commerce system demonstrating multi-file input capability.
- Multiple PDF files showing before/after architecture
- Pain points documentation
- `config.yaml` - Multi-file input configuration

### medical-drone-fleet
Medical drone fleet system for emergency response.
- `medical-drone-fleet.txt` - System description
- `config.yaml` - Analysis configuration

### sd-wan
Software-Defined WAN deployment example.
- `sd-wan-deployment-models-ra.pdf` - Reference architecture PDF
- `config.yaml` - Analysis configuration

### smart-grid
Smart electrical grid system example.
- `smart-grid.txt` - Detailed system description
- `description.txt` - Additional system details
- `config.yaml` - Analysis configuration

## Usage

To run an analysis on any example:

```bash
./ai-sec analyze --config example_systems/<example-name>/config.yaml
```

For enhanced mode with multiple cognitive styles:

```bash
./ai-sec analyze --config example_systems/<example-name>/config.yaml --enhanced
```

To override input files from command line:

```bash
./ai-sec analyze --config example_systems/<example-name>/config.yaml --input file1.pdf file2.txt
```