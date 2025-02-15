import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways = {}
    
    @app_commands.command(name="gcreate", description="Lance un appel du Nid pour un don mystique.")
    async def gcreate(self, interaction: discord.Interaction, duration: int, winners: int, *, prize: str):
        """Crée un giveaway avec une durée en secondes, un nombre de gagnants et une récompense."""
        embed = discord.Embed(
            title="🎁 Un cadeau du royaume apparaît !",
            description=f"**Récompense :** {prize}\n**Durée :** {duration} secondes\n**Gagnants :** {winners}\n\nClique sur le bouton ci-dessous pour entrer dans la sélection du destin...",
            color=discord.Color.gold()
        )
        embed.set_footer(text="La Protectrice veille sur ce concours.")

        view = GiveawayView(self, interaction.channel.id, winners, prize)
        message = await interaction.response.send_message(embed=embed, view=view)
        self.giveaways[message.id] = view
        await view.start(duration)
    
    @app_commands.command(name="gcancel", description="Dissipe un don avant qu'il ne soit réclamé.")
    async def gcancel(self, interaction: discord.Interaction, message_id: int):
        """Annule un giveaway en cours."""
        if message_id in self.giveaways:
            await self.giveaways[message_id].cancel()
            await interaction.response.send_message("Le don a été dissipé...", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun don actif avec cet ID.", ephemeral=True)

    @app_commands.command(name="gend", description="Termine un don et sélectionne les élus.")
    async def gend(self, interaction: discord.Interaction, message_id: int):
        """Force la fin d'un giveaway."""
        if message_id in self.giveaways:
            await self.giveaways[message_id].end()
            await interaction.response.send_message("Le don a été scellé et les élus désignés.", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun don actif avec cet ID.", ephemeral=True)

    @app_commands.command(name="greroll", description="Relance le destin pour un don déjà scellé.")
    async def greroll(self, interaction: discord.Interaction, message_id: int):
        """Relance un tirage pour un giveaway terminé."""
        if message_id in self.giveaways:
            await self.giveaways[message_id].reroll()
            await interaction.response.send_message("Le destin a été réécrit...", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun don trouvé avec cet ID.", ephemeral=True)

class GiveawayView(discord.ui.View):
    def __init__(self, cog, channel_id, winners, prize):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel_id = channel_id
        self.winners = winners
        self.prize = prize
        self.entries = []
        self.message = None

    @discord.ui.button(label="Participer", style=discord.ButtonStyle.green)
    async def participate(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.entries:
            self.entries.append(interaction.user.id)
            await interaction.response.send_message("Votre nom est inscrit dans le parchemin du destin...", ephemeral=True)
        else:
            await interaction.response.send_message("Vous avez déjà répondu à l'appel du destin.", ephemeral=True)
    
    async def start(self, duration):
        await asyncio.sleep(duration)
        await self.end()

    async def end(self):
        if not self.entries:
            result_text = "Personne ne s'est aventuré à réclamer ce don..."
        else:
            chosen = random.sample(self.entries, min(len(self.entries), self.winners))
            result_text = "**Les élus du destin sont :**\n" + "\n".join(f"<@{user}>" for user in chosen)
        
        embed = discord.Embed(
            title="🎉 Le don a été scellé !",
            description=f"Récompense : {self.prize}\n\n{result_text}",
            color=discord.Color.green()
        )
        channel = self.cog.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(embed=embed)
        self.cog.giveaways.pop(self.message.id, None)

    async def cancel(self):
        embed = discord.Embed(
            title="🚫 Le don a été dissipé...",
            description="Aucun élu ne recevra ce présent.",
            color=discord.Color.red()
        )
        channel = self.cog.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(embed=embed)
        self.cog.giveaways.pop(self.message.id, None)

    async def reroll(self):
        await self.end()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))