import discord
from discord.ext import commands
from discord import Embed

class Accueil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Accueille le nouveau membre avec un message mystique."""
        # Salon d'accueil (à modifier si nécessaire)
        welcome_channel = discord.utils.get(member.guild.text_channels, name="accueil")
        
        if welcome_channel:
            # Message d'accueil personnalisé
            embed = Embed(
                title="Bienvenue à Hollownest...",
                description=f"Bienvenue, {member.mention}. Votre voyage commence ici, dans l'ombre de la Caverne... Essayez de survivre, les ombres vous souhaient un bon moment dans notre demeur.",
                color=0x4b4f74  # Une couleur sombre pour le thème
            )
            embed.set_footer(text="L'écho des âmes perdues vous guidera.")
            
            # Envoi du message d'accueil
            await welcome_channel.send(embed=embed)
        else:
            print("Le salon `accueil` n'est pas trouvé.")  # Si le salon n'existe pas

async def setup(bot):
    await bot.add_cog(Accueil(bot))