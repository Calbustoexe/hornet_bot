import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import ButtonStyle, Interaction

class Announcement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="annonce_all", description="Hornet murmure aux âmes perdues...")
    @commands.has_permissions(administrator=True)
    async def message_all(self, ctx, title: str, content: str, footer: str, color: str = "#4b4f74"):
        """Envoie un message à tous les âmes errantes du royaume."""
        embed = self.create_embed(title, content, footer, color)
        buttons = self.create_buttons(ctx, embed)

        preview_msg = await ctx.send(
            embed=embed,
            content="**Échos du Néant... Validez-vous ce message ?**",
            view=buttons,
            ephemeral=True
        )
        buttons.preview_msg = preview_msg
        buttons.embed = embed

    def create_embed(self, title: str, content: str, footer: str, color: str):
        try:
            embed_color = int(color.strip("#"), 16)
        except ValueError:
            embed_color = 0x4b4f74  # Teinte ténébreuse par défaut
        embed = discord.Embed(title=title, description=content, color=embed_color)
        embed.set_footer(text=footer)
        return embed

    def create_buttons(self, ctx, embed):
        buttons = View(timeout=300)
        confirm_button = Button(label="Graver dans le Néant", style=ButtonStyle.green)
        cancel_button = Button(label="Dissiper l'Écho", style=ButtonStyle.red)

        async def confirm_callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ *Un combat qui n'est pas le vôtre...*", ephemeral=True)
                return
            await self.send_to_all_members(ctx.guild, embed)
            
            await interaction.response.edit_message(content="*Les paroles résonnent désormais dans le Vide...*", view=None)

        async def cancel_callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ *L'acier ne vacille pas sous une autre main...*", ephemeral=True)
                return
            await interaction.response.edit_message(content="🕸️ *L'écho s'est dissipé dans l'oubli...*", view=None)

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        buttons.add_item(confirm_button)
        buttons.add_item(cancel_button)
        return buttons

    async def send_to_all_members(self, guild, embed):
        """Envoie l'Annonce à tous les âmes errantes du serveur."""
        for member in guild.members:
            if not member.bot:
                try:
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass  # Impossible d'envoyer, l'ombre refuse

async def setup(bot):
    await bot.add_cog(Announcement(bot))