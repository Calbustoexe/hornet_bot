import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import re

def convertir_duree(texte_duree: str) -> int:
    """Convertit une durée sous forme '2j 5h 30m' en secondes."""
    regex = re.findall(r'(\d+)([jhm])', texte_duree)
    total_secondes = 0
    multiplicateurs = {'j': 86400, 'h': 3600, 'm': 60}
    
    for valeur, unite in regex:
        total_secondes += int(valeur) * multiplicateurs[unite]
    
    return total_secondes

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.concours = {}
    
    @app_commands.command(name="lancer_concours", description="Lance un concours mystique pour offrir une récompense.")
    async def lancer_concours(self, interaction: discord.Interaction, duree: str, gagnants: int, *, recompense: str):
        duree_secondes = convertir_duree(duree)
        
        if duree_secondes <= 0:
            await interaction.response.send_message("Durée invalide. Utilise le format '2j 5h 30m'", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎁 Un cadeau du royaume apparaît !",
            description=f"**Récompense :** {recompense}\n**Durée :** {duree}\n**Gagnants :** {gagnants}\n**Participants :** 0\n\nClique sur le bouton ci-dessous pour entrer dans la sélection du destin...",
            color=discord.Color.gold()
        )
        embed.set_footer(text="La Protectrice veille sur ce concours.")

        vue = VueConcours(self, interaction.channel.id, gagnants, recompense)
        message = await interaction.channel.send(embed=embed, view=vue)
        self.concours[message.id] = vue
        await interaction.response.send_message("Le concours a été lancé avec succès !", ephemeral=True)
        await vue.demarrer(duree_secondes, message)
    
    @app_commands.command(name="annuler_concours", description="Annule un concours avant qu'il ne soit réclamé.")
    async def annuler_concours(self, interaction: discord.Interaction, message_id: int):
        if message_id in self.concours:
            await self.concours[message_id].annuler()
            await interaction.response.send_message("Le concours a été dissipé...", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun concours actif avec cet ID.", ephemeral=True)

    @app_commands.command(name="terminer_concours", description="Termine un concours et sélectionne les élus.")
    async def terminer_concours(self, interaction: discord.Interaction, message_id: int):
        if message_id in self.concours:
            await self.concours[message_id].terminer()
            await interaction.response.send_message("Le concours a été scellé et les élus désignés.", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun concours actif avec cet ID.", ephemeral=True)

    @app_commands.command(name="relancer_concours", description="Relance un tirage pour désigner de nouveaux élus.")
    async def relancer_concours(self, interaction: discord.Interaction, message_id: int):
        if message_id in self.concours:
            await self.concours[message_id].terminer(reroll=True)
            await interaction.response.send_message("Un nouveau tirage a été effectué !", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun concours actif avec cet ID.", ephemeral=True)

class VueConcours(discord.ui.View):
    def __init__(self, cog, channel_id, gagnants, recompense):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel_id = channel_id
        self.gagnants = gagnants
        self.recompense = recompense
        self.participants = []

    @discord.ui.button(label="Participer", style=discord.ButtonStyle.green)
    async def participer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.participants:
            self.participants.append(interaction.user.id)
            await interaction.response.send_message("Votre nom est inscrit dans le parchemin du destin...", ephemeral=True)
            await self.mettre_a_jour_participants(interaction.message)
        else:
            await interaction.response.send_message("Vous avez déjà répondu à l'appel du destin.", ephemeral=True)
    
    async def mettre_a_jour_participants(self, message):
        embed = message.embeds[0]
        embed.set_field_at(0, name="Participants", value=str(len(self.participants)), inline=False)
        await message.edit(embed=embed, view=self)
    
    async def demarrer(self, duree, message):
        await asyncio.sleep(duree)
        await self.terminer()
    
    async def terminer(self, reroll=False):
        if not self.participants:
            texte_resultat = "Personne ne s'est aventuré à réclamer ce don..."
        else:
            choisis = random.sample(self.participants, min(len(self.participants), self.gagnants))
            texte_resultat = "**Les élus du destin sont :**\n" + "\n".join(f"<@{user}>" for user in choisis)
        
        embed = discord.Embed(
            title="🎉 Le concours a été scellé !" if not reroll else "🔄 Nouveau tirage effectué !",
            description=f"Récompense : {self.recompense}\n\n{texte_resultat}",
            color=discord.Color.green()
        )
        channel = self.cog.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))