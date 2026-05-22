from typing import Any, Callable, Optional, Protocol

import ujson
from kerchunk.combine import MultiZarrToZarr
from fsspec.spec import AbstractFileSystem


class MultiZarrToZarrConfig(Protocol):
    coo_map: Optional[dict[str, str]] = None
    concat_dims: Optional[list[str]] = None
    identical_dims: Optional[list[str]] = None
    preprocess: Optional[Callable] = None
    postprocess: Optional[Callable] = None

    # def kwargs(self) -> dict[str, Any]:
    #     return vars(self)


def combine_jsons(
    json_list: list[str],
    fs_local: AbstractFileSystem,
    mzz_config: Optional[MultiZarrToZarrConfig] = None,
    remote_protocol: str = 'file',
    output_path: str ='.',
    **kwargs,
) -> None:

    mzz_config_kwargs = vars(mzz_config) if mzz_config is not None else {}

    mzz = MultiZarrToZarr(
        json_list,
        remote_protocol=remote_protocol,
        **mzz_config_kwargs,
        **kwargs,
    )

    json_dict = mzz.translate()

    with fs_local.open(output_path, "w") as f:
        ujson.dump(json_dict, f)

    # Optionally, clean up memory after writing the combined JSON file.
    # (Helpful if running multiple combines.)
    # del json_dict
    # del mzz
    # gc.collect()
