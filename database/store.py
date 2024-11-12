from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    stock: int
    image_url: str

@dataclass
class Customer:
    id: int
    username: str
    cart: Dict[int, int]  # product_id: quantity
    total_spent: float

@dataclass
class Order:
    id: int
    customer_id: int
    products: Dict[int, int]  # product_id: quantity
    total: float
    status: str
    date: datetime

class Store:
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self.customers: Dict[int, Customer] = {}
        self.orders: List[Order] = []
        self.support_queue: List[int] = []  # List of user_ids waiting for support
        self.active_support_sessions: Dict[int, int] = {}  # user_id: admin_id
        self.next_product_id = 1
        self.next_order_id = 1

    def add_product(self, name: str, description: str, price: float, stock: int, image_url: str) -> Product:
        product = Product(self.next_product_id, name, description, price, stock, image_url)
        self.products[product.id] = product
        self.next_product_id += 1
        return product

    def get_product(self, product_id: int) -> Product:
        return self.products.get(product_id)

    def update_product(self, product_id: int, **kwargs) -> bool:
        if product_id in self.products:
            product = self.products[product_id]
            for key, value in kwargs.items():
                setattr(product, key, value)
            return True
        return False

    def delete_product(self, product_id: int) -> bool:
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False

    def add_to_cart(self, customer_id: int, product_id: int, quantity: int) -> bool:
        if customer_id not in self.customers:
            self.customers[customer_id] = Customer(customer_id, "", {}, 0.0)
        
        if product_id in self.products and self.products[product_id].stock >= quantity:
            customer = self.customers[customer_id]
            current_quantity = customer.cart.get(product_id, 0)
            customer.cart[product_id] = current_quantity + quantity
            return True
        return False

    def create_order(self, customer_id: int) -> Order:
        if customer_id not in self.customers:
            return None
        
        customer = self.customers[customer_id]
        if not customer.cart:
            return None
        
        total = sum(self.products[pid].price * qty for pid, qty in customer.cart.items())
        order = Order(self.next_order_id, customer_id, customer.cart.copy(), total, "pending", datetime.now())
        self.orders.append(order)
        self.next_order_id += 1
        
        # Clear cart after order creation
        customer.cart = {}
        
        return order

    def get_pending_order(self, customer_id: int) -> Order:
        """Get the latest pending order for a customer"""
        for order in reversed(self.orders):
            if order.customer_id == customer_id and order.status == "pending":
                return order
        return None

    def complete_order(self, order_id: int) -> bool:
        """Mark an order as completed and update customer total spent"""
        for order in self.orders:
            if order.id == order_id and order.status == "pending":
                order.status = "completed"
                # Update customer total spent
                if order.customer_id in self.customers:
                    self.customers[order.customer_id].total_spent += order.total
                # Update product stock
                for product_id, quantity in order.products.items():
                    if product_id in self.products:
                        self.products[product_id].stock -= quantity
                return True
        return False

    def get_revenue_stats(self) -> dict:
        total_revenue = sum(order.total for order in self.orders if order.status == "completed")
        total_orders = len([order for order in self.orders if order.status == "completed"])
        return {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "average_order_value": total_revenue / total_orders if total_orders > 0 else 0
        }