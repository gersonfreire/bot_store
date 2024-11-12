from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from database.store import Store

ADDING_PRODUCT = range(1)

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = """
Admin Commands:
/add_product - Add new product
/edit_product - Edit existing product
/delete_product - Delete a product
/view_products - View all products
/view_orders - View all orders
/view_customers - View all customers
/dashboard - View sales dashboard
/support_requests - View support requests
/git [command] - Execute git commands
/restart - Restart the bot
"""
    await update.message.reply_text(commands)

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in context.bot_data.get('admins', []):
        await update.message.reply_text("Unauthorized access.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Please send product details in the following format:\n"
        "name | description | price | stock | image_url"
    )
    return ADDING_PRODUCT

async def add_product_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = update.message.text.split('|')
        name = data[0].strip()
        description = data[1].strip()
        price = float(data[2].strip())
        stock = int(data[3].strip())
        image_url = data[4].strip()
        
        store: Store = context.bot_data['store']
        product = store.add_product(name, description, price, stock, image_url)
        
        await update.message.reply_text(f"Product added successfully!\nID: {product.id}")
    except Exception as e:
        await update.message.reply_text(f"Error adding product: {str(e)}")
    
    return ConversationHandler.END

async def view_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in context.bot_data.get('admins', []):
        await update.message.reply_text("Unauthorized access.")
        return
    
    store: Store = context.bot_data['store']
    stats = store.get_revenue_stats()
    
    dashboard = f"""
📊 Store Dashboard
Total Revenue: ${stats['total_revenue']:.2f}
Total Orders: {stats['total_orders']}
Average Order Value: ${stats['average_order_value']:.2f}
"""
    await update.message.reply_text(dashboard)

def register_admin_handlers(application):
    # Add product conversation
    add_product_conv = ConversationHandler(
        entry_points=[CommandHandler('add_product', add_product_start)],
        states={
            ADDING_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_data)]
        },
        fallbacks=[]
    )
    
    application.add_handler(add_product_conv)
    application.add_handler(CommandHandler('admin_help', admin_help))
    application.add_handler(CommandHandler('dashboard', view_dashboard))