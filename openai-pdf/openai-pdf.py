#!/usr/bin/env python3
"""
extract_pdf_with_gpt41nano.py

Usage:
    python extract_pdf_with_gpt41nano.py /path/to/your/file.pdf
"""

import sys, time, os, pathlib, json
from openai import OpenAI
from openai.types.beta.assistant import Assistant

# 1️⃣ Setup -------------------------------------------------------------------
if len(sys.argv) != 2 or not sys.argv[1].lower().endswith(".pdf"):
    sys.exit("Usage: python extract_pdf_with_gpt41nano.py your_doc.pdf")

pdf_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
if not pdf_path.is_file():
    sys.exit(f"File not found: {pdf_path}")

client = OpenAI()                # requires OPENAI_API_KEY env var
model_name = "gpt-4o"      # adjust if your account uses a different slug

# 2️⃣ Upload the PDF ----------------------------------------------------------
print("⇢ Uploading PDF …")
with open(pdf_path, "rb") as fp:
    file_obj = client.files.create(file=fp, purpose="assistants")
file_id = file_obj.id

# 3️⃣ Create / reuse an Assistant -------------------------------------------
print("⇢ Ensuring Assistant exists …")
asst_name = "PDF-extractor-nano"
assistant: Assistant

# Try to find an existing one (keeps your quota tidy)
for a in client.beta.assistants.list(order="desc", limit=100).data:
    if a.name == asst_name and a.model == model_name:
        assistant = a
        print("using existing assistant")
        break
else:
    assistant = client.beta.assistants.create(
        name=asst_name,
        model=model_name,
        tools=[{"type": "code_interpreter"}],
        description="Extracts full text from PDFs and returns it verbatim"
    )
    print("creating new assistant")

# 4️⃣ Start a thread + run -----------------------------------------------------
message = (
    "Please open the attached PDF, extract **all** textual content in the "
    "original order (no summaries, no headings, no analysis) and return only "
    "the plain text. If the PDF is empty, reply with an empty string."
)

print("⇢ Creating thread and run …")
thread = client.beta.threads.create(
    messages=[{
        "role": "user",
        "content": message,
        "attachments": [{"file_id": file_id, "tools": [{"type": "code_interpreter"}]}]
    }]
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Return only raw text."
)

# 5️⃣ Poll until done ---------------------------------------------------------
print("⇢ Waiting for GPT-4.1-nano to finish …")
while run.status not in {"completed", "failed", "cancelled", "expired"}:
    time.sleep(3)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print(f"   status: {run.status} …")

if run.status != "completed":
    sys.exit(f"Run ended with status {run.status}")

# 6️⃣ Fetch the answer --------------------------------------------------------
msgs = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
assistant_reply = next(m for m in msgs if m.role == "assistant").content[0].text.value

# 7️⃣ Write to disk -----------------------------------------------------------
txt_path = pdf_path.with_suffix(".txt")
txt_path.write_text(assistant_reply, encoding="utf-8")
print(f"✓ Done! Extracted text saved to {txt_path}")
