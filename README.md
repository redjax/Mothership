# Mothership <!-- omit in toc -->

<!-- Repo header image -->
<p align="center">
  <img src=".assets/img/mothership.jpg" alt="Mothership repo img" width="300">
</p>

This is a "meta" repository for all of my machine scripts, configurations, & dotfiles.

Each repository is a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), its own independent repository that is "joined" here in an overarching repository that groups my most important repositories for computer management.date

## Table of Contents <!-- omit in toc -->

- [Usage](#usage)
- [Submodules](#submodules)
  - [Updating submodules](#updating-submodules)
  - [Adding submodules](#adding-submodules)
  - [Removing submodules](#removing-submodules)
  - [Change submodule remote](#change-submodule-remote)
  - [Move a submodule in the repository](#move-a-submodule-in-the-repository)
- [Troubleshooting](#troubleshooting)
- [Links](#links)

## Usage

Clone the repository and initialize submodules:

```bash
git clone git@github.com:redjax/MetaRepo # or https://github.com/redjax/MetaRepo.git
cd MetaRepo
git submodule update --init --recursive
```

Alternatively, you can clone & initialize in 1 step:

```bash
git clone --recurse-submodules <meta-repo-url>
```

## Submodules

### Updating submodules

Run this command to recursively pull the `main` branch of each submodule:

```bash
git submodule foreach git pull origin main
```

### Adding submodules

###Add a submodule

```bash
git submodule add https://github.com/youruser/repo_name.git local/path/to/repo_name
```

### Removing submodules

```bash
git submodule deinit local/path/to/repo_name
git rm local/path/to/repo_name
rm -rf .git/modules/local/path/to/repo_name

## Commit changes to MetaRepo
git commit -m "Remove local/path/to/repo_name submodule"
```

### Change submodule remote

Edit `.gitmodules` file, update the URL of the submodule, then run the following to update MetaRepo:

```bash
git submodule sync
git submodule update --init --recursive
```

### Move a submodule in the repository

The easiest method is to use `git mv`:

```bash
git mv old/path/to/submodule new/path/to/submodule
```

Doing this moves the submodule directory, updates the `.gitmodules` file with the new path, and adjusts internal Git config as needed.

After moving a submodule, commit like this:

```bash
git add .gitmodules
git add -u
git commit -m "Move submodule to new path"
```

## Troubleshooting

...

## Links

- [Git docs: submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [FreeCodeCamp: How to use Git submodules - explained with examples](https://www.freecodecamp.org/news/how-to-use-git-submodules/)
- [Atlassian docs: Git submodules](https://www.atlassian.com/git/tutorials/git-submodule)
- [HowToGeek: What are submodules, and how do you use them?](https://www.howtogeek.com/devops/what-are-git-submodules-and-how-do-you-use-them/)
