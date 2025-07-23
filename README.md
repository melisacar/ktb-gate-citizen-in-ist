# Istanbul Border Gate Citizen Entry Monitoring System

ETL pipeline for processing monthly citizen entry data from Istanbul border gates, sourced from Turkish Ministry of Culture and Tourism reports.

## Key Features

- **Automated Data Collection**:
  - Scrapes Excel reports from [Turkish Ministry of Culture](https://yigm.ktb.gov.tr/) containing monthly border gate entries (2022-present)
  - Handles both `.xls` (xlrd) and `.xlsx` (openpyxl) formats
  - Robust error handling for HTTP requests and file downloads

- **Data Processing**:
  - Cleans Istanbul-specific entry data from national reports
  - Normalizes Turkish month names (e.g., "Şubat" → "subat") and maps to integers
  - Converts wide-format Excel data to long-form DataFrame
  - Handles special characters and text normalization (Unicode → ASCII)

- **Database Integration**:
  - Stores processed data in PostgreSQL under `etl.ist_sinir_kapilari_giris_yapan_vatandas`
  - Implements composite unique constraints on (tarih, sehir, sinir_kapilari)
  - Transaction management with session rollback on failures
  - Duplicate prevention with `ON CONFLICT` checks

- **Production-Ready Pipeline**:
  - Containerized with Docker (Airflow + PostgreSQL + Redis)
  - Scheduled via Airflow DAG (`02_03_ktb_pipe_etl_ist_sinir_kapilari_giris_yapan_vatandas`)
  - Detailed logging at all processing stages
  - Automatic retry logic for failed operations

- **Local Development**:
  - Pre-configured docker-compose environment
  - Alembic migrations for schema management
  - Sample test cases in `/tests`

---

## Project Structure

```bash
ktb-gate-citizen-in-ist/
├── dags/
│ └── 02_03.py          # Main Airflow DAG
├── logs/               # Airflow execution logs
├── plugins/            # Custom operators/hooks
├── src/
│ ├── __init__.py
│ ├── config.py         # Configuration
│ ├── main.py           # Core ETL logic
│ ├── models.py         # SQLAlchemy models
│ ├── alembic.ini       
├── migrations/         # Alembic migrations
├── .gitignore
├── docker-compose.yaml # Airflow+PostgreSQL setup
├── Dockerfile
├── LICENSE
├── README.md
└── requirements.txt    # Python dependencies
```

---

## Technologies Used

- **Python**
- **PostgreSQL**
- **SQLAlchemy**
- **BeautifulSoup** for HTML parsing
- **Docker**
- **Apache Airflow** for scheduling
- **Alembic** for migrations

---

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/melisacar/ktb-gate-citizen-in-ist.git
    ```

    ```bash
    cd ktb-gate-citizen-in-ist
    ```

2. Build and start the services using Docker Compose (Airflow & PostgreSQL):

    ```bash
    docker-compose up airflow-init
    docker-compose up -d --build
    ```

3. Install dependencies locally (optional if not using Docker):

    ```bash
    pip install -r requirements.txt
    ```

4. Configure your database connection in src/config.py or environment variables as needed.

5. Run Alembic migrations to create the database schema:

    ```bash
    alembic upgrade head
    ```

6. Access the Airflow UI at: [http://127.0.0.1:8080](http://127.0.0.1:8080)

    - Username: `airflow`
    - Password: `airflow`

7. The DAG defined in the `dags/` folder will appear in the Airflow UI. You can trigger it manually or set a schedule.

---

## Database Schema

**Schema**: `etl`  
**Table**: `ist_sinir_kapilari_giris_yapan_vatandas`

| Column Name        | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| `id`               | int     | Primary key (autoincrement)              |
| `tarih`            | date    | Reporting month                          |
| `sehir`            | string  | Name of the city                         |
| `sinir_kapilari`   | string  | Name of the border gate                  |
| `vatandas_sayisi`  | float   | Number of entries (citizen)              |
| `erisim_tarihi`    | date    | Date when the record was inserted        |

> Unique constraint on (`tarih`, `sehir`, `sinir_kapilari`)

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
