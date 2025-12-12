## Branch Naming Guidelines

### Branch Types
Branches should follow one of the following formats:

- **main**: The main production branch, always containing stable, production-ready code.
- **trunk**: The primary development branch where all features and fixes are merged before being pushed to `main`.
- **fix**: A branch for hotfixes or urgent bug fixes..
- **issueX**: A branch created for each specific issue. Named as `issueX`, where `X` is the number of the issue. Example: `issue42` for issue number 42.

### Branch Naming Format
- **For issue-specific branches**:  
  `issueX`  
  Example: `issue42` for issue number 42.

### Rules
- Always create a branch from `trunk` or the most recent stable commit.
- Never work directly in `main` or `trunk`; always create a separate branch for any work.
- Ensure that branch names are descriptive and correspond to the task or issue they are addressing.
- Use lowercase letters and separate words with hyphens (`-`), no spaces or special characters.
- Once the work for an **issue branch** (`issueX`) has been completed and merged into `trunk`, **delete the branch** to keep the repository clean and avoid clutter.
