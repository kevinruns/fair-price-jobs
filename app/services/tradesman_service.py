from typing import Optional, List, Dict, Any
from app.services.database import get_db_service

class TradesmanService:
    """Service class for tradesman-related database operations."""
    
    def __init__(self):
        self.db = get_db_service()
    
    def get_tradesman_by_id(self, tradesman_id: int) -> Optional[Dict[str, Any]]:
        """Get tradesman by ID with added_by information"""
        query = """
            SELECT t.*, u.username as added_by_username, u.id as added_by_user_id
            FROM tradesmen t
            LEFT JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            LEFT JOIN users u ON ut.user_id = u.id
            WHERE t.id = ?
        """
        result = self.db.execute_single_query(query, (tradesman_id,))
        return result
    
    def create_tradesman(self, trade: str, first_name: str, family_name: str,
                        company_name: str, address: str, postcode: str,
                        phone_number: str, email: str) -> int:
        """Create a new tradesman and return the tradesman ID."""
        query = """
            INSERT INTO tradesmen (
                trade, first_name, family_name, company_name, 
                address, postcode, phone_number, email
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_insert(query, (
            trade, first_name, family_name, company_name,
            address, postcode, phone_number, email
        ))
    
    def update_tradesman(self, tradesman_id: int, **kwargs) -> bool:
        """Update tradesman information."""
        allowed_fields = ['trade', 'first_name', 'family_name', 'company_name',
                         'address', 'postcode', 'phone_number', 'email']
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(tradesman_id)
        query = f"UPDATE tradesmen SET {', '.join(update_fields)} WHERE id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def delete_tradesman(self, tradesman_id: int) -> bool:
        """Delete a tradesman."""
        query = "DELETE FROM tradesmen WHERE id = ?"
        return self.db.execute_delete(query, (tradesman_id,)) > 0
    
    def search_tradesmen(self, search_term: str = None, trade: str = None, 
                        postcode: str = None) -> List[Dict[str, Any]]:
        """Search for tradesmen with filters"""
        query = """
            SELECT DISTINCT t.*, 
                   COUNT(j.id) as job_count,
                   AVG(j.rating) as avg_rating,
                   u.username as added_by_username,
                   u.id as added_by_user_id
            FROM tradesmen t
            LEFT JOIN jobs j ON t.id = j.tradesman_id
            JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            JOIN users u ON ut.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (t.first_name LIKE ? OR t.family_name LIKE ? OR t.company_name LIKE ? OR t.email LIKE ? OR t.phone_number LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])
            
        if trade:
            query += " AND t.trade = ?"
            params.append(trade)
            
        if postcode:
            query += " AND t.postcode LIKE ?"
            params.append(f"{postcode}%")
            
        query += " GROUP BY t.id ORDER BY COUNT(j.id) DESC, avg_rating DESC NULLS LAST"
        
        return self.db.execute_query(query, params)
    
    def get_tradesman_jobs(self, tradesman_id: int) -> List[Dict[str, Any]]:
        """Get all jobs for a tradesman."""
        query = """
            SELECT id, date_started, date_finished, title, description, 
                   total_cost, rating
            FROM jobs
            WHERE tradesman_id = ? AND type = 'job'
            ORDER BY date_finished DESC
        """
        return self.db.execute_query(query, (tradesman_id,))
    
    def get_tradesman_quotes(self, tradesman_id: int) -> List[Dict[str, Any]]:
        """Get all quotes for a tradesman (excluding accepted ones)."""
        query = """
            SELECT id, date_requested, date_received, title, description, 
                   total_quote, status
            FROM jobs
            WHERE tradesman_id = ? AND type = 'quote' AND status != 'accepted'
            ORDER BY date_received DESC
        """
        return self.db.execute_query(query, (tradesman_id,))
    
    def add_user_tradesman_relationship(self, user_id: int, tradesman_id: int) -> bool:
        """Add a relationship between a user and a tradesman."""
        query = """
            INSERT OR IGNORE INTO user_tradesmen (user_id, tradesman_id)
            VALUES (?, ?)
        """
        return self.db.execute_insert(query, (user_id, tradesman_id)) > 0
    
    def remove_user_tradesman_relationship(self, user_id: int, tradesman_id: int) -> bool:
        """Remove a relationship between a user and a tradesman."""
        query = "DELETE FROM user_tradesmen WHERE user_id = ? AND tradesman_id = ?"
        return self.db.execute_delete(query, (user_id, tradesman_id)) > 0
    
    def get_tradesman_added_by_info(self, tradesman_id: int) -> Optional[Dict[str, Any]]:
        """Get information about who added the tradesman."""
        query = """
            SELECT DATE(ut.date_added) as date_added, u.username, u.firstname, u.lastname
            FROM user_tradesmen ut
            JOIN users u ON ut.user_id = u.id
            WHERE ut.tradesman_id = ?
            ORDER BY ut.date_added ASC
            LIMIT 1
        """
        return self.db.execute_single_query(query, (tradesman_id,))
    
    def can_user_edit_tradesman(self, user_id: int, tradesman_id: int) -> bool:
        """Check if a user can edit a tradesman."""
        query = """
            SELECT 1 FROM user_tradesmen 
            WHERE user_id = ? AND tradesman_id = ?
        """
        result = self.db.execute_single_query(query, (user_id, tradesman_id))
        return result is not None
    
    def get_tradesmen_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all tradesmen associated with a specific user."""
        query = """
            SELECT t.*, 
                   COUNT(j.id) as job_count,
                   AVG(j.rating) as avg_rating,
                   ut.date_added
            FROM tradesmen t
            JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            LEFT JOIN jobs j ON t.id = j.tradesman_id
            WHERE ut.user_id = ?
            GROUP BY t.id
            ORDER BY t.trade, t.family_name, t.first_name, t.company_name
        """
        return self.db.execute_query(query, (user_id,))
    
    def get_tradesmen_by_group(self, group_id: int) -> List[Dict[str, Any]]:
        """Get all tradesmen in a specific group."""
        query = """
            SELECT t.*
            FROM tradesmen t
            JOIN group_tradesmen gt ON t.id = gt.tradesman_id
            WHERE gt.group_id = ?
            ORDER BY t.trade, t.family_name, t.first_name, t.company_name
        """
        return self.db.execute_query(query, (group_id,))
    
    def add_tradesman_to_group(self, group_id: int, tradesman_id: int) -> bool:
        """Add a tradesman to a group."""
        query = """
            INSERT OR IGNORE INTO group_tradesmen (group_id, tradesman_id)
            VALUES (?, ?)
        """
        return self.db.execute_insert(query, (group_id, tradesman_id)) > 0
    
    def remove_tradesman_from_group(self, group_id: int, tradesman_id: int) -> bool:
        """Remove a tradesman from a group."""
        query = "DELETE FROM group_tradesmen WHERE group_id = ? AND tradesman_id = ?"
        return self.db.execute_delete(query, (group_id, tradesman_id)) > 0
    
    def is_tradesman_in_group(self, group_id: int, tradesman_id: int) -> bool:
        """Check if a tradesman is in a specific group."""
        query = """
            SELECT 1 FROM group_tradesmen 
            WHERE group_id = ? AND tradesman_id = ?
        """
        result = self.db.execute_single_query(query, (group_id, tradesman_id))
        return result is not None
    
    def get_unique_trades(self):
        """Get all unique trades for filtering"""
        query = "SELECT DISTINCT trade FROM tradesmen ORDER BY trade"
        results = self.db.execute_query(query)
        return [row['trade'] for row in results]
    
    def get_top_rated_tradesmen_for_user(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top-rated tradesmen accessible to user through groups or direct ownership"""
        query = """
            SELECT t.*, 
                   COUNT(CASE WHEN j.type = 'job' THEN j.id END) as job_count,
                   AVG(CASE WHEN j.type = 'job' THEN j.rating END) as avg_rating,
                   u.username as added_by_username,
                   u.id as added_by_user_id,
                   CASE WHEN ut.user_id = ? THEN 1 ELSE 0 END as is_my_tradesman
            FROM tradesmen t
            JOIN user_tradesmen ut ON t.id = ut.tradesman_id
            LEFT JOIN jobs j ON t.id = j.tradesman_id
            JOIN users u ON ut.user_id = u.id
            WHERE ut.user_id = ? OR ut.user_id IN (
                SELECT DISTINCT ug2.user_id 
                FROM user_groups ug1
                JOIN user_groups ug2 ON ug1.group_id = ug2.group_id
                WHERE ug1.user_id = ? AND ug1.status IN ('member', 'admin', 'creator')
            )
            GROUP BY t.id
            ORDER BY AVG(CASE WHEN j.type = 'job' THEN j.rating END) DESC NULLS LAST, COUNT(CASE WHEN j.type = 'job' THEN j.id END) DESC
            LIMIT ?
        """
        return self.db.execute_query(query, (user_id, user_id, user_id, limit)) 