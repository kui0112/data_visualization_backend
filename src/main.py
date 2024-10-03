import asyncio
import json

import click
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

from object_service import ObjectService
from connection_manager import ConnectionManager, Connection
from log import logger_factory
from config import Config
from utils import Res

logger = logger_factory.get_logger(__name__)

service = ObjectService("static/objects")
manager = ConnectionManager()

cfg = Config()
store = {
    "current_object_name": "显卡"
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def static_resource_cors_middleware(request: Request, call_next):
    if request.url and request.url.path.startswith("/static"):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    return await call_next(request)


@app.get("/index", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/assets/{item}")
def assets(item: str):
    if item and item.endswith("js"):
        return FileResponse(f"static/assets/{item}", media_type="text/javascript")

    return FileResponse(f"static/assets/{item}")


@app.get("/object_names")
async def object_names():
    return service.get_object_names()


@app.get("/update_display")
async def update_display(object_name: str):
    if object_name not in service.get_object_names():
        logger.warning("unknown object name.")
        return Res.message("unknown object name")
    print("update_display")
    store["current_object_name"] = object_name
    await manager.publish(json.dumps(Res.update(name=object_name)))
    return Res.message("success")


@app.get("/current_object_name")
def current_object_name():
    return Res.message(store.get("current_object_name"))


@app.get("/vectors")
def vectors(object_name: str):
    return Res.message(service.get_vectors(object_name))


@app.get("/pictures")
def pictures(object_name: str):
    return Res.message(service.get_images_and_subtitles(object_name))


@app.get("/knowledge_graph")
def knowledge_graph(object_name: str):
    # 知识图谱
    data = service.get_knowledge_graph_data(object_name)
    # 知识图谱图片
    images = service.get_image_urls(object_name)
    return Res.message({"name": object_name, "data": data, "images": images})


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    conn = Connection(ws)
    await manager.connect(conn)
    while conn.active:
        try:
            await conn.send(json.dumps(Res.heartbeat()))
            await conn.receive()
            await asyncio.sleep(1)
        except Exception as ex:
            logger.debug(ex)
            await manager.disconnect(conn)


@click.command()
@click.option('--config', default='config.json', help='Path to the configuration file (default: config.json).')
def main(config: str):
    cfg.parse(config)
    logger_factory.set_level(cfg.log_level)
    service.set_base_directory(cfg.static_objects_directory)

    uvicorn.run(app, host="0.0.0.0", port=9999)


if __name__ == '__main__':
    main()
