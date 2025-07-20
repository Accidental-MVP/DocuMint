"""
Signal Ranker - Phase 4: Signal Extraction

Identifies high-signal files (routes, models, services) by scoring them based on
importance, relevance, and their role in the application architecture.
"""

import os
import re
from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict


class SignalRanker:
    """Ranks files by their signal strength and importance to the codebase."""
    
    # File importance weights based on type and location
    FILE_WEIGHTS = {
        'entry_point': 10.0,
        'configuration': 8.0,
        'routing': 9.0,
        'authentication': 8.5,
        'api_endpoint': 9.0,
        'database_model': 8.0,
        'service': 7.5,
        'component': 6.0,
        'utility': 4.0,
        'test': 3.0,
        'documentation': 2.0,
        'asset': 1.0
    }
    
    # Directory importance multipliers
    DIRECTORY_MULTIPLIERS = {
        'src/': 1.5,
        'app/': 1.5,
        'lib/': 1.3,
        'api/': 1.4,
        'routes/': 1.4,
        'controllers/': 1.4,
        'models/': 1.3,
        'services/': 1.3,
        'components/': 1.2,
        'utils/': 1.1,
        'config/': 1.2,
        'tests/': 0.7,
        'docs/': 0.5,
        'assets/': 0.3
    }
    
    # High-signal keywords that boost file importance
    HIGH_SIGNAL_KEYWORDS = {
        'auth': 2.0,
        'login': 2.0,
        'register': 2.0,
        'user': 1.5,
        'payment': 2.0,
        'stripe': 2.0,
        'checkout': 2.0,
        'order': 1.8,
        'product': 1.8,
        'chat': 1.8,
        'message': 1.5,
        'notification': 1.5,
        'email': 1.5,
        'upload': 1.5,
        'file': 1.3,
        'search': 1.5,
        'dashboard': 1.8,
        'admin': 1.8,
        'analytics': 1.5,
        'api': 1.5,
        'route': 1.5,
        'controller': 1.5,
        'service': 1.3,
        'model': 1.3,
        'database': 1.3,
        'config': 1.2,
        'main': 1.5,
        'app': 1.3,
        'index': 1.2
    }
    
    # File extensions and their base importance
    EXTENSION_WEIGHTS = {
        '.py': 1.0,
        '.js': 1.0,
        '.ts': 1.1,
        '.jsx': 1.1,
        '.tsx': 1.2,
        '.dart': 1.0,
        '.java': 1.0,
        '.go': 1.0,
        '.rs': 1.0,
        '.php': 1.0,
        '.rb': 1.0,
        '.json': 0.8,
        '.yaml': 0.8,
        '.yml': 0.8,
        '.toml': 0.8,
        '.md': 0.5,
        '.txt': 0.3,
        '.css': 0.6,
        '.scss': 0.6,
        '.sass': 0.6,
        '.html': 0.7,
        '.xml': 0.6,
        '.sql': 0.8,
        '.sh': 0.5,
        '.bat': 0.5,
        '.dockerfile': 0.8,
        '.gitignore': 0.2,
        '.env': 0.9
    }
    
    def __init__(self):
        self.ranked_files = []
        self.signal_scores = {}
        self.high_signal_files = []
        self.file_categories = defaultdict(list)
    
    def score_files_by_signal(self, repo_path: str, file_categories: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """
        Score files by their signal strength and importance.
        
        Args:
            repo_path: Path to the repository root
            file_categories: Pre-categorized files from structure mapper
            
        Returns:
            Dict containing ranked files, signal scores, and high-signal files
        """
        self.ranked_files = []
        self.signal_scores = {}
        self.high_signal_files = []
        self.file_categories = defaultdict(list)
        
        if file_categories:
            self.file_categories.update(file_categories)
        
        # Get all files in the repository
        all_files = self._get_all_files(repo_path)
        
        # Score each file
        for file_path in all_files:
            score = self._calculate_file_score(file_path, repo_path)
            self.signal_scores[file_path] = score
            
            # Categorize file by score
            if score >= 8.0:
                self.high_signal_files.append({
                    'path': file_path,
                    'score': score,
                    'category': self._categorize_file_by_score(score)
                })
        
        # Sort files by score
        self.ranked_files = sorted(
            self.signal_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Analyze signal distribution
        signal_analysis = self._analyze_signal_distribution()
        
        return {
            'ranked_files': self.ranked_files[:50],  # Top 50 files
            'high_signal_files': self.high_signal_files,
            'signal_scores': self.signal_scores,
            'signal_analysis': signal_analysis
        }
    
    def _get_all_files(self, repo_path: str) -> List[str]:
        """Get all files in the repository with relative paths."""
        files = []
        for root, dirs, filenames in os.walk(repo_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                '.pytest_cache', '.coverage', 'dist', 'build', '.next',
                'target', 'bin', 'obj', '.vs', '.idea'
            }]
            
            for filename in filenames:
                # Skip common files that don't provide signal
                if filename in {
                    '.DS_Store', 'Thumbs.db', '.gitignore', '.gitattributes',
                    'README.md', 'LICENSE', 'CHANGELOG.md'
                }:
                    continue
                
                rel_path = os.path.relpath(os.path.join(root, filename), repo_path)
                files.append(rel_path)
        
        return files
    
    def _calculate_file_score(self, file_path: str, repo_path: str) -> float:
        """Calculate the signal score for a file."""
        score = 0.0
        
        # Base score from file type
        file_type = self._determine_file_type(file_path)
        score += self.FILE_WEIGHTS.get(file_type, 5.0)
        
        # Directory multiplier
        dir_multiplier = self._get_directory_multiplier(file_path)
        score *= dir_multiplier
        
        # Extension weight
        ext_weight = self._get_extension_weight(file_path)
        score *= ext_weight
        
        # Keyword boost
        keyword_boost = self._calculate_keyword_boost(file_path)
        score *= keyword_boost
        
        # Content-based scoring
        content_score = self._analyze_file_content(file_path, repo_path)
        score += content_score
        
        # Size-based adjustment
        size_adjustment = self._calculate_size_adjustment(file_path, repo_path)
        score *= size_adjustment
        
        # Relationship boost (if file is referenced by others)
        relationship_boost = self._calculate_relationship_boost(file_path)
        score *= relationship_boost
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine the type of file based on path and name."""
        filename = os.path.basename(file_path).lower()
        path_parts = file_path.lower().split(os.sep)
        
        # Check for entry points
        if filename in ['main.py', 'app.py', 'server.py', 'index.js', 'main.dart', 'app.js', 'app.tsx']:
            return 'entry_point'
        
        # Check for configuration files
        if filename in ['config.py', 'settings.py', 'config.js', 'config.ts', '.env'] or 'config' in path_parts:
            return 'configuration'
        
        # Check for routing files
        if any(keyword in filename for keyword in ['route', 'url', 'router']):
            return 'routing'
        
        # Check for authentication files
        if any(keyword in filename for keyword in ['auth', 'login', 'register', 'jwt']):
            return 'authentication'
        
        # Check for API endpoints
        if any(keyword in filename for keyword in ['api', 'endpoint', 'controller', 'handler']):
            return 'api_endpoint'
        
        # Check for database models
        if any(keyword in filename for keyword in ['model', 'schema', 'entity']):
            return 'database_model'
        
        # Check for services
        if any(keyword in filename for keyword in ['service', 'business', 'logic']):
            return 'service'
        
        # Check for components
        if any(keyword in filename for keyword in ['component', 'widget', 'view']):
            return 'component'
        
        # Check for utilities
        if any(keyword in filename for keyword in ['util', 'helper', 'tool']):
            return 'utility'
        
        # Check for tests
        if any(keyword in filename for keyword in ['test', 'spec', 'mock']):
            return 'test'
        
        # Check for documentation
        if any(keyword in filename for keyword in ['readme', 'doc', 'guide']):
            return 'documentation'
        
        # Check for assets
        if any(keyword in filename for keyword in ['image', 'icon', 'font', 'style']):
            return 'asset'
        
        return 'utility'  # Default
    
    def _get_directory_multiplier(self, file_path: str) -> float:
        """Get the directory importance multiplier for a file."""
        path_parts = file_path.split(os.sep)
        
        for part in path_parts[:-1]:  # Exclude filename
            for pattern, multiplier in self.DIRECTORY_MULTIPLIERS.items():
                if pattern.rstrip('/') in part:
                    return multiplier
        
        return 1.0  # Default multiplier
    
    def _get_extension_weight(self, file_path: str) -> float:
        """Get the extension weight for a file."""
        _, ext = os.path.splitext(file_path)
        return self.EXTENSION_WEIGHTS.get(ext.lower(), 0.5)
    
    def _calculate_keyword_boost(self, file_path: str) -> float:
        """Calculate keyword boost based on filename."""
        filename = os.path.basename(file_path).lower()
        boost = 1.0
        
        for keyword, weight in self.HIGH_SIGNAL_KEYWORDS.items():
            if keyword in filename:
                boost *= weight
        
        return min(boost, 3.0)  # Cap at 3x boost
    
    def _analyze_file_content(self, file_path: str, repo_path: str) -> float:
        """Analyze file content for additional signal."""
        full_path = os.path.join(repo_path, file_path)
        score = 0.0
        
        try:
            # Only analyze text files
            if not self._is_text_file(file_path):
                return score
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for imports/exports (indicates dependencies)
            import_patterns = [
                r'import\s+.*from',  # ES6 imports
                r'require\s*\(',     # CommonJS requires
                r'from\s+.*import',  # Python imports
                r'include\s+',       # PHP includes
                r'using\s+',         # C# using statements
            ]
            
            for pattern in import_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    score += 0.5
                    break
            
            # Check for function/class definitions
            definition_patterns = [
                r'function\s+\w+',   # JavaScript functions
                r'class\s+\w+',      # Classes
                r'def\s+\w+',        # Python functions
                r'async\s+function', # Async functions
                r'const\s+\w+\s*=',  # Constants
                r'let\s+\w+\s*=',    # Variables
            ]
            
            for pattern in definition_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                score += len(matches) * 0.1
            
            # Check for API endpoints/routes
            route_patterns = [
                r'@app\.route',      # Flask routes
                r'@router\.',        # FastAPI routes
                r'router\.get',      # Express routes
                r'router\.post',     # Express routes
                r'@Get',             # NestJS routes
                r'@Post',            # NestJS routes
            ]
            
            for pattern in route_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    score += 1.0
                    break
            
            # Check for database operations
            db_patterns = [
                r'SELECT\s+.*FROM',  # SQL queries
                r'INSERT\s+INTO',    # SQL inserts
                r'UPDATE\s+.*SET',   # SQL updates
                r'DELETE\s+FROM',    # SQL deletes
                r'\.find\(',         # MongoDB operations
                r'\.save\(',         # Save operations
            ]
            
            for pattern in db_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    score += 0.5
                    break
            
        except (IOError, UnicodeDecodeError):
            pass
        
        return score
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if a file is likely a text file."""
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.dart', '.java', '.go',
            '.rs', '.php', '.rb', '.json', '.yaml', '.yml', '.toml',
            '.md', '.txt', '.css', '.scss', '.sass', '.html', '.xml',
            '.sql', '.sh', '.bat', '.env', '.gitignore'
        }
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_extensions
    
    def _calculate_size_adjustment(self, file_path: str, repo_path: str) -> float:
        """Calculate size-based adjustment for file score."""
        full_path = os.path.join(repo_path, file_path)
        
        try:
            size = os.path.getsize(full_path)
            
            # Prefer medium-sized files (not too small, not too large)
            if size < 100:  # Very small files
                return 0.7
            elif size < 1000:  # Small files
                return 0.9
            elif size < 10000:  # Medium files (ideal)
                return 1.0
            elif size < 50000:  # Large files
                return 0.8
            else:  # Very large files
                return 0.6
                
        except OSError:
            return 1.0
    
    def _calculate_relationship_boost(self, file_path: str) -> float:
        """Calculate relationship boost based on file references."""
        # This is a simplified version - in a full implementation,
        # you would analyze import/require statements across all files
        boost = 1.0
        
        # Check if file is in a commonly referenced directory
        path_parts = file_path.split(os.sep)
        if 'api' in path_parts or 'routes' in path_parts:
            boost *= 1.2
        if 'models' in path_parts or 'entities' in path_parts:
            boost *= 1.1
        if 'services' in path_parts:
            boost *= 1.1
        
        return boost
    
    def _categorize_file_by_score(self, score: float) -> str:
        """Categorize file by its signal score."""
        if score >= 9.0:
            return 'critical'
        elif score >= 7.0:
            return 'high'
        elif score >= 5.0:
            return 'medium'
        elif score >= 3.0:
            return 'low'
        else:
            return 'minimal'
    
    def _analyze_signal_distribution(self) -> Dict[str, Any]:
        """Analyze the distribution of signal scores."""
        if not self.signal_scores:
            return {}
        
        scores = list(self.signal_scores.values())
        
        analysis = {
            'total_files': len(scores),
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'score_distribution': {
                'critical': len([s for s in scores if s >= 9.0]),
                'high': len([s for s in scores if 7.0 <= s < 9.0]),
                'medium': len([s for s in scores if 5.0 <= s < 7.0]),
                'low': len([s for s in scores if 3.0 <= s < 5.0]),
                'minimal': len([s for s in scores if s < 3.0])
            },
            'top_files': self.ranked_files[:10] if self.ranked_files else []
        }
        
        return analysis 