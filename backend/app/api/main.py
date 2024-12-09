from fastapi import FastAPI
import app.api.routers.spaces as spaces
import app.api.routers.nametags as nametags


app = FastAPI()

app.include_router(spaces.router)
app.include_router(nametags.router)