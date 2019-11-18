import random
import discord
import secrets
from discord.ext import commands
from plugins.db import DB_Plugin
from datetime import datetime

class Groups(DB_Plugin):
    @commands.command()
    async def group(self, ctx, *, arg):    
        if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("We currently don't support making groups in DMs. Hop into our server and try again!")
        else:

            # group creation
            if arg.split(" ")[0] == "create":

                # generate important data
                name = ' '.join(arg.split()[1:])
                timestamp = datetime.now()
                group_id = secrets.token_hex(3) # I forsee conflicts in db but enough entropy ig so it's ok
                join_code = random.randrange(1000, 9999)

                # alert user
                await ctx.send("Creating raid group \"{}\"...".format(name))

                # make channel
                category = discord.utils.get(ctx.guild.categories, name="Your LFG Groups")
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    ctx.author: discord.PermissionOverwrite(read_messages=True, connect=True),
                    ctx.guild.me: discord.PermissionOverwrite(administrator=True, read_messages=True, connect=True)
                }
                text = await ctx.guild.create_text_channel(name+"-"+group_id, category=category, overwrites=overwrites)
                voice = await ctx.guild.create_voice_channel(name+" - "+group_id, category=category, overwrites=overwrites)

                # make embed and send
                embed = discord.Embed(
                    title = "PokePair - {}".format(name),
                    description = "Made at: {}".format(timestamp),
                    color = discord.Color.blue()
                )
                embed.set_footer(text="PokePair", icon_url="https://cdn.discordapp.com/avatars/645769421486424103/77b0befead90b9ec147304f312514f21.png?size=256")
                embed.add_field(name="Group ID:", value=group_id)
                embed.add_field(name="Code:", value=join_code)
                embed.add_field(name="Members:", value="• {}\n• {}\n• {}\n• {}".format(ctx.author.display_name,"N/A","N/A","N/A"))
                await text.send(f"Hey, {ctx.author.mention}, here's your group channel! We also made a voice channel for your members!")
                embed = await text.send(embed=embed)
                await text.send(f"Tell your friends to join by using `!group join {join_code}` in chat!")   

                # add records to the database
                result = await self.db_create_group(ctx, name, timestamp, group_id, join_code, text.id, voice.id, embed.id)
            # end group create 


            # Group Deletion
            elif arg.split(" ")[0] == "delete":
                group = await self.db_find_group_by_chat(ctx.channel.id)
                if not group:
                    await ctx.send("You're not in a group channel! Make sure you use this command in a group channel and that you're currently the group leader to proceed.")
                    return

                if group['members'][0] != ctx.author.id:
                    await ctx.send("You're not the group leader! Make sure you're the group leader to use this command.")
                    return

                if len(arg.split(" ")) > 1 and arg.split(" ")[1] == "confirm":
                    # delete channels
                    await self.bot.get_channel(group['text']).delete(reason="Group was deleted by its leader.")
                    await self.bot.get_channel(group['voice']).delete(reason="Group was deleted by its leader.")

                    # delete database entry
                    await self.db_delete_group(group['group-id'])
                else:
                    await ctx.send("Are you absolutely sure you want to delete this group? Use `!group delete confirm` to confirm your request.")
            # end group delete 


            # TODO: Group Join
            # TODO: Group Leave

            # TODO: Update Embed


            else:
                await ctx.send("Command {} not found! Check your syntax and try again!".format(arg.split(" ")[0]))

    @group.error
    async def group_error(self, ctx, error):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("We currently don't support making groups in DMs. Hop into our server and try again!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Seems a few arguments are missing! Check your syntax and try again!')

def setup(bot):
    bot.add_cog(Groups(bot))