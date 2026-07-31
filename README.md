# `@aboutcode-org/scancode-action`

Run [ScanCode.io](https://github.com/aboutcode-org/scancode.io) pipelines directly
from your **GitHub Workflows**.

> [!IMPORTANT]
> The scancode-action is currently in the **beta stage**, and we invite you to
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
  - [Specify pipeline options](#specify-pipeline-options)
  - [Choose the output formats](#choose-the-output-formats)
  - [Provide download URLs inputs](#provide-download-urls-inputs)
  - [Fetch pipelines inputs](#fetch-pipelines-inputs)
  - [Check for compliance issues](#check-for-compliance-issues)
  - [Define a custom project name](#define-a-custom-project-name)
  - [Use a specific ScanCode.io Docker image](#use-a-specific-scancodeio-docker-image)
  - [Install extra Python packages in the image](#install-extra-python-packages-in-the-image)
  - [Run source to binary mapping](#run-source-to-binary-mapping)
- [Where does the scan results go?](#where-are-the-scan-results)

## Usage

### Basic

```yaml
steps:
- uses: actions/checkout@v4
  with:
    path: scancode-inputs
- uses: aboutcode-org/scancode-action@beta
  with:
    pipelines: "scan_codebase"
    output-formats: "json xlsx spdx cyclonedx"
```

### Inputs

```yaml
- uses: aboutcode-org/scancode-action@beta
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

    # Check for compliance issues in the project.
    # Exits with a non-zero status if compliance issues are detected.
    # Default is false
    check-compliance:

    # Failure level for compliance check. Options: ERROR, WARNING, MISSING.
    # Default is 'ERROR'
    compliance-fail-level:
      
    # Exit with a non-zero status if known vulnerabilities are detected in discovered 
    # packages and dependencies.
    # Default is false
    compliance-fail-on-vulnerabilities:

    # ScanCode.io Docker image to use.
    scancodeio-image:

    # Extra Python packages to install on top of the ScanCode.io image
    # (comma-separated, e.g. minecode-pipelines).
    scancodeio-extra-packages:
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
- uses: aboutcode-org/scancode-action@beta
```

### Run a specific pipeline

[Built-in pipelines list](https://scancodeio.readthedocs.io/en/latest/built-in-pipelines.html)

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    pipelines: "scan_codebase"
```

### Run multiple pipelines

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    pipelines: "scan_codebase,find_vulnerabilities"
  env:
    VULNERABLECODE_URL: https://public.vulnerablecode.io/
```

### Specify pipeline options

Use the `pipeline_name:option1,option2` syntax to select optional steps for the
`map_deploy_to_develop` pipeline

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    pipelines: "map_deploy_to_develop:Java,JavaScript"
```

#### Configuring `find_vulnerabilities` Pipeline

The `find_vulnerabilities` pipeline requires access to a VulnerableCode instance,
which can be defined using the `VULNERABLECODE_URL` environment variable.

In the example provided, a public instance is referenced.
However, you also have the option to run your own VulnerableCode instance.
For details on setting up and configuring your own instance, please refer to the
[VulnerableCode documentation](https://vulnerablecode.readthedocs.io/en/latest/index.html).

#### Fail on known vulnerabilities

When enabled, the workflow will fail if any known vulnerabilities are found in the
project's discovered packages or dependencies.
Activate this behavior by enabling `check-compliance` and setting
`compliance-fail-on-vulnerabilities` to true.

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    pipelines: "scan_codebase,find_vulnerabilities"
    check-compliance: true
    compliance-fail-on-vulnerabilities: true
  env:
    VULNERABLECODE_URL: https://public.vulnerablecode.io/
```

### Choose the output formats

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    output-formats: "json xlsx spdx cyclonedx"
```

> [!NOTE]
> To specify a CycloneDX spec version (default to latest), use the syntax
  ``cyclonedx:VERSION`` as format value. For example: ``cyclonedx:1.5``.

### Provide download URLs inputs

```yaml
- uses: aboutcode-org/scancode-action@beta
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
- uses: aboutcode-org/scancode-action@beta
  with:
    pipelines: "scan_single_package"
```

### Check for compliance issues

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    check-compliance: true
    compliance-fail-level: "WARNING"
```

> [!NOTE]
> This feature requires to provide Project policies.
> For details on setting up and configuring your own instance, please refer to the
> [ScanCode.io Policies documentation](https://scancodeio.readthedocs.io/en/latest/policies.html).

### Define a custom project name

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    project-name: "my-project-name"
```

### Use a specific ScanCode.io Docker image

The action runs ScanCode.io from a pre-built Docker image. By default, it uses a
pinned release, but you can point it to another image or tag, for example to run
against the latest `main` build:

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    scancodeio-image: "ghcr.io/aboutcode-org/scancode.io:main"
```

### Install extra Python packages in the image

To run pipelines that are not part of the base image, such as `minecode_pipelines`
for PURL mining, provide the packages to install via `scancodeio-extra-packages`.
The action builds a local, throwaway image on top of `scancodeio-image` for this
run only:

```yaml
- uses: aboutcode-org/scancode-action@beta
  with:
    pipelines: "mine_pypi"
    scancodeio-extra-packages: "minecode-pipelines"
```

### Run source to binary mapping

Use this [workflow template](.github/workflows/map-deploy-to-develop-template.yml) for validating the integrity of open-source binary. It compares a project’s binary to its source code. Workflow will generate mapping between compiled binary and its original source code, which helps in spotting any malicious, unexpected, or otherwise undesirable code that may have made its way into the final binary.

#### To use follow these steps

1. In your workflow add job to build binary and upload it as a GitHub actions artifact.
2. Now add a second job to run source binary mapping using [template](.github/workflows/map-deploy-to-develop-template.yml).

   ```yaml
     map-source-binary:
       needs: # Job id from step 1
       uses: aboutcode-org/scancode-action/.github/workflows/map-deploy-to-develop-template.yml
       with:
         artifact-name: # Label of uploaded artifact from step 1
         steps: "python,java" # Comma separated optional steps. See https://scancodeio.readthedocs.io/en/latest/built-in-pipelines.html#map-deploy-to-develop
   ```

See an end-to-end working example for a python project [here](.github/workflows/map-source-binary-boolean-py.yml)

## Where are the Scan Results?

Upon completion of the workflow, you can **find the scan results** in the dedicated
**artifacts section** at the bottom of the workflow summary page.
Look for a file named `scancode-outputs` in that section.
This file contains the outputs generated by the `scancode-action`.
