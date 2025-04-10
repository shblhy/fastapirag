import json
import logging
import traceback

VERSION = '0.11'
logger = logging.getLogger('default')


class Item(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


class Config:
    """
        config为一份配置，可能由来自多处的数据组成，各处的数据由各自的"引擎"engine提取。
        例如 代码上、环境变量上、类似阿波罗的配置中心里、外部配置接口获取。
        编写时，需要初始化引擎，设置属性的获取方式。
        对用户，就是 配置类.属性 的使用方式。无需关注属性是普通字段还是property方法。
        注意，engines按顺序执行，按顺序初始化各个字段。
    """
    _engines = []
    _engines_ = {}

    def __init__(self):
        self.setup_engine()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = object.__new__(cls)
        return cls._instance

    def setup_engine(self):
        for engine in self._engines:
            e = engine() if isinstance(engine, type) else engine
            e.init(self)    # 初始化引擎
            e.setup(self)
            self._engines_[e._name] = e

    def get_all_property_keys(self):
        keys = []
        for engine in self._engines:
            keys.extend(getattr(self, engine.target))
        return keys

    def get_all_keys(self):
        return self.get_all_property_keys()

    def get_ori_keys(self, keys):
        return [k.split('__')[0] if '__' in k else k for k in keys]

    def get_data(self, keys=None):
        keys = keys or self.get_all_keys()
        return {k: getattr(self, k) for k in self.get_ori_keys(keys)}

    def get_prefix_data(self, prefix):
        """
            按prefix_前缀获取数据
        :param prefix:
        :return:
        """
        keys = self.get_all_keys()
        data = {}
        for k in self.get_ori_keys(keys):
            if k.startswith(f'{prefix}_'):
                data[k.replace(f'{prefix}_', '', 1)] = getattr(self, k)
        # data = {k.replace(f'{prefix}_', '', 1): v for k, v in self.get_data().items() if k.startswith(f'{prefix}_')}
        return Item(**data)


def parse(r, format, value):
    parsers = {
        'json': lambda x: json.loads(x) if x else None,
        'int': lambda x: int(x) if x else None,
        'float': lambda x: int(x) if x else None
    }
    if format in parsers:
        return parsers[format](r)
    return r if r is not None else value


def get_property(name, format='str', value=None, engine=None):
    """
        返回一个 property,动态获取值，如果无法取得值，则提供上一次的数据。
    """
    def get(self):
        try:
            r = engine._get_value(name)
            self.__dict__[name] = parse(r, format, value)
        except Exception as e:
            # 开发之初logger可能未配置完，无法输出信息，但已经发生了错误。直接print能确保用户一定看到错误。
            traceback.print_exception(e)
            logger.exception(e)
        return self.__dict__[name]
    return property(get)


class ConfigEngine:
    def init(self, conf):
        """
            初始动作，如连接服务、确认文件等。
        :param conf:
        :return:
        """
        pass

    def setup(self, config):
        """
            为config设置property
        """
        if not hasattr(config, self.target):
            return
        keys = getattr(config, self.target)
        datas = {}
        if type(keys) is dict:
            datas = keys
            keys = list(datas.keys())
        if not keys:
            return
        for key in keys:
            if '__' in key:
                key, format = key.split('__')
            else:
                format = 'str'
            setattr(config.__class__, key, get_property(key, format, datas.get(key), engine=self))

    @property
    def _name(self):
        if hasattr(self, 'name'):
            return self.name
        return self.__class__.__name__

    def _get_value(self, name):
        raise NotImplemented
