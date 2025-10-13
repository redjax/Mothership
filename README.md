# Mothership <!-- omit in toc -->

<!-- Repo header image -->
<p align="center">
  <img src=".assets/img/mothership.jpg" alt="Mothership repo img" width="300">
</p>

<table align="center">
  <tr>
    <th>Submodule Metadata Refreshed</th>
  </tr>

  <tr align="center">
    <td><!--LAST_UPDATED-->2025-10-13 01:15 UTC<!--END_LAST_UPDATED--></td>
  </tr>
</table>

<!-- Git Badges -->
<p align="center">
  <a href="https://github.com/redjax/Mothership">
    <img alt="Created At" src="https://img.shields.io/github/created-at/redjax/Mothership">
  </a>  
  <a href="https://github.com/redjax/Mothership/commit">
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/redjax/Mothership">
  </a>
  <a href="https://github.com/redjax/Mothership/commit">
    <img alt="Commits this year" src="https://img.shields.io/github/commit-activity/y/redjax/Mothership">
  </a>
  <a href="https://github.com/redjax/Mothership">
    <img alt="Repo size" src="https://img.shields.io/github/repo-size/redjax/Mothership">
  </a>
  <!-- ![GitHub Latest Release](https://img.shields.io/github/release-date/redjax/Mothership) -->
  <!-- ![GitHub commits since latest release](https://img.shields.io/github/commits-since/redjax/Mothership/latest) -->
  <!-- ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/redjax/Mothership/tests.yml) -->
</p>

---

This is a "meta" repository for all of my machine scripts, configurations, & dotfiles.

Each repository is a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), its own independent repository that is "joined" here in an overarching repository that groups my most important repositories for computer management.

## Table of Contents <!-- omit in toc -->

- [Purpose](#purpose)
- [Usage](#usage)
- [Submodules](#submodules)
  - [Updating submodules](#updating-submodules)
  - [Adding submodules](#adding-submodules)
  - [Removing submodules](#removing-submodules)
  - [Change submodule remote](#change-submodule-remote)
  - [Move a submodule in the repository](#move-a-submodule-in-the-repository)
- [Troubleshooting](#troubleshooting)
  - [Submodule updates in pipeline not applied locally](#submodule-updates-in-pipeline-not-applied-locally)
- [Links](#links)

## Purpose

Honestly, I'm not quite sure yet. I'm testing out submodules, and thought it might be convenient to have all the repos I clone on my main machine in one "mothership" configuration. Maybe I'll write scripts to keep this up to date as a sort of backup, maybe it will just serve as a map to the other repositories, maybe it'll actually be useful!

I'll probably edit this section to give the project a focus at some point.

## Usage

Clone the repository and initialize submodules:

```bash
git clone git@github.com:redjax/Mothership # or https://github.com/redjax/Mothership.git
cd Mothership
git submodule update --init --recursive
```

Alternatively, you can clone & initialize in 1 step:

```bash
git clone --recurse-submodules <mothership-repo-url>
```

If you want to always pull submodule changes when they are updated, set the repository's `submodule.recurse` to `true`:

```bash
git config submodule.recurse true
```

## Submodules

Table of the submodules found in the [modules/ directory](./modules/)

| Name              | Repository                                  | Description                                                                                                                                                                                                                                                        |
| ----------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ansible_homelab   | https://github.com/redjax/ansible_homelab   | My Ansible monorepo, with collections, roles, & playbooks for managing my homelab.                                                                                                                                                                                 |
| docker_templates  | https://github.com/redjax/                  | A large repository containing many Docker/Docker Compose containers for services I've self-hosted.                                                                                                                                                                 |
| dotfiles          | https://github.com/redjax/dotfiles          | My Linux dotfiles, managed with Chezmoi.                                                                                                                                                                                                                           |
| emacs             | https://github.com/redjax/emacs             | My Emacs configuration.                                                                                                                                                                                                                                            |
| helix             | https://github.com/redjax/helix             | My Helix editor configuration.                                                                                                                                                                                                                                     |
| neovim            | https://github.com/redjax/neovim            | A repository containing my neovim configuration(s), plus management scripts & cross-platform support.                                                                                                                                                              |
| PowershellModules | https://github.com/redjax/PowershellModules | Powershell modules I've written for work or personal use. I don't generally publish them, I just copy/paste or download them to my $PATH.                                                                                                                          |
| PowershellProfile | https://github.com/redjax/PowershellProfile | My Powershell profile with custom modules & functions.                                                                                                                                                                                                             |
| syst              | https://github.com/redjax/syst              | A "swiss army knife" CLI utility written in Go.                                                                                                                                                                                                                    |
| system_scripts    | https://github.com/redjax/Mothership        | A repository I've been adding to for many years (despite what the commit history shows), contains many scripts I've created or straight up copied (where legal, thank you to everyone who figured things out before me!) for multiple versions of Linux & Windows. |
| templates         | https://github.com/redjax/templates         | My templates monorepo, where I store copy/paste-able versions of pipelines & other code.                                                                                                                                                                           |
| Terraform         | https://github.com/redjax/Terraform         | My Terraform monorepo, where I store Terraform modules I write for myself.                                                                                                                                                                                         |
| wezterm           | https://github.com/redjax/wezterm           | My Wezterm configuration.                                                                                                                                                                                                                                          |

### Updating submodules

Run this command to recursively pull the `main` branch of each submodule:

```bash
git submodule foreach git pull origin main
```

### Adding submodules

```bash
git submodule add https://github.com/youruser/repo_name.git local/path/to/repo_name
```

### Removing submodules

```bash
git submodule deinit -f local/path/to/repo_name
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

### Submodule updates in pipeline not applied locally

When the [pipeline that updates submodules](./.github/workflows/update-submodules.yml) runs and pulls changes on the remote, you need to also pull the submodule changes locally. This can be done with `git pull --recurse-submodules`, or you can set the local repo to always pull submodule changes on a `git pull` with:

```bash
git config submodule.recurse true
```

## Links

- [Git docs: submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [FreeCodeCamp: How to use Git submodules - explained with examples](https://www.freecodecamp.org/news/how-to-use-git-submodules/)
- [Atlassian docs: Git submodules](https://www.atlassian.com/git/tutorials/git-submodule)
- [HowToGeek: What are submodules, and how do you use them?](https://www.howtogeek.com/devops/what-are-git-submodules-and-how-do-you-use-them/)
