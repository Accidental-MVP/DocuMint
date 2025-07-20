"""
Structure Mapper - Phase 3: Structure Mapping

Builds internal maps of folder → feature relationships by traversing the
project structure and categorizing files and directories by their purpose.
"""

import os
import re
from typing import Dict, List, Set, Optional, Any
from pathlib import Path
from collections import defaultdict


class StructureMapper:
    """Maps project structure to understand folder → feature relationships."""
    
    # Directory patterns that indicate specific purposes
    DIRECTORY_PATTERNS = {
        'frontend_ui': [
            'src/components/', 'src/pages/', 'src/views/', 'src/screens/',
            'lib/widgets/', 'lib/screens/', 'lib/pages/', 'components/',
            'pages/', 'views/', 'screens/', 'ui/', 'widgets/'
        ],
        'backend_api': [
            'api/', 'routes/', 'controllers/', 'handlers/', 'endpoints/',
            'app/api/', 'app/routes/', 'app/controllers/', 'src/api/',
            'src/routes/', 'src/controllers/'
        ],
        'data_models': [
            'models/', 'entities/', 'schemas/', 'types/', 'interfaces/',
            'app/models/', 'src/models/', 'lib/models/', 'data/',
            'domain/', 'entities/'
        ],
        'services': [
            'services/', 'utils/', 'helpers/', 'lib/', 'src/services/',
            'app/services/', 'core/', 'business/', 'logic/'
        ],
        'configuration': [
            'config/', 'settings/', 'env/', 'environment/', 'app/config/',
            'src/config/', 'lib/config/'
        ],
        'assets': [
            'assets/', 'static/', 'public/', 'resources/', 'images/',
            'styles/', 'css/', 'scss/', 'sass/', 'fonts/', 'icons/'
        ],
        'tests': [
            'tests/', 'test/', '__tests__/', 'spec/', 'e2e/', 'cypress/',
            'test_', 'tests_', 'specs/'
        ],
        'documentation': [
            'docs/', 'documentation/', 'readme/', 'guides/', 'wiki/',
            'examples/', 'samples/'
        ],
        'deployment': [
            'deploy/', 'deployment/', 'docker/', 'k8s/', 'kubernetes/',
            'terraform/', 'scripts/', 'build/', 'dist/'
        ]
    }
    
    # File patterns that indicate specific purposes
    FILE_PATTERNS = {
        'entry_points': [
            'main.py', 'app.py', 'server.py', 'index.js', 'main.dart',
            'App.js', 'App.tsx', 'main.ts', 'main.tsx', 'index.ts',
            'index.tsx', 'app.ts', 'app.tsx'
        ],
        'configuration': [
            'config.py', 'settings.py', 'config.js', 'config.ts',
            'environment.py', 'env.py', '.env', '.env.local',
            'package.json', 'pubspec.yaml', 'requirements.txt'
        ],
        'routing': [
            'urls.py', 'routes.py', 'router.py', 'app.py',
            'index.js', 'App.js', 'main.dart'
        ],
        'database': [
            'models.py', 'schema.py', 'migrations/', 'database.py',
            'db.py', 'connection.py'
        ],
        'authentication': [
            'auth.py', 'authentication.py', 'login.py', 'register.py',
            'middleware.py', 'jwt.py', 'oauth.py'
        ],
        'api_endpoints': [
            'api.py', 'endpoints.py', 'views.py', 'controllers.py',
            'handlers.py', 'routes.py'
        ]
    }
    
    # Feature keywords in file/directory names
    FEATURE_KEYWORDS = {
        'authentication': ['auth', 'login', 'register', 'signin', 'signup', 'user'],
        'payment': ['payment', 'stripe', 'paypal', 'checkout', 'billing', 'invoice'],
        'chat': ['chat', 'message', 'conversation', 'room', 'channel'],
        'notification': ['notification', 'alert', 'push', 'email', 'sms'],
        'file_upload': ['upload', 'file', 'image', 'media', 'attachment'],
        'search': ['search', 'query', 'filter', 'find'],
        'dashboard': ['dashboard', 'admin', 'panel', 'control'],
        'analytics': ['analytics', 'stats', 'metrics', 'report', 'chart'],
        'social': ['social', 'friend', 'follow', 'like', 'share'],
        'ecommerce': ['product', 'cart', 'order', 'shop', 'store', 'marketplace'],
        'booking': ['booking', 'reservation', 'appointment', 'schedule'],
        'gaming': ['game', 'player', 'score', 'leaderboard', 'level']
    }
    
    def __init__(self):
        self.structure_map = {}
        self.feature_map = defaultdict(list)
        self.file_categories = defaultdict(list)
        self.directory_categories = defaultdict(list)
    
    def map_project_structure(self, repo_path: str) -> Dict[str, Any]:
        """
        Map the project structure to understand folder → feature relationships.
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            Dict containing structure mapping, feature relationships, and categories
        """
        self.structure_map = {}
        self.feature_map = defaultdict(list)
        self.file_categories = defaultdict(list)
        self.directory_categories = defaultdict(list)
        
        # Walk through the repository
        for root, dirs, files in os.walk(repo_path):
            # Skip common directories that don't indicate structure
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                '.pytest_cache', '.coverage', 'dist', 'build', '.next'
            }]
            
            # Get relative path from repo root
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == '.':
                rel_path = ''
            
            # Categorize directories
            self._categorize_directory(rel_path, dirs)
            
            # Categorize files
            for file in files:
                file_path = os.path.join(rel_path, file) if rel_path else file
                self._categorize_file(file_path, file)
        
        # Build feature relationships
        self._build_feature_relationships()
        
        # Analyze structure patterns
        structure_analysis = self._analyze_structure_patterns()
        
        return {
            'structure_map': dict(self.structure_map),
            'feature_map': dict(self.feature_map),
            'file_categories': dict(self.file_categories),
            'directory_categories': dict(self.directory_categories),
            'structure_analysis': structure_analysis
        }
    
    def _categorize_directory(self, rel_path: str, dirs: List[str]):
        """Categorize directories based on patterns."""
        path_parts = rel_path.split(os.sep) if rel_path else []
        
        for category, patterns in self.DIRECTORY_PATTERNS.items():
            for pattern in patterns:
                pattern_parts = pattern.rstrip('/').split('/')
                
                # Check if pattern matches the current path
                if self._pattern_matches_path(pattern_parts, path_parts):
                    self.directory_categories[category].append(rel_path)
                    break
        
        # Check for feature keywords in directory names
        for feature, keywords in self.FEATURE_KEYWORDS.items():
            for keyword in keywords:
                if any(keyword.lower() in dir.lower() for dir in dirs):
                    self.feature_map[feature].append({
                        'type': 'directory',
                        'path': rel_path,
                        'matches': [dir for dir in dirs if keyword.lower() in dir.lower()]
                    })
    
    def _categorize_file(self, file_path: str, filename: str):
        """Categorize files based on patterns and content."""
        # Categorize by file pattern
        for category, patterns in self.FILE_PATTERNS.items():
            for pattern in patterns:
                if pattern.endswith('/'):
                    # Directory pattern
                    if file_path.startswith(pattern.rstrip('/')):
                        self.file_categories[category].append(file_path)
                        break
                else:
                    # File pattern
                    if filename == pattern or filename.endswith(pattern):
                        self.file_categories[category].append(file_path)
                        break
        
        # Check for feature keywords in filename
        for feature, keywords in self.FEATURE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in filename.lower():
                    self.feature_map[feature].append({
                        'type': 'file',
                        'path': file_path,
                        'keyword': keyword
                    })
                    break
    
    def _pattern_matches_path(self, pattern_parts: List[str], path_parts: List[str]) -> bool:
        """Check if a pattern matches a path."""
        if len(pattern_parts) > len(path_parts):
            return False
        
        for i, pattern_part in enumerate(pattern_parts):
            if i >= len(path_parts):
                return False
            
            # Handle wildcards or exact matches
            if pattern_part == '*' or pattern_part == path_parts[i]:
                continue
            elif pattern_part in path_parts[i]:
                continue
            else:
                return False
        
        return True
    
    def _build_feature_relationships(self):
        """Build relationships between features based on file/directory proximity."""
        # Group features by directory structure
        feature_groups = defaultdict(list)
        
        for feature, items in self.feature_map.items():
            for item in items:
                if item['type'] == 'file':
                    dir_path = os.path.dirname(item['path'])
                    feature_groups[dir_path].append(feature)
                else:
                    feature_groups[item['path']].append(feature)
        
        # Find related features
        related_features = defaultdict(set)
        for dir_path, features in feature_groups.items():
            if len(features) > 1:
                for feature in features:
                    related_features[feature].update(features)
        
        # Add relationship information to structure map
        for feature, related in related_features.items():
            if feature in self.feature_map:
                self.feature_map[feature].append({
                    'type': 'relationship',
                    'related_features': list(related - {feature})
                })
    
    def _analyze_structure_patterns(self) -> Dict[str, Any]:
        """Analyze the overall structure patterns."""
        analysis = {
            'architecture_pattern': self._detect_architecture_pattern(),
            'layer_separation': self._analyze_layer_separation(),
            'feature_clustering': self._analyze_feature_clustering(),
            'complexity_indicators': self._analyze_complexity()
        }
        
        return analysis
    
    def _detect_architecture_pattern(self) -> str:
        """Detect the overall architecture pattern."""
        patterns = {
            'mvc': self._has_mvc_pattern(),
            'layered': self._has_layered_pattern(),
            'microservices': self._has_microservices_pattern(),
            'monolithic': self._has_monolithic_pattern(),
            'feature_based': self._has_feature_based_pattern()
        }
        
        # Return the pattern with highest confidence
        return max(patterns.items(), key=lambda x: x[1])[0]
    
    def _has_mvc_pattern(self) -> float:
        """Check for MVC pattern indicators."""
        score = 0.0
        
        # Check for model, view, controller directories
        model_dirs = [d for d in self.directory_categories.get('data_models', []) 
                     if any(keyword in d.lower() for keyword in ['model', 'entity'])]
        view_dirs = [d for d in self.directory_categories.get('frontend_ui', []) 
                    if any(keyword in d.lower() for keyword in ['view', 'page', 'screen'])]
        controller_dirs = [d for d in self.directory_categories.get('backend_api', []) 
                          if any(keyword in d.lower() for keyword in ['controller', 'handler'])]
        
        if model_dirs:
            score += 0.3
        if view_dirs:
            score += 0.3
        if controller_dirs:
            score += 0.4
        
        return score
    
    def _has_layered_pattern(self) -> float:
        """Check for layered architecture pattern."""
        score = 0.0
        
        layers = ['presentation', 'business', 'data', 'infrastructure']
        for layer in layers:
            if any(layer in d.lower() for d in self.directory_categories.get('services', [])):
                score += 0.25
        
        return score
    
    def _has_microservices_pattern(self) -> float:
        """Check for microservices pattern."""
        score = 0.0
        
        # Look for multiple service directories or packages
        service_dirs = self.directory_categories.get('services', [])
        if len(service_dirs) > 3:
            score += 0.4
        
        # Check for service-specific configuration
        if any('service' in d.lower() for d in self.directory_categories.get('configuration', [])):
            score += 0.3
        
        # Check for deployment configurations
        if self.directory_categories.get('deployment', []):
            score += 0.3
        
        return score
    
    def _has_monolithic_pattern(self) -> float:
        """Check for monolithic pattern."""
        score = 0.0
        
        # Look for single application structure
        if len(self.directory_categories.get('backend_api', [])) <= 2:
            score += 0.4
        
        if len(self.directory_categories.get('services', [])) <= 2:
            score += 0.3
        
        # Check for single configuration
        if len(self.directory_categories.get('configuration', [])) <= 1:
            score += 0.3
        
        return score
    
    def _has_feature_based_pattern(self) -> float:
        """Check for feature-based architecture pattern."""
        score = 0.0
        
        # Look for feature-specific directories
        feature_dirs = []
        for feature in self.FEATURE_KEYWORDS.keys():
            if any(feature in d.lower() for d in self.directory_categories.get('frontend_ui', [])):
                feature_dirs.append(feature)
        
        if len(feature_dirs) >= 3:
            score += 0.5
        
        # Check for feature-specific services
        if len(feature_dirs) >= 2:
            score += 0.5
        
        return score
    
    def _analyze_layer_separation(self) -> Dict[str, float]:
        """Analyze how well layers are separated."""
        separation_scores = {}
        
        # Check separation between UI and business logic
        ui_dirs = len(self.directory_categories.get('frontend_ui', []))
        service_dirs = len(self.directory_categories.get('services', []))
        
        if ui_dirs > 0 and service_dirs > 0:
            separation_scores['ui_business_separation'] = 0.8
        else:
            separation_scores['ui_business_separation'] = 0.2
        
        # Check separation between API and data layers
        api_dirs = len(self.directory_categories.get('backend_api', []))
        model_dirs = len(self.directory_categories.get('data_models', []))
        
        if api_dirs > 0 and model_dirs > 0:
            separation_scores['api_data_separation'] = 0.8
        else:
            separation_scores['api_data_separation'] = 0.2
        
        return separation_scores
    
    def _analyze_feature_clustering(self) -> Dict[str, Any]:
        """Analyze how features are clustered in the codebase."""
        clustering = {
            'feature_count': len(self.feature_map),
            'feature_distribution': {},
            'co_located_features': []
        }
        
        # Analyze feature distribution
        for feature, items in self.feature_map.items():
            clustering['feature_distribution'][feature] = len(items)
        
        # Find co-located features
        feature_locations = defaultdict(list)
        for feature, items in self.feature_map.items():
            for item in items:
                if item['type'] in ['file', 'directory']:
                    feature_locations[item['path']].append(feature)
        
        for location, features in feature_locations.items():
            if len(features) > 1:
                clustering['co_located_features'].append({
                    'location': location,
                    'features': features
                })
        
        return clustering
    
    def _analyze_complexity(self) -> Dict[str, Any]:
        """Analyze codebase complexity indicators."""
        complexity = {
            'file_count': sum(len(files) for files in self.file_categories.values()),
            'directory_count': sum(len(dirs) for dirs in self.directory_categories.values()),
            'feature_count': len(self.feature_map),
            'layer_count': len(self.directory_categories),
            'complexity_score': 0.0
        }
        
        # Calculate complexity score
        complexity['complexity_score'] = (
            complexity['file_count'] * 0.1 +
            complexity['directory_count'] * 0.2 +
            complexity['feature_count'] * 0.3 +
            complexity['layer_count'] * 0.4
        ) / 10.0
        
        return complexity 