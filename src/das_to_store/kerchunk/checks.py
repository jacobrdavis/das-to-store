from typing import Optional, Union

from pathlib import Path

from das_to_store.kerchunk.refs import get_file_dimension_sizes


def find_inconsistent_dimension_sizes(
    ref_files: list[Union[str, Path]],
    baseline_ref: Optional[Union[str, Path]] = None,
    group: str = ""
) -> tuple[Union[str, Path], dict[str, int], list[Path], list[dict[str, int]]]:
    ref_files = list(map(Path, ref_files))

    if baseline_ref is None:
        baseline_ref = ref_files[0]

    baseline_sizes = get_file_dimension_sizes(baseline_ref, group=group)


    inconsistent_refs = []
    inconsistent_sizes = []
    for ref in ref_files[1:]:
        sizes = get_file_dimension_sizes(ref, group=group)

        if sizes != baseline_sizes:
            inconsistent_refs.append(ref)
            inconsistent_sizes.append(sizes)

    return baseline_ref, baseline_sizes, inconsistent_refs, inconsistent_sizes

