import os
import subprocess
from typing import List

from zenith.console import console
from zenith.core.menu import set_readline
from zenith.core.repo import GitHubRepo
from zenith.core.usernames import add_username, get_usernames


class SherlockRepo(GitHubRepo):
    def __init__(self):
        super().__init__(
            path="sherlock-project/sherlock",
            install={"pip": "requirements.txt"},
            description="Hunt down social media accounts by username across social networks",
        )

    def _validate_usernames(self, usernames: str) -> List[str]:
        """Validate and clean usernames."""
        if not usernames.strip():
            raise ValueError("No usernames provided")
        
        cleaned_usernames = []
        for username in usernames.split():
            # Basic username validation
            username = username.strip()
            if not username:
                continue
            # Remove common social media prefixes
            username = username.lstrip('@')
            cleaned_usernames.append(username)
        
        if not cleaned_usernames:
            raise ValueError("No valid usernames found")
        
        return cleaned_usernames

    def _build_command(self, usernames: List[str]) -> List[str]:
        """Build the sherlock command with proper arguments."""
        command = ["python3", "-m", "sherlock_project"]
        command.extend(usernames)
        
        # Add useful default options
        command.extend([
            "--timeout", "10",  # Reasonable timeout
            "--print-found",    # Only print found accounts
        ])
        
        return command

    def run(self):
        """Run Sherlock with improved error handling and user experience."""
        try:
            os.chdir(self.full_path)
            
            # Get existing usernames for autocomplete
            usernames = get_usernames()
            set_readline(usernames)
            
            # Get user input with better prompting
            console.print("\n" + "="*50, style="info")
            console.print("Sherlock - Social Media Username Search", style="tool_name")
            console.print("="*50, style="info")
            console.print("Enter usernames separated by spaces", style="tool_description")
            console.print("Example: john_doe alice_smith", style="tool_description")
            
            user_input = input("\nUsernames: ").strip()
            
            # Validate usernames
            try:
                validated_usernames = self._validate_usernames(user_input)
            except ValueError as e:
                console.print(f"Error: {e}", style="error")
                return 1
            
            # Save new usernames
            for username in validated_usernames:
                if username not in usernames:
                    add_username(username)
            
            # Build and execute command
            command = self._build_command(validated_usernames)
            
            console.print(f"\nSearching for: {', '.join(validated_usernames)}", style="info")
            console.print("This may take a few minutes...\n", style="warning")
            
            # Run sherlock with better process handling
            try:
                result = subprocess.run(
                    command,
                    cwd=self.full_path,
                    check=False,  # Don't raise on non-zero exit
                    text=True,
                    timeout=300,  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    console.print("\nSearch completed successfully!", style="success")
                elif result.returncode == 1:
                    console.print("\nSearch completed with some errors", style="warning")
                else:
                    console.print(f"\nSearch failed with exit code {result.returncode}", style="error")
                
                return result.returncode
                
            except subprocess.TimeoutExpired:
                console.print("\nSearch timed out after 5 minutes", style="error")
                return 124
            except FileNotFoundError:
                console.print("Python3 or sherlock module not found", style="error")
                console.print("Make sure Sherlock is properly installed", style="warning")
                return 127
            except Exception as e:
                console.print(f"Unexpected error: {e}", style="error")
                return 1
                
        except KeyboardInterrupt:
            console.print("\nSearch cancelled by user", style="warning")
            return 130
        except Exception as e:
            console.print(f"Failed to run Sherlock: {e}", style="error")
            return 1


sherlock = SherlockRepo()