"""Statistical aggregation service for dashboard data."""


def get_overview_stats(cursor):
    """Get high-level overview statistics."""
    cursor.execute('''
        SELECT
            COUNT(*) as total_projects,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_projects,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_projects,
            COALESCE(SUM(current_amount), 0) as total_budget,
            COALESCE(SUM(total_paid), 0) as total_spent,
            COALESCE(SUM(remaining_balance), 0) as total_remaining,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget_count,
            AVG(percent_complete) as avg_completion
        FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL
    ''')
    row = cursor.fetchone()
    return dict(row) if row else {}


def get_all_contract_stats(cursor):
    """Get stats for all contracts (not just surtax)."""
    cursor.execute('''
        SELECT
            COUNT(*) as total_projects,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_projects,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_projects,
            COALESCE(SUM(current_amount), 0) as total_budget,
            COALESCE(SUM(total_paid), 0) as total_spent,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count,
            SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) as over_budget_count,
            AVG(percent_complete) as avg_completion,
            AVG(overall_health_score) as avg_health_score
        FROM contracts
        WHERE is_deleted = 0
    ''')
    row = cursor.fetchone()
    return dict(row) if row else {}


def get_spending_by_category(cursor):
    """Get spending breakdown by surtax category."""
    cursor.execute('''
        SELECT
            surtax_category as category,
            COUNT(*) as project_count,
            COALESCE(SUM(current_amount), 0) as total_budget,
            COALESCE(SUM(total_paid), 0) as total_spent,
            AVG(percent_complete) as avg_completion
        FROM contracts
        WHERE is_deleted = 0 AND surtax_category IS NOT NULL
        GROUP BY surtax_category
        ORDER BY total_budget DESC
    ''')
    return [dict(row) for row in cursor.fetchall()]


def get_concerns_list(cursor):
    """Get list of delayed and over-budget projects."""
    cursor.execute('''
        SELECT contract_id, title, school_name, surtax_category, vendor_name,
               current_amount, total_paid, percent_complete,
               is_delayed, delay_days, delay_reason,
               is_over_budget, budget_variance_pct,
               overall_health_score, risk_level
        FROM contracts
        WHERE is_deleted = 0
          AND (is_delayed = 1 OR is_over_budget = 1)
        ORDER BY overall_health_score ASC
    ''')
    return [dict(row) for row in cursor.fetchall()]


def get_projects_by_school(cursor):
    """Get project count and budget by school."""
    cursor.execute('''
        SELECT
            school_name,
            COUNT(*) as project_count,
            COALESCE(SUM(current_amount), 0) as total_budget,
            COALESCE(SUM(total_paid), 0) as total_spent,
            AVG(percent_complete) as avg_completion,
            SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) as delayed_count
        FROM contracts
        WHERE is_deleted = 0 AND school_name IS NOT NULL
        GROUP BY school_name
        ORDER BY total_budget DESC
    ''')
    return [dict(row) for row in cursor.fetchall()]
