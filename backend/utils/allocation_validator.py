"""
Allocation Validation Utilities
Validates that employee allocations don't exceed 100% total allocation
"""
from datetime import date
from models import Allocation, Employee


def validate_allocation_percentage(session, employee_id, internal_allocation_percentage, start_date, end_date, exclude_allocation_id=None):
    """
    Validate that adding/updating an allocation won't cause total internal_allocation_percentage to exceed 100%
    
    Args:
        session: SQLAlchemy session
        employee_id: ID of the employee
        internal_allocation_percentage: The internal allocation percentage being added/updated (0-100)
        start_date: Start date of the new/updated allocation
        end_date: End date of the new/updated allocation (None for ongoing)
        exclude_allocation_id: ID of allocation to exclude (for updates)
    
    Returns:
        (is_valid, error_message): Tuple of (bool, str or None)
    """
    try:
        # Get all active allocations for this employee that overlap with the date range
        today = date.today()
        
        # Build query for overlapping allocations
        query = session.query(Allocation).filter(
            Allocation.emp_id == employee_id
        )
        
        # Exclude the allocation being updated
        if exclude_allocation_id:
            query = query.filter(Allocation.id != exclude_allocation_id)
        
        # Find allocations that overlap with the new date range
        # Two date ranges overlap if: start1 <= end2 AND start2 <= end1
        overlapping_allocations = []
        for alloc in query.all():
            # Check if dates overlap
            alloc_start = alloc.start_date
            alloc_end = alloc.end_date if alloc.end_date else date(2099, 12, 31)  # Treat None as far future
            new_end = end_date if end_date else date(2099, 12, 31)  # Treat None as far future
            
            # Check overlap: alloc_start <= new_end AND start_date <= alloc_end
            if alloc_start <= new_end and start_date <= alloc_end:
                overlapping_allocations.append(alloc)
        
        # Sum up internal_allocation_percentage from overlapping allocations
        total_allocation = 0
        for alloc in overlapping_allocations:
            try:
                # Try to get internal_allocation_percentage (primary field for validation)
                alloc_pct = getattr(alloc, 'internal_allocation_percentage', None)
                if alloc_pct is None:
                    # Fallback to allocation_percentage if internal_allocation_percentage doesn't exist
                    alloc_pct = getattr(alloc, 'allocation_percentage', None)
                    if alloc_pct is None:
                        # Fallback to utilization if allocation_percentage doesn't exist
                        alloc_pct = getattr(alloc, 'utilization', 100) or 100
                total_allocation += alloc_pct
            except (AttributeError, TypeError):
                # If field doesn't exist, assume 100%
                total_allocation += 100
        
        # If new internal allocation percentage is 0%, it doesn't count towards total allocation
        # (0% means not allocated, so it's always valid)
        if internal_allocation_percentage == 0:
            return True, None
        
        # Add the new internal allocation percentage
        total_allocation += internal_allocation_percentage
        
        # Check if total exceeds 100%
        if total_allocation > 100:
            employee = session.query(Employee).filter(Employee.id == employee_id).first()
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else f"Employee {employee_id}"
            current_total = total_allocation - internal_allocation_percentage
            return False, f"Total internal allocation for {employee_name} would be {total_allocation}%. Maximum allowed is 100%. Current overlapping allocations total {current_total}%."
        
        return True, None
    
    except Exception as e:
        # If there's an error, log it but allow the allocation (fail open for now)
        import traceback
        print(f"Warning: Error validating allocation percentage: {e}")
        print(traceback.format_exc())
        return True, None
