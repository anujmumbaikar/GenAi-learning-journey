# flake8: noqa
from fastapi import FastAPI,Query,Path
from .queue.connection import queue
from .queue.worker import process_query
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.post("/chat")
def chat(
    query: str = Query(..., description="User query"),
    #we have taken a query from the user 
):
    #next after user query we have to put it into queue .
    #So we willl use RQ 
    job = queue.enqueue(process_query, query)
    #job means information about the job that is being processed
    return {"message": "Query received", "job_id": job.id}

@app.get("/result/{job_id}")
def get_result(
    job_id:str = Path(... , description="Job ID")
):
    job = queue.fetch_job(job_id = job_id)
    result = job.return_value()
    return {"result":result}
    