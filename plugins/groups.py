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
                await ctx.send("Creating raid group \"{}\"...".format(arg))

                # make group in database
                result = await self.db_create_group(ctx, arg)

                # make channel
                category = discord.utils.get(ctx.guild.categories, name="Your LFG Groups")
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    ctx.author: discord.PermissionOverwrite(read_messages=True, connect=True),
                    ctx.guild.me: discord.PermissionOverwrite(administrator=True, read_messages=True, connect=True)
                }
                text_channel = await ctx.guild.create_text_channel(arg, category=category, overwrites=overwrites)
                voice_channel = await ctx.guild.create_voice_channel(arg, category=category, overwrites=overwrites)

                # make embed and send
                embed = discord.Embed(
                    title = "PokePair - {}".format(result['name']),
                    description = "Made at: {}".format(result['timestamp']),
                    color = discord.Color.blue()
                )
                embed.set_footer(text="PokePair", icon_url="https://cdn.discordapp.com/avatars/645769421486424103/77b0befead90b9ec147304f312514f21.png?size=256")
                embed.add_field(name="Group ID:", value=result['group-id'])
                embed.add_field(name="Code:", value=result['code'])
                embed.add_field(name="Members:", value="• {}\n• {}\n• {}\n• {}".format(result['members'][0]['name'],"N/A","N/A","N/A"))
                await text_channel.send(f"Hey, {ctx.author.mention}, here's your group channel! We also made a voice channel for your members!")
                await text_channel.send(embed=embed)

            else:
                await ctx.send("Command {} not found! Check your syntax and try again!".format(cmd))

    @group.error
    async def group_error(self, ctx, error):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("We currently don't support making groups in DMs. Hop into our server and try again!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Seems a few arguments are missing! Check your syntax and try again!')

def setup(bot):
    bot.add_cog(Groups(bot))