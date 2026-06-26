import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

# ============================
# إعدادات البوت
# ============================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# متغير لتخزين آخر رسالة بعتها البوت
last_bot_message = {}

# ID السيرفر
GUILD_ID = discord.Object(id=1386495074585546834)

# ============================
# الرول المسموح له باستخدام البوت
# ============================
OWNER_ROLE = "𝐎𝐖𝐍𝐄𝐑"

def has_owner_role(interaction: discord.Interaction) -> bool:
    return any(r.name == OWNER_ROLE for r in interaction.user.roles)

async def check_role(interaction: discord.Interaction) -> bool:
    if not has_owner_role(interaction):
        await interaction.response.send_message("❌ مش معاك صلاحية استخدام البوت!", ephemeral=True)
        return False
    return True

# ============================
# أحداث البوت
# ============================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=GUILD_ID)
        print(f"\033[92msuccess\033[0m")
    except Exception as e:
        print(f"error: {e}")

# ============================
# لوحة التحكم
# ============================

@bot.tree.command(guild=GUILD_ID, name="dashboard", description="لوحة تحكم البوت وكل الأوامر")
async def dashboard(interaction: discord.Interaction):
    if not await check_role(interaction): return
    embed = discord.Embed(title="🎛️ لوحة التحكم - cairoVerse", description="كل الأوامر المتاحة في البوت", color=discord.Color.gold())
    embed.add_field(name="🛡️ الإدارة", value="`/ban`\n`/unban`\n`/kick`\n`/role`\n`/roles`", inline=True)
    embed.add_field(name="💬 الرسائل", value="`/lock`\n`/unlock`\n`/clear`\n`/say`\n`/edit`\n`/announce`", inline=True)
    embed.add_field(name="ℹ️ عامة", value="`/profile`\n`/ping`\n`/serverinfo`\n`/dashboard`", inline=True)
    embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}")
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ============================
# أوامر الإدارة
# ============================

@bot.tree.command(guild=GUILD_ID, name="ban", description="حظر عضو من السيرفر")
@app_commands.describe(عضو="العضو اللي هتحظره", سبب="سبب الحظر")
async def ban(interaction: discord.Interaction, عضو: discord.Member, سبب: str = "مفيش سبب محدد"):
    if not await check_role(interaction): return
    await interaction.response.defer()
    await عضو.ban(reason=سبب)
    embed = discord.Embed(title="🔨 تم الحظر", description=f"تم حظر {عضو.mention}\n**السبب:** {سبب}", color=discord.Color.red())
    embed.set_footer(text=f"بواسطة: {interaction.user.name}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(guild=GUILD_ID, name="unban", description="رفع الحظر عن عضو")
@app_commands.describe(user_id="الـ ID بتاع العضو المحظور")
async def unban(interaction: discord.Interaction, user_id: str):
    if not await check_role(interaction): return
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        embed = discord.Embed(title="✅ تم رفع الحظر", description=f"تم رفع الحظر عن **{user.name}**", color=discord.Color.green())
        embed.set_footer(text=f"بواسطة: {interaction.user.name}")
        await interaction.response.send_message(embed=embed)
    except discord.NotFound:
        await interaction.response.send_message("❌ ملقتش العضو ده أو مش محظور!", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("❌ الـ ID مش صح!", ephemeral=True)

@bot.tree.command(guild=GUILD_ID, name="kick", description="طرد عضو من السيرفر بدون حظر")
@app_commands.describe(عضو="العضو اللي هتطرده", سبب="سبب الطرد")
async def kick(interaction: discord.Interaction, عضو: discord.Member, سبب: str = "مفيش سبب محدد"):
    if not await check_role(interaction): return
    await interaction.response.defer()
    await عضو.kick(reason=سبب)
    embed = discord.Embed(title="🦶 تم الطرد", description=f"تم طرد {عضو.mention}\n**السبب:** {سبب}", color=discord.Color.orange())
    embed.set_footer(text=f"بواسطة: {interaction.user.name}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(guild=GUILD_ID, name="role", description="إعطاء أو سحب رول من عضو")
@app_commands.describe(عضو="العضو", رول="الرول اللي هتديه أو تسحبه")
async def role(interaction: discord.Interaction, عضو: discord.Member, رول: discord.Role):
    if not await check_role(interaction): return
    await interaction.response.defer()
    if رول in عضو.roles:
        await عضو.remove_roles(رول)
        embed = discord.Embed(title="➖ تم سحب الرول", description=f"تم سحب {رول.mention} من {عضو.mention}", color=discord.Color.red())
    else:
        await عضو.add_roles(رول)
        embed = discord.Embed(title="➕ تم إعطاء الرول", description=f"تم إعطاء {رول.mention} لـ {عضو.mention}", color=discord.Color.green())
    embed.set_footer(text=f"بواسطة: {interaction.user.name}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(guild=GUILD_ID, name="roles", description="شوف رولات عضو معين")
@app_commands.describe(عضو="العضو اللي عايز تشوف رولاته")
async def roles(interaction: discord.Interaction, عضو: discord.Member = None):
    if not await check_role(interaction): return
    عضو = عضو or interaction.user
    رولات = [رول.mention for رول in عضو.roles[1:]]
    embed = discord.Embed(title=f"🎭 رولات {عضو.name}", description=", ".join(رولات) if رولات else "مفيش رولات", color=عضو.color)
    embed.set_thumbnail(url=عضو.display_avatar.url)
    embed.set_footer(text=f"عدد الرولات: {len(رولات)}")
    await interaction.response.send_message(embed=embed)

# ============================
# أوامر القنوات والرسائل
# ============================

@bot.tree.command(guild=GUILD_ID, name="clear", description="مسح رسايل من الشات")
@app_commands.describe(عدد="عدد الرسايل اللي هتمسحها")
async def clear(interaction: discord.Interaction, عدد: int):
    if not await check_role(interaction): return
    if عدد < 1 or عدد > 100:
        await interaction.response.send_message("❌ العدد لازم يكون بين 1 و 100!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=عدد)
    await interaction.followup.send(f"✅ تم مسح **{len(deleted)}** رسالة!", ephemeral=True)

@bot.tree.command(guild=GUILD_ID, name="say", description="قول رسالة في قناة معينة")
@app_commands.describe(قناة="القناة اللي هتبعت فيها", رسالة="الرسالة")
async def say(interaction: discord.Interaction, قناة: discord.TextChannel, رسالة: str):
    if not await check_role(interaction): return
    رسالة = رسالة.replace("\\n", "\n")
    msg = await قناة.send(رسالة)
    last_bot_message[قناة.id] = msg
    await interaction.response.send_message(f"✅ تم إرسال الرسالة في {قناة.mention}", ephemeral=True)

@bot.tree.command(guild=GUILD_ID, name="edit", description="تعديل آخر رسالة بعتها البوت في القناة")
@app_commands.describe(قناة="القناة اللي فيها الرسالة", رسالة_جديدة="النص الجديد")
async def edit(interaction: discord.Interaction, قناة: discord.TextChannel, رسالة_جديدة: str):
    if not await check_role(interaction): return
    msg = last_bot_message.get(قناة.id)
    if msg is None:
        await interaction.response.send_message("❌ مفيش رسالة بعتها البوت في الشات ده!", ephemeral=True)
        return
    await msg.edit(content=رسالة_جديدة)
    await interaction.response.send_message(f"✅ تم تعديل الرسالة في {قناة.mention}", ephemeral=True)

@bot.tree.command(guild=GUILD_ID, name="announce", description="إرسال إعلان مميز في قناة")
@app_commands.describe(قناة="القناة", عنوان="عنوان الإعلان", وصف="محتوى الإعلان")
async def announce(interaction: discord.Interaction, قناة: discord.TextChannel, عنوان: str, وصف: str):
    if not await check_role(interaction): return
    embed = discord.Embed(title=f"📢 {عنوان}", description=وصف, color=discord.Color.blue())
    embed.set_footer(text=f"من: {interaction.user.name}")
    await قناة.send(embed=embed)
    await interaction.response.send_message(f"✅ تم إرسال الإعلان في {قناة.mention}", ephemeral=True)

# ============================
# أوامر عامة
# ============================

@bot.tree.command(guild=GUILD_ID, name="profile", description="معلومات عن عضو")
@app_commands.describe(عضو="العضو اللي عايز تعرف معلوماته")
async def profile(interaction: discord.Interaction, عضو: discord.Member = None):
    if not await check_role(interaction): return
    عضو = عضو or interaction.user
    embed = discord.Embed(title=f"👤 معلومات {عضو.name}", color=عضو.color)
    embed.set_thumbnail(url=عضو.display_avatar.url)
    embed.add_field(name="الاسم", value=عضو.name, inline=True)
    embed.add_field(name="الرقم التعريفي", value=عضو.id, inline=True)
    embed.add_field(name="انضم للسيرفر", value=عضو.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="تاريخ إنشاء الحساب", value=عضو.created_at.strftime("%Y-%m-%d"), inline=True)
    رولات = [رول.mention for رول in عضو.roles[1:]]
    embed.add_field(name=f"الرتب ({len(رولات)})", value=", ".join(رولات) if رولات else "مفيش رتب", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(guild=GUILD_ID, name="ping", description="سرعة البوت")
async def ping(interaction: discord.Interaction):
    if not await check_role(interaction): return
    تأخير = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 سرعة البوت: **{تأخير} مللي ثانية**")

@bot.tree.command(guild=GUILD_ID, name="serverinfo", description="معلومات عن السيرفر")
async def serverinfo(interaction: discord.Interaction):
    if not await check_role(interaction): return
    guild = interaction.guild
    embed = discord.Embed(title=f"🏠 {guild.name}", color=discord.Color.blurple())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="الأعضاء", value=guild.member_count, inline=True)
    embed.add_field(name="القنوات", value=len(guild.channels), inline=True)
    embed.add_field(name="الرولات", value=len(guild.roles), inline=True)
    embed.add_field(name="المالك", value=guild.owner.mention, inline=True)
    embed.add_field(name="تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    await interaction.response.send_message(embed=embed)

# ============================
# تشغيل البوت
# ============================
التوكن = os.getenv("DISCORD_TOKEN")
if not التوكن:
    print("❌ مفيش توكن! افتح ملف .env وحط فيه: DISCORD_TOKEN=توكنك")
else:
    bot.run(التوكن)
