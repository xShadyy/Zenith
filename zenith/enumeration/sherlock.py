import os

from zenith.core.repo import GitHubRepo


class SherlockRepo(GitHubRepo):
    def __init__(self):
        super().__init__(
            path="sherlock-project/sherlock",
            install={"pip": "pip install ."},
            description="Hunt down social media accounts by username across social networks",
        )

    def run(self):
        from zenith.console import console
        from zenith.core.menu import confirm

        results_dir = os.path.join(self.full_path, "results")
        os.makedirs(results_dir, exist_ok=True)

        os.chdir(self.full_path)

        console.print("\n===== Sherlock Username Search =====", style="info")
        user_usernames = input("\nEnter one or more usernames: ").strip()

        if not user_usernames:
            console.print("No usernames entered. Aborting.", style="warning")
            return 1

        save_results = confirm("\nDo you want to save search results to a file?")

        searched_usernames = user_usernames.split()
        date_suffix = os.popen("date +'%Y%m%d_%H%M%S'").read().strip()

        exit_code = 0
        for username in searched_usernames:
            if os.path.exists(
                os.path.join(self.full_path, "sherlock_project", "sherlock.py")
            ):
                base_cmd = f"python3 {os.path.join(self.full_path, 'sherlock_project', 'sherlock.py')} {username}"
            else:
                base_cmd = f"sherlock {username}"

            if save_results:

                username_dir = os.path.join(results_dir, f"{username}_{date_suffix}")
                os.makedirs(username_dir, exist_ok=True)
                cmd = f"{base_cmd} --folderoutput {username_dir} --print-found"
            else:
                cmd = f"{base_cmd} --print-found"

            result = os.system(cmd)
            if result != 0:
                exit_code = result

            result_files = []
            if save_results and os.path.exists(username_dir):
                result_files = [
                    f for f in os.listdir(username_dir) if f.endswith(".txt")
                ]

        if save_results and len(searched_usernames) > 0:
            console.print("\n═════ Search Summary ═════", style="info")

            console.print("Results saved to:", style="success")
            for username in searched_usernames:
                username_dir = os.path.join(results_dir, f"{username}_{date_suffix}")
                if os.path.exists(username_dir):

                    result_files = [
                        f for f in os.listdir(username_dir) if f.endswith(".txt")
                    ]
                    if result_files:
                        console.print(
                            f"  • {username}: {username_dir} ({len(result_files)} matches)",
                            style="info",
                        )
                    else:
                        console.print(
                            f"  • {username}: {username_dir} (no matches)",
                            style="warning",
                        )

        return exit_code


sherlock = SherlockRepo()
