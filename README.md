
# ☁️ GCloud GUI Manager (v1.0.0)

A simple, modern, and lightweight GUI tool to manage your Google Cloud CLI (`gcloud`) effortlessly. Say goodbye to typing long commands just to switch projects or refresh your authentication tokens!

## ✨ Features

* **Auto-Fetch Projects:** Instantly loads your active and available GCP projects.
* **Smart Search:** Filter through your project list quickly with a built-in search bar.
* **1-Click Re-Authenticate:** Run `gcloud auth login` and `gcloud auth application-default login` with a single click.
* **Built-in Native Terminal:** A persistent mini-console embedded at the bottom of the GUI. It inherits your current working directory and can execute native shell commands or live `gcloud` tasks (like deployments) in real-time.
* **Global Access:** Run the tool from anywhere in your terminal using a single, short command.

## 📋 Prerequisites

Before installing, make sure you have the following installed on your system:
* [Python 3.x](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads)
* [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install) (Ensure it is added to your system PATH)

## 🚀 Installation

You can install this tool globally directly from this GitHub repository using `pip`. Open your terminal or command prompt and run:

```bash
pip install git+[https://github.com/sherlockjack/aruaru.git](https://github.com/sherlockjack/aruaru.git)

```

---

## 🔄 How to Update

If there is a new version or feature pushed to this repository, you need to force `pip` to upgrade and reinstall the package. Run this command:

```bash
pip install --upgrade --force-reinstall git+[https://github.com/sherlockjack/aruaru.git](https://github.com/sherlockjack/aruaru.git)

```

---

## 💻 Usage

Once installed, the command is globally registered to your system. You can launch the GUI from **any directory** (it will inherit the directory path you launch it from).

Just open your terminal (or VS Code terminal) and type:

```bash
gcloudui

```

### Navigating the UI:

1. **Search & Select:** Type in the search bar to filter your GCP projects, then click **Set Active Project** to switch context.
2. **Re-Authenticate:** Click the **🔐 1-Click Re-Auth** button whenever your token expires. It will safely open your browser for Google Login.
3. **Using the Mini Terminal:**
* Look for the `⌨️ Input >` box at the very bottom of the app.
* Type any command (e.g., `gcloud run services list`, `dir`, `ping google.com`) and press **Enter**.
* The output will be streamed into the dark screen above it.
* *Tip: Clicking on the dark screen and typing will automatically redirect your keystrokes back to the input box!*



---
\