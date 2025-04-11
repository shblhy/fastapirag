import os
import pathlib
from exlib.config import Config as Config_
from exlib.config.yaml import YamlEngine

PROJ_NAME = 'ragproj_fastapi'
BASE_DIR = pathlib.Path(__file__).parent.parent
SOURCE_DIR = os.environ.get('SOURCE', BASE_DIR)
CONFIG_YML = os.path.join(SOURCE_DIR, 'local_config.yaml')
if not os.path.exists(CONFIG_YML):
    CONFIG_YML = os.path.join(os.path.join(SOURCE_DIR, PROJ_NAME), 'config.yaml')


class Config(Config_):
    _engines = [YamlEngine('default', CONFIG_YML, 'yaml_keys')]
    yaml_keys = [
        'env',  # 取值有 local / test / gray / prod / future 五种
        # 'database',
        'db_path',
        'cors_allowed_origins',
        'redis',
        'log_dir_path',
        'allow_hosts',
        'csrf_trusted_origins',
        'website_path',
        'debug__bool',
        'ali_bucket',
        'kimi_api_key',
        'jwt_secret_key',
        'signature_group',
        'TRANSFORMERS_CACHE',
        'VECTOR_MODEL',
        'aimlapi_api_key',
        'deepseek_api_key',
        'toutiao_api_key'
    ]



LOCAL_RUN = False

try:
    from local_config import *
except:
    pass

conf = Config()
