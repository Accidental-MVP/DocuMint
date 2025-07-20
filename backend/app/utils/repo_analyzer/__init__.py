"""
Repo Analyzer Module - Oracle-level repository understanding engine

This module implements a six-phase analysis loop to understand any repository:
1. Classification - Detect repo type (web, mobile, backend, etc.)
2. Dependency Mapping - Parse dependencies to infer stack and features
3. Structure Mapping - Build internal map of folder → feature relationships
4. Signal Extraction - Identify high-signal files (routes, models, services)
5. Flow + Feature Inference - Link components to reconstruct UX and logic
6. Narrative Synthesis - Convert insights into human-level summaries
"""

from .detector import RepoTypeDetector
from .dependency_parser import DependencyParser
from .structure_mapper import StructureMapper
from .signal_ranker import SignalRanker
from .feature_inferer import FeatureInferer
from .narrative_writer import NarrativeWriter
from .analyzer import RepoAnalyzer

__all__ = [
    'RepoAnalyzer',
    'RepoTypeDetector', 
    'DependencyParser',
    'StructureMapper',
    'SignalRanker',
    'FeatureInferer',
    'NarrativeWriter'
] 