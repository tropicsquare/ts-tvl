## How to release new version on GitHub
When introducing new changes to TVL, they have to be specified in the [`CHANGELOG.md`](../CHANGELOG.md), which follows the [Keep a changelog](https://keepachangelog.com/en/1.1.0/) format. Only two-digit version are allowed at the moment (can be changed if needed). After the new version is ready to be released, follow these steps:
1. in the file [`CHANGELOG.md`](../CHANGELOG.md), give the 'Unreleased' version a two-digit version number,
2. in the file [`pyproject.toml`](../pyproject.toml), change the `version` field to the new one,
3. if the model targets a newer ts-tr01-app or SPECT firmware release, update `RISCV_FW_VERSION_STR` and/or `SPECT_FW_VERSION_STR` in [`tvl/constants.py`](../tvl/constants.py),
4. push all changes that should be included in the new release to the master branch, including the `CHANGELOG.md`, `pyproject.toml`, and `constants.py` files,
5. create an annotated tag with `git tag -a <version_number> <commit_hash> -m "tag message"` and push it with `git push origin <version_number>`.

After these steps, the action **Release new version on tag creation** should create the new release.
