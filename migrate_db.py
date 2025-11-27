"""
Database Migration Script for Graph Feature

This script migrates the existing database to support the new graph management feature.
It will:
1. Create the new 'graphs' table
2. Add the 'graph_id' column to 'friend_relationships' table
3. Update the unique constraint to include graph_id

Run this script after updating your models to migrate existing data.
"""

from sqlalchemy import text
from database import engine, get_db
from models import Base, Graph, FriendRelationship
import sys


def migrate_database():
    """Run database migration"""
    print("Starting database migration...")
    
    try:
        with engine.begin() as conn:
            # Check if migration is needed
            print("\n1. Checking current database schema...")
            
            # Check if graphs table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'graphs'
                );
            """))
            graphs_exists = result.scalar()
            
            if graphs_exists:
                print("✓ Graphs table already exists")
            else:
                print("✗ Graphs table does not exist - will be created")
            
            # Check if graph_id column exists in friend_relationships
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'friend_relationships' 
                    AND column_name = 'graph_id'
                );
            """))
            graph_id_exists = result.scalar()
            
            if graph_id_exists:
                print("✓ graph_id column already exists in friend_relationships")
            else:
                print("✗ graph_id column does not exist - will be added")
            
            # If no migration needed
            if graphs_exists and graph_id_exists:
                print("\n✓ Database is already up to date!")
                return
            
            print("\n2. Starting migration...")
            
            # Drop old unique constraint if it exists
            if not graph_id_exists:
                print("   Dropping old unique constraint...")
                try:
                    conn.execute(text("""
                        ALTER TABLE friend_relationships 
                        DROP CONSTRAINT IF EXISTS unique_relationship;
                    """))
                    print("   ✓ Old constraint dropped")
                except Exception as e:
                    print(f"   Note: {str(e)}")
            
            # Create all tables (will create graphs if needed and update friend_relationships)
            print("   Creating/updating tables...")
            Base.metadata.create_all(bind=engine)
            print("   ✓ Tables created/updated")
            
            # Add graph_id column if it doesn't exist
            if not graph_id_exists:
                print("   Adding graph_id column to friend_relationships...")
                conn.execute(text("""
                    ALTER TABLE friend_relationships 
                    ADD COLUMN IF NOT EXISTS graph_id INTEGER REFERENCES graphs(id) ON DELETE CASCADE;
                """))
                
                # Create index
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_graph_id ON friend_relationships(graph_id);
                """))
                print("   ✓ graph_id column added")
            
            # Update unique constraint to include graph_id
            print("   Updating unique constraint...")
            try:
                conn.execute(text("""
                    ALTER TABLE friend_relationships 
                    DROP CONSTRAINT IF EXISTS unique_relationship_per_graph;
                """))
                conn.execute(text("""
                    ALTER TABLE friend_relationships 
                    ADD CONSTRAINT unique_relationship_per_graph 
                    UNIQUE (ens_name_1, ens_name_2, graph_id);
                """))
                print("   ✓ Unique constraint updated")
            except Exception as e:
                print(f"   Warning: Could not update constraint: {str(e)}")
            
            print("\n3. Migration completed successfully!")
            print("\nNotes:")
            print("- Existing relationships will have graph_id = NULL (orphaned)")
            print("- You can optionally create a default graph and assign them")
            print("- New relationships should be created within graphs")
            
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure the database is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Ensure you have proper database permissions")
        sys.exit(1)


def create_default_graph():
    """Optional: Create a default graph and assign orphaned relationships"""
    print("\n" + "="*60)
    print("Creating default graph for existing relationships...")
    print("="*60)
    
    try:
        db = next(get_db())
        
        # Check if there are orphaned relationships
        orphaned = db.query(FriendRelationship).filter(
            FriendRelationship.graph_id == None
        ).count()
        
        if orphaned == 0:
            print("✓ No orphaned relationships found")
            return
        
        print(f"Found {orphaned} orphaned relationship(s)")
        
        # Create default graph
        default_graph = Graph(
            name="Default Graph",
            description="Automatically created for existing relationships"
        )
        db.add(default_graph)
        db.commit()
        db.refresh(default_graph)
        
        print(f"✓ Created default graph (id: {default_graph.id})")
        
        # Assign orphaned relationships to default graph
        db.query(FriendRelationship).filter(
            FriendRelationship.graph_id == None
        ).update({"graph_id": default_graph.id})
        
        db.commit()
        print(f"✓ Assigned {orphaned} relationship(s) to default graph")
        
    except Exception as e:
        print(f"✗ Failed to create default graph: {str(e)}")
        db.rollback()


if __name__ == "__main__":
    print("="*60)
    print("ENS Network Graph - Database Migration")
    print("="*60)
    
    # Check for auto-migrate flag (for Docker)
    auto_migrate = "--auto-migrate" in sys.argv
    
    migrate_database()
    
    if auto_migrate:
        print("\n🐳 Auto-migrate mode (Docker)")
        create_default_graph()
    else:
        # Ask if user wants to create default graph
        response = input("\nDo you want to create a default graph for existing relationships? (y/n): ")
        if response.lower() in ['y', 'yes']:
            create_default_graph()
    
    print("\n" + "="*60)
    print("Migration process complete!")
    print("="*60)

