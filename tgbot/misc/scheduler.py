import pytz
from adguardhome import AdGuardHome
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config

scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Yekaterinburg"))
config = load_config(".env")


async def dns_stats(bot: Bot):
    """Отправляет статистику запросов из Adguard Home."""
    async with AdGuardHome(host=config.internet.adguard_host, port=config.internet.adguard_port, username=config.internet.adguard_username, password=config.internet.adguard_password) as adguard:
        version = await adguard.version()
        protection_status = await adguard.protection_enabled()
        dns_queries = await adguard.stats.dns_queries()
        blocked_queries = await adguard.stats.blocked_filtering()
        blocked_queries_perc = await adguard.stats.blocked_percentage()
        avg_processing_time = await adguard.stats.avg_processing_time()
        period = await adguard.stats.period()

    message = await bot.send_message(
        chat_id=config.group.group_id,
        message_thread_id=config.group.internet_topic,
        text=f"""🛡️ <b>Статистика AdGuard Home</b>

📈 <b>DNS-запросов:</b> <code>{dns_queries}</code>
🚫 <b>Блокировано запросов:</b> <code>{blocked_queries}</code>
({blocked_queries_perc:.1f}%)
⏱️ <b>Среднее время обработки:</b> <code>{avg_processing_time:.2f} мс</code>

{'✅ Защита включена' if protection_status else '❌ Защита выключена'}
♻️ Частота очистки: <code>Раз в {period} дней</code>
🔢 <b>Версия:</b> <code>{version}</code>"""
    )
    await bot.pin_chat_message(message_id=message.message_id, chat_id=message.chat.id)
