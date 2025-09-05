#!/usr/bin/env python3
"""
Tests for the models module
"""

import pytest
from datetime import datetime, timedelta
from models import Game, Odds, Order, Position, OrderStatus, OrderSide
from config.constants import Sport, Provider, BetType

class TestGame:
    """Test cases for Game model"""
    
    def test_game_creation(self):
        """Test basic game creation"""
        start_time = datetime.now() + timedelta(days=1)
        game = Game(
            game_id="test_001",
            sport=Sport.NFL,
            home_team="KC",
            away_team="BUF",
            start_time=start_time
        )
        
        assert game.game_id == "test_001"
        assert game.sport == Sport.NFL
        assert game.home_team == "KC"
        assert game.away_team == "BUF"
        assert game.start_time == start_time
        assert len(game.provider_ids) == 0
        assert len(game.odds) == 0
    
    def test_game_hash_and_equality(self):
        """Test game hashing and equality for deduplication"""
        start_time = datetime.now() + timedelta(days=1)
        
        game1 = Game(
            game_id="test_001",
            sport=Sport.NFL,
            home_team="KC",
            away_team="BUF",
            start_time=start_time
        )
        
        game2 = Game(
            game_id="test_002",  # Different ID
            sport=Sport.NFL,
            home_team="KC",
            away_team="BUF",
            start_time=start_time
        )
        
        # Should be equal despite different IDs
        assert game1 == game2
        assert hash(game1) == hash(game2)
    
    def test_game_provider_ids(self):
        """Test adding provider IDs"""
        game = Game(
            game_id="test_001",
            sport=Sport.NFL,
            home_team="KC",
            away_team="BUF",
            start_time=datetime.now()
        )
        
        game.add_provider_id(Provider.ODDS_API, "odds_123")
        game.add_provider_id(Provider.KALSHI, "kalshi_456")
        
        assert len(game.provider_ids) == 2
        assert game.provider_ids[Provider.ODDS_API] == "odds_123"
        assert game.provider_ids[Provider.KALSHI] == "kalshi_456"
    
    def test_game_time_until_start(self):
        """Test time until start calculation"""
        # Future game
        future_game = Game(
            game_id="future",
            sport=Sport.NFL,
            home_team="KC",
            away_team="BUF",
            start_time=datetime.now() + timedelta(hours=2, minutes=30)
        )
        
        time_until = future_game.time_until_start()
        assert "2h" in time_until
        assert "30m" in time_until
        
        # Past game
        past_game = Game(
            game_id="past",
            sport=Sport.NFL,
            home_team="KC",
            away_team="BUF",
            start_time=datetime.now() - timedelta(hours=1)
        )
        
        assert past_game.time_until_start() == "Started"

class TestOdds:
    """Test cases for Odds model"""
    
    def test_odds_creation(self):
        """Test basic odds creation"""
        odds = Odds(
            provider=Provider.ODDS_API,
            bet_type=BetType.MONEYLINE,
            timestamp=datetime.now(),
            home_ml=-110,
            away_ml=+100
        )
        
        assert odds.provider == Provider.ODDS_API
        assert odds.bet_type == BetType.MONEYLINE
        assert odds.home_ml == -110
        assert odds.away_ml == 100
    
    def test_odds_conversions(self):
        """Test odds conversion methods"""
        odds = Odds(
            provider=Provider.ODDS_API,
            bet_type=BetType.MONEYLINE,
            timestamp=datetime.now()
        )
        
        # Test decimal to American conversion
        assert odds.to_american_odds(2.0) == 100
        assert odds.to_american_odds(1.5) == -200
        
        # Test American to decimal conversion
        assert odds.to_decimal_odds(100) == 2.0
        assert abs(odds.to_decimal_odds(-200) - 1.5) < 0.01
        
        # Test implied probability
        assert abs(odds.to_implied_probability(100) - 0.5) < 0.01
        assert abs(odds.to_implied_probability(-200) - (2/3)) < 0.01
    
    def test_moneyline_favorite(self):
        """Test moneyline favorite detection"""
        odds = Odds(
            provider=Provider.ODDS_API,
            bet_type=BetType.MONEYLINE,
            timestamp=datetime.now(),
            home_ml=-150,  # Home favored
            away_ml=+130
        )
        
        assert odds.get_moneyline_favorite() == "home"
        
        # Switch favorites
        odds.home_ml = +120
        odds.away_ml = -140
        assert odds.get_moneyline_favorite() == "away"
    
    def test_spread_favorite(self):
        """Test spread favorite detection"""
        odds = Odds(
            provider=Provider.ODDS_API,
            bet_type=BetType.SPREAD,
            timestamp=datetime.now(),
            spread_line=3.5  # Home favored by 3.5
        )
        
        assert odds.get_spread_favorite() == "home"
        
        odds.spread_line = -2.5  # Away favored by 2.5
        assert odds.get_spread_favorite() == "away"

class TestOrder:
    """Test cases for Order model"""
    
    def test_order_creation(self):
        """Test basic order creation"""
        order = Order(
            order_id="order_001",
            provider=Provider.KALSHI,
            game_id="game_123",
            bet_type=BetType.MONEYLINE,
            side=OrderSide.BUY,
            quantity=10.0,
            price=0.55
        )
        
        assert order.order_id == "order_001"
        assert order.provider == Provider.KALSHI
        assert order.side == OrderSide.BUY
        assert order.quantity == 10.0
        assert order.price == 0.55
        assert order.status == OrderStatus.PENDING
        assert order.filled_quantity == 0.0
    
    def test_order_fill_updates(self):
        """Test order fill updates"""
        order = Order(
            order_id="order_001",
            provider=Provider.KALSHI,
            game_id="game_123",
            bet_type=BetType.MONEYLINE,
            side=OrderSide.BUY,
            quantity=100.0,
            price=0.50
        )
        
        # Partial fill
        order.update_fill(30.0, 0.52)
        assert order.filled_quantity == 30.0
        assert order.average_fill_price == 0.52
        assert order.status == OrderStatus.PARTIALLY_FILLED
        assert not order.is_fully_filled
        
        # Another partial fill
        order.update_fill(70.0, 0.48)
        assert order.filled_quantity == 100.0
        assert order.status == OrderStatus.FILLED
        assert order.is_fully_filled
        
        # Average fill price should be weighted
        expected_avg = (30.0 * 0.52 + 70.0 * 0.48) / 100.0
        assert abs(order.average_fill_price - expected_avg) < 0.001
    
    def test_order_cancellation(self):
        """Test order cancellation"""
        order = Order(
            order_id="order_001",
            provider=Provider.KALSHI,
            game_id="game_123",
            bet_type=BetType.MONEYLINE,
            side=OrderSide.BUY,
            quantity=100.0,
            price=0.50
        )
        
        order.cancel()
        assert order.status == OrderStatus.CANCELLED

class TestPosition:
    """Test cases for Position model"""
    
    def test_position_creation(self):
        """Test basic position creation"""
        position = Position(
            provider=Provider.KALSHI,
            game_id="game_123",
            bet_type=BetType.MONEYLINE,
            quantity=100.0,
            average_cost=0.50,
            current_price=0.55
        )
        
        assert position.quantity == 100.0
        assert position.average_cost == 0.50
        assert position.current_price == 0.55
    
    def test_position_pnl(self):
        """Test position P&L calculations"""
        # Long position
        long_position = Position(
            provider=Provider.KALSHI,
            game_id="game_123",
            bet_type=BetType.MONEYLINE,
            quantity=100.0,
            average_cost=0.50,
            current_price=0.60
        )
        
        assert long_position.total_cost == 50.0  # 100 * 0.50
        assert long_position.current_value == 60.0  # 100 * 0.60
        assert long_position.unrealized_pnl == 10.0  # (0.60 - 0.50) * 100
        assert long_position.unrealized_pnl_percentage == 20.0  # 10/50 * 100
        
        # Short position (negative quantity)
        short_position = Position(
            provider=Provider.KALSHI,
            game_id="game_123",
            bet_type=BetType.MONEYLINE,
            quantity=-100.0,
            average_cost=0.60,
            current_price=0.50
        )
        
        assert short_position.unrealized_pnl == 10.0  # (0.60 - 0.50) * 100

def run_tests():
    """Run all tests manually"""
    print("Running model tests...")
    
    # Run each test class
    test_classes = [TestGame, TestOdds, TestOrder, TestPosition]
    
    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"  ✅ {method_name}")
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
    
    print(f"\n✅ Model tests completed!")

if __name__ == "__main__":
    run_tests()