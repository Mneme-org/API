import uvicorn
from api import config

if __name__ == "__main__":
    uvicorn.run("api:app", host=config.host, port=config.port, log_level="info")
