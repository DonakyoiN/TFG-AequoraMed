from fastapi import FastAPI

app = FastAPI()

# API Base de la documentación de FastAPI - Para que Funcione
# TODO: API de la aplicación
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}