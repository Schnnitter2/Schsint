"""Schsint command-line entry point."""

from schsint.bot.app import main

if __name__ == "__main__":
    import asyncio
    import logging

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
