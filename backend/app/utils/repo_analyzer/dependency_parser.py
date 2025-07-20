"""
Dependency Parser - Phase 2: Dependency Mapping

Parses dependency files to understand the technology stack, external services,
and infer potential features based on the libraries and frameworks used.
"""

import os
import json
import yaml
import re
from typing import Dict, List, Set, Optional, Any
from pathlib import Path


class DependencyParser:
    """Parses dependency files to extract technology stack and feature insights."""
    
    # Feature inference patterns based on dependencies
    FEATURE_PATTERNS = {
        'authentication': [
            'firebase_auth', 'auth0', 'passport', 'django.contrib.auth',
            'next-auth', 'supabase', 'cognito', 'keycloak'
        ],
        'database': [
            'sqlalchemy', 'django.db', 'prisma', 'typeorm', 'sequelize',
            'firebase_firestore', 'mongodb', 'redis', 'postgresql', 'mysql'
        ],
        'payment_processing': [
            'stripe', 'paypal', 'square', 'braintree', 'razorpay',
            'flutter_stripe', 'stripe-react', 'django-stripe'
        ],
        'real_time_communication': [
            'socket.io', 'websockets', 'signalr', 'pusher', 'ably',
            'firebase_messaging', 'twilio', 'agora'
        ],
        'file_storage': [
            'aws-sdk', 'boto3', 'firebase_storage', 'cloudinary',
            'multer', 'django-storages', 'azure-storage'
        ],
        'email_service': [
            'nodemailer', 'sendgrid', 'mailgun', 'ses', 'smtplib',
            'django.core.mail', 'resend', 'postmark'
        ],
        'ai_ml': [
            'tensorflow', 'pytorch', 'scikit-learn', 'openai', 'anthropic',
            'huggingface', 'langchain', 'transformers', 'numpy', 'pandas'
        ],
        'monitoring_analytics': [
            'sentry', 'datadog', 'newrelic', 'mixpanel', 'amplitude',
            'google-analytics', 'hotjar', 'logrocket'
        ],
        'testing': [
            'jest', 'pytest', 'mocha', 'cypress', 'playwright',
            'selenium', 'flutter_test', 'unittest'
        ],
        'deployment_devops': [
            'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
            'github-actions', 'gitlab-ci', 'vercel', 'netlify'
        ],
        'ui_frameworks': [
            'material-ui', 'ant-design', 'bootstrap', 'tailwind',
            'chakra-ui', 'semantic-ui', 'bulma', 'foundation'
        ],
        'state_management': [
            'redux', 'mobx', 'zustand', 'recoil', 'jotai',
            'vuex', 'pinia', 'ngrx', 'bloc'
        ]
    }
    
    # Technology stack patterns
    STACK_PATTERNS = {
        'frontend': {
            'react': ['react', 'next.js', 'gatsby', 'create-react-app'],
            'vue': ['vue', 'nuxt', 'quasar'],
            'angular': ['angular', '@angular'],
            'flutter': ['flutter', 'dart'],
            'svelte': ['svelte', 'sveltekit'],
            'vanilla': ['vanilla-js', 'jquery']
        },
        'backend': {
            'python': ['fastapi', 'django', 'flask', 'uvicorn', 'gunicorn'],
            'node': ['express', 'koa', 'nest', 'fastify', 'hapi'],
            'java': ['spring', 'quarkus', 'micronaut'],
            'go': ['gin', 'echo', 'fiber', 'gorilla'],
            'rust': ['actix', 'rocket', 'axum'],
            'php': ['laravel', 'symfony', 'codeigniter']
        },
        'database': {
            'sql': ['postgresql', 'mysql', 'sqlite', 'sqlserver'],
            'nosql': ['mongodb', 'redis', 'cassandra', 'dynamodb'],
            'cloud': ['firebase', 'supabase', 'aws', 'azure']
        }
    }
    
    def __init__(self):
        self.dependencies = {}
        self.features = set()
        self.stack = {}
        self.external_services = set()
    
    def parse_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """
        Parse all dependency files in the repository.
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            Dict containing parsed dependencies, features, and stack information
        """
        self.dependencies = {}
        self.features = set()
        self.stack = {}
        self.external_services = set()
        
        # Parse different types of dependency files
        self._parse_package_json(repo_path)
        self._parse_pubspec_yaml(repo_path)
        self._parse_requirements_txt(repo_path)
        self._parse_pyproject_toml(repo_path)
        self._parse_setup_py(repo_path)
        self._parse_gemfile(repo_path)
        self._parse_cargo_toml(repo_path)
        
        # Infer features and stack from dependencies
        self._infer_features()
        self._infer_stack()
        self._infer_external_services()
        
        return {
            'dependencies': self.dependencies,
            'features': list(self.features),
            'stack': self.stack,
            'external_services': list(self.external_services)
        }
    
    def _parse_package_json(self, repo_path: str):
        """Parse Node.js package.json file."""
        package_json_path = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                deps = {}
                if 'dependencies' in data:
                    deps.update(data['dependencies'])
                if 'devDependencies' in data:
                    deps.update(data['devDependencies'])
                if 'peerDependencies' in data:
                    deps.update(data['peerDependencies'])
                
                self.dependencies['node'] = deps
                
                # Extract project metadata
                if 'name' in data:
                    self.dependencies['project_name'] = data['name']
                if 'description' in data:
                    self.dependencies['description'] = data['description']
                if 'scripts' in data:
                    self.dependencies['scripts'] = data['scripts']
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error parsing package.json: {e}")
    
    def _parse_pubspec_yaml(self, repo_path: str):
        """Parse Flutter pubspec.yaml file."""
        pubspec_path = os.path.join(repo_path, 'pubspec.yaml')
        if os.path.exists(pubspec_path):
            try:
                with open(pubspec_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                deps = {}
                if 'dependencies' in data:
                    deps.update(data['dependencies'])
                if 'dev_dependencies' in data:
                    deps.update(data['dev_dependencies'])
                
                self.dependencies['flutter'] = deps
                
                # Extract project metadata
                if 'name' in data:
                    self.dependencies['project_name'] = data['name']
                if 'description' in data:
                    self.dependencies['description'] = data['description']
                    
            except (yaml.YAMLError, IOError) as e:
                print(f"Error parsing pubspec.yaml: {e}")
    
    def _parse_requirements_txt(self, repo_path: str):
        """Parse Python requirements.txt file."""
        requirements_path = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                deps = {}
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package name and version
                        if '==' in line:
                            name, version = line.split('==', 1)
                        elif '>=' in line:
                            name, version = line.split('>=', 1)
                        elif '<=' in line:
                            name, version = line.split('<=', 1)
                        else:
                            name, version = line, '*'
                        
                        deps[name.strip()] = version.strip()
                
                self.dependencies['python'] = deps
                
            except IOError as e:
                print(f"Error parsing requirements.txt: {e}")
    
    def _parse_pyproject_toml(self, repo_path: str):
        """Parse Python pyproject.toml file."""
        pyproject_path = os.path.join(repo_path, 'pyproject.toml')
        if os.path.exists(pyproject_path):
            try:
                with open(pyproject_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                deps = {}
                if 'project' in data and 'dependencies' in data['project']:
                    deps.update(data['project']['dependencies'])
                if 'project' in data and 'optional-dependencies' in data['project']:
                    for group, group_deps in data['project']['optional-dependencies'].items():
                        deps.update(group_deps)
                
                if deps:
                    self.dependencies['python'] = deps
                
                # Extract project metadata
                if 'project' in data:
                    project = data['project']
                    if 'name' in project:
                        self.dependencies['project_name'] = project['name']
                    if 'description' in project:
                        self.dependencies['description'] = project['description']
                        
            except (yaml.YAMLError, IOError) as e:
                print(f"Error parsing pyproject.toml: {e}")
    
    def _parse_setup_py(self, repo_path: str):
        """Parse Python setup.py file."""
        setup_path = os.path.join(repo_path, 'setup.py')
        if os.path.exists(setup_path):
            try:
                with open(setup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple regex to extract install_requires
                install_requires_match = re.search(
                    r'install_requires\s*=\s*\[(.*?)\]',
                    content,
                    re.DOTALL
                )
                
                if install_requires_match:
                    deps_str = install_requires_match.group(1)
                    deps = {}
                    
                    # Parse dependencies from the string
                    dep_matches = re.findall(r'"([^"]+)"', deps_str)
                    for dep in dep_matches:
                        if '==' in dep:
                            name, version = dep.split('==', 1)
                        else:
                            name, version = dep, '*'
                        deps[name.strip()] = version.strip()
                    
                    if deps:
                        self.dependencies['python'] = deps
                        
            except IOError as e:
                print(f"Error parsing setup.py: {e}")
    
    def _parse_gemfile(self, repo_path: str):
        """Parse Ruby Gemfile."""
        gemfile_path = os.path.join(repo_path, 'Gemfile')
        if os.path.exists(gemfile_path):
            try:
                with open(gemfile_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                deps = {}
                for line in lines:
                    line = line.strip()
                    if line.startswith('gem '):
                        # Parse gem name and version
                        match = re.search(r'gem\s+["\']([^"\']+)["\']', line)
                        if match:
                            name = match.group(1)
                            version_match = re.search(r'["\'],\s*["\']([^"\']+)["\']', line)
                            version = version_match.group(1) if version_match else '*'
                            deps[name] = version
                
                if deps:
                    self.dependencies['ruby'] = deps
                    
            except IOError as e:
                print(f"Error parsing Gemfile: {e}")
    
    def _parse_cargo_toml(self, repo_path: str):
        """Parse Rust Cargo.toml file."""
        cargo_path = os.path.join(repo_path, 'Cargo.toml')
        if os.path.exists(cargo_path):
            try:
                with open(cargo_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                deps = {}
                if 'dependencies' in data:
                    deps.update(data['dependencies'])
                if 'dev-dependencies' in data:
                    deps.update(data['dev-dependencies'])
                
                if deps:
                    self.dependencies['rust'] = deps
                
                # Extract project metadata
                if 'package' in data:
                    package = data['package']
                    if 'name' in package:
                        self.dependencies['project_name'] = package['name']
                    if 'description' in package:
                        self.dependencies['description'] = package['description']
                        
            except (yaml.YAMLError, IOError) as e:
                print(f"Error parsing Cargo.toml: {e}")
    
    def _infer_features(self):
        """Infer features based on dependencies."""
        all_deps = []
        for deps in self.dependencies.values():
            if isinstance(deps, dict):
                all_deps.extend(deps.keys())
            elif isinstance(deps, list):
                all_deps.extend(deps)
        
        # Convert to lowercase for matching
        all_deps_lower = [dep.lower() for dep in all_deps]
        
        # Check each feature pattern
        for feature, patterns in self.FEATURE_PATTERNS.items():
            for pattern in patterns:
                if any(pattern.lower() in dep for dep in all_deps_lower):
                    self.features.add(feature)
                    break
    
    def _infer_stack(self):
        """Infer technology stack based on dependencies."""
        all_deps = []
        for deps in self.dependencies.values():
            if isinstance(deps, dict):
                all_deps.extend(deps.keys())
            elif isinstance(deps, list):
                all_deps.extend(deps)
        
        all_deps_lower = [dep.lower() for dep in all_deps]
        
        # Check each stack category
        for category, technologies in self.STACK_PATTERNS.items():
            self.stack[category] = []
            for tech, patterns in technologies.items():
                for pattern in patterns:
                    if any(pattern.lower() in dep for dep in all_deps_lower):
                        self.stack[category].append(tech)
                        break
    
    def _infer_external_services(self):
        """Infer external services being used."""
        service_patterns = {
            'aws': ['aws-sdk', 'boto3', 'amazon', 's3', 'lambda', 'ec2'],
            'google_cloud': ['google-cloud', 'firebase', 'gcp'],
            'azure': ['azure', 'microsoft'],
            'stripe': ['stripe'],
            'twilio': ['twilio'],
            'sendgrid': ['sendgrid'],
            'mailgun': ['mailgun'],
            'pusher': ['pusher'],
            'sentry': ['sentry'],
            'datadog': ['datadog'],
            'newrelic': ['newrelic'],
            'supabase': ['supabase'],
            'vercel': ['vercel'],
            'netlify': ['netlify']
        }
        
        all_deps = []
        for deps in self.dependencies.values():
            if isinstance(deps, dict):
                all_deps.extend(deps.keys())
            elif isinstance(deps, list):
                all_deps.extend(deps)
        
        all_deps_lower = [dep.lower() for dep in all_deps]
        
        for service, patterns in service_patterns.items():
            for pattern in patterns:
                if any(pattern.lower() in dep for dep in all_deps_lower):
                    self.external_services.add(service)
                    break 