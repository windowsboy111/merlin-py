#!/bin/python3
# bot.py
from main_imports import *
_globals = globals()
_locals = locals()
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#token is stored inside ".env"
#console log
logger.info("Program started.")
logger.debug("Finished importing and logger configuration.  Loaded all libraries.")

# init
bot.remove_command('help')
logger.debug("Loaded env, custom exceptions, and \"constant\" variables / some global variables.")
MODE = os.getenv('MODE')
print(MODE)
# ---

@bot.event
async def on_message(message: discord.Message):
    global lastmsg,shell,_globals,_locals,stop
    if await easteregg.easter(message): return
    if type(message.channel) != discord.DMChannel and message.channel.name == 'python' and message.author != bot.user:
        p = threading.Thread(target=load_py,args=[message,shell,_globals,_locals])
        p.start()
        p.join(5)
        if p.is_alive():
            stop = True
            p.join()
            for i in range(3):  await message.author.send('No more fork bombs')
            shell['py_out'] = "Enough fork bomb."
        if len(shell['py_out']) > 1998:
            await message.channel.send(file=discord.File(open("samples/pyoutput.txt","r"),"output.txt"))
            stop=False
            return
        await message.channel.send(shell['py_out'])
        shell['py_out'] = ''
        stop=False
        return
    if message.content.startswith('/') and message.author != bot.user:
        isCmd = False
        for cmd in bot.commands:
            if message.content.lower().split(' ')[0] == '/'+cmd.name:
                isCmd=True
                break
            for alias in cmd.aliases:
                if message.content.lower().split(' ')[0] == '/'+alias:
                    isCmd=True
                    break
        if isCmd:
            msgtoSend = f'{message.author.name} has issued command: {message.content}'
            logger.info(msgtoSend)
            print(msgtoSend)
            await log(message.channel.mention + ' ' + msgtoSend)
            try:
                await bot.process_commands(message)
                try:    await message.delete()
                except: pass
                finally:return
            except discord.ext.commands.errors.CommandNotFound: return
            except Exception as e:
                await message.channel.send(f'{message.author.mention}, there was an error trying to execute that command! :(')
                print(str(e))
    if 'invite me' in message.content.lower():  await message.channel.send('RbBFAfK is the invite code for this server.\nhttps://discord.gg/RbBFAfK\n')
    if (message.author.bot): return
    if lastmsg == []:   lastmsg = [message.content.lower(),message.author,1,False]
    elif lastmsg[2] == 4 and message.content.lower() == lastmsg[0] and message.author == lastmsg[1] and lastmsg[3]:
        lastmsg[2]+=1
        await message.delete()
        ctx = await bot.get_context(message)
        await ctx.invoke(bot.get_command('warn'),person=lastmsg[1],reason='spamming')
    elif lastmsg[0] == message.content.lower() and lastmsg[1] == message.author:
        lastmsg[2]+=1
        if lastmsg[2] == 4: lastmsg[3]=True
    else:   lastmsg=[message.content.lower(),message.author,1,False]

@bot.event
async def on_ready():
    print(style.cyan(f'Logged in as {bot.user.name} - {bot.user.id}'))
    if not MODE or MODE=='NORMAL':
        activity = discord.Activity(type=discord.ActivityType(3),name=random.choice(statusLs))
        await bot.change_presence(status=discord.Status.online, activity=activity)
    elif MODE=='DEBUG':
        await bot.change_presence(status=discord.Status.idle)
        await log('RUNNING IN **DEBUG** MODE!')
    elif MODE=='FIX':
        await bot.change_presence(status=discord.Status.dnd)
        await log('*RUNNING IN EMERGENCY **FIX** MODE!')
    await log(f'logged in')
    for cog in cogs:
        bot.load_extension('cogs.' + cog)
    await log('loaded extensions / cogs')
    return

@bot.event
async def on_member_join(member):
    logger.info(f"Detected {member.name} joined, welcoming the member in dm...")
    await member.send(f'Hi {member.name}, welcome to KCCS Official Discord server!\nBy using the guild, you accept the rules.')
    print(f"{member} has joined the server.")

#####################################################################################################################################################################################

@bot.group(name='mc',help="Same as kccsofficial.exe mc <args>\nUsage: /mc srv hypixel",pass_context=True,aliases=['minecraft'])
async def mc(ctx):
   if ctx.invoked_subcommand is None:
        await ctx.send(f"2 bed idk wat u r toking 'bout, but wut?")
        return
@mc.command(name='srv',help='list servers',aliases=['server'])
async def srv(ctx,*,args:str=None):
    global embed
    global rtc
    embed = discord.Embed(title='Spinning \'round...',description='Gift me a sec')
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(bot.get_emoji(687495401661661324))
    rtc=0
    try:
        logger.info("Attempting to call botmc.mcsrv()")
        embed = botmc.mcsrv(embed,args)
    except botmc.InvalidArgument as e:
        rtrn = "Panic 2: InvalidArgument. Send gud args!!!!!!!?\n""Details:  " + str(e) + "\n"
        rtrn += "2 get da usage, includ da \"help\" args, i.e. `/mc help`\n"
        rtc = 2
    except botmc.OfflineServer as e:
        rtrn = "Panic 4: OfflineServer.  Details: {}\n2 get da usage, includ da \"help\" args, i.e. `/mc help`\n".format(str(e))
        rtc = 3
    except Exception as e:
        rtrn = "Panic 1: Unknun Era.  Program kthxbai.\nDetails:  " + str(e) + "\n"
        rtc = 1
    if rtc != 0:
        embed = discord.Embed(title="ERROR",description=str(rtrn),color=0xFF0000)
        if rtc == 1:
            logger.error("Exit code: " + str(rtc))
        else:
            logger.warn("Exit code: " + str(rtc))
    else:
        logger.info("Exit code: " + str(rtc))
    embed.set_footer(text="kthxbai code: {}.".format(rtc))
    await msg.edit(embed=embed)
    await msg.remove_reaction(bot.get_emoji(687495401661661324), bot.user)
@mc.command(name='addsrv', help='add a shortcut looking for a server', aliases=['asv'])
async def addsrv(ctx,link:str=None,name:str=None,note:str=None):
    if not link or not name or not note:
        return await ctx.send('Missing required arguments :/')
    with open('samples/mcsrvs.csv',mode='w') as csv_f:
        w = csv.writer(csv_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow([link,name,note])
        return await ctx.send('Operation completed successfully.')
@mc.command(name='kill',help='cmd /kill')
async def kill(ctx,*,member=None):
    try:
        if member=='@a' or member=='@e':
            a = ""
            for member in ctx.guild.members:
                a += f'{member.display_name} fell out of the world\n'
                a += f'Killed {member.display_name}\n'
                await ctx.send(a)
                a=""
            return
        if member=='@r':
            r = random.choice(ctx.guild.members).display_name
            await ctx.send(f'{r} fell out fo the world.\nKilled {r}')
            return
        if member == '@p' or member == '@s':
            await ctx.send(f'{ctx.message.author.display_name} fell out of the world.\nKilled {ctx.message.author.display_name}')
            return
        if member == None:
            await ctx.send(f'{ctx.message.author.display_name} fell out of the world.\nKilled {ctx.message.author.display_name}')
            return
        rs = ''
        for char in member:
            if char in ['0','1','2','3','4','5','6','7','8','9']:
                rs += char
        member = bot.get_user(int(rs))
        member = member or ctx.message.author
        await ctx.send(f'{member.display_name} fell out of the world.\nKilled {member.display_name}')
        return
    except Exception as e:
        await ctx.send('No entity was found')
        print(e)
@mc.command(name='crash')
async def crash(ctx,*,args=None):
    f=open("samples/mc_crash.txt", "r",encoding='utf-8')
    await ctx.send(f.read())


@bot.command(name='help', help='Shows this message')
async def help(ctx,*,args=None):
    try: await ctx.message.delete()
    except: pass
    if args:
        command = None
        for cmd in bot.commands:
            if cmd.name == args and not cmd.hidden:
                command = cmd
                break
        if not command: return await ctx.send('Command not found, please try again.')
        e = discord.Embed(title=f'Command `/' + ((' '.join(command.parents) + ' ' + command.name) if (command.parents) else (command.name)) + '`', description=(command.description or "<no description>"))
        e.add_field(name='Objective',   value=command.help)
        e.add_field(name='Usage',       value=command.usage)
        e.add_field(name='Cog',         value="No cog" if not command.cog else command.cog.qualified_name)
        try:
            if command.commands:
                e.add_field(name='Sub-Commands',value=', '.join([cmd.name for cmd in command.commands]))
        except: pass
        msg = await ctx.send('Type a command name in 30 seconds to get info about the command. [awaiting...]',embed=e)
        names = [(None if cmd.hidden else cmd.name) for cmd in bot.commands] # loop over all commands, if not hidden, append its string name
        cogs = bot.cogs
        def check(m): return m.author == ctx.message.author and m.channel == ctx.message.channel and (m.content in names or m.content in cogs)
        try:
            rt = await bot.wait_for('message', check=check, timeout=30)
            if rt:
                return await ctx.invoke(bot.get_command('help'), args=rt.content)
            return
        except asyncio.exceptions.TimeoutError: return

    all_cmds = bot.commands
    e = discord.Embed(title='Command list',description='wd: <GLOBAL>')
    count = 1
    for cmd in all_cmds:
        e.add_field(name=cmd.name,value=cmd.help or "<no help>")
        count += 1
    msg = await ctx.send('Type a command name in 30 seconds to get info about the command. [awaiting...]',embed=e)
    names = [(None if cmd.hidden else cmd.name) for cmd in bot.commands]
    cogs = bot.cogs
    def check(m):
        return m.author == ctx.message.author and m.channel == ctx.message.channel and (m.content in names or m.content in cogs)
    try:
        rt = await bot.wait_for('message', check=check, timeout=30)
        if rt:
            return await ctx.invoke(bot.get_command('help'), args=rt.content)
        return
    except asyncio.exceptions.TimeoutError: return


@bot.command(name='eval',help='it is eval')
@commands.is_owner()
async def _eval(ctx, *, code='"bruh wat to eval"'):
    try:
        await ctx.send(eval(code))
    except Exception:
        await ctx.send('uh oh. there\'s an error in your code:\n```\n' + traceback.format_exc() + '\n```')


######### background
async def status():
        await bot.wait_until_ready()
        while True:
            try:
                if not MODE or MODE=='NORMAL':
                    activity = discord.Activity(type=discord.ActivityType(3),name=random.choice(statusLs))
                    await bot.change_presence(status=discord.Status.online, activity=activity)
                elif MODE=='DEBUG':
                    await bot.change_presence(status=discord.Status.idle)
                    await log('RUNNING IN **DEBUG** MODE!')
                elif MODE=='FIX':
                    await bot.change_presence(status=discord.Status.dnd)
                    await log('*RUNNING IN EMERGENCY **FIX** MODE!')
                await asyncio.sleep(30)
            except:
                pass


bot.loop.create_task(status())

@bot.event
async def on_command_error(ctx, error):
    """The event triggered when an error is raised while invoking a command.
    Parameters
    ------------
    ctx: commands.Context
        The context used for command invocation.
    error: commands.CommandError
        The Exception raised.
    """

    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return await log(ctx.content + 'caused an error: ' + traceback.format_exc())

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    ignored = (commands.CommandNotFound, )

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, ignored):
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass

    # For this error example we check to see where it came from...
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('I could not find that member. Please try again.')

    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        await log('Ignoring exception in command {}:'.format(str(ctx.command)) + '\n\n```' + str(traceback.format_exc()) + '\n```')

#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_#*_
bot.run(TOKEN,bot=True,reconnect=True)
