import fsspec
from pathlib import Path

import xarray as xr
import zarr
from tqdm.notebook import tqdm

from das_to_store.kerchunk.generate import generate_json
from das_to_store.kerchunk.combine import combine_jsons
from das_to_store.kerchunk.checks import find_inconsistent_dimension_sizes, inconsistent_dimension_sizes_to_csv
from das_to_store.interrogators.sintela import SintelaOnyxMultiZarrToZarrConfig


# Path to data files.
MVCO_DAS_PATH = '/proj/das-onyx/mvco_2023-2024/'
SUBSET = 'decimator_mvco_20231218-20240209/'
DATA_DIR = Path(MVCO_DAS_PATH) / SUBSET

# Store reference files in the working directory.
REF_DIR = DATA_DIR.with_name(f'{DATA_DIR.stem}_refs')
COMBINED_REF_FILENAME = DATA_DIR.name + '_combined.json'
COMBINED_REF_PATH = REF_DIR / COMBINED_REF_FILENAME

GENERATE_REFS = False
COMBINE_REFS = True

fs_remote = fsspec.filesystem('file')  # file system to access the H5 files
fs_local = fsspec.filesystem('file')  # local file system to save final jsons to

if GENERATE_REFS:

    flist = fs_remote.glob(str(DATA_DIR / '*.h5'))

    print(f'Number of H5 files found: {len(flist)}')

    # Create the reference output directory if it doesn't exist.
    REF_DIR.mkdir(exist_ok=True)

    print(f'Generating individual JSON reference files in {REF_DIR} ...')

    # Inline threshold adjusts the size (in bytes) below which binary blocks
    # are included directly in the output. A higher threshold results in a
    # larger JSON but faster loading time.
    for f in tqdm(flist):
        generate_json(
            file_url=f,
            fs_remote=fs_remote,
            fs_local=fs_local,
            output_dir=REF_DIR,
            inline_threshold=300,
        )

    print(f'Done.')

if COMBINE_REFS:
    # Exclude the combined reference file from the list of JSON files to
    # combine (in case it already exists).
    json_list = fs_local.glob(str(REF_DIR / "*.json"))
    json_list = [f for f in json_list if COMBINED_REF_FILENAME not in f]

    print(f'Number of JSON files found: {len(json_list)}')

    # Remove any JSON files with inconsistent dimension sizes before
    # combining. The first file is used as the baseline for comparison.
    baseline_ref, baseline_sizes, inconsistent_refs, inconsistent_sizes \
        = find_inconsistent_dimension_sizes(
        ref_files=json_list,
        baseline_ref=json_list[0],
        group="Acquisition/Raw[0]",
    )
    inconsistent_dimension_sizes_to_csv(
        inconsistent_refs=inconsistent_refs,
        inconsistent_sizes=inconsistent_sizes,
        output_file= REF_DIR / (DATA_DIR.name + '_inconsistent_refs.csv'),
    )
    good_json_list = [f for f in json_list if f not in str(inconsistent_refs)]

    print(f'Number of consistent JSON files found: {len(good_json_list)}')


    print(f'Generating combined JSON reference file in {REF_DIR} ...')

    combine_jsons(
        json_list=good_json_list,
        fs_local=fs_local,
        mzz_config=SintelaOnyxMultiZarrToZarrConfig(),
        remote_protocol='file',
        output_path=str(COMBINED_REF_PATH),
    )

    print(f'Done.')
