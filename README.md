# Music Track Generator

A GCP-powered music track generation system with CLI interface. Generate music tracks with different genres, structures, and styles using Google Cloud Platform's Vertex AI.

## Features

- 🎵 **Multiple Genres**: Rock, Jazz, Electronic, Classical, Pop, and more
- 🏗️ **Customizable Structure**: Define verses, choruses, bridges, intros, and outros
- 🎨 **Style References**: Specify style inspirations like "in the style of..." or "similar to..."
- 💾 **Preset Management**: Save and reuse your favorite configurations
- ⏱️ **Flexible Duration**: Generate tracks between 1-4 minutes
- 🔧 **CLI & SDK**: Use via command-line or Python SDK
- ☁️ **GCP Integration**: Powered by Google Cloud Platform Vertex AI
- 📝 **Built-in Tips**: Get prompting tips for each preset

## Installation

### Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account with Vertex AI enabled
- GCP service account with appropriate permissions (or Application Default Credentials)

### Install from source

```bash
# Clone the repository
git clone https://github.com/kngms/github-dev-sandbox.git
cd github-dev-sandbox

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install in a virtual environment (recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### 1. Setup GCP Credentials

Run the interactive setup wizard:

```bash
music-gen setup
```

Or manually create a `.env` file:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 2. List Available Presets

```bash
music-gen list-presets
```

### 3. Generate Your First Track

```bash
music-gen generate \
  --text "Walking down the street, feeling the beat..." \
  --genre rock \
  --preset rock_anthem \
  --output my_track.mp3
```

## Usage

### CLI Commands

#### Generate a Track

```bash
music-gen generate --text "Your lyrics here" --genre rock [OPTIONS]
```

**Options:**
- `--text, -t`: Lyrics or text description (required)
- `--genre, -g`: Music genre (required)
- `--duration, -d`: Duration in seconds (60-240, default: 180)
- `--preset, -p`: Use a preset configuration
- `--output, -o`: Output file path
- `--intro/--no-intro`: Include intro section (default: yes)
- `--verses`: Number of verses (default: 2)
- `--choruses`: Number of choruses (default: 2)
- `--bridge/--no-bridge`: Include bridge (default: yes)
- `--outro/--no-outro`: Include outro (default: yes)
- `--style, -s`: Style reference (can be used multiple times)
- `--temperature`: Creativity level 0.0-1.0 (default: 0.7)
- `--project-id`: GCP project ID
- `--location`: GCP region (default: us-central1)
- `--credentials`: Path to service account JSON

**Example with style references:**

```bash
music-gen generate \
  --text "Lyrics about love and loss..." \
  --genre pop \
  --duration 240 \
  --style "style:contemporary pop" \
  --style "sound:acoustic guitar with soft piano" \
  --style "similar_to:Coldplay" \
  --output love_song.mp3
```

#### List Presets

```bash
music-gen list-presets
```

#### Show Preset Details

```bash
music-gen show-preset rock_anthem
```

#### Save a Custom Preset

```bash
music-gen save-preset \
  --name my_metal \
  --description "Heavy metal with aggressive sound" \
  --genre metal \
  --verses 3 \
  --choruses 2 \
  --bridge \
  --style "style:heavy metal" \
  --style "sound:distorted guitars with double bass drums" \
  --temperature 0.9 \
  --tips "Use aggressive, powerful lyrics. Focus on energy and intensity."
```

#### Delete a Preset

```bash
music-gen delete-preset my_metal
```

### Python SDK Usage

```python
from music_generator.models import TrackConfig, SongStructure, StyleReference
from music_generator.generator import MusicGenerator
from music_generator.presets import PresetManager

# Option 1: Use a preset
preset_manager = PresetManager()
preset = preset_manager.load_preset("rock_anthem")
config = preset.to_track_config(
    text_input="Your lyrics here...",
    duration_seconds=180
)

# Option 2: Create custom configuration
structure = SongStructure(
    intro=True,
    verse_count=2,
    chorus_count=3,
    bridge=True,
    outro=True
)

style_refs = [
    StyleReference(type="style", value="arena rock"),
    StyleReference(type="sound", value="electric guitars with powerful drums")
]

config = TrackConfig(
    text_input="Your lyrics here...",
    genre="rock",
    duration_seconds=180,
    structure=structure,
    style_references=style_refs,
    temperature=0.8
)

# Generate the track
generator = MusicGenerator(project_id="your-project-id")
result = generator.generate_track(config, output_path="output.mp3")

print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
```

## Built-in Presets

### rock_anthem
High-energy rock anthem with powerful vocals
- **Genre**: Rock
- **Tips**: Use energetic and empowering lyrics. Great for anthems and motivational songs.

### jazz_smooth
Smooth jazz with relaxed tempo
- **Genre**: Jazz
- **Tips**: Focus on sophisticated, laid-back lyrics. Perfect for evening moods.

### electronic_dance
Upbeat electronic dance music
- **Genre**: Electronic
- **Tips**: Keep lyrics simple and repetitive. Build energy through structure.

### classical_orchestral
Classical orchestral composition
- **Genre**: Classical
- **Tips**: Use poetic and dramatic text. Focus on emotional depth and dynamics.

### pop_catchy
Catchy pop song with radio-friendly structure
- **Genre**: Pop
- **Tips**: Focus on memorable hooks and relatable themes. Keep it upbeat and accessible.

## Song Structure

Define the structure of your song:

- **Intro**: Opening section that sets the mood
- **Verses**: Main storytelling sections (1-5 verses)
- **Choruses**: Repeated hook sections (1-4 choruses)
- **Bridge**: Transitional section with different melody/lyrics
- **Outro**: Closing section

## Style References

You can specify style references to guide the generation:

- `style`: Overall style (e.g., "arena rock", "smooth jazz")
- `sound`: Specific sound characteristics (e.g., "electric guitars with drums")
- `artist`: Artist reference (e.g., "The Beatles")
- `similar_to`: Similar to a specific song or artist

**Example:**

```bash
--style "style:80s synth pop" \
--style "sound:synthesizers and drum machines" \
--style "artist:Depeche Mode"
```

## Temperature Setting

The temperature parameter controls creativity:

- **0.0-0.3**: Conservative, stays close to typical patterns
- **0.4-0.7**: Balanced creativity (recommended)
- **0.8-1.0**: Very creative, more experimental

## Development

### Running in Codespaces

This project works great in GitHub Codespaces:

1. Open the repository in Codespaces
2. Run `pip install -r requirements.txt && pip install -e .`
3. Set up your GCP credentials with `music-gen setup`
4. Start generating music!

### Running Locally

```bash
# Clone the repository
git clone https://github.com/kngms/github-dev-sandbox.git
cd github-dev-sandbox

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install
pip install -r requirements.txt
pip install -e .

# Run
music-gen --help
```

### Project Structure

```
github-dev-sandbox/
├── src/
│   └── music_generator/
│       ├── __init__.py
│       ├── cli.py           # CLI interface
│       ├── generator.py     # GCP integration
│       ├── models.py        # Data models
│       └── presets.py       # Preset management
├── presets/                 # Saved presets
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
└── README.md               # This file
```

## Environment Variables

- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON (optional if using ADC)

## Troubleshooting

### "GCP project ID not provided"

Make sure you've set the `GOOGLE_CLOUD_PROJECT` environment variable or use the `--project-id` flag.

### "Google Cloud libraries not installed"

Install the required dependencies:
```bash
pip install google-cloud-aiplatform google-auth
```

### Permission Errors

Ensure your service account has the following permissions:
- Vertex AI User
- Service Account Token Creator

## Cost Estimation

The CLI provides cost estimates before generation. Actual costs depend on:
- Track duration
- GCP pricing in your region
- API usage

Typical costs range from $0.01 to $0.05 per track.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review example configurations in the `presets/` directory
