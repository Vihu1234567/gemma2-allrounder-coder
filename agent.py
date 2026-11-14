import json
import os
import re
import subprocess
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "allrounder-coder"
WORKSPACE = "workspace"
HISTORY_FILE = "history.json"
os.makedirs(WORKSPACE, exist_ok=True)

SYSTEM_PROMPT = """You are an autonomous multi-file coding agent.
When asked to build, update, or fix code, ALWAYS respond using this exact format for EVERY modified or new file:
FILENAME: <filename.ext>
```<lang>
<complete runnable code>
```
Never leave TODOs or placeholder comments; write full working logic. Keep explanations to 1 sentence outside the code blocks."""

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_history(messages):
    trimmed = [messages] + messages[-16:] if len(messages) > 17 else messages
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2)

def get_workspace_snapshot():
    files = [f for f in os.listdir(WORKSPACE) if os.path.isfile(os.path.join(WORKSPACE, f))]
    if not files:
        return ""
    snapshot = ["\n[CURRENT WORKSPACE FILES ON DISK]:"]
    for fname in files:
        fpath = os.path.join(WORKSPACE, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            snapshot.append(f"--- {fname} ---\n{content}")
        except Exception:
            pass
    return "\n".join(snapshot)

def ask_ollama(messages):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
        "options": {"temperature": 0.15, "num_ctx": 8192}
    }
    full_reply = []
    with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=180) as res:
        res.raise_for_status()
        for line in res.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                token = chunk.get("message", {}).get("content", "")
                print(token, end="", flush=True)
                full_reply.append(token)
                if chunk.get("done"):
                    break
    print()
    return "".join(full_reply)

def extract_and_save_all(reply):
    saved = []
    current_file = None
    in_code = False
    code_lines = []

    for line in reply.splitlines():
        stripped = line.strip()
        if not in_code:
            # Look for any filename like index.html, style.css, app.js, boot.asm, Main.java
            m = re.search(r"([a-zA-Z0-9_-]+\.(?:html|css|js|py|java|asm|c|cpp|h|ino|json|md|txt|ps1|bat))", stripped)
            if m:
                current_file = os.path.basename(m.group(1))
            elif stripped.startswith("```") and current_file:
                in_code = True
                code_lines = []
        else:
            if stripped.startswith("```"):
                in_code = False
                filepath = os.path.join(WORKSPACE, current_file)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(code_lines).strip() + "\n")
                saved.append((current_file, filepath))
                current_file = None
            else:
                code_lines.append(line)
    return saved

def run_test(filename, filepath):
    if filename.endswith(".py"):
        proc = subprocess.run(["python", filepath], capture_output=True, text=True, timeout=10)
        return proc.returncode == 0, proc.stderr or proc.stdout
    elif filename.endswith(".java"):
        comp = subprocess.run(["javac", filepath], capture_output=True, text=True)
        if comp.returncode != 0:
            return False, comp.stderr
        class_name = filename.replace(".java", "")
        run = subprocess.run(["java", "-cp", WORKSPACE, class_name], capture_output=True, text=True, timeout=10)
        return run.returncode == 0, run.stderr or run.stdout
    elif filename.endswith(".asm"):
        out_bin = filepath.replace(".asm", ".bin")
        proc = subprocess.run(["nasm", "-f", "bin", filepath, "-o", out_bin], capture_output=True, text=True)
        if proc.returncode != 0:
            return False, proc.stderr
        return True, f"Assembled cleanly to {out_bin}"
    return True, f"Saved {filepath} (ready to open)."

def main():
    messages = load_history()
    restored = len(messages) - 1
    print(f"=== {MODEL_NAME} Persistent Agent Ready (Restored {restored} past messages) ===")
    print("Commands: '/reset' to wipe memory for a new project, 'exit' to quit.")

    while True:
        user_task = input("\nTask: ").strip()
        if user_task.lower() in ("exit", "quit"):
            break
        if user_task.lower() == "/reset":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            save_history(messages)
            print("[Memory Cleared] Started fresh session.")
            continue

        workspace_context = get_workspace_snapshot()
        full_prompt = f"{user_task}\n{workspace_context}" if workspace_context else user_task
        messages.append({"role": "user", "content": full_prompt})

        for attempt in range(1, 4):
            print(f"\n[Attempt {attempt}] Generating...\n")
            reply = ask_ollama(messages)
            messages[-1] = {"role": "user", "content": user_task}
            messages.append({"role": "assistant", "content": reply})
            save_history(messages)

            saved_files = extract_and_save_all(reply)
            if not saved_files:
                print("\n[Note] No file blocks detected.")
                break

            all_ok = True
            for filename, filepath in saved_files:
                print(f"\n[Saved] -> {filepath}")
                try:
                    ok, output = run_test(filename, filepath)
                except FileNotFoundError as e:
                    ok, output = True, f"Saved {filepath} (tool not in PATH: {e.filename})"

                if ok:
                    print(f"[Success] {output.strip()}")
                else:
                    all_ok = False
                    print(f"[Error in {filename}]\n{output.strip()}")
                    messages.append({
                        "role": "user",
                        "content": f"{filename} failed with this error:\n{output}\nFix the bug and output the full corrected file."
                    })
                    break

            if all_ok:
                break

if __name__ == "__main__":
    main()
