@echo off
REM run_load_tests.bat
REM Run this with your FastAPI server already started: uvicorn main:app --port 8000

mkdir results 2>nul

echo Running 1 user...
locust -f locustfile.py --headless -u 1 -r 1 --run-time 60s --host http://localhost:8000 --csv results/load_u1 --html results/load_u1.html

echo Running 10 users...
locust -f locustfile.py --headless -u 10 -r 2 --run-time 60s --host http://localhost:8000 --csv results/load_u10 --html results/load_u10.html

echo Running 50 users...
locust -f locustfile.py --headless -u 50 -r 5 --run-time 60s --host http://localhost:8000 --csv results/load_u50 --html results/load_u50.html

echo Running 200 users...
locust -f locustfile.py --headless -u 200 -r 20 --run-time 60s --host http://localhost:8000 --csv results/load_u200 --html results/load_u200.html

echo All done. Running graph generator...
python generate_load_graph.py