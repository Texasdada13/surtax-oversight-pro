-- Surtax Oversight Pro - Unified Database Schema
-- Merged from contract-oversight-system, florida-school-surtax-oversight, and surtax-oversight-dashboard

-- Contracts table (superset of all three apps)
CREATE TABLE IF NOT EXISTS contracts (
    contract_id TEXT PRIMARY KEY,
    contract_number TEXT,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT,

    -- Vendor
    vendor_id TEXT,
    vendor_name TEXT,

    -- Financial
    original_amount REAL DEFAULT 0,
    current_amount REAL DEFAULT 0,
    total_paid REAL DEFAULT 0,
    remaining_balance REAL DEFAULT 0,

    -- Dates
    solicitation_date TEXT,
    award_date TEXT,
    start_date TEXT,
    original_end_date TEXT,
    current_end_date TEXT,
    actual_end_date TEXT,

    -- Status
    status TEXT DEFAULT 'Active',
    phase TEXT,
    percent_complete REAL DEFAULT 0,

    -- Scoring (from contract-oversight scoring engine)
    performance_score REAL,
    cost_variance_score REAL,
    schedule_variance_score REAL,
    compliance_score REAL,
    overall_health_score REAL,
    risk_level TEXT DEFAULT 'Low',

    -- Procurement
    procurement_method TEXT,
    bid_count INTEGER DEFAULT 0,
    is_sole_source INTEGER DEFAULT 0,
    justification TEXT,

    -- Compliance
    board_approval_date TEXT,
    requires_insurance INTEGER DEFAULT 0,
    insurance_verified INTEGER DEFAULT 0,
    requires_bond INTEGER DEFAULT 0,
    bond_verified INTEGER DEFAULT 0,

    -- Location
    project_location TEXT,
    latitude REAL,
    longitude REAL,
    council_district TEXT,

    -- Risk tracking
    change_order_count INTEGER DEFAULT 0,
    total_change_order_amount REAL DEFAULT 0,

    -- Surtax-specific fields
    school_name TEXT,
    school_id TEXT,
    surtax_category TEXT,
    expenditure_type TEXT,
    is_delayed INTEGER DEFAULT 0,
    delay_days INTEGER DEFAULT 0,
    delay_reason TEXT,
    is_over_budget INTEGER DEFAULT 0,
    budget_variance_amount REAL DEFAULT 0,
    budget_variance_pct REAL DEFAULT 0,

    -- Executive analytics fields
    land_cost REAL,
    construction_cost REAL,
    cost_per_sqft REAL,
    burn_rate_monthly REAL,
    risk_probability_score REAL,
    expected_completion_date TEXT,

    -- Enhanced project fields
    purpose TEXT,
    scope TEXT,
    community_impact TEXT,
    contingency_amount REAL DEFAULT 0,

    -- Audit
    created_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    is_emergency INTEGER DEFAULT 0,
    notes TEXT
);

-- Vendors table
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dba_name TEXT,
    contact_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    vendor_type TEXT,
    vendor_size TEXT,
    headquarters_city TEXT,
    headquarters_state TEXT,
    tax_id TEXT,
    registration_date TEXT,
    status TEXT DEFAULT 'Active',
    performance_score REAL DEFAULT 0,
    total_contracts INTEGER DEFAULT 0,
    total_awarded REAL DEFAULT 0,
    minority_owned INTEGER DEFAULT 0,
    woman_owned INTEGER DEFAULT 0,
    small_business INTEGER DEFAULT 0,
    local_business INTEGER DEFAULT 0,
    years_in_business INTEGER,
    bonding_capacity REAL,
    certifications TEXT,
    license_number TEXT,
    insurance_expiry TEXT,
    notes TEXT
);

-- Change orders
CREATE TABLE IF NOT EXISTS change_orders (
    change_order_id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    change_order_number INTEGER,
    description TEXT,
    reason TEXT,
    original_value REAL DEFAULT 0,
    change_value REAL DEFAULT 0,
    new_value REAL DEFAULT 0,
    status TEXT DEFAULT 'Pending',
    schedule_impact_days INTEGER DEFAULT 0,
    requested_date TEXT,
    approved_date TEXT,
    approved_by TEXT,
    board_approval_required INTEGER DEFAULT 0,
    board_approval_date TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Milestones/deliverables
CREATE TABLE IF NOT EXISTS milestones (
    milestone_id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    planned_date TEXT,
    actual_date TEXT,
    status TEXT DEFAULT 'Pending',
    percent_complete REAL DEFAULT 0,
    payment_amount REAL DEFAULT 0,
    payment_status TEXT DEFAULT 'Pending',
    verified_by TEXT,
    verified_date TEXT,
    is_blocker INTEGER DEFAULT 0,
    blocker_description TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    vendor_id TEXT,
    milestone_id TEXT,
    invoice_number TEXT,
    invoice_date TEXT,
    amount REAL DEFAULT 0,
    payment_date TEXT,
    payment_type TEXT,
    check_number TEXT,
    status TEXT DEFAULT 'Pending',
    approved_by TEXT,
    approved_date TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Concerns / Issues
CREATE TABLE IF NOT EXISTS concerns (
    concern_id TEXT PRIMARY KEY,
    contract_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'Other',
    severity TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Open',
    created_date TEXT DEFAULT (datetime('now')),
    resolved_date TEXT,
    created_by TEXT,
    resolved_by TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    action TEXT NOT NULL,
    field_name TEXT,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT,
    changed_at TEXT DEFAULT (datetime('now')),
    ip_address TEXT
);

-- Comments
CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    parent_id TEXT,
    content TEXT NOT NULL,
    is_internal INTEGER DEFAULT 1,
    created_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    email TEXT,
    role TEXT DEFAULT 'viewer',
    department TEXT,
    last_login TEXT,
    is_active INTEGER DEFAULT 1
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    contract_id TEXT,
    title TEXT NOT NULL,
    document_type TEXT DEFAULT 'Other',
    file_path TEXT,
    file_size INTEGER,
    mime_type TEXT,
    description TEXT,
    uploaded_by TEXT,
    uploaded_date TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id TEXT PRIMARY KEY,
    user_id TEXT,
    title TEXT NOT NULL,
    message TEXT,
    type TEXT DEFAULT 'info',
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Vendor ratings
CREATE TABLE IF NOT EXISTS vendor_ratings (
    rating_id TEXT PRIMARY KEY,
    vendor_id TEXT NOT NULL,
    contract_id TEXT,
    rating REAL,
    category TEXT,
    comments TEXT,
    rated_by TEXT,
    rated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- Meeting minutes
CREATE TABLE IF NOT EXISTS meeting_minutes (
    meeting_id TEXT PRIMARY KEY,
    meeting_date TEXT NOT NULL,
    meeting_type TEXT DEFAULT 'Regular',
    location TEXT,
    attendees TEXT,
    agenda TEXT,
    minutes TEXT,
    decisions TEXT,
    action_items TEXT,
    status TEXT DEFAULT 'Draft',
    document_path TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Counties (for comparison)
CREATE TABLE IF NOT EXISTS counties (
    county_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT DEFAULT 'FL',
    fips_code TEXT,
    population INTEGER,
    school_district TEXT
);

-- County fiscal data
CREATE TABLE IF NOT EXISTS county_fiscal_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    county_id TEXT,
    fiscal_year TEXT,
    total_revenue REAL,
    total_expenditure REAL,
    surtax_revenue REAL,
    capital_expenditure REAL,
    source TEXT,
    FOREIGN KEY (county_id) REFERENCES counties(county_id)
);

-- Benchmark KPI values (Coupa 2025)
CREATE TABLE IF NOT EXISTS benchmark_kpi_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    kpi_name TEXT,
    actual_value REAL,
    benchmark_value REAL,
    score REAL,
    rating TEXT,
    last_updated TEXT
);

-- Project phases (from surtax-dashboard)
CREATE TABLE IF NOT EXISTS project_phases (
    phase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id TEXT NOT NULL,
    phase_name TEXT NOT NULL,
    phase_order INTEGER DEFAULT 0,
    start_date TEXT,
    end_date TEXT,
    status TEXT DEFAULT 'Not Started',
    percent_complete REAL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Inspection log
CREATE TABLE IF NOT EXISTS inspection_log (
    inspection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id TEXT NOT NULL,
    inspection_date TEXT,
    inspector_name TEXT,
    inspection_type TEXT,
    findings TEXT,
    deficiency_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Pass',
    follow_up_required INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Community engagement
CREATE TABLE IF NOT EXISTS community_engagement (
    engagement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id TEXT NOT NULL,
    meeting_date TEXT,
    attendee_count INTEGER DEFAULT 0,
    feedback_summary TEXT,
    concerns_raised TEXT,
    location TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Committee actions
CREATE TABLE IF NOT EXISTS committee_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id TEXT,
    action_item TEXT NOT NULL,
    assignee TEXT,
    due_date TEXT,
    status TEXT DEFAULT 'Open',
    priority TEXT DEFAULT 'Medium',
    created_date TEXT DEFAULT (datetime('now')),
    completed_date TEXT,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Contractor performance
CREATE TABLE IF NOT EXISTS contractor_performance (
    perf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id TEXT NOT NULL,
    vendor_name TEXT,
    safety_record TEXT DEFAULT 'Good',
    quality_score REAL DEFAULT 0,
    past_projects INTEGER DEFAULT 0,
    deficiency_rate REAL DEFAULT 0,
    local_hiring_pct REAL DEFAULT 0,
    on_time_rate REAL DEFAULT 0,
    on_budget_rate REAL DEFAULT 0,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_school ON contracts(school_name);
CREATE INDEX IF NOT EXISTS idx_contracts_vendor ON contracts(vendor_name);
CREATE INDEX IF NOT EXISTS idx_contracts_category ON contracts(surtax_category);
CREATE INDEX IF NOT EXISTS idx_contracts_delayed ON contracts(is_delayed);
CREATE INDEX IF NOT EXISTS idx_contracts_over_budget ON contracts(is_over_budget);
CREATE INDEX IF NOT EXISTS idx_contracts_deleted ON contracts(is_deleted);
CREATE INDEX IF NOT EXISTS idx_contracts_health ON contracts(overall_health_score);
CREATE INDEX IF NOT EXISTS idx_change_orders_contract ON change_orders(contract_id);
CREATE INDEX IF NOT EXISTS idx_milestones_contract ON milestones(contract_id);
CREATE INDEX IF NOT EXISTS idx_payments_contract ON payments(contract_id);
CREATE INDEX IF NOT EXISTS idx_concerns_contract ON concerns(contract_id);
CREATE INDEX IF NOT EXISTS idx_concerns_status ON concerns(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_documents_contract ON documents(contract_id);
CREATE INDEX IF NOT EXISTS idx_project_phases_contract ON project_phases(contract_id);
CREATE INDEX IF NOT EXISTS idx_inspection_contract ON inspection_log(contract_id);
