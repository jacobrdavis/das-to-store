from typing import Optional, Union

import pandas as pd
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
    for ref in ref_files:
        sizes = get_file_dimension_sizes(ref, group=group)

        if sizes != baseline_sizes:
            inconsistent_refs.append(ref)
            inconsistent_sizes.append(sizes)

    return baseline_ref, baseline_sizes, inconsistent_refs, inconsistent_sizes


def inconsistent_dimension_sizes_to_csv(
    inconsistent_refs: list[Path],
    inconsistent_sizes: list[dict[str, int]],
    output_file: Union[str, Path] = 'inconsistent_refs.csv',
) -> None:
    rows = []
    for ref, sizes in zip(inconsistent_refs, inconsistent_sizes):
        row = {"file": str(ref.name)}
        row.update(sizes)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)
