from typing import Optional, List, Dict, Any
from app.services.database import get_db_service

class GroupService:
    """Service class for group-related database operations."""
    def __init__(self):
        self.db = get_db_service()

    def get_group_by_id(self, group_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM groups WHERE id = ?"
        return self.db.execute_single_query(query, (group_id,))

    def create_group(self, name: str, postcode: str, description: str = None) -> int:
        # Convert empty string to None
        if description == '':
            description = None
        query = "INSERT INTO groups (name, postcode, description) VALUES (?, ?, ?)"
        return self.db.execute_insert(query, (name, postcode, description))

    def create_group_with_creator(self, name: str, postcode: str, creator_user_id: int, description: str = None) -> int:
        """Create a group and add the creator in a single transaction."""
        # Convert empty string to None
        if description == '':
            description = None
        
        # First create the group
        group_id = self.db.execute_insert(
            "INSERT INTO groups (name, postcode, description) VALUES (?, ?, ?)",
            (name, postcode, description)
        )
        
        if group_id:
            # Then add the creator to the group
            try:
                self.db.execute_insert(
                    "INSERT INTO user_groups (user_id, group_id, status) VALUES (?, ?, 'creator')",
                    (creator_user_id, group_id)
                )
                return group_id
            except Exception as e:
                # If adding creator fails, delete the group to maintain consistency
                self.db.execute_delete("DELETE FROM groups WHERE id = ?", (group_id,))
                raise Exception(f"Failed to create group with creator: {e}")
        else:
            raise Exception("Failed to create group")

    def update_group(self, group_id: int, name: Optional[str] = None, postcode: Optional[str] = None) -> bool:
        update_fields = []
        params: list[Any] = []
        if name is not None:
            update_fields.append("name = ?")
            params.append(name)
        if postcode is not None:
            update_fields.append("postcode = ?")
            params.append(postcode)
        if not update_fields:
            return False
        params.append(group_id)
        query = f"UPDATE groups SET {', '.join(update_fields)} WHERE id = ?"
        return self.db.execute_update(query, tuple(params)) > 0

    def delete_group(self, group_id: int) -> bool:
        query = "DELETE FROM groups WHERE id = ?"
        return self.db.execute_delete(query, (group_id,)) > 0

    def get_all_groups(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM groups ORDER BY name"
        return self.db.execute_query(query)

    def search_groups(self, name: Optional[str] = None, postcode: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM groups"
        conditions = []
        params = []
        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        if postcode:
            conditions.append("postcode LIKE ?")
            params.append(f"%{postcode}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY name"
        return self.db.execute_query(query, tuple(params))

    def add_user_to_group(self, user_id: int, group_id: int, status: str = 'pending') -> bool:
        """Add user to group. Returns True if successful, False if user already exists in group."""
        try:
            query = "INSERT INTO user_groups (user_id, group_id, status) VALUES (?, ?, ?)"
            return self.db.execute_insert(query, (user_id, group_id, status)) > 0
        except Exception as e:
            # If it's a unique constraint violation, user already exists in group
            if "UNIQUE constraint failed" in str(e):
                return False
            raise e

    def update_user_group_status(self, user_id: int, group_id: int, status: str) -> bool:
        query = "UPDATE user_groups SET status = ? WHERE user_id = ? AND group_id = ?"
        return self.db.execute_update(query, (status, user_id, group_id)) > 0

    def remove_user_from_group(self, user_id: int, group_id: int) -> bool:
        query = "DELETE FROM user_groups WHERE user_id = ? AND group_id = ?"
        return self.db.execute_delete(query, (user_id, group_id)) > 0

    def get_user_group_membership(self, user_id: int, group_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM user_groups WHERE user_id = ? AND group_id = ?"
        return self.db.execute_single_query(query, (user_id, group_id))

    def get_group_members(self, group_id: int) -> List[Dict[str, Any]]:
        """Get all members of a group with their status"""
        query = """
            SELECT u.id, u.username, u.firstname, u.lastname, u.email, ug.status
            FROM user_groups ug
            JOIN users u ON ug.user_id = u.id
            WHERE ug.group_id = ? AND ug.status IN ('member', 'admin', 'creator')
            ORDER BY u.username
        """
        return self.db.execute_query(query, (group_id,))

    def get_user_groups(self, user_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT g.*, ug.status
            FROM groups g
            JOIN user_groups ug ON g.id = ug.group_id
            WHERE ug.user_id = ?
            ORDER BY g.name
        """
        return self.db.execute_query(query, (user_id,))

    def get_pending_requests(self, group_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT ug.id, ug.user_id, u.username, u.email
            FROM user_groups ug
            JOIN users u ON ug.user_id = u.id
            WHERE ug.group_id = ? AND ug.status = 'pending'
        """
        return self.db.execute_query(query, (group_id,))

    def handle_request(self, request_id: int, action: str) -> bool:
        # This would need to be implemented based on your join_requests table if used
        return False

    def get_user_groups_with_stats(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get user's groups with member count statistics"""
        query = """
            SELECT g.*, 
                   (SELECT COUNT(*) FROM user_groups WHERE group_id = g.id AND status != 'pending') as member_count,
                   ug.status
            FROM groups g
            JOIN user_groups ug ON g.id = ug.group_id
            WHERE ug.user_id = ? AND ug.status != 'pending'
            ORDER BY g.name
            LIMIT ?
        """
        return self.db.execute_query(query, (user_id, limit))
    
    def add_user_tradesmen_to_group(self, user_id: int, group_id: int) -> int:
        """Add all tradesmen from a user to a group. Returns the number of tradesmen added."""
        # Get all tradesmen associated with the user
        query = """
            SELECT t.id FROM tradesmen t
            JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            WHERE ut.user_id = ?
        """
        user_tradesmen = self.db.execute_query(query, (user_id,))
        
        added_count = 0
        for tradesman in user_tradesmen:
            # Add each tradesman to the group (using INSERT OR IGNORE to avoid duplicates)
            insert_query = """
                INSERT OR IGNORE INTO group_tradesmen (group_id, tradesman_id)
                VALUES (?, ?)
            """
            if self.db.execute_insert(insert_query, (group_id, tradesman['id'])) > 0:
                added_count += 1
        
        return added_count
    
    def get_request_by_id(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Get a join request by its ID."""
        query = "SELECT * FROM user_groups WHERE id = ?"
        return self.db.execute_single_query(query, (request_id,))
    
    def get_group_creator(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get the creator of a group."""
        query = """
            SELECT u.id, u.username, u.firstname, u.lastname, u.email
            FROM user_groups ug
            JOIN users u ON ug.user_id = u.id
            WHERE ug.group_id = ? AND ug.status = 'creator'
        """
        return self.db.execute_single_query(query, (group_id,))
    
    def get_group_job_count(self, group_id: int) -> int:
        """Get the number of jobs entered by users who have tradesmen in this group."""
        query = """
            SELECT COUNT(DISTINCT j.id) as count 
            FROM jobs j
            JOIN users u ON j.user_id = u.id
            JOIN user_groups ug ON u.id = ug.user_id
            JOIN group_tradesmen gt ON ug.group_id = gt.group_id
            WHERE ug.group_id = ? AND ug.status IN ('member', 'admin', 'creator')
        """
        result = self.db.execute_single_query(query, (group_id,))
        return result['count'] if result else 0
    
    def get_group_member_count(self, group_id: int) -> int:
        """Get the number of members in a group (excluding pending requests)."""
        query = """
            SELECT COUNT(*) as count 
            FROM user_groups 
            WHERE group_id = ? AND status IN ('member', 'admin', 'creator')
        """
        result = self.db.execute_single_query(query, (group_id,))
        return result['count'] if result else 0
    
    def get_all_pending_requests_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all pending requests for groups where user is admin/creator."""
        query = """
            SELECT g.name as group_name, g.id as group_id, u.username, u.email, ug.id as request_id
            FROM user_groups ug1
            JOIN user_groups ug ON ug1.group_id = ug.group_id
            JOIN groups g ON ug.group_id = g.id
            JOIN users u ON ug.user_id = u.id
            WHERE ug1.user_id = ? 
            AND ug1.status IN ('admin', 'creator')
            AND ug.status = 'pending'
            ORDER BY g.name, u.username
        """
        return self.db.execute_query(query, (user_id,)) 

    def get_group_names(self) -> List[str]:
        """Get all group names."""
        query = "SELECT name FROM groups ORDER BY name"
        results = self.db.execute_query(query)
        return [row['name'] for row in results] 