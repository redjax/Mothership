# 🛸 Mothership <!-- omit in toc -->

<!-- Repo header image -->
<p align="center">
  <img src=".assets/img/mothership.jpg" alt="Mothership repo img" width="300">
</p>

<table align="center">
  <tr>
    <th>Submodule Metadata Refreshed</th>
  </tr>

  <tr align="center">
    <td><!--LAST_UPDATED-->2026-02-23 01:53 UTC<!--END_LAST_UPDATED--></td>
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

Mothership is a "meta" repository that brings together my core machine scripts, configurations, and dotfiles. Each project is a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), an independent repository connected here to form a unified hub for managing my development environment.

Clone this repository, then pull in the "fleet" with `git submodule update --init --recursive`.

## Table of Contents <!-- omit in toc -->

- [Purpose](#purpose)
- [Usage](#usage)
- [Submodules](#submodules)
  - [Deploying submodules](#deploying-submodules)
    - [Python deployment script](#python-deployment-script)
  - [Updating submodules](#updating-submodules)
  - [Adding submodules](#adding-submodules)
  - [Removing submodules](#removing-submodules)
  - [Change submodule remote](#change-submodule-remote)
  - [Move a submodule in the repository](#move-a-submodule-in-the-repository)
- [Taskfile tasks](#taskfile-tasks)
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
| Ansible           | https://github.com/redjax/Ansible           | My Ansible monorepo, with collections, roles, & playbooks for managing my homelab.                                                                                                                                                                                 |
| docker_templates  | https://github.com/redjax/                  | A large repository containing many Docker/Docker Compose containers for services I've self-hosted.                                                                                                                                                                 |
| dotfiles          | https://github.com/redjax/dotfiles          | My Linux dotfiles, managed with Chezmoi.                                                                                                                                                                                                                           |
| emacs             | https://github.com/redjax/emacs             | My Emacs configuration.                                                                                                                                                                                                                                            |
| git_dir           | https://github.com/redjax/git_dir           | My `~/git` directory as a repository.                                                                                                                                                                                                                              |
| helix             | https://github.com/redjax/helix             | My Helix editor configuration.                                                                                                                                                                                                                                     |
| neovim            | https://github.com/redjax/neovim            | A repository containing my neovim configuration(s), plus management scripts & cross-platform support.                                                                                                                                                              |
| Notetkr           | https://github.com/redjax/Notetkr           | Go app for taking notes/journal entries in the terminal.                                                                                                                                                                                                           |
| PowershellModules | https://github.com/redjax/PowershellModules | Powershell modules I've written for work or personal use. I don't generally publish them, I just copy/paste or download them to my $PATH.                                                                                                                          |
| PowershellProfile | https://github.com/redjax/PowershellProfile | My Powershell profile with custom modules & functions.                                                                                                                                                                                                             |
| syst              | https://github.com/redjax/syst              | A "swiss army knife" CLI utility written in Go.                                                                                                                                                                                                                    |
| system_scripts    | https://github.com/redjax/Mothership        | A repository I've been adding to for many years (despite what the commit history shows), contains many scripts I've created or straight up copied (where legal, thank you to everyone who figured things out before me!) for multiple versions of Linux & Windows. |
| templates         | https://github.com/redjax/templates         | My templates monorepo, where I store copy/paste-able versions of pipelines & other code.                                                                                                                                                                           |
| Terraform         | https://github.com/redjax/Terraform         | My Terraform monorepo, where I store Terraform modules I write for myself.                                                                                                                                                                                         |
| Toolbelt          | https://github.com/redjax/Toolbelt          | Dynamic `README.md` file populated by a JSON file & Python script. An awesomelist-style collection of tools I use.                                                                                                                                                 |
| wezterm           | https://github.com/redjax/wezterm           | My Wezterm configuration.                                                                                                                                                                                                                                          |

### Deploying submodules

The Mothership can deploy submodules to paths on the filesystem by "cloning" the submodule. This initializes a standalone repository with the Mothership repository's path as its remote.

For example, to deploy the [`git_dir` module](./modules/git_dir/) to `~/git`:

```shell
git clone . ~/git
```

If you `cd ~/git` and run `git remote -v`, you will see the remote is the local Mothership repository's path:

```shell
git remote -v
origin  /path/to/Mothership/modules/git_dir/. (fetch)
origin  /path/to/Mothership/modules/git_dir/. (push)
```

You can leave this configuration as-is, so you will need to [update the Mothership's submodules](#updating-submodules) before doing `git pull` to update the local repository. This centralizes updates, and can help control which version is checked out locally, which can be useful for app configurations.

You can also change the remote back to the module's original repository. For example, set the `~/git` repository's remote back to [`git@github.com:redjax/git_dir.git`](https://github.com/redjax/git_dir.git):

```shell
git remote set-url origin "git@github.com:redjax/git_dir.git"
git checkout main
```

#### Python deployment script

The [`do_deployment.py` script](./scripts/deploy/do_deployment.py) can clone repositories to paths on the host, automating the process of cloning out of the Mothership repository and optionally setting the remote back to the submodule's origin.

Start by creating a `deploy.json` file (see the [`example.deploy.json` file for the structure](./example.deploy.json)):

```json
{
    "repositories": [
        {
            "name": "",
            "target": "",
            "branch": "",
            "mothership_remote": false
        }
    ]
}
```

- `name` should match one of the submodule paths in the [`modules/` directory](./modules/).
- `target` is the path on the current machine where you want the cloned repository to exist.
- `branch` (default should be `main`) sets the branch to checkout after cloning.
- `mothership_remote` is a boolean value. When `true`, the submodule's remote will be the path where you cloned Mothership (i.e. `~/Mothership`).
  - If you leave `"mothership_remote": true`, the cloned repository will be pointed back at the Mothership directory.
  - This means to pull updates, you need to `cd` back to the Mothership remote and [update the submodules](#updating-submodules), then `cd` to the cloned repository and run `git pull`.
  - This can help to control updates to configurations; you won't accidentally pull changes until you switch back to the Mothership repository and pull the submodule.

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

## Taskfile tasks

The [`Taskfile.yml` file](./Taskfile.yml) defines tasks/automations for [`go-task/task`](https://github.com/go-task/task). This allows for powerful automation, and can be used locally or in pipelines.

To see a list of tasks that can be run, use:

```shell
task -l
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

