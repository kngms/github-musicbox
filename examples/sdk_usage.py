"""
Example: Using the Python SDK to generate tracks
"""

from music_generator.models import TrackConfig, SongStructure, StyleReference
from music_generator.generator import MusicGenerator
from music_generator.presets import PresetManager


def example_with_preset():
    """Generate a track using a preset."""
    
    # Initialize preset manager
    preset_manager = PresetManager()
    
    # Load a preset
    preset = preset_manager.load_preset("rock_anthem")
    
    # Create track configuration from preset
    config = preset.to_track_config(
        text_input="We are the champions, rising from the ground",
        duration_seconds=180
    )
    
    # Generate track
    generator = MusicGenerator(project_id="your-project-id")
    result = generator.generate_track(config, output_path="rock_track.mp3")
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")


def example_custom_track():
    """Generate a track with custom configuration."""
    
    # Define song structure
    structure = SongStructure(
        intro=True,
        verse_count=3,
        chorus_count=3,
        bridge=True,
        outro=True
    )
    
    # Define style references
    style_refs = [
        StyleReference(type="style", value="indie folk"),
        StyleReference(type="sound", value="acoustic guitar with soft vocals"),
        StyleReference(type="similar_to", value="Bon Iver")
    ]
    
    # Create track configuration
    config = TrackConfig(
        text_input="Walking through the forest, sunlight through the trees...",
        genre="folk",
        duration_seconds=240,
        structure=structure,
        style_references=style_refs,
        temperature=0.6
    )
    
    # Generate track
    generator = MusicGenerator(project_id="your-project-id")
    result = generator.generate_track(config, output_path="folk_track.mp3")
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")


def example_save_preset():
    """Save a custom preset."""
    
    from music_generator.models import PresetConfig
    
    # Create custom preset
    preset = PresetConfig(
        name="indie_folk",
        description="Indie folk with acoustic sound",
        genre="folk",
        structure=SongStructure(
            intro=True,
            verse_count=3,
            chorus_count=2,
            bridge=True,
            outro=True
        ),
        style_references=[
            StyleReference(type="style", value="indie folk"),
            StyleReference(type="sound", value="acoustic instruments")
        ],
        temperature=0.6,
        tips="Use introspective, nature-themed lyrics. Keep it intimate and authentic."
    )
    
    # Save preset
    preset_manager = PresetManager()
    preset_path = preset_manager.save_preset(preset)
    
    print(f"Preset saved to: {preset_path}")


if __name__ == "__main__":
    print("Example 1: Using a preset")
    print("-" * 50)
    example_with_preset()
    
    print("\n\nExample 2: Custom track configuration")
    print("-" * 50)
    example_custom_track()
    
    print("\n\nExample 3: Saving a custom preset")
    print("-" * 50)
    example_save_preset()
