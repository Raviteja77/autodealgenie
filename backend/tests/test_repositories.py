"""Tests for repository pattern implementations"""

from app.repositories.deal_repository import DealRepository
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import DealCreate, DealUpdate, UserCreate


class TestUserRepository:
    """Test UserRepository methods"""

    def test_create_user(self, db):
        """Test creating a user"""
        repo = UserRepository(db)
        user_in = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            full_name="Test User",
        )

        user = repo.create(user_in)
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.hashed_password != "testpass123"  # Should be hashed

    def test_get_by_email(self, db):
        """Test getting user by email"""
        repo = UserRepository(db)
        user_in = UserCreate(email="test@example.com", username="testuser", password="testpass123")

        created_user = repo.create(user_in)
        found_user = repo.get_by_email("test@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email

    def test_get_by_email_not_found(self, db):
        """Test getting user by non-existent email"""
        repo = UserRepository(db)
        user = repo.get_by_email("nonexistent@example.com")
        assert user is None

    def test_get_by_username(self, db):
        """Test getting user by username"""
        repo = UserRepository(db)
        user_in = UserCreate(email="test@example.com", username="testuser", password="testpass123")

        created_user = repo.create(user_in)
        found_user = repo.get_by_username("testuser")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == created_user.username

    def test_get_by_username_not_found(self, db):
        """Test getting user by non-existent username"""
        repo = UserRepository(db)
        user = repo.get_by_username("nonexistent")
        assert user is None

    def test_get_by_id(self, db):
        """Test getting user by ID"""
        repo = UserRepository(db)
        user_in = UserCreate(email="test@example.com", username="testuser", password="testpass123")

        created_user = repo.create(user_in)
        found_user = repo.get_by_id(created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id

    def test_get_by_id_not_found(self, db):
        """Test getting user by non-existent ID"""
        repo = UserRepository(db)
        user = repo.get_by_id(99999)
        assert user is None

    def test_authenticate_success(self, db):
        """Test successful authentication"""
        repo = UserRepository(db)
        user_in = UserCreate(email="test@example.com", username="testuser", password="testpass123")

        repo.create(user_in)
        authenticated_user = repo.authenticate("test@example.com", "testpass123")

        assert authenticated_user is not None
        assert authenticated_user.email == "test@example.com"

    def test_authenticate_wrong_password(self, db):
        """Test authentication with wrong password"""
        repo = UserRepository(db)
        user_in = UserCreate(email="test@example.com", username="testuser", password="testpass123")

        repo.create(user_in)
        authenticated_user = repo.authenticate("test@example.com", "wrongpassword")

        assert authenticated_user is None

    def test_authenticate_nonexistent_user(self, db):
        """Test authentication with non-existent user"""
        repo = UserRepository(db)
        authenticated_user = repo.authenticate("nonexistent@example.com", "testpass123")
        assert authenticated_user is None

    def test_authenticate_inactive_user(self, db):
        """Test authentication with inactive user"""
        repo = UserRepository(db)
        user_in = UserCreate(email="test@example.com", username="testuser", password="testpass123")

        user = repo.create(user_in)
        # Manually set user as inactive
        user.is_active = False
        db.commit()

        authenticated_user = repo.authenticate("test@example.com", "testpass123")
        assert authenticated_user is None


class TestDealRepository:
    """Test DealRepository methods"""

    def test_create_deal(self, db):
        """Test creating a deal"""
        repo = DealRepository(db)
        deal_in = DealCreate(
            customer_name="John Doe",
            customer_email="john@example.com",
            vehicle_make="Toyota",
            vehicle_model="Camry",
            vehicle_year=2022,
            vehicle_mileage=15000,
            asking_price=25000.00,
            status="pending",
        )

        deal = repo.create(deal_in)
        assert deal.id is not None
        assert deal.customer_name == "John Doe"
        assert deal.vehicle_make == "Toyota"

    def test_get_deal(self, db):
        """Test getting a deal by ID"""
        repo = DealRepository(db)
        deal_in = DealCreate(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            vehicle_make="Honda",
            vehicle_model="Accord",
            vehicle_year=2021,
            vehicle_mileage=20000,
            asking_price=23000.00,
            status="pending",
        )

        created_deal = repo.create(deal_in)
        found_deal = repo.get(created_deal.id)

        assert found_deal is not None
        assert found_deal.id == created_deal.id
        assert found_deal.customer_name == created_deal.customer_name

    def test_get_deal_not_found(self, db):
        """Test getting a non-existent deal"""
        repo = DealRepository(db)
        deal = repo.get(99999)
        assert deal is None

    def test_get_all_deals(self, db):
        """Test getting all deals with pagination"""
        repo = DealRepository(db)

        # Create multiple deals
        for i in range(5):
            deal_in = DealCreate(
                customer_name=f"Customer {i}",
                customer_email=f"customer{i}@example.com",
                vehicle_make="Toyota",
                vehicle_model="Camry",
                vehicle_year=2022,
                vehicle_mileage=15000,
                asking_price=25000.00,
                status="pending",
            )
            repo.create(deal_in)

        deals = repo.get_all(skip=0, limit=10)
        assert len(deals) == 5

    def test_get_all_deals_pagination(self, db):
        """Test pagination in get_all"""
        repo = DealRepository(db)

        # Create multiple deals
        for i in range(5):
            deal_in = DealCreate(
                customer_name=f"Customer {i}",
                customer_email=f"customer{i}@example.com",
                vehicle_make="Toyota",
                vehicle_model="Camry",
                vehicle_year=2022,
                vehicle_mileage=15000,
                asking_price=25000.00,
                status="pending",
            )
            repo.create(deal_in)

        # Get first 3
        deals = repo.get_all(skip=0, limit=3)
        assert len(deals) == 3

        # Get next 2
        deals = repo.get_all(skip=3, limit=3)
        assert len(deals) == 2

    def test_get_by_status(self, db):
        """Test getting deals by status"""
        repo = DealRepository(db)

        # Create deals with different statuses
        for status in ["pending", "in_progress", "completed"]:
            deal_in = DealCreate(
                customer_name="Customer",
                customer_email="customer@example.com",
                vehicle_make="Toyota",
                vehicle_model="Camry",
                vehicle_year=2022,
                vehicle_mileage=15000,
                asking_price=25000.00,
                status=status,
            )
            repo.create(deal_in)

        pending_deals = repo.get_by_status("pending")
        assert len(pending_deals) == 1
        assert pending_deals[0].status == "pending"

    def test_get_by_email(self, db):
        """Test getting deals by customer email"""
        repo = DealRepository(db)

        email = "customer@example.com"

        # Create multiple deals for same customer
        for i in range(3):
            deal_in = DealCreate(
                customer_name="Customer",
                customer_email=email,
                vehicle_make="Toyota",
                vehicle_model=f"Model {i}",
                vehicle_year=2022,
                vehicle_mileage=15000,
                asking_price=25000.00,
                status="pending",
            )
            repo.create(deal_in)

        deals = repo.get_by_email(email)
        assert len(deals) == 3
        assert all(deal.customer_email == email for deal in deals)

    def test_update_deal(self, db):
        """Test updating a deal"""
        repo = DealRepository(db)
        deal_in = DealCreate(
            customer_name="John Doe",
            customer_email="john@example.com",
            vehicle_make="Toyota",
            vehicle_model="Camry",
            vehicle_year=2022,
            vehicle_mileage=15000,
            asking_price=25000.00,
            status="pending",
        )

        deal = repo.create(deal_in)

        # Update the deal
        update_data = DealUpdate(status="in_progress", offer_price=24000.00, notes="Negotiating")

        updated_deal = repo.update(deal.id, update_data)

        assert updated_deal is not None
        assert updated_deal.id == deal.id
        assert updated_deal.status == "in_progress"
        assert updated_deal.offer_price == 24000.00
        assert updated_deal.notes == "Negotiating"

    def test_update_nonexistent_deal(self, db):
        """Test updating a non-existent deal"""
        repo = DealRepository(db)
        update_data = DealUpdate(status="completed")

        updated_deal = repo.update(99999, update_data)
        assert updated_deal is None

    def test_delete_deal(self, db):
        """Test deleting a deal"""
        repo = DealRepository(db)
        deal_in = DealCreate(
            customer_name="John Doe",
            customer_email="john@example.com",
            vehicle_make="Toyota",
            vehicle_model="Camry",
            vehicle_year=2022,
            vehicle_mileage=15000,
            asking_price=25000.00,
            status="pending",
        )

        deal = repo.create(deal_in)
        result = repo.delete(deal.id)

        assert result is True
        assert repo.get(deal.id) is None

    def test_delete_nonexistent_deal(self, db):
        """Test deleting a non-existent deal"""
        repo = DealRepository(db)
        result = repo.delete(99999)
        assert result is False
