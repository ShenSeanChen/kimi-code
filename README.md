# Kimi Code Setup

A quick reference for setting up [Kimi Code](https://www.kimi.com/code) — Moonshot AI's coding agent — either in your terminal or inside VS Code / Cursor.

---

## Option 1: Terminal (CLI)

### 1. Install

**macOS / Linux:**

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
```

**Windows (PowerShell):**

```powershell
Invoke-RestMethod https://code.kimi.com/kimi-code/install.ps1 | Invoke-Expression
```

### 2. Restart your shell

If `kimi` is not found, reload your shell config:

```bash
source ~/.zshrc   # or ~/.bashrc
```

Or just open a new terminal tab.

### 3. Authenticate

Run:

```bash
kimi
```

Then type:

```
/login
```

This opens a browser and logs you in automatically.

### 4. Start coding

```bash
kimi
```

Then ask it anything, e.g.:

```
Create a simple React counter component
```

---

## Option 2: VS Code / Cursor Extension

1. Open **Extensions** (`Cmd+Shift+X` / `Ctrl+Shift+X`).
2. Search **"Kimi Code"** and install it.
3. Open the Kimi Code panel from the sidebar.
4. Run `/login` in the extension terminal to authenticate.
5. Start asking Kimi Code to edit, explain, or generate code.

> Cursor is built on VS Code, so you can usually install the same extension from the marketplace. If it is not available in Cursor's store, use the terminal CLI instead.

---

## Useful commands

| Command | What it does |
|---------|--------------|
| `kimi --version` | Check installed version |
| `kimi --thinking` | Enable deeper reasoning |
| `/login` | Log in via browser |
| `/setup` | Configure API key manually |
| `/sessions` | View past sessions |
| `kimi --continue` | Resume last session |

---

## References

- [Kimi Code official site](https://www.kimi.com/code)
- [Kimi Code CLI on GitHub](https://github.com/MoonshotAI/kimi-cli)
- [Kimi Code introduction / docs](https://www.kimi.com/resources/kimi-code-introduction)
