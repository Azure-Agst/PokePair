import discord
from discord.ext import commands
from plugins.db import DB_Plugin


class Roles(DB_Plugin):
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Checks if reaction message is in channel. If not, makes it.
        """
        history = await self.bot.channels['roles'].history(limit=5).flatten()
        if len(history) < 1:
            # make embed and send
            embed = discord.Embed(
                title="Server Roles",
                description="React to this message to get roles!",
                color=discord.Color.blue()
            )
            embed.set_footer(text="PokePair", icon_url="https://cdn.discordapp.com/avatars/645769421486424103/77b0befead90b9ec147304f312514f21.png?size=256")
            embed.add_field(name="Game:", value="- Sword\n- Shield")
            embed.add_field(name="Professions:", value="- Pokemon Breeder\n- Shiny Hunter\n- Pokedex Completionist")

            self.main_message = await self.bot.channels['roles'].send(embed=embed)
        else:
            self.main_message = history[0]

        if len(self.main_message.reactions) != 1:
            # Add all the reaction
            await history[0].clear_reactions()
            await self.main_message.add_reaction(discord.utils.get(self.bot.guild.emojis, name="pokemon_egg"))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print(f"{user.display_name} reacted with {reaction.emoji.name}")
        if user.bot:
            return
        elif reaction.message.id == self.main_message.id:
            try:
                if reaction.emoji.name == "pokemon_egg":
                    await user.add_roles(discord.utils.get(self.bot.guild.roles, name="Pokemon Breeder"))
            except discord.HTTPException:
                print("Add role went wrong")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print(f"{user.display_name} undid reaction {reaction.emoji.name}")
        if user.bot:
            return
        elif reaction.message.id == self.main_message.id:
            try:
                if reaction.emoji.name == "pokemon_egg":
                    await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name="Pokemon Breeder"))
            except discord.HTTPException:
                print("Remove role went wrong")


def setup(bot):
    bot.add_cog(Roles(bot))
