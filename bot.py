"""
Discord Bot Implementation for Game Spawn Notifications.
"""

import logging
import discord
from discord.ext import commands
from scheduler_manager import SpawnSchedulerManager
from config import CHANNEL_NAME

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Discord bot for sending game spawn notifications."""
    
    def __init__(self):
        """Initialize the Discord bot."""
        # Set up bot intents - using only basic permissions
        intents = discord.Intents.default()
        intents.message_content = False  # Not needed for sending messages
        intents.guilds = True
        
        # Initialize bot with command prefix
        super().__init__(
            command_prefix='!spawn',
            intents=intents,
            help_command=None
        )
        
        self.spawn_scheduler = None
        self.target_channel = None
    
    async def setup_hook(self):
        """Set up the bot after login."""
        logger.info("Setting up bot...")
        
        # Initialize scheduler with message callback
        self.spawn_scheduler = SpawnSchedulerManager(self.send_spawn_message)
        
        # Set up all spawn schedules
        await self.spawn_scheduler.setup_schedules()
        
        # Start the scheduler
        await self.spawn_scheduler.start()
        
        logger.info("Bot setup completed")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        
        # Find the target channel
        await self.find_target_channel()
        
        if self.target_channel:
            logger.info(f"Target channel found: {self.target_channel.name} (ID: {self.target_channel.id})")
            
            # Send startup message
            try:
                embed = discord.Embed(
                    title="🐉 Yohara Spawn Bot Online",
                    description="Bot is now active and monitoring spawn schedules!",
                    color=0x00ff00
                )
                embed.add_field(
                    name="Scheduled Notifications",
                    value="• Temintia Misterioasa V5 (every 2h)\n• Pustietate (every 3h)\n• Canionul Nordic (every 4h)",
                    inline=False
                )
                embed.add_field(
                    name="Start Time",
                    value="12:10 PM Bucharest Time",
                    inline=True
                )
                
                await self.target_channel.send(embed=embed)
                logger.info("Startup message sent successfully")
                
            except Exception as e:
                logger.error(f"Failed to send startup message: {e}")
        else:
            logger.error(f"Could not find target channel: {CHANNEL_NAME}")
    
    async def find_target_channel(self):
        """Find the target channel by name."""
        try:
            for guild in self.guilds:
                for channel in guild.text_channels:
                    if channel.name == CHANNEL_NAME:
                        self.target_channel = channel
                        return
            
            logger.warning(f"Channel '{CHANNEL_NAME}' not found in any guild")
            
        except Exception as e:
            logger.error(f"Error finding target channel: {e}")
    
    async def send_spawn_message(self, message):
        """
        Send a spawn notification message to the target channel.
        
        Args:
            message: The message to send
        """
        try:
            if not self.target_channel:
                logger.error("Target channel not available")
                return
            
            # Create an embed for better visual appearance
            embed = discord.Embed(
                title="⚔️ Boss Spawn Alert",
                description=message,
                color=0xff6b35
            )
            embed.set_footer(text="Yohara Spawn Notification System")
            
            # Send the message
            await self.target_channel.send(embed=embed)
            logger.info(f"Spawn message sent: {message}")
            
        except discord.Forbidden:
            logger.error("Bot does not have permission to send messages to the target channel")
        except discord.HTTPException as e:
            logger.error(f"Failed to send message due to HTTP error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Try to find the target channel in the new guild
        if not self.target_channel:
            await self.find_target_channel()
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        logger.error(f"Command error: {error}")
        
        try:
            await ctx.send(f"An error occurred: {str(error)}")
        except Exception:
            pass  # Ignore if we can't send error message
    
    async def close(self):
        """Clean up when the bot is shutting down."""
        logger.info("Shutting down bot...")
        
        # Stop the scheduler
        if self.spawn_scheduler:
            await self.spawn_scheduler.stop()
        
        # Close the bot connection
        await super().close()
        logger.info("Bot shutdown complete")

    # Add status command to the bot class
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Check the status of spawn schedules."""
        try:
            if not self.spawn_scheduler:
                await ctx.send("Scheduler not initialized.")
                return
            
            status = self.spawn_scheduler.get_status()
            
            embed = discord.Embed(
                title="🔍 Spawn Scheduler Status",
                color=0x0099ff
            )
            
            embed.add_field(
                name="Status",
                value="🟢 Running" if status.get("running", False) else "🔴 Stopped",
                inline=True
            )
            
            embed.add_field(
                name="Active Jobs",
                value=str(status.get("job_count", 0)),
                inline=True
            )
            
            if status.get("jobs"):
                job_info = "\n".join([
                    f"• {job['name']}" for job in status["jobs"]
                ])
                embed.add_field(
                    name="Scheduled Jobs",
                    value=job_info,
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await ctx.send(f"Error getting status: {str(e)}")
