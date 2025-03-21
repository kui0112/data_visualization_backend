import asyncio
import json
import random

import click
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

from object_service import ObjectService
from log import logger_factory
from config import Config
from utils import Res, WebSocketsManager

logger = logger_factory.get_logger(__name__)

service = ObjectService("static/objects")

cfg = Config()
CURRENT = "nothing"
CURRENT_PROB = 0
manager = WebSocketsManager()

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
async def update_display(object_name: str, prob: float):
    if not object_name:
        logger.warning("object_name can not be blank.")
        return Res.message("object_name can not be blank.")

    if object_name != "nothing" and object_name not in service.get_object_names():
        logger.warning("unknown object name.")
        return Res.message("unknown object name")

    logger.info(f"update_display: {object_name}")
    global CURRENT, CURRENT_PROB
    CURRENT = object_name
    CURRENT_PROB = prob
    await manager.publish(json.dumps({"object_name": object_name, "prob": prob}, ensure_ascii=False))
    return Res.message("success")


@app.get("/current_object_name")
async def current_object_name():
    return Res.message(CURRENT)


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
    images = service.get_knowledge_image_urls(object_name)
    return Res.message({"name": object_name, "data": data, "images": images})


@app.get("/knowledge_graph_ex")
def knowledge_graph_ex(object_name: str):
    # 知识图谱, all in one
    return Res.message({"name": object_name, "data": service.get_knowledge_graph_data_ex(object_name)})


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await manager.add(ws)
    try:
        while True:
            await ws.send_text(json.dumps({"object_name": CURRENT, "prob": CURRENT_PROB}, ensure_ascii=False))
            await ws.receive()
            await asyncio.sleep(1.0 + random.random() * 0.5)
    except Exception as ex:
        await manager.remove(ws)
        logger.debug(ex)


@click.command()
@click.option('--config', default='config.json', help='Path to the configuration file (default: config.json).')
def main(config: str):
    cfg.parse(config)
    logger_factory.set_level(cfg.log_level)
    service.set_base_directory(cfg.static_objects_directory)

    uvicorn.run(app, host="0.0.0.0", port=9999)


if __name__ == '__main__':
    main()
