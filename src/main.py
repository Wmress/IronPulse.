from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

conn = sqlite3.connect("sensor.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    machine_id INTEGER,
    timestamp TEXT,
    event_type TEXT
)
""")
conn.commit()

# The attrabutes the sensor data should give us and how we will stort the data
class SensorData(BaseModel):
    machine_id: int
    timestamp: datetime
    event_type: str


# the client which is the sensor sent the data to the api and the api took it, accepted it and stores/process it etc. server to create something new
@app.post("/sensor-data")
def recieve_sensor_data(data: SensorData):

    cursor.execute(
        "INSERT INTO sensor_data (machine_id, timestamp, event_type) VALUES (?, ?, ?)",
        (data.machine_id, data.timestamp.isoformat(), data.event_type)
    )
    conn.commit()

    return {"status": "success", "data": data}

# Gets all the data from the sensor_data table uncleaned
@app.get("/all-data")
def get_all_data():
    cursor.execute("SELECT * FROM sensor_data")
    return cursor.fetchall()


#API Endpoint call to usage Summary which displays the data in a more readable manner
@app.get("/usage-summary")
def usage_summary():
    cursor.execute("""
    SELECT machine_id, COUNT(*) as usage_count
    FROM sensor_data
    WHERE event_type = 'start'
    GROUP BY machine_id               
""")
    rows = cursor.fetchall()

    return [
        {"machine_id": row[0], "usage_count": row[1]}
        for row in rows
    ]

@app.get("/peak-hours")
def peak_hours():
    cursor.execute("""
    SELECT strftime('%H', timestamp) as hour, COUNT(*)
    FROM sensor_data
    WHERE event_type = 'start'
    GROUP BY hour
    ORDER BY COUNT(*) DESC
    """)
    rows = cursor.fetchall()

    return [
        {"hour": row[0], "usage_count": row[1]}
        for row in rows
    ]