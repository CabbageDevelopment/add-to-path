# addtopath

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/addtopath?color=brightgreen)](https://pypi.org/project/addtopath)

## Introduction

`addtopath` is a CLI program which allows you to easily add a directory to your PATH using the terminal on Windows. 

## Requirements

You need to have Python 3.6 or higher installed. This will allow you to install `addtopath` with Python's package manager, `pip`. 

## How to install 

To install `addtopath` with `pip`:

```bash
pip install addtopath
```

## How to use 

After installation with `pip`, the `addtopath` executable should be available on the PATH. It's very easy to use: just run it with a directory as an argument, to add that directory to the PATH.

To add the current working directory to the PATH, run:

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