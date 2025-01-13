from fastapi import FastAPI

app =  FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World to my FastAPI app"}

@app.get("/product_service")
def read_root():
    return {"Hello": "Microserver for product service"}