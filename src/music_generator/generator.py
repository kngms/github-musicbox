"""GCP integration for music track generation using Vertex AI."""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
import logging

try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

from .models import TrackConfig

logger = logging.getLogger(__name__)


class MusicGenerator:
    """Music track generator using Google Cloud Platform Vertex AI."""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        credentials_path: Optional[str] = None
    ):
        """Initialize the music generator.
        
        Args:
            project_id: GCP project ID. If None, uses GOOGLE_CLOUD_PROJECT env var
            location: GCP region for Vertex AI
            credentials_path: Path to service account JSON. If None, uses GOOGLE_APPLICATION_CREDENTIALS env var
        """
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError(
                "Google Cloud libraries not installed. "
                "Install with: pip install google-cloud-aiplatform google-auth"
            )
        
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        
        if not self.project_id:
            raise ValueError(
                "GCP project ID not provided. Set GOOGLE_CLOUD_PROJECT environment variable "
                "or pass project_id parameter"
            )
        
        # Initialize credentials
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
        else:
            credentials = None  # Will use default credentials
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.project_id,
            location=self.location,
            credentials=credentials
        )
        
        logger.info(f"Initialized MusicGenerator for project {self.project_id} in {self.location}")
    
    def _build_prompt(self, config: TrackConfig) -> str:
        """Build a prompt for the AI model based on track configuration.
        
        Args:
            config: Track configuration
            
        Returns:
            Formatted prompt string
        """
        # Build structure description with proper verse/chorus interleaving
        structure_parts = []
        if config.structure.intro:
            structure_parts.append("intro")
        
        # Interleave verses and choruses
        verse_count = config.structure.verse_count
        chorus_count = config.structure.chorus_count
        
        for i in range(max(verse_count, chorus_count)):
            if i < verse_count:
                structure_parts.append(f"verse {i+1}")
            if i < chorus_count:
                structure_parts.append("chorus")
        
        if config.structure.bridge:
            structure_parts.append("bridge")
        if config.structure.outro:
            structure_parts.append("outro")
        
        structure_str = " -> ".join(structure_parts)
        
        # Build style references
        style_str = ""
        if config.style_references:
            refs = []
            for ref in config.style_references:
                refs.append(f"{ref.type}: {ref.value}")
            style_str = "\nStyle references:\n" + "\n".join(f"- {r}" for r in refs)
        
        prompt = f"""Generate a {config.genre} music track with the following specifications:

Duration: {config.duration_seconds} seconds ({config.duration_seconds // 60} minutes {config.duration_seconds % 60} seconds)

Song structure: {structure_str}

Lyrics/Text input:
{config.text_input}
{style_str}

Create a track that follows this structure and incorporates the provided text and style references.
Temperature: {config.temperature}
"""
        return prompt
    
    def generate_track(
        self,
        config: TrackConfig,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a music track based on configuration.
        
        Args:
            config: Track configuration
            output_path: Optional path to save the generated track
            
        Returns:
            Dictionary with generation results including metadata and file path
        """
        prompt = self._build_prompt(config)
        
        logger.info(f"Generating {config.genre} track ({config.duration_seconds}s)")
        logger.debug(f"Prompt:\n{prompt}")
        
        # For now, we'll create a simulation response since actual music generation
        # requires specific models and APIs that may not be available
        # In production, this would use Vertex AI's music generation endpoints
        
        result = {
            "status": "simulated",
            "genre": config.genre,
            "duration_seconds": config.duration_seconds,
            "prompt": prompt,
            "metadata": {
                "structure": config.structure.model_dump(),
                "style_references": [ref.model_dump() for ref in config.style_references],
                "temperature": config.temperature
            },
            "message": (
                "Track generation simulated. In production, this would call "
                "Google Cloud Vertex AI music generation API with the generated prompt."
            )
        }
        
        # Save metadata if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            metadata_path = output_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            result["metadata_path"] = str(metadata_path)
            logger.info(f"Saved metadata to {metadata_path}")
        
        return result
    
    def estimate_cost(self, config: TrackConfig) -> Dict[str, float]:
        """Estimate the cost of generating a track.
        
        Args:
            config: Track configuration
            
        Returns:
            Dictionary with cost estimates
        """
        # These are example costs - actual costs depend on GCP pricing
        base_cost = 0.01  # Base cost per track
        duration_cost = config.duration_seconds * 0.0001  # Cost per second
        
        return {
            "base_cost_usd": base_cost,
            "duration_cost_usd": duration_cost,
            "estimated_total_usd": base_cost + duration_cost,
            "note": "Actual costs may vary based on GCP pricing and usage"
        }
