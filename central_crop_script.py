import os
from PIL import Image


def rm_recursive(path):
    if os.path.isdir(path):
        for f in os.listdir(path):
            p = os.path.join(path, f)
            if os.path.isdir(p):
                rm_recursive(p)
            else:
                os.remove(p)
        os.rmdir(path)
    else:
        os.remove(path)


def main():
    objects_dir = "src/static/objects"
    for object_dir in os.listdir(objects_dir):
        object_dir_abs = os.path.join(objects_dir, object_dir)
        image_dir = os.path.join(object_dir_abs, "images")

        output_dir = os.path.join(object_dir_abs, "images_square")
        if os.path.exists(output_dir):
            rm_recursive(output_dir)
        os.mkdir(output_dir)

        for file in os.listdir(image_dir):
            if not file.endswith(".jpg"):
                continue
            image_path = os.path.join(image_dir, file)
            output_path = os.path.join(output_dir, file)
            with Image.open(image_path) as img:
                width, height = img.size
                new_size = min(width, height, 256)
                new_width = new_height = new_size

                left = (width - new_width) / 2
                top = (height - new_height) / 2
                right = (width + new_width) / 2
                bottom = (height + new_height) / 2

                new_img = img.crop((left, top, right, bottom))
                new_img.save(output_path)


if __name__ == '__main__':
    main()
