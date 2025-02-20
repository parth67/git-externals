# **git-externals** 🚀  
*A simple tool to manage external Git repositories within your project.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  
[![GitHub stars](https://img.shields.io/github/stars/parth67/git-externals?style=social)](https://github.com/parth67/git-externals)  
[![GitHub issues](https://img.shields.io/github/issues/parth67/git-externals.svg)](https://github.com/parth67/git-externals/issues)  

---

## **📖 Overview**
`git-externals` is a **Git subcommand** that helps manage external repositories within your project. It provides an alternative to SVN externals, allowing you to keep dependencies in a structured, Git-friendly way.

✅ **Supports external repositories** with branch or commit-based tracking  
✅ **Clones repositories into a hidden directory** to keep your workspace clean  
✅ **Creates symbolic links** to reference externals from your project  
✅ **Auto-completion for Bash & Zsh**  
✅ **Works on Linux & macOS**  

---

## **📥 Installation**
### **🔹 One-line install (via `curl`)**
```sh
curl -sSL https://raw.githubusercontent.com/parth67/git-externals/main/install.sh | bash
```
or using `wget`:
```sh
wget -qO- https://raw.githubusercontent.com/parth67/git-externals/main/install.sh | bash
```

### **🔹 Manual Installation**
1. **Clone the repository**  
   ```sh
   git clone https://github.com/parth67/git-externals.git
   cd git-externals
   ```
2. **Run the installation script**  
   ```sh
   ./install.sh
   ```

---

## **🚀 Usage**
`git-externals` provides multiple subcommands to manage your external repositories.

### **🔹 Add an External Repository**
```sh
git externals add <name> <url> <path> --branch <branch>
```
or pin to a commit:
```sh
git externals add <name> <url> <path> --revision <commit-hash>
```
Example:
```sh
git externals add fw git@bitbucket.org:user/firmware.git fw --branch main
```

### **🔹 Update an External Repository**
Change the branch or commit reference for an existing external.
```sh
git externals update <name> --branch <new-branch>
git externals update <name> --revision <new-commit-hash>
```
Example:
```sh
git externals update fw --branch develop
```

### **🔹 Remove an External Repository**
```sh
git externals remove <name>
```
Example:
```sh
git externals remove fw
```

### **🔹 List All Externals**
```sh
git externals list
```

### **🔹 Sync External Repositories**
Clone or update all externals.
```sh
git externals sync
```

### **🔹 Help**
```sh
git externals --help
```

---

## **🛠 Configuration**
Externals are defined in a JSON configuration file (`externals.json`):

```json
{
  "externals": [
    {
      "name": "repo1",
      "url": "https://github.com/parth67/git-externals.git",
      "path": "git-externals",
      "branch": "main",
      "revision": "aaderad",
      "description": "This repo contains git-externals helper script."
    }
  ]
}
```
- Either **branch** or **revision** is required (revision takes priority).
- The **path** is relative to the project root.
- The external repositories are stored inside `.externals/` and symlinked to the specified `path`.

---

## **🎯 Auto-Completion**
Auto-completion for `git externals` is available for **Bash** and **Zsh**.

### **🔹 Enable Bash Completion**
```sh
source /etc/bash_completion.d/git-externals
```
or add to `.bashrc`:
```sh
echo "source /etc/bash_completion.d/git-externals" >> ~/.bashrc
source ~/.bashrc
```

### **🔹 Enable Zsh Completion**
```sh
mkdir -p ~/.zsh/completions
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
autoload -Uz compinit && compinit
source ~/.zshrc
```

---

## **📜 Man Page**
You can access the manual using:
```sh
man git-externals
```

---

## **🤝 Contributing**
We welcome contributions! Feel free to fork the repository, submit issues, or create pull requests.

### **🔹 Clone the repo & contribute**
```sh
git clone https://github.com/parth67/git-externals.git
cd git-externals
```

1. **Create a new branch**  
   ```sh
   git checkout -b feature/new-feature
   ```
2. **Make changes & commit**  
   ```sh
   git commit -am "Added new feature"
   ```
3. **Push & create a pull request**  
   ```sh
   git push origin feature/new-feature
   ```

---

## **📝 License**
This project is licensed under the [MIT License](LICENSE).

---

## **📩 Support**
Having issues? Feel free to open an [issue](https://github.com/parth67/git-externals/issues) or reach out.

---

### **🚀 Now You're Ready to Manage Your Git Externals Efficiently!** 🎯  
Would you like a **Homebrew package** next? 😊