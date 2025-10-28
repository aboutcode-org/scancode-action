# ScanCode.io GitLab CI/CD Integration

Run [ScanCode.io](https://github.com/aboutcode-org/scancode.io) into your GitLab CI/CD 
pipeline.

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Simple Example](#simple-example)
- [Specify Pipeline](#specify-pipeline)
- [Additional Resources](#additional-resources)

---

## Overview

This integration allows you to automatically scan your code as part of your GitLab
pipeline:

- Scans your entire codebase using ScanCode.io
- Generates a comprehensive JSON report
- Archives the results as GitLab pipeline artifacts
- Runs automatically on every build

## Quick Start

### Step 1: Create a .gitlab-ci.yml file

Create a file named `.gitlab-ci.yml` in the root of your repository with the following
content:

```yaml
# GitLab CI/CD Pipeline with ScanCode.io Integration

stages:
  - scan

# ScanCode.io Scan Job
scancode_scan:
  stage: scan
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_DRIVER: overlay2
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - echo "Running ScanCode.io scan..."
    
    # Run the scan and save results
    - |
      docker run --rm \
        -v "$(pwd)":/codedrop \
        ghcr.io/aboutcode-org/scancode.io:latest \
        run scan_codebase /codedrop \
        > scancode_results.json
    
    - echo "Scan completed!"
  
  artifacts:
    name: "scancode-results-${CI_COMMIT_SHORT_SHA}"
    paths:
      - scancode_results.json
    expire_in: 30 days
    when: always
```

### Step 2: Access Your Results

After the pipeline completes:
1. Go to your pipeline page
2. Click on the job name (`scancode_scan`)
3. On the right sidebar, click "Browse" under "Job artifacts"
4. Download `scancode_results.json`

Or download directly from the pipeline page using the download button.

## Specify Pipeline

Instead of `scan_codebase`, you can use other ScanCode.io pipelines:

- `scan_single_package` - For scanning a single package
- `analyse_docker_image` - For scanning Docker images
- `load_inventory` - For loading existing scan data

Example with a different pipeline:
```yaml
script:
  - |
    docker run --rm \
      -v "$(pwd)":/codedrop \
      ghcr.io/aboutcode-org/scancode.io:latest \
      run analyse_docker_image docker://alpine:3.22.1 \
      > scancode_results.json
```

## Additional Resources

- **ScanCode.io Documentation:** https://scancodeio.readthedocs.io/
- **ScanCode.io GitHub:** https://github.com/aboutcode-org/scancode.io
- **GitLab CI/CD Documentation:** https://docs.gitlab.com/ee/ci/
