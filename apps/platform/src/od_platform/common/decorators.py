#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  : decorators.py
# @Project   : ODPlatform
# @Function  : 通用装饰器集合——计时 / 重试 / 日志记录 / 权限检查 / 参数校验

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union


# ============================================================
# 辅助函数
# ============================================================

def _truncate_repr(obj: Any, max_len: int) -> str:
    """截断过长对象的 repr，避免日志/异常信息泛滥。"""
    s = repr(obj)
    if len(s) > max_len:
        return s[:max_len - 3] + "..."
    return s


# ============================================================
# 1. 计时装饰器 — @timing / @timing()
# ============================================================

def timing(func=None, *, log_level: int = logging.INFO,
           msg: Optional[str] = None):
    """记录函数执行耗时，通过 logger 输出。

    Args:
        log_level: 日志级别，默认 INFO。
        msg:       自定义标签，默认使用函数名。

    Example:
        @timing
        def train(): ...

        @timing(log_level=logging.DEBUG, msg="推理阶段")
        def inference(): ...
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                label = msg if msg is not None else f.__name__
                logging.getLogger(f.__module__).log(
                    log_level, f"{label} 耗时 {elapsed:.4f}s"
                )
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


# ============================================================
# 2. 重试装饰器 — @retry / @retry()
# ============================================================

def retry(func=None, *, max_attempts: int = 3, delay: float = 1.0,
          backoff: float = 2.0,
          exceptions: Union[Type[BaseException],
                            Tuple[Type[BaseException], ...]] = Exception):
    """失败后自动重试，支持指数退避延迟。

    Args:
        max_attempts: 最大尝试次数（含首次调用）。
        delay:        首次重试前的等待秒数。
        backoff:      退避倍数，每次重试后 delay *= backoff。
        exceptions:   需要重试的异常类型，默认捕获所有 Exception。

    Example:
        @retry(max_attempts=5, delay=0.5, exceptions=ConnectionError)
        def fetch(url: str): ...
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exc: Optional[BaseException] = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts:
                        logging.getLogger(f.__module__).warning(
                            f"{f.__name__} 第 {attempt}/{max_attempts} 次失败，"
                            f"{current_delay:.1f}s 后重试：{e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
            logging.getLogger(f.__module__).error(
                f"{f.__name__} 重试 {max_attempts} 次全部失败"
            )
            raise last_exc  # type: ignore[misc]
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


# ============================================================
# 3. 日志记录装饰器 — @log_call / @log_call()
# ============================================================

def log_call(func=None, *, log_level: int = logging.DEBUG,
             log_args: bool = True, log_result: bool = True,
             max_arg_len: int = 200):
    """记录函数调用：入口参数与出口返回值。

    Args:
        log_level:   日志级别，默认 DEBUG。
        log_args:    是否记录入口参数。
        log_result:  是否记录返回值。
        max_arg_len: 参数/返回值 repr 最大长度，超出部分截断。

    Example:
        @log_call
        def process(data: dict): ...

        @log_call(log_result=False)  # 返回值太长，只记参数
        def generate(): ...
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if log_args:
                args_repr = _truncate_repr(args, max_arg_len)
                kwargs_repr = _truncate_repr(kwargs, max_arg_len)
                logging.getLogger(f.__module__).log(
                    log_level,
                    f"→ {f.__name__}(*{args_repr}, **{kwargs_repr})"
                )
            result = f(*args, **kwargs)
            if log_result:
                result_repr = _truncate_repr(result, max_arg_len)
                logging.getLogger(f.__module__).log(
                    log_level, f"← {f.__name__} → {result_repr}"
                )
            return result
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


# ============================================================
# 4. 权限检查装饰器 — @require_permission
# ============================================================

# 简易全局权限注册表
_permission_registry: Dict[str, bool] = {}


def register_permission(name: str, granted: bool = True) -> None:
    """向权限注册表中注册（或撤销）一项权限。

    Example:
        register_permission("admin")       # 授权
        register_permission("debug", False)  # 撤销
    """
    _permission_registry[name] = granted


def check_permission(name: str) -> bool:
    """查询某项权限是否已授权。"""
    return _permission_registry.get(name, False)


def require_permission(permission: Union[str, Callable[[], bool]]):
    """检查权限，未通过则抛出 PermissionError。

    Args:
        permission: 权限名（str，查询注册表）或自定义检查函数（Callable[[], bool]）。

    Example:
        register_permission("delete")

        @require_permission("delete")
        def delete_file(path): ...

        @require_permission(lambda: os.getenv("ENV") == "dev")
        def dev_only(): ...
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if isinstance(permission, str):
                if not check_permission(permission):
                    raise PermissionError(f"缺少权限：{permission}")
            else:
                if not permission():
                    raise PermissionError("权限检查未通过（自定义检查）")
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# 5. 参数校验装饰器 — @validate_params
# ============================================================

def validate_params(validator: Callable[..., bool],
                    error_msg: str = "参数校验失败"):
    """在调用函数前执行参数校验。

    Args:
        validator: 校验函数，接收与被装饰函数相同的 (*args, **kwargs)，返回 bool。
        error_msg: 校验失败时 ValueError 携带的信息。

    Example:
        @validate_params(lambda x: x > 0, error_msg="x 必须大于 0")
        def sqrt(x): ...

        def check_shape(*args, **kwargs):
            return len(args) >= 1 and isinstance(args[0], (list, tuple))

        @validate_params(check_shape, error_msg="第一个参数必须为 list/tuple")
        def batch_process(data): ...
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not validator(*args, **kwargs):
                raise ValueError(
                    f"{f.__name__}: {error_msg} "
                    f"(args={_truncate_repr(args, 100)}, "
                    f"kwargs={_truncate_repr(kwargs, 100)})"
                )
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=== decorators 自测 ===\n")

    # ---- 1. timing ----
    print("【1. 计时装饰器】")

    @timing
    def slow_add(a, b):
        time.sleep(0.05)
        return a + b

    print(f"  slow_add(1, 2) = {slow_add(1, 2)}\n")

    # ---- 2. retry ----
    print("【2. 重试装饰器】")

    _attempts = 0

    @retry(max_attempts=3, delay=0.05)
    def flaky_func():
        global _attempts
        _attempts += 1
        if _attempts < 3:
            raise ValueError("临时错误")
        return "成功"

    print(f"  flaky_func() = {flaky_func()}\n")

    # ---- 3. log_call ----
    print("【3. 日志记录装饰器】")

    @log_call
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    print(f"  greet('ODPlatform') = {greet('ODPlatform')}\n")

    # ---- 4. require_permission ----
    print("【4. 权限检查装饰器】")

    register_permission("admin")

    @require_permission("admin")
    def admin_action():
        return "admin OK"

    print(f"  admin_action() = {admin_action()}")

    @require_permission("superuser")
    def super_action():
        return "super OK"

    try:
        super_action()
    except PermissionError as e:
        print(f"  super_action() → PermissionError: {e}\n")

    # ---- 5. validate_params ----
    print("【5. 参数校验装饰器】")

    @validate_params(lambda x: x > 0, error_msg="x 必须大于 0")
    def divide_by(x, y=2):
        return y / x

    print(f"  divide_by(5) = {divide_by(5)}")
    try:
        divide_by(-1)
    except ValueError as e:
        print(f"  divide_by(-1) → ValueError: {e}")

    print("\n=== 自测完成 ===")
