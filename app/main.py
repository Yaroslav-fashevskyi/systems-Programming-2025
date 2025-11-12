from fastapi import FastAPI

app = FastAPI(title="P4")

@app.get("/")
def hello_world():
    return {"Hello": "World"}

if __name__ == "__main__":
    # Локальний запуск через Python (спосіб №3)
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

