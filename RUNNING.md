# Running the FastAPI Server

To start the FastAPI server, use the following command:

```bash
# Make sure you're in the project root directory
python run.py
```

This will start the server with the following configuration:
- Host: 0.0.0.0 (accessible from other devices on the network)
- Port: 8000
- Auto-reload: Enabled (for development)

For production deployment, you should use a production-grade ASGI server like Uvicorn with Gunicorn:

```bash
# Install gunicorn if not already installed
pip install gunicorn

# Run with Gunicorn as process manager
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

Where:
- `-w 4`: Runs 4 worker processes
- `-k uvicorn.workers.UvicornWorker`: Uses the Uvicorn ASGI worker
