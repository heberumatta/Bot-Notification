# 🤖 Event-Driven Telegram Bot & REST API

An end-to-end, containerized Data Engineering and Backend architecture. This project demonstrates an event-driven system where a Python-based Telegram bot ingests user interactions, processes SQL aggregations, and persists data in SQLite. A high-performance, asynchronous C# .NET 8 Minimal API then exposes these logs with built-in pagination.

## 📐 System Architecture

1. **Ingestion Layer (Python):** A Telegram bot built with `pyTelegramBotAPI` using long-polling. It processes real-time events, manages user states, and executes parameterized SQL queries for real-time analytics (`/stats` and `/history`).
2. **Persistence Layer (SQLite):** A relational database ensuring data integrity for user interactions. It bridges the gap between the event-driven bot and the REST API.
3. **Exposure Layer (C# .NET 8):** An asynchronous Minimal API utilizing `Microsoft.Data.Sqlite`. It features query parameter-based pagination (Limit/Offset) to ensure network scalability and uses modern C# immutable `record` structs for DTOs.
4. **Infrastructure:** Fully dockerized environment using `docker-compose`, decoupling secrets via `.env` variables and sharing a persistent volume for the database.

## 🚀 Tech Stack
* **Python 3.11:** `pyTelegramBotAPI`, `python-dotenv`
* **Backend:** C# 12, .NET 8, Minimal APIs, Asynchronous Programming (`async/await`)
* **Database:** SQLite (Relational, Parameterized Queries)
* **DevOps:** Docker, Docker Compose

## ⚙️ How to Run Locally

### Prerequisites
* Docker and Docker Compose installed on your machine.
* A Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather)).

### Quick Start
1. Clone the repository.
2. Create a `.env` file in the `Bot/` directory with your token:
   ```env
   TELEGRAM_TOKEN=your_token_here
   DB_PATH=/app/Data/bot_logs.db
3. Run the orchestration command from the root directory:
```Bash
docker-compose up --build
```

The Bot will start listening for messages on Telegram immediately, and the .NET API will be available on http://localhost:5000.

### 📡 API Endpoints
`GET /api/logs`
Retrieves paginated interaction logs.

Query Parameters:
* page (optional, default 1): The page number.
* size (optional, default 10, max 50): The number of records per page.

Example Request:
`GET http://localhost:5000/api/logs?page=2&size=5`

Example Response:

```JSON
{
  "page": 2,
  "pageSize": 5,
  "data": [
    {
      "id": 42,
      "telegramUserId": 123456789,
      "username": "johndoe",
      "messageText": "Hello bot!",
      "timestamp": "2026-07-16 14:30:00"
    }
  ]
}
```
### 👨‍💻 About the Developer
Developed by an Information Systems Engineering student at UTN. With solid foundations in UML system design, theoretical SQL, and algorithmic logic, this project was built to showcase cross-ecosystem integration, secure credential management, and clean, scalable architectural principles for modern Backend and Data Engineering roles.