"""Music track generation with optional GCP Vertex AI integration."""

import os
import json
from typing import Optional, Dict, Any, Literal
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
    """Music track generator with simulate and GCP modes."""
    
    def __init__(
        self,
        mode: Optional[Literal["simulate", "gcp"]] = None,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        credentials_path: Optional[str] = None
    ):
        """Initialize the music generator.
        
        Args:
            mode: Generation mode - 'simulate' or 'gcp'. If None, reads from MUSIC_GEN_MODE env var (default: simulate)
            project_id: GCP project ID (required for gcp mode). If None, uses GOOGLE_CLOUD_PROJECT env var
            location: GCP region for Vertex AI (only used in gcp mode)
            credentials_path: Path to service account JSON (only used in gcp mode). If None, uses GOOGLE_APPLICATION_CREDENTIALS env var
        """
        # Determine mode
        self.mode = mode or os.getenv("MUSIC_GEN_MODE", "simulate")
        if self.mode not in ["simulate", "gcp"]:
            raise ValueError(f"Invalid mode '{self.mode}'. Must be 'simulate' or 'gcp'")
        
        self.location = location
        self.project_id = None
        
        if self.mode == "gcp":
            # GCP mode requires project ID and initialization
            if not GOOGLE_CLOUD_AVAILABLE:
                raise ImportError(
                    "Google Cloud libraries not installed. "
                    "Install with: pip install google-cloud-aiplatform google-auth"
                )
            
            self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
            
            if not self.project_id:
                raise ValueError(
                    "GCP project ID required in gcp mode. Set GOOGLE_CLOUD_PROJECT environment variable "
                    "or pass project_id parameter"
                )
            
            # Initialize credentials
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
            else:
                credentials = None  # Will use default credentials (ADC)
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials
            )
            
            logger.info(f"Initialized MusicGenerator in GCP mode for project {self.project_id} in {self.location}")
        else:
            # Simulate mode - no GCP initialization needed
            logger.info("Initialized MusicGenerator in simulate mode (no GCP credentials required)")
    
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
        
        logger.info(f"Generating {config.genre} track ({config.duration_seconds}s) in {self.mode} mode")
        logger.debug(f"Prompt:\n{prompt}")
        
        # Simulate mode or GCP mode (currently both simulated until real model is integrated)
        if self.mode == "simulate":
            message = "Track generation simulated (no GCP credentials required)."
        else:
            message = (
                "Track generation simulated. In production, this would call "
                "Google Cloud Vertex AI music generation API with the generated prompt."
            )
        
        result = {
            "status": "simulated",
            "mode": self.mode,
            "genre": config.genre,
            "duration_seconds": config.duration_seconds,
            "prompt": prompt,
            "metadata": {
                "structure": config.structure.model_dump(),
                "style_references": [ref.model_dump() for ref in config.style_references],
                "temperature": config.temperature
            },
            "message": message
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
