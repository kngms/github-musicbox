# Music Track Generator

Music track generation system with CLI and REST API. Generate music tracks with different genres, structures, and styles. Works in simulate mode (no credentials needed) or with Google Cloud Platform Vertex AI integration.

## Features

- 🎵 **Multiple Genres**: Rock, Jazz, Electronic, Classical, Pop, and more
- 🏗️ **Customizable Structure**: Define verses, choruses, bridges, intros, and outros
- 🎨 **Style References**: Specify style inspirations like "in the style of..." or "similar to..."
- 💾 **Preset Management**: Save and reuse your favorite configurations
- ⏱️ **Flexible Duration**: Generate tracks between 1-4 minutes (60-240 seconds)
- 🔧 **CLI & API**: Use via command-line or REST API
- ☁️ **Optional GCP Integration**: Works without credentials (simulate mode) or with Vertex AI (gcp mode)
- 📝 **Built-in Tips**: Get prompting tips for each preset
- 🐳 **Cloud Run Ready**: Deploy to Google Cloud Run with included Dockerfile

## Modes

### Simulate Mode (Default)
- **No GCP credentials required**
- Perfect for development, testing, and demos
- Generates prompts and metadata without calling AI models
- Set `MUSIC_GEN_MODE=simulate` or omit (default)

### GCP Mode
- **Requires GCP project and credentials**
- For production deployment with Vertex AI
- Set `MUSIC_GEN_MODE=gcp`
- Requires `GOOGLE_CLOUD_PROJECT` environment variable

## Installation

### Prerequisites

- Python 3.9 or higher
- (Optional) Google Cloud Platform account for GCP mode

### Quick Install

```bash
# Clone the repository
git clone https://github.com/kngms/github-dev-sandbox.git
cd github-dev-sandbox

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install in Virtual Environment (Recommended)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### CLI Usage (No Credentials Needed)

```bash
# List available presets
music-gen list-presets

# Generate a track (simulate mode by default)
music-gen generate \
  --text "Walking down the street, feeling the beat..." \
  --genre rock \
  --preset rock_anthem
```

### API Server

```bash
# Start the API server (binds to 0.0.0.0:8080 by default)
uvicorn music_generator.api:app --host 0.0.0.0 --port 8080

# Or set custom port
PORT=3000 uvicorn music_generator.api:app --host 0.0.0.0 --port 3000
```

Access API documentation at `http://localhost:8080/docs`

## CLI Usage

### Generate a Track

```bash
music-gen generate --text "Your lyrics here" --genre rock [OPTIONS]
```

**Options:**
- `--text, -t`: Lyrics or text description (required)
- `--genre, -g`: Music genre (required)
- `--duration, -d`: Duration in seconds (60-240, default: 180)
- `--preset, -p`: Use a preset configuration
- `--output, -o`: Output file path
- `--mode`: Generation mode: simulate or gcp (default: simulate)
- `--intro/--no-intro`: Include intro section (default: yes)
- `--verses`: Number of verses (default: 2)
- `--choruses`: Number of choruses (default: 2)
- `--bridge/--no-bridge`: Include bridge (default: yes)
- `--outro/--no-outro`: Include outro (default: yes)
- `--style, -s`: Style reference (can be used multiple times)
- `--temperature`: Creativity level 0.0-1.0 (default: 0.7)
- `--project-id`: GCP project ID (for gcp mode)
- `--location`: GCP region (default: us-central1)
- `--credentials`: Path to GCP service account JSON

**Examples:**

```bash
# Using a preset (simulate mode)
music-gen generate \
  --text "We are the champions" \
  --genre rock \
  --preset rock_anthem

# Custom configuration with style references
music-gen generate \
  --text "Moonlight on the water" \
  --genre jazz \
  --duration 240 \
  --verses 3 \
  --choruses 2 \
  --style "style:smooth jazz" \
  --style "sound:saxophone and piano" \
  --temperature 0.6

# Using GCP mode (requires credentials)
export MUSIC_GEN_MODE=gcp
export GOOGLE_CLOUD_PROJECT=your-project-id
music-gen generate \
  --text "Your lyrics" \
  --genre rock \
  --preset rock_anthem
```

### Preset Commands

```bash
# List all presets
music-gen list-presets

# Show preset details
music-gen show-preset rock_anthem

# Save custom preset
music-gen save-preset \
  --name my_metal \
  --description "Heavy metal preset" \
  --genre metal \
  --verses 3 \
  --style "style:heavy metal" \
  --tips "Use aggressive lyrics"

# Delete preset
music-gen delete-preset my_metal
```

## API Usage

### Starting the Server

```bash
# Default (simulate mode, no auth)
uvicorn music_generator.api:app --host 0.0.0.0 --port 8080

# With API key authentication
export MUSIC_GEN_API_KEY=your-secret-key
uvicorn music_generator.api:app --host 0.0.0.0 --port 8080

# GCP mode
export MUSIC_GEN_MODE=gcp
export GOOGLE_CLOUD_PROJECT=your-project-id
uvicorn music_generator.api:app --host 0.0.0.0 --port 8080
```

### API Endpoints

#### Generate Track
```bash
# POST /tracks/generate
curl -X POST http://localhost:8080/tracks/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text_input": "We are the champions",
    "genre": "rock",
    "duration_seconds": 180,
    "preset_name": "rock_anthem"
  }'

# With custom structure (no preset)
curl -X POST http://localhost:8080/tracks/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text_input": "Moonlight dancing",
    "genre": "jazz",
    "duration_seconds": 200,
    "structure": {
      "intro": true,
      "verse_count": 2,
      "chorus_count": 2,
      "bridge": true,
      "outro": true
    },
    "temperature": 0.6
  }'
```

#### List Presets
```bash
# GET /presets
curl http://localhost:8080/presets
```

#### Get Specific Preset
```bash
# GET /presets/{name}
curl http://localhost:8080/presets/rock_anthem
```

#### Create/Update Preset
```bash
# POST /presets
curl -X POST http://localhost:8080/presets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_indie",
    "description": "Indie folk preset",
    "genre": "indie",
    "structure": {
      "intro": true,
      "verse_count": 3,
      "chorus_count": 2,
      "bridge": true,
      "outro": true
    },
    "style_references": [
      {"type": "style", "value": "indie folk"}
    ],
    "temperature": 0.6,
    "tips": "Use introspective lyrics"
  }'
```

#### Delete Preset
```bash
# DELETE /presets/{name}
curl -X DELETE http://localhost:8080/presets/my_indie
```

#### Get Prompt Tips
```bash
# GET /prompt-tips
curl http://localhost:8080/prompt-tips

# Filter by preset
curl http://localhost:8080/prompt-tips?preset_name=rock_anthem
```

#### Health Check
```bash
# GET /health
curl http://localhost:8080/health
```

### API Authentication

When `MUSIC_GEN_API_KEY` is set, all endpoints require authentication:

```bash
# Using X-API-Key header
curl http://localhost:8080/presets \
  -H "X-API-Key: your-secret-key"

# Using Authorization Bearer token
curl http://localhost:8080/presets \
  -H "Authorization: Bearer your-secret-key"
```

## Python SDK Usage

```python
from music_generator.presets import PresetManager
from music_generator.generator import MusicGenerator
from music_generator.models import TrackConfig, SongStructure, StyleReference

# Using a preset (simulate mode - no credentials needed)
preset_manager = PresetManager()
preset = preset_manager.load_preset("rock_anthem")
config = preset.to_track_config(
    text_input="Your lyrics here",
    duration_seconds=180
)

generator = MusicGenerator(mode="simulate")
result = generator.generate_track(config, output_path="track.mp3")

# Custom configuration
structure = SongStructure(
    intro=True,
    verse_count=2,
    chorus_count=3,
    bridge=True,
    outro=True
)

config = TrackConfig(
    text_input="Your lyrics",
    genre="rock",
    duration_seconds=180,
    structure=structure,
    style_references=[
        StyleReference(type="style", value="arena rock")
    ],
    temperature=0.8
)

generator = MusicGenerator(mode="simulate")
result = generator.generate_track(config)
print(f"Status: {result['status']}, Mode: {result['mode']}")
```

## Built-in Presets

| Preset | Genre | Description |
|--------|-------|-------------|
| **rock_anthem** | Rock | High-energy rock with powerful vocals |
| **jazz_smooth** | Jazz | Smooth jazz with relaxed tempo |
| **electronic_dance** | Electronic | Upbeat EDM |
| **classical_orchestral** | Classical | Classical orchestral composition |
| **pop_catchy** | Pop | Radio-friendly pop |

## Docker & Cloud Run

### Build Docker Image

```bash
docker build -t music-track-generator .
```

### Run Locally with Docker

```bash
# Simulate mode (no credentials)
docker run -p 8080:8080 music-track-generator

# With API key
docker run -p 8080:8080 \
  -e MUSIC_GEN_API_KEY=your-secret-key \
  music-track-generator

# GCP mode
docker run -p 8080:8080 \
  -e MUSIC_GEN_MODE=gcp \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  music-track-generator
```

### Deploy to Google Cloud Run

```bash
# Build and push to Google Container Registry
export PROJECT_ID=your-gcp-project-id
gcloud builds submit --tag gcr.io/${PROJECT_ID}/music-track-generator

# Deploy to Cloud Run (simulate mode - no credentials needed)
gcloud run deploy music-track-generator \
  --image gcr.io/${PROJECT_ID}/music-track-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MUSIC_GEN_MODE=simulate

# Deploy with GCP mode (uses Cloud Run service account for Vertex AI)
gcloud run deploy music-track-generator \
  --image gcr.io/${PROJECT_ID}/music-track-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MUSIC_GEN_MODE=gcp,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}

# Deploy with API key authentication
gcloud run deploy music-track-generator \
  --image gcr.io/${PROJECT_ID}/music-track-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MUSIC_GEN_MODE=simulate,MUSIC_GEN_API_KEY=your-secret-key
```

**Note for GCP Mode on Cloud Run:**
- The Cloud Run service account needs Vertex AI permissions
- No service account JSON file is needed - Cloud Run uses Application Default Credentials (ADC)
- Grant the service account the "Vertex AI User" role:

```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## Running in Codespaces

GitHub Codespaces works out of the box:

1. Open repository in Codespaces
2. Install dependencies: `pip install -r requirements.txt && pip install -e .`
3. Start using (no GCP credentials needed in simulate mode):
   ```bash
   music-gen list-presets
   music-gen generate --text "Your lyrics" --genre rock --preset rock_anthem
   ```
4. Or start the API server:
   ```bash
   uvicorn music_generator.api:app --host 0.0.0.0 --port 8080
   ```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MUSIC_GEN_MODE` | Mode: `simulate` or `gcp` | `simulate` | No |
| `MUSIC_GEN_API_KEY` | API key for authentication | None | No |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | None | Yes (gcp mode) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | None | No (uses ADC) |
| `GOOGLE_CLOUD_REGION` | GCP region | `us-central1` | No |
| `PORT` | Server port | `8080` | No |

## Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
```

## Project Structure

```
github-dev-sandbox/
├── src/music_generator/
│   ├── __init__.py
│   ├── api.py           # FastAPI REST API server
│   ├── cli.py           # CLI interface
│   ├── generator.py     # Music generation (simulate/gcp modes)
│   ├── models.py        # Pydantic data models
│   └── presets.py       # Preset management
├── presets/             # Built-in YAML presets
├── tests/              # API and integration tests
├── examples/           # Usage examples
├── docs/              # Documentation
├── Dockerfile         # Cloud Run deployment
├── .dockerignore      # Docker build exclusions
├── requirements.txt   # Python dependencies
├── setup.py          # Package setup
└── README.md         # This file
```

## TODOs for Real Audio Generation

The current implementation generates prompts and metadata (simulate mode). To integrate with actual music generation:

1. **Choose a music generation model** on Vertex AI or another platform
2. **Update `generator.py`** in GCP mode:
   - Replace simulated response with actual API calls
   - Handle audio file generation and storage
   - Implement streaming or async generation if needed
3. **Add audio storage**:
   - Integrate with Google Cloud Storage for audio files
   - Return signed URLs or direct downloads
4. **Update response models** to include audio URLs/data
5. **Add audio format options** (MP3, WAV, FLAC, etc.)

## Troubleshooting

### "Invalid or missing API key" (401)
Set the `MUSIC_GEN_API_KEY` environment variable and include it in requests.

### "GCP project ID required in gcp mode"
Set `GOOGLE_CLOUD_PROJECT` environment variable or pass `--project-id` to CLI.

### "Google Cloud libraries not installed"
Install GCP dependencies: `pip install google-cloud-aiplatform google-auth`

### Port already in use
Change the port: `PORT=3000 uvicorn music_generator.api:app --host 0.0.0.0 --port 3000`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

- API Documentation: Run server and visit `/docs` for interactive Swagger UI
- Issues: https://github.com/kngms/github-dev-sandbox/issues
- Examples: Check the `examples/` directory
