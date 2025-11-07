import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence

TARGET_REPO = "nvaccess/addon-datastore"
ISSUE_TEMPLATE_NAME = "Add-on registration"
DEFAULT_CHANNEL = "stable"
LICENSE_NAME = "GPL v2"
LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"


gh_path = shutil.which("gh")
if not gh_path:
    print("The executible of the GitHub cli (gh) was not found.")
    sys.exit(1)


def exec_gh(
    args: Sequence,
    env: dict | None = None,
    stdin_data: str | None = None,
) -> subprocess.CompletedProcess:
    args = list(args)
    base_env = os.environ.copy()
    base_env.update(
        {
            "GH_NO_UPDATE_NOTIFIER": "1",
            "GH_NO_EXTENSION_UPDATE_NOTIFIER": "1",
            "GH_SPINNER_DISABLED": "1",
            "GH_PROMPT_DISABLED": "1",
        },
    )

    env = (base_env | env) if env else base_env
    print(f"> gh {' '.join(args)}")
    args.insert(0, gh_path)
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        input=stdin_data,
        encoding="utf-8",
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=False,
    )
    if proc.returncode != 0:
        print(f"gh exitted with return code {proc.returncode}")
    if proc.stdout:
        print(f"STDOUT: {proc.stdout}")
    if proc.stderr:
        print(f"STDERR: {proc.stderr}")
    return proc


def get_latest_release_title() -> str:
    proc = exec_gh(
        [
            "release",
            "list",
            "--exclude-drafts",
            "--exclude-pre-releases",
            "--limit",
            "1",
            "--json",
            "name",
        ],
    )
    proc.check_returncode()
    output = proc.stdout.strip()
    releases = json.loads(output)
    if not releases:
        msg = "No releases found in this repository."
        raise RuntimeError(msg)
    return releases[0]["name"]


def get_repo_field_jq(jq_expr: str) -> str:
    proc = exec_gh(["repo", "view", "--json", "name,owner,url", "--jq", jq_expr])
    proc.check_returncode()
    return proc.stdout.strip()


def get_current_repo_name() -> str:
    return get_repo_field_jq(".name")


def get_current_repo_url() -> str:
    return get_repo_field_jq(".url")


def get_current_repo_owner() -> str:
    return get_repo_field_jq(".owner.login // .owner.name")


def get_latest_addon_asset_url() -> str | None:
    proc = exec_gh(
        [
            "release",
            "view",
            "--json",
            "assets",
            "--jq",
            '.assets[] | select(.name | endswith(".nvda-addon")) | .url',
        ],
    )
    if proc.returncode != 0:
        return None
    out = proc.stdout.strip()
    if not out:
        return None
    return out.splitlines()[0]


def build_issue_title(repo_name: str, latest_release_title: str) -> str:
    display_repo = repo_name
    if display_repo.lower().startswith("nvda"):
        display_repo = display_repo[4:].lstrip("-_ .")
    return f"[Submit add-on]: {display_repo} {latest_release_title}"


def build_issue_body(  # noqa: PLR0913
    *,
    download_url: str,
    source_url: str,
    publisher: str,
    channel: str,
    license_name: str,
    license_url: str,
) -> str:
    return (
        f"### Download URL\n\n{download_url}\n\n"
        f"### Source URL\n\n{source_url}\n\n"
        f"### Publisher\n\n{publisher}\n\n"
        f"### Channel\n\n{channel}\n\n"
        f"### License Name\n\n{license_name}\n\n"
        f"### License URL\n\n{license_url}\n"
    )


def confirm(prompt: str) -> bool:
    try:
        resp = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return resp in {"y", "yes"}


def main(argv: list[str]) -> int:  # noqa: PLR0911
    parser = argparse.ArgumentParser(
        description=(
            f"Prepare and submit an NVDA add-on registration issue to the store ({TARGET_REPO})."
        ),
    )
    parser.add_argument(
        "--channel",
        choices=["stable", "beta", "dev"],
        default=DEFAULT_CHANNEL,
        help="Release channel to declare (default: stable)",
    )
    parser.add_argument(
        "--target-repo",
        default=TARGET_REPO,
        help="Target repository for issue creation",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation and submit immediately",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not create the issue; just print the content",
    )

    args = parser.parse_args(argv)

    # Gather defaults via gh CLI
    try:
        repo_name = get_current_repo_name()
        source_url = get_current_repo_url()
        publisher = get_current_repo_owner()
    except subprocess.CalledProcessError as e:
        print("Failed to query repository details via gh.")
        return e.returncode or 1

    try:
        latest_release_title = get_latest_release_title()
    except (
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        RuntimeError,
    ) as e:  # keep simple surface
        print(f"Error determining latest release title: {e}")
        return 1

    download_url = get_latest_addon_asset_url()
    if not download_url:
        print("Could not auto-detect a .nvda-addon asset in the latest release.")
        try:
            manual = input("Enter the download URL manually (or leave empty to abort): ").strip()
        except EOFError:
            manual = ""
        if not manual:
            return 1
        download_url = manual

    title = build_issue_title(repo_name, latest_release_title)
    body = build_issue_body(
        download_url=download_url,
        source_url=source_url,
        publisher=publisher,
        channel=args.channel,
        license_name=LICENSE_NAME,
        license_url=LICENSE_URL,
    )

    print("\nPrepared issue title and body:\n")
    print(title)
    print("\n" + "-" * 60 + "\n")
    print(body)
    print("-" * 60 + "\n")

    if args.dry_run:
        return 0

    if not args.yes and not confirm("Create the issue now?"):
        print("Aborted by user.")
        return 0

    # Create the issue via gh
    proc = exec_gh(
        [
            "issue",
            "create",
            "-R",
            args.target_repo,
            "-T",
            ISSUE_TEMPLATE_NAME,
            "-t",
            title,
            "-b",
            body,
        ],
    )
    if proc.returncode != 0:
        print("Failed to create the issue via gh.")
        return proc.returncode

    print("Issue created successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
