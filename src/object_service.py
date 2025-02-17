import json
import os
import random
import re
from typing import Dict, List, Set

from knowledge_graph_service import KnowledgeGraphService
from log import logger_factory

logger = logger_factory.get_logger(__name__)

name_map = {
    "苹果": "apple",
    "显卡": "graphics card",
    "石头": "rock",
    "软盘": "floppy disk",
    "树木枝干": "tree branch",
    "汽车": "car",
    "国际象棋": "chess",
    "手机": "smart phone",
    "锤子": "hammer",
    "枪": "gun",
    "锁与钥匙": "lock and keys",
    "闹钟": "alarm",
    "发卡": "hair clip",
    "布洛芬": "ibuprofen",
}


def get_name_en(name_zh: str):
    return name_map.get(name_zh) or name_zh


class ObjectService:
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.object_paths: Dict[str, List[str]] = dict()
        self.object_names: Set[str] = set()
        self.object_alias: Dict[str, List[str]] = dict()

        self.knowledge_graph_service = KnowledgeGraphService()

        self._scan()

    def set_base_directory(self, base_directory: str):
        self.base_directory = base_directory
        self.object_paths: Dict[str, List[str]] = dict()
        self.object_names: Set[str] = set()
        self.object_alias: Dict[str, List[str]] = dict()
        self._scan()

    def _scan(self):
        logger.debug(f"scanning directory {self.base_directory}.")
        if not self.base_directory or not os.path.exists(self.base_directory):
            logger.error("the directory to be scanned does not exist.")
            return
        files = os.listdir(self.base_directory)
        for file in files:
            name = file.strip().split("_")[0]
            path: str = f"{self.base_directory}/{file}"
            self.object_names.add(name)
            if self.object_paths.get(name) is None:
                self.object_paths[name] = []
            self.object_paths[name].append(path)
        logger.debug(f"scanning directory {self.base_directory} finish.")

    def get_object_names(self):
        return self.object_names

    def get_knowledge_graph_data(self, name: str):
        object_path = random.choice(self.object_paths[name])
        files = os.listdir(object_path)

        kg_files = list(filter(lambda x: str.endswith(x, "kg.json"), files))
        if kg_files:
            file = f"{object_path}/{kg_files[0]}"
            return self.knowledge_graph_service.get_graph_data(name, file)

        return None

    def get_knowledge_graph_data_ex(self, name: str):
        object_path = random.choice(self.object_paths[name])
        files = os.listdir(object_path)
        res = {
            "shape": dict(),
            "zh": dict(),
            "en": dict(),
            "image": dict()
        }

        files_zh = list(filter(lambda x: str.endswith(x, "kg.json"), files))
        if not files_zh:
            logger.error(f"knowledge graph file not found in {object_path}.")
            return None

        file = f"{object_path}/{files_zh[0]}"
        shape = self.knowledge_graph_service.get_graph_data(name, file)
        for node in shape["nodes"]:
            res["zh"].update({node["id"]: node["data"]["text"]})
        for node in shape["nodes"]:
            del node["data"]["text"]
        res["shape"] = shape

        files_en = list(filter(lambda x: str.endswith(x, "kg_en.json"), files))
        if not files_en:
            logger.error(f"knowledge graph en file not found in {object_path}.")
            return res

        file = f"{object_path}/{files_en[0]}"
        res_en = self.knowledge_graph_service.get_graph_data(name, file)
        for node in res_en["nodes"]:
            if node["id"] == '0':
                res["en"].update({node["id"]: get_name_en(node["data"]["text"])})
            else:
                res["en"].update({node["id"]: node["data"]["text"]})

        images = self.get_knowledge_image_urls(name)
        for node in shape["nodes"]:
            res["image"].update({node["id"]: random.choice(images)})

        return res

    def get_knowledge_image_urls(self, name: str):
        object_path = random.choice(self.object_paths[name])
        path = f"{object_path}/images_square"
        if not object_path or not os.path.exists(path) or not os.path.isdir(path):
            logger.error(f"directory not found: {path}.")
            return []

        files = list(filter(lambda x: str.endswith(x, ".jpg"), os.listdir(path)))
        urls = []
        for file in files:
            file_path: str = f"{path}/{file}".replace("/", os.path.sep)
            if os.path.exists(file_path):
                url = file_path.replace(os.path.sep, "/")
                urls.append(f"/{url}")
        return urls

    def read_all_lines(self, filename: str):
        res = []
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                stripped_line = line.strip()
                if line and stripped_line:
                    res.append(stripped_line)
        return res

    def _get_images_and_subtitles(self, object_path: str):
        # 获取字幕
        files_in_object_path = os.listdir(object_path)

        filtered = list(filter(lambda x: str.endswith(x, "structure-lang.txt"), files_in_object_path))
        if not filtered:
            logger.error(f"subtitle file zh not found in {object_path}.")
            return []
        subtitle_file_zh = filtered[0]
        subtitle_lines_zh = self.read_all_lines(f"{object_path}/{subtitle_file_zh}")

        filtered = list(filter(lambda x: str.endswith(x, "structure-lang_en.txt"), files_in_object_path))
        if not filtered:
            logger.error(f"subtitle file zh not found in {object_path}.")
            return []
        subtitle_file_en = filtered[0]
        subtitle_lines_en = self.read_all_lines(f"{object_path}/{subtitle_file_en}")

        if len(subtitle_lines_zh) != len(subtitle_lines_en):
            logger.warning("line count is not equal.")
            if len(subtitle_lines_zh) > len(subtitle_lines_en):
                for i in range(len(subtitle_lines_zh) - len(subtitle_lines_en)):
                    subtitle_lines_en.append("")

        path_images = f"{object_path}/images"
        files_in_images = os.listdir(path_images)

        segment_count = len(subtitle_lines_zh)

        segments = []
        for i in range(segment_count):
            segment_id = str(i)
            segment_images = []
            segment_videos = []
            for f in files_in_images:
                m = re.match(rf"^{segment_id}_\d+\.jpg$", f)
                if m is not None:
                    segment_images.append(m.string)
                m = re.match(rf"^{segment_id}_.*\.mp4$", f)
                if m is not None:
                    segment_videos.append(m.string)

            if not segment_images:
                continue

            random_image_file = f"/{path_images}/{random.choice(segment_images)}" if segment_images else ""
            random_video_file = f"/{path_images}/{random.choice(segment_videos)}" if segment_videos else ""

            segment = {
                "id": segment_id,
                "image": random_image_file,
                "video": random_video_file,
                "subtitle": subtitle_lines_zh[i],
                "subtitleEn": subtitle_lines_en[i],
            }
            segments.append(segment)

        return segments

    def get_images_and_subtitles(self, name: str):
        paths = self.object_paths[name][:]
        if not paths:
            return []
        # 随机播放一组
        obj_path = random.choice(paths)
        res = self._get_images_and_subtitles(obj_path)
        print(json.dumps(res))
        return res

    def get_vectors(self, name: str):
        object_path = random.choice(self.object_paths[name])
        files = os.listdir(object_path)
        res = list(filter(lambda x: "vector" in x, files))
        if res:
            file_path = f"{object_path}/{res[0]}"
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        return None


if __name__ == '__main__':
    service = ObjectService("static/objects")
    print(service.get_object_names())
    # print(service.get_vector_data("苹果"))
    # print(service.get_image_urls("苹果"))
    # print(service.get_knowledge_graph_data("苹果"))
    print(service.get_images_and_subtitles("苹果"))
