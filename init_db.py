"""
Database initialization script
Creates tables and optionally seeds test data
"""
import sys
from database import engine, SessionLocal, Base
from models import FriendRelationship, Graph

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def seed_test_data():
    """Seed database with test data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(FriendRelationship).first()
        if existing:
            print("⚠️  Test data already exists, skipping seed...")
            return
        
        print("Seeding test data...")
        
        test_relationships = [
            FriendRelationship(ens_name_1="nick.eth", ens_name_2="vitalik.eth"),
            FriendRelationship(ens_name_1="brantly.eth", ens_name_2="vitalik.eth"),
            FriendRelationship(ens_name_1="brantly.eth", ens_name_2="nick.eth"),
        ]
        
        db.add_all(test_relationships)
        db.commit()
        
        print("✅ Test data seeded successfully!")
        print(f"   Added {len(test_relationships)} relationships")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("ENS Network Graph - Database Initialization")
    print("=" * 50)
    
    init_database()
    
    # Check for auto-seed flag (for Docker)
    auto_seed = "--auto-seed" in sys.argv
    
    if auto_seed:
        print("\n🐳 Auto-seeding mode (Docker)")
        seed_test_data()
    else:
        # Ask if user wants to seed test data
        response = input("\nWould you like to seed test data? (y/n): ")
        if response.lower() == 'y':
            seed_test_data()
    
    print("\n" + "=" * 50)
    print("✅ Database setup complete!")
    print("=" * 50)

