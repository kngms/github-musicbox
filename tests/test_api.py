"""Tests for the Music Track Generator API."""

import os
import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["MUSIC_GEN_MODE"] = "simulate"

from music_generator.api import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Music Track Generator API"
    assert data["mode"] == "simulate"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_generate_track_invalid_duration():
    """Test track generation with invalid duration (should return 422)."""
    response = client.post("/tracks/generate", json={
        "text_input": "Test lyrics",
        "genre": "rock",
        "duration_seconds": 30,  # Too short
        "structure": {
            "intro": True,
            "verse_count": 2,
            "chorus_count": 2,
            "bridge": True,
            "outro": True
        }
    })
    assert response.status_code == 422


def test_generate_track_happy_path():
    """Test successful track generation."""
    response = client.post("/tracks/generate", json={
        "text_input": "We are the champions",
        "genre": "rock",
        "duration_seconds": 180,
        "structure": {
            "intro": True,
            "verse_count": 2,
            "chorus_count": 3,
            "bridge": True,
            "outro": True
        },
        "temperature": 0.8
    })
    assert response.status_code == 200
    data = response.json()
    
    # Check required keys
    assert "status" in data
    assert "mode" in data
    assert "genre" in data
    assert "duration_seconds" in data
    assert "prompt" in data
    assert "message" in data
    
    # Check values
    assert data["status"] == "simulated"
    assert data["mode"] == "simulate"
    assert data["genre"] == "rock"
    assert data["duration_seconds"] == 180


def test_generate_track_with_preset():
    """Test track generation using a preset."""
    response = client.post("/tracks/generate", json={
        "text_input": "We are the champions",
        "genre": "rock",
        "duration_seconds": 180,
        "preset_name": "rock_anthem"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["genre"] == "rock"
    assert data["status"] == "simulated"


def test_generate_track_with_invalid_preset():
    """Test track generation with non-existent preset (should return 404)."""
    response = client.post("/tracks/generate", json={
        "text_input": "Test lyrics",
        "genre": "rock",
        "duration_seconds": 180,
        "preset_name": "nonexistent_preset"
    })
    assert response.status_code == 404


def test_list_presets():
    """Test listing presets."""
    response = client.get("/presets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check first preset has required fields
    preset = data[0]
    assert "name" in preset
    assert "genre" in preset
    assert "description" in preset


def test_get_preset():
    """Test getting a specific preset."""
    response = client.get("/presets/rock_anthem")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "rock_anthem"
    assert data["genre"] == "rock"
    assert "structure" in data
    assert "style_references" in data


def test_get_nonexistent_preset():
    """Test getting a non-existent preset (should return 404)."""
    response = client.get("/presets/nonexistent_preset")
    assert response.status_code == 404


def test_preset_crud_flow():
    """Test complete preset CRUD flow: create, list, get, delete."""
    # Create a new preset
    preset_data = {
        "name": "test_preset_api",
        "description": "Test preset for API",
        "genre": "test",
        "structure": {
            "intro": True,
            "verse_count": 2,
            "chorus_count": 2,
            "bridge": True,
            "outro": True
        },
        "style_references": [],
        "temperature": 0.7
    }
    
    response = client.post("/presets", json=preset_data)
    assert response.status_code == 200
    
    # List presets and verify it's in the list
    response = client.get("/presets")
    assert response.status_code == 200
    preset_names = [p["name"] for p in response.json()]
    assert "test_preset_api" in preset_names
    
    # Get the specific preset
    response = client.get("/presets/test_preset_api")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_preset_api"
    assert data["genre"] == "test"
    
    # Delete the preset
    response = client.delete("/presets/test_preset_api")
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get("/presets/test_preset_api")
    assert response.status_code == 404


def test_prompt_tips():
    """Test getting prompt tips."""
    response = client.get("/prompt-tips")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Check structure of tips
    if len(data) > 0:
        tip = data[0]
        assert "preset_name" in tip
        assert "genre" in tip
        assert "tips" in tip


def test_prompt_tips_filtered():
    """Test getting prompt tips for a specific preset."""
    response = client.get("/prompt-tips?preset_name=rock_anthem")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["preset_name"] == "rock_anthem"


def test_api_key_authentication():
    """Test API key authentication when configured."""
    # Save current env
    old_api_key = os.environ.get("MUSIC_GEN_API_KEY")
    
    try:
        # Set API key
        os.environ["MUSIC_GEN_API_KEY"] = "test_secret_key"
        
        # Reimport to pick up new env var
        from importlib import reload
        import music_generator.api as api_module
        reload(api_module)
        test_client = TestClient(api_module.app)
        
        # Request without API key should fail
        response = test_client.get("/presets")
        assert response.status_code == 401
        
        # Request with correct API key in X-API-Key header
        response = test_client.get("/presets", headers={"X-API-Key": "test_secret_key"})
        assert response.status_code == 200
        
        # Request with correct API key in Authorization header
        response = test_client.get("/presets", headers={"Authorization": "Bearer test_secret_key"})
        assert response.status_code == 200
        
        # Request with wrong API key
        response = test_client.get("/presets", headers={"X-API-Key": "wrong_key"})
        assert response.status_code == 401
    
    finally:
        # Restore env
        if old_api_key:
            os.environ["MUSIC_GEN_API_KEY"] = old_api_key
        else:
            os.environ.pop("MUSIC_GEN_API_KEY", None)
