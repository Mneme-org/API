import uvicorn
from api.utils import read_config

host, port, workers = read_config()

if __name__ == "__main__":
    uvicorn.run("api:app", host=host, port=port, log_level="info", workers=workers)
