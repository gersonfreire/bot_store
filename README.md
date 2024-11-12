# Telegram Store Bot 🛍️

A feature-rich Telegram bot that runs a complete online store with product management, shopping cart, and customer support features.

## Features ✨

- **Product Management**
  - Add, edit, and delete products
  - Product catalog with images and descriptions
  - Stock management

- **Shopping Experience**
  - Browse products with images
  - Shopping cart functionality
  - Checkout process
  - Payment integration

- **Admin Dashboard**
  - Sales statistics
  - Revenue tracking
  - Order management
  - Customer overview

- **Customer Support**
  - Live chat with support representatives
  - Support queue system
  - Admin notification system

- **Data Persistence**
  - All data persists between bot restarts
  - Secure storage of bot data

## Setup 🚀

1. **Prerequisites**
   ```bash
   python 3.7+
   pip
   ```

2. **Installation**
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd telegram-store-bot

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Create a `.env` file in the root directory
   - Add your configuration:
     ```env
     BOT_TOKEN=your_telegram_bot_token
     PAYMENT_PROVIDER_TOKEN=your_payment_provider_token
     ```
   - Update admin IDs in `main.py`

4. **Running the Bot**
   ```bash
   python main.py
   ```

## Usage 📱

### Customer Commands
- `/start` - Start the bot
- `/products` - View available products
- `/cart` - View shopping cart
- `/support` - Request customer support
- `/end_support` - End support session

### Admin Commands
- `/admin_help` - View admin commands
- `/add_product` - Add new product
- `/edit_product` - Edit existing product
- `/delete_product` - Delete product
- `/view_products` - View all products
- `/view_orders` - View all orders
- `/dashboard` - View sales dashboard
- `/support_requests` - View support queue

## Project Structure 📁

```
telegram-store-bot/
├── main.py              # Bot initialization and core setup
├── requirements.txt     # Project dependencies
├── .env                 # Configuration file
├── database/
│   └── store.py        # Data models and store logic
└── handlers/
    ├── admin.py        # Admin command handlers
    ├── customer.py     # Customer command handlers
    └── support.py      # Support system handlers
```

## Security 🔒

- Admin-only commands are protected
- Secure product management
- Protected support system
- Environment variables for sensitive data

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For support, please use the GitHub issues system or contact the maintainers directly.

## Acknowledgments 🙏

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the excellent Telegram bot API wrapper
- All contributors who help improve this project