"""
Repo Type Detector - Phase 1: Classification

Detects the type of repository based on key files and structure patterns.
Returns standardized repo types that inform the rest of the analysis pipeline.
"""

import os
import re
from typing import Dict, List, Set, Optional
from pathlib import Path


class RepoTypeDetector:
    """Detects repository type using file presence and structure heuristics."""
    
    # File patterns that indicate specific repo types
    TYPE_INDICATORS = {
        'flutter_mobile': {
            'files': ['pubspec.yaml', 'lib/main.dart', 'android/', 'ios/'],
            'keywords': ['flutter', 'dart', 'pubspec']
        },
        'react_web': {
            'files': ['package.json', 'src/', 'public/', 'index.html'],
            'keywords': ['react', 'next.js', 'create-react-app']
        },
        'vue_web': {
            'files': ['package.json', 'src/', 'public/', 'vue.config.js'],
            'keywords': ['vue', 'nuxt', 'vite']
        },
        'angular_web': {
            'files': ['package.json', 'src/', 'angular.json', 'tsconfig.json'],
            'keywords': ['angular', '@angular']
        },
        'fastapi_backend': {
            'files': ['requirements.txt', 'main.py', 'app/', 'api/'],
            'keywords': ['fastapi', 'uvicorn', 'pydantic']
        },
        'django_backend': {
            'files': ['requirements.txt', 'manage.py', 'settings.py', 'urls.py'],
            'keywords': ['django', 'djangorestframework']
        },
        'express_backend': {
            'files': ['package.json', 'server.js', 'app.js', 'routes/'],
            'keywords': ['express', 'node.js', 'npm']
        },
        'chrome_extension': {
            'files': ['manifest.json', 'background.js', 'content.js'],
            'keywords': ['chrome.extension', 'manifest_version']
        },
        'python_library': {
            'files': ['setup.py', 'pyproject.toml', '__init__.py'],
            'keywords': ['setuptools', 'poetry']
        },
        'node_library': {
            'files': ['package.json', 'index.js', 'lib/', 'src/'],
            'keywords': ['npm', 'yarn', 'node_modules']
        },
        'mono_repo': {
            'files': ['lerna.json', 'nx.json', 'workspace.json', 'packages/'],
            'keywords': ['lerna', 'nx', 'workspace', 'monorepo']
        },
        'docker_project': {
            'files': ['Dockerfile', 'docker-compose.yml', '.dockerignore'],
            'keywords': ['docker', 'container']
        },
        'terraform_infra': {
            'files': ['main.tf', 'variables.tf', 'outputs.tf', '.tfstate'],
            'keywords': ['terraform', 'aws', 'azure', 'gcp']
        }
    }
    
    def __init__(self):
        self.detected_type = None
        self.confidence_score = 0.0
        self.evidence = []
    
    def detect_repo_type(self, repo_path: str) -> Dict[str, any]:
        """
        Detect the type of repository at the given path.
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            Dict containing:
            - type: The detected repo type
            - confidence: Confidence score (0.0-1.0)
            - evidence: List of evidence supporting the detection
        """
        if not os.path.exists(repo_path):
            return {
                'type': 'unknown',
                'confidence': 0.0,
                'evidence': ['Repository path does not exist']
            }
        
        # Get all files and directories
        all_files = self._get_all_files(repo_path)
        all_dirs = self._get_all_directories(repo_path)
        
        # Score each repo type
        type_scores = {}
        
        for repo_type, indicators in self.TYPE_INDICATORS.items():
            score = 0.0
            evidence = []
            
            # Check for required files
            for file_pattern in indicators['files']:
                if self._file_exists(file_pattern, all_files, all_dirs):
                    score += 0.3
                    evidence.append(f"Found: {file_pattern}")
            
            # Check for keywords in key files
            keyword_score = self._check_keywords(indicators['keywords'], all_files, repo_path)
            score += keyword_score * 0.4
            if keyword_score > 0:
                evidence.append(f"Keywords found: {indicators['keywords']}")
            
            # Check for structural patterns
            structure_score = self._check_structure_patterns(repo_type, all_files, all_dirs)
            score += structure_score * 0.3
            if structure_score > 0:
                evidence.append("Structure patterns match")
            
            type_scores[repo_type] = {
                'score': min(score, 1.0),
                'evidence': evidence
            }
        
        # Find the best match
        best_type = max(type_scores.items(), key=lambda x: x[1]['score'])
        
        # Special handling for mono repos
        if best_type[0] == 'mono_repo' and best_type[1]['score'] > 0.5:
            # Check if it contains multiple project types
            sub_types = self._detect_mono_repo_subtypes(repo_path)
            if sub_types:
                best_type[1]['evidence'].append(f"Contains sub-projects: {', '.join(sub_types)}")
        
        return {
            'type': best_type[0] if best_type[1]['score'] > 0.3 else 'unknown',
            'confidence': best_type[1]['score'],
            'evidence': best_type[1]['evidence']
        }
    
    def _get_all_files(self, repo_path: str) -> Set[str]:
        """Get all files in the repository."""
        files = set()
        for root, dirs, filenames in os.walk(repo_path):
            # Skip common directories that don't indicate repo type
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
            for filename in filenames:
                files.add(filename)
        return files
    
    def _get_all_directories(self, repo_path: str) -> Set[str]:
        """Get all directories in the repository."""
        dirs = set()
        for root, dirnames, files in os.walk(repo_path):
            # Skip common directories that don't indicate repo type
            dirnames[:] = [d for d in dirnames if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
            for dirname in dirnames:
                dirs.add(dirname)
        return dirs
    
    def _file_exists(self, pattern: str, files: Set[str], dirs: Set[str]) -> bool:
        """Check if a file or directory pattern exists."""
        if pattern.endswith('/'):
            return pattern.rstrip('/') in dirs
        else:
            return pattern in files
    
    def _check_keywords(self, keywords: List[str], files: Set[str], repo_path: str) -> float:
        """Check for keywords in key configuration files."""
        score = 0.0
        key_files = ['package.json', 'pubspec.yaml', 'requirements.txt', 'setup.py', 'pyproject.toml']
        
        for key_file in key_files:
            if key_file in files:
                file_path = os.path.join(repo_path, key_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for keyword in keywords:
                            if keyword.lower() in content:
                                score += 0.2
                except (IOError, UnicodeDecodeError):
                    continue
        
        return min(score, 1.0)
    
    def _check_structure_patterns(self, repo_type: str, files: Set[str], dirs: Set[str]) -> float:
        """Check for structural patterns specific to repo types."""
        patterns = {
            'flutter_mobile': {
                'required': ['lib/'],
                'optional': ['android/', 'ios/', 'test/']
            },
            'react_web': {
                'required': ['src/', 'public/'],
                'optional': ['components/', 'pages/', 'hooks/']
            },
            'fastapi_backend': {
                'required': ['app/'],
                'optional': ['api/', 'models/', 'services/']
            },
            'mono_repo': {
                'required': ['packages/', 'apps/'],
                'optional': ['libs/', 'tools/']
            }
        }
        
        if repo_type not in patterns:
            return 0.0
        
        pattern = patterns[repo_type]
        score = 0.0
        
        # Check required patterns
        for required in pattern['required']:
            if self._file_exists(required, files, dirs):
                score += 0.5
        
        # Check optional patterns
        for optional in pattern['optional']:
            if self._file_exists(optional, files, dirs):
                score += 0.2
        
        return min(score, 1.0)
    
    def _detect_mono_repo_subtypes(self, repo_path: str) -> List[str]:
        """Detect sub-project types within a mono repo."""
        sub_types = []
        
        # Check for packages directory
        packages_dir = os.path.join(repo_path, 'packages')
        if os.path.exists(packages_dir):
            for package in os.listdir(packages_dir):
                package_path = os.path.join(packages_dir, package)
                if os.path.isdir(package_path):
                    sub_detector = RepoTypeDetector()
                    result = sub_detector.detect_repo_type(package_path)
                    if result['type'] != 'unknown':
                        sub_types.append(result['type'])
        
        return sub_types 