import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import ButtonStyle, Interaction

class Annonce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="annonce_all", description="Hornet murmure aux âmes perdues...")
    @commands.has_permissions(administrator=True)
    async def message_tous(self, ctx, title: str, content: str, footer: str, color: str = "#4b4f74"):
        """Envoie un message à toutes les âmes errantes du royaume."""
        embed = self.creer_embed(title, content, footer, color)
        buttons = self.creer_boutons(ctx, embed)

        preview_msg = await ctx.send(
            embed=embed,
            content="**Échos du Néant... Validez-vous ce message ?**",
            view=buttons,
            ephemeral=True
        )
        buttons.preview_msg = preview_msg
        buttons.embed = embed

    def creer_embed(self, title: str, content: str, footer: str, color: str):
        try:
            embed_color = int(color.strip("#"), 16)
        except ValueError:
            embed_color = 0x4b4f74  # Teinte ténébreuse par défaut
        embed = discord.Embed(title=title, description=content, color=embed_color)
        embed.set_footer(text=footer)
        return embed

    def creer_boutons(self, ctx, embed):
        buttons = View(timeout=300)
        bouton_confirmer = Button(label="Graver dans le Néant", style=ButtonStyle.green)
        bouton_annuler = Button(label="Dissiper l'Écho", style=ButtonStyle.red)

        async def callback_confirmer(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ *Un combat qui n'est pas le vôtre...*", ephemeral=True)
                return
            await self.envoyer_a_tous_les_membres(ctx.guild, embed)
            
            await interaction.response.edit_message(content="*Les paroles résonnent désormais dans le Vide...*", view=None)

        async def callback_annuler(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ *L'acier ne vacille pas sous une autre main...*", ephemeral=True)
                return
            await interaction.response.edit_message(content="🕸️ *L'écho s'est dissipé dans l'oubli...*", view=None)

        bouton_confirmer.callback = callback_confirmer
        bouton_annuler.callback = callback_annuler
        buttons.add_item(bouton_confirmer)
        buttons.add_item(bouton_annuler)
        return buttons

    async def envoyer_a_tous_les_membres(self, guild, embed):
        """Envoie l'Annonce à toutes les âmes errantes du serveur."""
        for member in guild.members:
            if not member.bot:
                try:
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass  # Impossible d'envoyer, l'ombre refuse

async def setup(bot):
    await bot.add_cog(Annonce(bot))