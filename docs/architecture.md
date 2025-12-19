# Architecture Documentation

## Overview

The Music Track Generator is a Python-based system that provides a command-line interface and SDK for generating music tracks using Google Cloud Platform's Vertex AI. The system is designed to be simple, extensible, and user-friendly.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  CLI (Click) │              │  Python SDK  │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                              │                     │
│         └──────────────┬───────────────┘                     │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│                   Core Components                            │
├────────────────────────┼─────────────────────────────────────┤
│                        │                                     │
│  ┌─────────────────────▼──────────────────┐                 │
│  │        Configuration Models            │                 │
│  │  - TrackConfig                         │                 │
│  │  - SongStructure                       │                 │
│  │  - StyleReference                      │                 │
│  │  - PresetConfig                        │                 │
│  └─────────────────────┬──────────────────┘                 │
│                        │                                     │
│  ┌─────────────────────▼──────────────────┐                 │
│  │       Preset Manager                   │                 │
│  │  - Built-in presets                    │                 │
│  │  - Save/Load presets                   │                 │
│  │  - YAML persistence                    │                 │
│  └─────────────────────┬──────────────────┘                 │
│                        │                                     │
│  ┌─────────────────────▼──────────────────┐                 │
│  │       Music Generator                  │                 │
│  │  - Prompt building                     │                 │
│  │  - GCP integration                     │                 │
│  │  - Cost estimation                     │                 │
│  └─────────────────────┬──────────────────┘                 │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  External Services                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────┐                   │
│  │  Google Cloud Platform               │                   │
│  │  - Vertex AI                         │                   │
│  │  - Authentication                    │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

#### CLI (cli.py)
- Built with Click framework
- Provides rich terminal UI using Rich library
- Commands:
  - `generate`: Generate music tracks
  - `list-presets`: List available presets
  - `show-preset`: Show preset details
  - `save-preset`: Save custom presets
  - `delete-preset`: Delete presets
  - `setup`: Interactive GCP setup wizard

#### Python SDK
- Direct programmatic access to all functionality
- Same models and APIs used by CLI
- Allows integration into larger applications

### 2. Core Components

#### Configuration Models (models.py)
- **SongStructure**: Defines track structure (intro, verses, choruses, bridge, outro)
- **StyleReference**: Style and sound references for the track
- **TrackConfig**: Complete configuration for track generation
- **PresetConfig**: Saved preset configurations

Uses Pydantic for:
- Data validation
- Type safety
- Serialization/deserialization
- Default values

#### Preset Manager (presets.py)
- Manages preset configurations
- Built-in presets:
  - rock_anthem
  - jazz_smooth
  - electronic_dance
  - classical_orchestral
  - pop_catchy
- YAML-based persistence
- CRUD operations for presets

#### Music Generator (generator.py)
- Interfaces with Google Cloud Vertex AI
- Builds prompts from track configurations
- Handles GCP authentication
- Provides cost estimation
- Manages metadata storage

### 3. External Services

#### Google Cloud Platform
- **Vertex AI**: Music generation model
- **Authentication**: Service account or ADC
- **Storage**: Optional for generated tracks

## Data Flow

### Track Generation Flow

```
1. User Input (CLI or SDK)
   ↓
2. Configuration Creation
   - Load preset (optional)
   - Parse user parameters
   - Validate configuration
   ↓
3. Prompt Generation
   - Build structure description
   - Incorporate style references
   - Format text input
   ↓
4. GCP Integration
   - Authenticate
   - Call Vertex AI API
   - Receive generated track
   ↓
5. Output
   - Save track file
   - Save metadata
   - Display results
```

### Preset Management Flow

```
1. Create Preset
   ↓
2. Validate Configuration
   ↓
3. Serialize to YAML
   ↓
4. Save to presets/ directory
   ↓
5. Available for use
```

## Technology Stack

### Core Technologies
- **Python 3.9+**: Primary language
- **Click**: CLI framework
- **Pydantic**: Data validation and models
- **Rich**: Terminal UI
- **PyYAML**: Preset persistence

### Google Cloud
- **google-cloud-aiplatform**: Vertex AI client
- **google-auth**: Authentication

### Development
- **setuptools**: Package management
- **python-dotenv**: Environment configuration

## Security

### Credentials Management
- Environment variables for sensitive data
- Support for service account JSON files
- Application Default Credentials (ADC) support
- No credentials stored in code

### Data Protection
- User presets stored locally
- Generated tracks stored locally
- Metadata includes no sensitive information

## Extensibility

### Adding New Presets
1. Create PresetConfig with desired parameters
2. Save using PresetManager
3. Immediately available in CLI and SDK

### Adding New Features
- **New genres**: Simply pass as parameter, no code changes needed
- **New structure types**: Extend SongStructure model
- **New style types**: Add to StyleReference type field
- **Custom outputs**: Extend MusicGenerator.generate_track()

### Integration Points
- Python SDK allows embedding in other applications
- CLI can be wrapped by scripts
- Output metadata in JSON format for processing
- YAML presets can be version controlled

## Performance Considerations

### Optimization Strategies
- Lazy loading of presets
- Credential caching
- Minimal dependencies
- Efficient prompt building

### Scalability
- Stateless design allows parallel execution
- No database required
- File-based storage for presets
- Can be containerized for cloud deployment

## Error Handling

### Validation
- Pydantic validates all input data
- Clear error messages for invalid configurations
- Duration and count constraints enforced

### GCP Errors
- Connection failures handled gracefully
- Authentication errors reported clearly
- Cost estimation before generation
- User confirmation for operations

## Future Enhancements

### Potential Features
1. Audio preview before generation
2. Batch generation of multiple tracks
3. Track variations (generate multiple versions)
4. Web UI interface
5. Cloud storage integration
6. Collaborative preset sharing
7. Advanced audio editing options
8. Custom model training support

### Architecture Evolution
- Could add caching layer for cost optimization
- Database for large-scale preset management
- API server for web/mobile clients
- Queue system for batch processing
- Analytics for usage tracking
