"""Tests for the Music Track Generator API."""

import os
import pytest
from fastapi.testclient import TestClient

# Set test environment and clear any leftover API key
os.environ["MUSIC_GEN_MODE"] = "simulate"
os.environ.pop("MUSIC_GEN_API_KEY", None)

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
        
        # Reload module again to restore original state
        from importlib import reload
        import music_generator.api as api_module
        reload(api_module)


def test_get_config():
    """Test getting configuration information."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "mode" in data
    assert "region" in data
    assert "project" in data
    assert "presets_available" in data
    assert "auth_enabled" in data
    
    # Check values for simulate mode
    assert data["mode"] == "simulate"
    assert data["region"] is None  # Not set in simulate mode
    assert data["project"] is None  # Not set in simulate mode
    assert isinstance(data["presets_available"], list)
    assert len(data["presets_available"]) > 0
    assert data["auth_enabled"] is False


def test_get_config_gcp_mode():
    """Test configuration endpoint in GCP mode."""
    # Save current env
    old_mode = os.environ.get("MUSIC_GEN_MODE")
    old_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    old_region = os.environ.get("GOOGLE_CLOUD_REGION")
    
    try:
        # Set GCP mode environment
        os.environ["MUSIC_GEN_MODE"] = "gcp"
        os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project-123"
        os.environ["GOOGLE_CLOUD_REGION"] = "us-west1"
        
        # Reimport to pick up new env vars
        from importlib import reload
        import music_generator.api as api_module
        reload(api_module)
        test_client = TestClient(api_module.app)
        
        response = test_client.get("/config")
        assert response.status_code == 200
        data = response.json()
        
        # Check GCP-specific values
        assert data["mode"] == "gcp"
        assert data["project"] == "test-project-123"
        assert data["region"] == "us-west1"
        assert isinstance(data["presets_available"], list)
        
    finally:
        # Restore env
        if old_mode:
            os.environ["MUSIC_GEN_MODE"] = old_mode
        else:
            os.environ.pop("MUSIC_GEN_MODE", None)
        if old_project:
            os.environ["GOOGLE_CLOUD_PROJECT"] = old_project
        else:
            os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
        if old_region:
            os.environ["GOOGLE_CLOUD_REGION"] = old_region
        else:
            os.environ.pop("GOOGLE_CLOUD_REGION", None)
        
        # Reload module again to restore original state
        from importlib import reload
        import music_generator.api as api_module
        reload(api_module)


def test_validation_error_structure():
    """Test that validation errors return structured responses with field names."""
    # Test with invalid duration (too short)
    response = client.post("/tracks/generate", json={
        "text_input": "Test lyrics",
        "genre": "rock",
        "duration_seconds": 30,  # Too short, must be >= 60
        "structure": {
            "intro": True,
            "verse_count": 2,
            "chorus_count": 2,
            "bridge": True,
            "outro": True
        }
    })
    
    assert response.status_code == 422
    data = response.json()
    
    # Check structured error response
    assert "detail" in data
    assert "errors" in data
    assert isinstance(data["errors"], list)
    assert len(data["errors"]) > 0
    
    # Check error structure
    error = data["errors"][0]
    assert "field" in error
    assert "message" in error
    assert "type" in error
    
    # Check that the field is identified correctly
    assert "duration_seconds" in error["field"]


def test_validation_error_missing_fields():
    """Test validation errors for missing required fields."""
    # Test with missing required fields
    response = client.post("/tracks/generate", json={
        "genre": "rock",
        # Missing text_input
        "duration_seconds": 180
    })
    
    assert response.status_code == 422
    data = response.json()
    
    # Check structured error response
    assert "detail" in data
    assert "errors" in data
    assert isinstance(data["errors"], list)
    assert len(data["errors"]) > 0
    
    # Check that text_input field is mentioned
    field_names = [err["field"] for err in data["errors"]]
    assert any("text_input" in field for field in field_names)
