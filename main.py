from telegram.ext import Application, CommandHandler, MessageHandler, filters, PicklePersistence
from dotenv import load_dotenv
import os
import logging
import sys
import subprocess
from handlers.admin import register_admin_handlers
from handlers.customer import register_customer_handlers
from handlers.support import register_support_handlers
from handlers.payments import register_payment_handlers
from database.store import Store

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    user_id = update.effective_user.id
    if user_id in context.bot_data.get('admins', []):
        await update.message.reply_text(
            "Welcome admin! Use /help_admin to see available commands."
        )
    else:
        await update.message.reply_text(
            "Welcome to our store! Use /help to see available commands."
        )

async def help_command(update, context):
    help_text = """
🛍️ *Available Commands*

Shopping:
/products - Browse our product catalog
/cart - View your shopping cart
/pay - Process payment for your order
/paypal - Get PayPal payment link

Support:
/support - Request to talk with a support representative
/end\_support - End your support session

General:
/help - Show this help message
/start - Start/restart the bot

Need assistance? Use /support to chat with our team!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def git_command(update, context):
    """Handle git commands from admin users"""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get('admins', []):
        await update.message.reply_text("Unauthorized access.")
        return

    if not context.args:
        await update.message.reply_text("Please provide a git command. Example: /git pull")
        return

    try:
        # Construct the git command
        git_cmd = ['git'] + list(context.args)
        
        # Execute the git command and capture output
        process = subprocess.Popen(
            git_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        # Prepare response message
        response = ""
        if stdout:
            response += f"Output:\n{stdout}\n"
        if stderr:
            response += f"Errors:\n{stderr}\n"
        if not response:
            response = "Command executed successfully with no output."

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error executing git command: {str(e)}")

async def restart_command(update, context):
    """Handle bot restart from admin users"""
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get('admins', []):
        await update.message.reply_text("Unauthorized access.")
        return

    await update.message.reply_text("Bot is restarting...")
    
    # Save any pending data
    if hasattr(context.application, 'persistence'):
        context.application.persistence.flush()
    
    # Restart the process
    os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    load_dotenv()
    
    # Initialize persistence
    persistence = PicklePersistence(filepath="store_bot_data")
    
    # Initialize application
    application = Application.builder()\
        .token(os.getenv('BOT_TOKEN'))\
        .persistence(persistence)\
        .build()
    
    # Initialize store if not exists
    if not hasattr(application.bot_data, 'store'):
        application.bot_data['store'] = Store()
    
    # Initialize admins list if not exists
    if 'admins' not in application.bot_data:
        # Add your admin Telegram ID here
        application.bot_data['admins'] = [123456789]  # Replace with actual admin IDs
    
    # Add payment provider tokens to bot_data
    application.bot_data['payment_provider_token'] = os.getenv('PAYMENT_PROVIDER_TOKEN')
    
    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('git', git_command))
    application.add_handler(CommandHandler('restart', restart_command))
    register_admin_handlers(application)
    register_customer_handlers(application)
    register_support_handlers(application)
    register_payment_handlers(application)
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()