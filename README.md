
# Behavioral Biometric Static Analysis (BBSA) System

The BBSA system is a containerized static analysis framework for detecting and classifying behavioral biometric scripts on the web using advanced taint analysis techniques. This system is part of a comprehensive web measurement pipeline described in "Tracking for Good: Finding Behavioral Biometrics on the Web using Static Taint Analysis" thesis.

## Overview

This system performs automated static analysis on JavaScript files to:
- **Detect Behavioral Biometric Scripts**: Identify scripts that collect user interaction data (mouse, keyboard, touch)
- **Classify Script Behavior**: Distinguish behavioral biometric scripts from analytics and session replay scripts
- **Extract Security Features**: Analyze data flows, aggregation patterns, and API usage
- **Generate ML Features**: Create vendor-agnostic features for machine learning classification

## System Architecture

The BBSA system operates as part of a distributed pipeline:

1. **VisibleV8 Crawler** → Discovers and forwards JavaScript files
2. **BBSA System** → Performs static analysis and classification
3. **Observability Stack** → Centralized logging and monitoring

## Prerequisites

- Docker and Docker Compose installed
- Access to VisibleV8 Crawler system for script forwarding
- Network connectivity for observability integration

## Quick Start

### 1. Navigate to Static Analysis Directory
```bash
cd static_analysis
```

### 2. Build and Start the System
```bash
docker-compose up --build
```

The system will start with **100 worker replicas** by default for high-throughput analysis.

### 3. Configure Worker Count (Optional)
To adjust the number of analysis workers, modify the `docker-compose.yml` file:

```yaml
services:
  worker:
    # ... other configuration
    deploy:
      replicas: 50  # Change this number based on your hardware
```

Recommended worker count: `Number of CPU cores / 2`

## Integration with VisibleV8 Crawler

The BBSA system is designed to work with the [VisibleV8 Crawler](https://github.com/aswad546/visiblev8-crawler) pipeline:

### Port Forwarding Setup
If running on separate machines, forward the required ports:

```bash
# Forward VisibleV8 scripts to BBSA system
ssh -L 8100:localhost:8100 user@bbsa-server

# Forward VV8 database access to BBSA system  
ssh -L 5434:localhost:5434 user@vv8-server

# Forward Loki logging (see observability config)
ssh -L 3100:localhost:3100 user@logging-server
```

### API Endpoint
The system listens on **port 8100** for incoming JavaScript analysis requests from the VisibleV8 Crawler.

## Core Functionality

### Static Taint Analysis
- **Program Dependency Graph (PDG) Construction**: Creates detailed code structure representations
- **Data Flow Tracing**: Tracks behavioral data from sources to sinks
- **API Aggregation Analysis**: Identifies points where multiple behavioral APIs converge
- **Vendor-Agnostic Feature Extraction**: Generates features independent of specific implementations

### Machine Learning Classification
- **Random Forest Classifier**: Trained on vendor-agnostic features
- **Behavioral vs Non-Behavioral**: Distinguishes biometric scripts from other categories
- **Vendor Generalization**: Detects scripts from previously unseen providers
- **High Accuracy**: 93.2% accuracy with 97.7% ROC-AUC performance

### Supported Analysis Features
- **Behavioral Source APIs**: Mouse, keyboard, touch, device motion events
- **Fingerprinting APIs**: Navigator, screen, canvas, audio fingerprinting vectors
- **Data Sinks**: Network transmission, storage, DOM manipulation endpoints
- **Aggregation Patterns**: Complex data combination and processing flows

## Configuration

### Environment Variables
The system uses environment-based configuration for flexibility:

```bash
# Database connections
VV8_DB_HOST=localhost
VV8_DB_PORT=5434
VV8_DB_NAME=vv8_backend

# Analysis parameters
WORKER_TIMEOUT=420  # 7 minutes per script analysis
GRAPH_CONSTRUCTION_TIMEOUT=420
PARALLEL_WORKERS=100

# Observability
LOKI_ENDPOINT=http://localhost:3100
LOG_LEVEL=INFO
```

### Docker Compose Configuration
Key services in the system:

```yaml
services:
  api:
    # FastAPI server listening on port 8100
    ports:
      - "8100:8100"
  
  worker:
    # Analysis workers with configurable replicas
    deploy:
      replicas: 100
  
  redis:
    # Task queue for distributed processing
  
  postgres:
    # Results storage and caching
```

## Monitoring and Observability

### Centralized Logging
All analysis logs are forwarded to **Loki** for centralized aggregation:
- Analysis progress and results
- Error tracking and debugging
- Performance metrics
- Classification outcomes

### Integration with Observability Stack
The system integrates with the observability infrastructure in the VisibleV8 Crawler repository:
- **Loki**: Centralized log aggregation
- **Prometheus**: Metrics collection  
- **Grafana**: Dashboard visualization
- **Jaeger**: Distributed tracing (when applicable)

## Performance Characteristics

### Throughput
- **100 concurrent workers** (default configuration)
- **~8-10 scripts per minute per worker** (depending on script complexity)
- **Automatic scaling** based on available CPU resources

### Analysis Accuracy
- **Graph Construction Success**: 92%+ for typical JavaScript files
- **Classification Accuracy**: 93.2% overall accuracy
- **Vendor Generalization**: 72.7% recall on unseen vendors
- **False Positive Rate**: <5% in production deployments

## Research Applications

This system enables large-scale empirical studies:
- **Web Measurement**: Analyze prevalence of behavioral biometrics across millions of websites
- **Vendor Discovery**: Identify new behavioral biometric providers automatically  
- **Security Analysis**: Assess data collection practices and privacy implications
- **Longitudinal Studies**: Track evolution of behavioral biometric deployments

## API Reference

### Script Analysis Endpoint
```bash
POST http://localhost:8100/analyze
Content-Type: application/json

{
  "script_url": "https://example.com/script.js",
  "script_content": "JavaScript code content",
  "submission_id": "unique_identifier",
  "domain": "example.com"
}
```

### Health Check
```bash
GET http://localhost:8100/health
```

### Metrics Endpoint
```bash
GET http://localhost:8100/metrics
```

## Development and Debugging

### Local Development Setup
For development without Docker:

```bash
# Install dependencies
npm install
pip3 install -r requirements.txt

# Run single analysis
python3 static.py --export filename

# Enable Redis queue for batch processing
python queue_worker.py
```

### Debug Configuration
Modify `.env` for debugging:
```bash
# Write mode: "immediate" or "batch"
DB_WRITE_MODE=immediate
LOG_LEVEL=DEBUG
WORKER_TIMEOUT=600  # Extended timeout for debugging
```

## Troubleshooting

### Common Issues

#### Graph Construction Failures
- **Cause**: Heavily obfuscated or syntactically invalid JavaScript
- **Solution**: System automatically falls back to API-only analysis
- **Monitoring**: Check Loki logs for `graph_construction_failed` events

#### High Memory Usage
- **Cause**: Large JavaScript files or complex dependency graphs
- **Solution**: Reduce worker replica count or increase container memory limits
- **Configuration**: Adjust `--memory` limits in docker-compose.yml

#### Database Connection Issues
- **Cause**: VV8 database not accessible or port forwarding misconfigured
- **Solution**: Verify port 5434 forwarding and database connectivity
- **Debug**: Check container logs for database connection errors

### Performance Tuning

```bash
# Monitor worker performance
docker stats

# View analysis logs
docker-compose logs -f worker

# Check Redis queue status
docker-compose exec redis redis-cli monitor
```

## Integration Notes

This system is specifically designed to integrate with:
- **LoginGPT**: Enhanced login page discovery system
- **VisibleV8 Crawler**: Large-scale web crawling infrastructure  
- **Observability Stack**: Comprehensive monitoring and analysis tools

For complete pipeline deployment, refer to the [VisibleV8 Crawler documentation](https://github.com/aswad546/visiblev8-crawler) for coordinated system setup and configuration.

## Research Citation

This system implements the methodology described in:
> "Tracking for Good: Finding Behavioral Biometrics on the Web using Static Taint Analysis" 
> *Thesis research on large-scale behavioral biometric measurement and detection*

The BBSA system represents a significant advancement in automated web security analysis, enabling researchers and practitioners to systematically identify and analyze behavioral biometric deployments across the modern web at unprecedented scale.
```
