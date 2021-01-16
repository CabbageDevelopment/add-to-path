#  MIT License
#
#  Copyright (c) 2020 Sam McCormack
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import os
import platform
import re
import subprocess
import sys
import traceback
from os.path import abspath, expandvars, expanduser
from typing import List

from addtopath.argparsing import args

if platform.system() != "Windows":
    print(f"Sorry, we only support Windows at the moment.")
    sys.exit(1)


def get_abs(path: str) -> str:
    return abspath(expandvars(expanduser(path)))


def run_command(command: str):
    return subprocess.check_output(command).decode("utf-8").replace("\r", "").rstrip()


def get_command(target: str, user: bool, process=False) -> str:
    """
    Returns the Powershell command which will add the new item to the path.
    """
    path_cmd = powershell_command_get_path(user)
    path_cmd_stdout = run_command(path_cmd)

    path = re.findall(r"^\s*(.*)\s*$", path_cmd_stdout)[0]

    if not (args.force or args.remove) and any(
        item == target for item in path.split(";")
    ):
        print(f"Error: '{target}' is already on the PATH.")
        sys.exit(1)

    # Ensure PATH ends with semicolon.
    if not re.match(r".*;\s*$", path):
        path = f"{path};"

    if args.remove:
        path = remove_from_path(path, target)
    else:
        path = add_to_path(path, target, prepend=args.prepend)

    # Ensure path does not end in semicolon.
    path = re.findall(r"^(.*?);?\s*$", path)[0]

    set_cmd = (
        f'powershell.exe /c "[System.Environment]::'
        f'SetEnvironmentVariable("""PATH""", """{path}""", {_get_environment_var_target(user, process)})"'
    )

    return set_cmd


def _get_environment_var_target(user: bool, process=False) -> str:
    return (
        f"[System.EnvironmentVariableTarget]::"
        f"{'Process' if process else ('User' if user else 'Machine')}"
    )


def powershell_command_get_path(user: bool) -> str:
    env_var_target = _get_environment_var_target(user)
    return f'powershell.exe /c "[System.Environment]::GetEnvironmentVariable("""PATH""", {env_var_target})"'


def get_current_path(user: bool) -> List[str]:
    cmd = powershell_command_get_path(user)
    path = run_command(cmd)

    return path.split(";")


def add_to_path(path: str, target: str, prepend: bool) -> str:
    if prepend:
        path = f"{target};{path}"
    else:
        path = f"{path}{target}"
    return path


def remove_from_path(path: str, to_remove: str) -> str:
    matches = []
    current_items = path.split(";")

    for item in current_items:
        try:
            if os.path.samefile(to_remove, item):
                matches.append(item)
        except:
            if os.path.normpath(item) == os.path.normpath(to_remove):
                matches.append(item)

    if not matches:
        print(f"Error: '{to_remove}' not found on the PATH.")
        sys.exit(1)

    new_items = []
    for item in current_items:
        if item not in matches:
            new_items.append(item)

    [
        print(f"Removing '{i}' from the {'system' if args.system else 'user'} PATH")
        for i in matches
    ]
    return ";".join(new_items)


for p in args.path:
    target = get_abs(p)
    if os.path.isfile(target):
        target = os.path.dirname(target)
        print(f"'{target}' is a file; using its parent folder instead.")

    if not args.force and not os.path.exists(target) and not args.remove:
        print(
            f"Error: location '{target}' does not exist. "
            f"Re-run with the '--force' parameter if you still wish to add to the PATH."
        )
        sys.exit(1)

    if not args.remove:
        print(f"Adding '{target}' to the {'system' if args.system else 'user'} PATH...")

    command = get_command(target, user=not args.system)
    if args.dry_run:
        print(f"\nThis is the command we'll run:\n")
        print(command)
    else:
        try:
            run_command(command)
            print(
                f"\nPATH updated. Don't forget to open a new terminal, or run "
                f"'addtopath -g' to update the current session."
            )
        except subprocess.CalledProcessError as e:
            traceback.print_exc()

            hashes = 20 * "#"
            print(
                f"\n{hashes} ERROR {hashes}\n\n"
                f"There was an error running the command. ",
                end="\n",
            )
            if args.system:
                print(
                    f"Are you in an elevated shell? "
                    f"You need admin permissions to add to the system PATH."
                )
if args.show:
    items = get_current_path(user=not args.system)
    print(
        f"\nCurrent items on the {'user' if not args.system else 'system'} PATH:",
        end="\n\n",
    )

    for i in items:
        print(f"'{i}'")

if args.generate_script:
    print(f"Creating Powershell script to update the PATH in the current session...")

    cmd = (
        f'$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + '
        f'[System.Environment]::GetEnvironmentVariable("Path","User")\n'
        f'Write-Output "Updated PATH in current session."\n'
        f'Write-Output "Script deleting self."\n'
        f"rm $PSCommandPath"
    )

    filename = "Update-Path.ps1"

    for i in range(2):
        try:
            with open(filename, "w") as f:
                f.write(cmd)
                break
        except PermissionError:
            print(
                f"Don't have write permissions in '{os.getcwd()}', falling back to home directory."
            )
            filename = os.path.join(os.path.expanduser("~"), filename)

    print(
        f"\nSelf-deleting Powershell script generated. "
        f"Execute the script with the command:\n\n.\\{os.path.relpath(filename)}",
        end="\n\n",
    )

elif not args.path:
    print(f"Nothing to do.")
