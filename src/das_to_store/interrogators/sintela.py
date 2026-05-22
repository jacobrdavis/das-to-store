from dataclasses import dataclass, field
from typing import Optional, Callable

from das_to_store.kerchunk.refs import merge_group_attrs, remove_attr


def preprocess(refs):
    refs1 = merge_group_attrs(
        refs,
        src_group="Acquisition",
        dst_group="",
        overwrite=False,
        remove_from_src=True
    )
    return merge_group_attrs(
        refs1,
        src_group="Acquisition/Raw[0]",
        dst_group="",
        overwrite=True,
        remove_from_src=True
    )

def postprocess(refs):
    refs1 = remove_attr(refs, group="", attr_name="MeasurementStartTime")
    return remove_attr(refs1, group="", attr_name="uuid")

@dataclass
class SintelaOnyxMultiZarrToZarrConfig:
    coo_map: dict[str, str] = field(
        default_factory=lambda: {
            'time': 'attr:MeasurementStartTime',
        }
    )
    concat_dims: list[str] = field(
        default_factory=lambda: ['time']
    )
    identical_dims: list[str] = field(
        default_factory=lambda: ['phony_dim_0', 'phony_dim_1']
    )
    preprocess: Optional[Callable] = preprocess
    postprocess: Optional[Callable] = postprocess

