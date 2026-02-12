# GitHub Data Pipeline Example

A Python ETL (Extract, Transform, Load) pipeline for collecting and processing GitHub repository data.

## Features

- **Extract**: Fetch repository metadata and issues from GitHub API
- **Transform**: Standardize and enrich data with computed fields
- **Load**: Export data to JSON and CSV formats

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage (Public Data Only)

```python
from github_data_pipeline import GitHubDataPipeline

# Initialize pipeline without authentication
pipeline = GitHubDataPipeline()

# Extract repository data
repo_data = pipeline.extract_repository_data("microsoft", "vscode")

# Extract issues
issues = pipeline.extract_issues_data("microsoft", "vscode", state="open", limit=20)

# Load to files
pipeline.load_to_json("output.json")
pipeline.load_to_csv("output.csv")
```

### With Authentication (For Higher Rate Limits)

```python
# Get token from: https://github.com/settings/tokens
pipeline = GitHubDataPipeline(token="your_github_token_here")
```

## Running the Example

```bash
python github_data_pipeline.py
```

This will:
1. Extract data from the VSCode repository
2. Extract open issues
3. Output `github_example_data.json` and `github_example_data.csv` to Downloads folder

## Pipeline Components

### GitHubDataPipeline Class

#### Methods:

- **`extract_repository_data(owner, repo)`** - Extracts repository metadata
  - Stars, forks, language, creation date, etc.
  
- **`extract_issues_data(owner, repo, state="all", limit=30)`** - Extracts issues
  - Issue title, state, comments, author, labels
  
- **`transform_data(data)`** - Transforms raw data into standardized format
  - Adds timestamp, computes popularity score
  
- **`load_to_json(filename)`** - Exports data to JSON
  
- **`load_to_csv(filename)`** - Exports data to CSV

## Data Fields

### Repository Data
- name, owner, url, description
- stars, forks, watchers
- language, license
- created_at, updated_at
- is_fork, open_issues
- topics

### Issues Data
- number, title, state
- created_at, updated_at
- comments, author
- labels

## Authentication

For private repositories and higher API rate limits, use a GitHub Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Create a new token with `repo` scope
3. Pass it to the pipeline: `GitHubDataPipeline(token="your_token")`

Without authentication, you're limited to public data and ~60 requests/hour.

## API Rate Limits

- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 5,000 requests/hour

## Output Examples

### JSON Output
```json
[
  {
    "extraction_timestamp": "2024-02-11T10:30:00.123456",
    "source": "github_api",
    "name": "vscode",
    "owner": "microsoft",
    "stars": 150000,
    "popularity_score": 75500.0,
    ...
  }
]
```

### CSV Output
Plain text CSV with headers and data rows, easy to import into Excel, SQL databases, etc.

## Advanced Usage

### Custom Repository Analysis

```python
pipeline = GitHubDataPipeline()

# Extract data from multiple repos
repos = [
    ("torvalds", "linux"),
    ("python", "cpython"),
    ("golang", "go"),
]

for owner, repo in repos:
    data = pipeline.extract_repository_data(owner, repo)
    issues = pipeline.extract_issues_data(owner, repo, limit=50)

# Load everything to files
pipeline.load_to_json("multi_repo_analysis.json")
pipeline.load_to_csv("multi_repo_analysis.csv")
```

## Error Handling

The pipeline includes error handling for:
- Invalid repository/owner names
- API rate limiting
- Network errors
- Authentication failures

## Notes

- Timestamps are in ISO format
- Lists and complex objects are JSON-serialized in CSV export
- The popularity score is a weighted combination of stars, forks, and watchers
- Data is extracted in chronological order for issues

## License

MIT
