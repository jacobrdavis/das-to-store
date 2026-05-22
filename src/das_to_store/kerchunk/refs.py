""" Utilities for managing and modifying Kerchunk reference files. """
from typing import Optional, Union

import ujson
from pathlib import Path


def get_dimension_sizes(
    ref_path: Union[str, Path],
    group: str = ""
) -> dict[str, dict[str, int]]:
    ref_path = Path(ref_path)

    with open(ref_path) as f:
        refs = ujson.load(f)

    r = refs["refs"] if "refs" in refs else refs
    prefix = f"{group.strip('/')}/" if group else ""

    out = {}

    for key, value in r.items():
        if not (key.startswith(prefix) and key.endswith("/.zarray")):
            continue

        var = key[len(prefix):-len("/.zarray")]

        zarray = ujson.loads(value) if isinstance(value, str) else value

        zattrs_key = key[:-len("/.zarray")] + "/.zattrs"
        zattrs_raw = r.get(zattrs_key, "{}")
        zattrs = ujson.loads(zattrs_raw) if isinstance(zattrs_raw, str) else zattrs_raw

        dims = zattrs.get("_ARRAY_DIMENSIONS", [])
        shape = zarray["shape"]

        out[var] = dict(zip(dims, shape))

    return out


def get_file_dimension_sizes(
    ref_path: Union[str, Path],
    group: str = ""
) -> dict[str, int]:

    per_var = get_dimension_sizes(ref_path, group=group)

    sizes = {}
    for var, dims in per_var.items():
        for dim, size in dims.items():
            if dim in sizes and sizes[dim] != size:
                raise ValueError(
                    f"Inconsistent size for dim {dim!r}: "
                    f"{sizes[dim]} vs {size} in variable {var!r}"
                )
            sizes[dim] = size

    return sizes


def remove_attr(
    refs: dict,
    attr_name: str,
    group: str = "",
) -> dict:
    r = refs["refs"] if "refs" in refs else refs

    key = f"{group.strip('/')}/.zattrs" if group else ".zattrs"

    if key in r:
        attrs = ujson.loads(r[key])
        attrs.pop(attr_name, None)
        r[key] = ujson.dumps(attrs)

    return refs


def merge_group_attrs(
    refs: dict,
    src_group: str,
    dst_group: str,
    overwrite: bool = False,
    remove_from_src: bool = False
) -> dict:
    # Kerchunk refs may either be the refs dict itself, or {"refs": {...}, ...}
    r = refs["refs"] if "refs" in refs else refs

    src_key = f"{src_group.strip('/')}/.zattrs" if src_group else ".zattrs"
    dst_key = f"{dst_group.strip('/')}/.zattrs" if dst_group else ".zattrs"

    # Load attrs, defaulting to {}
    src_attrs = ujson.loads(r.get(src_key, "{}"))
    dst_attrs = ujson.loads(r.get(dst_key, "{}"))

    for k, v in src_attrs.items():
        if overwrite or k not in dst_attrs:
            dst_attrs[k] = v

    if remove_from_src:
        for k in list(src_attrs):
            if overwrite or k not in ujson.loads(r.get(dst_key, "{}")):
                src_attrs.pop(k, None)

    r[dst_key] = ujson.dumps(dst_attrs)
    if remove_from_src:
        r[src_key] = ujson.dumps(src_attrs)

    return refs
