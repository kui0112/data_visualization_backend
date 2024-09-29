import json
from log import logger_factory
from typing import Dict, List

logger = logger_factory.get_logger(__name__)


class TreeNode:
    def __init__(self, _id="", value="", level=0, _type="", branch=""):
        self.id: str = _id
        self.text: str = value
        self.level: int = level
        # type 有三种，root、sub、leaf
        self.type: str = _type
        self.branch = branch
        self.children: list = []

    def to_graph_node(self):
        return {
            "id": self.id,
            "data": {
                "branch": self.branch,
                "text": self.text,
                "level": self.level,
                "type": self.type
            },
            # "children": [v.to_graph_node() for v in self.children]
        }

    def to_dict(self):
        data = {
            "id": self.id,
            "text": self.text,
            "level": self.level,
            "type": self.type,
            "branch": self.branch,
            "children": [v.to_dict() for v in self.children]
        }

        return data

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self):
        return self.to_json()


class KnowledgeGraphService:
    def __init__(self):
        self.branch_flag = 0
        self.cache = dict()

    def read_raw_data(self, path: str):
        if not path:
            logger.error(f"file not found: {path}.")
            return None
        if path in self.cache:
            return self.cache[path]

        logger.debug(f"reading data in {path}.")
        data: Dict = json.load(open(path, "r", encoding="utf-8"))
        logger.debug(f"reading data in {path} finish.")
        self.cache[path] = data
        return data

    def get_graph_data(self, name: str, path: str):
        tree = self.translate_tree(name, path)
        nodes = [tree.to_graph_node()]
        edges = []
        self._tree_to_graph(tree, nodes, edges)
        return {
            "nodes": nodes,
            "edges": edges
        }

    def _tree_to_graph(self, parent: TreeNode, nodes: list, edges: list):
        children: List[TreeNode] = parent.children
        for v in children:
            nodes.append(v.to_graph_node())
            edges.append({
                "source": parent.id,
                "target": v.id
            })
            self._tree_to_graph(v, nodes, edges)

    def translate_tree(self, name: str, path: str):
        # 计数器，用于生成节点id
        counter = [0]
        # 节点层级
        level = 0
        # 根节点
        root = TreeNode(str(counter[0]), name, level, "root", str(0))
        self.branch_flag = 1
        counter[0] += 1

        # 原始数据
        raw = self.read_raw_data(path)
        logger.debug(f"raw data: {raw}")
        self._translate_sub_tree(root, raw, level + 1, counter)
        logger.debug(f"translated data: {root}")

        return root

    def _translate_sub_tree(self, parent, children, level, counter):
        # 如果子节点是字符串
        if isinstance(children, str):
            parent.children.append(TreeNode(str(counter[0]), children.strip(), level, "leaf", str(self.branch_flag)))
            counter[0] += 1
        # 如果子节点是列表
        elif isinstance(children, list):
            for i, v in enumerate(children):
                if isinstance(v, str):
                    node = TreeNode(str(counter[0]), v.strip(), level, "leaf", str(self.branch_flag))
                    parent.children.append(node)
                    counter[0] += 1
                    continue

                node = TreeNode(str(counter[0]), str(i), level, "sub", str(self.branch_flag))
                parent.children.append(node)
                counter[0] += 1
                self._translate_sub_tree(node, v, level + 1, counter)
        elif isinstance(children, dict):
            for k, v in children.items():
                node = TreeNode(str(counter[0]), k, level, "sub", str(self.branch_flag))
                parent.children.append(node)
                counter[0] += 1
                self._translate_sub_tree(node, v, level + 1, counter)
                if level == 1:
                    self.branch_flag += 1
        else:
            # 其他数据类型直接丢弃
            logger.warning(f"unprocessable children data type: {type(children)}, children value: {children}.")


if __name__ == '__main__':
    service = KnowledgeGraphService()
    t = service.translate_tree("苹果", "static/objects/苹果_240909103649/苹果_423655173693215_kg.json")
    print(t.to_json())
    g = service.get_graph_data("苹果", "static/objects/苹果_240909103649/苹果_423655173693215_kg.json")
    print(json.dumps(g, ensure_ascii=False))

    # for n in g["nodes"]:
    #     n["text"] = n["data"]["text"]
    #     n["level"] = n["data"]["level"]
    #     n["type"] = n["data"]["type"]
    #     del n["data"]
    # print(json.dumps(g, ensure_ascii=False))
