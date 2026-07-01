#引用解析，把命令行用户给的dataset / yaml / model/等等名字或路径统一做好解析，解析成统一的path

from __future__ import annotations

from pathlib import Path
from typing import Optional
from od_platform.common.paths import RAW_DATA_DIR

def resolve_ref(ref: str, *, base_dir:Path, default_suffix:Optional[str] = None) -> Path:
    p = Path(ref)
    if p.is_absolute() or len(p.parts) > 1:
        return p.resolve()
    name = ref if (not default_suffix or ref.endswith(default_suffix)) else ref + default_suffix
    return (base_dir / name).resolve()

def resolve_dataset(ref: str) -> Path:
    return resolve_ref(ref, base_dir=RAW_DATA_DIR)