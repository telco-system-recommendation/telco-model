# How to Contribute to telco

Welcome to the team! We are excited to have you here. To ensure our project is clean, consistent, and easy to manage, we follow a set of contribution guidelines.

This document will guide you through our workflow, from creating a branch to merging your code.

## Table of Contents
- [How to Contribute to telco](#how-to-contribute-to-telco)
  - [Table of Contents](#table-of-contents)
  - [The Core Principle](#the-core-principle)
  - [Your First Contribution (The Workflow)](#your-first-contribution-the-workflow)
    - [Step 1: Get Your Task](#step-1-get-your-task)
    - [Step 2: Create Your Branch](#step-2-create-your-branch)
    - [Step 4: Push Your Branch to GitHub](#step-4-push-your-branch-to-github)
    - [Step 5: Open a Pull Request (PR)](#step-5-open-a-pull-request-pr)
    - [Step 6: Code Review \& Merge](#step-6-code-review--merge)
  - [Reference: Branch Naming Convention](#reference-branch-naming-convention)
  - [Reference: Commit Message Convention (Conventional Commits)](#reference-commit-message-convention-conventional-commits)
    - [💡 Good vs. Bad Commits](#-good-vs-bad-commits)
    - [Breaking Changes](#breaking-changes)
  - [Asking for Help](#asking-for-help)

---

## The Core Principle

> **All work is done on a feature branch. All code must be reviewed via a Pull Request (PR) before it is merged into the `main` branch.**

Directly committing to the `main` branch is blocked. This protects our codebase and ensures every change is reviewed by at least one other person.

---

## Your First Contribution (The Workflow)

Follow these steps to get your code from your brain to `main`.

### Step 1: Get Your Task

Find or create an **Issue** in our GitHub repository for the task you are working on. This helps us track what's being worked on and why.

### Step 2: Create Your Branch

All new work must be done on a new branch. We use a specific naming convention to keep our branches organized.

From the `main` branch, create your new branch.

```bash
# Make sure you are on the main branch and have the latest code
git checkout main
git pull

# Create your new branch
git checkout -b type/short-description

**See the [Branch Naming Convention](https://www.google.com/search?q=%23reference-branch-naming-convention) below for what `type` to use.**

**Good Examples:**

  * `feature/add-user-login-page`
  * `bugfix/fix-submit-button-crash`
  * `docs/update-readme-setup-guide`

### Step 3: Do the Work & Commit Your Changes

Make your code changes. As you save your work, you **must** use our commit message convention. This helps us create automatic changelogs and makes our history readable.

```bash
# Add your changed files
git add .

# Commit your changes with a clear message
git commit -m "type: description of your change"
```

**See the [Commit Message Convention](https://www.google.com/search?q=%23reference-commit-message-convention) below for details.**

**Good Examples:**

  * `git commit -m "feat: Add email and password fields to login form"`
  * `git commit -m "fix: Prevent crash when submit button is double-clicked"`

### Step 4: Push Your Branch to GitHub

Push your new branch up to the remote repository on GitHub.

```bash
git push origin feature/add-user-login-page
```

### Step 5: Open a Pull Request (PR)

1.  Go to our repository on GitHub.
2.  You will see a green button to **"Compare & create pull request"** for your new branch. Click it.
3.  Fill out the **Pull Request Template**.
      * Give it a clear title (it should follow the commit convention, e.g., `feat: Add user login page`).
      * Fill out the description, linking the issue it solves (e.g., "Closes \#123").
4.  Assign a reviewer from the team (or leave it for the team lead).

### Step 6: Code Review & Merge

A team member will review your code. They may leave comments or request changes.

  * **If changes are requested:** Make the new commits on the *same branch*. The Pull Request will update automatically.
  * **Once approved:** A team leader will **Squash and Merge** your PR into `main`. This combines all your commits into a single, clean commit on the `main` branch.

Your branch will be deleted automatically after merging. You can then pull the latest `main` branch and start on your next task\!

-----

## Reference: Branch Naming Convention

We use this format: **`type/short-description`**

  * **`type`**: What *kind* of change is this?
  * **`short-description`**: A few words (using hyphens) to describe the goal.

| Type | Description |
| :--- | :--- |
| **`feature`** | For adding a new feature or functionality. |
| **`bugfix`** | For fixing a bug that is broken. |
| **`docs`** | For changes to documentation (README, etc.). |
| **`refactor`** | For code changes that don't add a feature or fix a bug. |
| **`test`** | For adding or improving tests. |
| **`chore`** | For maintenance (updating packages, build scripts, etc.). |

-----

## Reference: Commit Message Convention (Conventional Commits)

We use the **Conventional Commits** standard. This is the rule for all commit messages.

Format: **`type: description`**

| Type | Description |
| :--- | :--- |
| **`feat`** | A new feature for the user. |
| **`fix`** | A bug fix for the user. |
| **`docs`** | Documentation-only changes. |
| **`style`** | Code style changes (formatting, missing semicolons, etc.). |
| **`refactor`** | A code change that neither fixes a bug nor adds a feature. |
| **`test`** | Adding missing tests or correcting existing tests. |
| **`chore`** | Changes to the build process, tooling, or dependencies. |

### 💡 Good vs. Bad Commits

  * **BAD:** `git commit -m "updated code"`

  * **BAD:** `git commit -m "fixed bug"`

  * **BAD:** `git commit -m "login page"`

  * **GOOD:** `git commit -m "feat: Add user login form with validation"`

  * **GOOD:** `git commit -m "fix: Correct password regex in validation logic"`

  * **GOOD:** `git commit -m "docs: Update API endpoints in README"`

### Breaking Changes

If your commit introduces a change that will break existing functionality, add a `!` after the type.

`feat!: Change user ID in database from integer to UUID`

-----

## Asking for Help

Don't ever get stuck\! If you have questions about the code, the workflow, or anything else:

1.  Leave a comment on your **GitHub Issue or Pull Request**.
2.  Ask in our team's **Whatsapp**.

We are all here to help each other succeed.
