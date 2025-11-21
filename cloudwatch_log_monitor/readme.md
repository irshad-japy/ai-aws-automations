docker compose up -d --build

curl -X POST http://localhost:8000/check-lambda-logs

# run fast api below command
uvicorn app:app --reload --port 8000
POST http://localhost:8000/check-logs

body
{
  "send_if_no_logs": true
}
