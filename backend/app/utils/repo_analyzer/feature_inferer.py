"""
Feature Inferer - Phase 5: Flow + Feature Inference

Links routes, components, and services to reconstruct UX and user flows.
Infers application features and user journeys based on code structure and patterns.
"""

import os
import re
from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict


class FeatureInferer:
    """Infers application features and user flows from code structure."""
    
    # Feature patterns that indicate specific functionality
    FEATURE_PATTERNS = {
        'authentication': {
            'files': ['auth', 'login', 'register', 'signin', 'signup', 'user', 'profile'],
            'routes': ['/auth', '/login', '/register', '/signin', '/signup', '/user', '/profile'],
            'components': ['LoginForm', 'RegisterForm', 'UserProfile', 'AuthGuard'],
            'services': ['AuthService', 'UserService', 'TokenService'],
            'keywords': ['authentication', 'authorization', 'jwt', 'oauth', 'session']
        },
        'payment_processing': {
            'files': ['payment', 'stripe', 'paypal', 'checkout', 'billing', 'invoice', 'order'],
            'routes': ['/payment', '/checkout', '/billing', '/orders', '/invoices'],
            'components': ['PaymentForm', 'CheckoutPage', 'OrderSummary', 'BillingInfo'],
            'services': ['PaymentService', 'StripeService', 'OrderService'],
            'keywords': ['payment', 'stripe', 'paypal', 'checkout', 'billing', 'transaction']
        },
        'real_time_communication': {
            'files': ['chat', 'message', 'socket', 'websocket', 'notification', 'room'],
            'routes': ['/chat', '/messages', '/rooms', '/notifications'],
            'components': ['ChatRoom', 'MessageList', 'NotificationCenter', 'SocketManager'],
            'services': ['ChatService', 'SocketService', 'NotificationService'],
            'keywords': ['websocket', 'socket.io', 'real-time', 'chat', 'notification']
        },
        'file_management': {
            'files': ['upload', 'file', 'image', 'media', 'attachment', 'storage'],
            'routes': ['/upload', '/files', '/media', '/attachments'],
            'components': ['FileUpload', 'ImageGallery', 'MediaViewer', 'FileManager'],
            'services': ['FileService', 'UploadService', 'StorageService'],
            'keywords': ['upload', 'file', 'image', 'media', 'storage', 'cloudinary']
        },
        'search_functionality': {
            'files': ['search', 'query', 'filter', 'find', 'explore'],
            'routes': ['/search', '/explore', '/discover'],
            'components': ['SearchBar', 'SearchResults', 'FilterPanel', 'SearchFilters'],
            'services': ['SearchService', 'QueryService', 'FilterService'],
            'keywords': ['search', 'query', 'filter', 'elasticsearch', 'algolia']
        },
        'dashboard_analytics': {
            'files': ['dashboard', 'admin', 'analytics', 'stats', 'metrics', 'report'],
            'routes': ['/dashboard', '/admin', '/analytics', '/reports'],
            'components': ['Dashboard', 'AdminPanel', 'AnalyticsChart', 'MetricsCard'],
            'services': ['AnalyticsService', 'DashboardService', 'ReportService'],
            'keywords': ['dashboard', 'analytics', 'metrics', 'report', 'chart', 'graph']
        },
        'social_features': {
            'files': ['social', 'friend', 'follow', 'like', 'share', 'comment', 'post'],
            'routes': ['/social', '/friends', '/follow', '/posts', '/comments'],
            'components': ['SocialFeed', 'FriendList', 'LikeButton', 'ShareButton'],
            'services': ['SocialService', 'FriendService', 'PostService'],
            'keywords': ['social', 'friend', 'follow', 'like', 'share', 'comment']
        },
        'ecommerce': {
            'files': ['product', 'cart', 'shop', 'store', 'marketplace', 'catalog'],
            'routes': ['/products', '/cart', '/shop', '/store', '/catalog'],
            'components': ['ProductCard', 'ShoppingCart', 'ProductList', 'StoreFront'],
            'services': ['ProductService', 'CartService', 'StoreService'],
            'keywords': ['product', 'cart', 'shop', 'store', 'marketplace', 'catalog']
        },
        'booking_reservation': {
            'files': ['booking', 'reservation', 'appointment', 'schedule', 'calendar'],
            'routes': ['/booking', '/reservations', '/appointments', '/schedule'],
            'components': ['BookingForm', 'Calendar', 'AppointmentSlot', 'ReservationList'],
            'services': ['BookingService', 'CalendarService', 'AppointmentService'],
            'keywords': ['booking', 'reservation', 'appointment', 'schedule', 'calendar']
        },
        'gaming': {
            'files': ['game', 'player', 'score', 'leaderboard', 'level', 'achievement'],
            'routes': ['/game', '/players', '/leaderboard', '/scores'],
            'components': ['GameBoard', 'PlayerProfile', 'Leaderboard', 'ScoreCard'],
            'services': ['GameService', 'PlayerService', 'ScoreService'],
            'keywords': ['game', 'player', 'score', 'leaderboard', 'level', 'achievement']
        }
    }
    
    # User flow patterns
    USER_FLOW_PATTERNS = {
        'onboarding': ['register', 'login', 'welcome', 'tutorial', 'setup'],
        'purchase_flow': ['browse', 'product', 'cart', 'checkout', 'payment', 'confirmation'],
        'social_interaction': ['profile', 'friend', 'message', 'post', 'comment', 'like'],
        'content_creation': ['create', 'edit', 'upload', 'publish', 'share'],
        'search_discovery': ['search', 'filter', 'browse', 'explore', 'discover'],
        'notification_management': ['notification', 'alert', 'email', 'push', 'settings']
    }
    
    def __init__(self):
        self.inferred_features = {}
        self.user_flows = []
        self.feature_relationships = defaultdict(list)
        self.ux_patterns = []
    
    def infer_features_and_user_flow(self, repo_path: str, structure_data: Dict[str, Any], 
                                   dependency_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infer application features and user flows from code structure.
        
        Args:
            repo_path: Path to the repository root
            structure_data: Output from structure mapper
            dependency_data: Output from dependency parser
            
        Returns:
            Dict containing inferred features, user flows, and UX patterns
        """
        self.inferred_features = {}
        self.user_flows = []
        self.feature_relationships = defaultdict(list)
        self.ux_patterns = []
        
        # Extract file and directory information
        file_categories = structure_data.get('file_categories', {})
        directory_categories = structure_data.get('directory_categories', {})
        feature_map = structure_data.get('feature_map', {})
        
        # Infer features from file patterns
        self._infer_features_from_files(repo_path, file_categories)
        
        # Infer features from directory structure
        self._infer_features_from_directories(directory_categories)
        
        # Infer features from dependencies
        self._infer_features_from_dependencies(dependency_data)
        
        # Infer features from existing feature map
        self._infer_features_from_feature_map(feature_map)
        
        # Build user flows
        self._build_user_flows()
        
        # Analyze feature relationships
        self._analyze_feature_relationships()
        
        # Identify UX patterns
        self._identify_ux_patterns()
        
        return {
            'inferred_features': self.inferred_features,
            'user_flows': self.user_flows,
            'feature_relationships': dict(self.feature_relationships),
            'ux_patterns': self.ux_patterns
        }
    
    def _infer_features_from_files(self, repo_path: str, file_categories: Dict[str, List[str]]):
        """Infer features from file patterns and content."""
        for category, files in file_categories.items():
            for file_path in files:
                filename = os.path.basename(file_path).lower()
                
                # Check each feature pattern
                for feature, patterns in self.FEATURE_PATTERNS.items():
                    score = 0.0
                    evidence = []
                    
                    # Check file name patterns
                    for pattern in patterns['files']:
                        if pattern in filename:
                            score += 2.0
                            evidence.append(f"File name contains '{pattern}'")
                    
                    # Check component patterns
                    for pattern in patterns['components']:
                        if pattern.lower() in filename:
                            score += 1.5
                            evidence.append(f"Component pattern '{pattern}' found")
                    
                    # Check service patterns
                    for pattern in patterns['services']:
                        if pattern.lower() in filename:
                            score += 1.5
                            evidence.append(f"Service pattern '{pattern}' found")
                    
                    # Analyze file content for keywords
                    content_score, content_evidence = self._analyze_file_content_for_keywords(
                        file_path, repo_path, patterns['keywords']
                    )
                    score += content_score
                    evidence.extend(content_evidence)
                    
                    # Add feature if score is high enough
                    if score >= 1.0:
                        if feature not in self.inferred_features:
                            self.inferred_features[feature] = {
                                'confidence': score,
                                'evidence': evidence,
                                'files': []
                            }
                        else:
                            # Update existing feature
                            self.inferred_features[feature]['confidence'] += score
                            self.inferred_features[feature]['evidence'].extend(evidence)
                        
                        self.inferred_features[feature]['files'].append(file_path)
    
    def _infer_features_from_directories(self, directory_categories: Dict[str, List[str]]):
        """Infer features from directory structure."""
        for category, directories in directory_categories.items():
            for directory in directories:
                dir_name = os.path.basename(directory).lower()
                
                for feature, patterns in self.FEATURE_PATTERNS.items():
                    score = 0.0
                    evidence = []
                    
                    # Check directory name patterns
                    for pattern in patterns['files']:
                        if pattern in dir_name:
                            score += 1.5
                            evidence.append(f"Directory name contains '{pattern}'")
                    
                    # Check route patterns
                    for pattern in patterns['routes']:
                        if pattern.strip('/') in dir_name:
                            score += 2.0
                            evidence.append(f"Route pattern '{pattern}' found")
                    
                    # Add feature if score is high enough
                    if score >= 1.0:
                        if feature not in self.inferred_features:
                            self.inferred_features[feature] = {
                                'confidence': score,
                                'evidence': evidence,
                                'directories': []
                            }
                        else:
                            self.inferred_features[feature]['confidence'] += score
                            self.inferred_features[feature]['evidence'].extend(evidence)
                        
                        if 'directories' not in self.inferred_features[feature]:
                            self.inferred_features[feature]['directories'] = []
                        self.inferred_features[feature]['directories'].append(directory)
    
    def _infer_features_from_dependencies(self, dependency_data: Dict[str, Any]):
        """Infer features from dependency information."""
        features = dependency_data.get('features', [])
        external_services = dependency_data.get('external_services', [])
        
        for feature in features:
            if feature not in self.inferred_features:
                self.inferred_features[feature] = {
                    'confidence': 3.0,  # High confidence from dependencies
                    'evidence': [f"Dependency analysis detected {feature}"],
                    'source': 'dependencies'
                }
            else:
                self.inferred_features[feature]['confidence'] += 3.0
                self.inferred_features[feature]['evidence'].append(f"Dependency analysis confirmed {feature}")
        
        # Map external services to features
        service_feature_map = {
            'stripe': 'payment_processing',
            'firebase': 'authentication',
            'supabase': 'authentication',
            'aws': 'file_management',
            'google_cloud': 'file_management',
            'twilio': 'real_time_communication',
            'sendgrid': 'notification',
            'pusher': 'real_time_communication'
        }
        
        for service in external_services:
            if service in service_feature_map:
                feature = service_feature_map[service]
                if feature not in self.inferred_features:
                    self.inferred_features[feature] = {
                        'confidence': 2.5,
                        'evidence': [f"External service '{service}' indicates {feature}"],
                        'external_services': [service]
                    }
                else:
                    self.inferred_features[feature]['confidence'] += 2.5
                    self.inferred_features[feature]['evidence'].append(f"External service '{service}' confirms {feature}")
    
    def _infer_features_from_feature_map(self, feature_map: Dict[str, List[Dict]]):
        """Infer features from existing feature map."""
        for feature, items in feature_map.items():
            if feature not in self.inferred_features:
                self.inferred_features[feature] = {
                    'confidence': len(items) * 1.0,
                    'evidence': [f"Structure analysis found {len(items)} {feature} indicators"],
                    'structure_items': items
                }
            else:
                self.inferred_features[feature]['confidence'] += len(items) * 1.0
                self.inferred_features[feature]['evidence'].append(f"Structure analysis confirmed {feature}")
    
    def _analyze_file_content_for_keywords(self, file_path: str, repo_path: str, 
                                         keywords: List[str]) -> Tuple[float, List[str]]:
        """Analyze file content for feature keywords."""
        full_path = os.path.join(repo_path, file_path)
        score = 0.0
        evidence = []
        
        try:
            if not self._is_text_file(file_path):
                return score, evidence
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            for keyword in keywords:
                if keyword in content:
                    score += 0.5
                    evidence.append(f"Content contains '{keyword}'")
            
        except (IOError, UnicodeDecodeError):
            pass
        
        return score, evidence
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if a file is likely a text file."""
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.dart', '.java', '.go',
            '.rs', '.php', '.rb', '.json', '.yaml', '.yml', '.toml',
            '.md', '.txt', '.css', '.scss', '.sass', '.html', '.xml',
            '.sql', '.sh', '.bat', '.env'
        }
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in text_extensions
    
    def _build_user_flows(self):
        """Build user flows based on inferred features."""
        # Map features to user flows
        feature_flow_map = {
            'authentication': ['onboarding'],
            'payment_processing': ['purchase_flow'],
            'social_features': ['social_interaction'],
            'file_management': ['content_creation'],
            'search_functionality': ['search_discovery'],
            'notification': ['notification_management']
        }
        
        for feature, flows in feature_flow_map.items():
            if feature in self.inferred_features:
                for flow in flows:
                    self.user_flows.append({
                        'flow': flow,
                        'features': [feature],
                        'confidence': self.inferred_features[feature]['confidence'],
                        'description': self._generate_flow_description(flow, feature)
                    })
        
        # Build complex flows from multiple features
        self._build_complex_user_flows()
    
    def _build_complex_user_flows(self):
        """Build complex user flows that involve multiple features."""
        # E-commerce flow
        ecommerce_features = ['ecommerce', 'payment_processing', 'authentication']
        if all(feature in self.inferred_features for feature in ecommerce_features):
            self.user_flows.append({
                'flow': 'ecommerce_purchase',
                'features': ecommerce_features,
                'confidence': sum(self.inferred_features[f]['confidence'] for f in ecommerce_features),
                'description': 'Complete e-commerce purchase flow from browsing to payment'
            })
        
        # Social platform flow
        social_features = ['social_features', 'authentication', 'file_management']
        if all(feature in self.inferred_features for feature in social_features):
            self.user_flows.append({
                'flow': 'social_content_creation',
                'features': social_features,
                'confidence': sum(self.inferred_features[f]['confidence'] for f in social_features),
                'description': 'Social platform content creation and sharing flow'
            })
        
        # Dashboard flow
        dashboard_features = ['dashboard_analytics', 'authentication', 'search_functionality']
        if all(feature in self.inferred_features for feature in dashboard_features):
            self.user_flows.append({
                'flow': 'dashboard_analytics',
                'features': dashboard_features,
                'confidence': sum(self.inferred_features[f]['confidence'] for f in dashboard_features),
                'description': 'Dashboard analytics and reporting flow'
            })
    
    def _generate_flow_description(self, flow: str, feature: str) -> str:
        """Generate a description for a user flow."""
        flow_descriptions = {
            'onboarding': f'User registration and initial setup process',
            'purchase_flow': f'Product selection, cart management, and payment processing',
            'social_interaction': f'User interaction, content sharing, and social features',
            'content_creation': f'Content creation, editing, and publishing workflow',
            'search_discovery': f'Content discovery and search functionality',
            'notification_management': f'User notification preferences and management'
        }
        
        return flow_descriptions.get(flow, f'{flow} flow involving {feature}')
    
    def _analyze_feature_relationships(self):
        """Analyze relationships between different features."""
        features = list(self.inferred_features.keys())
        
        for i, feature1 in enumerate(features):
            for feature2 in features[i+1:]:
                relationship_score = self._calculate_feature_relationship(feature1, feature2)
                
                if relationship_score > 0.5:
                    self.feature_relationships[feature1].append({
                        'related_feature': feature2,
                        'relationship_score': relationship_score,
                        'relationship_type': self._determine_relationship_type(feature1, feature2)
                    })
    
    def _calculate_feature_relationship(self, feature1: str, feature2: str) -> float:
        """Calculate the relationship score between two features."""
        # Define feature relationships
        relationships = {
            ('authentication', 'payment_processing'): 0.8,
            ('authentication', 'social_features'): 0.7,
            ('authentication', 'dashboard_analytics'): 0.6,
            ('payment_processing', 'ecommerce'): 0.9,
            ('file_management', 'social_features'): 0.7,
            ('file_management', 'content_creation'): 0.8,
            ('search_functionality', 'ecommerce'): 0.6,
            ('search_functionality', 'social_features'): 0.5,
            ('real_time_communication', 'social_features'): 0.8,
            ('notification', 'social_features'): 0.6,
            ('notification', 'ecommerce'): 0.5
        }
        
        # Check both directions
        key1 = (feature1, feature2)
        key2 = (feature2, feature1)
        
        return relationships.get(key1, relationships.get(key2, 0.0))
    
    def _determine_relationship_type(self, feature1: str, feature2: str) -> str:
        """Determine the type of relationship between features."""
        relationship_types = {
            ('authentication', 'payment_processing'): 'prerequisite',
            ('authentication', 'social_features'): 'enabler',
            ('payment_processing', 'ecommerce'): 'core_component',
            ('file_management', 'social_features'): 'enhancement',
            ('real_time_communication', 'social_features'): 'enhancement',
            ('notification', 'social_features'): 'supporting'
        }
        
        key1 = (feature1, feature2)
        key2 = (feature2, feature1)
        
        return relationship_types.get(key1, relationship_types.get(key2, 'related'))
    
    def _identify_ux_patterns(self):
        """Identify UX patterns based on inferred features."""
        patterns = []
        
        # Authentication patterns
        if 'authentication' in self.inferred_features:
            patterns.append({
                'pattern': 'user_registration_flow',
                'description': 'User registration and login system',
                'features': ['authentication'],
                'confidence': self.inferred_features['authentication']['confidence']
            })
        
        # Payment patterns
        if 'payment_processing' in self.inferred_features:
            patterns.append({
                'pattern': 'secure_payment_flow',
                'description': 'Secure payment processing with multiple options',
                'features': ['payment_processing'],
                'confidence': self.inferred_features['payment_processing']['confidence']
            })
        
        # Social patterns
        if 'social_features' in self.inferred_features:
            patterns.append({
                'pattern': 'social_interaction_ui',
                'description': 'Social media-style interaction interface',
                'features': ['social_features'],
                'confidence': self.inferred_features['social_features']['confidence']
            })
        
        # Dashboard patterns
        if 'dashboard_analytics' in self.inferred_features:
            patterns.append({
                'pattern': 'data_visualization_dashboard',
                'description': 'Analytics dashboard with charts and metrics',
                'features': ['dashboard_analytics'],
                'confidence': self.inferred_features['dashboard_analytics']['confidence']
            })
        
        self.ux_patterns = patterns 