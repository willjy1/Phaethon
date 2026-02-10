"""Phaethon entry point."""

import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║       🔥 PHAETHON: Attention Firewall 🔥                      ║
    ║                                                                ║
    ║  Learning your values. Protecting your focus.                 ║
    ║                                                                ║
    ║  An intelligent filter that learns your higher-order          ║
    ║  productive values and curates your entire digital            ║
    ║  experience accordingly.                                      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main entry point."""
    print_banner()
    
    logger.info("Starting Phaethon server...")
    
    import uvicorn
    from phaethon import config
    
    uvicorn.run(
        "phaethon.server.app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
