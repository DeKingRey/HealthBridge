from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

"""TEMPORARY - DEVELOPMENT ONLY (hopefully)
Follow these steps to initialize celery:
1. Open docker desktop

2. Create redis container with:
    docker run -p 6379:6379 redis

3. Verify docker is working with:2
    docker ps

4. Start celery worker with:
    celery -A celery_worker.celery worker --pool=solo --loglevel=info
"""
