from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get('/', response_class=HTMLResponse)
def get_root():
    with open('test.html','r', encoding='utf8') as file:
        return file.read()
