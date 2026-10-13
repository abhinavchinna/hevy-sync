# hevy-sync

A lightweight Python script to back up and extract your workout history, routines, body measurements, and exercise templates from the [Hevy](https://hevy.com/) API directly into structured JSON.

## Features

- **Full Data Backup**: Exports workouts (with individual set and exercise details), routines, body measurements, and exercise templates.
- **Incremental Updates**: Merges existing JSON data so previous syncs are preserved without redundant downloads.
- **Configurable**: Run via CLI flags or load your API key seamlessly from `.env` or system environment variables.
- **Granular Controls**: Selectively skip endpoints using CLI flags (`--skip-workouts`, `--skip-routines`, etc.).

## Prerequisites

- Python 3.8 or higher
- A Hevy API Key (Hevy Pro is required for API access)
  - You can generate your key in the Hevy mobile app under **Settings > Developer** or on the [Hevy Web Settings](https://hevy.com/settings).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abhinavchinna/hevy-sync.git
   cd hevy-sync
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and paste your Hevy API key:
   ```env
   HEVY_API_KEY=your_actual_api_key_here
   ```

## Usage

### Basic Sync
Run the sync with default settings (saves output to `hevy_data.json`):
```bash
python sync_hevy.py
```

### Command-Line Options
You can also customize the output location or provide the API key directly:

```bash
# Save to custom file
python sync_hevy.py -o backups/my_workouts.json

# Pass API key explicitly via CLI
python sync_hevy.py --api-key <YOUR_KEY>

# Only sync workouts and measurements
python sync_hevy.py --skip-routines --skip-templates
```

### Full CLI Options

| Argument | Description | Default |
|---|---|---|
| `--api-key` | Hevy API Key | Reads from `HEVY_API_KEY` in environment / `.env` |
| `-o`, `--output` | Output JSON destination | `hevy_data.json` |
| `--skip-workouts` | Skip pulling workouts | `False` |
| `--skip-routines` | Skip pulling routines | `False` |
| `--skip-measurements` | Skip pulling body measurements | `False` |
| `--skip-templates` | Skip pulling exercise templates | `False` |

## Output Format

The output JSON has the following structure (see [`sample_data.json`](sample_data.json) for an example payload):

```json
{
  "workouts": {
    "<workout_id>": { ... }
  },
  "routines": {
    "<routine_id>": { ... }
  },
  "templates": [ ... ],
  "measurements": {
    "<date>": { ... }
  },
  "last_sync": "2026-10-13T22:00:00"
}
```

## License

MIT
