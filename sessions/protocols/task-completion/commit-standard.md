### Step 3: Commit and Merge

1. Stage all changes with `git add -A`
2. Commit with descriptive message

   {commit_style_guidance}

3. {merge_instruction}

   **IMPORTANT: Linear History Policy**
   The `{default_branch}` branch must maintain a linear history (no merge commits).
   Feature branches should be incorporated as a single commit:

   - **Single commit on feature branch**: Use fast-forward merge
     ```bash
     git checkout {default_branch}
     git merge --ff-only <feature-branch>
     ```
     If fast-forward fails (e.g., {default_branch} has diverged), rebase first:
     ```bash
     git checkout <feature-branch>
     git rebase {default_branch}
     git checkout {default_branch}
     git merge --ff-only <feature-branch>
     ```

   - **Multiple commits on feature branch**: Use squash merge
     ```bash
     git checkout {default_branch}
     git merge --squash <feature-branch>
     git commit -m "descriptive message for the squashed changes"
     ```

   If asking about merge:
   ```markdown
   [DECISION: Merge to {default_branch}]
   Would you like to merge this branch to {default_branch}?
   - YES: Merge to {default_branch} (maintaining linear history)
   - NO: Keep changes on feature branch

   Your choice:
   ```

4. {push_instruction}

   If asking about push:
   ```markdown
   [DECISION: Push to Remote]
   Would you like to push the changes to remote?
   - YES: Push to origin
   - NO: Keep changes local only

   Your choice:
   ```

5. Clean up feature branch

   After successfully merging and pushing:
   ```bash
   # Delete local feature branch
   git branch -d <feature-branch>

   # Delete remote feature branch (if it was pushed)
   git push origin --delete <feature-branch>
   ```

   Note: If the remote branch doesn't exist (never pushed), the delete command will fail harmlessly.