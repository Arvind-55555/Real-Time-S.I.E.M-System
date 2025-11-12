#!/usr/bin/env python3
"""
Main entry point for the Real-Time SIEM System
"""

import click
from .core.siem_engine import SIEMCore
from .config.config_manager import ConfigManager

@click.group()
def cli():
    """Real-Time SIEM System CLI"""
    pass

@cli.command()
@click.option('--config', default='config/siem_config.yaml', help='Configuration file path')
def start(config):
    """Start the SIEM system"""
    click.echo("Starting Real-Time SIEM System...")
    
    # Load configuration
    config_manager = ConfigManager(config_path=config)
    
    # Initialize and start SIEM core
    siem = SIEMCore(config_manager)
    siem.start()

@cli.command()
def status():
    """Check system status"""
    click.echo("SIEM System Status: Active")

@cli.command()
@click.option('--rule-file', help='Path to rule file to validate')
def validate_rules(rule_file):
    """Validate detection rules"""
    from .detection.rules_engine import RulesEngine
    engine = RulesEngine()
    try:
        engine.load_rules(rule_file)
        click.echo("✓ Rules validation successful")
    except Exception as e:
        click.echo(f"✗ Rules validation failed: {e}")

if __name__ == "__main__":
    cli()