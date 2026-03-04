#!/usr/bin/env python
"""Generate realistic sample data for Surtax Oversight Pro."""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_connection, init_db

# Marion County schools
SCHOOLS = [
    "Belleview High School", "Belleview-Santos Elementary", "Blessed Trinity Catholic School",
    "Dunnellon High School", "Dunnellon Middle School", "Dunnellon Elementary",
    "Emerald Shores Elementary", "Evergreen Elementary", "Forest High School",
    "Fort King Middle School", "Fort McCoy School", "Greenway Elementary",
    "Hammett Bowen Jr Elementary", "Harbor View Elementary", "Howard Middle School",
    "Lake Weir High School", "Lake Weir Middle School", "Legacy Elementary",
    "Liberty Middle School", "Madison Street Academy", "Marion Oaks Elementary",
    "Maplewood Elementary", "North Marion High School", "North Marion Middle School",
    "Oakcrest Elementary", "Ocala Springs Elementary", "Osceola Middle School",
    "Romeo Elementary", "Saddlewood Elementary", "Shady Hill Elementary",
    "South Ocala Elementary", "Sparr Elementary", "Stanton-Weirsdale Elementary",
    "Sunrise Elementary", "Vanguard High School", "Ward-Highlands Elementary",
    "West Port High School", "Wyomina Park Elementary"
]

SURTAX_CATEGORIES = [
    "New Construction", "Renovation", "Safety & Security", "Technology",
    "HVAC", "Site Improvements", "Roofing", "ADA Compliance"
]

VENDORS = [
    ("Stellar Construction Group", "Large", "Ocala", "FL"),
    ("Marion Build Partners", "Medium", "Ocala", "FL"),
    ("Sunshine State Contractors", "Large", "Gainesville", "FL"),
    ("Central FL Renovations", "Medium", "Orlando", "FL"),
    ("SafeSchool Systems Inc", "Small", "Jacksonville", "FL"),
    ("TechConnect Solutions", "Small", "Tampa", "FL"),
    ("AirFlow HVAC Services", "Medium", "Ocala", "FL"),
    ("SiteWorks Engineering", "Medium", "Ocala", "FL"),
    ("TopCoat Roofing LLC", "Small", "Leesburg", "FL"),
    ("AccessAbility Builders", "Small", "Ocala", "FL"),
    ("Premier Paving Co", "Medium", "Gainesville", "FL"),
    ("Guardian Security Systems", "Small", "Orlando", "FL"),
]

PROJECT_TEMPLATES = {
    "New Construction": [
        "{school} - New Classroom Wing", "{school} - Media Center Expansion",
        "{school} - Gymnasium Addition", "{school} - Cafeteria Expansion"
    ],
    "Renovation": [
        "{school} - Building Renovation Phase {n}", "{school} - Restroom Modernization",
        "{school} - Science Lab Renovation", "{school} - Administration Building Remodel"
    ],
    "Safety & Security": [
        "{school} - Single Point of Entry", "{school} - Security Camera System",
        "{school} - Fencing & Access Control", "{school} - Emergency Communication System"
    ],
    "Technology": [
        "{school} - Network Infrastructure Upgrade", "{school} - Smart Classroom Technology",
        "{school} - Data Center Upgrade"
    ],
    "HVAC": [
        "{school} - HVAC Replacement Phase {n}", "{school} - Chiller Plant Upgrade",
        "{school} - Building {n} AC Replacement"
    ],
    "Site Improvements": [
        "{school} - Parking Lot Expansion", "{school} - Drainage Improvements",
        "{school} - Athletic Field Renovation", "{school} - Drop-off Loop Redesign"
    ],
    "Roofing": [
        "{school} - Roof Replacement Building {n}", "{school} - Full Roof Replacement",
        "{school} - Roof Restoration"
    ],
    "ADA Compliance": [
        "{school} - ADA Accessibility Upgrade", "{school} - Elevator Installation",
        "{school} - Accessible Restroom Conversion"
    ]
}


def generate_data():
    """Generate realistic sample data."""
    init_db()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM contracts")
        if cursor.fetchone()[0] > 0:
            print("Data already exists. Skipping generation.")
            return

        # Insert vendors
        for name, size, city, state in VENDORS:
            vid = str(uuid.uuid4())[:8]
            perf_score = random.uniform(65, 98)
            cursor.execute('''
                INSERT INTO vendors (vendor_id, name, vendor_size, headquarters_city, headquarters_state,
                                    status, performance_score, years_in_business, bonding_capacity)
                VALUES (?, ?, ?, ?, ?, 'Active', ?, ?, ?)
            ''', (vid, name, size, city, state, round(perf_score, 1),
                  random.randint(5, 40), random.choice([5000000, 10000000, 25000000, 50000000])))

        # Generate 44 surtax projects
        used_schools = set()
        contracts_created = 0

        for i in range(44):
            school = random.choice(SCHOOLS)
            category = random.choice(SURTAX_CATEGORIES)
            templates = PROJECT_TEMPLATES[category]
            template = random.choice(templates)
            title = template.format(school=school, n=random.randint(1, 5))

            # Avoid exact duplicates
            while title in used_schools:
                school = random.choice(SCHOOLS)
                title = template.format(school=school, n=random.randint(1, 5))
            used_schools.add(title)

            vendor = random.choice(VENDORS)
            cid = f"SC-2025-{i+1:03d}"

            # Financial data
            if category == "New Construction":
                budget = random.uniform(5000000, 35000000)
            elif category in ("Renovation", "HVAC"):
                budget = random.uniform(1500000, 12000000)
            elif category == "Technology":
                budget = random.uniform(500000, 3000000)
            else:
                budget = random.uniform(800000, 6000000)

            budget = round(budget, -3)  # Round to nearest thousand

            # Timeline
            start = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 180))
            duration_months = random.randint(6, 30)
            end = start + timedelta(days=duration_months * 30)
            now = datetime(2026, 3, 1)

            # Progress and status
            elapsed_pct = min(100, max(0, (now - start).days / max(1, (end - start).days) * 100))
            percent_complete = round(min(100, elapsed_pct * random.uniform(0.7, 1.1)), 1)

            if percent_complete >= 100:
                status = "Completed"
                percent_complete = 100
            elif start > now:
                status = "Not Started"
                percent_complete = 0
            else:
                status = "Active"

            # Spending
            paid_pct = percent_complete / 100 * random.uniform(0.85, 1.15)
            total_paid = round(budget * min(1.0, paid_pct), -2)
            current_amount = budget

            # Over budget / delayed flags
            is_over_budget = 0
            budget_variance_pct = 0
            if random.random() < 0.2:  # 20% chance over budget
                overage_pct = random.uniform(5, 25)
                current_amount = round(budget * (1 + overage_pct / 100), -3)
                budget_variance_pct = round(overage_pct, 1)
                is_over_budget = 1

            is_delayed = 0
            delay_days = 0
            delay_reason = None
            if random.random() < 0.25 and status == "Active":  # 25% chance delayed
                delay_days = random.randint(15, 120)
                is_delayed = 1
                delay_reason = random.choice([
                    "Supply chain delays", "Permitting issues", "Weather delays",
                    "Change order processing", "Subcontractor availability",
                    "Design modification required", "Material shortage"
                ])

            # Health score
            health = 85
            if is_delayed:
                health -= random.randint(15, 35)
            if is_over_budget:
                health -= random.randint(10, 25)
            health = max(15, min(100, health + random.randint(-5, 5)))

            risk_level = "Low"
            if health < 30:
                risk_level = "Critical"
            elif health < 50:
                risk_level = "High"
            elif health < 70:
                risk_level = "Medium"

            cursor.execute('''
                INSERT INTO contracts (
                    contract_id, title, description, vendor_name,
                    original_amount, current_amount, total_paid, remaining_balance,
                    start_date, original_end_date, current_end_date,
                    status, percent_complete,
                    overall_health_score, risk_level,
                    school_name, surtax_category, expenditure_type,
                    is_delayed, delay_days, delay_reason,
                    is_over_budget, budget_variance_pct,
                    is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                cid, title, f"{category} project at {school}",
                vendor[0],
                budget, current_amount, total_paid, round(current_amount - total_paid, 2),
                start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'),
                status, percent_complete,
                health, risk_level,
                school, category, "Capital",
                is_delayed, delay_days, delay_reason,
                is_over_budget, budget_variance_pct
            ))
            contracts_created += 1

        # Generate 20 general (non-surtax) contracts
        general_types = [
            "IT Infrastructure Maintenance", "Janitorial Services",
            "Transportation Services", "Professional Development",
            "Consulting Services", "Grounds Maintenance",
            "Food Services Equipment", "Administrative Software",
            "Security Guard Services", "Legal Services",
            "Insurance Services", "Telecommunications",
            "Printing Services", "Vehicle Fleet Maintenance",
            "Professional Audit Services", "Payroll Processing",
            "Employee Benefits Administration", "Energy Management",
            "Waste Management Services", "Facility Management"
        ]

        for i, title in enumerate(general_types):
            cid = f"GC-2025-{i+1:03d}"
            vendor = random.choice(VENDORS)
            budget = round(random.uniform(50000, 2000000), -3)
            start = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))
            end = start + timedelta(days=random.randint(180, 730))
            pct = round(random.uniform(10, 90), 1)
            paid = round(budget * pct / 100, -2)
            health = random.randint(55, 98)

            cursor.execute('''
                INSERT INTO contracts (
                    contract_id, title, description, vendor_name,
                    original_amount, current_amount, total_paid, remaining_balance,
                    start_date, original_end_date, current_end_date,
                    status, percent_complete,
                    overall_health_score, risk_level,
                    is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?, ?, ?, 0)
            ''', (
                cid, title, f"General contract for {title.lower()}",
                vendor[0],
                budget, budget, paid, round(budget - paid, 2),
                start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'),
                pct, health,
                "Low" if health >= 70 else "Medium" if health >= 50 else "High"
            ))
            contracts_created += 1

        conn.commit()
        print(f"Generated {contracts_created} contracts ({44} surtax + {20} general)")
        print(f"Generated {len(VENDORS)} vendors")
        print("Sample data generation complete!")


if __name__ == '__main__':
    generate_data()
