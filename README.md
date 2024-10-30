# `@nexB/scancode-action`

Run [ScanCode.io](https://github.com/aboutcode-org/scancode.io) pipelines from your 
Workflows.

> [!IMPORTANT]
> The scancode-action is currently in the **alpha stage**, and we invite you to 
> contribute to its improvement. Please feel free to submit bug reports or share 
> your ideas by creating new entries in the "Issues" section. 
> Your collaboration helps us enhance the action and ensures a more stable and 
> effective tool for the community. 
> Thank you for your support!

- [Usage](#usage)
  - [Basic](#basic)
  - [Inputs](#inputs)
- [Examples](#examples)
  - [Scan repo codebase](#scan-repo-codebase)
  - [Run a specific pipeline](#run-a-specific-pipeline)
  - [Run multiple pipelines](#run-multiple-pipelines)
  - [Choose the output formats](#choose-the-output-formats)
  - [Provide download URLs inputs](#provide-download-urls-inputs)
  - [Fetch pipelines inputs](#fetch-pipelines-inputs)
  - [Define a custom project name](#define-a-custom-project-name)
- [Where does the scan results go?](#where-does-the-scan-results-go)

## Usage

### Basic

```yaml
steps:
- uses: actions/checkout@v4
  with:
    path: scancode-inputs
- uses: nexB/scancode-action@alpha
  with:
    pipelines: "scan_codebase"
    output-formats: "json xlsx spdx cyclonedx"
```

### Inputs

```yaml
- uses: nexB/scancode-action@alpha
  with:
    # Names of the pipelines (comma-separated) and in order.
    # Default is 'scan_codebase'
    pipelines:

    # The list of output formats to generate.
    # Default is 'json xlsx spdx cyclonedx'
    output-formats:

    # Relative path within the $GITHUB_WORKSPACE for pipeline inputs.
    # Default is 'scancode-inputs'
    inputs-path:

    # Provide one or more URLs to download for the pipeline run execution
    input-urls:

    # Name of the project.
    # Default is 'scancode-action'
    project-name:

    # Name of the outputs archive.
    # Default is 'scancode-outputs'
    outputs-archive-name:

    # Python version that will be installed to run ScanCode.io
    # Default is '3.11'
    python-version:
```

## Examples

See https://github.com/aboutcode-org/scancode-action/tree/main/.github/workflows for 
Workflows examples.

### Scan repo codebase

```yaml
steps:
- uses: actions/checkout@v4
  with:
    path: scancode-inputs
- uses: nexB/scancode-action@alpha
```

### Run a specific pipeline

[Built-in pipelines list](https://scancodeio.readthedocs.io/en/latest/built-in-pipelines.html)

```yaml
- uses: nexB/scancode-action@alpha
  with:
    pipelines: "scan_codebase"
```

### Run multiple pipelines

```yaml
- uses: nexB/scancode-action@alpha
  with:
    pipelines: "scan_codebase,find_vulnerabilities"
  env:
    VULNERABLECODE_URL: https://public.vulnerablecode.io/
```

#### Configuring `find_vulnerabilities` Pipeline

The `find_vulnerabilities` pipeline requires access to a VulnerableCode instance, 
which can be defined using the `VULNERABLECODE_URL` environment variable.

In the example provided, a public instance is referenced. 
However, you also have the option to run your own VulnerableCode instance. 
For details on setting up and configuring your own instance, please refer to the 
[VulnerableCode documentation](https://vulnerablecode.readthedocs.io/en/latest/index.html).

### Choose the output formats

```yaml
- uses: nexB/scancode-action@alpha
  with:
    output-formats: "json xlsx spdx cyclonedx"
```

### Provide download URLs inputs

```yaml
- uses: nexB/scancode-action@alpha
  with:
    pipelines: "map_deploy_to_develop"
    input-urls:
      https://domain.url/source.zip#from
      https://domain.url/binaries.zip#to
```

### Fetch pipelines inputs

```yaml
- name: Download repository archive to scancode-inputs/ directory
  run: |
    wget --directory-prefix=scancode-inputs https://github.com/${GITHUB_REPOSITORY}/archive/${GITHUB_REF}.zip
- uses: nexB/scancode-action@alpha
  with:
    pipelines: "scan_single_package"
```

### Define a custom project name

```yaml
- uses: nexB/scancode-action@alpha
  with:
    project-name: "my-project-name"
```

## Where are the Scan Results?

Upon completion of the workflow, you can **find the scan results** in the dedicated 
**artifacts section** at the bottom of the workflow summary page. 
Look for a file named `scancode-outputs` in that section. 
This file contains the outputs generated by the `scancode-action`.
