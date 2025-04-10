from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from config import conf
app = FastAPI()

origins = [
    # "http://localhost:5174",  # 根据需要更改，这里以 HBuilderX 默认开发端口为例
    # "ws://localhost:5174",
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
TORTOISE_ORM = {
    "connections": {"default": fr"sqlite://{conf.db_path}"},
    "apps": {
        "models": {
            "models": ["models", ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "logging": {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "WARNING",  # 将日志级别设置为 WARNING
            },
        },
        "loggers": {
            "tortoise": {
                "handlers": ["console"],
                "level": "WARNING",  # 将 Tortoise ORM 的日志级别设置为 WARNING
                "propagate": False,
            },
            "db_client": {
                "handlers": ["console"],
                "level": "WARNING",  # 将数据库客户端的日志级别设置为 WARNING
                "propagate": False,
            },
        }
    }
}

# 注册数据库
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)
