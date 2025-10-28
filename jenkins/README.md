# ScanCode.io Jenkins Integration

Run [ScanCode.io](https://github.com/aboutcode-org/scancode.io) into your Jenkins CI/CD 
pipeline.

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Simple Example](#simple-example)
- [Specify Pipeline](#specify-pipeline)
- [Additional Resources](#additional-resources)

---

## Overview

This integration allows you to automatically scan your code as part of your Jenkins
pipeline:

- Scans your entire codebase using ScanCode.io
- Generates a comprehensive JSON report
- Archives the results as Jenkins build artifacts
- Runs automatically on every build

## Prerequisites

Before you begin, ensure you have:

1. **Jenkins installed and running**
   - Version 2.x or higher recommended

2. **Docker installed on your Jenkins agent**
   - Docker must be accessible to Jenkins
   - Test with: `docker --version`

3. **Required Jenkins Plugins**:
   - Docker Pipeline Plugin
   - Pipeline Plugin
   - Git Plugin (if using Git)

## Quick Start

### Step 1: Create a Jenkinsfile

Create a file named `Jenkinsfile` in the root of your repository with the following
content:

```groovy
pipeline {
    agent any
    
    stages {
        stage('ScanCode.io Scan') {
            steps {
                echo 'Running ScanCode.io scan...'
                
                sh '''
                    docker run --rm \
                      -v "${WORKSPACE}":/codedrop \
                      ghcr.io/aboutcode-org/scancode.io:latest \
                      run scan_codebase /codedrop \
                      > scancode_results.json
                '''
                
                echo 'Scan completed!'
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'scancode_results.json', fingerprint: true
                echo 'Results archived successfully'
            }
        }
    }
}
```

### Step 2: Access Your Results

After the build completes:
1. Go to the build page
2. Click on "Build Artifacts"
3. Download `scancode_results.json`

## Simple Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Scan') {
            steps {
                sh '''
                    docker run --rm \
                      -v "${WORKSPACE}":/codedrop \
                      ghcr.io/aboutcode-org/scancode.io:latest \
                      run scan_codebase /codedrop \
                      > scancode_results.json
                '''
                archiveArtifacts 'scancode_results.json'
            }
        }
    }
}
```

This minimal example:
- Runs the scan in a single stage
- Archives the results

## Specify Pipeline

Instead of `scan_codebase`, you can use other ScanCode.io pipelines:

- `scan_single_package` - For scanning a single package
- `analyse_docker_image` - For scanning Docker images
- `load_inventory` - For loading existing scan data

Example with a different pipeline:
```groovy
sh '''
    docker run --rm \
      -v "${WORKSPACE}":/codedrop \
      ghcr.io/aboutcode-org/scancode.io:latest \
      run analyse_docker_image docker://alpine:3.22.1 \
      > scancode_results.json
'''
```

## Additional Resources

- **ScanCode.io Documentation:** https://scancodeio.readthedocs.io/
- **ScanCode.io GitHub:** https://github.com/aboutcode-org/scancode.io
- **Jenkins Pipeline Documentation:** https://www.jenkins.io/doc/book/pipeline/
