to run every thing - 
uvicorn src.main:app --reload --port 8000

**Open Swagger UI:**
http://localhost:8000/docs

**to run test**
Run tests:
pytest test_api.py -v
pytest test_errors.py -v
pytest test_pipeline.py -v