# Repo Analyzer - Oracle-Level Repository Understanding Engine

A comprehensive repository analysis system that implements a six-phase pipeline to understand any codebase at a deep, contextual level. This module transforms your README generator from "good" to **oracle-level** by providing intelligent, context-aware repository understanding.

## 🧠 The Core Mental Model

The Repo Analyzer implements the same six-phase loop that makes Cursor's repository understanding so powerful:

| Phase | What It Does | Implementation |
|-------|-------------|----------------|
| **1. Classification** | Detects repo type (web, mobile, backend, etc.) | `RepoTypeDetector` |
| **2. Dependency Mapping** | Parses dependencies to infer stack, features, APIs | `DependencyParser` |
| **3. Structure Mapping** | Builds internal map of folder → feature relationships | `StructureMapper` |
| **4. Signal Extraction** | Identifies high-signal files (routes, models, services) | `SignalRanker` |
| **5. Flow + Feature Inference** | Links components to reconstruct UX and logic | `FeatureInferer` |
| **6. Narrative Synthesis** | Converts insights into human-level summaries | `NarrativeWriter` |

## 🏗️ Architecture

```
repo_analyzer/
├── __init__.py              # Main entry point and exports
├── analyzer.py              # Main orchestrator (RepoAnalyzer)
├── detector.py              # Phase 1: RepoTypeDetector
├── dependency_parser.py     # Phase 2: DependencyParser
├── structure_mapper.py      # Phase 3: StructureMapper
├── signal_ranker.py         # Phase 4: SignalRanker
├── feature_inferer.py       # Phase 5: FeatureInferer
├── narrative_writer.py      # Phase 6: NarrativeWriter
└── README.md               # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from app.utils.repo_analyzer import RepoAnalyzer

# Initialize the analyzer
analyzer = RepoAnalyzer()

# Analyze a repository
results = analyzer.analyze_repository("/path/to/repository")

# Get insights
insights = analyzer.get_analysis_insights()

# Export results
analyzer.export_results("analysis.json", "json")
analyzer.export_results("README.md", "markdown")
```

### Advanced Usage

```python
# Run specific phases
repo_type = analyzer.analyze_phase("/path/to/repo", "classification")
dependencies = analyzer.analyze_phase("/path/to/repo", "dependencies")
structure = analyzer.analyze_phase("/path/to/repo", "structure")

# Get comprehensive analysis without narrative
results = analyzer.analyze_repository("/path/to/repo", include_narrative=False)

# Export in multiple formats
analyzer.export_results("results.json", "json")
analyzer.export_results("generated_readme.md", "markdown")
analyzer.export_results("report.html", "html")
```

## 📊 What It Detects

### Repository Types
- **Flutter Mobile**: Cross-platform mobile apps
- **React Web**: Modern web applications
- **FastAPI Backend**: High-performance APIs
- **Django Backend**: Full-stack web frameworks
- **Express Backend**: Node.js applications
- **Chrome Extension**: Browser extensions
- **Mono Repo**: Multi-project repositories
- **Python Library**: Python packages
- **Node Library**: JavaScript packages
- **Docker Project**: Containerized applications
- **Terraform Infra**: Infrastructure as code

### Features
- **Authentication**: User login, registration, JWT
- **Payment Processing**: Stripe, PayPal, checkout flows
- **Real-time Communication**: WebSockets, chat, notifications
- **File Management**: Upload, storage, media handling
- **Search Functionality**: Search, filtering, discovery
- **Dashboard Analytics**: Metrics, reporting, charts
- **Social Features**: Social networking, sharing
- **E-commerce**: Shopping carts, marketplaces
- **Booking/Reservation**: Appointment scheduling
- **Gaming**: Game mechanics, scoring

### Architecture Patterns
- **MVC**: Model-View-Controller
- **Layered**: Presentation, Business, Data layers
- **Microservices**: Service-oriented architecture
- **Monolithic**: Single application structure
- **Feature-based**: Feature-driven organization

## 🎯 Key Capabilities

### 1. Intelligent Classification
```python
# Detects repository type with confidence scoring
repo_type = analyzer.detector.detect_repo_type("/path/to/repo")
print(f"Type: {repo_type['type']}")
print(f"Confidence: {repo_type['confidence']:.2f}")
print(f"Evidence: {repo_type['evidence']}")
```

### 2. Dependency Intelligence
```python
# Parses all dependency files and infers features
deps = analyzer.dependency_parser.parse_dependencies("/path/to/repo")
print(f"Features: {deps['features']}")
print(f"Tech Stack: {deps['stack']}")
print(f"External Services: {deps['external_services']}")
```

### 3. Structure Understanding
```python
# Maps folder structure to understand organization
structure = analyzer.structure_mapper.map_project_structure("/path/to/repo")
print(f"Architecture: {structure['structure_analysis']['architecture_pattern']}")
print(f"File Categories: {structure['file_categories']}")
```

### 4. Signal Ranking
```python
# Identifies the most important files
signal = analyzer.signal_ranker.score_files_by_signal("/path/to/repo")
print(f"High-signal files: {signal['high_signal_files']}")
```

### 5. Feature Inference
```python
# Infers application features from code patterns
features = analyzer.feature_inferer.infer_features_and_user_flow("/path/to/repo", structure, deps)
print(f"Inferred features: {features['inferred_features']}")
```

### 6. Narrative Generation
```python
# Generates human-readable documentation
narrative = analyzer.narrative_writer.compose_readme_narrative("/path/to/repo", analysis_data)
print(f"README content: {narrative['readme_content']}")
```

## 📈 Analysis Output

The analyzer provides comprehensive output including:

### Summary Metrics
- Project type and confidence
- Feature count and types
- Technology stack breakdown
- Architecture pattern detection
- Complexity scoring
- File importance ranking

### Detailed Insights
- Key findings and evidence
- Architecture recommendations
- Feature relationship mapping
- User flow reconstruction
- External service integration

### Generated Documentation
- Complete README generation
- Project structure documentation
- API reference templates
- Getting started guides
- Deployment instructions

## 🔧 Configuration

### Customizing Detection Patterns

You can extend the detection patterns by modifying the pattern dictionaries in each component:

```python
# Add custom repo type detection
RepoTypeDetector.TYPE_INDICATORS['custom_type'] = {
    'files': ['custom.config', 'special.file'],
    'keywords': ['custom', 'special']
}

# Add custom feature detection
FeatureInferer.FEATURE_PATTERNS['custom_feature'] = {
    'files': ['custom', 'special'],
    'routes': ['/custom', '/special'],
    'components': ['CustomComponent'],
    'services': ['CustomService'],
    'keywords': ['custom', 'special']
}
```

### Adjusting Signal Weights

```python
# Modify file importance weights
SignalRanker.FILE_WEIGHTS['custom_type'] = 9.0

# Adjust directory multipliers
SignalRanker.DIRECTORY_MULTIPLIERS['custom/'] = 1.5

# Add custom keywords
SignalRanker.HIGH_SIGNAL_KEYWORDS['custom'] = 2.0
```

## 🧪 Testing

Run the test script to see the analyzer in action:

```bash
cd backend
python test_repo_analyzer.py
```

This will:
1. Analyze the current DocuMint project
2. Display comprehensive results
3. Export analysis in multiple formats
4. Show generated README preview

## 📊 Performance

The analyzer is designed for efficiency:
- **Fast**: Analyzes repositories in seconds, not minutes
- **Scalable**: Handles projects of any size
- **Accurate**: High-confidence detection with evidence
- **Comprehensive**: Covers all major project types and patterns

## 🔮 Future Enhancements

### Planned Features
- **Language-specific analysis**: Deep understanding of Python, JavaScript, Go, Rust
- **Security analysis**: Vulnerability detection and security recommendations
- **Performance analysis**: Code quality and performance insights
- **Team collaboration**: Multi-developer project analysis
- **CI/CD integration**: Automated analysis in build pipelines

### Extensibility
- **Plugin system**: Custom analyzers for specific domains
- **API integration**: REST API for remote analysis
- **Real-time analysis**: Live repository monitoring
- **Comparative analysis**: Compare multiple repositories

## 🤝 Contributing

The repo analyzer is designed to be extensible. To add new capabilities:

1. **New Repository Types**: Extend `RepoTypeDetector.TYPE_INDICATORS`
2. **New Features**: Add patterns to `FeatureInferer.FEATURE_PATTERNS`
3. **New File Types**: Extend `SignalRanker.EXTENSION_WEIGHTS`
4. **New Templates**: Add to `NarrativeWriter.README_TEMPLATES`

## 📚 API Reference

### RepoAnalyzer

Main orchestrator class that runs the complete analysis pipeline.

#### Methods
- `analyze_repository(repo_path, include_narrative=True)`: Run complete analysis
- `analyze_phase(repo_path, phase)`: Run specific analysis phase
- `get_analysis_insights()`: Get insights and recommendations
- `export_results(output_path, format)`: Export results to file

### Individual Components

Each phase can be used independently:

- **RepoTypeDetector**: Repository classification
- **DependencyParser**: Dependency and stack analysis
- **StructureMapper**: Project structure mapping
- **SignalRanker**: File importance ranking
- **FeatureInferer**: Feature and user flow inference
- **NarrativeWriter**: Documentation generation

## 🎉 What You've Built

You now have a **self-aware, auto-contextualizing project analyst** that can:

- **Automatically understand any repository** in seconds
- **Generate comprehensive documentation** without manual input
- **Provide architectural insights** and recommendations
- **Detect features and user flows** from code patterns
- **Export results in multiple formats** for different use cases

This transforms your README generator from a simple template system into an **oracle-level repository understanding engine** that rivals the best AI-powered development tools.

---

*Built with ❤️ for the DocuMint project* 