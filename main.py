import time
import uuid
from fastapi import FastAPI, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

# -------------------------------------------------------------
# 1. STRICT CORS POLICY CONFIGURATION
# -------------------------------------------------------------
# Replace this string exactly with your assigned allowed origin
ALLOWED_ORIGIN = "https://dash-bje4te.example.com"

# Standard CORSMiddleware can sometimes behave unexpectedly with 
# non-matching origins during preflights depending on the setup. 
# To ensure "evil" origins are strictly rejected with NO ACAO header,
# we intercept and validate the Origin header carefully.
@app.middleware("http")
async def cors_validation_middleware(request: Request, call_next):
    origin = request.headers.get("Origin")
    
    # Handle Preflight (OPTIONS) or standard requests containing an Origin header
    if origin and origin != ALLOWED_ORIGIN:
        if request.method == "OPTIONS":
            # Strictly reject evil preflights by returning a blank response with NO ACAO
            return Response(status_code=400)
    
    response = await call_next(request)
    
    # Explicitly set the header only for the allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
    return response


# -------------------------------------------------------------
# 2. REQUIRED MIDDLEWARE HEADERS (X-Request-ID & X-Process-Time)
# -------------------------------------------------------------
class CustomHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        
        # Inject the required custom headers into every response
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        
        return response

app.add_middleware(CustomHeadersMiddleware)


# -------------------------------------------------------------
# 3. GET /stats ENDPOINT
# -------------------------------------------------------------
@app.get("/stats")
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    # Parse the comma-separated integers
    try:
        numbers = [int(x.strip()) for x in values.split(",") if x.strip()]
    except ValueError:
        return Response(content='{"error": "Invalid integer format"}', status_code=400, media_type="application/json")
    
    if not numbers:
        return Response(content='{"error": "No numbers provided"}', status_code=400, media_type="application/json")

    # Compute statistics
    n = len(numbers)
    s = sum(numbers)
    m = min(numbers)
    x = max(numbers)
    mean = s / n
    
    # TODO: Replace 'your.email@example.com' with your actual platform login email
    return {
        "email": "23f2001721@ds.study.iitm.ac.in", 
        "count": n,
        "sum": s,
        "min": m,
        "max": x,
        "mean": round(mean, 2)
    }