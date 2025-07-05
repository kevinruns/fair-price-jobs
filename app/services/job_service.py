from typing import Optional, List, Dict, Any
from app.services.database import get_db_service

class JobService:
    """Service class for job and quote-related database operations."""
    
    def __init__(self):
        self.db = get_db_service()
    
    def get_job_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get job by ID with related information."""
        query = """
            SELECT j.*, 
                   t.first_name, t.family_name, t.company_name, t.trade,
                   u.username as added_by_username,
                   u.id as added_by_user_id
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            JOIN users u ON j.user_id = u.id
            WHERE j.id = ?
        """
        return self.db.execute_single_query(query, (job_id,))
    
    def create_job(self, user_id: int, tradesman_id: int, title: str, description: str,
                   date_started: str = None, date_finished: str = None,
                   call_out_fee: int = None, materials_fee: int = None,
                   hourly_rate: int = None, hours_worked: float = None,
                   daily_rate: int = None, days_worked: float = None,
                   total_cost: int = None, rating: int = None) -> int:
        """Create a new job and return the job ID."""
        query = """
            INSERT INTO jobs (
                user_id, tradesman_id, type, title, description,
                date_started, date_finished, date_requested, date_received,
                call_out_fee, materials_fee, hourly_rate, hours_worked,
                hours_estimated, daily_rate, days_worked, days_estimated,
                total_cost, total_quote, rating, status
            )
            VALUES (?, ?, 'job', ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, NULL, ?, ?, NULL, ?, NULL, ?, 'accepted')
        """
        return self.db.execute_insert(query, (
            user_id, tradesman_id, title, description,
            date_started, date_finished, call_out_fee, materials_fee,
            hourly_rate, hours_worked, daily_rate, days_worked,
            total_cost, rating
        ))
    
    def create_quote(self, user_id: int, tradesman_id: int, title: str, description: str,
                     date_requested: str = None, date_received: str = None,
                     call_out_fee: int = None, materials_fee: int = None,
                     hourly_rate: int = None, hours_estimated: float = None,
                     daily_rate: int = None, days_estimated: float = None,
                     total_quote: int = None) -> int:
        """Create a new quote and return the quote ID."""
        query = """
            INSERT INTO jobs (
                user_id, tradesman_id, type, title, description,
                date_requested, date_received, call_out_fee, materials_fee,
                hourly_rate, hours_estimated, daily_rate, days_estimated,
                total_quote
            )
            VALUES (?, ?, 'quote', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_insert(query, (
            user_id, tradesman_id, title, description,
            date_requested, date_received, call_out_fee, materials_fee,
            hourly_rate, hours_estimated, daily_rate, days_estimated,
            total_quote
        ))
    
    def update_job(self, job_id: int, **kwargs) -> bool:
        """Update job information."""
        allowed_fields = [
            'title', 'description', 'date_started', 'date_finished',
            'call_out_fee', 'materials_fee', 'hourly_rate', 'hours_worked',
            'daily_rate', 'days_worked', 'total_cost', 'rating'
        ]
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(job_id)
        query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def update_quote(self, quote_id: int, **kwargs) -> bool:
        """Update quote information."""
        allowed_fields = [
            'title', 'description', 'date_requested', 'date_received',
            'call_out_fee', 'materials_fee', 'hourly_rate', 'hours_estimated',
            'daily_rate', 'days_estimated', 'total_quote', 'status'
        ]
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(quote_id)
        query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job or quote."""
        query = "DELETE FROM jobs WHERE id = ?"
        return self.db.execute_delete(query, (job_id,)) > 0
    
    def get_jobs_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all jobs created by a user."""
        query = """
            SELECT j.*, t.first_name, t.family_name, t.trade
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            WHERE j.user_id = ? AND j.type = 'job'
            ORDER BY j.date_started DESC
        """
        return self.db.execute_query(query, (user_id,))
    
    def get_quotes_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all quotes created by a user."""
        query = """
            SELECT j.*, t.first_name, t.family_name, t.trade
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            WHERE j.user_id = ? AND j.type = 'quote'
            ORDER BY j.date_requested DESC
        """
        return self.db.execute_query(query, (user_id,))
    
    def search_jobs(self, search_term=None, trade=None, rating=None, added_by_user=None, group=None):
        """Search for jobs with filters"""
        query = """
            SELECT j.*, 
                   t.first_name, t.family_name, t.company_name, t.trade,
                   u.username as added_by_username,
                   u.id as added_by_user_id
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            JOIN users u ON j.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (j.title LIKE ? OR j.description LIKE ?)"
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern])
            
        if trade:
            query += " AND t.trade = ?"
            params.append(trade)
            
        if rating:
            query += " AND j.rating >= ?"
            params.append(str(rating))
            
        if added_by_user:
            query += " AND u.username = ?"
            params.append(added_by_user)
            
        if group:
            query += """ AND EXISTS (
                SELECT 1 FROM group_tradesmen gt 
                JOIN groups g ON gt.group_id = g.id 
                WHERE gt.tradesman_id = t.id AND g.name = ?
            )"""
            params.append(group)
            
        query += " ORDER BY j.date_finished DESC NULLS LAST"
        
        return self.db.execute_query(query, tuple(params))
    
    def search_quotes(self, search_term: str = None, trade: str = None,
                     postcode: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Search quotes with optional filters."""
        query = """
            SELECT j.*, t.first_name, t.family_name, t.trade,
                   u.username as added_by_username, u.firstname, u.lastname
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            JOIN users u ON j.user_id = u.id
            WHERE j.type = 'quote'
        """
        
        conditions = []
        params = []
        
        if search_term:
            conditions.append("""
                (j.title LIKE ? OR j.description LIKE ? OR 
                 t.first_name LIKE ? OR t.family_name LIKE ? OR t.trade LIKE ?)
            """)
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern] * 5)
        
        if trade:
            conditions.append("t.trade = ?")
            params.append(trade)
        
        if postcode:
            conditions.append("t.postcode LIKE ?")
            params.append(f"%{postcode}%")
        
        if status:
            conditions.append("j.status = ?")
            params.append(status)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY j.date_requested DESC"
        
        return self.db.execute_query(query, tuple(params))
    
    def convert_quote_to_job(self, quote_id: int) -> bool:
        """Convert a quote to a job."""
        # First get the quote details
        quote = self.get_job_by_id(quote_id)
        if not quote or quote['type'] != 'quote':
            return False
        
        try:
            # Update the quote to be a job
            self.update_job(quote_id, 
                           date_started=quote.get('date_requested'),
                           total_cost=quote.get('total_quote'))
            
            # Update the type from 'quote' to 'job'
            query = "UPDATE jobs SET type = 'job', status = 'accepted' WHERE id = ?"
            return self.db.execute_update(query, (quote_id,)) > 0
        except Exception:
            return False
    
    def reject_quote(self, quote_id: int) -> bool:
        """Reject a quote by updating its status."""
        query = "UPDATE jobs SET status = 'declined' WHERE id = ? AND type = 'quote'"
        return self.db.execute_update(query, (quote_id,)) > 0
    
    def accept_quote(self, quote_id: int) -> bool:
        """Accept a quote by updating its status."""
        query = "UPDATE jobs SET status = 'accepted' WHERE id = ? AND type = 'quote'"
        return self.db.execute_update(query, (quote_id,)) > 0
    
    def get_jobs_by_tradesman(self, tradesman_id: int) -> List[Dict[str, Any]]:
        """Get all jobs for a specific tradesman."""
        query = """
            SELECT j.*, u.username, u.firstname, u.lastname
            FROM jobs j
            JOIN users u ON j.user_id = u.id
            WHERE j.tradesman_id = ? AND j.type = 'job'
            ORDER BY j.date_started DESC
        """
        return self.db.execute_query(query, (tradesman_id,))
    
    def get_quotes_by_tradesman(self, tradesman_id: int) -> List[Dict[str, Any]]:
        """Get all quotes for a specific tradesman."""
        query = """
            SELECT j.*, u.username, u.firstname, u.lastname
            FROM jobs j
            JOIN users u ON j.user_id = u.id
            WHERE j.tradesman_id = ? AND j.type = 'quote'
            ORDER BY j.date_requested DESC
        """
        return self.db.execute_query(query, (tradesman_id,))
    
    def can_user_edit_job(self, user_id: int, job_id: int) -> bool:
        """Check if a user can edit a job."""
        query = "SELECT 1 FROM jobs WHERE id = ? AND user_id = ?"
        result = self.db.execute_single_query(query, (job_id, user_id))
        return result is not None
    
    def get_unique_trades(self):
        """Get all unique trades for filtering"""
        query = "SELECT DISTINCT trade FROM tradesmen ORDER BY trade"
        results = self.db.execute_query(query)
        return [row['trade'] for row in results]
    
    def get_unique_users(self):
        """Get all unique users who have added jobs for filtering"""
        query = """
            SELECT DISTINCT u.username 
            FROM users u 
            JOIN jobs j ON u.id = j.user_id 
            ORDER BY u.username
        """
        results = self.db.execute_query(query)
        return [row['username'] for row in results]
    
    def get_unique_groups(self):
        """Get all unique groups for filtering"""
        query = """
            SELECT DISTINCT g.name 
            FROM groups g 
            JOIN group_tradesmen gt ON g.id = gt.group_id 
            JOIN jobs j ON gt.tradesman_id = j.tradesman_id
            ORDER BY g.name
        """
        results = self.db.execute_query(query)
        return [dict(row) for row in results]
    
    def get_recent_completed_jobs_for_user(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently completed jobs for user or users in their groups"""
        query = """
            SELECT j.*, 
                   t.first_name, t.family_name, t.company_name, t.trade,
                   u.username as added_by_username,
                   u.id as added_by_user_id
            FROM jobs j
            JOIN tradesmen t ON j.tradesman_id = t.id
            JOIN users u ON j.user_id = u.id
            LEFT JOIN user_groups ug ON u.id = ug.user_id
            LEFT JOIN groups g ON ug.group_id = g.id
            WHERE (j.user_id = ? OR 
                   (ug.group_id IN (
                       SELECT group_id FROM user_groups 
                       WHERE user_id = ? AND status IN ('member', 'admin', 'creator')
                   )))
            AND j.date_finished IS NOT NULL
            ORDER BY j.date_finished DESC
            LIMIT ?
        """
        return self.db.execute_query(query, (user_id, user_id, limit)) 

    def get_job_status_counts(self, tradesman_id: int) -> Dict[str, int]:
        """Get counts of jobs by status for a tradesman."""
        query = """
            SELECT status, COUNT(*) as count
            FROM jobs
            WHERE tradesman_id = ?
            GROUP BY status
        """
        results = self.db.execute_query(query, (tradesman_id,))
        counts: Dict[str, int] = {}
        for row in results:
            counts[row['status']] = row['count']
        return counts

    def get_job_titles_for_tradesman(self, tradesman_id: int) -> List[str]:
        """Get all job titles for a tradesman."""
        query = "SELECT title FROM jobs WHERE tradesman_id = ?"
        results = self.db.execute_query(query, (tradesman_id,))
        return [row['title'] for row in results] 