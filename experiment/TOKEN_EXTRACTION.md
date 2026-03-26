# Token Extraction Implementation Notes

## Current Status

The `experiment/utils/isolation.py` file contains a placeholder `_extract_token_count()` method that always returns 0. This needs to be adapted for the actual OpenCode environment.

## OpenCode Token Storage

OpenCode stores token usage in a SQLite database at `~/.local/share/opencode/opencode.db`.

### Option 1: Query SQLite Database (Recommended)

After each agent run, query the OpenCode database for the most recent session's token usage:

```python
import sqlite3
from pathlib import Path

def get_last_session_tokens():
    """Query OpenCode database for last session's token usage."""
    db_path = Path.home() / ".local/share/opencode/opencode.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query for most recent session
    cursor.execute("""
        SELECT input_tokens, output_tokens, cache_read_tokens, cache_write_tokens
        FROM sessions
        ORDER BY created_at DESC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'input_tokens': row[0] or 0,
            'output_tokens': row[1] or 0,
            'cache_read_tokens': row[2] or 0,
            'cache_write_tokens': row[3] or 0,
        }
    return None
```

### Option 2: Parse `opencode stats` Output

Run `opencode stats` and parse the JSON output (if available) or text output:

```python
import subprocess
import re

def parse_opencode_stats():
    """Parse OpenCode stats command output."""
    result = subprocess.run(
        ["opencode", "stats", "--json"],  # If JSON flag exists
        capture_output=True,
        text=True,
        timeout=30
    )
    # Parse output for token counts
    # ...
```

### Option 3: Environment Variable Tracking

Set environment variables before running OpenCode that instruct it to log token usage to a specific file:

```python
env = os.environ.copy()
env["OPENCODE_TOKEN_LOG"] = str(temp_dir / "tokens.json")
```

(This would require OpenCode to support such a feature)

## Implementation Steps

1. **Investigate OpenCode database schema**: Run `sqlite3 ~/.local/share/opencode/opencode.db ".schema"` to see available tables and columns

2. **Test token extraction**: Create a simple test that runs OpenCode and extracts token counts

3. **Update `isolation.py`**: Replace the placeholder `_extract_token_count()` with actual implementation

4. **Validate**: Run a mock experiment to ensure token counts are captured correctly

## Testing Token Extraction

```bash
# Run a simple OpenCode command
echo "What is 2+2?" | opencode --no-tui

# Query the database for the last session
sqlite3 ~/.local/share/opencode/opencode.db "SELECT id, created_at, input_tokens, output_tokens FROM sessions ORDER BY created_at DESC LIMIT 1;"
```

## Next Steps

- [ ] Investigate OpenCode database schema
- [ ] Implement token extraction in `isolation.py`
- [ ] Test with a single task
- [ ] Validate against OpenCode stats
- [ ] Run full experiment
