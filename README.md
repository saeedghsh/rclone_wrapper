[![black](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/formatting.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/formatting.yml)
[![pylint](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pylint.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pylint.yml)
[![mypy](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/type-check.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/type-check.yml)
[![pytest](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest.yml)
[![pytest-cov](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest-cov.yml/badge.svg?branch=master)](https://github.com/saeedghsh/rclone_wrapper/actions/workflows/pytest-cov.yml)

# rclone wrappers
A bunch of simle utilities for using rclone.
ATM, we are interested in simple operations such as mounting, copy, check (content comparison), navigation, etc.
To be extended upon need.

## Usage examples

**Bash script version**:
```bash
$ source rclone_wrapper.sh
$ nav_gdrive # to navigate the remote in command line
$ gmount # execute to see help
$ gumount # execute to see help
$ is_the_same # execute to see help
$ copy_to_gdrive # execute to see help
$ copy_from_gdrive # execute to see help
```

**Python version**:
```bash
$ pip install -r requirements.txt
$ python -m main navigate
```

## Keeping Configuration File Changes Untracked by Git
Once set, these commands do not need to be repeated.

**Ignore Local Changes (Git Won't Track Updates)**
```bash
git update-index --assume-unchanged rclone_wrapper/config.yaml
git update-index --no-assume-unchanged rclone_wrapper/config.yaml # to revert
```

**Prevent File Reset on `git reset --hard`**
```bash
git update-index --skip-worktree rclone_wrapper/config.yaml
git update-index --no-skip-worktree rclone_wrapper/config.yaml # To undo
```

## TODO
* [ ] move implementation to Python with `subprocess` for more flexibility.

## License
```
Copyright (C) Saeed Gholami Shahbandi
```

Distributed with a GNU GENERAL PUBLIC LICENSE; see [LICENSE](https://github.com/saeedghsh/rclone_wapper/blob/master/LICENSE).  

**NOTE:** Portions of this code/project were developed with the assistance of ChatGPT (a product of OpenAI) and Copilot (A product of Microsoft).