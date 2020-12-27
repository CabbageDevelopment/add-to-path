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
import platform
import re
import subprocess
import sys
import traceback
from argparse import ArgumentParser
from os.path import abspath, expandvars, expanduser

if platform.system() != "Windows":
    print(f"Sorry, we only support Windows at the moment.")
    sys.exit(1)

argparser = ArgumentParser()

argparser.add_argument("path", help="The path to add to the PATH")
argparser.add_argument(
    "-d",
    "--dry-run",
    action="store_true",
    help="Print the command which would be run, but don't execute it",
)
argparser.add_argument(
    "-s",
    "--system",
    action="store_true",
    help="Whether to add to the system PATH; will require elevated permissions in your shell",
)

args = argparser.parse_args()


def get_abs(path: str) -> str:
    return abspath(expandvars(expanduser(path)))


def run_command(command: str):
    return subprocess.check_output(command).decode("utf-8").replace("\r", "\n")


def get_command(target: str, user: bool) -> str:
    env_var_target = (
        f"[System.EnvironmentVariableTarget]::{'User' if user else 'Machine'}"
    )

    path_cmd = f'powershell.exe /c "[System.Environment]::GetEnvironmentVariable("""PATH""", {env_var_target})"'
    path_cmd_stdout = run_command(path_cmd)

    path = re.findall(r"^\s*(.*)\s*$", path_cmd_stdout)[0]

    for item in path.split(";"):
        if item == target:
            print(f"Error: '{target}' is already on the PATH.")
            exit(1)

    if not re.match(r".*;\s*$", path):
        path = f"{path};"

    path = f"{path}{target}"
    set_cmd = f'powershell.exe /c "[System.Environment]::SetEnvironmentVariable("""PATH""", """{path}""", {env_var_target})"'

    return set_cmd


target = get_abs(args.path)
print(f"Adding '{target}' to the {'system' if args.system else 'user'} PATH...")

command = get_command(target, not args.system)
if args.dry_run:
    print(f"\nThis is the command we'll run:\n\n")
    print(command)
else:
    try:
        run_command(command)
        print(
            f"\nAdded to the PATH. Don't forget, you'll need to open a new terminal to see the changes."
        )
    except subprocess.CalledProcessError as e:
        traceback.print_exc()

        hashes = 20 * "#"
        print(f"\n{hashes} ERROR {hashes}\n\nThere was an error running the command. ", end="\n")
        if args.system:
            print(
                f"Are you in an elevated shell? You need admin permissions to add to the system PATH."
            )
