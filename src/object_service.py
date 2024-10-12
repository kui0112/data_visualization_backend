import json
import os
import random
import re
from typing import Dict, List, Set

from knowledge_graph_service import KnowledgeGraphService
from log import logger_factory

logger = logger_factory.get_logger(__name__)


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
        res = list(filter(lambda x: str.endswith(x, "kg.json"), files))
        if res:
            file = f"{object_path}/{res[0]}"
            return self.knowledge_graph_service.get_graph_data(name, file)
        return None

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

    def _get_images_and_subtitles(self, object_path: str):
        path = f"{object_path}/images"
        files = os.listdir(path)
        subtitle_files: List[str] = list(filter(lambda x: re.match(r"\d+\.txt", x), files))
        subtitle_files.sort(key=lambda x: int(x.replace(".txt", "")))
        segments = []
        for subtitle_file in subtitle_files:
            segment_id = subtitle_file.replace(".txt", "")
            segment_images = []
            segment_videos = []
            for f in files:
                m = re.match(rf"^{segment_id}_\d+\.jpg$", f)
                if m is not None:
                    segment_images.append(m.string)
                m = re.match(rf"^{segment_id}_.*\.mp4$", f)
                if m is not None:
                    segment_videos.append(m.string)

            if not segment_images:
                continue

            random_image_file = f"/{path}/{random.choice(segment_images)}" if segment_images else ""
            random_video_file = f"/{path}/{random.choice(segment_videos)}" if segment_videos else ""

            with open(f"{path}/{subtitle_file}", "r", encoding="utf-8") as f:
                segment = {
                    "id": segment_id,
                    "image": random_image_file,
                    "video": random_video_file,
                    "subtitle": f.read()
                }
                segments.append(segment)
        return segments

    def get_images_and_subtitles(self, name: str):
        paths = self.object_paths[name][:]
        if not paths:
            return []
        # 打乱顺序
        random.shuffle(paths)
        segments = []
        for i, obj_path in enumerate(paths):
            current_segments = self._get_images_and_subtitles(obj_path)
            for seg in current_segments:
                seg["id"] = f"{i}{seg['id']}"
            segments.extend(current_segments)
        print(json.dumps(segments))
        return segments

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
