import os
import sqlite3
import json
# import razorpay
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, Response

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_in_production'

@app.template_filter('datetime_12hr')
def datetime_12hr_filter(value):
    if not value: return ""
    try:
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%b %d, %Y %I:%M %p')
    except ValueError:
        return value

# Load config once on startup for performance
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

# Load it globally into app config
app.config['SITE_CONFIG'] = load_config()

# Setup Razorpay client
rzp_client = None
payment_config = app.config['SITE_CONFIG'].get('payment', {})
# if payment_config.get('enabled'):
#     try:
#         rzp_client = razorpay.Client(auth=(payment_config['razorpay_key_id'], payment_config['razorpay_key_secret']))
#     except Exception as e:
#         print(f"Error initializing Razorpay: {e}")

# Setup SQLite Database
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                date TEXT NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Add payment tracking columns safely if they don't exist
        try:
            conn.execute("ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'Pending'")
            conn.execute("ALTER TABLE appointments ADD COLUMN order_id TEXT")
        except sqlite3.OperationalError:
            pass # Columns exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                review TEXT NOT NULL,
                rating INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
init_db()

# Ensure images directory exists for dynamic uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
GALLERY_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'gallery')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)

# Make global context available to all templates natively
@app.context_processor
def inject_globals():
    gallery_files = []
    if os.path.exists(GALLERY_FOLDER):
        gallery_files = os.listdir(GALLERY_FOLDER)
    return dict(config=app.config['SITE_CONFIG'], gallery_files=gallery_files)

# Security: HTTP Basic Auth helper for Admin
def check_auth(username, password):
    """This function is called to check if a username / password combination is valid."""
    admin_pass = app.config['SITE_CONFIG'].get('admin_password', 'admin')
    return username == 'admin' and password == admin_pass

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# Routes
@app.route('/')
def index():
    db_reviews = []
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM reviews ORDER BY created_at DESC')
            db_reviews = [{'name': r['name'], 'review': r['review'], 'rating': r['rating']} for r in cur.fetchall()]
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        
    return render_template('index.html', db_reviews=db_reviews)

@app.route('/add_review', methods=['POST'])
def add_review():
    name = request.form.get('name', '').strip()
    review = request.form.get('review', '').strip()
    rating = request.form.get('rating', '5').strip()
    
    if not name or not review:
        flash("Name and review are required.", "error")
        return redirect(url_for('index') + "#reviews")
        
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = 5
            
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('INSERT INTO reviews (name, review, rating) VALUES (?, ?, ?)', (name, review, rating))
        flash("Thank you! Your review has been submitted.", "success")
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred. Please try again later.", "error")
        
    return redirect(url_for('index') + "#reviews")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        date = request.form.get('date', '').strip()
        message = request.form.get('message', '').strip()
        
        # 6. Basic Security / Validation
        if not name or not phone or not date:
            flash("Please fill all required fields (Name, Phone, Date)", "error")
            return redirect(url_for('contact'))
            
        try:
            order_id = ""
            status = "Confirmed" # Payment bypass
            payment_cfg = app.config['SITE_CONFIG'].get('payment', {})
            
            # Create razorpay order
            # if payment_cfg.get('enabled') and rzp_client:
            #     amount = int(payment_cfg.get('fee', 500)) * 100
            #     order = rzp_client.order.create({
            #         "amount": amount,
            #         "currency": payment_cfg.get("currency", "INR"),
            #         "payment_capture": "1"
            #     })
            #     order_id = order['id']
            # else:
            #     status = "Confirmed" # No payment required
                
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    'INSERT INTO appointments (name, phone, email, date, message, status, order_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (name, phone, email, date, message, status, order_id)
                )
                
            if order_id:
                return render_template('payment.html', order_id=order_id, name=name, email=email, phone=phone)
                
            flash("Your appointment request has been submitted successfully!", "success")
            return redirect(url_for('contact'))
        except Exception as e:
            print(f"Database error: {e}")
            flash("An error occurred. Please try again later.", "error")
            return redirect(url_for('contact'))
            
    return render_template('contact.html')

@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    '''
    payment_id = request.form.get('razorpay_payment_id', '')
    order_id = request.form.get('razorpay_order_id', '')
    signature = request.form.get('razorpay_signature', '')
    
    if rzp_client and order_id and signature:
        try:
            rzp_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE appointments SET status = 'Paid' WHERE order_id = ?", (order_id,))
            flash("Payment Successful! Your appointment is confirmed.", "success")
        except Exception as e:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE appointments SET status = 'Failed' WHERE order_id = ?", (order_id,))
            flash("Payment verification failed. Please contact us.", "error")
    '''
    return redirect(url_for('index'))

@app.route('/admin')
@requires_auth
def admin():
    # Fetch all appointments
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM appointments ORDER BY created_at DESC')
            appointments = cur.fetchall()
    except Exception as e:
        appointments = []
        print(f"Error fetching appointments: {e}")
        
    admin_gallery = []
    if os.path.exists(GALLERY_FOLDER):
        admin_gallery = os.listdir(GALLERY_FOLDER)
        
    return render_template('admin.html', appointments=appointments, admin_gallery=admin_gallery)

@app.route('/admin/upload_gallery', methods=['POST'])
@requires_auth
def upload_gallery():
    if 'gallery_files' in request.files:
        files = request.files.getlist('gallery_files')
        for file in files:
            if file.filename != '':
                file.save(os.path.join(GALLERY_FOLDER, file.filename))
        flash("Gallery files uploaded successfully!", "success")
    return redirect(url_for('admin'))

@app.route('/admin/delete_gallery/<filename>', methods=['POST'])
@requires_auth
def delete_gallery(filename):
    file_path = os.path.join(GALLERY_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"Removed {filename} from gallery.", "success")
    return redirect(url_for('admin'))

@app.route('/admin/upload', methods=['POST'])
@requires_auth
def upload_image():
    if 'hero_image' in request.files:
        file = request.files['hero_image']
        if file.filename != '':
            file.save(os.path.join(UPLOAD_FOLDER, 'hero.jpg'))
            flash("Hero image updated successfully!", "success")
            
    if 'doctor_image' in request.files:
        file = request.files['doctor_image']
        if file.filename != '':
            file.save(os.path.join(UPLOAD_FOLDER, 'doctor.jpg'))
            flash("Doctor image updated successfully!", "success")
            
    return redirect(url_for('admin'))

@app.route('/admin/delete_appointment/<int:appointment_id>', methods=['POST'])
@requires_auth
def delete_appointment(appointment_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
        flash("Appointment removed successfully.", "success")
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        flash("Could not remove appointment.", "error")
    return redirect(url_for('admin'))

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
