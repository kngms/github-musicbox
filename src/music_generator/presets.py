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
        
        # Load built-in presets
        self._ensure_builtin_presets()
    
    def _ensure_builtin_presets(self):
        """Create built-in presets if they don't exist."""
        builtin_presets = self._get_builtin_presets()
        
        for preset in builtin_presets:
            preset_path = self.presets_dir / f"{preset.name}.yaml"
            if not preset_path.exists():
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
        return True
