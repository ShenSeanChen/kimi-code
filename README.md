# ⚡ Kimi Code × k2.7: Catch, Train, Ship 🐭

```
              ⚡
            /\        /\
           /  \      /  \
          /⚫  \    /  ⚫\
         /      \  /      \
        |   o      o      |
        |  (O)      (O)   |
        |       v         |
         \    ⌒  ⌒       /
          \_____________/
```

> *“To become a Pokémon Master of Code, you must first choose your starter.”*

Welcome, trainer! 🌟

This repo shows how to go from **zero to a real financial dashboard** using **[Kimi Code](https://www.kimi.com/code)** and its latest model, **k2.7**.

No slide decks. No fake screenshots. Just one detailed prompt, real stock market data, and a working research terminal that opens in your browser.

---

## 🎯 TL;DR

1. Install Kimi Code (terminal or VS Code / Cursor).
2. Log in with `/login`.
3. Install the **Kimi Data Source Plugin** with `/plugins`.
4. Copy the prompt from [`prompt.md`](./prompt.md) and paste it into Kimi.
5. Wait a few minutes. Open the generated `research_workbench.html`.

That’s it. You just shipped a Bloomberg-style research terminal.

---

## 🎥 What this repo demonstrates

The journey is simple:

1. **Catch Kimi Code** — install the agent.
2. **Log in once** with `/login`.
3. **Add a data plugin** so Kimi can read real market data.
4. **Issue one big prompt** and let k2.7 build everything.
5. **Open the generated dashboard** and explore charts, tickers, and news.

One idea → one prompt → one shipped tool.

---

## 🤔 What is Kimi Code?

Kimi Code is an AI coding agent. You tell it what you want in plain English, and it can:

- Write and edit code
- Search the web and read documents
- Run terminal commands
- Build full apps and dashboards

It works in two places: your **terminal** and inside **VS Code / Cursor** as an extension.

---

## 🥚 Choose Your Starter

Pick the path that feels easiest for you:

| Starter | Path | Best for |
|---------|------|----------|
| 🔥 **Charmander** | Terminal | You’re comfortable typing commands |
| 💧 **Squirtle** | VS Code / Cursor | You prefer buttons and side panels |

You only need one. Both lead to the same result.

---

## 🔥 Charmander Route: Terminal

### 1. Install Kimi Code

**Mac / Linux:**

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
```

**Windows:**

```powershell
Invoke-RestMethod https://code.kimi.com/kimi-code/install.ps1 | Invoke-Expression
```

### 2. Start Kimi Code

```bash
kimi
```

If `kimi` is not found, restart your terminal or run:

```bash
source ~/.zshrc   # or ~/.bashrc
```

### 3. Log in

Inside Kimi Code, type:

```
/login
```

This opens your browser and signs you in automatically.

### 4. Try a quick command

```
Build me a React app that looks like a Pokédex
```

---

## 💧 Squirtle Route: VS Code / Cursor

1. Open **Extensions** (`Cmd+Shift+X` on Mac, `Ctrl+Shift+X` on Windows).
2. Search **“Kimi Code”** and install it.
3. Open the Kimi Code panel from the sidebar.
4. Type `/login` in the Kimi terminal.
5. Start coding.

> 💡 *Cursor is built on VS Code, so the Kimi Code extension usually works there too. If you don’t see it in Cursor’s store, use the terminal route instead.*

---

## 🧰 Add the Data Plugin

For the research terminal demo, Kimi needs access to financial data. That’s where the **Kimi Data Source Plugin** comes in.

Inside Kimi Code, run:

```
/plugins
```

Find **Kimi Data Source Plugin** and install it.

Then activate it with:

```
/kimi-datasource
```

Once that’s done, Kimi can pull real stock prices, company info, news, and filings — basically everything the big prompt needs.

---

## 🚀 Build the Research Terminal

Now for the fun part.

### 1. Open Kimi Code

Terminal:

```bash
kimi
```

Or open the Kimi Code panel in VS Code / Cursor.

### 2. Paste the prompt

Open [`prompt.md`](./prompt.md) and copy the entire text.

Paste it into Kimi Code.

### 3. Let k2.7 work

The prompt asks k2.7 to:

- Pick 8–12 U.S. clean energy stocks
- Download real price history and recent news
- Build an interactive HTML dashboard with charts
- Create Excel files for peer comparisons and sources
- Open the dashboard in your browser to check everything loads

This usually takes a few minutes, depending on your internet speed.

### 4. Open the result

Once it’s done, open this file in your browser:

```
us_clean_energy_power_research_workbench/research_workbench.html
```

You’ll see a scrolling ticker tape, stock charts, comparison tables, and more — all built from real data.

---

## 🧭 Command Pokédex

| Command | What it does |
|---------|--------------|
| `kimi --version` | Check which version you have |
| `kimi --thinking` | Make Kimi reason harder (slower but smarter) |
| `/login` | Sign in with your browser |
| `/setup` | Add an API key manually |
| `/plugins` | Install plugins |
| `/sessions` | See your previous chats |
| `kimi --continue` | Resume your last chat |
| `/compact` | Free up memory when chats get long |

---

## 🏆 Pro Tips

- **Use `@filename`** to point Kimi at a specific file, like calling a Pokémon to attack.
- **Press `Ctrl-X`** in the terminal to run normal shell commands without leaving Kimi.
- **Run `/compact`** if your chat starts getting slow.
- **The prompt is long on purpose.** k2.7 reads all the details so you don’t have to micromanage it.

---

## 📦 What gets created

After running the prompt, you’ll get a new folder:

```
us_clean_energy_power_research_workbench/
├── research_workbench.html          # The interactive dashboard
├── us_clean_energy_power_peer_comps.xlsx  # Stock comparison spreadsheet
├── source_inventory.xlsx            # List of data sources used
├── market_ohlcv.json                # Real stock price history
└── README.md                        # Notes from k2.7 about the build
```

---

## 📜 Learn More

- [Kimi Code official site](https://www.kimi.com/code)
- [Kimi Code CLI on GitHub](https://github.com/MoonshotAI/kimi-cli)
- [Kimi Code introduction](https://www.kimi.com/resources/kimi-code-introduction)

---

## 🤝 Open Source

This repo is meant to be an open Pokédex. Fork it, remix the prompt, swap the theme, or use it as a starting point for your own k2.7 demos.

If you build something cool, share it. The Pokémon League has room for many champions. ⚡

---

*May your builds pass and your bugs be few.*

*“I’m gonna be a Pokémon Master… of Code!”* 👑
