#!/usr/bin/env python3
"""
Discord Bot Entry Point
Main script to start the Discord notification bot for game spawns.
"""

import asyncio
import logging
import os
import sys
from bot import DiscordBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Discord bot."""
    try:
        # Get Discord token from environment
        discord_token = os.getenv('DISCORD_TOKEN')
        if not discord_token:
            logger.error("DISCORD_TOKEN environment variable not found!")
            logger.error("Please set your Discord bot token in the environment variables.")
            sys.exit(1)
        
        logger.info("Starting Discord notification bot...")
        
        # Create and start the bot
        bot = DiscordBot()
        await bot.start(discord_token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
