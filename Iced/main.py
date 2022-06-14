import discord
from discord.ext import commands
import json
import os
import random
from io import BytesIO
from PIL import Image
from discord_components import Select, SelectOption



os.chdir('C:\\Users\\61444\\Desktop\\price eco')
intents = discord.Intents.all()
with open("prefixes.json") as f:
    prefixes = json.load(f)
default_prefix = ">"


def get_prefix(client, message):
    prefix = default_prefix
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
        prefix = prefixes[str(message.guild.id)]

    return commands.when_mentioned_or(prefix)(client, message)


client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
# CMD ERROR
@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    msg = "This command is on cooldown for another {:.2f}s".format(error.retry_after)
    await ctx.reply(msg)
# ON READY
@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Streaming(name=f'{len(client.guilds)} Servers!',url='https://www.twitch.tv/tuxot'))

    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))


# PREFIX
@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '>'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def prefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'`Prefix changed to:` {prefix}')

# ECONOMY START
@client.command(aliases=['bal'])
async def balance(ctx, user: discord.Member=None):
    if user == None:
        user = ctx.author
    await open_account(user)

    users = await get_bank_data()
    wallet = users[str(user.id)]['wallet']
    bank = users[str(user.id)]['bank']
    total = wallet + bank

    embed = discord.Embed(
        title = f"{user}'s Balance",
        color = 0x00FF00
    )
    embed.add_field(name='Wallet Amount', value=wallet)
    embed.add_field(name='Bank Amount', value=bank)
    embed.add_field(name='Total', value=f"💵 {total}", inline = False)
    embed.set_thumbnail(url=user.avatar_url)
    await ctx.reply(embed=embed)

@client.command()
@commands.cooldown(1,120, commands.BucketType.user)
async def beg(ctx):
    user = ctx.author
    await open_account(user)

    users = await get_bank_data()
    earned = random.randrange(251)
    await ctx.reply(f"Dirty Begger, you recieved: ${earned}")
    users[str(user.id)]['wallet'] += earned
    with open("bank.json", "w") as f:
        json.dump(users,f,indent=4)

@client.command(aliases=['with'])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.reply('You cannot withdraw nothing! Please enter an amount!')
        return

    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount>bal[1]:
        await ctx.reply('You do not have enough money in your bank!')
        return
    if amount<0:
        await ctx.reply('You must withdraw a positive amount!')
        return
    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1*amount, "bank")
    await ctx.reply(f'You successfully withdrew: ${amount}')
    
@client.command()
async def deposit(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.reply('You cannot deposit nothing! Please enter an amount!')
        return

    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount>bal[0]:
        await ctx.reply('You do not have enough money in your wallet!')
        return
    if amount<0:
        await ctx.reply('You must deposit a positive amount!')
        return
    await update_bank(ctx.author, -1*amount)
    await update_bank(ctx.author,amount, "bank")
    await ctx.reply(f'You successfully deposited: ${amount}')

@client.command()
async def send(ctx, member: discord.Member,amount=None):
    await open_account(member)
    await open_account(ctx.author)
    if amount == None:
        await ctx.reply('You cannot send nothing! Please enter an amount!')
        return

    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount>bal[1]:
        await ctx.reply('You do not have enough money in your bank!')
        return
    if amount<0:
        await ctx.reply('You must send a positive amount!')
        return
    await update_bank(ctx.author, -1*amount, "bank")
    await update_bank(member,amount, "bank")
    await ctx.reply(f'You successfully gave: {member}: ${amount}')

@client.command()
async def slots(ctx, amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.reply('You cannot bet nothing! Please enter an amount!')
        return

    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount>bal[0]:
        await ctx.reply('You do not have enough money in your wallet!')
        return
    if amount<0:
        await ctx.reply('You must bet a positive amount!')
        return
    final = []
    for i in range(3):
         a = random.choice(["🍒", "🍐", "🍇", "🍎", "🍌", "🍍", "🍉"])

         final.append(a)
    await ctx.reply(str(final))
    if final[0] == final[1] or final[0] == final[2] or final[1] == final[2]:
        await update_bank(ctx.author, 1*amount)
        await ctx.reply("You doubled your bet!")
    else:
        await update_bank(ctx.author, -1*amount)
        await ctx.reply("You lost your bet!")   

@client.command()
async def rob(ctx, member: discord.Member):
    await open_account(member)
    await open_account(ctx.author)
    bal = await update_bank(member)
    if bal[0]<100:
        await ctx.reply('They are too poor! Try someone else!')
        return
    earned = random.randrange(0, bal[0])
    await update_bank(ctx.author, earned)
    await update_bank(member,-1*earned, "bank")
    await ctx.reply(f'You robbed: {member} of ${earned}')

mainshop = [{"name":"Watch","price":100,"description":"Time"},
            {"name":"Laptop","price":1000,"description":"Work"},
            {"name":"PC","price":10000,"description":"Gaming"}]
@client.command()
async def shop(ctx):
    em = discord.Embed(title = "Iced Shop", color = 0x00FF00)

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"${price} | {desc}")

    await ctx.send(embed = em)

@client.command()
async def buy(ctx,item,amount=1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.reply("That object is not here!")
            return
        if res[1]==2:
            await ctx.reply(f"You do not have enough money to buy {amount} {item}")
            return
    
    await ctx.reply(f"You just bought {amount} {item}")

@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    embed = discord.Embed(
        title = 'Bag',
        color = 0x00FF00
    )
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        embed.add_field(name=name, value=f"{amount}")
    
    await ctx.reply(embed=embed)

async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break
    
    if name_ == None:
        return [False,1]

    cost = price*amount
    users = await get_bank_data()
    bal = await update_bank(user)
    
    if bal[0]<cost:
        return [False,2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1
        if t == None:
            obj = {"item":item_name, "amount": amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name, "amount": amount}
        users[str(user.id)]["bag"] = [obj]

    with open("bank.json", "w") as f:
        json.dump(users,f)
    
    await update_bank(user,cost*-1, "wallet")
    return [True, "Worked"]

async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 100

    with open("bank.json", "w") as f:
        json.dump(users,f,indent=4)
    return True

async def get_bank_data():
    with open("bank.json", "r") as f:
        users = json.load(f)

    return users

async def update_bank(user,change = 0,mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("bank.json", "w") as f:
        json.dump(users,f,indent=4)

    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal

# WANTED
@client.command()
async def wanted(ctx, user: discord.Member = None):
  if user == None:
      user = ctx.author

    
  wanted = Image.open("./images/wanted.png")

  asset = user.avatar_url_as(size = 128)
  data = BytesIO(await asset.read())
  pfp = Image.open(data)

  pfp1 = pfp.resize((251,251))
    
  wanted.paste(pfp1, (99,201))

  wanted.save("./images/wanted.jpg")
  await ctx.send(file = discord.File("./images/wanted.jpg"))
@client.command()
async def spongebob(ctx, user: discord.Member = None):
  if user == None:
      user = ctx.author

    
  wanted = Image.open("./images/spongebob.png")

  asset = user.avatar_url_as(size = 128)
  data = BytesIO(await asset.read())
  pfp = Image.open(data)

  pfp1 = pfp.resize((54,63))
    
  wanted.paste(pfp1, (124,88))

  wanted.save("./images/spongebob.jpg")
  await ctx.send(file = discord.File("./images/spongebob.jpg"))



client.run('OTg1ODExNTU3NjEzMTgzMDE4.G7YPji.aFuXk2gloQtOgjt9QB11lgqys1I2kNhb0bAUdA')

