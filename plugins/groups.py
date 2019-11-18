import discord
from discord.ext import commands
from plugins.db import DB_Plugin

class Groups(DB_Plugin):
    @commands.command()
    async def group(self, ctx, cmd, *, arg):    
        if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("We currently don't support making groups in DMs. Hop into a server and try again!")
        else:

            # handle raid creation
            if cmd == "create":
                await ctx.send("Creating raid group \"{}\"! Check your DMs for more info!".format(arg))

                # make group in database
                result = await self.db_create_group(ctx, arg)

                # make embed
                embed = discord.Embed(
                    title = "PokePair - {}".format(result['name']),
                    description = "Made at: {}".format(result['timestamp']),
                    color = discord.Color.blue()
                )
                embed.set_footer(text="PokePair", icon_url="https://cdn.discordapp.com/avatars/645769421486424103/77b0befead90b9ec147304f312514f21.png?size=256")
                embed.add_field(name="Code:", value=result['code'])
                embed.add_field(name="Members:", value="• {}\n• {}\n• {}\n• {}".format(result['members'][0]['name'],"N/A","N/A","N/A"))
                await ctx.author.send(embed=embed)
                await ctx.author.send("We made a channel for you in {} for you to pair up with other people!".format(ctx.guild))

            elif cmd == "wow":
                await ctx.send("Amazing!")

            else:
                await ctx.send("Command {} not found! Check your syntax and try again!".format(cmd))

    @group.error
    async def group_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Seems a few arguments are missing! Check your syntax and try again!')

def setup(bot):
    bot.add_cog(Groups(bot))