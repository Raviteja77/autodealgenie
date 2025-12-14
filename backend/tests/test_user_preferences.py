"""
Tests for user preferences schemas
"""

import pytest
from pydantic import ValidationError

from app.schemas.user_preferences import (
    BudgetRange,
    CarPreferences,
    CarType,
    FuelType,
    NotificationPreferences,
    SavedSearch,
    SavedSearchCreate,
    SearchPreferences,
    TransmissionType,
    UserPreferencesCreate,
    UserPreferencesUpdate,
)


class TestBudgetRange:
    """Tests for BudgetRange schema"""

    def test_valid_budget_range(self):
        """Test creating a valid budget range"""
        budget = BudgetRange(min=10000, max=30000)
        assert budget.min == 10000
        assert budget.max == 30000

    def test_negative_min_fails(self):
        """Test that negative min value fails validation"""
        with pytest.raises(ValidationError):
            BudgetRange(min=-1000, max=30000)

    def test_zero_max_fails(self):
        """Test that zero max value fails validation"""
        with pytest.raises(ValidationError):
            BudgetRange(min=10000, max=0)

    def test_max_less_than_min_fails(self):
        """Test that max less than min fails validation"""
        with pytest.raises(ValidationError):
            BudgetRange(min=30000, max=10000)

    def test_max_equal_to_min_fails(self):
        """Test that max equal to min fails validation"""
        with pytest.raises(ValidationError):
            BudgetRange(min=10000, max=10000)


class TestCarPreferences:
    """Tests for CarPreferences schema"""

    def test_empty_car_preferences(self):
        """Test creating empty car preferences"""
        prefs = CarPreferences()
        assert prefs.make is None
        assert prefs.model is None
        assert prefs.budget is None

    def test_full_car_preferences(self):
        """Test creating car preferences with all fields"""
        budget = BudgetRange(min=20000, max=40000)
        prefs = CarPreferences(
            make="Toyota",
            model="Camry",
            budget=budget,
            car_type=CarType.SEDAN,
            year_min=2020,
            year_max=2024,
            mileage_max=50000,
            fuel_type=FuelType.HYBRID,
            transmission=TransmissionType.AUTOMATIC,
            colors=["black", "white"],
            features=["sunroof", "leather"],
            priorities="Fuel efficiency and reliability",
        )
        assert prefs.make == "Toyota"
        assert prefs.model == "Camry"
        assert prefs.budget.min == 20000
        assert prefs.car_type == CarType.SEDAN

    def test_invalid_year_range_fails(self):
        """Test that invalid year range fails validation"""
        with pytest.raises(ValidationError):
            CarPreferences(year_min=2024, year_max=2020)

    def test_negative_mileage_fails(self):
        """Test that negative mileage fails validation"""
        with pytest.raises(ValidationError):
            CarPreferences(mileage_max=-1000)

    def test_year_out_of_range_fails(self):
        """Test that year out of range fails validation"""
        with pytest.raises(ValidationError):
            CarPreferences(year_min=1800)

    def test_priorities_too_long_fails(self):
        """Test that priorities exceeding max length fails validation"""
        with pytest.raises(ValidationError):
            CarPreferences(priorities="x" * 501)


class TestNotificationPreferences:
    """Tests for NotificationPreferences schema"""

    def test_default_notification_preferences(self):
        """Test default notification preferences"""
        prefs = NotificationPreferences()
        assert prefs.email_notifications is True
        assert prefs.deal_alerts is True
        assert prefs.price_drop_alerts is True
        assert prefs.new_inventory_alerts is False
        assert prefs.weekly_digest is False

    def test_custom_notification_preferences(self):
        """Test custom notification preferences"""
        prefs = NotificationPreferences(
            email_notifications=False,
            deal_alerts=False,
            price_drop_alerts=False,
            new_inventory_alerts=True,
            weekly_digest=True,
        )
        assert prefs.email_notifications is False
        assert prefs.new_inventory_alerts is True


class TestSearchPreferences:
    """Tests for SearchPreferences schema"""

    def test_default_search_preferences(self):
        """Test default search preferences"""
        prefs = SearchPreferences()
        assert prefs.default_location is None
        assert prefs.search_radius_miles is None
        assert prefs.auto_save_searches is True
        assert prefs.results_per_page == 10

    def test_custom_search_preferences(self):
        """Test custom search preferences"""
        prefs = SearchPreferences(
            default_location="New York, NY",
            search_radius_miles=50,
            auto_save_searches=False,
            results_per_page=25,
        )
        assert prefs.default_location == "New York, NY"
        assert prefs.search_radius_miles == 50
        assert prefs.results_per_page == 25

    def test_invalid_radius_fails(self):
        """Test that invalid radius fails validation"""
        with pytest.raises(ValidationError):
            SearchPreferences(search_radius_miles=0)
        with pytest.raises(ValidationError):
            SearchPreferences(search_radius_miles=501)

    def test_invalid_results_per_page_fails(self):
        """Test that invalid results per page fails validation"""
        with pytest.raises(ValidationError):
            SearchPreferences(results_per_page=4)
        with pytest.raises(ValidationError):
            SearchPreferences(results_per_page=101)


class TestUserPreferencesCreate:
    """Tests for UserPreferencesCreate schema"""

    def test_minimal_user_preferences(self):
        """Test creating minimal user preferences"""
        prefs = UserPreferencesCreate(user_id=1)
        assert prefs.user_id == 1
        assert prefs.car_preferences is not None
        assert prefs.notification_preferences is not None
        assert prefs.search_preferences is not None

    def test_full_user_preferences(self):
        """Test creating full user preferences"""
        car_prefs = CarPreferences(
            make="Honda", model="Accord", car_type=CarType.SEDAN, year_min=2020
        )
        notification_prefs = NotificationPreferences(email_notifications=False)
        search_prefs = SearchPreferences(default_location="Los Angeles, CA")

        prefs = UserPreferencesCreate(
            user_id=1,
            car_preferences=car_prefs,
            notification_preferences=notification_prefs,
            search_preferences=search_prefs,
        )
        assert prefs.user_id == 1
        assert prefs.car_preferences.make == "Honda"
        assert prefs.notification_preferences.email_notifications is False
        assert prefs.search_preferences.default_location == "Los Angeles, CA"

    def test_invalid_user_id_fails(self):
        """Test that invalid user_id fails validation"""
        with pytest.raises(ValidationError):
            UserPreferencesCreate(user_id=0)
        with pytest.raises(ValidationError):
            UserPreferencesCreate(user_id=-1)


class TestUserPreferencesUpdate:
    """Tests for UserPreferencesUpdate schema"""

    def test_empty_update(self):
        """Test creating empty update"""
        update = UserPreferencesUpdate()
        assert update.car_preferences is None
        assert update.notification_preferences is None
        assert update.search_preferences is None

    def test_partial_update(self):
        """Test partial update"""
        car_prefs = CarPreferences(make="Tesla", car_type=CarType.SEDAN)
        update = UserPreferencesUpdate(car_preferences=car_prefs)
        assert update.car_preferences.make == "Tesla"
        assert update.notification_preferences is None


class TestSavedSearch:
    """Tests for SavedSearch schemas"""

    def test_valid_saved_search(self):
        """Test creating a valid saved search"""
        criteria = CarPreferences(make="BMW", car_type=CarType.SEDAN)
        search = SavedSearch(name="My BMW Search", criteria=criteria, alert_enabled=True)
        assert search.name == "My BMW Search"
        assert search.criteria.make == "BMW"
        assert search.alert_enabled is True

    def test_saved_search_create(self):
        """Test creating SavedSearchCreate"""
        criteria = CarPreferences(make="Audi")
        search = SavedSearchCreate(
            name="Audi Search", criteria=criteria, alert_enabled=False, user_id=1
        )
        assert search.user_id == 1
        assert search.name == "Audi Search"

    def test_invalid_name_fails(self):
        """Test that invalid name fails validation"""
        criteria = CarPreferences(make="Ford")
        with pytest.raises(ValidationError):
            SavedSearch(name="", criteria=criteria)

    def test_invalid_user_id_fails(self):
        """Test that invalid user_id fails validation"""
        criteria = CarPreferences(make="Ford")
        with pytest.raises(ValidationError):
            SavedSearchCreate(name="Test", criteria=criteria, user_id=0)


class TestEnums:
    """Tests for enum types"""

    def test_car_type_enum(self):
        """Test CarType enum values"""
        assert CarType.SEDAN.value == "sedan"
        assert CarType.SUV.value == "suv"
        assert CarType.TRUCK.value == "truck"

    def test_fuel_type_enum(self):
        """Test FuelType enum values"""
        assert FuelType.GASOLINE.value == "gasoline"
        assert FuelType.ELECTRIC.value == "electric"
        assert FuelType.HYBRID.value == "hybrid"

    def test_transmission_type_enum(self):
        """Test TransmissionType enum values"""
        assert TransmissionType.AUTOMATIC.value == "automatic"
        assert TransmissionType.MANUAL.value == "manual"
        assert TransmissionType.CVT.value == "cvt"
