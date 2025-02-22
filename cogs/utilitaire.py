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


    @commands.hybrid_command(name="mp", with_app_command=True, description="Envoie un message privé à un utilisateur.")
    async def mp(self, ctx: commands.Context, user: discord.User, *, message: str):
        """Commande hybride pour envoyer un message privé."""
        try:
            await user.send(message)
            
            embed = discord.Embed(
                title="📩 Message envoyé",
                description=f"**'{message}'**\n\n a été envoyé à {user.mention} avec succès.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Échec de l'envoi",
                description=f"Impossible d'envoyer un MP à {user.mention}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


    @commands.hybrid_command(name="mp_embed", with_app_command=True, description="Envoie un message privé sous forme d'embed à un utilisateur avec confirmation.")
    async def mp_embed(
        self, ctx: commands.Context, user: discord.User,
        titre: str, corps: str, 
        contenu: str = None, footer: str = None, couleur: str = None
    ):
        """Commande hybride pour envoyer un MP sous forme d'embed avec confirmation."""

        # Vérification des arguments obligatoires (pour le préfixe uniquement)
        if not titre or not corps:
            if isinstance(ctx, commands.Context):  # Si c'est une commande avec préfixe
                await ctx.send("❌ **Titre et Corps sont obligatoires !**", delete_after=5)
            return

        # Définition de la couleur
        try:
            color = discord.Color(int(couleur, 16)) if couleur else discord.Color.dark_gray()
        except ValueError:
            color = discord.Color.dark_gray()

        # Création de l'embed du message
        embed_mp = discord.Embed(title=titre, description=contenu, color=color)
        embed_mp.add_field(name="Message :", value=corps, inline=False)

        if footer:
            embed_mp.set_footer(text=footer)

        embed_mp.set_author(name=f"Envoyé par {ctx.author}", icon_url=ctx.author.display_avatar.url)

        # Embed de confirmation
        embed_confirm = discord.Embed(
            title="🔔 Confirmation requise",
            description=f"Tu es sur le point d'envoyer cet embed à {user.mention}.\n\n✅ **Confirmer** ou ❌ **Annuler**.",
            color=discord.Color.orange()
        )
        embed_confirm.add_field(name="Titre", value=titre, inline=False)
        embed_confirm.add_field(name="Corps", value=corps, inline=False)
        embed_confirm.set_footer(text="Clique sur un bouton ci-dessous.")

        # Boutons de confirmation
        class Confirm(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.success)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("❌ **Tu ne peux pas interagir avec ce message.**", ephemeral=True)

                try:
                    await user.send(embed=embed_mp)
                    await interaction.response.edit_message(
                        embed=discord.Embed(title="✅ Message envoyé", description=f"L'embed a bien été envoyé à {user.mention}.", color=discord.Color.green()),
                        view=None
                    )
                except discord.Forbidden:
                    await interaction.response.edit_message(
                        embed=discord.Embed(title="❌ Échec de l'envoi", description=f"Impossible d'envoyer un MP à {user.mention}.", color=discord.Color.red()),
                        view=None
                    )

            @discord.ui.button(label="Annuler", style=discord.ButtonStyle.danger)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("❌ **Tu ne peux pas interagir avec ce message.**", ephemeral=True)

                await interaction.response.edit_message(
                    embed=discord.Embed(title="❌ Annulé", description="L'envoi du message a été annulé.", color=discord.Color.red()),
                    view=None
                )

        # Envoi du message de confirmation
        await ctx.send(embed=embed_confirm, view=Confirm())

async def setup(bot):
    await bot.add_cog(Utilitaire(bot))