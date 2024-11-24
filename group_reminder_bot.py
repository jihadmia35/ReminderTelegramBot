from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import asyncio

# Replace with your API token from BotFather
API_TOKEN = "8051289787:AAGkZN84emfDP_DtkzNUwj1jzXULjEcYZUY"
GROUP_CHAT_ID = "-1002028827977"  # Replace with your group's chat ID

# User mention mapping (daily and weekly reminders)
USER_MENTIONS = {
    "Saturday": ("Robi Today is the day to take out your trash", "@RIRrobi"),
    "Sunday": ("Mehedi Today is the day to take out your trash", "@Mehedi SEU"),
    "Monday": ("Abid Today is the day to take out your trash", "@Abid_3_1_3"),
    "Tuesday": ("Jihad Today is the day to take out your trash", "@Jihad"),
    "Wednesday": ("Habib Today is the day to take out your trash", "@Habib SEU"),
    "Thursday": ("Shoyab Today is the day to take out your trash", "@Kishor_70"),
    "Friday": None,  # No daily reminders on Friday
}

# Weekly reminder queue (rotating among the 6 users)
WEEKLY_QUEUE = list(USER_MENTIONS.values())[:-1]  # Exclude Friday
weekly_index = 0  # To track the current person in the queue


async def send_message(bot: Bot, message: str):
    """Send a message to the group chat."""
    try:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        print(f"Error sending message: {e}")


async def send_daily_reminders(bot: Bot):
    """Send daily reminders at specified times."""
    current_day = datetime.now().strftime("%A")  # Get current day name

    if current_day == "Friday":
        return  # Skip reminders on Friday

    # Fetch daily message and mention based on the day
    daily_message, mention = USER_MENTIONS.get(current_day, ("", ""))
    if not daily_message or not mention:
        return  # No message defined for the day

    # Prepare and send the message
    message = f"{mention}, {daily_message}"
    await send_message(bot, message)


async def send_weekly_reminders(bot: Bot):
    """Send weekly reminders, rotating through the user queue."""
    global weekly_index

    # Get the current user in the weekly queue
    if weekly_index >= len(WEEKLY_QUEUE):
        weekly_index = 0  # Reset rotation

    weekly_message, mention = WEEKLY_QUEUE[weekly_index]
    if weekly_message and mention:
        message = f"Weekly Reminder: {mention}, {weekly_message}"
        await send_message(bot, message)

    # Move to the next person in the queue
    weekly_index += 1


def wrap_coroutine(coroutine_func, *args):
    """Wrap a coroutine in a synchronous function for APScheduler."""
    asyncio.run(coroutine_func(*args))


def setup_scheduler(bot: Bot):
    """Set up the reminder scheduler."""
    scheduler = BackgroundScheduler(timezone="Asia/Dhaka")  # Set to your timezone

    # Schedule daily reminders (3 times a day)
    scheduler.add_job(
        wrap_coroutine, 'cron', hour=13, minute=00, args=[send_daily_reminders, bot]
    )  # 1 PM
    scheduler.add_job(
        wrap_coroutine, 'cron', hour=16, minute=0, args=[send_daily_reminders, bot]
    )  # 4 PM
    scheduler.add_job(
        wrap_coroutine, 'cron', hour=19, minute=0, args=[send_daily_reminders, bot]
    )  # 7 PM

    # Schedule weekly reminders (3 times a day)
    scheduler.add_job(
        wrap_coroutine, 'cron', hour=13, minute=0, args=[send_weekly_reminders, bot]
    )  # 1 PM
    scheduler.add_job(
        wrap_coroutine, 'cron', hour=16, minute=0, args=[send_weekly_reminders, bot]
    )  # 4 PM
    scheduler.add_job(
        wrap_coroutine, 'cron', hour=19, minute=0, args=[send_weekly_reminders, bot]
    )  # 7 PM

    scheduler.start()


async def start(update, context):
    """Handle the /start command."""
    await update.message.reply_text("Reminder bot is now active and scheduled!")


def main():
    """Main entry point for the bot."""
    # Create the application (replaces Updater in 20.x+)
    application = Application.builder().token(API_TOKEN).build()

    # Add /start command
    application.add_handler(CommandHandler("start", start))

    # Create a Bot instance
    bot = Bot(token=API_TOKEN)

    # Start the scheduler
    setup_scheduler(bot)

    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    main()
