import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.category import ProductCategory
from app.models.rule import ComplianceRule, RuleCategoryMapping
from app.models.product import Product, ExtractedDeclaration
from app.models.report import ComplianceReport, ViolationDetail

# In-memory SQLite for fast, isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token_headers(test_user):
    token = create_access_token(test_user.id, roles=test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token_headers(admin_user):
    token = create_access_token(admin_user.id, roles=admin_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_category(db):
    cat = ProductCategory(
        name="Electronics & Electricals",
        description="Consumer electrical and electronic appliances"
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@pytest.fixture
def sample_rule(db, sample_category):
    rule = ComplianceRule(
        rule_code="LM-ELEC-01",
        declaration_name="Part Number",
        description="Mandatory part number for electronic items",
        mandatory_fields="Part Number, Part No, P/N, Model Number",
        enforcement_level="strict",
        legal_reference="Legal Metrology (Packaged Commodities) Amendment Rules, 2022"
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    mapping = RuleCategoryMapping(
        category_id=sample_category.id,
        rule_id=rule.id,
        is_required=True
    )
    db.add(mapping)
    db.commit()
    return rule


@pytest.fixture
def sample_product(db):
    product = Product(
        title="Wireless Bluetooth Headphones",
        url="https://www.example.com/dp/B08X123456",
        domain="example.com",
        image_urls=["https://www.example.com/img1.jpg"]
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
