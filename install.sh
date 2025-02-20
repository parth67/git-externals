#!/bin/bash

set -e  # Exit on error

# Repository URL
REPO_URL="https://raw.githubusercontent.com/parth67/git-externals/main"

# Installation Paths
BIN_DIR="/usr/local/bin"
MAN_DIR="/usr/local/share/man/man1"
BASH_COMPLETION_DIR="/etc/bash_completion.d"
ZSH_COMPLETION_DIR="$HOME/.zsh/completions"

echo "🔹 Installing git-externals..."

# Ensure required tools are available
command -v curl >/dev/null 2>&1 || { echo "❌ curl is required but not installed. Aborting."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git is required but not installed. Aborting."; exit 1; }

# Download and install the main script
echo "📥 Downloading git-externals.py..."
sudo curl -sSL "$REPO_URL/git-externals.py" -o "$BIN_DIR/git-externals"
sudo chmod +x "$BIN_DIR/git-externals"

# Download and install the man page
echo "📖 Installing man page..."
sudo curl -sSL "$REPO_URL/git-externals.1" -o "$MAN_DIR/git-externals.1"
sudo mandb >/dev/null 2>&1 || echo "⚠️ mandb update skipped (not available)."

# Install Bash completion
if [ -d "$BASH_COMPLETION_DIR" ]; then
    echo "🖥️ Installing Bash auto-completion..."
    sudo curl -sSL "$REPO_URL/completion/bash/bash_completion.sh" -o "$BASH_COMPLETION_DIR/git-externals"
    sudo chmod +x "$BASH_COMPLETION_DIR/git-externals"
    source "$BASH_COMPLETION_DIR/git-externals"
fi

# Install Zsh completion
if [ -d "$ZSH_COMPLETION_DIR" ]; then
    echo "🖥️ Installing Zsh auto-completion..."
    mkdir -p "$ZSH_COMPLETION_DIR"
    curl -sSL "$REPO_URL/completion/zsh/_zsh_completion" -o "$ZSH_COMPLETION_DIR/_git-externals"
    echo 'fpath=("$HOME/.zsh/completions" $fpath)' >> ~/.zshrc
    echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
    source ~/.zshrc
fi

echo "✅ Installation complete!"
echo "Run 'git externals --help' to get started."
