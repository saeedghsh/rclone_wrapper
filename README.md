[![black](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/formatting.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/formatting.yml)
[![pylint](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pylint.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pylint.yml)
[![mypy](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/type-check.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/type-check.yml)
[![pytest](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest.yml)
[![pytest-cov](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest-cov.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest-cov.yml)

# rclone wrappers
A bunch of simple utilities for using rclone.  

ATM, we are interested in simple operations such as mounting, copy, check (content comparison), navigation, etc.
To be extended upon need.

🚨 **Disclaimer: Experimental & Potentially Buggy**  
This project is still a work in progress and may contain bugs or unexpected behavior.


## Usage examples

### Remote authentication setup
Follow [this instructions](docs/instructions_rclone_gcp_oauth_setup.md) to setup rclone OAuth with GCP for Google Drive.
The rclone config name for the remote should be placed in `rclone_wrapper/config.yaml`.

### Python version
Install dependencies
```bash
$ pip install -r requirements.txt
```

Run commands
```bash
$ python -m main navigate
$ python -m main mount --remote-path <path> --mount-point <mount-point>
$ python -m main compare --remote-path <path> --local-path <path>
$ python -m main upload --remote-path <path> --local-path <path>
$ python -m main download --remote-path <path> --local-path <path>
```

NOTE on upload/download:
download and upload operations behave like UNIX `cp -r` and not like `mv`.
Source (local or remote) can be a file or a directory, but destination has to be a directory onto which the src object is copied to.
There is a guardrail against overwriting a dir/file at destination.

## Development

<details>
<summary>Code quality checks</summary>

```bash
mypy .
pylint .
pytest .
isort .
black .
```
</details>

<details>
<summary>Keeping Configuration File Changes Untracked by Git</summary>

Once set, these commands do not need to be repeated.

Ignore Local Changes (Git Won't Track Updates):
```bash
git update-index --assume-unchanged rclone_wrapper/config.yaml
git update-index --no-assume-unchanged rclone_wrapper/config.yaml # to revert
```

Prevent File Reset on `git reset --hard`:
```bash
git update-index --skip-worktree rclone_wrapper/config.yaml
git update-index --no-skip-worktree rclone_wrapper/config.yaml # To undo
```
</details>


## License
```
Copyright (C) Saeed Gholami Shahbandi
```

Distributed with a GNU GENERAL PUBLIC LICENSE; see [LICENSE](https://github.com/saeedghsh/rclone_wapper/blob/master/LICENSE).  

**NOTE:** Portions of this code/project were developed with the assistance of ChatGPT (a product of OpenAI) and Copilot (A product of Microsoft).