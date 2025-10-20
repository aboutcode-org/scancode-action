# ScanCode.io Azure Pipeline Template

Run [ScanCode.io](https://github.com/aboutcode-org/scancode.io) pipelines from your Azure DevOps Pipelines.

- [Usage](#usage)
  - [Basic](#basic)
  - [Parameters](#parameters)
- [Examples](#examples)
  - [Scan repo codebase](#scan-repo-codebase)
  - [Run a specific pipeline](#run-a-specific-pipeline)
  - [Run multiple pipelines](#run-multiple-pipelines)
  - [Choose the output formats](#choose-the-output-formats)
  - [Provide download URLs inputs](#provide-download-urls-inputs)
  - [Fetch pipelines inputs](#fetch-pipelines-inputs)
  - [Check for compliance issues](#check-for-compliance-issues)
  - [Define a custom project name](#define-a-custom-project-name)
  - [Install ScanCode.io from a repository branch](#install-scancodeio-from-a-repository-branch)
- [Where does the scan results go?](#where-does-the-scan-results-go)

## Usage

### Basic

```yaml
stages:
  - stage: ScanCode
    jobs:
      - job: RunScanCode
        steps:
          - template: azure-pipelines/templates/scancode-template.yml@scancode-action
            parameters:
              pipelines: "scan_codebase"
              outputFormats: "json xlsx spdx cyclonedx"
```

### Parameters

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    # Names of the pipelines (comma-separated) and in order.
    # Default is 'scan_codebase'
    pipelines:

    # The list of output formats to generate.
    # Default is 'json xlsx spdx cyclonedx'
    outputFormats:

    # Relative path within the $(Build.SourcesDirectory) for pipeline inputs.
    # Default is '$(Build.SourcesDirectory)/scancode-inputs'
    inputsPath:

    # Provide one or more URLs to download for the pipeline run execution
    inputUrls:

    # Name of the project.
    # Default is 'scancode-devops'
    projectName:

    # Name of the outputs archive.
    # Default is 'scancode-outputs'
    outputsArchiveName:

    # Check for compliance issues in the project.
    # Exits with a non-zero status if compliance issues are detected.
    # Default is false
    checkCompliance:

    # Failure level for compliance check. Options: ERROR, WARNING, MISSING.
    # Default is 'ERROR'
    complianceFailLevel:
      
    # Exit with a non-zero status if known vulnerabilities are detected in discovered 
    # packages and dependencies.
    # Default is false
    complianceFailOnVulnerabilities:

    # Python version that will be installed to run ScanCode.io
    # Default is '3.12'
    pythonVersion:

    # Install ScanCode.io from a specific GitHub branch (optional)
    # Default is empty (uses latest PyPI release)
    scancodeioRepoBranch:
```

## Examples

### Scan repo codebase

```yaml
stages:
  - stage: ScanCode
    jobs:
      - job: RunScanCode
        steps:
          - template: azure-pipelines/templates/scancode-template.yml@scancode-action
```

### Run a specific pipeline

[Built-in pipelines list](https://scancodeio.readthedocs.io/en/latest/built-in-pipelines.html)

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    pipelines: "scan_codebase"
```

### Run multiple pipelines

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    pipelines: "scan_codebase,find_vulnerabilities"
  env:
    VULNERABLECODE_URL: https://public.vulnerablecode.io/
```

#### Configuring find_vulnerabilities Pipeline

The find_vulnerabilities pipeline requires access to a VulnerableCode instance, 
which can be defined using the VULNERABLECODE_URL environment variable.

In the example provided, a public instance is referenced. 
However, you also have the option to run your own VulnerableCode instance. 
For details on setting up and configuring your own instance, please refer to the 
[VulnerableCode documentation](https://vulnerablecode.readthedocs.io/en/latest/index.html).

#### Fail on known vulnerabilities

When enabled, the pipeline will fail if any known vulnerabilities are found in the 
project's discovered packages or dependencies.
Activate this behavior by enabling checkCompliance and setting 
complianceFailOnVulnerabilities to true.

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    pipelines: "scan_codebase,find_vulnerabilities"
    checkCompliance: true
    complianceFailOnVulnerabilities: true
  env:
    VULNERABLECODE_URL: https://public.vulnerablecode.io/
```

### Choose the output formats

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    outputFormats: "json xlsx spdx cyclonedx"
```

> [!NOTE]
> To specify a CycloneDX spec version (default to latest), use the syntax
  `cyclonedx:VERSION` as format value. For example: `cyclonedx:1.5`.

### Provide download URLs inputs

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    pipelines: "map_deploy_to_develop"
    inputUrls: "https://domain.url/source.zip#from https://domain.url/binaries.zip#to"
```

### Fetch pipelines inputs

```yaml
stages:
  - stage: ScanCode
    jobs:
      - job: RunScanCode
        steps:
          - script: |
              mkdir -p $(Build.SourcesDirectory)/scancode-inputs
              wget --directory-prefix=$(Build.SourcesDirectory)/scancode-inputs https://github.com/$(Build.Repository.Name)/archive/$(Build.SourceBranch).zip
            displayName: 'Download repository archive to scancode-inputs/ directory'
          - template: azure-pipelines/templates/scancode-template.yml@scancode-action
            parameters:
              pipelines: "scan_single_package"
```

### Check for compliance issues

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    checkCompliance: true
    complianceFailLevel: "WARNING"
```

> [!NOTE]
> This feature requires to provide Project policies. 
> For details on setting up and configuring your own instance, please refer to the 
> [ScanCode.io Policies documentation](https://scancodeio.readthedocs.io/en/latest/policies.html).

### Define a custom project name

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    projectName: "my-project-name"
```

### Install ScanCode.io from a repository branch

```yaml
- template: azure-pipelines/templates/scancode-template.yml@scancode-action
  parameters:
    scancodeioRepoBranch: "main"
```

## Where are the Scan Results?

Upon completion of the pipeline, you can **find the scan results** in the dedicated 
**pipeline artifacts section**. Navigate to your pipeline run summary page and look 
for the **Artifacts** tab. The scan results will be available as a published artifact 
named `scancode-outputs` (or your custom `outputsArchiveName` if specified). 
This artifact contains all the outputs generated by the ScanCode.io pipelines in the 
formats you specified.
