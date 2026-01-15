"""Preset management for music track generation."""

import os
import yaml
from pathlib import Path
from typing import List, Optional
from .models import PresetConfig


class PresetManager:
    """Manages presets for music track generation."""
    
    def __init__(self, presets_dir: Optional[str] = None):
        """Initialize the preset manager.
        
        Args:
            presets_dir: Directory to store presets. Defaults to './presets'
        """
        if presets_dir is None:
            presets_dir = os.path.join(os.getcwd(), "presets")
        
        self.presets_dir = Path(presets_dir)
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for preset metadata to avoid repeated file I/O
        self._metadata_cache: dict[str, dict] = {}
        
        # Load built-in presets (lazy initialization)
        self._ensure_builtin_presets()
    
    def _ensure_builtin_presets(self):
        """Create built-in presets if they don't exist (optimized to check only once per preset)."""
        # Batch check: load all existing preset names at once (efficient for typical preset counts < 100)
        existing_presets = set(p.stem for p in self.presets_dir.glob("*.yaml"))
        builtin_presets = self._get_builtin_presets()
        
        # Only save presets that don't exist yet
        for preset in builtin_presets:
            if preset.name not in existing_presets:
                self.save_preset(preset)
    
    def _get_builtin_presets(self) -> List[PresetConfig]:
        """Get built-in preset configurations."""
        from .models import SongStructure, StyleReference
        
        return [
            PresetConfig(
                name="rock_anthem",
                description="High-energy rock anthem with powerful vocals",
                genre="rock",
                structure=SongStructure(
                    intro=True,
                    verse_count=2,
                    chorus_count=3,
                    bridge=True,
                    outro=True
                ),
                style_references=[
                    StyleReference(type="style", value="arena rock"),
                    StyleReference(type="sound", value="distorted electric guitars with powerful drums")
                ],
                temperature=0.8,
                tips="Use energetic and empowering lyrics. Great for anthems and motivational songs."
            ),
            PresetConfig(
                name="jazz_smooth",
                description="Smooth jazz with relaxed tempo",
                genre="jazz",
                structure=SongStructure(
                    intro=True,
                    verse_count=2,
                    chorus_count=2,
                    bridge=True,
                    outro=True
                ),
                style_references=[
                    StyleReference(type="style", value="smooth jazz"),
                    StyleReference(type="sound", value="saxophone and piano with brushed drums")
                ],
                temperature=0.6,
                tips="Focus on sophisticated, laid-back lyrics. Perfect for evening moods."
            ),
            PresetConfig(
                name="electronic_dance",
                description="Upbeat electronic dance music",
                genre="electronic",
                structure=SongStructure(
                    intro=True,
                    verse_count=2,
                    chorus_count=3,
                    bridge=True,
                    outro=True
                ),
                style_references=[
                    StyleReference(type="style", value="EDM"),
                    StyleReference(type="sound", value="synthesizers with heavy bass and electronic beats")
                ],
                temperature=0.9,
                tips="Keep lyrics simple and repetitive. Build energy through structure."
            ),
            PresetConfig(
                name="classical_orchestral",
                description="Classical orchestral composition",
                genre="classical",
                structure=SongStructure(
                    intro=True,
                    verse_count=3,
                    chorus_count=2,
                    bridge=True,
                    outro=True
                ),
                style_references=[
                    StyleReference(type="style", value="romantic era classical"),
                    StyleReference(type="sound", value="full orchestra with strings and brass")
                ],
                temperature=0.5,
                tips="Use poetic and dramatic text. Focus on emotional depth and dynamics."
            ),
            PresetConfig(
                name="pop_catchy",
                description="Catchy pop song with radio-friendly structure",
                genre="pop",
                structure=SongStructure(
                    intro=True,
                    verse_count=2,
                    chorus_count=3,
                    bridge=True,
                    outro=False
                ),
                style_references=[
                    StyleReference(type="style", value="contemporary pop"),
                    StyleReference(type="sound", value="bright synths with acoustic elements")
                ],
                temperature=0.7,
                tips="Focus on memorable hooks and relatable themes. Keep it upbeat and accessible."
            )
        ]
    
    def save_preset(self, preset: PresetConfig) -> Path:
        """Save a preset to disk.
        
        Args:
            preset: Preset configuration to save
            
        Returns:
            Path to the saved preset file
        """
        preset_path = self.presets_dir / f"{preset.name}.yaml"
        
        with open(preset_path, 'w') as f:
            yaml.dump(preset.model_dump(), f, default_flow_style=False, sort_keys=False)
        
        # Invalidate cache for this preset
        self._metadata_cache.pop(preset.name, None)
        
        return preset_path
    
    def load_preset(self, name: str) -> Optional[PresetConfig]:
        """Load a preset from disk.
        
        Args:
            name: Name of the preset to load
            
        Returns:
            Loaded preset configuration or None if not found
        """
        preset_path = self.presets_dir / f"{name}.yaml"
        
        if not preset_path.exists():
            return None
        
        try:
            with open(preset_path, 'r') as f:
                data = yaml.safe_load(f)
            
            return PresetConfig(**data)
        except (IOError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to load preset '{name}': {str(e)}")
    
    def list_presets(self) -> List[str]:
        """List all available presets.
        
        Returns:
            List of preset names
        """
        presets = []
        for preset_file in self.presets_dir.glob("*.yaml"):
            presets.append(preset_file.stem)
        return sorted(presets)
    
    def list_presets_with_metadata(self) -> List[dict]:
        """List all available presets with metadata (optimized for API).
        
        Returns:
            List of preset metadata dictionaries with name, genre, and description
        """
        presets = []
        for name in self.list_presets():
            # Check cache first
            if name in self._metadata_cache:
                presets.append(self._metadata_cache[name])
            else:
                # Load only metadata fields from file
                preset = self.load_preset(name)
                if preset:
                    metadata = {
                        "name": preset.name,
                        "genre": preset.genre,
                        "description": preset.description
                    }
                    self._metadata_cache[name] = metadata
                    presets.append(metadata)
        return presets
    
    def delete_preset(self, name: str) -> bool:
        """Delete a preset.
        
        Args:
            name: Name of the preset to delete
            
        Returns:
            True if deleted, False if preset not found
        """
        preset_path = self.presets_dir / f"{name}.yaml"
        
        if not preset_path.exists():
            return False
        
        preset_path.unlink()
        # Invalidate cache for this preset
        self._metadata_cache.pop(name, None)
        return True
