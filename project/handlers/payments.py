from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.store import Store
import uuid
import os
import json
import hmac
import hashlib
from datetime import datetime

class PayPalHandler:
    def __init__(self):
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        self.webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')
        self.base_url = "https://api-m.paypal.com" if os.getenv('PAYPAL_MODE') == 'live' else "https://api-m.sandbox.paypal.com"
        self.payment_links = {}  # Store payment links with order info

    def generate_payment_link(self, order_id: int, amount: float, description: str) -> str:
        """Generate a PayPal payment link for the order"""
        # In a real implementation, you would use PayPal's API to create a payment link
        # This is a simplified example
        payment_id = str(uuid.uuid4())
        payment_link = f"{self.base_url}/checkout/pay/{payment_id}"
        
        # Store payment information for verification
        self.payment_links[payment_id] = {
            'order_id': order_id,
            'amount': amount,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        return payment_link

    def verify_webhook_signature(self, payload: str, headers: dict) -> bool:
        """Verify PayPal webhook signature"""
        if not self.webhook_id:
            return False

        auth_algo = headers.get('PAYPAL-AUTH-ALGO')
        cert_url = headers.get('PAYPAL-CERT-URL')
        transmission_id = headers.get('PAYPAL-TRANSMISSION-ID')
        transmission_sig = headers.get('PAYPAL-TRANSMISSION-SIG')
        transmission_time = headers.get('PAYPAL-TRANSMISSION-TIME')

        # Verify webhook signature using PayPal's algorithm
        # This is a simplified example - in production, implement full signature verification
        expected_sig = hmac.new(
            self.webhook_id.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(transmission_sig, expected_sig)

async def paypal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /paypal command to generate a PayPal payment link"""
    store: Store = context.bot_data['store']
    user_id = update.effective_user.id
    
    # Get the latest pending order
    order = store.get_pending_order(user_id)
    if not order:
        await update.message.reply_text("No pending orders found. Please create an order first.")
        return

    # Get PayPal handler from bot data or create new one
    if 'paypal_handler' not in context.bot_data:
        context.bot_data['paypal_handler'] = PayPalHandler()
    paypal_handler = context.bot_data['paypal_handler']

    # Generate payment link
    payment_link = paypal_handler.generate_payment_link(
        order.id,
        order.total,
        f"Order #{order.id} - Total: ${order.total:.2f}"
    )

    # Send payment link to user
    await update.message.reply_text(
        f"Please complete your payment using this link:\n{payment_link}\n\n"
        "Your order will be confirmed automatically once the payment is completed."
    )

async def handle_paypal_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PayPal webhook notifications"""
    store: Store = context.bot_data['store']
    paypal_handler = context.bot_data.get('paypal_handler')
    
    if not paypal_handler:
        return
    
    # Verify webhook signature
    if not paypal_handler.verify_webhook_signature(
        update.message.text,
        update.message.json.get('headers', {})
    ):
        return

    try:
        # Parse webhook payload
        payload = json.loads(update.message.text)
        event_type = payload.get('event_type')
        
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Get payment and order details
            payment_id = payload['resource']['id']
            payment_info = paypal_handler.payment_links.get(payment_id)
            
            if payment_info and payment_info['status'] == 'pending':
                order_id = payment_info['order_id']
                
                # Complete the order
                if store.complete_order(order_id):
                    # Get customer ID from order
                    order = next((o for o in store.orders if o.id == order_id), None)
                    if order:
                        # Notify customer
                        await context.bot.send_message(
                            chat_id=order.customer_id,
                            text="🎉 Your payment has been completed! Thank you for your purchase."
                        )
                        
                        # Notify admins
                        for admin_id in context.bot_data.get('admins', []):
                            await context.bot.send_message(
                                chat_id=admin_id,
                                text=f"💰 New payment received for Order #{order_id}\n"
                                     f"Amount: ${payment_info['amount']:.2f}"
                            )
                        
                        # Update payment status
                        payment_info['status'] = 'completed'
                
    except Exception as e:
        # Log the error in a production environment
        print(f"Error processing PayPal webhook: {str(e)}")

def register_payment_handlers(application):
    """Register payment-related handlers"""
    application.add_handler(CommandHandler('paypal', paypal_command))