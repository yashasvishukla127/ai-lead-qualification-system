from pathlib import Path

# This gives the absolute folder path of the executing script
file_dir = Path(__file__).resolve().parent
print(f"File directory: {file_dir}")



import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from src.utils.logger import correlation_id_var


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    #   here in Requeset - we have kept what request we were processing 
    async def dispatch(self, request: Request, call_next) -> Response:
        
        # flow -> 2 -  Use incoming header or generate a fresh UUID
        cid = request.headers.get("x-request-id", str(uuid.uuid4()))  
        token = correlation_id_var.set(cid)  # bind to this async context / so that later memory 
        
        # flow -> 2 - for this paritcular request we can get the correlation id and                                        # could get cleaned of 

        try:              # flow -> 3 - call the next middleware   
                          #  <- will go back to main.py continue the request
            response: Response = await call_next(request)
        finally:
            correlation_id_var.reset(token)  # always clean up

        response.headers["x-request-id"] = cid  # echo it back in response
        return response