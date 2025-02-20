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


def load_config():
    """Load the externals.json configuration file."""
    if not os.path.exists(CONFIG_FILE):
        logging.error(f"Error: Configuration file '{CONFIG_FILE}' not found.")
        sys.exit(1)

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    """Save the externals.json file atomically."""
    temp_file = CONFIG_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(config, f, indent=4)
    os.rename(temp_file, CONFIG_FILE)  # Atomic write


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


def ensure_gitignore():
    """Ensure that .externals is gitignored."""
    gitignore_path = ".gitignore"
    ignore_entry = ".externals/\n"

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
        if ignore_entry not in lines:
            with open(gitignore_path, "a") as f:
                f.write(ignore_entry)
    else:
        with open(gitignore_path, "w") as f:
            f.write(ignore_entry)


def check_git_repository():
    """Check if the current directory is a Git repository."""
    if not os.path.isdir(".git"):
        logging.error("Error: Current directory is not a Git repository.")
        sys.exit(1)


def sync_externals():
    """Sync all external repositories."""
    check_git_repository()
    config = load_config()
    os.makedirs(EXTERNALS_DIR, exist_ok=True)

    for external in config.get("externals", []):
        name, url, path = external["name"], external["url"], external["path"]
        branch, revision = external.get("branch"), external.get("revision")
        repo_path = os.path.join(EXTERNALS_DIR, name)

        logging.info(f"Processing {name}...")

        if os.path.isdir(os.path.join(repo_path, ".git")):
            logging.info(f"Updating {name}...")
            run_command("git fetch --all", cwd=repo_path, silent=True)
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
        if os.path.exists(path) or os.path.islink(path):
            os.remove(path)
        os.symlink(repo_path, path)
        logging.info(f"External '{name}' linked at '{path}'.")

    ensure_gitignore()
    logging.info("Externals sync complete.")


def add_external(name, url, path, branch=None, revision=None):
    """Add a new external repository."""
    check_git_repository()
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
    check_git_repository()
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


def remove_external(name):
    """Remove an external repository."""
    check_git_repository()
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

    if os.path.exists(repo_path):
        run_command(f"rm -rf {repo_path}")

    logging.info(f"Removed external {name}.")


def list_externals():
    """List all configured externals."""
    check_git_repository()
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
