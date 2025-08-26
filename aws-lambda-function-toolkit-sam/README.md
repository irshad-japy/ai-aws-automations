
# SAM + SQS → Lambda (Python) → Pandas → ReportLab PDF (Local POC)

This PoC uses your **existing `template.yml`** as-is and focuses on local development with **AWS Toolkit + SAM CLI + Docker** in **VS Code**.

## What it does

1. Receives an **SQS** event (locally we simulate it with `events/sqs_event.json`).
2. Parses a CSV string from the message body (or uses a built-in sample).
3. Builds a **Pandas DataFrame**.
4. Generates a **PDF** with **ReportLab**.
5. **Mounts a local folder** into the Docker container so the PDF lands on your Windows machine.

---

## Prerequisites

- **Docker Desktop** (running)
- **AWS SAM CLI**
- **AWS CLI** (optional, for deployment later)
- **VS Code** with **AWS Toolkit** extension
- Python 3.12 (optional for linting/type checking locally)

> On Windows, run commands in **PowerShell** or **CMD** as shown.

---

## Project layout

```
sam-sqs-pandas-pdf/
├─ template.yml
├─ src/
│  └─ lambda_function.py
├─ requirements.txt
├─ events/
│  └─ sqs_event.json
├─ env.json               # sets OUTPUT_DIR=/var/task/output for local runs
├─ output/                # local folder to receive generated PDF
└─ .vscode/
   └─ launch.json
```

---

## 1) Install dependencies & build (SAM)

SAM will build inside a Lambda-like Docker container (recommended for native deps like Pandas).

**PowerShell**

```powershell
cd sam-sqs-pandas-pdf
sam build --use-container
```

**CMD**

```cmd
cd /d sam-sqs-pandas-pdf
sam build --use-container
```

**macOS/Linux**

```bash
cd "sam-sqs-pandas-pdf"
sam build --use-container
sam build --use-container --no-cached --debug
```

---

## 2) Run locally with SQS event and mount output folder

We'll mount your local `output/` folder into the container at `/var/task/output` and tell the function to write the PDF there.

### Create an env file (already included)
`env.json` contains:
```json
{
  "tgepdfexpressstatementstaging": {
    "OUTPUT_DIR": "/var/task/output"
  }
}

```

### Invoke (PowerShell)
```powershell
sam local invoke tgepdfexpressstatementstaging `
  -e events\sqs_event.json `
  --env-vars env.json

```

### Invoke (CMD)
```cmd
set OUTPUT=%cd%\output
sam local invoke tgepdfexpressstatementstaging -e events\sqs_event.json --env-vars env.json"
```

### Invoke (macOS/Linux)
```bash
sam local invoke tgepdfexpressstatementstaging   -e events/sqs_event.json   --env-vars env.json"
```

After a successful run, check `output/sample_dataframe.pdf` on your machine.

---

## 3) Debug in **VS Code** (AWS Toolkit)

1. Open the folder in VS Code.
2. In the **AWS Explorer** (left sidebar), under **Lambda** → **Local**, right-click the function
   `tgepdfexpressstatementstaging` (from `template.yml`) → **Debug Locally**.
3. When prompted for an event payload, select **`events/sqs_event.json`**.
4. To save the PDF to your host, add a **Docker volume** mapping in the *SAM CLI Docker options* VS Code setting
   (Command Palette → *Preferences: Open Settings (JSON)*), add:

5. Add an env var via **`env.json`** or Toolkit's debug config to set `OUTPUT_DIR=/var/task/output`.

You can set breakpoints in `src/lambda_function.py` and step through the code.

> If the Toolkit UI differs, you can always fall back to the `sam local invoke` commands above for reliable volume mounting.

---

## 4) (Optional) Wire up **real SQS trigger** in AWS

Your `template.yml` is kept exactly as provided. To receive real SQS events in AWS, add an SQS event mapping later:

```yaml
Events:
  SqsTrigger:
    Type: SQS
    Properties:
      Queue: arn:aws:sqs:ap-southeast-2:ACCOUNT_ID:YOUR_QUEUE_NAME
      BatchSize: 10
```

Then deploy:

```bash
sam deploy --guided
```

---

## 5) Sending your own CSV in local tests

Edit `events/sqs_event.json` and replace the CSV under `body.csv`. The function accepts either:
- Raw CSV string as the SQS message body **or**
- JSON string with a `"csv"` field (as provided).

---

## 6) Troubleshooting

- **Pandas/ReportLab import errors** → Always build with `sam build --use-container`.
- **No PDF on host** → Ensure the `OUTPUT_DIR=/var/task/output` is set.
---

## 7) Clean up

```bash
sam delete
```

Enjoy! 🚀
