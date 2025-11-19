"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_brief():
    """Sample video brief for testing"""
    return {
        "title": "Test Video",
        "description": "Propaganda de cafeteria moderna",
        "target": "Jovens adultos 25-35",
        "style": "moderno e clean",
        "duration": 30,
        "cta": "Visite nossa loja!"
    }


@pytest.fixture
def sample_analysis():
    """Sample analysis for testing"""
    return {
        "objective": "Atrair clientes para cafeteria",
        "target_audience": "Millennials urbanos",
        "style": "moderno",
        "duration_seconds": 30,
        "visual_requirements": ["cafe", "pessoas felizes"],
        "audio_requirements": ["narração", "música upbeat"],
        "cta": "Visite nossa loja!"
    }


@pytest.fixture
def sample_script():
    """Sample script for testing"""
    return {
        "script_id": "test_001",
        "title": "Cafeteria Moderna",
        "duration_seconds": 30,
        "scenes": [
            {
                "scene_number": 1,
                "duration": 10,
                "visual_description": "Abertura cafeteria",
                "narration": "Descubra o melhor café da cidade",
                "on_screen_text": "Cafeteria Premium",
                "keywords": ["cafe", "modern", "cozy"],
                "mood": "acolhedor"
            },
            {
                "scene_number": 2,
                "duration": 15,
                "visual_description": "Pessoas tomando café",
                "narration": "Ambiente perfeito para trabalhar e relaxar",
                "on_screen_text": "",
                "keywords": ["people", "coffee", "laptop"],
                "mood": "produtivo"
            },
            {
                "scene_number": 3,
                "duration": 5,
                "visual_description": "Logo e endereço",
                "narration": "Visite nossa loja!",
                "on_screen_text": "Visite-nos hoje!",
                "keywords": ["cta", "location"],
                "mood": "convidativo"
            }
        ]
    }


@pytest.fixture
def sample_state(sample_brief, sample_analysis):
    """Sample VideoState for testing"""
    return {
        "brief": sample_brief,
        "analysis": sample_analysis,
        "current_phase": 0,
        "script": None,
        "visual_plan": None,
        "audio_files": None,
        "video_path": None
    }
