import json
import logging
import os
import subprocess
import sys

import yaml
from minio import Minio
from pydantic import BaseModel, Field

log = logging.getLogger('uploader')

upload_file_path = sys.argv[1]


class Setting(BaseModel):
    endpoint: str = Field(description="Endpoint")
    bucket: str = Field(description="Bucket name. default: screenshot", default='screenshot')
    public_dir: str = Field(description="Save directory name. default: public", default='public')
    access_key: str = Field(description='Minio s3 access_key')
    secret_key: str = Field(description='Minio s3 secret_key')


def load_config():
    # 获取用户目录路径
    user_dir = os.path.expanduser("~")

    configfile = ".flameshot-uploader.yaml"
    # 拼接文件的完整路径
    file_path = os.path.join(user_dir, configfile)
    # file_path = configfile

    # 检测配置文件是否存在
    if os.path.isfile(file_path):
        with open(file_path) as file:
            config_data = yaml.safe_load(file.read())
            json_data = json.dumps(config_data)
            return Setting.model_validate_json(json_data, strict=True)
    else:
        log.error(
            f"The configuration file does not exist. Please refer to `.flameshot-uploader.yaml` for configuration.")


try:
    config = load_config()
    if os.path.isfile(upload_file_path):
        filename = upload_file_path.rsplit('/', 1)[1]
        client = Minio(
            endpoint=config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
        )
        found = client.bucket_exists(config.bucket)
        if not found:
            client.make_bucket(config.bucket)
            log.info("Created bucket", config.bucket)
        else:
            log.info("Bucket", config.bucket, "already exists")

        client.fput_object(
            bucket_name=config.bucket,
            object_name=f'/{config.public_dir}/{filename}',
            file_path=upload_file_path,
            content_type='image/jpeg'
        )
        template = f"""notify-send "Upload successful!" "<a href='https://{config.endpoint}/{config.bucket}/{config.public_dir}/{filename}'>View screenshots</a>" --icon=cloud-upload && echo 'https://{config.endpoint}/{config.bucket}/{config.public_dir}/{filename}'"""
        # 执行Shell命令
        output = subprocess.run(template, shell=True, capture_output=True, text=True)
        # 输出命令的执行结果
        print(output.stdout)

except IndexError as e:
    log.error('file not found error')
