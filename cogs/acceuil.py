import discord
from discord.ext import commands
from discord import Embed

class Accueil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = None  # On garde l'ID du salon d'accueil

    @commands.command(name="acceuil")
    @commands.has_permissions(administrator=True)
    async def set_accueil(self, ctx, channel_id: int):
        """Permet à un administrateur de définir un salon d'accueil."""
        self.welcome_channel_id = channel_id
        await ctx.send(f"Salon d'accueil défini avec succès! ID: {channel_id}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Accueille le nouveau membre avec un message mystique."""
        # Vérifie si un salon d'accueil est défini
        if self.welcome_channel_id is None:
            await member.guild.system_channel.send("Aucun salon d'accueil défini.")
            return
        
        welcome_channel = member.guild.get_channel(self.welcome_channel_id)
        
        if welcome_channel:
            # Message d'accueil personnalisé
            embed = Embed(
                title="Bienvenue à Hollownest...",
                description=f"Bienvenue, {member.mention}. Votre voyage commence ici, dans l'ombre de la Caverne... Essayez de survivre, les ombres vous souhaitent un bon moment dans notre demeure.",
                color=0x4b4f74  # Une couleur sombre pour le thème
            )
            embed.set_footer(text="L'écho des âmes perdues vous guidera.")
            
            # Envoi du message d'accueil
            await welcome_channel.send(embed=embed)
        else:
            print("Le salon d'accueil n'est pas trouvé.")  # Si le salon n'existe pas

async def setup(bot):
    await bot.add_cog(Accueil(bot))