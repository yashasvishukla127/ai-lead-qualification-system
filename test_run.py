import asyncio
from src.services.lead_service import analyse_lead

async def test():
    for i in range(5):
        try:
            result = await analyse_lead(
                "Sarah runs a 15-person startup spending 3hrs/day on manual reporting."
            )
            print(f"{i} -> SUCCESS")
            print(result)
        except Exception as e:
            print(f"{i} -> FAILED: {e}")

asyncio.run(test())