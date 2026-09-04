import asyncio
import logging

from app.jobs.persona_scheduler import trigger_persona_discussions_job

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    res = asyncio.run(trigger_persona_discussions_job())
    print("PERSONA DISCUSSIONS RESULT:", res)
