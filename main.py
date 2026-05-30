import uvicorn
import os
import sys

# Asegurarnos de que el root está en el sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from interfaces.api.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
