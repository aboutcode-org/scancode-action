"""
ScanCode Pipeline Runner - Reusable script for CI/CD implementations
"""
import argparse
import os
import subprocess
import sys
import secrets
import shutil
from pathlib import Path
from typing import List, Optional


class ScanCodePipelineRunner:
    def __init__(self, config: dict):
        self.config = config
        self.project_work_directory = None
        
    def setup_environment(self):
        """Set up environment variables"""
        print("Setting up environment...")
        
        if not os.getenv('SECRET_KEY'):
            secret_key = secrets.token_urlsafe(32)
            os.environ['SECRET_KEY'] = secret_key
            
        os.environ['SCANCODEIO_DB_NAME'] = self.config.get('db_name', 'scancodeio')
        os.environ['SCANCODEIO_DB_USER'] = self.config.get('db_user', 'scancodeio') 
        os.environ['SCANCODEIO_DB_PASSWORD'] = self.config.get('db_password', 'scancodeio')
        
        print("Environment setup completed")
        
    def setup_postgresql(self):
        """Start and configure PostgreSQL service"""
        print("Setting up PostgreSQL...")
        
        db_user = os.environ['SCANCODEIO_DB_USER']
        db_password = os.environ['SCANCODEIO_DB_PASSWORD']
        db_name = os.environ['SCANCODEIO_DB_NAME']
        
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql.service'], check=True)
            
            subprocess.run([
                'sudo', '-u', 'postgres', 'createuser', 
                '--no-createrole', '--no-superuser', '--login', 
                '--inherit', '--createdb', db_user
            ], check=True)
            
            subprocess.run([
                'sudo', '-u', 'postgres', 'psql', '-c',
                f"ALTER USER {db_user} WITH encrypted password '{db_password}'"
            ], check=True)
            
            subprocess.run([
                'sudo', '-u', 'postgres', 'createdb',
                f'--owner={db_user}', '--encoding=UTF-8', db_name
            ], check=True)
            
            print("PostgreSQL setup completed")
            
        except subprocess.CalledProcessError as e:
            print(f"PostgreSQL setup failed: {e}")
            sys.exit(1)
            
    def install_scancodeio(self):
        """Install ScanCode.io"""
        print("Installing ScanCode.io...")
        
        repo_branch = self.config.get('scancodeio_repo_branch')
        
        try:
            if not repo_branch:
                print("Installing the latest ScanCode.io release from PyPI")
                subprocess.run(['pip', 'install', '--upgrade', 'scancodeio'], check=True)
            else:
                print(f"Installing ScanCode.io from GitHub branch: {repo_branch}")
                repo_url = f"git+https://github.com/aboutcode-org/scancode.io.git@{repo_branch}"
                subprocess.run(['pip', 'install', repo_url], check=True)
                
            print("ScanCode.io installation completed")
            
        except subprocess.CalledProcessError as e:
            print(f"ScanCode.io installation failed: {e}")
            sys.exit(1)
            
    def run_migrations(self):
        """Run database migrations"""
        print("Running migrations...")
        
        try:
            subprocess.run(['scanpipe', 'migrate', '--verbosity', '0'], check=True)
            print("Migrations completed")
            
        except subprocess.CalledProcessError as e:
            print(f"Migrations failed: {e}")
            sys.exit(1)
            
    def generate_pipeline_args(self, pipelines: List[str]) -> List[str]:
        """Generate pipeline CLI arguments"""
        args = []
        for pipeline in pipelines:
            args.extend(['--pipeline', pipeline.strip()])
        return args
        
    def generate_input_url_args(self, input_urls: List[str]) -> List[str]:
        """Generate input URL CLI arguments"""
        args = []
        for url in input_urls:
            if url.strip():
                args.extend(['--input-url', url.strip()])
        return args
        
    def create_project(self):
        """Create ScanCode project"""
        print(f"Creating project: {self.config['project_name']}")
        
        pipelines = self.config.get('pipelines', ['scan_codebase'])
        input_urls = self.config.get('input_urls', [])
        
        pipeline_args = self.generate_pipeline_args(pipelines)
        input_url_args = self.generate_input_url_args(input_urls)
        
        cmd = ['scanpipe', 'create-project', self.config['project_name']]
        cmd.extend(pipeline_args)
        cmd.extend(input_url_args)
        
        try:
            subprocess.run(cmd, check=True)
            print("Project created successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"Project creation failed: {e}")
            sys.exit(1)
            
    def get_project_work_directory(self):
        """Get project work directory"""
        print("Getting project work directory...")
        
        try:
            result = subprocess.run([
                'scanpipe', 'status', '--project', self.config['project_name']
            ], capture_output=True, text=True, check=True)
            
            for line in result.stdout.split('\n'):
                if 'Work directory:' in line:
                    self.project_work_directory = line.split('Work directory:')[1].strip()
                    break
                    
            if not self.project_work_directory:
                raise ValueError("Could not find work directory in status output")
                
            print(f"Project work directory: {self.project_work_directory}")
            
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Failed to get project work directory: {e}")
            sys.exit(1)
            
    def copy_input_files(self):
        """Copy input files to project work directory"""
        inputs_path = self.config.get('inputs_path')
        
        if not inputs_path or not os.path.exists(inputs_path):
            print("No input files to copy")
            return
            
        destination_path = os.path.join(self.project_work_directory, 'input')
        
        print(f"Copying input files from {inputs_path} to {destination_path}")
        
        try:
            if os.path.isdir(inputs_path):
                for item in os.listdir(inputs_path):
                    source_item = os.path.join(inputs_path, item)
                    dest_item = os.path.join(destination_path, item)
                    
                    if os.path.isdir(source_item):
                        shutil.copytree(source_item, dest_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_item, dest_item)
                        
            print("Input files copied successfully")
            
        except Exception as e:
            print(f"Failed to copy input files: {e}")
            sys.exit(1)
            
    def run_pipelines(self):
        """Execute the pipelines"""
        print("Running pipelines...")
        
        try:
            subprocess.run([
                'scanpipe', 'execute', 
                '--project', self.config['project_name'],
                '--no-color'
            ], check=True)
            
            print("Pipelines executed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"Pipeline execution failed: {e}")
            sys.exit(1)
            
    def generate_outputs(self):
        """Generate output files"""
        print("Generating outputs...")
        
        output_formats = self.config.get('output_formats', ['json', 'xlsx', 'spdx', 'cyclonedx'])
        
        for fmt in output_formats:
            fmt = fmt.strip()
            print(f"\n=== Generating {fmt.upper()} format ===")
            
            cmd = [
                'scanpipe', 'output',
                '--project', self.config['project_name'],
                '--format', fmt
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"✓ {fmt.upper()} format generated successfully")
                if result.stdout:
                    print(f"  Output: {result.stdout.strip()}")
                    
            except subprocess.CalledProcessError as e:
                print(f"✗ {fmt.upper()} format generation failed")
                print(f"  Exit code: {e.returncode}")
                if e.stdout:
                    print(f"  Stdout: {e.stdout.strip()}")
                if e.stderr:
                    print(f"  Stderr: {e.stderr.strip()}")
                continue
        
        output_path = self.get_output_path()
        if os.path.exists(output_path):
            files = os.listdir(output_path)
            print(f"\n=== Generated files in {output_path} ===")
            for file in files:
                file_path = os.path.join(output_path, file)
                size = os.path.getsize(file_path)
                print(f"  {file} ({size} bytes)")
        else:
            print(f"\n⚠ Output directory not found: {output_path}")
        
        print("Output generation completed")


    def check_compliance(self):
        """Check compliance if enabled"""
        if not self.config.get('check_compliance', False):
            return
            
        print("Checking compliance...")
        
        cmd = [
            'scanpipe', 'check-compliance',
            '--project', self.config['project_name'],
            '--fail-level', self.config.get('compliance_fail_level', 'ERROR')
        ]
        
        if self.config.get('compliance_fail_on_vulnerabilities', False):
            cmd.append('--fail-on-vulnerabilities')
            
        try:
            subprocess.run(cmd, check=True)
            print("Compliance check passed")
            
        except subprocess.CalledProcessError as e:
            print(f"Compliance check failed: {e}")
            sys.exit(1)
            
    def get_output_path(self) -> str:
        """Get the output directory path"""
        return os.path.join(self.project_work_directory, 'output')
        
    def run_full_pipeline(self):
        """Run the complete pipeline"""
        print("Starting ScanCode pipeline...")
        
        self.setup_environment()
        self.setup_postgresql()
        self.install_scancodeio()
        self.run_migrations()
        self.create_project()
        self.get_project_work_directory()
        self.copy_input_files()
        self.run_pipelines()
        self.generate_outputs()
        self.check_compliance()
        
        print("Pipeline completed successfully!")
        print(f"Output files available at: {self.get_output_path()}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='ScanCode Pipeline Runner')
    
    parser.add_argument('--project-name', default='scancode-project',
                       help='Name of the project')
    parser.add_argument('--pipelines', default='scan_codebase',
                       help='Comma-separated list of pipelines')
    parser.add_argument('--output-formats', default='json xlsx spdx cyclonedx',
                       help='Comma-separated list of output formats')
    parser.add_argument('--inputs-path',
                       help='Path to input files directory')
    parser.add_argument('--input-urls',
                       help='Comma-separated list of input URLs')
    parser.add_argument('--check-compliance', action='store_true',
                       help='Enable compliance checking')
    parser.add_argument('--compliance-fail-level', default='ERROR',
                       choices=['ERROR', 'WARNING', 'MISSING'],
                       help='Compliance failure level')
    parser.add_argument('--compliance-fail-on-vulnerabilities', action='store_true',
                       help='Fail on vulnerabilities')
    parser.add_argument('--scancodeio-repo-branch',
                       help='ScanCode.io repository branch to install from')
    parser.add_argument('--db-name', default='scancodeio',
                       help='Database name')
    parser.add_argument('--db-user', default='scancodeio',
                       help='Database user')
    parser.add_argument('--db-password', default='scancodeio',
                       help='Database password')
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    config = {
        'project_name': args.project_name,
        'pipelines': [p.strip() for p in args.pipelines.split(',')],
        'output_formats': [f.strip() for f in args.output_formats.replace(',', ' ').split()],
        'inputs_path': args.inputs_path,
        'input_urls': [u.strip() for u in (args.input_urls or '').split(',') if u.strip()],
        'check_compliance': args.check_compliance,
        'compliance_fail_level': args.compliance_fail_level,
        'compliance_fail_on_vulnerabilities': args.compliance_fail_on_vulnerabilities,
        'scancodeio_repo_branch': args.scancodeio_repo_branch,
        'db_name': args.db_name,
        'db_user': args.db_user,
        'db_password': args.db_password,
    }
    
    runner = ScanCodePipelineRunner(config)
    runner.run_full_pipeline()


if __name__ == '__main__':
    main()
