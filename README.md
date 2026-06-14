# Offline Deep-File Miner & AI Naming Assistant

> **Reclaim your time from tedious office organization.** Seamlessly rename and reorganize files according to your company's exact policies. An offline execution assistant that uses free AI APIs to securely retrieve and format files across infinite directory layers.

---

## Overview

In any real-world office environment, you already know **where** your documents belong (project folders, department drives, or client directories). The actual pain point is **renaming** thousands of legacy files so they strictly conform to corporate naming conventions, versioning rules, or audit-ready formats.

Most open-source tools try to "guess" how to classify your files, often messing up your existing structure. **File & Folder Manager V5** (FFM-V5) takes a more practical approach. It provides an intuitive Tkinter UI that keeps you in control while using AI as a high-speed execution assistant.

| ✅ | What You Do | 🤖 | What the AI Does |
|---|-------------|---|-------------------|
| **Select Source Folder** | The tool scans the entire directory hierarchy, no matter how many layers deep. | **Analyze Content via Local AI** | Reads file metadata and content (Text, PDF, Images) completely offline using a local LLM/VLM. |
| **Apply Naming Rules** | Choose or define your rule set (e.g., `Client-Project-Date`). Configurable batch sizes. | **Generate Compliant Suggestions** | Evaluates the file's context and proposes a perfect, standardized filename based on your rules. |
| **Review & Execute** | Hit **Rename** or **Copy**. The UI updates your language preference automatically. | **Safe Execution & Logging** | Executes changes instantly with a built-in undo stack, while logging operations for compliance. |

*Privacy-First Architecture: Your files, directory trees, and paths are processed locally on your machine. The network connection is exclusively used to send string metadata to your chosen **AI API** for name generation; your actual corporate documents never leave your device.*

---

## How It Works

1. **Deep Directory Scan:** FFM-V5 walks through your entire folder structure, navigating deep sub-folders that standard batch renamers fail to process. You can easily filter targets by keywords, file extensions, or case-sensitivity.
2. **Context-Aware AI Suggestion:** For each target, the tool securely sends the filename string to your connected AI API (such as Gemini or Groq). The AI analyzes the contextual semantics and maps it perfectly to your designated rule pattern.
3. **Side-by-Side Preview:** The UI displays a clear **Current Name ↔ AI-Suggested Name** view. You can modify any suggestion on the fly, bulk-approve a batch, or skip specific items.
4. **Atomic Execution:** Once you confirm, the tool performs the operation (Rename, Copy, or Move) entirely on your local device. 
---

## Key Features

- **Office-Centric Workflow:** Unlike tools that force automated auto-classification, FFM-V5 respects your company's predefined destination rules and structures.
- **Deep-Folder Retrieval & Exclusion:** Pierces through infinite layers of sub-folders to extract and consolidate scattered files. Includes advanced keyword filtering to either target specific folders or **explicitly exclude** non-relevant ones.
- **Flexible Folder Operations:** Not just for renaming. You can create brand-new empty directory structures on the fly, or execute precise copy/move operations entirely via the UI.
- **Excel-Driven Reusability:** Export and save your operation configurations or history into Excel format. Perfect for repetitive corporate routines, batch tracking, and keeping an unalterable audit log.
- **Granular Batch Control:** Process files at your own pace (batches of 8, 10, 20, 50, or "All") to monitor AI tokens and performance metrics.
- **One-Click Undo:** Made a mistake? Revert any atomic batch operation instantly with zero risk to your original files.
- **Hybrid Security Model:** Designed for strict corporate compliance. It functions as a high-speed manual renamer completely offline. When AI features are enabled, only the necessary filename strings are sent via API for semantic analysis, keeping your internal file content entirely secure and invisible to the cloud.
- **Smart Language Toggle:** Features a polished slide-switch widget (`EN / 繁中`) that remembers your preferred language preference across sessions.

---

## Quick Start

Whether you are an office professional looking for an instant solution or a developer exploring the code, you can get started in seconds.

### 🏢 For Office Users (No Installation Required)
1. Go to the [**Releases**](https://github.com/你的帳號/你的專案名/releases) page.
2. Download the latest `FFM-V5.exe` (Windows standalone package).
3. Double-click to launch the UI instantly. *No Python configuration or environment setup needed.*

### 💻 For Developers & Technical Review
If you prefer to run the project from the source code:

```powershell
# 1. Clone the repository and navigate into it
git clone [https://github.com/你的帳號/你的專案名.git](https://github.com/你的帳號/你的專案名.git)
cd your-repo-name

# 2. Initialize and activate a virtual environment
python -m venv venv
./venv/Scripts/activate

# 3. Install dependencies and run the UI
pip install -r requirements.txt
python ui_main.py
