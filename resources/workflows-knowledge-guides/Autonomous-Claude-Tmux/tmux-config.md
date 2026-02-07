# tmux Configuration for Claude Code

A complete `~/.tmux.conf` optimized for long-running, autonomous Claude Code sessions with the Catppuccin Mocha theme.

## Core tmux.conf

```bash
# ~/.tmux.conf

# ── True Color Support ──────────────────────────────────────────────
set -g default-terminal "xterm-256color"
set-option -ga terminal-overrides ",xterm-256color:Tc"

# ── Prefix Key ──────────────────────────────────────────────────────
# Ctrl+a is more ergonomic than the default Ctrl+b
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# ── Mouse & Input ───────────────────────────────────────────────────
set -g mouse on

# ── History ─────────────────────────────────────────────────────────
# Claude Code generates verbose output - keep a large scrollback
set -g history-limit 50000

# ── Encoding ────────────────────────────────────────────────────────
setw -q -g utf8 on

# ── Catppuccin Mocha Theme ──────────────────────────────────────────
set -g status-style "bg=#1e1e2e,fg=#cdd6f4"
set -g window-status-current-style "bg=#89b4fa,fg=#1e1e2e,bold"
set -g pane-border-style "fg=#313244"
set -g pane-active-border-style "fg=#89b4fa"
set -g message-style "bg=#313244,fg=#cdd6f4"

# ── Status Bar ──────────────────────────────────────────────────────
set -g status-left "#[bg=#89b4fa,fg=#1e1e2e,bold] #S #[bg=#1e1e2e,fg=#89b4fa]"
set -g status-right "#[fg=#f5c2e7]#(whoami) #[fg=#89b4fa]│ #[fg=#cba6f7]%Y-%m-%d %H:%M #[bg=#89b4fa,fg=#1e1e2e,bold] #h "
set -g status-left-length 50
set -g status-right-length 100

# ── Intuitive Pane Splitting ────────────────────────────────────────
# Split with | and - instead of % and "
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

# ── Vim-Style Pane Navigation ───────────────────────────────────────
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# ── Quick Actions ───────────────────────────────────────────────────
# Clear pane for a fresh Claude prompt
bind C-l send-keys 'clear' Enter
```

## Shell Environment

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export TERM=xterm-256color
export COLORTERM=truecolor
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

## Session Persistence Plugins

For automatic save/restore of your tmux workspace across reboots:

```bash
# Install tmux plugin manager (TPM)
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# Add to ~/.tmux.conf
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @continuum-restore 'on'

# Initialize TPM (keep at bottom of tmux.conf)
run '~/.tmux/plugins/tpm/tpm'
```

After adding the plugin lines, press `Ctrl+a I` to install them.

## Troubleshooting

**Colors not displaying correctly?**
```bash
# Test true color support
curl -s https://raw.githubusercontent.com/JohnMorales/dotfiles/master/colors/24-bit-color.sh | bash
```

**Claude Code output garbled?**
```bash
locale -a | grep UTF-8
export LC_ALL=en_US.UTF-8
```

**Can't detach from session?**
The config remaps prefix to `Ctrl+a`:
- Detach: `Ctrl+a d`
- Not: `Ctrl+b d`
