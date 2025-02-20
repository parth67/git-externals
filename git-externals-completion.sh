
#!/bin/bash

_git_externals() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="sync add update remove list help"

    case "${prev}" in
        add)
            COMPREPLY=($(compgen -W "$(git remote -v | awk '{print $2}' | uniq)" -- "${cur}"))
            return 0
            ;;
        update|remove)
            externals=$(jq -r '.externals[].name' externals.json 2>/dev/null)
            COMPREPLY=($(compgen -W "${externals}" -- "${cur}"))
            return 0
            ;;
        *)
            COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
            return 0
            ;;
    esac
}

complete -F _git_externals git-externals
