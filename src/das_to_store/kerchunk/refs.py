from typing import Any, Callable, Optional, Protocol

import ujson


def merge_group_attrs(refs, src_group, dst_group, overwrite=False, remove_from_src=False):
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

def remove_attr(refs, group="", attr_name="member_id"):
    r = refs["refs"] if "refs" in refs else refs

    key = f"{group.strip('/')}/.zattrs" if group else ".zattrs"

    if key in r:
        attrs = ujson.loads(r[key])
        attrs.pop(attr_name, None)
        r[key] = ujson.dumps(attrs)

    return refs
