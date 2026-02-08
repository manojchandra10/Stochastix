from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cortex.app.api.v1 import endpoints
from cortex.app.core.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stochastix Cortex API",
    version="1.0.0",
    description="The Neural Network Backend for Stochastix."
)

# CORS (Cross-Origin Resource Sharing)
# origins = [
#     "http://localhost:5173",    # Vite default
#     "http://127.0.0.1:5173"
#     # "https://stochastix.com",   # my future domain
#     # "https://www.stochastix.com"
# ]

origins = [
    "http://localhost:5173",    #  Vite default
    "http://127.0.0.1:5173",
    "http://localhost:3000",    # Docker Frontend Port
    "http://127.0.0.1:3000"    # Docker Frontend IP
    # "https://stochastix.com", # my future domain
    # "https://www.stochastix.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origins=["*"], # Temporarily allow all for local debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our routes
app.include_router(endpoints.router, prefix="/api/v1", tags=["Forecast"])

@app.get("/")
def health_check():
    return {"status": "online", "system": "Cortex v1.0"}