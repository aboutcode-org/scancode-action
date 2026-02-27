// ScanCode.io scan with vulnerability detection
// Mirrors: azure-pipelines/examples/scan-codebase-vulnerabilities.yml

@Library('scancode-action') _

pipeline {
    agent any

    environment {
        VULNERABLECODE_URL = 'https://public.vulnerablecode.io/'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: scm.branches,
                    extensions: [
                        [$class: 'RelativeTargetDirectory',
                         relativeTargetDir: 'scancode-inputs']
                    ],
                    userRemoteConfigs: scm.userRemoteConfigs
                ])
            }
        }

        stage('ScanCode') {
            steps {
                script {
                    scancodeTemplate(
                        pipelines: 'scan_codebase,find_vulnerabilities',
                        checkCompliance: true,
                        complianceFailOnVulnerabilities: true
                    )
                }
            }
        }
    }
}