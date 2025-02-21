#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import argparse
import logging

# Configurable externals file (allows external modification)
CONFIG_FILE = os.getenv("GIT_EXTERNALS_FILE", "externals.json")
EXTERNALS_DIR = ".externals"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_git_root():
    """Get the root directory of the current Git repository."""
    try:
        result = subprocess.run("git rev-parse --show-toplevel", shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        logging.error("Error: Current directory is not a Git repository.")
        sys.exit(1)


def load_config():
    """Load the externals.json configuration file from the Git root."""
    git_root = get_git_root()
    config_file_path = os.path.join(git_root, CONFIG_FILE)
    if not os.path.exists(config_file_path):
        logging.error(f"Error: Configuration file '{config_file_path}' not found.")
        sys.exit(1)

    with open(config_file_path, "r") as f:
        return json.load(f)


def save_config(config):
    """Save the externals.json file atomically in the Git root."""
    git_root = get_git_root()
    config_file_path = os.path.join(git_root, CONFIG_FILE)
    temp_file = config_file_path + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(config, f, indent=4)
    os.rename(temp_file, config_file_path)  # Atomic write


def run_command(command, cwd=None, silent=False):
    """Run a shell command with error handling."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if not silent:
            logging.info(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running command: {command}")
        logging.error(e.stderr.strip())
        sys.exit(1)


def ensure_gitignore(symlinks):
    """Ensure that .externals and symlinks are gitignored."""
    git_root = get_git_root()
    gitignore_path = os.path.join(git_root, ".gitignore")
    ignore_entries = [".externals/\n"] + [f"{link}\n" for link in symlinks]

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
        with open(gitignore_path, "a") as f:
            for entry in ignore_entries:
                if entry not in lines:
                    f.write(entry)
    else:
        with open(gitignore_path, "w") as f:
            f.writelines(ignore_entries)


def check_git_repository():
    """Check if the current directory is a Git repository."""
    if not os.path.isdir(".git"):
        logging.error("Error: Current directory is not a Git repository.")
        sys.exit(1)


def sync_externals():
    """Sync all external repositories."""
    # check_git_repository()
    git_root = get_git_root()
    config = load_config()
    os.makedirs(os.path.join(git_root, EXTERNALS_DIR), exist_ok=True)
    symlinks = []

    for external in config.get("externals", []):
        name, url, path = external["name"], external["url"], external["path"]
        branch, revision = external.get("branch"), external.get("revision")
        if os.path.isabs(path):
            logging.error(f"Error: Path '{path}' is an absolute path. path attribute must be relative to the git root.")
            sys.exit(1)
        path = os.path.join(git_root, path)
        repo_path = os.path.join(git_root, EXTERNALS_DIR, name)

        logging.info(f"Processing {name}...")

        if os.path.isdir(os.path.join(repo_path, ".git")):
            logging.info(f"Updating {name}...")
            run_command("git pull --all", cwd=repo_path)
        else:
            logging.info(f"Cloning {name}...")
            clone_cmd = f"git clone {url} {repo_path}"
            if branch:
                clone_cmd += f" --branch {branch}"
            run_command(clone_cmd)

        # Checkout specific revision or branch
        if revision:
            run_command(f"git checkout {revision}", cwd=repo_path)
        elif branch:
            run_command(f"git checkout {branch}", cwd=repo_path)

        # Create symlink
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path) or os.path.islink(path):
            os.remove(path)
        os.symlink(repo_path, path)
        symlinks.append(path)
        logging.info(f"External '{name}' linked at '{os.path.relpath(path, git_root)}'.")

    ensure_gitignore(symlinks)
    logging.info("Externals sync complete.")


def add_external(name, url, path, branch=None, revision=None):
    """Add a new external repository."""
    # check_git_repository()
    config = load_config()

    if any(ext["name"] == name for ext in config.get("externals", [])):
        logging.error(f"Error: External '{name}' already exists.")
        sys.exit(1)

    new_entry = {"name": name, "url": url, "path": path}
    if branch:
        new_entry["branch"] = branch
    if revision:
        new_entry["revision"] = revision

    config["externals"].append(new_entry)
    save_config(config)

    logging.info(
        f"Added external {name}. Run 'git externals sync' to fetch it.")


def update_external(name, branch=None, revision=None):
    """Update an existing external repository's branch or revision."""
    # check_git_repository()
    config = load_config()

    for external in config.get("externals", []):
        if external["name"] == name:
            if branch:
                external["branch"] = branch
                # Remove revision if branch is updated
                external.pop("revision", None)
            if revision:
                external["revision"] = revision
                # Remove branch if revision is updated
                external.pop("branch", None)
            save_config(config)
            logging.info(
                f"Updated {name}: branch={branch}, revision={revision}")
            return

    logging.error(f"Error: External '{name}' not found.")
    sys.exit(1)


def remove_gitignore_entry(entry):
    """Remove an entry from .gitignore."""
    git_root = get_git_root()
    gitignore_path = os.path.join(git_root, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
        with open(gitignore_path, "w") as f:
            for line in lines:
                if line.strip() != entry.strip():
                    f.write(line)


def remove_external(name):
    """Remove an external repository."""
    # check_git_repository()
    config = load_config()
    updated_externals = [e for e in config.get(
        "externals", []) if e["name"] != name]

    if len(updated_externals) == len(config["externals"]):
        logging.error(f"Error: External '{name}' not found.")
        return

    config["externals"] = updated_externals
    save_config(config)

    repo_path = os.path.join(EXTERNALS_DIR, name)
    for external in config["externals"]:
        if external["name"] == name and os.path.islink(external["path"]):
            os.remove(external["path"])
            remove_gitignore_entry(external["path"])

    if os.path.exists(repo_path):
        run_command(f"rm -rf {repo_path}")

    logging.info(f"Removed external {name}.")


def list_externals():
    """List all configured externals."""
    # check_git_repository()
    config = load_config()
    externals = config.get("externals", [])

    if not externals:
        logging.info("No externals configured.")
        return

    logging.info("Configured externals:")
    for ext in externals:
        branch_info = f"(Branch: {ext['branch']})" if 'branch' in ext else ""
        revision_info = f"(Revision: {ext['revision']})" if 'revision' in ext else ""
        logging.info(
            f"  - {ext['name']} → {ext['url']} @ {ext['path']} {branch_info} {revision_info}")


def main():
    """Main function to handle CLI arguments using argparse."""
    parser = argparse.ArgumentParser(description="Manage git externals.")
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    subparsers.add_parser("sync", help="Sync all external repositories")

    add_parser = subparsers.add_parser("add", help="Add a new external repository")
    add_parser.add_argument("name", help="Unique identifier for the external repository")
    add_parser.add_argument("url", help="Git repository URL")
    add_parser.add_argument("path", help="Path where the repository should be linked")
    add_parser.add_argument("--branch", default=None, help="Branch to check out (optional)")
    add_parser.add_argument("--revision", default=None, help="Specific commit hash to check out (optional)")

    update_parser = subparsers.add_parser(
        "update", help="Update an external repository's branch or revision")
    update_parser.add_argument("name", help="The name of the external repository to update")
    update_parser.add_argument("--branch", default=None, help="Update to a different branch (optional)")
    update_parser.add_argument("--revision", default=None, help="Checkout a specific commit (optional)")

    remove_parser = subparsers.add_parser(
        "remove", help="Remove an external repository")
    remove_parser.add_argument("name", help="The name of the external repository to remove")

    subparsers.add_parser("list", help="List all configured external repositories")

    args = parser.parse_args()

    if args.command == "sync":
        sync_externals()
    elif args.command == "add":
        add_external(args.name, args.url, args.path,
                     args.branch, args.revision)
    elif args.command == "update":
        update_external(args.name, args.branch, args.revision)
    elif args.command == "remove":
        remove_external(args.name)
    elif args.command == "list":
        list_externals()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
