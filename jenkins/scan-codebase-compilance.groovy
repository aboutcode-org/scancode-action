// ScanCode.io codebase scan with compliance check
// Mirrors: azure-pipelines/examples/scan-codebase-compliance.yml

@Library('scancode-action') _

pipeline {
    agent any

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
                        pipelines: 'scan_codebase',
                        checkCompliance: true,
                        complianceFailLevel: 'WARNING'
                    )
                }
            }
        }
    }
}