#!/bin/bash
# Sanctum OS Bash Configuration
# Theological shell prompt and environment

# ═══════════════════════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════════════════════

# Sanctum color palette
export SANCTUM_BG='\[
[truncated]
r █ SANCtum OS v1.0${RESET}"
    echo -e "${BORDERS}───────────────────────────────────
[truncated]
──────────┘${RESET}"
    echo ""
fi

# ═══════════════════════════════════════════════════════════════════════════════
# DAILY SCRIPTURE BANNER
# ═══════════════════════════════════════════════════════════════════════════════

# Run sanctum-quote on new terminal sessions (throttled)
_sanctum_banner_throttle() {
    local last_run_file="$HOME/.local/share/sanctum/last_banner"
    local current_time=$(date +%s)
    local last_run=0
    
    if [ -f "$last_run_file" ]; then
        last_run=$(cat "$last_run_file" 2>/dev/null || echo 0)
    fi
    
    local diff=$((current_time - last_run))
    
    # Show banner once per hour (3600 seconds)
    if [ $diff -gt 3600 ]; then
        mkdir -p "$HOME/.local/share/sanctum"
        echo "$current_time" > "$last_run_file"
        
        # Clear screen and show banner
        clear
        echo -e "${BG}"
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
        echo -e "${RESET}"
        
        # Show daily verse
        if command -v sanctum-quote &> /dev/null; then
            sanctum-quote 2>/dev/null
        fi
    fi
}

# Run banner on login shells
if [[ $- == *i* ]] && shopt -q login_shell 2>/dev/null; then
    _sanctum_banner_throttle
fi
