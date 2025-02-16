# rclone wrappers
A bunch of simle utilities for using rclone.
ATM, we are interested in simple operations such as mounting, copy, check (content comparison), navigation, etc.
To be extended upon need.

## Usage examples

```bash
$ source rclone_wrapper.sh
$ nav_gdrive # to navigate the remote in command line
$ gmount # execute to see help
$ gumount # execute to see help
$ is_the_same # execute to see help
$ copy_to_gdrive # execute to see help
$ copy_from_gdrive # execute to see help
```

## TODO
* [ ] move implementation to Python with `subprocess` for more flexibility.

## License
```
Copyright (C) Saeed Gholami Shahbandi
```

Distributed with a GNU GENERAL PUBLIC LICENSE; see [LICENSE](https://github.com/saeedghsh/rclone_wapper/blob/master/LICENSE).  

**NOTE:** Portions of this code/project were developed with the assistance of ChatGPT (a product of OpenAI) and Copilot (A product of Microsoft).