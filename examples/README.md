# Examples

This directory contains example usage of the Music Track Generator.

## Shell Script Examples

### Rock Anthem
```bash
bash rock_anthem.sh
```

Generates a high-energy rock anthem using the built-in `rock_anthem` preset.

### Jazz Smooth
```bash
bash jazz_smooth.sh
```

Generates a smooth jazz track using the built-in `jazz_smooth` preset.

### Custom EDM
```bash
bash custom_edm.sh
```

Generates a custom electronic dance music track with specific style references and parameters.

## Python SDK Examples

### Run all examples
```bash
python sdk_usage.py
```

### Individual examples

The `sdk_usage.py` file contains three examples:

1. **Using a preset**: Shows how to use a built-in preset
2. **Custom track configuration**: Demonstrates creating a track with full custom configuration
3. **Saving a custom preset**: Shows how to create and save your own preset

You can run individual functions by importing them:

```python
from sdk_usage import example_with_preset

example_with_preset()
```

## Notes

- Make sure you've configured your GCP credentials before running these examples
- Update the `project_id` in the Python examples to match your GCP project
- Example outputs will be saved to the current directory
