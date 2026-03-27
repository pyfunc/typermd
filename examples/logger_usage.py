"""Structured logging with typermd.logger."""

import typermd as typer
from typermd.logger import get_logger

app = typer.Typer()
log = get_logger("deploy")


@app.command()
def deploy(
    env: str = typer.Option("staging", help="Target environment"),
    dry_run: bool = typer.Option(False, help="Dry run mode"),
) -> None:
    """Simulate a deployment with structured logging."""
    log.info(f"Starting deployment to {env}")
    log.step(1, 4, "Building artifacts...")
    log.step(2, 4, "Running tests...")
    log.step(3, 4, "Uploading package...")

    if dry_run:
        log.warning("Dry run — skipping actual deploy")
        log.step(4, 4, "Skipped.")
    else:
        log.step(4, 4, "Deploying...")
        log.success(f"Deployed to {env} successfully!")

    log.action("Next", f"Monitor at https://dashboard.example.com/{env}")


if __name__ == "__main__":
    deploy()
