"""
Configuration settings for the Discord notification bot.
"""

import pytz
from datetime import time

# Discord Configuration
CHANNEL_NAME = "〔🐉〕yohara-spawn"

# Timezone Configuration
BUCHAREST_TZ = pytz.timezone('Europe/Bucharest')

# Schedule Configuration
START_TIME = time(12, 10)  # 12:10 PM

# Game Spawn Messages and Schedules
SPAWN_CONFIGS = [
    {
        "name": "Temintia Misterioasa V5",
        "message": "Sefii din Temintia Misterioasa V5 apar in 5 min !!!",
        "followup_message": "Sefii din Temnita Misterioasa V5 au aparut !!!",
        "interval_hours": 2,
        "job_id": "temintia_spawn",
        "followup_job_id": "temintia_followup"
    },
    {
        "name": "Pustietate",
        "message": "Sefii din Pustietate isi fac aparitia in 5 min !!!",
        "followup_message": "Sefii din Pustietate au aparut !!!",
        "interval_hours": 3,
        "job_id": "pustietate_spawn",
        "followup_job_id": "pustietate_followup"
    },
    {
        "name": "Canionul Nordic",
        "message": "Sefii din Canionul Nordic isi fac aparitia in 5 min !!!",
        "followup_message": "Sefii din Canionul Nordic au aparut !!!",
        "interval_hours": 4,
        "job_id": "canion_spawn",
        "followup_job_id": "canion_followup"
    }
]

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
