from __future__ import annotations

def should_exit(*, in_range: bool, out_of_range_seconds: int,
                max_out_seconds: int, rug_flags: tuple[str,...]) -> tuple[bool,str]:
    if rug_flags: return True,"RUG_FLAG:"+",".join(rug_flags)
    if not in_range and out_of_range_seconds>=max_out_seconds: return True,"OUT_OF_RANGE"
    return False,""
