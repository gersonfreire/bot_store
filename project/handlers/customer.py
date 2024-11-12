from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, PreCheckoutQueryHandler
from database.store import Store

async def view_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: Store = context.bot_data['store']
    
    if not store.products:
        await update.message.reply_text("No products available.")
        return
    
    for product in store.products.values():
        keyboard = [
            [InlineKeyboardButton("Add to Cart", callback_data=f"add_to_cart_{product.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
{product.name}
Description: {product.description}
Price: ${product.price:.2f}
Stock: {product.stock}
"""
        await update.message.reply_photo(
            photo=product.image_url,
            caption=message,
            reply_markup=reply_markup
        )

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: Store = context.bot_data['store']
    user_id = update.effective_user.id
    
    if user_id not in store.customers or not store.customers[user_id].cart:
        await update.message.reply_text("Your cart is empty.")
        return
    
    customer = store.customers[user_id]
    cart_items = []
    total = 0
    
    for product_id, quantity in customer.cart.items():
        product = store.products[product_id]
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append(f"{product.name} x{quantity} - ${subtotal:.2f}")
    
    cart_message = "\n".join(cart_items) + f"\n\nTotal: ${total:.2f}"
    
    keyboard = [[InlineKeyboardButton("Checkout", callback_data="checkout")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(cart_message, reply_markup=reply_markup)

async def handle_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    store: Store = context.bot_data['store']
    
    if query.data.startswith("add_to_cart_"):
        product_id = int(query.data.split("_")[-1])
        if store.add_to_cart(query.from_user.id, product_id, 1):
            await query.answer("Product added to cart!")
        else:
            await query.answer("Failed to add product to cart.")
    elif query.data == "checkout":
        order = store.create_order(query.from_user.id)
        if order:
            await query.message.reply_text(
                f"Order created! Total: ${order.total:.2f}\n"
                "Use /pay to complete your purchase."
            )
        else:
            await query.message.reply_text("Failed to create order.")

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store: Store = context.bot_data['store']
    user_id = update.effective_user.id
    
    # Get the latest pending order for the user
    order = store.get_pending_order(user_id)
    if not order:
        await update.message.reply_text("No pending orders found. Please create an order first.")
        return

    # Create the invoice
    title = "Order Payment"
    description = "Payment for your order"
    payload = f"order_{order.id}"
    currency = "USD"
    
    # Convert total to cents/minimal units as required by Telegram
    price = int(order.total * 100)
    prices = [LabeledPrice("Total", price)]

    # Send invoice
    await context.bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=context.bot_data.get('payment_provider_token'),
        currency=currency,
        prices=prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the pre-checkout callback"""
    query = update.pre_checkout_query
    
    # Always accept the checkout for this example
    # In a real application, you might want to verify stock availability here
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payments"""
    store: Store = context.bot_data['store']
    payment = update.message.successful_payment
    order_id = int(payment.invoice_payload.split('_')[1])
    
    # Update order status
    store.complete_order(order_id)
    
    await update.message.reply_text(
        "Thank you for your purchase! Your order has been confirmed."
    )

def register_customer_handlers(application):
    application.add_handler(CommandHandler('products', view_products))
    application.add_handler(CommandHandler('cart', view_cart))
    application.add_handler(CommandHandler('pay', process_payment))
    application.add_handler(CallbackQueryHandler(handle_cart_callback))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))