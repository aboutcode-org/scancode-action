def call(Map config = [:]) {
    def defaults = [
        pipelines: 'scan_codebase',
        outputFormats: 'json xlsx spdx cyclonedx',
        inputsPath: 'scancode-inputs',
        inputUrls: '',
        projectName: 'scancode-jenkins',
        outputsArchiveName: 'scancode-outputs',
        checkCompliance: false,
        complianceFailLevel: 'ERROR',
        complianceFailOnVulnerabilities: false,
        pythonVersion: '3.12',
        scancodeioBranch: ''
    ]

    def settings = defaults + config

    def scanCodeEnv = [
        "SECRET_KEY=${generateSecretKey()}",
        "SCANCODEIO_DB_NAME=scancodeio",
        "SCANCODEIO_DB_USER=scancodeio", 
        "SCANCODEIO_DB_PASSWORD=scancodeio"
    ]
    
    try {
        stage('Setup Environment') {
            setupPython(settings.pythonVersion)
            setupPostgreSQL(scanCodeEnv)
            installScanCodeIO(settings.scancodeioBranch)
        }
        
        stage('Prepare Database') {
            withEnv(scanCodeEnv) {
                sh 'scanpipe migrate --verbosity 0'
            }
        }
        
        stage('Create Project') {
            withEnv(scanCodeEnv) {
                def pipelineCLIArgs = generatePipelineArgs(settings.pipelines)
                def inputUrlCLIArgs = generateInputUrlArgs(settings.inputUrls)
                
                sh """
                    scanpipe create-project ${settings.projectName} \\
                    ${pipelineCLIArgs} \\
                    ${inputUrlCLIArgs}
                """
                
                def projectStatus = sh(
                    script: "scanpipe status --project ${settings.projectName}",
                    returnStdout: true
                ).trim()
                
                def workDirectory = extractWorkDirectory(projectStatus)
                env.PROJECT_WORK_DIRECTORY = workDirectory
            }
        }
        
        stage('Copy Input Files') {
            copyInputFiles(settings.inputsPath, env.PROJECT_WORK_DIRECTORY)
        }
        
        stage('Run ScanCode Pipelines') {
            withEnv(scanCodeEnv) {
                sh "scanpipe execute --project ${settings.projectName} --no-color"
            }
        }
        
        stage('Generate Outputs') {
            withEnv(scanCodeEnv) {
                sh """
                    scanpipe output \\
                    --project ${settings.projectName} \\
                    --format ${settings.outputFormats}
                """
            }
        }
        
        stage('Archive Outputs') {
            archiveArtifacts(
                artifacts: "${env.PROJECT_WORK_DIRECTORY}/output/*",
                allowEmptyArchive: false,
                fingerprint: true
            )
        }
        
        if (settings.checkCompliance) {
            stage('Check Compliance') {
                checkCompliance(
                    settings.projectName,
                    settings.complianceFailLevel,
                    settings.complianceFailOnVulnerabilities,
                    scanCodeEnv
                )
            }
        }
        
        echo "ScanCode.io pipeline completed successfully"
        
    } catch (Exception e) {
        error "ScanCode.io pipeline failed: ${e.getMessage()}"
    }
}

def setupPython(pythonVersion) {
    echo "Setting up Python ${pythonVersion}"

    sh """
        sudo apt-get update

        sudo apt-get install -y python${pythonVersion} python${pythonVersion}-pip python${pythonVersion}-venv

        sudo ln -sf /usr/bin/python${pythonVersion} /usr/bin/python3
        sudo ln -sf /usr/bin/pip${pythonVersion} /usr/bin/pip3

        python3 --version
        pip3 --version
    """
}

def setupPostgreSQL(scanCodeEnv) {
    echo "Setting up PostgreSQL"
    
    withEnv(scanCodeEnv) {
        sh """

            sudo apt-get install -y postgresql postgresql-contrib
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            
            sudo -u postgres createuser --no-createrole --no-superuser --login --inherit --createdb \$SCANCODEIO_DB_USER || true
            sudo -u postgres psql -c "ALTER USER \$SCANCODEIO_DB_USER WITH encrypted password '\$SCANCODEIO_DB_PASSWORD'"
            sudo -u postgres createdb --owner=\$SCANCODEIO_DB_USER --encoding=UTF-8 \$SCANCODEIO_DB_NAME || true
        """
    }
}

def installScanCodeIO(branch) {
    echo "Installing ScanCode.io"
    
    if (branch) {
        echo "Installing ScanCode.io from branch: ${branch}"
        sh "pip3 install git+https://github.com/aboutcode-org/scancode.io.git@${branch}"
    } else {
        echo "Installing latest ScanCode.io release from PyPI"
        sh "pip3 install --upgrade scancodeio"
    }
}

def generatePipelineArgs(pipelines) {
    def pipelineList = pipelines.split(',')
    def args = ""
    
    pipelineList.each { pipeline ->
        args += " --pipeline ${pipeline.trim()}"
    }
    
    return args
}

def generateInputUrlArgs(inputUrls) {
    if (!inputUrls || inputUrls.trim().isEmpty()) {
        return ""
    }
    
    def urlList = inputUrls.split(/\s+/)
    def args = ""
    
    urlList.each { url ->
        if (url.trim()) {
            args += " --input-url ${url.trim()}"
        }
    }
    
    return args
}

def extractWorkDirectory(projectStatus) {
    def matcher = projectStatus =~ /Work directory:\s*([^\n]+)/
    if (matcher) {
        return matcher[0][1].trim()
    }
    error "Could not extract work directory from project status"
}

def copyInputFiles(inputsPath, workDirectory) {
    echo "Copying input files"
    
    if (fileExists(inputsPath)) {
        sh """
            mkdir -p ${workDirectory}/input/
            cp -r ${inputsPath}/* ${workDirectory}/input/ || true
        """
    } else {
        echo "Input path ${inputsPath} does not exist, skipping file copy"
    }
}

def checkCompliance(projectName, failLevel, failOnVulnerabilities, scanCodeEnv) {
    echo "Checking compliance"
    
    withEnv(scanCodeEnv) {
        def cmd = "scanpipe check-compliance --project ${projectName} --fail-level ${failLevel}"
        
        if (failOnVulnerabilities) {
            cmd += " --fail-on-vulnerabilities"
        }
        
        try {
            sh cmd
            echo "Compliance check passed"
        } catch (Exception e) {
            error "Compliance check failed: ${e.getMessage()}"
        }
    }
}

def generateSecretKey() {
    return sh(
        script: 'openssl rand -base64 32',
        returnStdout: true
    ).trim()
}