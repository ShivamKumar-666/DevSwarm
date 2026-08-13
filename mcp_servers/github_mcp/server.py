from mcp.server.fastmcp import FastMCP
from github import Github
import os

mcp = FastMCP("github-mcp")

# Initialize GitHub client
# In a real environment, this requires GITHUB_TOKEN environment variable.
github_token = os.environ.get("GITHUB_TOKEN")
if github_token:
    g = Github(github_token)
else:
    g = None
    print("Warning: GITHUB_TOKEN not set. GitHub API calls will fail.")

@mcp.tool()
def post_pr_comment(repo_name: str, pr_number: int, comment_body: str) -> str:
    """
    Posts a comment to a specific GitHub Pull Request.
    """
    if not g:
        return "Error: GitHub client not initialized (missing token)."
    
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(comment_body)
        return f"Successfully posted comment to PR #{pr_number}"
    except Exception as e:
        return f"Error posting comment: {str(e)}"

@mcp.tool()
def merge_pr(repo_name: str, pr_number: int, commit_message: str = "Merged by DevSwarm") -> str:
    """
    Merges a GitHub Pull Request.
    """
    if not g:
        return "Error: GitHub client not initialized (missing token)."
    
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        status = pr.merge(commit_message=commit_message)
        if status.merged:
            return f"Successfully merged PR #{pr_number}"
        else:
            return f"Failed to merge PR #{pr_number}: {status.message}"
    except Exception as e:
        return f"Error merging PR: {str(e)}"

if __name__ == "__main__":
    mcp.run()
