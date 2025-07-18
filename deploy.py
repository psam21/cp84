#!/usr/bin/env python3
"""
Bitcoin Crypto Dashboard - Deployment Automation Script
Automates git operations: status, diff, staging, commit with descriptive messages
Enhanced with comprehensive logging and error handling
"""

import subprocess
import sys
import os
import logging
import traceback
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
import json
from pathlib import Path


class DeploymentLogger:
    """Enhanced logging system for deployment operations"""
    
    def __init__(self, log_level: str = "INFO"):
        self.setup_logging(log_level)
        self.operation_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.start_time = datetime.now()
        
    def setup_logging(self, log_level: str):
        """Setup comprehensive logging configuration"""
        try:
            # Create logs directory if it doesn't exist
            log_dir = Path("deployment_logs")
            log_dir.mkdir(exist_ok=True)
            
            # Create timestamp for log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"deployment_{timestamp}.log"
            
            # Configure logging
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            self.logger = logging.getLogger(__name__)
            self.log_file_path = log_file
            
            self.info(f"🚀 Deployment session started - Log file: {log_file}")
            self.info(f"📍 Working directory: {os.getcwd()}")
            self.info(f"🐍 Python version: {sys.version}")
            
        except Exception as e:
            print(f"❌ Failed to setup logging: {e}")
            # Fallback to basic logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
            self.log_file_path = None
    
    def debug(self, message: str, context: Dict = None):
        """Log debug message with optional context"""
        self._log(logging.DEBUG, message, context)
    
    def info(self, message: str, context: Dict = None):
        """Log info message with optional context"""
        self._log(logging.INFO, message, context)
    
    def warning(self, message: str, context: Dict = None):
        """Log warning message with optional context"""
        self.warning_count += 1
        self._log(logging.WARNING, message, context)
    
    def error(self, message: str, context: Dict = None, exception: Exception = None):
        """Log error message with optional context and exception details"""
        self.error_count += 1
        
        if exception:
            message += f" | Exception: {str(exception)}"
            if context is None:
                context = {}
            context['exception_type'] = type(exception).__name__
            context['traceback'] = traceback.format_exc()
        
        self._log(logging.ERROR, message, context)
    
    def success(self, message: str, context: Dict = None):
        """Log success message with optional context"""
        self._log(logging.INFO, f"✅ {message}", context)
    
    def operation_start(self, operation: str, details: Dict = None):
        """Log the start of a major operation"""
        self.operation_count += 1
        message = f"🔄 Starting operation #{self.operation_count}: {operation}"
        self.info(message, details)
    
    def operation_end(self, operation: str, success: bool, details: Dict = None):
        """Log the end of a major operation"""
        status = "✅ COMPLETED" if success else "❌ FAILED"
        message = f"{status} operation: {operation}"
        if success:
            self.success(message, details)
        else:
            self.error(message, details)
    
    def _log(self, level: int, message: str, context: Dict = None):
        """Internal logging method with context support"""
        try:
            if context:
                context_str = json.dumps(context, indent=2, default=str)
                full_message = f"{message}\n📊 Context: {context_str}"
            else:
                full_message = message
            
            self.logger.log(level, full_message)
            
        except Exception as e:
            # Fallback if logging fails
            print(f"Logging error: {e} | Original message: {message}")
    
    def get_session_summary(self) -> Dict:
        """Get comprehensive session summary"""
        duration = datetime.now() - self.start_time
        return {
            'session_start': self.start_time.isoformat(),
            'session_duration': str(duration),
            'operations_performed': self.operation_count,
            'errors_encountered': self.error_count,
            'warnings_issued': self.warning_count,
            'log_file': str(self.log_file_path) if self.log_file_path else None,
            'working_directory': os.getcwd()
        }


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class GitAutomation:
    """Automates git operations for deployment with comprehensive logging and error handling"""
    
    def __init__(self, repo_path: str = ".", logger: DeploymentLogger = None):
        self.repo_path = repo_path
        self.logger = logger or DeploymentLogger()
        self.modified_files = []
        self.staged_files = []
        self.untracked_files = []
        
        self.logger.info(f"🔧 GitAutomation initialized", {
            'repo_path': self.repo_path,
            'absolute_path': os.path.abspath(self.repo_path)
        })
        
        # Validate git repository
        self._validate_git_repo()
        
    def _validate_git_repo(self):
        """Validate that we're in a git repository"""
        try:
            self.logger.operation_start("Repository validation")
            
            git_dir = os.path.join(self.repo_path, '.git')
            if not os.path.exists(git_dir):
                raise Exception(f"Not a git repository: {os.path.abspath(self.repo_path)}")
            
            # Check git version
            success, git_version = self.run_command(["git", "--version"], capture_output=True)
            if success:
                self.logger.info(f"✅ Git repository validated", {
                    'git_version': git_version.strip(),
                    'git_dir_exists': True
                })
            else:
                raise Exception("Git not found or not working")
                
            self.logger.operation_end("Repository validation", True)
            
        except Exception as e:
            self.logger.operation_end("Repository validation", False, {'error': str(e)})
            raise
        
    def run_command(self, cmd: List[str], capture_output: bool = True, timeout: int = 30) -> Tuple[bool, str]:
        """Run a git command with comprehensive logging and error handling"""
        cmd_str = ' '.join(cmd)
        
        try:
            self.logger.debug(f"🔧 Executing command: {cmd_str}", {
                'command': cmd,
                'capture_output': capture_output,
                'timeout': timeout,
                'cwd': self.repo_path
            })
            
            start_time = datetime.now()
            
            if capture_output:
                result = subprocess.run(
                    cmd, 
                    cwd=self.repo_path, 
                    capture_output=True, 
                    text=True,
                    timeout=timeout
                )
                output = result.stdout.strip()
                error_output = result.stderr.strip()
                
                duration = datetime.now() - start_time
                
                if result.returncode == 0:
                    self.logger.debug(f"✅ Command successful: {cmd_str}", {
                        'return_code': result.returncode,
                        'duration_ms': duration.total_seconds() * 1000,
                        'output_length': len(output),
                        'has_stderr': bool(error_output)
                    })
                    return True, output
                else:
                    self.logger.error(f"❌ Command failed: {cmd_str}", {
                        'return_code': result.returncode,
                        'duration_ms': duration.total_seconds() * 1000,
                        'stdout': output,
                        'stderr': error_output
                    })
                    return False, error_output or output
            else:
                result = subprocess.run(cmd, cwd=self.repo_path, text=True, timeout=timeout)
                duration = datetime.now() - start_time
                
                success = result.returncode == 0
                self.logger.debug(f"{'✅' if success else '❌'} Command executed: {cmd_str}", {
                    'return_code': result.returncode,
                    'duration_ms': duration.total_seconds() * 1000,
                    'capture_output': False
                })
                return success, ""
                
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"⏰ Command timeout: {cmd_str}", {
                'timeout_seconds': timeout,
                'command': cmd
            }, e)
            return False, f"Command timeout after {timeout} seconds"
            
        except FileNotFoundError as e:
            self.logger.error(f"📂 Command not found: {cmd_str}", {
                'command': cmd[0] if cmd else None,
                'path': os.environ.get('PATH', 'Not available')
            }, e)
            return False, f"Command not found: {cmd[0] if cmd else 'Unknown'}"
            
        except Exception as e:
            self.logger.error(f"💥 Unexpected error running command: {cmd_str}", {
                'command': cmd,
                'exception_type': type(e).__name__
            }, e)
            return False, f"Unexpected error: {str(e)}"
    
    def print_status(self, message: str, color: str = Colors.OKBLUE):
        """Print colored status message with logging"""
        colored_message = f"{color}{Colors.BOLD}[DEPLOY]{Colors.ENDC} {message}"
        print(colored_message)
        # Also log without color codes
        clean_message = message
        self.logger.info(clean_message)
    
    def check_git_status(self) -> bool:
        """Check git repository status and categorize files with detailed logging"""
        try:
            self.logger.operation_start("Git status check")
            self.print_status("🔍 Checking git repository status...", Colors.HEADER)
            
            # Get porcelain status
            success, output = self.run_command(["git", "status", "--porcelain"])
            if not success:
                raise Exception(f"Failed to check git status: {output}")
            
            # Parse git status output
            self.modified_files = []
            self.staged_files = []
            self.untracked_files = []
            
            status_lines = [line for line in output.split('\n') if line.strip()]
            
            self.logger.debug(f"📋 Parsing {len(status_lines)} status lines", {
                'total_lines': len(status_lines),
                'raw_output_preview': output[:200] + '...' if len(output) > 200 else output
            })
            
            for line in status_lines:
                try:
                    if len(line) < 3:
                        continue
                        
                    status = line[:2]
                    filename = line[3:]
                    
                    # Categorize files based on git status codes
                    if status == '??':
                        self.untracked_files.append(filename)
                        self.logger.debug(f"🆕 Untracked file: {filename}")
                    elif status[0] in ['M', 'A', 'D', 'R', 'C']:
                        self.staged_files.append(filename)
                        self.logger.debug(f"✅ Staged file: {filename} (status: {status})")
                    elif status[1] in ['M', 'D']:
                        self.modified_files.append(filename)
                        self.logger.debug(f"🔄 Modified file: {filename} (status: {status})")
                    else:
                        self.logger.warning(f"🤔 Unknown status code: {status} for file: {filename}")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Error parsing status line: {line}", {'line': line}, e)
                    continue
            
            # Get additional repository information
            branch_success, current_branch = self.run_command(["git", "branch", "--show-current"])
            remote_success, remote_info = self.run_command(["git", "remote", "-v"])
            
            # Display comprehensive status summary
            print(f"\n{Colors.OKGREEN}📊 Repository Status Summary:{Colors.ENDC}")
            print(f"  🌿 Current branch: {current_branch if branch_success else 'Unknown'}")
            print(f"  🔴 Modified files: {len(self.modified_files)}")
            print(f"  🟢 Staged files: {len(self.staged_files)}")
            print(f"  🟡 Untracked files: {len(self.untracked_files)}")
            
            if self.modified_files:
                print(f"\n{Colors.WARNING}📝 Modified files:{Colors.ENDC}")
                for file in self.modified_files:
                    print(f"    • {file}")
            
            if self.staged_files:
                print(f"\n{Colors.OKGREEN}✅ Staged files:{Colors.ENDC}")
                for file in self.staged_files:
                    print(f"    • {file}")
            
            if self.untracked_files:
                print(f"\n{Colors.OKCYAN}❓ Untracked files:{Colors.ENDC}")
                for file in self.untracked_files:
                    print(f"    • {file}")
            
            # Log comprehensive status information
            status_summary = {
                'current_branch': current_branch if branch_success else None,
                'modified_count': len(self.modified_files),
                'staged_count': len(self.staged_files),
                'untracked_count': len(self.untracked_files),
                'modified_files': self.modified_files,
                'staged_files': self.staged_files,
                'untracked_files': self.untracked_files,
                'has_remote': remote_success and bool(remote_info.strip())
            }
            
            self.logger.operation_end("Git status check", True, status_summary)
            return True
            
        except Exception as e:
            self.logger.operation_end("Git status check", False, {'error': str(e)})
            self.print_status(f"❌ Failed to check git status: {e}", Colors.FAIL)
            return False
    
    def show_diffs(self, files: List[str] = None) -> bool:
        """Show git diffs for specified files or all modified/staged files with detailed logging"""
        try:
            self.logger.operation_start("Show file diffs")
            files_to_diff = files or (self.modified_files + self.staged_files)
            
            if not files_to_diff:
                self.print_status("ℹ️ No modified or staged files to show diffs for", Colors.OKCYAN)
                self.logger.info("No files to diff", {'requested_files': files, 'modified_files': self.modified_files, 'staged_files': self.staged_files})
                return True
            
            self.print_status(f"📋 Showing differences for {len(files_to_diff)} files...", Colors.HEADER)
            
            diff_stats = {
                'files_processed': 0,
                'files_with_changes': 0,
                'total_additions': 0,
                'total_deletions': 0,
                'files_failed': 0
            }
            
            for file in files_to_diff:
                try:
                    # Determine if file is staged or modified
                    is_staged = file in self.staged_files
                    is_modified = file in self.modified_files
                    
                    status_text = "📦 Staged" if is_staged else "🔄 Modified"
                    print(f"\n{Colors.BOLD}{Colors.UNDERLINE}📄 Diff for {file} ({status_text}):{Colors.ENDC}")
                    self.logger.debug(f"🔍 Getting diff for file: {file} (staged: {is_staged})")
                    
                    # Choose diff command based on file status
                    diff_cmd = ["git", "diff", "--staged", file] if is_staged else ["git", "diff", file]
                    stat_cmd = ["git", "diff", "--staged", "--stat", file] if is_staged else ["git", "diff", "--stat", file]
                    
                    # Get diff with statistics
                    success, diff_output = self.run_command(stat_cmd)
                    if success and diff_output:
                        print(f"  {Colors.OKCYAN}📊 Stats: {diff_output}{Colors.ENDC}")
                    
                    # Get actual diff content
                    success, diff_content = self.run_command(diff_cmd)
                    
                    if not success:
                        print(f"  {Colors.FAIL}❌ Failed to get diff for {file}: {diff_content}{Colors.ENDC}")
                        self.logger.error(f"Failed to get diff for {file}", {'file': file, 'error': diff_content})
                        diff_stats['files_failed'] += 1
                        continue
                    
                    if not diff_content.strip():
                        print(f"  {Colors.OKCYAN}ℹ️ No changes to display{Colors.ENDC}")
                        self.logger.debug(f"No diff content for {file}")
                        diff_stats['files_processed'] += 1
                        continue
                    
                    # Count additions and deletions
                    additions = len([line for line in diff_content.split('\n') if line.startswith('+')])
                    deletions = len([line for line in diff_content.split('\n') if line.startswith('-')])
                    
                    diff_stats['files_with_changes'] += 1
                    diff_stats['total_additions'] += additions
                    diff_stats['total_deletions'] += deletions
                    
                    # Show abbreviated diff (first 50 lines)
                    diff_lines = diff_content.split('\n')
                    lines_to_show = min(50, len(diff_lines))
                    
                    for line in diff_lines[:lines_to_show]:
                        self._print_diff_line(line)
                    
                    if len(diff_lines) > 50:
                        remaining = len(diff_lines) - 50
                        print(f"\n  {Colors.WARNING}... ({remaining} more lines truncated - use 'git diff {file}' to see full diff){Colors.ENDC}")
                    
                    diff_stats['files_processed'] += 1
                    
                    self.logger.debug(f"✅ Diff processed for {file}", {
                        'file': file,
                        'total_lines': len(diff_lines),
                        'lines_shown': lines_to_show,
                        'additions': additions,
                        'deletions': deletions
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing diff for {file}", {'file': file}, e)
                    print(f"  {Colors.FAIL}❌ Error processing diff for {file}: {e}{Colors.ENDC}")
                    diff_stats['files_failed'] += 1
                    continue
            
            # Print summary
            print(f"\n{Colors.BOLD}📊 Diff Summary:{Colors.ENDC}")
            print(f"  📁 Files processed: {diff_stats['files_processed']}")
            print(f"  📝 Files with changes: {diff_stats['files_with_changes']}")
            print(f"  ➕ Total additions: {diff_stats['total_additions']}")
            print(f"  ➖ Total deletions: {diff_stats['total_deletions']}")
            if diff_stats['files_failed'] > 0:
                print(f"  ❌ Failed files: {diff_stats['files_failed']}")
            
            self.logger.operation_end("Show file diffs", True, diff_stats)
            return True
            
        except Exception as e:
            self.logger.operation_end("Show file diffs", False, {'error': str(e)})
            self.print_status(f"❌ Failed to show diffs: {e}", Colors.FAIL)
            return False
    
    def _print_diff_line(self, line: str):
        """Print a diff line with appropriate coloring and logging"""
        try:
            if line.startswith('+') and not line.startswith('+++'):
                print(f"  {Colors.OKGREEN}{line}{Colors.ENDC}")
            elif line.startswith('-') and not line.startswith('---'):
                print(f"  {Colors.FAIL}{line}{Colors.ENDC}")
            elif line.startswith('@@'):
                print(f"  {Colors.OKCYAN}{line}{Colors.ENDC}")
            else:
                print(f"  {line}")
        except Exception as e:
            # Fallback for any encoding issues
            self.logger.warning(f"Error printing diff line", {'line_preview': str(line)[:50]}, e)
            print(f"  [Line display error: {e}]")
    
    def stage_files(self, files: List[str] = None, stage_all: bool = False) -> bool:
        """Stage files for commit with comprehensive logging and error handling"""
        try:
            self.logger.operation_start("Stage files for commit")
            
            if stage_all:
                self.print_status("📦 Staging all modified and untracked files...", Colors.HEADER)
                
                # Log what will be staged
                all_files = self.modified_files + self.untracked_files
                self.logger.info(f"Staging all files", {
                    'total_files': len(all_files),
                    'modified_files': self.modified_files,
                    'untracked_files': self.untracked_files
                })
                
                success, output = self.run_command(["git", "add", "."])
                if success:
                    self.print_status("✅ All files staged successfully", Colors.OKGREEN)
                    self.logger.operation_end("Stage files for commit", True, {
                        'method': 'stage_all',
                        'files_count': len(all_files)
                    })
                    return True
                else:
                    raise Exception(f"Failed to stage all files: {output}")
            
            files_to_stage = files or self.modified_files
            if not files_to_stage:
                self.print_status("ℹ️ No files to stage", Colors.OKCYAN)
                self.logger.info("No files to stage", {
                    'requested_files': files,
                    'modified_files': self.modified_files
                })
                return True
            
            self.print_status(f"📦 Staging {len(files_to_stage)} files...", Colors.HEADER)
            
            staging_results = {
                'successful': [],
                'failed': [],
                'total_attempted': len(files_to_stage)
            }
            
            for file in files_to_stage:
                try:
                    self.logger.debug(f"Staging file: {file}")
                    success, output = self.run_command(["git", "add", file])
                    
                    if success:
                        print(f"  {Colors.OKGREEN}✅ Staged: {file}{Colors.ENDC}")
                        staging_results['successful'].append(file)
                        self.logger.debug(f"✅ Successfully staged: {file}")
                    else:
                        error_msg = f"Failed to stage {file}: {output}"
                        print(f"  {Colors.FAIL}❌ {error_msg}{Colors.ENDC}")
                        staging_results['failed'].append({'file': file, 'error': output})
                        self.logger.error(error_msg, {'file': file, 'git_output': output})
                        
                except Exception as e:
                    error_msg = f"Exception staging {file}: {e}"
                    print(f"  {Colors.FAIL}❌ {error_msg}{Colors.ENDC}")
                    staging_results['failed'].append({'file': file, 'error': str(e)})
                    self.logger.error(error_msg, {'file': file}, e)
            
            # Check results
            if staging_results['failed']:
                self.logger.operation_end("Stage files for commit", False, staging_results)
                self.print_status(f"❌ {len(staging_results['failed'])} files failed to stage", Colors.FAIL)
                return False
            else:
                self.print_status("✅ All specified files staged successfully", Colors.OKGREEN)
                self.logger.operation_end("Stage files for commit", True, staging_results)
                return True
            
        except Exception as e:
            self.logger.operation_end("Stage files for commit", False, {'error': str(e)})
            self.print_status(f"❌ Failed to stage files: {e}", Colors.FAIL)
            return False
    
    def generate_commit_message(self, files: List[str] = None) -> str:
        """Generate intelligent commit message based on file changes with detailed analysis"""
        try:
            self.logger.operation_start("Generate commit message")
            changed_files = files or self.modified_files + self.staged_files
            
            if not changed_files:
                default_msg = "chore: general updates and improvements"
                self.logger.info("No files for commit message generation, using default", {
                    'default_message': default_msg,
                    'files_provided': files,
                    'modified_files': self.modified_files,
                    'staged_files': self.staged_files
                })
                return default_msg
            
            # Analyze file changes to generate meaningful commit message
            analysis = {
                'app_changes': any('app.py' in f for f in changed_files),
                'config_changes': any(f.endswith(('.txt', '.toml', '.yml', '.yaml', '.json')) for f in changed_files),
                'script_changes': any(f.endswith('.py') and f != 'app.py' for f in changed_files),
                'doc_changes': any(f.endswith(('.md', '.rst')) for f in changed_files),
                'deployment_changes': any('deploy' in f.lower() for f in changed_files),
                'requirements_changes': any('requirements' in f.lower() for f in changed_files),
                'total_files': len(changed_files),
                'file_types': {}
            }
            
            # Count file types
            for file in changed_files:
                ext = Path(file).suffix.lower()
                analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
            
            self.logger.debug("File change analysis for commit message", analysis)
            
            # Generate commit type and description based on analysis
            if analysis['deployment_changes']:
                message = "feat: enhance deployment automation and workflow scripts"
            elif analysis['app_changes'] and analysis['total_files'] == 1:
                # Single app.py change - try to be more specific
                message = "feat: update main application functionality and UI improvements"
            elif analysis['app_changes']:
                message = "feat: enhance Bitcoin dashboard with UI and functionality updates"
            elif analysis['script_changes'] and analysis['config_changes']:
                message = "chore: update configuration and automation scripts"
            elif analysis['requirements_changes']:
                message = "chore: update project dependencies and requirements"
            elif analysis['config_changes']:
                message = "chore: update project configuration files"
            elif analysis['script_changes']:
                message = "feat: add new automation and utility scripts"
            elif analysis['doc_changes']:
                message = "docs: update project documentation and guides"
            else:
                message = "chore: project maintenance and improvements"
            
            # Add file count context if significant
            if analysis['total_files'] > 5:
                message += f" ({analysis['total_files']} files)"
            
            self.logger.operation_end("Generate commit message", True, {
                'generated_message': message,
                'analysis': analysis,
                'changed_files': changed_files
            })
            
            return message
            
        except Exception as e:
            self.logger.operation_end("Generate commit message", False, {'error': str(e)})
            self.logger.error("Failed to generate commit message", exception=e)
            return "chore: automated commit with deployment script"
    
    def commit_changes(self, message: str = None, auto_message: bool = False) -> bool:
        """Commit staged changes with comprehensive validation and logging"""
        try:
            self.logger.operation_start("Commit staged changes")
            
            # Check if there are staged changes
            self.logger.debug("Checking for staged changes")
            success, output = self.run_command(["git", "diff", "--cached", "--name-only"])
            if not success:
                raise Exception(f"Failed to check staged changes: {output}")
            
            staged_files = [f for f in output.split('\n') if f.strip()]
            if not staged_files:
                self.print_status("ℹ️ No staged changes to commit", Colors.OKCYAN)
                self.logger.info("No staged changes found for commit")
                return True
            
            # Get additional pre-commit information
            commit_info = {
                'staged_files': staged_files,
                'staged_count': len(staged_files),
                'timestamp': datetime.now().isoformat()
            }
            
            # Get current branch and commit hash
            branch_success, current_branch = self.run_command(["git", "branch", "--show-current"])
            if branch_success:
                commit_info['current_branch'] = current_branch
            
            # Get last commit hash for reference
            hash_success, last_commit = self.run_command(["git", "rev-parse", "HEAD"])
            if hash_success:
                commit_info['parent_commit'] = last_commit
            
            # Generate or get commit message
            if auto_message:
                message = self.generate_commit_message(staged_files)
                self.logger.info("Using auto-generated commit message", {'message': message})
            elif not message:
                # Interactive message input
                print(f"\n{Colors.BOLD}📝 Enter commit message:{Colors.ENDC}")
                suggested = self.generate_commit_message(staged_files)
                print(f"  {Colors.OKCYAN}💡 Suggested: {suggested}{Colors.ENDC}")
                
                try:
                    message = input(f"  {Colors.WARNING}📝 Your message: {Colors.ENDC}").strip()
                except KeyboardInterrupt:
                    self.logger.info("Commit cancelled by user (Ctrl+C)")
                    self.print_status("❌ Commit cancelled by user", Colors.WARNING)
                    return False
                
                if not message:
                    message = suggested
                    print(f"  {Colors.OKCYAN}Using suggested message{Colors.ENDC}")
                    self.logger.info("Using suggested message as fallback", {'message': message})
            
            # Validate commit message
            if not message or len(message.strip()) < 3:
                raise Exception("Commit message too short (minimum 3 characters)")
            
            commit_info['commit_message'] = message
            
            self.print_status(f"💾 Committing with message: '{message}'", Colors.HEADER)
            self.logger.info(f"Executing commit", commit_info)
            
            # Perform the commit
            success, output = self.run_command(["git", "commit", "-m", message])
            
            if success:
                # Get new commit hash
                new_hash_success, new_commit_hash = self.run_command(["git", "rev-parse", "HEAD"])
                if new_hash_success:
                    commit_info['new_commit_hash'] = new_commit_hash
                
                self.print_status("✅ Commit successful!", Colors.OKGREEN)
                print(f"  {Colors.OKCYAN}📦 Files committed: {len(staged_files)}{Colors.ENDC}")
                for file in staged_files:
                    print(f"    • {file}")
                
                if new_hash_success:
                    print(f"  {Colors.OKCYAN}🔗 Commit hash: {new_commit_hash[:8]}...{Colors.ENDC}")
                
                self.logger.operation_end("Commit staged changes", True, commit_info)
                return True
                
            else:
                # Handle commit failure
                commit_info['git_error'] = output
                self.logger.operation_end("Commit staged changes", False, commit_info)
                
                # Try to provide helpful error messages
                if "nothing to commit" in output.lower():
                    self.print_status("ℹ️ Nothing to commit - all changes already staged?", Colors.OKCYAN)
                elif "author identity unknown" in output.lower():
                    self.print_status("❌ Git user identity not configured. Run: git config --global user.email 'you@example.com'", Colors.FAIL)
                else:
                    self.print_status(f"❌ Commit failed: {output}", Colors.FAIL)
                
                return False
                
        except Exception as e:
            self.logger.operation_end("Commit staged changes", False, {'error': str(e)})
            self.print_status(f"❌ Commit failed: {e}", Colors.FAIL)
            return False
    
    def push_changes(self, remote: str = "origin", branch: str = "main") -> bool:
        """Push committed changes to remote repository with comprehensive error handling"""
        try:
            self.logger.operation_start("Push changes to remote")
            
            push_info = {
                'remote': remote,
                'branch': branch,
                'timestamp': datetime.now().isoformat()
            }
            
            # Validate remote exists
            self.logger.debug(f"Validating remote: {remote}")
            remote_success, remote_list = self.run_command(["git", "remote"])
            if remote_success:
                available_remotes = remote_list.split('\n') if remote_list else []
                push_info['available_remotes'] = available_remotes
                
                if remote not in available_remotes:
                    self.logger.warning(f"Remote '{remote}' not found", {
                        'requested_remote': remote,
                        'available_remotes': available_remotes
                    })
                    self.print_status(f"⚠️ Remote '{remote}' not found. Available: {', '.join(available_remotes)}", Colors.WARNING)
                    # Continue anyway - git will provide its own error
            
            # Check if we have commits to push
            self.logger.debug("Checking for unpushed commits")
            ahead_success, ahead_output = self.run_command(["git", "rev-list", "--count", f"{remote}/{branch}..HEAD"])
            if ahead_success and ahead_output.strip().isdigit():
                commits_ahead = int(ahead_output.strip())
                push_info['commits_ahead'] = commits_ahead
                
                if commits_ahead == 0:
                    self.print_status("ℹ️ No new commits to push", Colors.OKCYAN)
                    self.logger.info("No commits to push", push_info)
                    return True
                else:
                    self.logger.info(f"Found {commits_ahead} commits to push", push_info)
            
            self.print_status(f"🚀 Pushing to {remote}/{branch}...", Colors.HEADER)
            
            # Perform the push with timeout
            success, output = self.run_command(["git", "push", remote, branch], timeout=60)
            
            if success:
                self.print_status("✅ Push successful!", Colors.OKGREEN)
                
                # Get additional success information
                if "up to date" in output.lower():
                    print(f"  {Colors.OKCYAN}📊 Repository was already up to date{Colors.ENDC}")
                elif commits_ahead and commits_ahead > 0:
                    print(f"  {Colors.OKCYAN}📊 Pushed {commits_ahead} commit(s){Colors.ENDC}")
                
                push_info['push_output'] = output
                self.logger.operation_end("Push changes to remote", True, push_info)
                return True
                
            else:
                # Handle push failure with detailed error analysis
                push_info['error_output'] = output
                
                if "non-fast-forward" in output.lower():
                    self.print_status("❌ Push rejected: non-fast-forward (pull needed)", Colors.FAIL)
                    print(f"  {Colors.WARNING}💡 Try: git pull {remote} {branch} then push again{Colors.ENDC}")
                elif "permission denied" in output.lower():
                    self.print_status("❌ Push failed: Permission denied (check credentials)", Colors.FAIL)
                elif "could not resolve host" in output.lower():
                    self.print_status("❌ Push failed: Network/DNS issue", Colors.FAIL)
                elif "repository not found" in output.lower():
                    self.print_status("❌ Push failed: Repository not found", Colors.FAIL)
                else:
                    self.print_status(f"❌ Push failed: {output}", Colors.FAIL)
                
                self.logger.operation_end("Push changes to remote", False, push_info)
                return False
                
        except Exception as e:
            self.logger.operation_end("Push changes to remote", False, {'error': str(e)})
            self.print_status(f"❌ Push failed with exception: {e}", Colors.FAIL)
            return False


def interactive_menu(git_auto: GitAutomation) -> bool:
    """Interactive menu for deployment operations with enhanced error handling"""
    try:
        git_auto.logger.operation_start("Interactive deployment menu")
        
        while True:
            try:
                print(f"\n{Colors.BOLD}{Colors.HEADER}🚀 Bitcoin Dashboard Deployment Menu{Colors.ENDC}")
                print(f"{Colors.BOLD}{'='*50}{Colors.ENDC}")
                print(f"1. {Colors.OKBLUE}🔍 Check git status{Colors.ENDC}")
                print(f"2. {Colors.OKBLUE}📋 Show file diffs{Colors.ENDC}")
                print(f"3. {Colors.OKBLUE}📦 Stage files{Colors.ENDC}")
                print(f"4. {Colors.OKBLUE}💾 Commit changes{Colors.ENDC}")
                print(f"5. {Colors.OKBLUE}🚀 Push to remote{Colors.ENDC}")
                print(f"6. {Colors.WARNING}⚡ Quick deploy (all steps){Colors.ENDC}")
                print(f"7. {Colors.OKCYAN}📊 View session summary{Colors.ENDC}")
                print(f"8. {Colors.FAIL}❌ Exit{Colors.ENDC}")
                
                try:
                    choice = input(f"\n{Colors.BOLD}Select option (1-8): {Colors.ENDC}").strip()
                    git_auto.logger.debug(f"User selected menu option: {choice}")
                except KeyboardInterrupt:
                    print(f"\n{Colors.WARNING}⚠️ Operation cancelled by user{Colors.ENDC}")
                    git_auto.logger.info("Menu operation cancelled by user (Ctrl+C)")
                    continue
                except EOFError:
                    print(f"\n{Colors.WARNING}⚠️ Input ended unexpectedly{Colors.ENDC}")
                    git_auto.logger.info("Menu input ended unexpectedly (EOF)")
                    return True
                
                if choice == '1':
                    try:
                        git_auto.check_git_status()
                    except Exception as e:
                        git_auto.logger.error("Failed to check git status", exception=e)
                        print(f"{Colors.FAIL}❌ Error checking git status: {e}{Colors.ENDC}")
                
                elif choice == '2':
                    try:
                        if not git_auto.modified_files:
                            git_auto.check_git_status()
                        
                        if git_auto.modified_files:
                            try:
                                files_choice = input(f"\n{Colors.WARNING}Show diffs for: (a)ll files, (s)pecific files, (Enter) for all: {Colors.ENDC}").strip().lower()
                                
                                if files_choice == 's':
                                    print(f"\n{Colors.OKCYAN}Available files:{Colors.ENDC}")
                                    for i, file in enumerate(git_auto.modified_files, 1):
                                        print(f"  {i}. {file}")
                                    
                                    try:
                                        file_nums = input(f"\n{Colors.WARNING}Enter file numbers (comma-separated): {Colors.ENDC}").strip()
                                        selected_files = []
                                        for num in file_nums.split(','):
                                            idx = int(num.strip()) - 1
                                            if 0 <= idx < len(git_auto.modified_files):
                                                selected_files.append(git_auto.modified_files[idx])
                                        
                                        if selected_files:
                                            git_auto.show_diffs(selected_files)
                                        else:
                                            print(f"{Colors.FAIL}No valid files selected{Colors.ENDC}")
                                            
                                    except ValueError as e:
                                        git_auto.logger.error("Invalid file selection", {'input': file_nums}, e)
                                        print(f"{Colors.FAIL}Invalid file numbers: {e}{Colors.ENDC}")
                                    except Exception as e:
                                        git_auto.logger.error("Error in file selection", exception=e)
                                        print(f"{Colors.FAIL}Error selecting files: {e}{Colors.ENDC}")
                                else:
                                    git_auto.show_diffs()
                                    
                            except KeyboardInterrupt:
                                print(f"\n{Colors.WARNING}⚠️ Diff operation cancelled{Colors.ENDC}")
                                continue
                        else:
                            print(f"{Colors.OKCYAN}No modified files to show diffs for{Colors.ENDC}")
                            
                    except Exception as e:
                        git_auto.logger.error("Failed to show diffs", exception=e)
                        print(f"{Colors.FAIL}❌ Error showing diffs: {e}{Colors.ENDC}")
                
                elif choice == '3':
                    try:
                        if not git_auto.modified_files and not git_auto.untracked_files:
                            git_auto.check_git_status()
                        
                        try:
                            stage_choice = input(f"\n{Colors.WARNING}Stage: (a)ll files, (m)odified only, (s)pecific files: {Colors.ENDC}").strip().lower()
                            
                            if stage_choice == 'a':
                                git_auto.stage_files(stage_all=True)
                            elif stage_choice == 's':
                                all_files = git_auto.modified_files + git_auto.untracked_files
                                if all_files:
                                    print(f"\n{Colors.OKCYAN}Available files:{Colors.ENDC}")
                                    for i, file in enumerate(all_files, 1):
                                        print(f"  {i}. {file}")
                                    
                                    try:
                                        file_nums = input(f"\n{Colors.WARNING}Enter file numbers (comma-separated): {Colors.ENDC}").strip()
                                        selected_files = []
                                        for num in file_nums.split(','):
                                            idx = int(num.strip()) - 1
                                            if 0 <= idx < len(all_files):
                                                selected_files.append(all_files[idx])
                                        
                                        if selected_files:
                                            git_auto.stage_files(selected_files)
                                        else:
                                            print(f"{Colors.FAIL}No valid files selected{Colors.ENDC}")
                                            
                                    except ValueError as e:
                                        git_auto.logger.error("Invalid file selection for staging", {'input': file_nums}, e)
                                        print(f"{Colors.FAIL}Invalid file numbers: {e}{Colors.ENDC}")
                                else:
                                    print(f"{Colors.OKCYAN}No files available to stage{Colors.ENDC}")
                            else:
                                git_auto.stage_files()  # Stage modified files only
                                
                        except KeyboardInterrupt:
                            print(f"\n{Colors.WARNING}⚠️ Staging operation cancelled{Colors.ENDC}")
                            continue
                            
                    except Exception as e:
                        git_auto.logger.error("Failed to stage files", exception=e)
                        print(f"{Colors.FAIL}❌ Error staging files: {e}{Colors.ENDC}")
                
                elif choice == '4':
                    try:
                        try:
                            commit_choice = input(f"\n{Colors.WARNING}Commit with: (a)uto message, (c)ustom message: {Colors.ENDC}").strip().lower()
                            
                            if commit_choice == 'a':
                                git_auto.commit_changes(auto_message=True)
                            else:
                                git_auto.commit_changes()
                                
                        except KeyboardInterrupt:
                            print(f"\n{Colors.WARNING}⚠️ Commit operation cancelled{Colors.ENDC}")
                            continue
                            
                    except Exception as e:
                        git_auto.logger.error("Failed to commit changes", exception=e)
                        print(f"{Colors.FAIL}❌ Error committing changes: {e}{Colors.ENDC}")
                
                elif choice == '5':
                    try:
                        try:
                            push_choice = input(f"\n{Colors.WARNING}Push to (default: origin/main) or specify remote/branch: {Colors.ENDC}").strip()
                            
                            if push_choice:
                                parts = push_choice.split('/')
                                if len(parts) == 2:
                                    git_auto.push_changes(parts[0], parts[1])
                                else:
                                    print(f"{Colors.FAIL}Invalid format. Use: remote/branch{Colors.ENDC}")
                            else:
                                git_auto.push_changes()
                                
                        except KeyboardInterrupt:
                            print(f"\n{Colors.WARNING}⚠️ Push operation cancelled{Colors.ENDC}")
                            continue
                            
                    except Exception as e:
                        git_auto.logger.error("Failed to push changes", exception=e)
                        print(f"{Colors.FAIL}❌ Error pushing changes: {e}{Colors.ENDC}")
                
                elif choice == '6':
                    # Quick deploy - all steps with comprehensive error handling
                    try:
                        print(f"\n{Colors.BOLD}{Colors.WARNING}⚡ Quick Deploy - All Steps{Colors.ENDC}")
                        git_auto.logger.operation_start("Quick deploy workflow")
                        
                        # Step 1: Check status
                        if not git_auto.check_git_status():
                            git_auto.logger.error("Quick deploy failed at status check")
                            continue
                        
                        if not git_auto.modified_files and not git_auto.untracked_files:
                            print(f"{Colors.OKCYAN}✅ Repository is clean - nothing to deploy{Colors.ENDC}")
                            git_auto.logger.info("Quick deploy: repository clean, nothing to deploy")
                            continue
                        
                        # Step 2: Show brief diff summary
                        print(f"\n{Colors.BOLD}📋 Quick diff summary:{Colors.ENDC}")
                        
                        # Show both modified and staged files
                        all_changed_files = git_auto.modified_files + git_auto.staged_files
                        if all_changed_files:
                            for file in all_changed_files[:3]:  # Show first 3 files only
                                status_indicator = "🔄" if file in git_auto.modified_files else "✅"
                                print(f"  {status_indicator} {Colors.WARNING}{file}{Colors.ENDC}")
                            if len(all_changed_files) > 3:
                                print(f"  • {Colors.OKCYAN}... and {len(all_changed_files) - 3} more files{Colors.ENDC}")
                            
                            # Show actual diffs for the files
                            git_auto.show_diffs(all_changed_files)
                        else:
                            print(f"  {Colors.OKCYAN}No changes to display{Colors.ENDC}")
                        
                        # Step 3: Confirm and stage all
                        try:
                            confirm = input(f"\n{Colors.WARNING}🚀 Deploy all changes? (y/N): {Colors.ENDC}").strip().lower()
                            if confirm != 'y':
                                print(f"{Colors.OKCYAN}Deployment cancelled by user{Colors.ENDC}")
                                git_auto.logger.info("Quick deploy cancelled by user")
                                continue
                        except KeyboardInterrupt:
                            print(f"\n{Colors.WARNING}⚠️ Quick deploy cancelled{Colors.ENDC}")
                            git_auto.logger.info("Quick deploy cancelled by user (Ctrl+C)")
                            continue
                        
                        # Execute deployment steps with error handling
                        deploy_success = True
                        
                        if not git_auto.stage_files(stage_all=True):
                            deploy_success = False
                            git_auto.logger.error("Quick deploy failed at staging step")
                        
                        if deploy_success and not git_auto.commit_changes(auto_message=True):
                            deploy_success = False
                            git_auto.logger.error("Quick deploy failed at commit step")
                        
                        if deploy_success:
                            try:
                                push_confirm = input(f"\n{Colors.WARNING}🚀 Push to remote? (Y/n): {Colors.ENDC}").strip().lower()
                                if push_confirm != 'n':
                                    if not git_auto.push_changes():
                                        deploy_success = False
                                        git_auto.logger.error("Quick deploy failed at push step")
                            except KeyboardInterrupt:
                                print(f"\n{Colors.WARNING}⚠️ Push step cancelled{Colors.ENDC}")
                                git_auto.logger.info("Quick deploy push step cancelled")
                        
                        if deploy_success:
                            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Quick deployment completed successfully!{Colors.ENDC}")
                            git_auto.logger.operation_end("Quick deploy workflow", True)
                        else:
                            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Quick deployment failed!{Colors.ENDC}")
                            git_auto.logger.operation_end("Quick deploy workflow", False)
                            
                    except Exception as e:
                        git_auto.logger.operation_end("Quick deploy workflow", False, {'error': str(e)})
                        git_auto.logger.error("Quick deploy failed with exception", exception=e)
                        print(f"{Colors.FAIL}❌ Quick deploy failed: {e}{Colors.ENDC}")
                
                elif choice == '7':
                    # Show session summary
                    try:
                        summary = git_auto.logger.get_session_summary()
                        print(f"\n{Colors.BOLD}{Colors.HEADER}📊 Deployment Session Summary{Colors.ENDC}")
                        print(f"{Colors.BOLD}{'='*40}{Colors.ENDC}")
                        print(f"🕐 Session started: {summary['session_start']}")
                        print(f"⏱️ Duration: {summary['session_duration']}")
                        print(f"🔄 Operations performed: {summary['operations_performed']}")
                        print(f"❌ Errors encountered: {summary['errors_encountered']}")
                        print(f"⚠️ Warnings issued: {summary['warnings_issued']}")
                        if summary.get('log_file'):
                            print(f"📄 Log file: {summary['log_file']}")
                        print(f"📁 Working directory: {summary['working_directory']}")
                        
                    except Exception as e:
                        git_auto.logger.error("Failed to show session summary", exception=e)
                        print(f"{Colors.FAIL}❌ Error showing session summary: {e}{Colors.ENDC}")
                
                elif choice == '8':
                    try:
                        summary = git_auto.logger.get_session_summary()
                        print(f"\n{Colors.OKCYAN}� Final Session Summary:{Colors.ENDC}")
                        print(f"  Operations: {summary['operations_performed']}")
                        print(f"  Errors: {summary['errors_encountered']}")
                        print(f"  Duration: {summary['session_duration']}")
                        print(f"\n{Colors.OKCYAN}�👋 Goodbye! Happy deploying!{Colors.ENDC}")
                        
                        git_auto.logger.operation_end("Interactive deployment menu", True)
                        return True
                        
                    except Exception as e:
                        git_auto.logger.error("Error during exit", exception=e)
                        print(f"\n{Colors.OKCYAN}👋 Goodbye! (with errors){Colors.ENDC}")
                        return True
                
                else:
                    print(f"{Colors.FAIL}Invalid choice. Please select 1-8.{Colors.ENDC}")
                    git_auto.logger.warning(f"Invalid menu choice: {choice}")
                    
            except Exception as e:
                git_auto.logger.error("Error in menu loop iteration", exception=e)
                print(f"{Colors.FAIL}❌ Menu error: {e}{Colors.ENDC}")
                print(f"{Colors.WARNING}💡 Try again or press Ctrl+C to exit{Colors.ENDC}")
                continue
                
    except KeyboardInterrupt:
        print(f"\n\n{Colors.OKCYAN}👋 Deployment interrupted. Goodbye!{Colors.ENDC}")
        git_auto.logger.info("Interactive menu interrupted by user")
        return True
    except Exception as e:
        git_auto.logger.error("Critical error in interactive menu", exception=e)
        print(f"\n{Colors.FAIL}❌ Critical menu error: {e}{Colors.ENDC}")
        return False


def main():
    """Main deployment automation function with comprehensive error handling"""
    try:
        # Initialize logging first
        logger = DeploymentLogger()
        
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("🚀 Bitcoin Crypto Dashboard - Deployment Automation")
        print("=" * 50)
        print(f"Enhanced with comprehensive logging and error handling")
        print(f"{Colors.ENDC}")
        
        logger.info("🚀 Deployment automation started", {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'command_line_args': sys.argv
        })
        
        # Check if we're in a git repository
        try:
            if not os.path.exists('.git'):
                error_msg = f"Not a git repository. Please run from your project root."
                logger.error(error_msg, {
                    'current_directory': os.getcwd(),
                    'directory_contents': os.listdir('.') if os.path.exists('.') else []
                })
                print(f"{Colors.FAIL}❌ {error_msg}{Colors.ENDC}")
                sys.exit(1)
        except Exception as e:
            logger.error("Failed to check git repository", exception=e)
            print(f"{Colors.FAIL}❌ Error checking git repository: {e}{Colors.ENDC}")
            sys.exit(1)
        
        # Initialize git automation with enhanced error handling
        try:
            git_auto = GitAutomation(logger=logger)
            logger.info("✅ GitAutomation initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize GitAutomation", exception=e)
            print(f"{Colors.FAIL}❌ Failed to initialize git automation: {e}{Colors.ENDC}")
            sys.exit(1)
        
        # Check command line arguments with detailed logging
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            logger.info(f"Processing command line argument: {arg}")
            
            try:
                if arg == '--quick' or arg == '-q':
                    # Quick deployment mode
                    logger.operation_start("Quick deployment mode (CLI)")
                    print(f"{Colors.WARNING}⚡ Quick deployment mode{Colors.ENDC}")
                    
                    try:
                        if not git_auto.check_git_status():
                            logger.error("Quick deploy failed: status check failed")
                            sys.exit(1)
                            
                        if git_auto.modified_files or git_auto.untracked_files:
                            logger.info("Quick deploy: staging, committing, and pushing changes")
                            
                            if (git_auto.stage_files(stage_all=True) and 
                                git_auto.commit_changes(auto_message=True) and 
                                git_auto.push_changes()):
                                
                                print(f"{Colors.OKGREEN}✅ Quick deployment completed successfully!{Colors.ENDC}")
                                logger.operation_end("Quick deployment mode (CLI)", True)
                            else:
                                logger.operation_end("Quick deployment mode (CLI)", False)
                                sys.exit(1)
                        else:
                            print(f"{Colors.OKCYAN}✅ Repository is clean - nothing to deploy{Colors.ENDC}")
                            logger.info("Quick deploy: repository clean, nothing to deploy")
                            
                    except Exception as e:
                        logger.operation_end("Quick deployment mode (CLI)", False, {'error': str(e)})
                        logger.error("Quick deployment failed", exception=e)
                        print(f"{Colors.FAIL}❌ Quick deployment failed: {e}{Colors.ENDC}")
                        sys.exit(1)
                    
                    return
                
                elif arg == '--all' or arg == '-a':
                    # Force deploy all files mode (bypasses git status detection)
                    logger.operation_start("Force deploy all files mode (CLI)")
                    print(f"{Colors.WARNING}⚡ Force deploy ALL files mode (bypassing git status)...{Colors.ENDC}")
                    
                    try:
                        # Skip git status check, force stage EVERYTHING in the repository
                        logger.info("Force deploy: staging ALL files in repository without any checks")
                        
                        print(f"{Colors.WARNING}🚨 WARNING: This will stage ALL files in the repository!{Colors.ENDC}")
                        print(f"{Colors.OKCYAN}📁 Forcing deployment of entire repository...{Colors.ENDC}")
                        
                        # Force add all files in the repository (even unchanged ones)
                        # This uses git add --force . to stage everything
                        if (git_auto.run_command(["git", "add", "--force", "."])[0] and 
                            git_auto.commit_changes(auto_message=True) and 
                            git_auto.push_changes()):
                            
                            print(f"{Colors.OKGREEN}✅ Force deployment completed successfully!{Colors.ENDC}")
                            logger.operation_end("Force deploy all files mode (CLI)", True)
                        else:
                            logger.operation_end("Force deploy all files mode (CLI)", False)
                            sys.exit(1)
                            
                    except Exception as e:
                        logger.operation_end("Force deploy all files mode (CLI)", False, {'error': str(e)})
                        logger.error("Force deployment failed", exception=e)
                        print(f"{Colors.FAIL}❌ Force deployment failed: {e}{Colors.ENDC}")
                        sys.exit(1)
                    
                    return
                
                elif arg == '--status' or arg == '-s':
                    # Status only mode
                    logger.operation_start("Status check mode (CLI)")
                    try:
                        git_auto.check_git_status()
                        logger.operation_end("Status check mode (CLI)", True)
                    except Exception as e:
                        logger.operation_end("Status check mode (CLI)", False, {'error': str(e)})
                        logger.error("Status check failed", exception=e)
                        print(f"{Colors.FAIL}❌ Status check failed: {e}{Colors.ENDC}")
                        sys.exit(1)
                    return
                
                elif arg == '--help' or arg == '-h':
                    # Help mode
                    logger.info("Displaying help information")
                    print(f"{Colors.OKCYAN}Usage:{Colors.ENDC}")
                    print(f"  python deploy.py           - Interactive mode")
                    print(f"  python deploy.py --quick   - Quick deploy all changes")
                    print(f"  python deploy.py --all     - Force deploy ALL files (⚠️  FORCES ALL FILES)")
                    print(f"  python deploy.py --status  - Show git status only")
                    print(f"  python deploy.py --help    - Show this help")
                    print(f"\n{Colors.OKCYAN}Features:{Colors.ENDC}")
                    print(f"  • Comprehensive logging to deployment_logs/")
                    print(f"  • Detailed error handling and recovery")
                    print(f"  • Session analytics and operation tracking")
                    print(f"  • Intelligent commit message generation")
                    return
                
                elif arg == '--logs' or arg == '-l':
                    # Show recent logs
                    logger.info("Displaying recent deployment logs")
                    try:
                        log_dir = Path("deployment_logs")
                        if log_dir.exists():
                            log_files = sorted(log_dir.glob("deployment_*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
                            if log_files:
                                print(f"{Colors.OKCYAN}📄 Recent deployment logs:{Colors.ENDC}")
                                for i, log_file in enumerate(log_files[:5]):  # Show last 5 log files
                                    size = log_file.stat().st_size
                                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                                    print(f"  {i+1}. {log_file.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
                            else:
                                print(f"{Colors.OKCYAN}No deployment logs found{Colors.ENDC}")
                        else:
                            print(f"{Colors.OKCYAN}No deployment logs directory found{Colors.ENDC}")
                    except Exception as e:
                        logger.error("Failed to show logs", exception=e)
                        print(f"{Colors.FAIL}❌ Error showing logs: {e}{Colors.ENDC}")
                    return
                
                else:
                    logger.warning(f"Unknown command line argument: {arg}")
                    print(f"{Colors.FAIL}❌ Unknown argument: {arg}{Colors.ENDC}")
                    print(f"{Colors.OKCYAN}Use --help for usage information{Colors.ENDC}")
                    sys.exit(1)
                    
            except Exception as e:
                logger.error(f"Error processing command line argument: {arg}", exception=e)
                print(f"{Colors.FAIL}❌ Error processing argument '{arg}': {e}{Colors.ENDC}")
                sys.exit(1)
        
        # Interactive mode
        try:
            logger.info("Starting interactive mode")
            interactive_menu(git_auto)
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKCYAN}👋 Deployment interrupted. Goodbye!{Colors.ENDC}")
            logger.info("Interactive mode interrupted by user")
            
        except Exception as e:
            logger.error("Interactive mode failed", exception=e)
            print(f"{Colors.FAIL}❌ Interactive mode failed: {e}{Colors.ENDC}")
            sys.exit(1)
            
        finally:
            # Final session summary
            try:
                summary = logger.get_session_summary()
                logger.info("🏁 Deployment session completed", summary)
                
                if summary['errors_encountered'] > 0:
                    print(f"\n{Colors.WARNING}⚠️ Session completed with {summary['errors_encountered']} errors{Colors.ENDC}")
                    if logger.log_file_path:
                        print(f"📄 Check log file: {logger.log_file_path}")
                        
            except Exception as e:
                print(f"{Colors.FAIL}❌ Error generating session summary: {e}{Colors.ENDC}")
    
    except Exception as e:
        # Catch-all for any unexpected errors
        try:
            if 'logger' in locals():
                logger.error("Critical deployment error", exception=e)
            else:
                print(f"{Colors.FAIL}❌ Critical error before logging initialized: {e}{Colors.ENDC}")
                traceback.print_exc()
        except:
            pass  # Don't let logging errors crash the error handler
        
        print(f"{Colors.FAIL}❌ Critical deployment error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
