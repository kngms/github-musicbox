"""Configuration models for music track generation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SongStructure(BaseModel):
    """Defines the structure of a song."""
    
    intro: bool = Field(default=True, description="Include an intro section")
    verse_count: int = Field(default=2, ge=1, le=5, description="Number of verses")
    chorus_count: int = Field(default=2, ge=1, le=4, description="Number of choruses")
    bridge: bool = Field(default=True, description="Include a bridge section")
    outro: bool = Field(default=True, description="Include an outro section")
    
    @field_validator('verse_count', 'chorus_count')
    @classmethod
    def validate_counts(cls, v):
        if v < 1:
            raise ValueError("Count must be at least 1")
        return v


class StyleReference(BaseModel):
    """Style or sound reference for the track."""
    
    type: str = Field(..., description="Type of reference: 'style', 'sound', 'artist', 'similar_to'")
    value: str = Field(..., description="Reference value (e.g., artist name, song name, style description)")


class TrackConfig(BaseModel):
    """Configuration for generating a music track."""
    
    text_input: str = Field(..., description="Lyrics or text description for the track")
    genre: str = Field(..., description="Music genre (e.g., rock, jazz, electronic, classical)")
    duration_seconds: int = Field(default=180, ge=60, le=240, description="Track duration in seconds (1-4 minutes)")
    structure: SongStructure = Field(default_factory=SongStructure)
    style_references: List[StyleReference] = Field(default_factory=list, description="Style and sound references")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Creativity level (0=conservative, 1=very creative)")


class PresetConfig(BaseModel):
    """Saved preset configuration."""
    
    name: str = Field(..., description="Preset name")
    description: Optional[str] = Field(None, description="Preset description")
    genre: str = Field(..., description="Default genre")
    structure: SongStructure = Field(default_factory=SongStructure)
    style_references: List[StyleReference] = Field(default_factory=list)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    tips: Optional[str] = Field(None, description="Tips for using this preset")
    
    def to_track_config(self, text_input: str, duration_seconds: int = 180) -> TrackConfig:
        """Convert preset to a track configuration."""
        return TrackConfig(
            text_input=text_input,
            genre=self.genre,
            duration_seconds=duration_seconds,
            structure=self.structure,
            style_references=self.style_references,
            temperature=self.temperature
        )
