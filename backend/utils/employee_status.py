"""
Employee Status Utility Functions
Derives employee status from actual allocations rather than stored status field
"""
from datetime import date
from models import Employee, EmployeeStatus, Allocation


def get_derived_employee_status(employee, session=None, today=None):
    """
    Derive employee status from actual allocations
    
    Rules:
    - ALLOCATED: Has active allocations (start_date <= today AND (end_date is None OR end_date >= today))
    - NOTICE_PERIOD: Employee status is NOTICE_PERIOD (preserve this special status)
    - BENCH: No active allocations
    
    Args:
        employee: Employee model instance
        session: SQLAlchemy session (optional, will use employee.allocations relationship if not provided)
        today: Date to check against (defaults to date.today())
    
    Returns:
        EmployeeStatus enum value
    """
    if today is None:
        today = date.today()
    
    # Preserve NOTICE_PERIOD status - this is a special status that should override allocation status
    if employee.status == EmployeeStatus.NOTICE_PERIOD:
        return EmployeeStatus.NOTICE_PERIOD
    
    # Check for active allocations
    active_allocations = []
    
    if session:
        # Use session query for more control
        active_allocations = session.query(Allocation).filter(
            Allocation.emp_id == employee.id,
            Allocation.start_date <= today,
            (
                (Allocation.end_date.is_(None)) |
                (Allocation.end_date >= today)
            )
        ).all()
    else:
        # Use relationship (lazy loading)
        for alloc in employee.allocations:
            if alloc.start_date <= today:
                if alloc.end_date is None or alloc.end_date >= today:
                    active_allocations.append(alloc)
    
    # Filter out trainee-only allocations (they don't count as "allocated" for status)
    # Only count allocations where the employee is actually working (not just shadowing)
    # A trainee allocation is one where is_trainee=True AND allocation_percentage=0
    real_allocations = []
    for alloc in active_allocations:
        is_trainee = getattr(alloc, 'is_trainee', False)
        if is_trainee:
            # For trainees, check if they have any actual allocation percentage
            internal_pct = getattr(alloc, 'internal_allocation_percentage', None)
            alloc_pct = getattr(alloc, 'allocation_percentage', None)
            util = getattr(alloc, 'utilization', None)
            # Get the actual percentage value (handle None cases)
            actual_pct = internal_pct if internal_pct is not None else (alloc_pct if alloc_pct is not None else (util if util is not None else 0))
            # If trainee has 0% allocation (pure shadow), don't count as allocated
            if actual_pct == 0:
                continue  # Skip pure trainee allocations
        real_allocations.append(alloc)
    
    # If has active real allocations, status is ALLOCATED
    if real_allocations:
        return EmployeeStatus.ALLOCATED
    
    # Otherwise, status is BENCH
    return EmployeeStatus.BENCH


def get_current_allocation(employee, session=None, today=None):
    """
    Get the current active allocation for an employee
    Prefers non-trainee allocations, but returns trainee allocations if that's all they have
    
    Args:
        employee: Employee model instance
        session: SQLAlchemy session (optional)
        today: Date to check against (defaults to date.today())
    
    Returns:
        Allocation object or None
    """
    if today is None:
        today = date.today()
    
    if session:
        # Get all active allocations
        allocations = session.query(Allocation).filter(
            Allocation.emp_id == employee.id,
            Allocation.start_date <= today,
            (
                (Allocation.end_date.is_(None)) |
                (Allocation.end_date >= today)
            )
        ).order_by(Allocation.start_date.desc()).all()
        
        # Prefer non-trainee allocations
        for alloc in allocations:
            if not getattr(alloc, 'is_trainee', False):
                return alloc
        
        # If no non-trainee allocations, return first trainee allocation (if any)
        if allocations:
            return allocations[0]
        
        return None
    else:
        # Use relationship
        active_allocations = []
        for alloc in employee.allocations:
            if alloc.start_date <= today:
                if alloc.end_date is None or alloc.end_date >= today:
                    active_allocations.append(alloc)
        
        # Sort by start_date descending
        active_allocations.sort(key=lambda x: x.start_date, reverse=True)
        
        # Prefer non-trainee allocations
        for alloc in active_allocations:
            if not getattr(alloc, 'is_trainee', False):
                return alloc
        
        # If no non-trainee allocations, return first trainee allocation (if any)
        if active_allocations:
            return active_allocations[0]
        
        return None


def sync_employee_status(employee, session):
    """
    Sync the stored employee.status field with derived status from allocations
    This can be called periodically or after allocation changes
    
    Args:
        employee: Employee model instance
        session: SQLAlchemy session
    
    Returns:
        bool: True if status was updated, False if already correct
    """
    derived_status = get_derived_employee_status(employee, session)
    
    if employee.status != derived_status:
        employee.status = derived_status
        return True
    
    return False
