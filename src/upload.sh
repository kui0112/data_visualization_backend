# 全部同步
scp -r -P 27845 ./src/* root@103.40.13.76:/root/data_visualization/src
# 同步代码
scp -r -P 27845 ./src/*.py root@103.40.13.76:/root/data_visualization/src
# 同步static
scp -r -P 27845 ./src/static/* root@103.40.13.76:/root/data_visualization/src/static/

scp -r -P 27845 ./src/static/tick.mp3 root@103.40.13.76:/root/data_visualization/src/static/tick.mp3

# 同步objects
scp -r -P 27845 ./src/static/objects/显卡* root@103.40.13.76:/root/data_visualization/src/static/objects/

