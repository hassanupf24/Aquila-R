"""
Command Line Interface for Aquila-R.

Provides CLI access to Aquila-R's research capabilities.
"""

import argparse
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from aquila_r import AquilaR, AquilaConfig
from aquila_r.core.config import MethodologyParadigm, OutputLanguage


console = Console()


def print_banner():
    """Print the Aquila-R banner."""
    banner = """
    🦅 AQUILA-R
    Autonomous Bilingual Research Intelligence
    
    >> Thinking over speed
    >> Analysis over fluency
    >> Research integrity over convenience
    """
    console.print(Panel(banner, border_style="blue"))


def cmd_analyze(args):
    """Execute research analysis command."""
    config = AquilaConfig.from_env()
    agent = AquilaR(config)
    
    # Validate configuration
    issues = agent.validate_configuration()
    if issues:
        console.print("[yellow]Configuration warnings:[/yellow]")
        for issue in issues:
            console.print(f"  ⚠️ {issue}")
    
    # Resolve options
    methodology = None
    if args.methodology:
        try:
            methodology = MethodologyParadigm(args.methodology)
        except ValueError:
            console.print(f"[red]Unknown methodology: {args.methodology}[/red]")
            return 1
    
    output_language = OutputLanguage.AUTO
    if args.language:
        try:
            output_language = OutputLanguage(args.language)
        except ValueError:
            console.print(f"[red]Unknown language: {args.language}[/red]")
            return 1
    
    # Execute analysis
    console.print(f"\n[bold blue]Analyzing:[/bold blue] {args.query}\n")
    
    result = agent.analyze(
        query=args.query,
        modules=args.modules.split(",") if args.modules else None,
        methodology=methodology,
        output_language=output_language,
    )
    
    # Output result
    if result.language == "ar":
        output = result.to_arabic_markdown()
    else:
        output = result.to_markdown()
    
    console.print(Markdown(output))
    
    return 0


def cmd_status(args):
    """Show agent status."""
    config = AquilaConfig.from_env()
    agent = AquilaR(config)
    
    status = agent.get_status()
    
    console.print("\n[bold]Aquila-R Status[/bold]\n")
    console.print(f"  Agent: {status['agent']} v{status['version']}")
    console.print(f"  LLM Provider: {status['llm_provider']}")
    console.print(f"  LLM Configured: {'✓' if status['llm_configured'] else '✗'}")
    console.print(f"  Config Valid: {'✓' if status['config_valid'] else '✗'}")
    console.print(f"  LLM Connected: {'✓' if status.get('llm_connected', False) else '✗'}")
    console.print(f"\n  Active Roles:")
    for role in status['roles']:
        console.print(f"    - {role}")
    
    return 0


def cmd_identity(args):
    """Show agent identity and system prompt."""
    from aquila_r.core.identity import AgentIdentity
    
    identity = AgentIdentity()
    language = args.language or "en"
    
    prompt = identity.get_system_prompt(language)
    
    console.print(Panel(
        prompt,
        title=f"System Prompt ({language.upper()})",
        border_style="green",
    ))
    
    return 0


def cmd_glossary(args):
    """Interact with the technical glossary."""
    from aquila_r.language.glossary import TechnicalGlossary
    
    glossary = TechnicalGlossary()
    
    if args.list_domains:
        console.print("\n[bold]Glossary Domains:[/bold]")
        for domain in glossary.get_domains():
            console.print(f"  - {domain}")
        return 0
    
    if args.domain:
        entries = glossary.get_by_domain(args.domain)
        console.print(f"\n[bold]Terms in '{args.domain}':[/bold]\n")
        for entry in entries:
            status = "✓" if entry.status.value == "approved" else "?"
            console.print(f"  {status} {entry.term_en} → {entry.term_ar}")
        return 0
    
    if args.term:
        entry = glossary.get_entry(args.term)
        if entry:
            console.print(f"\n[bold]{entry.term_en}[/bold] ({entry.term_ar})")
            console.print(f"  Domain: {entry.domain}")
            console.print(f"  Status: {entry.status.value}")
            if entry.alternatives_ar:
                console.print(f"  Alternatives: {', '.join(entry.alternatives_ar)}")
            if entry.usage_notes:
                console.print(f"  Notes: {entry.usage_notes}")
        else:
            console.print(f"[yellow]Term not found: {args.term}[/yellow]")
        return 0
    
    # Show summary
    summary = glossary.get_summary()
    console.print("\n[bold]Glossary Summary:[/bold]")
    console.print(f"  Total entries: {summary['total_entries']}")
    console.print(f"  Domains: {', '.join(summary['domains'])}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="aquila-r",
        description="Aquila-R: Autonomous Bilingual Research Intelligence",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Perform research analysis")
    analyze_parser.add_argument("query", help="Research query or question")
    analyze_parser.add_argument(
        "-m", "--modules",
        help="Comma-separated list of modules (literature,synthesis,critical)",
    )
    analyze_parser.add_argument(
        "--methodology",
        choices=["positivist", "interpretivist", "critical", "pragmatist", "mixed"],
        help="Research methodology paradigm",
    )
    analyze_parser.add_argument(
        "-l", "--language",
        choices=["en", "ar", "auto", "bilingual"],
        help="Output language",
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show agent status")
    status_parser.set_defaults(func=cmd_status)
    
    # Identity command
    identity_parser = subparsers.add_parser("identity", help="Show agent identity")
    identity_parser.add_argument(
        "-l", "--language",
        choices=["en", "ar"],
        default="en",
        help="Language for system prompt",
    )
    identity_parser.set_defaults(func=cmd_identity)
    
    # Glossary command
    glossary_parser = subparsers.add_parser("glossary", help="Technical glossary")
    glossary_parser.add_argument("-t", "--term", help="Look up a term")
    glossary_parser.add_argument("-d", "--domain", help="List terms in domain")
    glossary_parser.add_argument(
        "--list-domains",
        action="store_true",
        help="List all domains",
    )
    glossary_parser.set_defaults(func=cmd_glossary)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
