from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.store import Store

async def request_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: Store = context.bot_data['store']
    user_id = update.effective_user.id
    
    if user_id in store.support_queue:
        await update.message.reply_text("You are already in the support queue.")
        return
    
    if user_id in store.active_support_sessions:
        await update.message.reply_text("You are already in an active support session.")
        return
    
    store.support_queue.append(user_id)
    await update.message.reply_text(
        "You have been added to the support queue. "
        "An administrator will be with you shortly."
    )
    
    # Notify all admins
    for admin_id in context.bot_data.get('admins', []):
        keyboard = [[
            InlineKeyboardButton(
                "Accept Request",
                callback_data=f"support_accept_{user_id}"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"New support request from user {user_id}",
            reply_markup=reply_markup
        )

async def handle_support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    store: Store = context.bot_data['store']
    
    if query.data.startswith("support_accept_"):
        user_id = int(query.data.split("_")[-1])
        admin_id = query.from_user.id
        
        if user_id in store.support_queue:
            store.support_queue.remove(user_id)
            store.active_support_sessions[user_id] = admin_id
            
            await context.bot.send_message(
                chat_id=user_id,
                text="An administrator has accepted your support request. You can now communicate directly."
            )
            await query.message.reply_text(f"You are now connected with user {user_id}")
        else:
            await query.message.reply_text("This support request is no longer valid.")

async def end_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: Store = context.bot_data['store']
    user_id = update.effective_user.id
    
    if user_id in store.active_support_sessions:
        admin_id = store.active_support_sessions[user_id]
        del store.active_support_sessions[user_id]
        
        await update.message.reply_text("Support session ended.")
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"Support session with user {user_id} has ended."
        )
    else:
        await update.message.reply_text("You are not in an active support session.")

def register_support_handlers(application):
    application.add_handler(CommandHandler('support', request_support))
    application.add_handler(CommandHandler('end_support', end_support))
    application.add_handler(CallbackQueryHandler(handle_support_callback))