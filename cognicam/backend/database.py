import sqlite3
import hashlib
import uuid
import json
import os
from datetime import datetime, timedelta

DB_FILE = os.path.join(os.path.dirname(__file__), "cognicam.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Table: users
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        organization TEXT,
        role TEXT DEFAULT 'analyst',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_login TEXT
    )
    ''')
    
    # Table: sessions
    c.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        token TEXT UNIQUE NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    ''')
    
    # Table: appraisals
    c.execute('''
    CREATE TABLE IF NOT EXISTS appraisals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        session_token TEXT,
        company_name TEXT,
        gstin TEXT,
        sector TEXT,
        final_score REAL,
        decision TEXT,
        credit_limit_cr REAL,
        interest_rate REAL,
        risk_grade TEXT,
        character_score REAL,
        capacity_score REAL,
        capital_score REAL,
        collateral_score REAL,
        conditions_score REAL,
        gstr_flags TEXT,
        field_note TEXT,
        shap_explanation TEXT,
        full_report_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'completed'
    )
    ''')
    
    conn.commit()
    
    # Insert default demo user if not exists
    c.execute("SELECT id FROM users WHERE username = 'demo'")
    if not c.fetchone():
        create_user(
            username='demo',
            email='demo@cognicam.ai',
            password='demo123',
            full_name='Demo Analyst',
            org='IIT Hyderabad'
        )
    
    conn.close()

def hash_password(password: str) -> str:
    salt = "cognicam_salt_2025"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash

def create_user(username, email, password, full_name, org):
    conn = get_connection()
    c = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        c.execute("""
            INSERT INTO users (username, email, password_hash, full_name, organization, role)
            VALUES (?, ?, ?, ?, ?, 'analyst')
        """, (username, email, pwd_hash, full_name, org))
        conn.commit()
        user_id = c.lastrowid
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = dict(c.fetchone())
        # never return password hash
        if 'password_hash' in user:
            del user['password_hash']
        return user
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row and verify_password(password, row['password_hash']):
        user = dict(row)
        del user['password_hash']
        
        # Update last login
        conn = get_connection()
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user['id']))
        conn.commit()
        conn.close()
        
        return user
    return None

def create_session(user_id):
    conn = get_connection()
    c = conn.cursor()
    token = str(uuid.uuid4())
    expires = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO sessions (user_id, token, expires_at)
        VALUES (?, ?, ?)
    """, (user_id, token, expires))
    conn.commit()
    conn.close()
    return token

def get_user_from_token(token):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        SELECT u.* FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.token = ? AND s.is_active = 1 AND s.expires_at > ?
    """, (token, now_str))
    row = c.fetchone()
    conn.close()
    if row:
        user = dict(row)
        del user['password_hash']
        return user
    return None

def invalidate_session(token):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE sessions SET is_active = 0 WHERE token = ?", (token,))
    conn.commit()
    conn.close()

def save_appraisal(user_id, data_dict):
    conn = get_connection()
    c = conn.cursor()
    
    # Extract keys safely
    scores = data_dict.get('scoringData', {})
    shap = data_dict.get('shapData', {})
    company = data_dict.get('companyInfo', {})
    gstr_flags = data_dict.get('gstrFlags', {})
    field_note = data_dict.get('fieldNote', '')
    
    c.execute("""
        INSERT INTO appraisals (
            user_id, session_token, company_name, gstin, sector, 
            final_score, decision, credit_limit_cr, interest_rate, risk_grade,
            character_score, capacity_score, capital_score, collateral_score, conditions_score,
            gstr_flags, field_note, shap_explanation, full_report_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data_dict.get('token', ''),
        company.get('name', 'Unknown'),
        company.get('gstin', ''),
        company.get('sector', ''),
        scores.get('overall_score', 0),
        scores.get('decision', 'CONDITIONAL'),
        scores.get('credit_limit_cr', 0.0),
        scores.get('interest_rate_pa', 0.0),
        scores.get('risk_grade', 'C'),
        scores.get('character_score', 0),
        scores.get('capacity_score', 0),
        scores.get('capital_score', 0),
        scores.get('collateral_score', 0),
        scores.get('conditions_score', 0),
        json.dumps(gstr_flags),
        field_note,
        json.dumps(shap),
        json.dumps(data_dict)
    ))
    conn.commit()
    appraisal_id = c.lastrowid
    conn.close()
    return appraisal_id

def get_user_appraisals(user_id, limit=20, offset=0, search='', decision_filter='all'):
    conn = get_connection()
    c = conn.cursor()
    
    query = "SELECT id, company_name, gstin, sector, final_score, decision, credit_limit_cr, interest_rate, risk_grade, created_at, status FROM appraisals WHERE user_id = ? AND status != 'archived'"
    params = [user_id]
    
    if search:
        query += " AND company_name LIKE ?"
        params.append(f"%{search}%")
        
    if decision_filter and decision_filter.lower() != 'all':
        query += " AND decision = ?"
        params.append(decision_filter.upper())
        
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    c.execute(query, params)
    rows = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM appraisals WHERE user_id = ? AND status != 'archived'", (user_id,))
    total = c.fetchone()[0]
    
    conn.close()
    return {"items": [dict(r) for r in rows], "total": total}

def get_appraisal_by_id(appraisal_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM appraisals WHERE id = ? AND user_id = ? AND status != 'archived'", (appraisal_id, user_id))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def delete_appraisal(appraisal_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE appraisals SET status = 'archived' WHERE id = ? AND user_id = ?", (appraisal_id, user_id))
    conn.commit()
    success = c.rowcount > 0
    conn.close()
    return success

def get_dashboard_stats(user_id):
    conn = get_connection()
    c = conn.cursor()
    
    # Total
    c.execute("SELECT COUNT(*) FROM appraisals WHERE user_id = ? AND status != 'archived'", (user_id,))
    total = c.fetchone()[0]
    
    # Approved
    c.execute("SELECT COUNT(*) FROM appraisals WHERE user_id = ? AND decision = 'APPROVE' AND status != 'archived'", (user_id,))
    approved = c.fetchone()[0]
    
    # Declined
    c.execute("SELECT COUNT(*) FROM appraisals WHERE user_id = ? AND decision = 'DECLINE' AND status != 'archived'", (user_id,))
    declined = c.fetchone()[0]
    
    # Avg Score
    c.execute("SELECT AVG(final_score) FROM appraisals WHERE user_id = ? AND status != 'archived'", (user_id,))
    avg_score_row = c.fetchone()[0]
    avg_score = round(avg_score_row, 1) if avg_score_row else 0.0
    
    # This month
    current_month = datetime.now().strftime("%Y-%m")
    c.execute("SELECT COUNT(*) FROM appraisals WHERE user_id = ? AND status != 'archived' AND created_at LIKE ?", (user_id, f"{current_month}%"))
    this_month = c.fetchone()[0]
    
    approval_rate = round((approved / total * 100), 1) if total > 0 else 0.0
    
    conn.close()
    return {
        "total_appraisals": total,
        "approved_count": approved,
        "declined_count": declined,
        "avg_score": avg_score,
        "this_month_count": this_month,
        "approval_rate": approval_rate
    }

def update_user_profile(user_id, full_name, org, email, role=None):
    conn = get_connection()
    c = conn.cursor()
    if role:
        c.execute("""
            UPDATE users 
            SET full_name = ?, organization = ?, email = ?, role = ?
            WHERE id = ?
        """, (full_name, org, email, role, user_id))
    else:
        c.execute("""
            UPDATE users 
            SET full_name = ?, organization = ?, email = ?
            WHERE id = ?
        """, (full_name, org, email, user_id))
    conn.commit()
    success = c.rowcount > 0
    conn.close()
    return success

def update_user_password(user_id, new_password):
    conn = get_connection()
    c = conn.cursor()
    pwd_hash = hash_password(new_password)
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pwd_hash, user_id))
    conn.commit()
    success = c.rowcount > 0
    conn.close()
    return success

def get_portfolio_analytics(user_id):
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Sector Performance
    c.execute("""
        SELECT sector, COUNT(*) as count, AVG(final_score) as avg_score,
        SUM(CASE WHEN decision = 'APPROVE' THEN 1 ELSE 0 END) as approved
        FROM appraisals WHERE user_id = ? AND status != 'archived'
        GROUP BY sector
    """, (user_id,))
    sectors = [dict(r) for r in c.fetchall()]
    
    # 2. Score Distribution (buckets of 10)
    c.execute("""
        SELECT (CAST(final_score/10 AS INTEGER)*10) as bucket, COUNT(*) as count
        FROM appraisals WHERE user_id = ? AND status != 'archived'
        GROUP BY bucket
    """, (user_id,))
    distribution = [dict(r) for r in c.fetchall()]
    
    # 3. Monthly Trends
    c.execute("""
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count, AVG(final_score) as avg_score
        FROM appraisals WHERE user_id = ? AND status != 'archived'
        GROUP BY month ORDER BY month ASC LIMIT 12
    """, (user_id,))
    trends = [dict(r) for r in c.fetchall()]
    
    # 4. Decision Split
    c.execute("""
        SELECT decision, COUNT(*) as count
        FROM appraisals WHERE user_id = ? AND status != 'archived'
        GROUP BY decision
    """, (user_id,))
    decisions = [dict(r) for r in c.fetchall()]
    
    # 5. KPI Metrics
    c.execute("""
        SELECT 
            SUM(credit_limit_cr) as total_vol,
            AVG(interest_rate) as avg_rate,
            COUNT(*) as total_count,
            SUM(CASE WHEN decision = 'APPROVE' THEN 1 ELSE 0 END) as approved_count
        FROM appraisals 
        WHERE user_id = ? AND status != 'archived'
    """, (user_id,))
    kpis = dict(c.fetchone())
    
    total_vol = round(kpis.get('total_vol') or 0, 2)
    avg_rate = round(kpis.get('avg_rate') or 0, 1)
    total_count = kpis.get('total_count') or 0
    approved_count = kpis.get('approved_count') or 0
    approval_rate = round((approved_count / total_count * 100), 1) if total_count > 0 else 0.0
    
    conn.close()
    return {
        "sector_performance": sectors,
        "score_distribution": distribution,
        "monthly_trends": trends,
        "decision_split": decisions,
        "total_credit_approved_cr": total_vol,
        "avg_interest_rate": avg_rate,
        "approval_rate": approval_rate
    }
