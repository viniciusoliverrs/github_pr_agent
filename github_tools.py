import os
from github import Github
from github import Auth

class GitHubTools:
    def __init__(self, token=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN is not set")
        self.auth = Auth.Token(self.token)
        self.g = Github(auth=self.auth)

    def get_pr_diff(self, repo_name, pr_number):
        """Fetches the diff of a Pull Request."""
        try:
            repo = self.g.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            # getting the diff url content or using files
            # PyGithub doesn't give raw diff directly easily on the object, 
            # but we can iterate files or request the diff media type.
            # For simplicity in this agent, let's iterate files and get patches.
            
            diff_content = f"PR: {pr.title}\nDescription: {pr.body}\n\n"
            
            files = pr.get_files()
            for file in files:
                diff_content += f"--- {file.filename} ---\n"
                diff_content += f"{file.patch}\n\n"
            
            return diff_content
        except Exception as e:
            return f"Error fetching PR diff: {str(e)}"

    def post_comment(self, repo_name, pr_number, body):
        """Posts a comment on the Pull Request."""
        try:
            repo = self.g.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(body)
            return "Comment posted successfully."
        except Exception as e:
            return f"Error posting comment: {str(e)}"
