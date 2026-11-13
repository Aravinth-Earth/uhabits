"""
Generate a test database for Loop Habit Tracker Progress View feature showcase.

Database Schema:
- Habits: id, archived, color, description, freq_den, freq_num, highlight, name, position, 
          reminder_hour, reminder_min, reminder_days, type, target_type, target_value, unit, question, uuid
- Repetitions: id, habit, timestamp, value, notes

Entry Values:
- 0 = NO (missed, explicit no)
- 2 = YES_MANUAL (completed)
- 3 = SKIP (skipped)
- For numerical habits, value > 0 represents the actual value

Habit Types:
- type 0 = Boolean habit
- type 1 = Numerical habit

Frequency (freq_num / freq_den):
- 1/1 = Daily
- 3/7 = 3 times per week
- 1/7 = Weekly
- 1/30 = Monthly
"""

import sqlite3
import uuid
import random
from datetime import datetime, timedelta

# Configuration
OUTPUT_DB = r"C:\Users\w11-d\OneDrive\Desktop\u habit progress pr\test data\Progress_Feature_Demo.db"
START_DATE = datetime(2025, 6, 1)  # June 1, 2025
END_DATE = datetime(2026, 1, 26)  # January 26, 2026

# Palette colors (0-19)
COLORS = list(range(20))

# Generic habit templates - categorized for variety
HABIT_TEMPLATES = [
    # Daily wellness habits (type=0, freq=1/1)
    {"name": "Morning Stretch", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Evening Walk", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Meditation", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Healthy Breakfast", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Take Vitamins", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Skincare Routine", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Floss Teeth", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Drink Water", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "No Junk Food", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Sleep Before Midnight", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    
    # Weekly habits (type=0, freq=1/7 or 2/7 or 3/7)
    {"name": "Weekly Review", "freq_num": 1, "freq_den": 7, "type": 0, "category": "productivity"},
    {"name": "Grocery Shopping", "freq_num": 1, "freq_den": 7, "type": 0, "category": "home"},
    {"name": "Laundry", "freq_num": 2, "freq_den": 7, "type": 0, "category": "home"},
    {"name": "Call Family", "freq_num": 1, "freq_den": 7, "type": 0, "category": "social"},
    {"name": "Deep Clean Room", "freq_num": 1, "freq_den": 7, "type": 0, "category": "home"},
    
    # 3x per week habits
    {"name": "Gym Workout", "freq_num": 3, "freq_den": 7, "type": 0, "category": "fitness"},
    {"name": "Running", "freq_num": 3, "freq_den": 7, "type": 0, "category": "fitness"},
    {"name": "Yoga Session", "freq_num": 3, "freq_den": 7, "type": 0, "category": "fitness"},
    {"name": "Swimming", "freq_num": 2, "freq_den": 7, "type": 0, "category": "fitness"},
    
    # Every other day
    {"name": "Practice Instrument", "freq_num": 4, "freq_den": 7, "type": 0, "category": "learning"},
    {"name": "Language Learning", "freq_num": 4, "freq_den": 7, "type": 0, "category": "learning"},
    
    # Monthly habits
    {"name": "Budget Review", "freq_num": 1, "freq_den": 30, "type": 0, "category": "finance"},
    {"name": "Car Maintenance", "freq_num": 1, "freq_den": 30, "type": 0, "category": "home"},
    
    # Numerical habits - daily tracking
    {"name": "Water Glasses", "freq_num": 1, "freq_den": 1, "type": 1, "target": 8000, "unit": "ml", "category": "health"},
    {"name": "Steps Walked", "freq_num": 1, "freq_den": 1, "type": 1, "target": 10000, "unit": "steps", "category": "fitness"},
    {"name": "Reading Pages", "freq_num": 1, "freq_den": 1, "type": 1, "target": 30000, "unit": "pages", "category": "learning"},
    {"name": "Pushups", "freq_num": 1, "freq_den": 1, "type": 1, "target": 50000, "unit": "reps", "category": "fitness"},
    {"name": "Coding Minutes", "freq_num": 1, "freq_den": 1, "type": 1, "target": 60000, "unit": "min", "category": "productivity"},
    {"name": "Sleep Hours", "freq_num": 1, "freq_den": 1, "type": 1, "target": 8000, "unit": "hours", "category": "wellness"},
    {"name": "Calories Burned", "freq_num": 1, "freq_den": 1, "type": 1, "target": 500000, "unit": "cal", "category": "fitness"},
    {"name": "Journal Words", "freq_num": 1, "freq_den": 1, "type": 1, "target": 200000, "unit": "words", "category": "mindfulness"},
    
    # More daily boolean habits for variety
    {"name": "Morning Coffee Only", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "No Social Media", "freq_num": 1, "freq_den": 1, "type": 0, "category": "productivity"},
    {"name": "Inbox Zero", "freq_num": 1, "freq_den": 1, "type": 0, "category": "productivity"},
    {"name": "Plan Tomorrow", "freq_num": 1, "freq_den": 1, "type": 0, "category": "productivity"},
    {"name": "Gratitude Entry", "freq_num": 1, "freq_den": 1, "type": 0, "category": "mindfulness"},
    {"name": "Cold Shower", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Make Bed", "freq_num": 1, "freq_den": 1, "type": 0, "category": "home"},
    {"name": "No Snooze", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Review Goals", "freq_num": 1, "freq_den": 1, "type": 0, "category": "productivity"},
    {"name": "Practice Typing", "freq_num": 1, "freq_den": 1, "type": 0, "category": "learning"},
    
    # 5x per week habits (weekdays)
    {"name": "Work Focus Time", "freq_num": 5, "freq_den": 7, "type": 0, "category": "productivity"},
    {"name": "Lunch Walk", "freq_num": 5, "freq_den": 7, "type": 0, "category": "wellness"},
    {"name": "Standup Notes", "freq_num": 5, "freq_den": 7, "type": 0, "category": "productivity"},
    
    # Additional numerical habits
    {"name": "Protein Grams", "freq_num": 1, "freq_den": 1, "type": 1, "target": 100000, "unit": "g", "category": "health"},
    {"name": "Meditation Minutes", "freq_num": 1, "freq_den": 1, "type": 1, "target": 15000, "unit": "min", "category": "mindfulness"},
    {"name": "Screen Break Count", "freq_num": 1, "freq_den": 1, "type": 1, "target": 5000, "unit": "breaks", "category": "wellness"},
    
    # More variety
    {"name": "No Caffeine After 2PM", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Stretch Breaks", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Read News", "freq_num": 1, "freq_den": 1, "type": 0, "category": "learning"},
    {"name": "Practice Drawing", "freq_num": 3, "freq_den": 7, "type": 0, "category": "creativity"},
    {"name": "Write Blog", "freq_num": 1, "freq_den": 7, "type": 0, "category": "creativity"},
    {"name": "Photography", "freq_num": 2, "freq_den": 7, "type": 0, "category": "creativity"},
    {"name": "Clean Desk", "freq_num": 1, "freq_den": 1, "type": 0, "category": "productivity"},
    {"name": "Water Plants", "freq_num": 2, "freq_den": 7, "type": 0, "category": "home"},
    {"name": "Study Session", "freq_num": 1, "freq_den": 1, "type": 0, "category": "learning"},
    {"name": "Posture Check", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Eye Exercises", "freq_num": 1, "freq_den": 1, "type": 0, "category": "wellness"},
    {"name": "Meal Prep", "freq_num": 1, "freq_den": 7, "type": 0, "category": "home"},
    {"name": "Review Finances", "freq_num": 1, "freq_den": 7, "type": 0, "category": "finance"},
]


def date_to_timestamp(dt):
    """Convert datetime to midnight UTC timestamp in milliseconds."""
    # Loop uses midnight timestamps
    midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(midnight.timestamp() * 1000)


def generate_uuid():
    """Generate a UUID without dashes."""
    return uuid.uuid4().hex


def get_habit_start_date(habit_index, total_habits):
    """
    Determine when a habit was "created" based on the gradual addition pattern.
    ~50 habits initially (June 2025), then +10 per month less going forward.
    
    Actually we want: habits gradually added over time
    June: start with ~20 habits
    July: +10 more (30 total)
    August: +8 more (38 total)
    September: +6 more (44 total)
    October: +5 more (49 total)
    November: +4 more (53 total)
    December: +3 more (56 total)
    January: +4 more (60 total)
    """
    if habit_index < 20:
        return START_DATE
    elif habit_index < 30:
        return datetime(2025, 7, 1)
    elif habit_index < 38:
        return datetime(2025, 8, 1)
    elif habit_index < 44:
        return datetime(2025, 9, 1)
    elif habit_index < 49:
        return datetime(2025, 10, 1)
    elif habit_index < 53:
        return datetime(2025, 11, 1)
    elif habit_index < 56:
        return datetime(2025, 12, 1)
    else:
        return datetime(2026, 1, 1)


def should_archive(habit_index, total_habits):
    """
    Determine if a habit should be archived.
    Archive a few habits here and there (~8-10 habits).
    """
    # Archive habits at specific indices spread across the range
    archived_indices = {5, 12, 23, 31, 37, 42, 48, 54}
    return habit_index in archived_indices


def get_archive_date(habit_index):
    """Get the date when a habit was archived."""
    archive_dates = {
        5: datetime(2025, 8, 15),
        12: datetime(2025, 9, 1),
        23: datetime(2025, 10, 10),
        31: datetime(2025, 11, 1),
        37: datetime(2025, 11, 20),
        42: datetime(2025, 12, 5),
        48: datetime(2025, 12, 20),
        54: datetime(2026, 1, 10),
    }
    return archive_dates.get(habit_index, END_DATE)


def generate_completion_pattern(habit_template, habit_start, habit_end, habit_index):
    """
    Generate a diverse pattern of completions for a habit.
    Returns list of (timestamp, value) tuples.
    """
    entries = []
    current = habit_start
    
    freq_num = habit_template["freq_num"]
    freq_den = habit_template["freq_den"]
    is_numerical = habit_template["type"] == 1
    target = habit_template.get("target", 10000)
    
    # Different completion profiles for variety
    # Based on habit_index, assign different behavior patterns
    profile = habit_index % 7
    
    # Profile 0: Very consistent (80-95% completion)
    # Profile 1: Good but with gaps (60-80% completion)
    # Profile 2: Struggling (30-50% completion)
    # Profile 3: Improving over time (starts low, gets better)
    # Profile 4: Declining over time (starts high, gets worse)
    # Profile 5: Weekend warrior (better on weekends)
    # Profile 6: Random/sporadic
    
    total_days = (habit_end - habit_start).days
    
    while current <= habit_end:
        day_number = (current - habit_start).days
        progress_ratio = day_number / max(total_days, 1)
        is_weekend = current.weekday() >= 5
        
        # Calculate base completion probability based on frequency
        # Daily habit should have entries almost every day
        # 3/7 habit should have entries about 3 days per week
        if freq_den == 1:
            base_prob = 0.85
        elif freq_den == 7:
            base_prob = min(1.0, (freq_num / freq_den) + 0.1)
        elif freq_den == 30:
            # Monthly habit - only on certain days
            if current.day in [1, 15, 28]:
                base_prob = 0.7
            else:
                base_prob = 0.02
        else:
            base_prob = freq_num / freq_den
        
        # Adjust based on profile
        if profile == 0:  # Very consistent
            prob = base_prob * random.uniform(0.9, 1.0)
        elif profile == 1:  # Good with gaps
            prob = base_prob * random.uniform(0.7, 0.9)
        elif profile == 2:  # Struggling
            prob = base_prob * random.uniform(0.3, 0.6)
        elif profile == 3:  # Improving
            prob = base_prob * (0.3 + 0.6 * progress_ratio)
        elif profile == 4:  # Declining
            prob = base_prob * (0.9 - 0.5 * progress_ratio)
        elif profile == 5:  # Weekend warrior
            prob = base_prob * (1.2 if is_weekend else 0.6)
        else:  # Random
            prob = base_prob * random.uniform(0.2, 1.0)
        
        # Add some randomness for missed days, skips, etc.
        roll = random.random()
        
        if roll < prob:
            # Completed
            if is_numerical:
                # Random value around target (50% to 150% of target)
                value = int(target * random.uniform(0.5, 1.5))
                entries.append((date_to_timestamp(current), value))
            else:
                entries.append((date_to_timestamp(current), 2))  # YES_MANUAL
        elif roll < prob + 0.05:
            # Skipped (only sometimes)
            entries.append((date_to_timestamp(current), 3))  # SKIP
        elif roll < prob + 0.08:
            # Explicit no (rare)
            entries.append((date_to_timestamp(current), 0))  # NO
        # else: no entry (UNKNOWN)
        
        current += timedelta(days=1)
    
    return entries


def create_database():
    """Create the test database with all habits and repetitions."""
    
    # Delete if exists
    import os
    if os.path.exists(OUTPUT_DB):
        os.remove(OUTPUT_DB)
    
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    # Create schema
    cursor.execute("CREATE TABLE android_metadata (locale TEXT)")
    cursor.execute("INSERT INTO android_metadata VALUES ('en_US')")
    
    cursor.execute("""
        CREATE TABLE Habits (
            id integer primary key autoincrement,
            archived integer,
            color integer,
            description text,
            freq_den integer,
            freq_num integer,
            highlight integer,
            name text,
            position integer,
            reminder_hour integer,
            reminder_min integer,
            reminder_days integer not null default 127,
            type integer not null default 0,
            target_type integer not null default 0,
            target_value real not null default 0,
            unit text not null default "",
            question text,
            uuid text
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Repetitions (
            id integer primary key autoincrement,
            habit integer not null references habits(id),
            timestamp integer not null,
            value integer not null,
            notes text
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Events (
            id integer primary key autoincrement,
            timestamp integer,
            message text,
            server_id integer
        )
    """)
    
    cursor.execute("CREATE UNIQUE INDEX idx_repetitions_habit_timestamp on Repetitions(habit, timestamp)")
    
    # Set database version to match Loop's current version (25)
    cursor.execute("PRAGMA user_version = 25")
    
    # Generate habits
    total_habits = len(HABIT_TEMPLATES)
    print(f"Generating {total_habits} habits...")
    
    for i, template in enumerate(HABIT_TEMPLATES):
        habit_start = get_habit_start_date(i, total_habits)
        is_archived = should_archive(i, total_habits)
        archive_date = get_archive_date(i) if is_archived else END_DATE
        habit_end = min(archive_date, END_DATE)
        
        # Habit data
        color = random.choice(COLORS)
        target_value = template.get("target", 0) / 1000.0 if template["type"] == 1 else 0
        unit = template.get("unit", "")
        
        cursor.execute("""
            INSERT INTO Habits (
                archived, color, description, freq_den, freq_num, highlight, 
                name, position, reminder_hour, reminder_min, reminder_days,
                type, target_type, target_value, unit, question, uuid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1 if is_archived else 0,
            color,
            "",  # description
            template["freq_den"],
            template["freq_num"],
            0,  # highlight
            template["name"],
            i,  # position
            None,  # reminder_hour
            None,  # reminder_min
            127,  # reminder_days (all days)
            template["type"],
            0,  # target_type
            target_value,
            unit,
            "",  # question
            generate_uuid()
        ))
        
        habit_id = cursor.lastrowid
        
        # Generate repetitions
        entries = generate_completion_pattern(template, habit_start, habit_end, i)
        
        for timestamp, value in entries:
            cursor.execute("""
                INSERT INTO Repetitions (habit, timestamp, value, notes)
                VALUES (?, ?, ?, ?)
            """, (habit_id, timestamp, value, None))
        
        status = "ARCHIVED" if is_archived else "active"
        print(f"  [{i+1}/{total_habits}] {template['name']} ({status}) - {len(entries)} entries")
    
    conn.commit()
    
    # Print summary
    cursor.execute("SELECT COUNT(*) FROM Habits WHERE archived = 0")
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Habits WHERE archived = 1")
    archived_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Repetitions")
    total_entries = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM Repetitions")
    min_ts, max_ts = cursor.fetchone()
    
    print(f"\n=== Summary ===")
    print(f"Active habits: {active_count}")
    print(f"Archived habits: {archived_count}")
    print(f"Total entries: {total_entries}")
    print(f"Date range: {datetime.fromtimestamp(min_ts/1000).date()} to {datetime.fromtimestamp(max_ts/1000).date()}")
    print(f"Output: {OUTPUT_DB}")
    
    conn.close()


if __name__ == "__main__":
    create_database()
    print("\nDone! Import this database into Loop Habit Tracker.")
