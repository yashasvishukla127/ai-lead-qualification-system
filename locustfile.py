# locustfile.py
from locust import HttpUser, task, between
import uuid

LEAD_TEXT = (
    "Sarah runs a 15-person e-commerce startup. Her team spends 3 hours daily "
    "on manual reporting and is actively evaluating automation tools this quarter."
)


class LeadAnalyserUser(HttpUser):
    wait_time = between(1, 2)   # seconds between tasks per user

    @task(5)                     # weighted: 5x more likely than health
    def analyse_lead(self):
        self.client.post(
            "/api/v1/analyse-lead",
            json={"lead_text": LEAD_TEXT},
            headers={"x-request-id": str(uuid.uuid4())},
            name="/api/v1/analyse-lead",   # groups results in UI
        )

    @task(1)
    def health_check(self):
        self.client.get("/health", name="/health")