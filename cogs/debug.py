from discord.ext import commands
from ext.logcfg import logger


class Debug(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Debug(bot))
