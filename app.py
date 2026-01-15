import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from github_tools import GitHubTools
from agents import PlannerAgent, ExecutorAgent

# Load environment variables
load_dotenv()

app = FastAPI(title="GitHub PR Review Agent API")

class ReviewRequest(BaseModel):
    repo: str
    pr_number: int
    dry_run: bool = False
    language: str = "pt-BR"
    max_tokens: int = 2000


@app.post("/review")
async def review_pr(request: ReviewRequest):
    """
    Review a GitHub Pull Request.
    """
    repo = request.repo
    pr_number = request.pr_number
    
    # 1. Initialize Tools
    try:
        gh_tools = GitHubTools()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Fetch Diff
    diff_content = gh_tools.get_pr_diff(repo, pr_number)
    
    if "Error fetching PR diff" in diff_content:
         raise HTTPException(status_code=400, detail=diff_content)

    # 3. Planner Step
    planner = PlannerAgent()
    plan = planner.plan_review(diff_content, language=request.language, max_tokens=request.max_tokens)
    
    # 4. Executor Step
    executor = ExecutorAgent()
    review_comment = executor.execute_review(diff_content, plan, language=request.language, max_tokens=request.max_tokens)
    
    # 5. Post to GitHub
    if not request.dry_run:
        result = gh_tools.post_comment(repo, pr_number, review_comment)
    else:
        result = "Dry run: Comment not posted."

    
    return {
        "status": "success",
        "plan": plan,
        "review": review_comment,
        "github_response": result
    }

@app.get("/")
def read_root():
    return {"message": "GitHub PR Review Agent API is running."}
