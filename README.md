colorschemes
============

Usage
-----

First, clone a repo:

```sh
cd ~ # Or wherever you want to put this repo
git clone -b custom https://github.com/ranger/colorschemes.git --single-branch
```

Then, to install the colorschemes, run a make command:

```sh
python install.py scheme  # Replace `scheme` with the name of the desired scheme
```

This creates symlinks, so that if the colorschemes are updated, you just have to
pull down the new changes using `git pull origin master` and you're set.

If you want to install copies, run this make command:

```sh
make cp_scheme # Replace `scheme` with the name of the desired scheme
```

Creating a new colorscheme
--------------------------

Read about how to create your own colorschemes in
[colorschemes.md](https://github.com/ranger/ranger/blob/master/doc/colorschemes.md)
in the ranger repo.
