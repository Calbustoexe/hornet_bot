import discord
from discord.ext import commands

class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_activity = discord.Streaming(name="Cornifère", url="https://www.twitch.tv/hornet_hk")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=self.default_activity)

    @commands.command(name="activité", help="Définir l'activité du bot Hornet.")
    async def activité(self, ctx, *, activité: str):
        # Définir l'activité du bot selon l'input
        activity = discord.Game(name=activité)

        # Appliquer cette activité à Discord
        await self.bot.change_presence(activity=activity)

        # Répondre à l'utilisateur
        await ctx.send(f"Hornet est maintenant **{activité}**.")

# Ajouter le cog au bot
async def setup(bot):
    await bot.add_cog(Activity(bot))