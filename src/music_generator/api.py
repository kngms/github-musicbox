"""FastAPI server for music track generation."""

import os
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

from .models import TrackConfig, SongStructure, StyleReference, PresetConfig
from .generator import MusicGenerator
from .presets import PresetManager

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Initialize shared components (before lifespan to ensure availability)
preset_manager = PresetManager()
# Cache for generator instances by mode
_generator_cache: Dict[str, MusicGenerator] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("=" * 70)
    logger.info("🎵 Music Track Generator API - Startup Configuration")
    logger.info("=" * 70)
    
    # Get configuration values
    mode = os.getenv("MUSIC_GEN_MODE", "simulate")
    api_key_set = "yes" if os.getenv("MUSIC_GEN_API_KEY") else "no"
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "not set")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    
    # Print core configuration
    logger.info(f"Mode: {mode}")
    logger.info(f"API Key Authentication: {api_key_set}")
    
    # Print GCP-specific configuration when in gcp mode
    if mode == "gcp":
        logger.info(f"Google Cloud Project: {project}")
        logger.info(f"Google Cloud Region: {region}")
    
    # Print available presets
    presets = preset_manager.list_presets()
    logger.info(f"Available Presets: {len(presets)} loaded")
    
    logger.info("=" * 70)
    logger.info("✅ Server ready to accept requests")
    logger.info("=" * 70)
    
    yield
    
    # Shutdown - clear generator cache
    _generator_cache.clear()
    logger.info("Shutting down...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Music Track Generator API",
    description="Generate music tracks with configurable genres, structures, and styles",
    version="0.1.0",
    lifespan=lifespan
)

# Get API key from environment (optional)
API_KEY = os.getenv("MUSIC_GEN_API_KEY")


# Request/Response Models
class GenerateTrackRequest(BaseModel):
    """Request model for track generation."""
    text_input: str = Field(..., description="Lyrics or text description for the track")
    genre: str = Field(..., description="Music genre")
    duration_seconds: int = Field(180, ge=60, le=240, description="Track duration in seconds (60-240)")
    preset_name: Optional[str] = Field(None, description="Optional preset name to use as base")
    structure: Optional[SongStructure] = Field(None, description="Song structure (optional if using preset)")
    style_references: Optional[List[StyleReference]] = Field(None, description="Style references (optional)")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Creativity level (0.0-1.0)")


class GenerateTrackResponse(BaseModel):
    """Response model for track generation."""
    status: str
    mode: str
    genre: str
    duration_seconds: int
    prompt: str
    metadata: Dict[str, Any]
    message: str


class PresetListItem(BaseModel):
    """Preset list item."""
    name: str
    genre: str
    description: Optional[str]


class PromptTip(BaseModel):
    """Prompt tip from a preset."""
    preset_name: str
    genre: str
    tips: Optional[str]


class ConfigResponse(BaseModel):
    """Response model for configuration endpoint."""
    mode: str
    region: Optional[str]
    project: Optional[str]
    presets_available: List[str]
    auth_enabled: bool


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    field: str
    message: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Structured validation error response."""
    detail: str
    errors: List[ValidationErrorDetail]


# API Key Authentication
def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """Verify API key if configured."""
    if not API_KEY:
        # No API key configured, allow access
        return True
    
    # Check X-API-Key header
    if x_api_key and x_api_key == API_KEY:
        return True
    
    # Check Authorization header (Bearer token)
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] == API_KEY:
            return True
    
    raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    """Custom handler for validation errors to return structured responses."""
    errors = []
    for error in exc.errors():
        # Get field name from loc (location)
        field = ".".join(str(loc) for loc in error["loc"]) if error["loc"] else "unknown"
        errors.append(
            ValidationErrorDetail(
                field=field,
                message=error["msg"],
                type=error["type"]
            )
        )
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": [e.model_dump() for e in errors]
        }
    )


def get_generator() -> MusicGenerator:
    """Get music generator instance based on mode (cached for performance)."""
    mode = os.getenv("MUSIC_GEN_MODE", "simulate")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    
    # Create cache key based on configuration (normalize None values)
    cache_key = f"{mode}:{project_id or ''}:{location}"
    
    # Return cached generator if available
    if cache_key in _generator_cache:
        return _generator_cache[cache_key]
    
    # Create and cache new generator
    generator = MusicGenerator(
        mode=mode,
        project_id=project_id,
        location=location
    )
    _generator_cache[cache_key] = generator
    
    return generator


# Endpoints

@app.get("/")
def root():
    """API root endpoint."""
    return {
        "message": "Music Track Generator API",
        "version": "0.1.0",
        "docs": "/docs",
        "mode": os.getenv("MUSIC_GEN_MODE", "simulate")
    }


@app.post("/tracks/generate", response_model=GenerateTrackResponse, dependencies=[Depends(verify_api_key)])
def generate_track(request: GenerateTrackRequest):
    """Generate a music track.
    
    If preset_name is provided, it will be used as a base and merged with any provided overrides.
    """
    try:
        # Start with preset if provided
        if request.preset_name:
            preset = preset_manager.load_preset(request.preset_name)
            if not preset:
                raise HTTPException(status_code=404, detail=f"Preset '{request.preset_name}' not found")
            
            # Create config from preset
            config = preset.to_track_config(
                text_input=request.text_input,
                duration_seconds=request.duration_seconds
            )
            
            # Apply overrides if provided
            if request.structure:
                config.structure = request.structure
            if request.style_references:
                config.style_references = request.style_references
            if request.temperature is not None:
                config.temperature = request.temperature
        else:
            # Create config from request
            if not request.structure:
                raise HTTPException(
                    status_code=422,
                    detail="Either preset_name or structure must be provided"
                )
            
            config = TrackConfig(
                text_input=request.text_input,
                genre=request.genre,
                duration_seconds=request.duration_seconds,
                structure=request.structure,
                style_references=request.style_references or [],
                temperature=request.temperature if request.temperature is not None else 0.7
            )
        
        # Generate track
        generator = get_generator()
        result = generator.generate_track(config)
        
        return GenerateTrackResponse(**result)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating track: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/presets", response_model=List[PresetListItem], dependencies=[Depends(verify_api_key)])
def list_presets():
    """List all available presets."""
    try:
        # Get preset metadata efficiently without loading full configs
        presets = preset_manager.list_presets_with_metadata()
        return presets
    
    except Exception as e:
        logger.error(f"Error listing presets: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/presets/{name}", response_model=PresetConfig, dependencies=[Depends(verify_api_key)])
def get_preset(name: str):
    """Get a specific preset by name."""
    try:
        preset = preset_manager.load_preset(name)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset '{name}' not found")
        
        return preset
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting preset: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/presets", response_model=PresetConfig, dependencies=[Depends(verify_api_key)])
def create_preset(preset: PresetConfig):
    """Create or update a preset."""
    try:
        preset_manager.save_preset(preset)
        return preset
    
    except Exception as e:
        logger.error(f"Error creating preset: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/presets/{name}", dependencies=[Depends(verify_api_key)])
def delete_preset(name: str):
    """Delete a preset."""
    try:
        success = preset_manager.delete_preset(name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Preset '{name}' not found")
        
        return {"message": f"Preset '{name}' deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting preset: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/prompt-tips", response_model=List[PromptTip], dependencies=[Depends(verify_api_key)])
def get_prompt_tips(preset_name: Optional[str] = Query(None, description="Filter by preset name")):
    """Get prompting tips from presets.
    
    If preset_name is provided, returns tips for that preset only.
    Otherwise, returns tips from all presets.
    """
    try:
        tips = []
        
        if preset_name:
            # Get tips for specific preset
            preset = preset_manager.load_preset(preset_name)
            if not preset:
                raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
            
            tips.append(PromptTip(
                preset_name=preset.name,
                genre=preset.genre,
                tips=preset.tips
            ))
        else:
            # Get tips from all presets
            preset_names = preset_manager.list_presets()
            for name in preset_names:
                preset = preset_manager.load_preset(name)
                if preset and preset.tips:
                    tips.append(PromptTip(
                        preset_name=preset.name,
                        genre=preset.genre,
                        tips=preset.tips
                    ))
        
        return tips
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt tips: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": os.getenv("MUSIC_GEN_MODE", "simulate")
    }


@app.get("/config", response_model=ConfigResponse, dependencies=[Depends(verify_api_key)])
def get_config():
    """Get current configuration information.
    
    Returns safe configuration details without exposing secrets.
    """
    mode = os.getenv("MUSIC_GEN_MODE", "simulate")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1") if mode == "gcp" else None
    project = os.getenv("GOOGLE_CLOUD_PROJECT") if mode == "gcp" else None
    presets = preset_manager.list_presets()
    auth_enabled = bool(os.getenv("MUSIC_GEN_API_KEY"))
    
    return ConfigResponse(
        mode=mode,
        region=region,
        project=project,
        presets_available=presets,
        auth_enabled=auth_enabled
    )
