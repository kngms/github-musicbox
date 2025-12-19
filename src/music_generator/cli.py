"""Command-line interface for music track generation."""

import os
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from dotenv import load_dotenv

from .models import TrackConfig, SongStructure, StyleReference, PresetConfig
from .generator import MusicGenerator
from .presets import PresetManager

# Load environment variables
load_dotenv()

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Music Track Generator - GCP-powered music generation CLI.
    
    Generate music tracks with different genres, structures, and styles
    using Google Cloud Platform's Vertex AI.
    """
    pass


@main.command()
@click.option('--text', '-t', required=True, help='Lyrics or text description for the track')
@click.option('--genre', '-g', required=True, help='Music genre (e.g., rock, jazz, electronic)')
@click.option('--duration', '-d', type=int, default=180, help='Duration in seconds (60-240)')
@click.option('--preset', '-p', help='Use a preset configuration')
@click.option('--output', '-o', help='Output file path')
@click.option('--intro/--no-intro', default=True, help='Include intro section')
@click.option('--verses', type=int, default=2, help='Number of verses')
@click.option('--choruses', type=int, default=2, help='Number of choruses')
@click.option('--bridge/--no-bridge', default=True, help='Include bridge section')
@click.option('--outro/--no-outro', default=True, help='Include outro section')
@click.option('--style', '-s', multiple=True, help='Style reference (format: type:value)')
@click.option('--temperature', type=float, default=0.7, help='Creativity level (0.0-1.0)')
@click.option('--project-id', help='GCP project ID (or set GOOGLE_CLOUD_PROJECT)')
@click.option('--location', default='us-central1', help='GCP region')
@click.option('--credentials', help='Path to GCP service account JSON')
def generate(text, genre, duration, preset, output, intro, verses, choruses, 
             bridge, outro, style, temperature, project_id, location, credentials):
    """Generate a music track."""
    
    try:
        # Load preset if specified
        if preset:
            preset_manager = PresetManager()
            preset_config = preset_manager.load_preset(preset)
            
            if not preset_config:
                console.print(f"[red]Preset '{preset}' not found[/red]")
                return
            
            console.print(f"[green]Using preset: {preset}[/green]")
            if preset_config.description:
                console.print(f"[dim]{preset_config.description}[/dim]")
            if preset_config.tips:
                console.print(Panel(preset_config.tips, title="Tips", border_style="blue"))
            
            # Create config from preset
            config = preset_config.to_track_config(text, duration)
        else:
            # Parse style references
            style_refs = []
            for s in style:
                if ':' not in s:
                    console.print(f"[yellow]Warning: Invalid style format '{s}', expected 'type:value'[/yellow]")
                    continue
                ref_type, ref_value = s.split(':', 1)
                style_refs.append(StyleReference(type=ref_type.strip(), value=ref_value.strip()))
            
            # Create configuration
            structure = SongStructure(
                intro=intro,
                verse_count=verses,
                chorus_count=choruses,
                bridge=bridge,
                outro=outro
            )
            
            config = TrackConfig(
                text_input=text,
                genre=genre,
                duration_seconds=duration,
                structure=structure,
                style_references=style_refs,
                temperature=temperature
            )
        
        # Display configuration
        console.print("\n[bold]Track Configuration:[/bold]")
        console.print(f"Genre: [cyan]{config.genre}[/cyan]")
        console.print(f"Duration: [cyan]{config.duration_seconds}s ({config.duration_seconds // 60}m {config.duration_seconds % 60}s)[/cyan]")
        console.print(f"Temperature: [cyan]{config.temperature}[/cyan]")
        
        if config.style_references:
            console.print("\n[bold]Style References:[/bold]")
            for ref in config.style_references:
                console.print(f"  • {ref.type}: [cyan]{ref.value}[/cyan]")
        
        console.print("\n[bold]Text Input:[/bold]")
        console.print(Panel(config.text_input, border_style="dim"))
        
        # Initialize generator
        with console.status("[bold green]Initializing GCP connection..."):
            generator = MusicGenerator(
                project_id=project_id,
                location=location,
                credentials_path=credentials
            )
        
        # Estimate cost
        cost_estimate = generator.estimate_cost(config)
        console.print(f"\n[bold]Estimated cost:[/bold] ${cost_estimate['estimated_total_usd']:.4f} USD")
        
        if not Confirm.ask("Proceed with generation?", default=True):
            console.print("[yellow]Generation cancelled[/yellow]")
            return
        
        # Generate track
        with console.status("[bold green]Generating track..."):
            result = generator.generate_track(config, output_path=output)
        
        # Display results
        console.print("\n[bold green]✓ Track generation completed![/bold green]")
        console.print(f"Status: [cyan]{result['status']}[/cyan]")
        console.print(f"\n{result['message']}")
        
        if 'metadata_path' in result:
            console.print(f"\nMetadata saved to: [cyan]{result['metadata_path']}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@main.command()
def list_presets():
    """List all available presets."""
    
    preset_manager = PresetManager()
    presets = preset_manager.list_presets()
    
    if not presets:
        console.print("[yellow]No presets found[/yellow]")
        return
    
    table = Table(title="Available Presets", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Genre", style="green")
    table.add_column("Description")
    
    for preset_name in presets:
        preset = preset_manager.load_preset(preset_name)
        if preset:
            table.add_row(
                preset.name,
                preset.genre,
                preset.description or ""
            )
    
    console.print(table)


@main.command()
@click.argument('preset_name')
def show_preset(preset_name):
    """Show details of a preset."""
    
    preset_manager = PresetManager()
    preset = preset_manager.load_preset(preset_name)
    
    if not preset:
        console.print(f"[red]Preset '{preset_name}' not found[/red]")
        return
    
    console.print(f"\n[bold]{preset.name}[/bold]")
    if preset.description:
        console.print(f"[dim]{preset.description}[/dim]\n")
    
    console.print(f"Genre: [cyan]{preset.genre}[/cyan]")
    console.print(f"Temperature: [cyan]{preset.temperature}[/cyan]")
    
    console.print("\n[bold]Structure:[/bold]")
    console.print(f"  Intro: {'✓' if preset.structure.intro else '✗'}")
    console.print(f"  Verses: {preset.structure.verse_count}")
    console.print(f"  Choruses: {preset.structure.chorus_count}")
    console.print(f"  Bridge: {'✓' if preset.structure.bridge else '✗'}")
    console.print(f"  Outro: {'✓' if preset.structure.outro else '✗'}")
    
    if preset.style_references:
        console.print("\n[bold]Style References:[/bold]")
        for ref in preset.style_references:
            console.print(f"  • {ref.type}: [cyan]{ref.value}[/cyan]")
    
    if preset.tips:
        console.print()
        console.print(Panel(preset.tips, title="Tips", border_style="blue"))


@main.command()
@click.option('--name', '-n', required=True, help='Preset name')
@click.option('--description', '-d', help='Preset description')
@click.option('--genre', '-g', required=True, help='Music genre')
@click.option('--intro/--no-intro', default=True, help='Include intro section')
@click.option('--verses', type=int, default=2, help='Number of verses')
@click.option('--choruses', type=int, default=2, help='Number of choruses')
@click.option('--bridge/--no-bridge', default=True, help='Include bridge section')
@click.option('--outro/--no-outro', default=True, help='Include outro section')
@click.option('--style', '-s', multiple=True, help='Style reference (format: type:value)')
@click.option('--temperature', type=float, default=0.7, help='Creativity level (0.0-1.0)')
@click.option('--tips', help='Tips for using this preset')
def save_preset(name, description, genre, intro, verses, choruses, bridge, 
                outro, style, temperature, tips):
    """Save a new preset configuration."""
    
    try:
        # Parse style references
        style_refs = []
        for s in style:
            if ':' not in s:
                console.print(f"[yellow]Warning: Invalid style format '{s}', expected 'type:value'[/yellow]")
                continue
            ref_type, ref_value = s.split(':', 1)
            style_refs.append(StyleReference(type=ref_type.strip(), value=ref_value.strip()))
        
        # Create preset
        structure = SongStructure(
            intro=intro,
            verse_count=verses,
            chorus_count=choruses,
            bridge=bridge,
            outro=outro
        )
        
        preset = PresetConfig(
            name=name,
            description=description,
            genre=genre,
            structure=structure,
            style_references=style_refs,
            temperature=temperature,
            tips=tips
        )
        
        # Save preset
        preset_manager = PresetManager()
        preset_path = preset_manager.save_preset(preset)
        
        console.print(f"[green]✓ Preset '{name}' saved to {preset_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@main.command()
@click.argument('preset_name')
def delete_preset(preset_name):
    """Delete a preset."""
    
    preset_manager = PresetManager()
    
    if not preset_manager.load_preset(preset_name):
        console.print(f"[red]Preset '{preset_name}' not found[/red]")
        return
    
    if not Confirm.ask(f"Delete preset '{preset_name}'?", default=False):
        console.print("[yellow]Deletion cancelled[/yellow]")
        return
    
    if preset_manager.delete_preset(preset_name):
        console.print(f"[green]✓ Preset '{preset_name}' deleted[/green]")
    else:
        console.print(f"[red]Failed to delete preset '{preset_name}'[/red]")


@main.command()
def setup():
    """Interactive setup wizard for GCP credentials."""
    
    console.print(Panel.fit(
        "[bold]Music Track Generator Setup[/bold]\n\n"
        "This wizard will help you configure GCP credentials.",
        border_style="blue"
    ))
    
    # Check for existing configuration
    has_project = bool(os.getenv("GOOGLE_CLOUD_PROJECT"))
    has_creds = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    
    if has_project and has_creds:
        console.print("[green]✓ GCP credentials already configured[/green]")
        console.print(f"  Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
        console.print(f"  Credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
        
        if not Confirm.ask("\nReconfigure?", default=False):
            return
    
    console.print("\n[bold]Step 1: GCP Project ID[/bold]")
    project_id = Prompt.ask("Enter your GCP project ID", default=os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    
    console.print("\n[bold]Step 2: Service Account Credentials[/bold]")
    console.print("You can either:")
    console.print("  1. Provide path to a service account JSON file")
    console.print("  2. Use Application Default Credentials (ADC)")
    
    use_file = Confirm.ask("Use service account JSON file?", default=True)
    
    if use_file:
        creds_path = Prompt.ask(
            "Enter path to service account JSON",
            default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        )
    else:
        creds_path = ""
        console.print("[yellow]Using Application Default Credentials[/yellow]")
        console.print("Make sure you've run: gcloud auth application-default login")
    
    # Create .env file
    env_path = Path(".env")
    with open(env_path, 'w') as f:
        f.write(f"GOOGLE_CLOUD_PROJECT={project_id}\n")
        if creds_path:
            f.write(f"GOOGLE_APPLICATION_CREDENTIALS={creds_path}\n")
    
    console.print(f"\n[green]✓ Configuration saved to {env_path}[/green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Run: music-gen list-presets")
    console.print("  2. Try: music-gen generate --text 'Your lyrics' --genre rock --preset rock_anthem")


if __name__ == "__main__":
    main()
