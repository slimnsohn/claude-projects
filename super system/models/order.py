from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
from config.constants import Provider, BetType

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    """Order model for tracking bets/positions"""
    order_id: str
    provider: Provider
    game_id: str
    bet_type: BetType
    side: OrderSide
    
    # Order details
    quantity: float  # Number of shares/contracts
    price: float     # Price per share/contract
    
    # Order state
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None
    
    # Execution details
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    
    # Metadata
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    market_description: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    @property
    def total_value(self) -> float:
        """Total value of the order"""
        return self.quantity * self.price
    
    @property
    def unfilled_quantity(self) -> float:
        """Remaining quantity to be filled"""
        return self.quantity - self.filled_quantity
    
    @property
    def is_fully_filled(self) -> bool:
        """Check if order is completely filled"""
        return self.filled_quantity >= self.quantity
    
    @property
    def fill_percentage(self) -> float:
        """Percentage of order that has been filled"""
        if self.quantity == 0:
            return 0.0
        return (self.filled_quantity / self.quantity) * 100
    
    def update_fill(self, fill_quantity: float, fill_price: float):
        """Update order with new fill information"""
        if fill_quantity <= 0:
            return
        
        # Calculate new average fill price
        total_filled_value = (self.filled_quantity * self.average_fill_price) + (fill_quantity * fill_price)
        new_total_quantity = self.filled_quantity + fill_quantity
        
        if new_total_quantity > 0:
            self.average_fill_price = total_filled_value / new_total_quantity
        
        self.filled_quantity = min(new_total_quantity, self.quantity)
        self.updated_at = datetime.now()
        
        # Update status
        if self.is_fully_filled:
            self.status = OrderStatus.FILLED
        elif self.filled_quantity > 0:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def cancel(self):
        """Cancel the order"""
        if self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]:
            self.status = OrderStatus.CANCELLED
            self.updated_at = datetime.now()
    
    def reject(self, reason: Optional[str] = None):
        """Reject the order"""
        self.status = OrderStatus.REJECTED
        self.updated_at = datetime.now()
    
    def __str__(self):
        return (f"{self.side.value.upper()} {self.quantity} @ ${self.price:.2f} "
                f"({self.bet_type.value} - {self.status.value})")

@dataclass
class Position:
    """Position model for tracking current holdings"""
    provider: Provider
    game_id: str
    bet_type: BetType
    
    # Position details
    quantity: float  # Current position size
    average_cost: float  # Average cost basis
    current_price: float  # Current market price
    
    # Metadata
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    market_description: Optional[str] = None
    
    # Timestamps
    opened_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.opened_at is None:
            self.opened_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = self.opened_at
    
    @property
    def total_cost(self) -> float:
        """Total cost basis of position"""
        return abs(self.quantity) * self.average_cost
    
    @property
    def current_value(self) -> float:
        """Current market value of position"""
        return abs(self.quantity) * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss"""
        if self.quantity > 0:  # Long position
            return (self.current_price - self.average_cost) * self.quantity
        else:  # Short position
            return (self.average_cost - self.current_price) * abs(self.quantity)
    
    @property
    def unrealized_pnl_percentage(self) -> float:
        """Unrealized P&L as percentage"""
        if self.total_cost == 0:
            return 0.0
        return (self.unrealized_pnl / self.total_cost) * 100
    
    def update_price(self, new_price: float):
        """Update current market price"""
        self.current_price = new_price
        self.updated_at = datetime.now()
    
    def add_to_position(self, quantity: float, price: float):
        """Add to existing position"""
        if self.quantity == 0:
            # New position
            self.quantity = quantity
            self.average_cost = price
        else:
            # Add to existing position
            total_cost = (self.quantity * self.average_cost) + (quantity * price)
            self.quantity += quantity
            if self.quantity != 0:
                self.average_cost = total_cost / self.quantity
        
        self.updated_at = datetime.now()
    
    def close_position(self, quantity: float = None):
        """Close all or part of the position"""
        if quantity is None:
            quantity = abs(self.quantity)
        
        if abs(quantity) >= abs(self.quantity):
            self.quantity = 0
        else:
            self.quantity -= quantity if self.quantity > 0 else -quantity
        
        self.updated_at = datetime.now()
    
    def __str__(self):
        direction = "LONG" if self.quantity > 0 else "SHORT"
        return (f"{direction} {abs(self.quantity)} @ ${self.average_cost:.2f} "
                f"(Current: ${self.current_price:.2f}, P&L: ${self.unrealized_pnl:.2f})")