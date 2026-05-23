import inspect

from tools.tool import Tool


# Python 类型注解 → JSON Schema type 的映射
_TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


def _derive_parameters(fn) -> dict:
    """从函数签名自动推导 tools 所需的 JSON Schema parameters。

    读取 fn.__annotations__ 中的参数类型，
    映射为 {"type": "object", "properties": {...}, "required": [...]}。
    没有默认值的参数自动标记为 required。
    """
    sig = inspect.signature(fn)

    properties: dict[str, dict] = {}
    required: list[str] = []

    for name, param in sig.parameters.items():
        # param.annotation 是类型注解，如 def foo(x: str) 中的 str
        python_type = param.annotation
        json_type = _TYPE_MAP.get(python_type, "string")
        properties[name] = {"type": json_type}

        # inspect.Parameter.empty 表示参数没有默认值 → 必填
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def tool(name: str, description: str):
    """装饰器：把普通函数包装成 Tool。

    name 和 description 必须由工具提供者手动填写，
    parameters 从类型注解自动推导。
    """
    def decorator(fn):
        params = _derive_parameters(fn)
        return Tool(name=name, description=description, parameters=params, fn=fn)
    return decorator