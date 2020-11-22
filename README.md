# addtopath

`addtopath` is a tool which allows you to easily add a directory to your PATH using the terminal on Windows.

`addtopath` is a Python program which runs like a standalone executable when installed with `pip`.

## How to install 

`addtopath` can be installed with `pip`:

```bash
pip install addtopath
```

## How to use 

After installation with `pip`, the `addtopath` executable should be available on the PATH. It's very easy to use: just run it with the desired directory to add to the PATH.

To add the current working directory to the PATH:

```bash
addtopath .
```

It works with relative paths:

```bash
addtopath ..
```

It also works with the `~` symbol in Powershell, for example:

```bash
addtopath ~/scripts
```

You can, of course, supply the absolute path to your target directory:

```bash
addtopath "C:\Program Files\SomeProgram"
```

## User and system PATHs

`addtopath` adds to the *user* path by default. This doesn't require admin permissions, and is usually sufficient. However, you can instead add to the *system* path using the `-s` or `--system` flag.

For example:

```bash
addtopath . -s
```

> **Note:** This requires an administrator Powershell or Command Prompt.