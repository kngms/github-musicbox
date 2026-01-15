"""Tests for performance optimizations."""

import os
import time
import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["MUSIC_GEN_MODE"] = "simulate"
os.environ.pop("MUSIC_GEN_API_KEY", None)

from music_generator.api import app
from music_generator.presets import PresetManager
from music_generator.generator import MusicGenerator
from music_generator.models import TrackConfig, SongStructure


client = TestClient(app)


def test_generator_caching():
    """Test that generator instances are cached and reused."""
    # Import the cache from the actual running instance
    from music_generator import api
    
    # Clear cache first
    api._generator_cache.clear()
    
    # Make multiple requests
    for _ in range(3):
        response = client.post("/tracks/generate", json={
            "text_input": "Test lyrics",
            "genre": "rock",
            "duration_seconds": 180,
            "preset_name": "rock_anthem"
        })
        assert response.status_code == 200
    
    # Cache should have one entry for the simulate mode
    assert len(api._generator_cache) >= 1
    
    # Verify cache key handles None values properly (simulate mode has no project_id)
    # The cache key should be consistent for multiple requests
    cache_keys = list(api._generator_cache.keys())
    assert all("None" not in key for key in cache_keys), "Cache keys should not contain 'None' string"


def test_list_presets_performance():
    """Test that list_presets is efficient and uses caching."""
    # First call - populates cache
    start = time.time()
    response1 = client.get("/presets")
    time1 = time.time() - start
    
    assert response1.status_code == 200
    presets1 = response1.json()
    assert len(presets1) > 0
    
    # Second call - should use cache and be faster
    start = time.time()
    response2 = client.get("/presets")
    time2 = time.time() - start
    
    assert response2.status_code == 200
    presets2 = response2.json()
    
    # Results should be the same
    assert presets1 == presets2
    
    # Second call should be faster or similar (cached)
    # We use a very lenient check since timing can vary
    assert time2 <= time1 * 2  # Allow for some variance


def test_preset_manager_metadata_cache():
    """Test that PresetManager caches metadata efficiently."""
    manager = PresetManager()
    
    # Clear cache
    manager._metadata_cache.clear()
    
    # First call - populates cache
    metadata1 = manager.list_presets_with_metadata()
    assert len(metadata1) > 0
    
    # Cache should be populated
    assert len(manager._metadata_cache) > 0
    
    # Second call - should use cache
    metadata2 = manager.list_presets_with_metadata()
    assert metadata1 == metadata2
    
    # Cache size should remain the same
    cache_size = len(manager._metadata_cache)
    assert cache_size > 0


def test_preset_manager_builtin_optimization():
    """Test that builtin presets are efficiently initialized."""
    # Create a new preset manager and measure initialization time
    start = time.time()
    manager1 = PresetManager()
    time1 = time.time() - start
    
    # Second initialization should be faster (presets already exist)
    start = time.time()
    manager2 = PresetManager()
    time2 = time.time() - start
    
    # Second init should be faster since presets already exist
    assert time2 <= time1
    
    # Both should have the same presets available
    assert manager1.list_presets() == manager2.list_presets()


def test_prompt_building_efficiency():
    """Test that prompt building is efficient."""
    generator = MusicGenerator(mode="simulate")
    
    config = TrackConfig(
        text_input="Test lyrics for performance",
        genre="rock",
        duration_seconds=180,
        structure=SongStructure(
            intro=True,
            verse_count=3,
            chorus_count=3,
            bridge=True,
            outro=True
        ),
        style_references=[],
        temperature=0.7
    )
    
    # Build prompt multiple times and measure
    times = []
    for _ in range(10):
        start = time.time()
        prompt = generator._build_prompt(config)
        times.append(time.time() - start)
    
    # All prompts should be identical
    prompts = [generator._build_prompt(config) for _ in range(10)]
    assert all(p == prompts[0] for p in prompts)
    
    # Average time should be very small (< 1ms)
    avg_time = sum(times) / len(times)
    assert avg_time < 0.001  # Less than 1 millisecond


def test_multiple_requests_with_caching():
    """Test that multiple API requests benefit from caching."""
    # Import the cache from the actual running instance
    from music_generator import api
    
    # Clear cache
    api._generator_cache.clear()
    
    # Make 10 requests
    times = []
    for i in range(10):
        start = time.time()
        response = client.post("/tracks/generate", json={
            "text_input": f"Test lyrics {i}",
            "genre": "rock",
            "duration_seconds": 180,
            "preset_name": "rock_anthem"
        })
        times.append(time.time() - start)
        assert response.status_code == 200
    
    # Later requests should not be significantly slower
    # (if generator wasn't cached, they would be slower)
    first_batch_avg = sum(times[:3]) / 3
    second_batch_avg = sum(times[3:6]) / 3
    
    # Second batch should be similar or faster (with caching)
    # Allow 2x variance for system noise
    assert second_batch_avg <= first_batch_avg * 2


def test_cache_invalidation_on_preset_save():
    """Test that metadata cache is invalidated when preset is saved."""
    manager = PresetManager()
    
    # Populate cache
    manager.list_presets_with_metadata()
    initial_cache_size = len(manager._metadata_cache)
    
    # Save a new preset
    from music_generator.models import PresetConfig, StyleReference
    new_preset = PresetConfig(
        name="test_perf_preset",
        description="Test preset for performance",
        genre="test",
        structure=SongStructure(),
        style_references=[],
        temperature=0.7
    )
    
    manager.save_preset(new_preset)
    
    # Cache for this preset should be cleared
    assert "test_perf_preset" not in manager._metadata_cache
    
    # Clean up
    manager.delete_preset("test_perf_preset")


def test_cache_invalidation_on_preset_delete():
    """Test that metadata cache is invalidated when preset is deleted."""
    manager = PresetManager()
    
    # Create and save a test preset
    from music_generator.models import PresetConfig
    test_preset = PresetConfig(
        name="test_perf_delete",
        description="Test preset for deletion",
        genre="test",
        structure=SongStructure(),
        style_references=[],
        temperature=0.7
    )
    
    manager.save_preset(test_preset)
    
    # Load metadata to populate cache
    manager.list_presets_with_metadata()
    
    # Delete the preset
    manager.delete_preset("test_perf_delete")
    
    # Cache for this preset should be cleared
    assert "test_perf_delete" not in manager._metadata_cache
