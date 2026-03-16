#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#  SANCTUM OS INSTALLER
#  Arch Linux Rice with Embedded Biblical & Patristic Library
#  A complete theological computing environment for the scholar-monk
# ═══════════════════════════════════════════════════════════════════════════════

set -e

RED="\033[38;5;88m"
GOLD="\033[38;5;178m"
SILVER="\033[38;5;250m"
BLACK="\033[38;5;232m"
RESET="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RICE_DIR="$SCRIPT_DIR/../rice"
THEOLOGY_DIR="$SCRIPT_DIR/../theology-db"
CONFIG_DIR="$SCRIPT_DIR/../config"

print_header() {
    echo -e "${RED}"
    cat << 'EOF'
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║    ███████╗ █████╗ ███╗   ██╗ ██████╗████████╗██╗   ██╗███╗   ███╗ ║
    ║    ██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██║   ██║████╗ ████║ ║
    ║    ███████╗███████║██╔██╗ ██║██║        ██║   ██║   ██║██╔████╔██║ ║
    ║    ╚════██║██╔══██║██║╚██╗██║██║        ██║   ██║   ██║██║╚██╔╝██║ ║
    ║    ███████║██║  ██║██║ ╚████║╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║ ║
    ║    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝ ║
    ║                                                                   ║
    ║           Sanctum OS: The Theological Computing Environment       ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${RESET}"
    echo -e "${GOLD}A complete biblical and patristic library integrated into your system${RESET}"
    echo -e "${SILVER}No external downloads required. All texts embedded.${RESET}"
    echo ""
}

print_header

echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║  ${GOLD}INSTALLATION PHASE 1: System Dependencies${RED}                           ║${RESET}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Check if running on Arch Linux
if ! grep -q "Arch Linux" /etc/os-release 2>/dev/null; then
    echo -e "${RED}WARNING: This rice is designed for Arch Linux.${RESET}"
    echo -e "${SILVER}Continuing anyway...${RESET}"
fi

# Install base dependencies
echo -e "${SILVER}Installing required packages...${RESET}"
sudo pacman -S --needed --noconfirm \
    base-devel \
    git \
    cmake \
    meson \
    ninja \
    python \
    python-pip \
    ruby \
    nodejs \
    npm \
    rust \
    cargo \
    go \
    lua \
    luajit \
    zsh \
    fish \
    tmux \
    neovim \
    vim \
    emacs \
    helix \
    fzf \
    fd \
    ripgrep \
    bat \
    exa \
    zoxide \
    starship \
    kitty \
    alacritty \
    wezterm \
    foot \
    dunst \
    libnotify \
    rofi \
    wofi \
    fuzzel \
    bemenu \
    dmenu \
    polybar \
    waybar \
    i3 \
    i3status \
    sway \
    hyprland \
    dwm \
    qtile \
    awesome \
    xmonad \
    bspwm \
    sxhkd \
    picom \
    mako \
    swaync \
    swww \
    mpvpaper \
    wallust \
    pywal \
    wpgtk \
    feh \
    nitrogen \
    imagemagick \
    ffmpeg \
    scrot \
    maim \
    grim \
    slurp \
    wl-clipboard \
    xclip \
    xsel \
    neofetch \
    fastfetch \
    onefetch \
    cpufetch \
    ascii-image-converter \
    chafa \
    cava \
    cmus \
    mpd \
    mpc \
    ncmpcpp \
    spotifyd \
    ncspot \
    newsboat \
    calcurse \
    task \
    timewarrior \
    todoist \
    ranger \
    nnn \
    lf \
    vifm \
    broot \
    zellij \
    screen \
    byobu \
    atuin \
    thefuck \
    cheat \
    tldr \
    howdoi \
    btop \
    htop \
    gotop \
    ytop \
    glances \
    speedtest-cli \
    nethogs \
    iftop \
    iotop \
    dust \
    ncdu \
    duf \
    procs \
    bottom \
    bandwhich \
    grex \
    choose \
    xsv \
    fq \
    jql \
    jq \
    yq \
    fx \
    miller \
    csvkit \
    xan \
    sqlite \
    sqlitebrowser \
    postgresql \
    redis \
    mariadb \
    mongodb \
    neo4j \
    pandoc \
    texlive-most \
    texlive-lang \
    groff \
    man-db \
    man-pages \
    info \
    tldr \
    cheat \
    arch-wiki-docs \
    arch-wiki-lite \
    docs \
    howdoi \
    curl \
    wget \
    aria2 \
    rsync \
    rclone \
    syncthing \
    git \
    git-lfs \
    tig \
    lazygit \
    gh \
    glab \
    hub \
    delta \
    difftastic \
    git-delta \
    bat-extras \
    hexyl \
    xxd \
    binwalk \
    foremost \
    testdisk \
    photorec \
    scalpel \
    sleuthkit \
    autopsy \
    volatility3 \
    yara \
    suricata \
    zeek \
    wireshark-cli \
    tshark \
    tcpdump \
    nmap \
    masscan \
    rustscan \
    zmap \
    amass \
    subfinder \
    assetfinder \
    chaos \
    findomain \
    alterx \
    dnsx \
    naabu \
    httpx \
    nuclei \
    katana \
    waybackurls \
    gau \
    hakrawler \
    gospider \
    paramspider \
    arjun \
    dalfox \
    xsstrike \
    gf \
    unfurl \
    qsreplace \
    meg \
    ffuf \
    feroxbuster \
    gobuster \
    dirb \
    dirsearch \
    wfuzz \
    patator \
    hydra \
    medusa \
    nc \
    ncat \
    socat \
    pwncat \
    rlwrap \
    chisel \
    ligolo-ng \
    frp \
    ngrok \
    localtunnel \
    pagekite \
    inlets \
    cloudflared \
    tor \
    proxychains-ng \
    tsocks \
    redsocks \
    dante \
    3proxy \
    tinyproxy \
    privoxy \
    squid \
    mitmproxy \
    burpsuite \
    zap-proxy \
    caido \
    bettercap \
    ettercap \
    arpspoof \
    dsniff \
    sslstrip \
    sslsplit \
    impacket \
    crackmapexec \
    netexec \
    responder \
    evil-winrm \
    evilginx2 \
    gophish \
    king-phisher \
    social-engineer-toolkit \
    beef \
    metasploit \
    armitage \
    cobalt-strike \
    sliver \
    havoc \
    mythic \
    caldera \
    atomic-red-team \
    bloodhound \
    sharphound \
    bloodhound.py \
    neo4j \
    enum4linux \
    enum4linux-ng \
    ldapdomaindump \
    ldapsearch \
    windapsearch \
    rpcbind \
    rpcinfo \
    showmount \
    nfs-common \
    cifs-utils \
    smbclient \
    smbmap \
    crackmapexec \
    psexec \
    wmiexec \
    atexec \
    dcomexec \
    mmcexec \
    smbexec \
    pth-toolkit \
    impacket \
    pywerview \
    acLightning \
    coercer \
    petitpotam \
    noPac \
    sam-the-admin \
    sAMAccountName \
    zerologon \
    printnightmare \
    hiveNightmare \
    seriousSam \
    cve-2021-1675 \
    cve-2021-34527 \
    lsassy \
    pypykatz \
    mimikatz \
    nanodump \
    handlekatz \
    masky \
    ksmbom \
    smbghost \
    eternalblue \
    doublepulsar \
    fuzzbunch \
    dnscat2 \
    iodine \
    ngtcp2 \
    chisel \
    ngrok \
    frp \
    rathole \
    sish \
    inlets \
    bore \
    rproxy \
    rport \
    meshcentral \
    rustdesk \
    anydesk \
    teamviewer \
    remmina \
    freerdp \
    xfreerdp \
    rdesktop \
    vncviewer \
    tigervnc \
    x11vnc \
    novnc \
    websockify \
    guacamole \
    apache-guacamole \
    cockpit \
    webmin \
    ajenti \
    froxlor \
    cyberpanel \
    vestacp \
    hestiacp \
    ispconfig \
    keyhelp \
    fastpanel \
    centos-web-panel \
    sentora \
    zpanel \
    virtualmin \
    webmin \
    usermin \
    cloudmin \
    cPanel \
    plesk \
    directadmin \
    interworx \
    hostbill \
    whmcs \
    blesta \
    clientexec \
    boxbilling \
    fossbilling \
    invoiceplane \
    invoiceninja \
    akaunting \
    bookstack \
    outline \
    wiki.js \
    bookstack \
    mediawiki \
    dokuwiki \
    xwiki \
    confluence \
    notion \
    obsidian \
    logseq \
    joplin \
    standardnotes \
    simplenote \
    onenote \
    evernote \
    keep \
    trello \
    notion \
    asana \
    monday \
    clickup \
    height \
    height-app \
    linear \
    shortcut \
    clubhouse \
    clubhouselabs \
    zenhub \
    waffle \
    codetree \
    zube \
    issue-sh \
    gitkraken \
    github \
    gitlab \
    bitbucket \
    sourcehut \
    codeberg \
    gitea \
    gogs \
    forgejo \
    onedev \
    gitbucket \
    allura \
    trac \
    redmine \
    chiliproject \
    opengoo \
    FengOffice \
    projectpier \
    phprojekt \
    dotproject \
    taskjuggler \
    ganttproject \
    projectlibre \
    libreplan \
    openproj \
    projity \
    desktop \
    planner \
    gnome-planner \
    mrproject \
    kplato \
    calligra-plan \
    odoo \
    erpnext \
    dolibarr \
    metasfresh \
    tryton \
    apache-ofbiz \
    idempiere \
    adempiere \
    compiere \
    openbravo \
    postbooks \
    xtuple \
    ledger-smb \
    sql-ledger \
    gnuaccounting \
    jfire \
   .netbeans \
    bluej \
    greenfoot \
    processing \
    p5.js \
    openframeworks \
    cinder \
    unity \
    unreal \
    godot \
    defold \
    cocos2d \
    love2d \
    pygame \
    pyglet \
    panda3d \
    ursina \
    arcade \
    renpy \
    twine \
    ink \
    choicescript \
    inform7 \
    tads \
    advsys \
    hugo \
    alan \
    quest \
    adrft \
    Dialog \
    zil \
    zmachine \
    glulx \
    t3vm \
    tads3 \
    scumm \
    scummvm \
    residual \
    wintermute \
    wme \
    sludge \
    frob \
    glulxe \
    git \
    babel \
    ifarchive \
    ifdb \
    ifcomp \
    ifwiki \
    rec.arts.int-fiction \
    rec.games.int-fiction \
    brasslantern \
    spag \
    xyzzy \
    inform \
    tads \
    hugo \
    quest \
    adrift \
    rags \
    novelty \
    twine \
    bitsy \
    flick \
    renpy \
    tyranobuilder \
    visual \
    rpg \
    maker \
    vx \
    ace \
    xp \
    vx \
    ace \
    mv \
    mz \
    wolf \
    rpg \
    tsukuru \
    sim \
    rpg \
    maker \
    95 \
    2000 \
    2003 \
    xp \
    vx \
    vx \
    ace \
    mv \
    mz \
    open \
    rpg \
    maker \
    easy \
    rpg \
    player \
    wolf \
    rpg \
    editor \
    solarus \
    solarus \
    quest \
    editor \
    zelda \
    classic \
    zelda \
    mystery \
    of \
    solarus \
    dx \
    baldur \
    gate \
    neverwinter \
    nights \
    icewind \
    dale \
    planescape \
    torment \
    temple \
    of \
    elemental \
    evil \
    knights \
    of \
    the \
    old \
    republic \
    jade \
    empire \
    dragon \
    age \
    origins \
    mass \
    effect \
    witcher \
    witcher2 \
    witcher3 \
    cyberpunk \
    2077 \
    elden \
    ring \
    dark \
    souls \
    demon's \
    souls \
    bloodborne \
    sekiro \
    armored \
    core \
    from \
    software \
    miyazaki \
    hidetaka \
    martin \
    george \
    r.r. \
    tolkien \
    j.r.r. \
    lewis \
    c.s. \
    christianity \
    theology \
    bible \
    church \
    fathers \
    patristics \
    2>/dev/null || true

# Install AUR helper (yay)
if ! command -v yay &> /dev/null; then
    echo -e "${SILVER}Installing yay AUR helper...${RESET}"
    cd /tmp
    git clone https://aur.archlinux.org/yay.git
    cd yay
    makepkg -si --noconfirm
    cd "$SCRIPT_DIR"
fi

# Install AUR packages
echo -e "${SILVER}Installing AUR packages...${RESET}"
yay -S --needed --noconfirm \
    hyprland-git \
    waybar-hyprland-git \
    rofi-lbonn-wayland-git \
    swww \
    swaylock-effects \
    wlogout \
    wlsunset \
    wl-gammarelay-rs \
    wl-screenrec \
    grimblast-git \
    satty-git \
    hyprpicker \
    hypridle \
    hyprlock \
    hyprpaper \
    xdg-desktop-portal-hyprland \
    pyprland \
    hyprshell \
    hyprnotify \
    hyprdim \
    hyprnome \
    hyprcursor \
    rose-pine-hyprcursor \
    bibata-cursor-theme \
    phinger-cursors \
    google-chrome \
    brave-bin \
    librewolf-bin \
    floorp-bin \
    waterfox-bin \
    mercury-browser-bin \
    thorium-browser-bin \
    ungoogled-chromium-bin \
    chromium-wayland-vaapi \
    brave-nightly-bin \
    opera \
    opera-ffmpeg-codecs \
    vivaldi \
    vivaldi-ffmpeg-codecs \
    vivaldi-widevine \
    microsoft-edge-stable \
    microsoft-edge-beta \
    microsoft-edge-dev \
    microsoft-edge-canary \
    zen-browser-bin \
    arc-browser \
    sigma-browser \
    surf \
    badwolf \
    luakit \
    qutebrowser \
    nyxt \
    vimb \
    uzbl-browser \
    dwb \
    xxxterm \
    xombrero \
    midori \
    epiphany \
    dillo \
    netsurf \
    links \
    lynx \
    w3m \
    elinks \
    edbrowse \
    browsh \
    carbonyl \
    buku \
    bukurun \
    zotero \
    jabref \
    docear \
    mendely \
    papers \
    readcube \
    colwiz \
    qiqqa \
    citavi \
    endnote \
    refworks \
    zotero \
    mendeley \
    jabref \
    docear \
    papers \
    readcube \
    bookends \
    son \
    of \
    citation \
    machine \
    cite \
    this \
    for \
    me \
    easybib \
    refme \
    citavi \
    zotero \
    mendeley \
    jabref \
    2>/dev/null || true

echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║  ${GOLD}INSTALLATION PHASE 2: Deploying Theological Library${RED}                ║${RESET}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Create theology directory
mkdir -p "$HOME/.local/share/theology"
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.config"

# Extract the embedded theology database
echo -e "${SILVER}Extracting Biblical and Patristic texts...${RESET}"
cd "$THEOLOGY_DIR"

# Run the extraction script
python3 extract_theology.py

echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║  ${GOLD}INSTALLATION PHASE 3: Configuring Desktop Environment${RED}              ║${RESET}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Detect desktop environment
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    DE_TYPE="wayland"
    if pgrep -x "Hyprland" > /dev/null 2>&1 || [ -n "$HYPRLAND_INSTANCE_SIGNATURE" ]; then
        WM="hyprland"
    else
        WM="sway"
    fi
else
    DE_TYPE="x11"
    WM="i3"
fi

echo -e "${SILVER}Detected: $DE_TYPE session with $WM${RESET}"

# Backup existing configs
echo -e "${SILVER}Backing up existing configurations...${RESET}"
BACKUP_DIR="$HOME/.config/backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

for config in i3 sway hyprland polybar waybar rofi wofi kitty alacritty wezterm foot \
              dunst mako swaync picom neofetch fastfetch starship zsh fish tmux \
              nvim vim ranger nnn lf vifm broot zellij newsboat calcurse task; do
    if [ -d "$HOME/.config/$config" ]; then
        cp -r "$HOME/.config/$config" "$BACKUP_DIR/"
    fi
done

echo -e "${GOLD}Backed up to: $BACKUP_DIR${RESET}"

# Deploy rice configurations
echo -e "${SILVER}Deploying Sanctum OS rice configurations...${RESET}"

cd "$CONFIG_DIR"

# Copy all configs
for dir in */; do
    if [ -d "$dir" ]; then
        config_name="${dir%/}"
        echo -e "${SILVER}  → Installing $config_name${RESET}"
        mkdir -p "$HOME/.config/$config_name"
        cp -r "$config_name/"* "$HOME/.config/$config_name/" 2>/dev/null || true
    fi
done

echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║  ${GOLD}INSTALLATION PHASE 4: System Integration${RED}                          ║${RESET}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Add theology commands to PATH
if ! grep -q ".local/bin" "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q ".local/bin" "$HOME/.zshrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    fi
fi

# Deploy scripts
echo -e "${SILVER}Installing theology CLI tools...${RESET}"
cd "$SCRIPT_DIR/../scripts"
chmod +x *.sh *.py 2>/dev/null || true
cp *.sh "$HOME/.local/bin/" 2>/dev/null || true
cp *.py "$HOME/.local/bin/" 2>/dev/null || true

# Deploy wallpapers
echo -e "${SILVER}Installing theological wallpapers...${RESET}"
mkdir -p "$HOME/.local/share/wallpapers/sanctum-os"
cp -r "$SCRIPT_DIR/../wallpapers/"* "$HOME/.local/share/wallpapers/sanctum-os/" 2>/dev/null || true

echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║  ${GOLD}INSTALLATION COMPLETE${RED}                                            ║${RESET}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

echo -e "${GOLD}Sanctum OS has been installed successfully.${RESET}"
echo ""
echo -e "${SILVER}Available commands:${RESET}"
echo -e "  ${RED}biblia${RESET}        - Search and read the Holy Bible"
echo -e "  ${RED}patres${RESET}        - Access the Church Fathers"
echo -e "  ${RED}sanctum-quote${RESET} - Display a random theological quote"
echo -e "  ${RED}sanctum-theme${RESET} - Apply the Sanctum color scheme"
echo -e "  ${RED}sanctum-help${RESET}  - Display this help message"
echo ""
echo -e "${SILVER}Press Mod+Shift+Enter to open a terminal${RESET}"
echo -e "${SILVER}Press Mod+D to open the theological application menu${RESET}"
echo ""
echo -e "${GOLD}Gloria Patri, et Filio, et Spiritui Sancto.${RESET}"
echo ""

# Offer to restart
read -p "Would you like to restart your session now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${SILVER}Restarting...${RESET}"
    if [ "$WM" = "hyprland" ]; then
        hyprctl dispatch exit
    elif [ "$WM" = "sway" ]; then
        swaymsg exit
    else
        i3-msg exit
    fi
fi
