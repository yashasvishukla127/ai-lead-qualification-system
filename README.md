to run every thing - 
uvicorn src.main:app --reload --port 8000

**Open Swagger UI:**
http://localhost:8000/docs

**to run test**
Run tests:
pytest tests/test_api.py -v
pytest tests/test_errors.py -v
pytest tests/test_pipeline.py -v