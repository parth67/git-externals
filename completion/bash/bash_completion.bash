# Bash completion script for git-externals

_git_externals() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Define available commands
    commands="sync add update remove list help"

    # Subcommands and their expected arguments
    case "${prev}" in
        add)
            # Complete repository name or URL when adding
            case "${COMP_CWORD}" in
                3) COMPREPLY=( $(compgen -W "$(ls -d */ 2>/dev/null)" -- "$cur") ) ;; # Suggest directories
                4) COMPREPLY=( $(compgen -W "--branch --revision" -- "$cur") ) ;; # Suggest options
            esac
            return 0
            ;;
        update)
            # Suggest configured external names for update
            COMPREPLY=( $(jq -r '.externals[].name' externals.json 2>/dev/null) )
            return 0
            ;;
        remove)
            # Suggest configured external names for removal
            COMPREPLY=( $(jq -r '.externals[].name' externals.json 2>/dev/null) )
            return 0
            ;;
    esac

    # Default completion for main commands
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${commands}" -- "$cur") )
        return 0
    fi
}

#complete -F _git_externals git-externals

