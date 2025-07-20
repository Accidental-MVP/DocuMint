"""
Narrative Writer - Phase 6: Narrative Synthesis

Converts raw insights from the analysis pipeline into human-level summaries,
README narratives, and comprehensive project documentation.
"""

import os
from typing import Dict, List, Set, Optional, Any
from pathlib import Path
from datetime import datetime


class NarrativeWriter:
    """Converts analysis insights into human-readable narratives and documentation."""
    
    # README templates for different project types
    README_TEMPLATES = {
        'flutter_mobile': {
            'title': 'Mobile Application',
            'description_template': 'A cross-platform mobile application built with Flutter that provides {features}.',
            'sections': ['overview', 'features', 'tech_stack', 'getting_started', 'architecture', 'api_reference']
        },
        'react_web': {
            'title': 'Web Application',
            'description_template': 'A modern web application built with React that offers {features}.',
            'sections': ['overview', 'features', 'tech_stack', 'getting_started', 'architecture', 'api_reference']
        },
        'fastapi_backend': {
            'title': 'Backend API',
            'description_template': 'A high-performance backend API built with FastAPI that provides {features}.',
            'sections': ['overview', 'features', 'tech_stack', 'getting_started', 'api_documentation', 'deployment']
        },
        'mono_repo': {
            'title': 'Monorepo Project',
            'description_template': 'A comprehensive monorepo containing multiple applications and services: {features}.',
            'sections': ['overview', 'projects', 'tech_stack', 'getting_started', 'architecture', 'development']
        }
    }
    
    # Feature descriptions for narrative generation
    FEATURE_DESCRIPTIONS = {
        'authentication': 'secure user authentication and authorization',
        'payment_processing': 'secure payment processing and transaction management',
        'real_time_communication': 'real-time messaging and communication features',
        'file_management': 'file upload, storage, and management capabilities',
        'search_functionality': 'advanced search and discovery features',
        'dashboard_analytics': 'comprehensive analytics and reporting dashboard',
        'social_features': 'social networking and community features',
        'ecommerce': 'complete e-commerce and marketplace functionality',
        'booking_reservation': 'booking and reservation management system',
        'gaming': 'gaming and entertainment features'
    }
    
    # Technology stack descriptions
    STACK_DESCRIPTIONS = {
        'frontend': {
            'react': 'React.js for building interactive user interfaces',
            'vue': 'Vue.js for progressive web applications',
            'angular': 'Angular for enterprise-grade applications',
            'flutter': 'Flutter for cross-platform mobile development',
            'svelte': 'Svelte for lightweight, reactive applications'
        },
        'backend': {
            'python': 'Python with FastAPI/Django for robust backend services',
            'node': 'Node.js with Express for scalable server-side applications',
            'java': 'Java with Spring Boot for enterprise applications',
            'go': 'Go for high-performance microservices',
            'rust': 'Rust for systems programming and performance-critical applications'
        },
        'database': {
            'sql': 'SQL databases for structured data storage',
            'nosql': 'NoSQL databases for flexible data models',
            'cloud': 'Cloud-based database solutions for scalability'
        }
    }
    
    def __init__(self):
        self.project_name = ""
        self.project_description = ""
        self.generated_narratives = {}
    
    def compose_readme_narrative(self, repo_path: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compose a comprehensive README narrative from analysis data.
        
        Args:
            repo_path: Path to the repository root
            analysis_data: Combined output from all analysis phases
            
        Returns:
            Dict containing README content, project summary, and narrative insights
        """
        # Extract data from analysis
        repo_type = analysis_data.get('repo_type', {})
        dependencies = analysis_data.get('dependencies', {})
        structure = analysis_data.get('structure', {})
        features = analysis_data.get('features', {})
        
        # Get project metadata
        self._extract_project_metadata(repo_path, dependencies)
        
        # Generate README content
        readme_content = self._generate_readme_content(repo_type, dependencies, structure, features)
        
        # Generate project summary
        project_summary = self._generate_project_summary(repo_type, dependencies, structure, features)
        
        # Generate narrative insights
        narrative_insights = self._generate_narrative_insights(analysis_data)
        
        return {
            'readme_content': readme_content,
            'project_summary': project_summary,
            'narrative_insights': narrative_insights,
            'metadata': {
                'project_name': self.project_name,
                'project_description': self.project_description,
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def _extract_project_metadata(self, repo_path: str, dependencies: Dict[str, Any]):
        """Extract project name and description from metadata."""
        # Try to get project name from dependencies
        if 'project_name' in dependencies:
            self.project_name = dependencies['project_name']
        else:
            # Fall back to directory name
            self.project_name = os.path.basename(repo_path)
        
        # Try to get project description
        if 'description' in dependencies:
            self.project_description = dependencies['description']
        else:
            self.project_description = f"A {self.project_name} project"
    
    def _generate_readme_content(self, repo_type: Dict[str, Any], dependencies: Dict[str, Any], 
                               structure: Dict[str, Any], features: Dict[str, Any]) -> str:
        """Generate comprehensive README content."""
        repo_type_name = repo_type.get('type', 'unknown')
        template = self.README_TEMPLATES.get(repo_type_name, self.README_TEMPLATES['react_web'])
        
        # Build README sections
        sections = []
        
        # Header
        sections.append(self._generate_header(template['title']))
        
        # Overview
        if 'overview' in template['sections']:
            sections.append(self._generate_overview_section(dependencies, features))
        
        # Features
        if 'features' in template['sections']:
            sections.append(self._generate_features_section(features))
        
        # Tech Stack
        if 'tech_stack' in template['sections']:
            sections.append(self._generate_tech_stack_section(dependencies))
        
        # Getting Started
        if 'getting_started' in template['sections']:
            sections.append(self._generate_getting_started_section(repo_type, dependencies))
        
        # Architecture
        if 'architecture' in template['sections']:
            sections.append(self._generate_architecture_section(structure))
        
        # API Reference
        if 'api_reference' in template['sections']:
            sections.append(self._generate_api_reference_section(structure))
        
        # API Documentation
        if 'api_documentation' in template['sections']:
            sections.append(self._generate_api_documentation_section(structure))
        
        # Deployment
        if 'deployment' in template['sections']:
            sections.append(self._generate_deployment_section(dependencies))
        
        # Development
        if 'development' in template['sections']:
            sections.append(self._generate_development_section(structure))
        
        return '\n\n'.join(sections)
    
    def _generate_header(self, project_type: str) -> str:
        """Generate README header."""
        return f"""# {self.project_name}

{self.project_description}

## Overview

This is a {project_type.lower()} that provides a comprehensive solution for modern application development.

---
"""
    
    def _generate_overview_section(self, dependencies: Dict[str, Any], features: Dict[str, Any]) -> str:
        """Generate overview section."""
        # Get detected features
        detected_features = list(features.get('inferred_features', {}).keys())
        
        # Create feature description
        if detected_features:
            feature_descriptions = []
            for feature in detected_features[:5]:  # Limit to top 5 features
                desc = self.FEATURE_DESCRIPTIONS.get(feature, feature.replace('_', ' '))
                feature_descriptions.append(desc)
            
            features_text = ', '.join(feature_descriptions)
        else:
            features_text = "modern application functionality"
        
        # Get project description from dependencies
        project_desc = dependencies.get('description', self.project_description)
        
        return f"""## Overview

{project_desc}

This project provides {features_text} with a focus on performance, scalability, and user experience.

### Key Highlights

- **Modern Architecture**: Built with cutting-edge technologies and best practices
- **Scalable Design**: Designed to handle growth and increased user demand
- **User-Centric**: Focused on delivering exceptional user experiences
- **Secure**: Implements industry-standard security practices
- **Maintainable**: Clean, well-documented codebase for easy maintenance

"""
    
    def _generate_features_section(self, features: Dict[str, Any]) -> str:
        """Generate features section."""
        inferred_features = features.get('inferred_features', {})
        
        if not inferred_features:
            return """## Features

- Modern, responsive user interface
- Secure authentication and authorization
- RESTful API endpoints
- Database integration
- Real-time updates
- Mobile-responsive design

"""
        
        # Sort features by confidence
        sorted_features = sorted(
            inferred_features.items(),
            key=lambda x: x[1].get('confidence', 0),
            reverse=True
        )
        
        features_content = ["## Features\n"]
        
        for feature_name, feature_data in sorted_features:
            confidence = feature_data.get('confidence', 0)
            evidence = feature_data.get('evidence', [])
            
            # Get human-readable feature name
            feature_display = feature_name.replace('_', ' ').title()
            
            features_content.append(f"### {feature_display}")
            
            # Add feature description
            desc = self.FEATURE_DESCRIPTIONS.get(feature_name, f"{feature_display.lower()} capabilities")
            features_content.append(f"{desc}.")
            
            # Add evidence if available
            if evidence:
                features_content.append(f"\n**Detected indicators:**")
                for ev in evidence[:3]:  # Limit to 3 pieces of evidence
                    features_content.append(f"- {ev}")
            
            features_content.append("")  # Empty line for spacing
        
        return '\n'.join(features_content)
    
    def _generate_tech_stack_section(self, dependencies: Dict[str, Any]) -> str:
        """Generate technology stack section."""
        stack = dependencies.get('stack', {})
        
        if not stack:
            return """## Technology Stack

- **Frontend**: Modern JavaScript framework
- **Backend**: Robust server-side technology
- **Database**: Reliable data storage solution
- **Deployment**: Cloud-based hosting platform

"""
        
        stack_content = ["## Technology Stack\n"]
        
        # Frontend technologies
        if 'frontend' in stack and stack['frontend']:
            stack_content.append("### Frontend")
            for tech in stack['frontend']:
                desc = self.STACK_DESCRIPTIONS['frontend'].get(tech, f"{tech.title()} for frontend development")
                stack_content.append(f"- **{tech.title()}**: {desc}")
            stack_content.append("")
        
        # Backend technologies
        if 'backend' in stack and stack['backend']:
            stack_content.append("### Backend")
            for tech in stack['backend']:
                desc = self.STACK_DESCRIPTIONS['backend'].get(tech, f"{tech.title()} for backend services")
                stack_content.append(f"- **{tech.title()}**: {desc}")
            stack_content.append("")
        
        # Database technologies
        if 'database' in stack and stack['database']:
            stack_content.append("### Database")
            for tech in stack['database']:
                desc = self.STACK_DESCRIPTIONS['database'].get(tech, f"{tech.title()} for data storage")
                stack_content.append(f"- **{tech.title()}**: {desc}")
            stack_content.append("")
        
        # External services
        external_services = dependencies.get('external_services', [])
        if external_services:
            stack_content.append("### External Services")
            for service in external_services:
                stack_content.append(f"- **{service.title()}**: {service.title()} integration for enhanced functionality")
            stack_content.append("")
        
        return '\n'.join(stack_content)
    
    def _generate_getting_started_section(self, repo_type: Dict[str, Any], dependencies: Dict[str, Any]) -> str:
        """Generate getting started section."""
        repo_type_name = repo_type.get('type', 'unknown')
        
        # Determine setup commands based on repo type
        if repo_type_name == 'flutter_mobile':
            setup_commands = """```bash
# Install Flutter dependencies
flutter pub get

# Run the application
flutter run
```"""
        elif repo_type_name == 'react_web':
            setup_commands = """```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```"""
        elif repo_type_name == 'fastapi_backend':
            setup_commands = """```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```"""
        else:
            setup_commands = """```bash
# Install dependencies
npm install

# Start development server
npm start
```"""
        
        return f"""## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd {self.project_name}
```

2. Install dependencies:
{setup_commands}

### Environment Setup

Create a `.env` file in the root directory and configure the following variables:

```env
# Database configuration
DATABASE_URL=your_database_url

# API keys
API_KEY=your_api_key

# Environment
NODE_ENV=development
```

### Running the Application

Follow the setup commands above to start the application.

"""
    
    def _generate_architecture_section(self, structure: Dict[str, Any]) -> str:
        """Generate architecture section."""
        structure_analysis = structure.get('structure_analysis', {})
        architecture_pattern = structure_analysis.get('architecture_pattern', 'modular')
        
        return f"""## Architecture

This project follows a **{architecture_pattern.replace('_', ' ').title()}** architecture pattern designed for scalability and maintainability.

### Project Structure

```
{self.project_name}/
├── src/                    # Source code
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page components
│   ├── services/          # Business logic services
│   ├── utils/             # Utility functions
│   └── styles/            # Styling files
├── public/                # Static assets
├── tests/                 # Test files
├── docs/                  # Documentation
└── config/                # Configuration files
```

### Key Components

- **Frontend Layer**: User interface and client-side logic
- **Backend Layer**: Server-side business logic and API endpoints
- **Data Layer**: Database models and data access logic
- **Service Layer**: External service integrations and utilities

### Design Patterns

- **Component-Based Architecture**: Modular, reusable components
- **Service-Oriented Design**: Separation of concerns through services
- **RESTful API Design**: Standardized API endpoints
- **Responsive Design**: Mobile-first approach

"""
    
    def _generate_api_reference_section(self, structure: Dict[str, Any]) -> str:
        """Generate API reference section."""
        return """## API Reference

### Authentication

```http
POST /api/auth/login
POST /api/auth/register
GET /api/auth/profile
```

### Core Endpoints

```http
GET /api/users
GET /api/users/{id}
POST /api/users
PUT /api/users/{id}
DELETE /api/users/{id}
```

### Response Format

All API responses follow a standard format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

For detailed API documentation, visit `/docs` when running the application.

"""
    
    def _generate_api_documentation_section(self, structure: Dict[str, Any]) -> str:
        """Generate API documentation section."""
        return """## API Documentation

This project includes comprehensive API documentation generated automatically.

### Interactive Documentation

When the application is running, you can access:

- **Swagger UI**: `/docs` - Interactive API documentation
- **ReDoc**: `/redoc` - Alternative documentation view
- **OpenAPI Schema**: `/openapi.json` - Raw OpenAPI specification

### API Endpoints

The API is organized into the following categories:

- **Authentication**: User registration, login, and profile management
- **Core Resources**: CRUD operations for main entities
- **Business Logic**: Application-specific operations
- **Utilities**: Helper endpoints and utilities

### Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. Register or login to receive a token
2. Include the token in the `Authorization` header
3. Format: `Bearer <your-token>`

"""
    
    def _generate_deployment_section(self, dependencies: Dict[str, Any]) -> str:
        """Generate deployment section."""
        return """## Deployment

### Production Build

```bash
# Build the application
npm run build

# Start production server
npm start
```

### Docker Deployment

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables

Configure the following environment variables for production:

```env
NODE_ENV=production
PORT=3000
DATABASE_URL=your_production_database_url
API_KEY=your_production_api_key
```

### Cloud Deployment

This application can be deployed to various cloud platforms:

- **Vercel**: Optimized for Next.js applications
- **Netlify**: Great for static sites and JAMstack
- **AWS**: Scalable cloud infrastructure
- **Google Cloud**: Enterprise-grade hosting
- **Heroku**: Simple deployment platform

"""
    
    def _generate_development_section(self, structure: Dict[str, Any]) -> str:
        """Generate development section."""
        return """## Development

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `npm test`
5. Commit your changes: `git commit -m 'Add your feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Open a Pull Request

### Code Style

This project follows standard coding conventions:

- Use meaningful variable and function names
- Write clear, descriptive comments
- Follow the established file structure
- Include tests for new features

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

"""
    
    def _generate_project_summary(self, repo_type: Dict[str, Any], dependencies: Dict[str, Any], 
                                structure: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive project summary."""
        # Extract key information
        repo_type_name = repo_type.get('type', 'unknown')
        confidence = repo_type.get('confidence', 0)
        
        # Get detected features
        inferred_features = features.get('inferred_features', {})
        feature_count = len(inferred_features)
        
        # Get tech stack
        stack = dependencies.get('stack', {})
        external_services = dependencies.get('external_services', [])
        
        # Get structure analysis
        structure_analysis = structure.get('structure_analysis', {})
        architecture_pattern = structure_analysis.get('architecture_pattern', 'unknown')
        
        return {
            'project_name': self.project_name,
            'project_type': repo_type_name,
            'type_confidence': confidence,
            'description': self.project_description,
            'feature_count': feature_count,
            'detected_features': list(inferred_features.keys()),
            'tech_stack': stack,
            'external_services': external_services,
            'architecture_pattern': architecture_pattern,
            'complexity_score': structure_analysis.get('complexity_indicators', {}).get('complexity_score', 0),
            'file_count': structure_analysis.get('complexity_indicators', {}).get('file_count', 0)
        }
    
    def _generate_narrative_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate narrative insights from the analysis."""
        insights = {
            'key_findings': [],
            'recommendations': [],
            'architecture_insights': [],
            'feature_insights': []
        }
        
        # Extract data
        repo_type = analysis_data.get('repo_type', {})
        dependencies = analysis_data.get('dependencies', {})
        structure = analysis_data.get('structure', {})
        features = analysis_data.get('features', {})
        
        # Key findings
        if repo_type.get('confidence', 0) > 0.7:
            insights['key_findings'].append(f"High-confidence detection of {repo_type.get('type', 'unknown')} project type")
        
        if dependencies.get('external_services'):
            insights['key_findings'].append(f"Integrates with {len(dependencies['external_services'])} external services")
        
        if features.get('inferred_features'):
            insights['key_findings'].append(f"Detected {len(features['inferred_features'])} distinct features")
        
        # Architecture insights
        structure_analysis = structure.get('structure_analysis', {})
        if structure_analysis.get('architecture_pattern'):
            insights['architecture_insights'].append(
                f"Follows {structure_analysis['architecture_pattern']} architecture pattern"
            )
        
        # Feature insights
        inferred_features = features.get('inferred_features', {})
        if inferred_features:
            top_features = sorted(
                inferred_features.items(),
                key=lambda x: x[1].get('confidence', 0),
                reverse=True
            )[:3]
            
            for feature, data in top_features:
                insights['feature_insights'].append(
                    f"Strong evidence for {feature.replace('_', ' ')} functionality"
                )
        
        # Recommendations
        if not dependencies.get('external_services'):
            insights['recommendations'].append("Consider integrating external services for enhanced functionality")
        
        if structure_analysis.get('complexity_indicators', {}).get('complexity_score', 0) > 0.7:
            insights['recommendations'].append("High complexity detected - consider refactoring for maintainability")
        
        return insights 