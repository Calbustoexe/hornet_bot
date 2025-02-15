import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_warns = {}

    @app_commands.command(name="clear", description="Hornet chasse l'écho des voix passées...")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        """Hornet efface un nombre défini de messages, laissant place au silence."""
        if amount < 1:
            await interaction.response.send_message("*Futile. On ne peut chasser ce qui n'existe pas.*", ephemeral=True)
            return

        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🕸️ *{len(deleted)} échos du passé ont été tranchés.*", ephemeral=True, delete_after=5)

    @commands.hybrid_command(name="ban", description="Exile un membre du royaume.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Aucune raison spécifiée."):
        """Bannit un membre et lui envoie un message d'exil."""
        embed_mp = discord.Embed(
            title="Bannissement du Royaume",
            description=f"Vous avez été banni de **{ctx.guild.name}**.\n\n**Raison :** {reason}",
            color=0x7D0000
        )
        embed_mp.set_footer(text="Votre écho s'efface du royaume...")

        try:
            await member.send(embed=embed_mp)
        except discord.Forbidden:
            pass

        await member.ban(reason=reason)

        embed_serveur = discord.Embed(
            title="Bannissement effectué",
            description=f"**{member.mention}** a été banni.\n\n**Raison :** {reason}",
            color=0x4b4f74
        )
        await ctx.send(embed=embed_serveur)

    @app_commands.command(name="warn", description="Infliger un rappel du Code de la Ruche à un voyageur égaré.")
    async def warn(self, interaction: discord.Interaction, membre: discord.Member, message: str):
        """Ajoute un avertissement à un membre avec une ambiance Hollow Knight."""
        if membre.id not in self.db_warns:
            self.db_warns[membre.id] = []

        self.db_warns[membre.id].append({
            "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message
        })

        embed = discord.Embed(title="Parole de la Protectrice (Avertissement.)", color=discord.Color.red())
        embed.add_field(name="Mot de la Veilleuse", value=message, inline=False)
        embed.set_footer(text=f"Prononcé par {interaction.user.display_name}, Gardien(ne) du Nid")
        
        try:
            await membre.send(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("Les ombres ne portent pas toujours les messages. Impossible d'envoyer un DM.", ephemeral=True)
            return
        
        await interaction.response.send_message(f"{membre.mention} a été rappelé(e) à l'ordre par la Protectrice !", ephemeral=True)

    @app_commands.command(name="warn_liste", description="Consulter les rappels faits à un voyageur.")
    async def warn_liste(self, interaction: discord.Interaction, membre: discord.Member):
        """Affiche la liste des avertissements d'un membre dans l'ambiance Hollow Knight."""
        warns = self.db_warns.get(membre.id, [])
        
        if not warns:
            await interaction.response.send_message(f"{membre.mention} est encore vierge de tout rappel du Code de la Ruche.", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"📜 Parchemins des Fautes de {membre.display_name}", color=discord.Color.orange())
        embed.description = f"**{len(warns)} rappel(s) des Anciens.**\n\n"
        
        for i, warn in enumerate(warns, 1):
            embed.add_field(name=f"Marque {i}", value=f"**Date** : {warn['date']}\n**Message** : {warn['message']}", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @commands.hybrid_command(name="mute", description="Scelle la voix d'un membre dans les ombres.")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int, *, reason: str = "Aucune raison précisée."):
        """Mute un membre pendant une durée définie en minutes et lui envoie un MP."""
        duration_seconds = duration * 60  # Conversion en secondes

        # Création de l'embed MP
        embed_mp = discord.Embed(
            title="Vous avez été réduit au silence...",
            description=f"Dans le royaume de **{ctx.guild.name}**, votre voix a été scellée pour **{duration} minutes**.\n\n"
                        f"**Raison :** {reason}",
            color=0x2E2E2E  # Noir sombre
        )
        embed_mp.set_footer(text="Attendez que l'écho du temps vous libère...")

        # Tentative d'envoi en MP
        try:
            await member.send(embed=embed_mp)
        except discord.Forbidden:
            pass  # Impossible d'envoyer le MP

        # Application du mute
        await member.timeout(duration=discord.utils.utcnow() + discord.timedelta(seconds=duration_seconds), reason=reason)

        # Message dans le serveur
        embed = discord.Embed(
            title="Silence imposé",
            description=f"**{member.mention}** a été réduit au silence pour **{duration} minutes**.\n\n**Raison :** {reason}",
            color=0x4b4f74
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unmute", description="Brise le sceau du silence d'un membre.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Dé-mute un membre."""
        await member.timeout(duration=None)

        embed = discord.Embed(
            title="Silence brisé",
            description=f"**{member.mention}** peut à nouveau faire entendre sa voix.",
            color=0x4b4f74
        )
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="kick", description="Rejette une âme du royaume sans l'exiler à jamais.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Aucune raison spécifiée."):
        """Expulse un membre du serveur sans bannissement définitif."""
        embed_mp = discord.Embed(
            title="Expulsion du Royaume",
            description=f"Vous avez été expulsé de **{ctx.guild.name}**.\n\n**Raison :** {reason}",
            color=0xCC5500  # Orange sombre
        )
        embed_mp.set_footer(text="Les portes du royaume vous sont fermées... pour l'instant.")

        try:
            await member.send(embed=embed_mp)
        except discord.Forbidden:
            pass  # MP impossible à envoyer

        await member.kick(reason=reason)

        embed_serveur = discord.Embed(
            title="Expulsion effectuée",
            description=f"**{member.mention}** a été rejeté du royaume.\n\n**Raison :** {reason}",
            color=0x4b4f74
        )
        await ctx.send(embed=embed_serveur)

    # Commande slash /infos
    @app_commands.command(name="infos_user", description="Obtiens des informations sur un membre du royaume.")
    async def infos(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user  # Si aucun membre n'est spécifié, utilise l'auteur de la commande

        # Création de l'embed avec une ambiance semi-RP
        embed = discord.Embed(
            title=f"Les Mystères de {member.display_name}",
            description="Les secrets du royaume se révèlent à ceux qui osent explorer.",
            color=discord.Color.blurple()  # Couleur neutre mais royale
        )
        
        # Ajout des informations à l'embed
        embed.add_field(name="Nom de l'explorateur", value=member.display_name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Rôle le plus élevé", value=member.top_role.mention, inline=True)
        embed.add_field(name="Venu dans le royaume le", value=member.joined_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="Premier souffle dans ce monde le", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        
        # Ajout de l'avatar de l'utilisateur
        embed.set_thumbnail(url=member.avatar.url)

        # Message de l'embed
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))