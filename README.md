# 🧠 Gemma2-AllRounder-Coder (Local CPU Autonomous Coding Agent)

A custom **Ollama coding model (`allrounder-coder`)** paired with an **autonomous, multi-file Python coding agent (`agent.py`)**—engineered to run **100% locally on CPU-only hardware (16 GB DDR4-3200 RAM)** with **zero dedicated GPU** required.

![Base Model](https://shields.io)
![Runtime](https://shields.io)
![Hardware](https://shields.io)
![Speed](https://shields.io)

---

## 🎯 Why I Built This
Most AI coding agents require expensive cloud APIs or heavy discrete GPUs. I built **`allrounder-coder`** to run completely offline on a standard **Windows 11 (16 GB RAM)** laptop—capable of generating, saving, executing, and self-debugging multi-file projects across:
* **Low-Level Systems & OS Dev:** x86/x86_64 Assembly (NASM/GAS), bootloaders, and Java system tools.
* **Embedded & IoT:** ESP32-S3 (MicroPython & Arduino C++).
* **Web & Automation:** HTML, CSS, JavaScript, Python scripts, and Windows CMD/PowerShell.

---

## ⚡ Real Local CPU Benchmarks
Tested locally on **Windows 11 (16 GB Dual-Channel DDR4-3200 RAM, CPU-only inference)**:
* **Model Load Time:** `~3.8 ms – 16.0 ms`
* **Prompt Evaluation Rate:** `84.63 tokens/s`
* **Token Generation Speed (`eval rate`):** `14.15 tokens/s` (faster than real-time reading speed, 100% offline)

---

## ⚙️ How the Agent Works (`agent.py`)

```text
[User Task Prompt]
        │
        ▼
[Workspace File Scanner + Persistent Memory (history.json)]
        │
        ▼
[Local Ollama API (http://localhost:11434) -> allrounder-coder]
        │
        ▼
[Live Token Streaming + Multi-File Parser -> ./workspace/]
        │
        ▼
[Auto-Test & Self-Debug Loop (Python / Java / NASM Assembly)]
```

### Key Features
* **Live Token Streaming:** Streams generated code directly to the terminal in real time.
* **Multi-File Extraction:** Automatically parses and saves `.html`, `.css`, `.js`, `.py`, `.java`, `.asm`, and `.ino` files straight into `./workspace/`.
* **Persistent Session Memory:** Saves conversation context in `history.json` and scans live workspace files on disk so features can be added step-by-step across sessions (with `/reset` to start fresh).
* **Self-Debugging Execution Loop:** Automatically runs `.py`, compiles `.java` (`javac`), or assembles `.asm` (`nasm`) and feeds any compiler/runtime error back to the model (up to 3 attempts) to self-correct bugs.

---

## 🚀 Quick Start

### 1. Prerequisites
* Install **[Ollama for Windows](https://ollama.com)** and pull Gemma 2:
  ```powershell
  ollama pull gemma2:2b
  ```
* Install Python `requests`:
  ```powershell
  pip install requests
  ```

### 2. Build the Custom Model & Launch the Agent
```powershell
ollama create allrounder-coder -f Modelfile
python agent.py
```

---

## 📂 Repository Structure
```text
├── Modelfile          # Custom Ollama system prompt & context/temperature config
├── agent.py           # Streaming multi-file autonomous Python agent with memory
├── workspace/         # Auto-generated project files (e.g., neonpulse.html)
└── README.md          # Project documentation & local CPU benchmarks
```

---

## 🔮 Future Roadmap
* **QLoRA Fine-Tuning:** Fine-tune Gemma 2 (2B/9B) using **Unsloth** on a custom dataset of Assembly bootloaders, Java systems code, Python automation, and ESP32-S3 firmware, then export custom `Q4_K_M` `.gguf` weights back to Ollama.
* **ESP32-S3 Micro Cyberdeck Bridge:** Connect the local Ollama API over Wi-Fi so my ESP32-S3 micro cyberdeck can query the coding agent wirelessly.

