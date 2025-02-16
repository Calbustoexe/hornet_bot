import discord
from discord.ext import commands
import discord.app_commands
import datetime

class Utilitaire(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # COMMANDES -----------------------------------------------------
    @discord.app_commands.command(
        name="parler",
        description="Laisse-moi murmurer tes paroles aux Royaumes oubliés."
    )
    @discord.app_commands.describe(
        salon="Le sanctuaire où les mots seront gravés.",
        message="Le message à transmettre aux âmes errantes."
    )
    @discord.app_commands.checks.has_permissions(manage_messages=True)
    async def parler(self, interaction: discord.Interaction, message: str, salon: discord.TextChannel = None):
        salon = salon or interaction.channel

        try:
            await salon.send(message)
            await interaction.response.send_message(
                f"☀️ Les vents ont porté ton message vers {salon.mention} : \"{message}\"",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"⚔️ Les ombres me retiennent... Je ne peux pas parler dans {salon.mention}.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Une brèche s'est ouverte dans le Néant : {e}", ephemeral=True)

    @discord.app_commands.command(
        name="activité",
        description="Écoute les échos des pas laissés dans le Royaume."
    )
    @discord.app_commands.describe(
        membre="L'âme dont tu veux sonder la trace."
    )
    async def activite(self, interaction: discord.Interaction, membre: discord.Member = None):
        if membre is None:
            membre = interaction.user

        # Récupération sécurisée des messages envoyés
        messages_count = 0
        for channel in interaction.guild.text_channels:
            try:
                async for message in channel.history(limit=None):
                    if message.author == membre:
                        messages_count += 1
            except (discord.Forbidden, discord.HTTPException):
                continue  # Ignore les salons inaccessibles

        # Gestion du temps passé en vocal
        if membre.voice and membre.voice.channel:
            total_vocal_time = "Actuellement dans le Royaume des Murmures."
        else:
            total_vocal_time = "Les ténèbres sont silencieuses..."

        # Gestion du fuseau horaire pour éviter l'erreur d'offset-naive et offset-aware
        joined_at = membre.joined_at
        if joined_at is not None:
            if joined_at.tzinfo is None:
                joined_at = joined_at.replace(tzinfo=datetime.timezone.utc)

            now = datetime.datetime.now(datetime.timezone.utc)
            days_active = (now - joined_at).days or 1
        else:
            days_active = 1  # Valeur par défaut si l'info est indisponible

        # Fréquence d'activité (évite division par zéro)
        avg_messages_per_day = messages_count / days_active if days_active > 0 else 0

        # Création de l'embed avec un style Hollow Knight
        embed = discord.Embed(
            title=f"Vestiges d'Errance - {membre.display_name}",
            description="Les échos de ton périple résonnent dans l'obscurité...",
            color=discord.Color.dark_blue()
        )
        embed.set_thumbnail(url=membre.display_avatar.url)
        embed.add_field(name="🌀 Murmures gravés", value=f"**{messages_count}** messages envoyés dans le Néant.", inline=False)
        embed.add_field(name="🔊 Chuchotements des ombres", value=total_vocal_time, inline=False)
        embed.add_field(name="📜 Fréquence d'apparition", value=f"**{avg_messages_per_day:.2f}** messages par cycle lunaire.", inline=False)
        embed.set_footer(text="Les Royaumes se souviennent toujours de ceux qui osent y marcher...")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilitaire(bot))