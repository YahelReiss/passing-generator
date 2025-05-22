from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.graph_builder import build_graph

app = FastAPI()

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/graph")
def get_graph(
    num_balls: int = Query(..., description="Number of balls"),
    max_throw: int = Query(..., description="Maximum throw height"),
):
    
    graph = build_graph(num_balls, max_throw)
    return graph
