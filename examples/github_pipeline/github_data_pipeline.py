"""
GitHub Data Pipeline Example
A simple ETL (Extract, Transform, Load) pipeline for GitHub repository data
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any
import os

try:
    from github import Github
except ImportError:
    print("PyGithub not installed. Install with: pip install PyGithub")
    exit(1)


class GitHubDataPipeline:
    """
    A data pipeline for extracting, transforming, and loading GitHub data.
    """

    def __init__(self, token: str = None):
        """
        Initialize the GitHub API client.
        
        Args:
            token: GitHub personal access token (optional, uses unauthenticated if not provided)
        """
        if token:
            self.github = Github(token)
        else:
            self.github = Github()
        self.extracted_data = []
        self.transformed_data = []

    def extract_repository_data(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Extract data from a GitHub repository.
        
        Args:
            repo_owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            Dictionary containing repository metadata
        """
        print(f"📥 Extracting data from {repo_owner}/{repo_name}...")
        
        try:
            repo = self.github.get_user(repo_owner).get_repo(repo_name)
            
            repo_data = {
                "name": repo.name,
                "owner": repo.owner.login,
                "url": repo.html_url,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "watchers": repo.watchers_count,
                "language": repo.language,
                "created_at": str(repo.created_at),
                "updated_at": str(repo.updated_at),
                "is_fork": repo.fork,
                "open_issues": repo.open_issues_count,
                "topics": repo.get_topics(),
                "license": repo.license.name if repo.license else "None",
            }
            
            self.extracted_data.append(repo_data)
            print(f"✓ Successfully extracted repository data")
            return repo_data
            
        except Exception as e:
            print(f"✗ Error extracting repository: {str(e)}")
            return None

    def extract_issues_data(self, repo_owner: str, repo_name: str, 
                          state: str = "all", limit: int = 30) -> List[Dict[str, Any]]:
        """
        Extract issues data from a repository.
        
        Args:
            repo_owner: Repository owner username
            repo_name: Repository name
            state: Issue state ("open", "closed", "all")
            limit: Maximum number of issues to extract
            
        Returns:
            List of issue dictionaries
        """
        print(f"📥 Extracting issues from {repo_owner}/{repo_name}...")
        
        try:
            repo = self.github.get_user(repo_owner).get_repo(repo_name)
            issues = repo.get_issues(state=state)
            
            issues_data = []
            for i, issue in enumerate(issues):
                if i >= limit:
                    break
                    
                issue_dict = {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": str(issue.created_at),
                    "updated_at": str(issue.updated_at),
                    "comments": issue.comments,
                    "author": issue.user.login if issue.user else "Unknown",
                    "labels": [label.name for label in issue.labels],
                }
                
                issues_data.append(issue_dict)
            
            self.extracted_data.extend(issues_data)
            print(f"✓ Extracted {len(issues_data)} issues")
            return issues_data
            
        except Exception as e:
            print(f"✗ Error extracting issues: {str(e)}")
            return []

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw GitHub data into a standardized format.
        
        Args:
            data: Raw data from GitHub API
            
        Returns:
            Transformed data dictionary
        """
        transformed = {
            "extraction_timestamp": datetime.now().isoformat(),
            "source": "github_api",
            **data
        }
        
        # Add computed fields
        if "stars" in data:
            transformed["popularity_score"] = (
                data.get("stars", 0) * 0.5 + 
                data.get("forks", 0) * 0.3 + 
                data.get("watchers", 0) * 0.2
            )
        
        return transformed

    def load_to_json(self, filename: str = "github_data.json") -> str:
        """
        Load transformed data to JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to created file
        """
        print(f"💾 Loading data to {filename}...")
        
        output_data = [self.transform_data(item) for item in self.extracted_data]
        
        filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
        
        with open(filepath, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"✓ Data loaded to {filepath}")
        return filepath

    def load_to_csv(self, filename: str = "github_data.csv") -> str:
        """
        Load transformed data to CSV file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to created file
        """
        print(f"💾 Loading data to {filename}...")
        
        if not self.extracted_data:
            print("✗ No data to load")
            return None
        
        filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
        
        # Get all unique keys
        all_keys = set()
        for item in self.extracted_data:
            all_keys.update(item.keys())
        
        fieldnames = sorted(list(all_keys))
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in self.extracted_data:
                # Convert lists/dicts to strings for CSV
                row = {}
                for key in fieldnames:
                    value = item.get(key, "")
                    if isinstance(value, (list, dict)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                writer.writerow(row)
        
        print(f"✓ Data loaded to {filepath}")
        return filepath


def main():
    """
    Example usage of the GitHub Data Pipeline
    """
    print("=" * 60)
    print("GitHub Data Pipeline Example")
    print("=" * 60)
    
    # Initialize pipeline (no auth token = public data only)
    pipeline = GitHubDataPipeline()
    
    # Example 1: Extract repository data
    print("\n[EXAMPLE 1] Extracting Repository Data")
    print("-" * 60)
    repo_data = pipeline.extract_repository_data("microsoft", "vscode")
    if repo_data:
        print(f"Repository: {repo_data['name']}")
        print(f"Stars: {repo_data['stars']}")
        print(f"Language: {repo_data['language']}")
    
    # Example 2: Extract issues data
    print("\n[EXAMPLE 2] Extracting Issues Data")
    print("-" * 60)
    issues = pipeline.extract_issues_data("microsoft", "vscode", state="open", limit=10)
    print(f"Found {len(issues)} open issues")
    
    # Example 3: Load to JSON
    print("\n[EXAMPLE 3] Loading to JSON")
    print("-" * 60)
    json_file = pipeline.load_to_json("github_example_data.json")
    
    # Example 4: Load to CSV
    print("\n[EXAMPLE 4] Loading to CSV")
    print("-" * 60)
    csv_file = pipeline.load_to_csv("github_example_data.csv")
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)
    
    # Display summary
    print(f"\nSummary:")
    print(f"  • Total records extracted: {len(pipeline.extracted_data)}")
    print(f"  • JSON output: {json_file}")
    print(f"  • CSV output: {csv_file}")


if __name__ == "__main__":
    main()
