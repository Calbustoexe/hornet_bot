import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.concours = {}
    
    @app_commands.command(name="lancer_concours", description="Lance un concours mystique pour offrir une récompense.")
    async def lancer_concours(self, interaction: discord.Interaction, duree: int, gagnants: int, *, recompense: str):
        """Crée un concours avec une durée en secondes, un nombre de gagnants et une récompense."""
        embed = discord.Embed(
            title="🎁 Un cadeau du royaume apparaît !",
            description=f"**Récompense :** {recompense}\n**Durée :** {duree} secondes\n**Gagnants :** {gagnants}\n\nClique sur le bouton ci-dessous pour entrer dans la sélection du destin...",
            color=discord.Color.gold()
        )
        embed.set_footer(text="La Protectrice veille sur ce concours.")

        vue = VueConcours(self, interaction.channel.id, gagnants, recompense)
        message = await interaction.response.send_message(embed=embed, view=vue)
        self.concours[message.id] = vue
        await vue.demarrer(duree)
    
    @app_commands.command(name="annuler_concours", description="Annule un concours avant qu'il ne soit réclamé.")
    async def annuler_concours(self, interaction: discord.Interaction, message_id: int):
        """Annule un concours en cours."""
        if message_id in self.concours:
            await self.concours[message_id].annuler()
            await interaction.response.send_message("Le concours a été dissipé...", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun concours actif avec cet ID.", ephemeral=True)

    @app_commands.command(name="terminer_concours", description="Termine un concours et sélectionne les élus.")
    async def terminer_concours(self, interaction: discord.Interaction, message_id: int):
        """Force la fin d'un concours."""
        if message_id in self.concours:
            await self.concours[message_id].terminer()
            await interaction.response.send_message("Le concours a été scellé et les élus désignés.", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun concours actif avec cet ID.", ephemeral=True)

    @app_commands.command(name="relancer_concours", description="Relance le tirage pour un concours déjà scellé.")
    async def relancer_concours(self, interaction: discord.Interaction, message_id: int):
        """Relance un tirage pour un concours terminé."""
        if message_id in self.concours:
            await self.concours[message_id].relancer()
            await interaction.response.send_message("Le destin a été réécrit...", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun concours trouvé avec cet ID.", ephemeral=True)

class VueConcours(discord.ui.View):
    def __init__(self, cog, channel_id, gagnants, recompense):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel_id = channel_id
        self.gagnants = gagnants
        self.recompense = recompense
        self.participants = []
        self.message = None

    @discord.ui.button(label="Participer", style=discord.ButtonStyle.green)
    async def participer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.participants:
            self.participants.append(interaction.user.id)
            await interaction.response.send_message("Votre nom est inscrit dans le parchemin du destin...", ephemeral=True)
        else:
            await interaction.response.send_message("Vous avez déjà répondu à l'appel du destin.", ephemeral=True)
    
    async def demarrer(self, duree):
        await asyncio.sleep(duree)
        await self.terminer()

    async def terminer(self):
        if not self.participants:
            texte_resultat = "Personne ne s'est aventuré à réclamer ce don..."
        else:
            choisis = random.sample(self.participants, min(len(self.participants), self.gagnants))
            texte_resultat = "**Les élus du destin sont :**\n" + "\n".join(f"<@{user}>" for user in choisis)
        
        embed = discord.Embed(
            title="🎉 Le concours a été scellé !",
            description=f"Récompense : {self.recompense}\n\n{texte_resultat}",
            color=discord.Color.green()
        )
        channel = self.cog.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(embed=embed)
        self.cog.concours.pop(self.message.id, None)

    async def annuler(self):
        embed = discord.Embed(
            title="🚫 Le concours a été dissipé...",
            description="Aucun élu ne recevra ce présent.",
            color=discord.Color.red()
        )
        channel = self.cog.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(embed=embed)
        self.cog.concours.pop(self.message.id, None)

    async def relancer(self):
        await self.terminer()

async def setup(bot):
    await bot.add_cog(Giveaway(bot))