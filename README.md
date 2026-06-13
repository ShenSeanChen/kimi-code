# ⚡ Kimi Code Adventure Guide 🏴‍☠️

> *“To become the King of Code, you must first choose your path.”*

Welcome, trainer — or should I say, pirate captain! 🌊

This repo is your map to setting up **[Kimi Code](https://www.kimi.com/code)**, Moonshot AI’s coding agent. You can wield it from the **terminal** like a lone swordsman, or pilot it from **VS Code / Cursor** like a Pokémon master commanding their partner.

Choose your starter below. ⬇️

---

## 🥚 Choose Your Starter

| Path | Best for | Difficulty |
|------|----------|------------|
| 🗡️ **Terminal** | Pirates who live in the command line | Easy |
| 🧩 **VS Code / Cursor** | Trainers who like buttons and sidebars | Easy |

---

## 🗡️ Path 1: Terminal (The Zoro Route)

No IDE. Just you, your shell, and three swords worth of AI power.

### Step 1: Catch your Kimi

**macOS / Linux:**

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
```

**Windows (PowerShell):**

```powershell
Invoke-RestMethod https://code.kimi.com/kimi-code/install.ps1 | Invoke-Expression
```

### Step 2: Wake up your shell

If `kimi` isn’t found, reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

Or open a new terminal tab like opening a new route on the Grand Line.

### Step 3: Log in

```bash
kimi
```

Then type:

```
/login
```

A browser will pop open — that’s your Pokédex… I mean, auth flow. 📱

### Step 4: Battle

```bash
kimi
```

Then challenge it:

```
Create a React counter faster than Pikachu’s Quick Attack
```

---

## 🧩 Path 2: VS Code / Cursor (The Ash Route)

You want a partner by your side, visible and ready.

1. Open **Extensions** (`Cmd+Shift+X` / `Ctrl+Shift+X`).
2. Search **"Kimi Code"** and install it. ✨
3. Open the Kimi Code panel from the sidebar.
4. Run `/login` in the extension terminal.
5. Start coding — “I choose you, Kimi!”

> 💡 *Cursor is built on VS Code, so the same extension usually works. If Cursor’s marketplace doesn’t have it, switch to the Terminal path above — it’s just as strong.*

---

## 🧭 Command Pokédex

| Command | Effect |
|---------|--------|
| `kimi --version` | Check your companion’s level |
| `kimi --thinking` | Use deeper reasoning (like entering Gear 2) |
| `/login` | Log in via browser |
| `/setup` | Configure API key manually |
| `/sessions` | View your saved adventures |
| `kimi --continue` | Resume your last quest |

---

## 🏆 Final Boss Tips

- Use `@filename` to point Kimi at a specific file, like calling a Pokémon to the field.
- Press `Ctrl-X` in the CLI to drop into shell mode — handy for quick looting.
- Run `/compact` when your context bar gets high, like healing your team at a Pokémon Center.

---

## 📜 Scrolls of Wisdom

- [Kimi Code official site](https://www.kimi.com/code)
- [Kimi Code CLI on GitHub](https://github.com/MoonshotAI/kimi-cli)
- [Kimi Code introduction](https://www.kimi.com/resources/kimi-code-introduction)

---

*May your builds pass and your bugs be few. 🌟*

*“I’m gonna be King of the Coders!”* 👑
