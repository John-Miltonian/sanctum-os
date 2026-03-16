#!/bin/zsh
# Sanctum OS Zsh Configuration
# Theological shell prompt and environment

# ═══════════════════════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════════════════════

# Sanctum color palette
local SANCTUM_BG='%{
[truncated]
s')  # Cardinal red
local C_GOLD='%F{178}'    # Byzantine gold
local C_SILVER='%F{250}'  # Silver
local C_DIM='%F{240}'     # Dim

local C_RESET='%f%b%u%s'

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

# Left prompt with cross symbol
PROMPT='${C_BG}${C_RED}  ${C_GOLD}%~${C_RESET}
[truncated]
zsh_async_init
fi

# Auto-suggest configuration
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=240'
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

# ═══════════════════════════════════════════════════════════════════════════════
# BINDINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Emacs bindings
bindkey -e

# Better history search
autoload -U up-line-or-beginning-search
autoload -U down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey "^[[A" up-line-or-beginning-search
bindkey "^[[B" down-line-or-beginning-search

# ═══════════════════════════════════════════════════════════════════════════════
# DAILY SCRIPTURE BANNER
# ═══════════════════════════════════════════════════════════════════════════════

_sanctum_banner_throttle() {
    local last_run_file="$HOME/.local/share/sanctum/last_banner"
    local current_time=$(date +%s)
    local last_run=0
    
    if [[ -f "$last_run_file" ]]; then
        last_run=$(cat "$last_run_file" 2>/dev/null || echo 0)
    fi
    
    local diff=$((current_time - last_run))
    
    # Show banner once per hour
    if [[ $diff -gt 3600 ]]; then
        mkdir -p "$HOME/.local/share/sanctum"
        echo "$current_time" > "$last_run_file"
        
        clear
        echo "${BG}"
        cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║    ███████╗ █████╗ ███╗   ██╗ ██████╗████████╗██╗   ██╗███╗   ███║
║    ██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██║   ██║████╗ ████║
║    ███████╗███████║██╔██╗ ██║██║        ██║   ██║   ██║██╔████╔██║
║    ╚════██║██╔══██║██║╚██╗██║██║        ██║   ██║   ██║██║╚██╔╝██║
║    ███████║██║  ██║██║ ╚████║╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║
║    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
        echo "${RESET}"
        
        if (( $+commands[sanctum-quote] )); then
            sanctum-quote 2>/dev/null
        fi
    fi
}

# Run on login
if [[ -o login ]]; then
    _sanctum_banner_throttle
fi

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETION
# ═══════════════════════════════════════════════════════════════════════════════

autoload -Uz compinit
compinit

zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
