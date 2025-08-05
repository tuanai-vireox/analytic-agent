#!/usr/bin/env python3
"""
Development environment setup script using uv.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True, capture_output=False):
    """Run a shell command."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True
        )
        if capture_output:
            return result.stdout.strip()
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if check:
            sys.exit(1)
        return None


def check_uv_installed():
    """Check if uv is installed."""
    if shutil.which("uv") is None:
        print("❌ uv is not installed. Please install it first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    print("✅ uv is installed")


def setup_environment():
    """Set up the environment file."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from env.example")
        print("⚠️  Please edit .env file with your configuration")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No env.example file found")


def install_dependencies():
    """Install project dependencies using uv."""
    print("📦 Installing dependencies...")
    run_command("uv sync --extra dev")
    print("✅ Dependencies installed")


def setup_pre_commit():
    """Set up pre-commit hooks."""
    print("🔧 Setting up pre-commit hooks...")
    run_command("uv run pre-commit install")
    print("✅ Pre-commit hooks installed")


def initialize_database():
    """Initialize the database."""
    print("🗄️  Initializing database...")
    run_command("uv run python scripts/init_db.py")
    print("✅ Database initialized")


def main():
    """Main setup function."""
    print("🚀 Setting up Analytic Agent development environment...")
    print("=" * 50)
    
    # Check prerequisites
    check_uv_installed()
    
    # Set up environment
    setup_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Set up pre-commit hooks
    setup_pre_commit()
    
    # Initialize database (optional)
    response = input("\n🤔 Do you want to initialize the database? (y/N): ")
    if response.lower() in ['y', 'yes']:
        initialize_database()
    
    print("\n" + "=" * 50)
    print("🎉 Development environment setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run 'make run' to start the application")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print("\nUseful commands:")
    print("- make run          # Start the application")
    print("- make test         # Run tests")
    print("- make format       # Format code")
    print("- make lint         # Run linting")
    print("- make pre-commit   # Run pre-commit checks")


if __name__ == "__main__":
    main() 