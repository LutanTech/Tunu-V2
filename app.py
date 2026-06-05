from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import string, secrets
from datetime import datetime, timedelta
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from functools import wraps
from flask_mail import Message

from emailer import send_welcome_message, send_reminder, send_weekend_wish
from utils import generate_token, verify_token
import os
import json

from flask_mail import Mail


app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'info.tunupublishers@gmail.com'
app.config['MAIL_PASSWORD'] = 'koax xipw fpvz neni'
app.config['MAIL_DEFAULT_SENDER'] = ('Tunu Publishers', 'info.tunupublishers@gmail.com')

mail = Mail(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tunu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
SHORTCODE = os.getenv("MPESA_SHORTCODE")
PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")



db = SQLAlchemy(app)
CORS(app)

migrate = Migrate(app, db)

# ========================
# UTIL
# ========================
def generate_id(prefix='STF', length=6):
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}-{suffix}"


# ========================
# MODELS
# ========================
class Staff(db.Model):
    id = db.Column(db.String(20), primary_key=True, default=lambda: generate_id('STF', 6))
    name = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(128), nullable=True, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    location = db.Column(db.String(128), default='Nairobi')
    added_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))
    added_by = db.Column(db.String(20), db.ForeignKey('staff.id'), nullable=True)
    password = db.Column(db.String(), nullable=False, default=generate_password_hash('#TunuStaff2026'))
    must_change = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    tkv = db.Column(db.String(10), nullable=False, default=lambda:generate_id('T', 6))

    def to_user_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'joined': self.added_at,
        }

    def to_admin_dict(self):
        ref = Staff.query.filter_by(id=self.added_by).first()
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'joined': self.added_at,
            'added_by': ref.name if ref else 'Undefined',
            'tkv':self.tkv
        }


class Book(db.Model):
    id = db.Column(db.String(20), primary_key=True, default=lambda: generate_id('BK', 4))
    title = db.Column(db.String(512), nullable=False)
    image = db.Column(db.String(), default='https://i.ibb.co/CKRYPD4p/image.png')
    added_by = db.Column(db.String(20), db.ForeignKey('staff.id'), nullable=False)
    grade = db.Column(db.String(512), nullable=False)
    authors = db.Column(db.Text, nullable=False)
    added_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))
    discounted = db.Column(db.Boolean, default=False)
    oldPrice = db.Column(db.Float, default=0)
    newPrice = db.Column(db.Float, default=0)
    edited_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))
    edited_by = db.Column(db.String(20), db.ForeignKey('staff.id'), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)


    def to_sale_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.image,
            'added_by': self.added_by,
            'added_at': self.added_at,
            'oldPrice': self.oldPrice,
            'newPrice': self.newPrice,
            'grade':self.grade,
            'authors':self.authors
        }

    def to_admin_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.image,
            'added_by': self.added_by,
            'added_at': self.added_at,
            'oldPrice': self.oldPrice,
            'newPrice': self.newPrice,
            'edited_at': self.edited_at,
            'edited_by': self.edited_by,
            'authors':self.authors,
            'grade':self.grade
            
        }


class Submission(db.Model):
    id = db.Column(db.String(20), primary_key=True, default=lambda: generate_id('SUB', 4))
    staffName = db.Column(db.String(128), nullable=False)
    visitLocation = db.Column(db.String(1024), nullable=False)
    locationPhone = db.Column(db.String(20), nullable=True)
    locationEmail = db.Column(db.String(20), nullable=True)
    saleComments = db.Column(db.String(), nullable=True)
    isSold = db.Column(db.Boolean, default=False)
    bookId = db.Column(db.String(), db.ForeignKey('book.id'))
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))

    def to_dict(self):
        book = Book.query.filter_by(id=self.bookId).first()
        return {
            'staffName': self.staffName,
            'visitLocation': self.visitLocation,
            'isSold': self.isSold,
            'locationPhone': self.locationPhone,
            'bookName': book.title if book else 'Invalid',
            'timestamp': self.submitted_at,
            'saleComments': self.saleComments
        }


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    staff_id = db.Column(db.String(20), db.ForeignKey('staff.id'), nullable=True)
    action = db.Column(db.String(256), nullable=False)

    method = db.Column(db.String(10))
    endpoint = db.Column(db.String(256))
    ip = db.Column(db.String(50))
    user_agent = db.Column(db.String(512))

    status_code = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=3))

    def to_dict(self):
        staff = Staff.query.filter_by(id=self.staff_id).first()
        return {
            'id': self.id,
            'staff': staff.name if staff else 'Anonymous',
            'action': self.action,
            'method': self.method,
            'endpoint': self.endpoint,
            'ip': self.ip,
            'user_agent': self.user_agent,
            'status': self.status_code,
            'time': self.timestamp
        }

class Order(db.Model):
    id = db.Column(db.String(50), default=lambda: generate_id('ORD',length=10), primary_key=True)
    temp_id = db.Column(db.String(512))
    data = db.Column(db.JSON)
    name = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(512), nullable=True)
    address = db.Column(db.String(1024), nullable=True)
    grand_total = db.Column(db.Float(1024), nullable=True)
    address = db.Column(db.String(1024), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(14), nullable=True)
    checkout_request_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(255), nullable=True, default='PENDING')
    
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=3)
    )
    
    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'city':self.city,
            'phone':self.phone,
            'email':self.email,
            'created':self.created_at,
            'address':self.address,
            'data':self.data
        }
# ========================
# LOGGING
# ========================
def log_action(action, status_code=200, staff_id=None):
    try:
        log = Log(
            staff_id=staff_id,
            action=action,
            method=request.method,
            endpoint=request.path,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status_code=status_code
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print("Manual log failed:", e)

def get_bearer_token():
    auth = request.headers.get("Authorization")

    if not auth:
        return None

    parts = auth.split(" ")

    if len(parts) != 2:
        return None

    if parts[0].lower() != "bearer":
        return None

    return parts[1]


def protected(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        token = get_bearer_token()
        uid = request.headers.get("X-UID")

        if not token:
            return jsonify({"error": "missing token"}), 401

        if not uid:
            return jsonify({"error": "missing uid"}), 401

        staff = Staff.query.filter_by(id=uid).first()

        if not staff:
            return jsonify({"error": "invalid token"}), 403

        if str(staff.id) != str(uid):
            return jsonify({"error": "uid mismatch"}), 403

        return f(staff, *args, **kwargs)

    return wrapper


def check_admin(staff_id):
    staff = Staff.query.filter_by(id=staff_id).first()
    
    if not staff.is_admin:
        return False
    else :
        return True

# @app.after_request
def log_every_request(response):
    try:
        log = Log(
            action=f"{request.method} {request.path}",
            method=request.method,
            endpoint=request.path,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            status_code=response.status_code
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print("Auto log failed:", e)

    return response


@app.route('/admin/api/toggle/staff')
@protected
def toggle_staff(adm):
    data = request.get_json()
    id = data.get('staff_id')
    if not id:
        return jsonify({'error':'Missing data in request'}), 404
    if not adm.is_super_admin:
        return jsonify({'error':'Unauthorized'}), 401
    
    staff = Staff.query.filter_by(id=id).first()
    if not staff:
        return jsonify({'error':'Staff not found in Database'}), 404
    if staff.is_super_admin:
        return jsonify({'error':'You do not have enough permisions to execute this action'}), 401
    staff.is_active = not staff.is_active
    db.session.commit()
    return jsonify({'msg':'Staff toggled successfully'}), 200
    

@app.route('/admin/api/send_email/test')
def send_email():
    staff = Staff.query.filter_by(id='ADM-0001').first()
    try:
        send_welcome_message(staff)
        return jsonify({'msg':'Sent'})
    except Exception as e:
        return jsonify({'error':'Failed to send'}), 500
    

@app.route('/admin/api/send-wishes', methods=['GET'])
def global_weekend_wishes():
    all_submissions = Submission.query.filter(Submission.locationEmail != None).all()

    if not all_submissions:
        return jsonify({'msg': 'No customer emails found in Submissions'}), 404

    contact_list = [(s.locationEmail, s.visitLocation) for s in all_submissions]

    try:
        count = send_weekend_wish(contact_list)
        
        admin_id = request.json.get('admin_id', 'SYSTEM')
        log_action(f"Sent global weekend wishes to {count} customers", 200, admin_id)
        
        return jsonify({'msg': f'Successfully sent wishes to {count} customers'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/send-reminders')
def bulk_reminder():
    admin_id =  'ADM-0001'
    
    staff_members = Staff.query.filter_by(is_active=True).all()
    email_list = [s.email for s in staff_members if s.email]

    if not email_list:
        return jsonify({'msg': 'No staff emails found'}), 404

    try:
        success = send_reminder(email_list)
        
        if success:
            log_action(f"Sent bulk reminders to {len(email_list)} staff", 200, admin_id)
            return jsonify({'msg': f'Reminders sent to {len(email_list)} staff members'})
        else:
            return jsonify({'error': 'Mail server rejected the request'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
# ========================
# ROUTES
# ========================
@app.route('/create_dummy', methods=['GET'])
def dummy():
    
    bk1 = Book(title='Favoured by Grace', added_by='STF-453Y70', discounted=True, oldPrice=630.00, newPrice=420.00, grade='4', authors='Regina Ebenezer')
    bk2 = Book(title='Kudurusu Kiswahili', added_by='STF-4R67H0', discounted=False, oldPrice=630.00, newPrice=630.00, grade='7', authors='Dr.Sussy Nandama ')
    
    admin = Staff(name='ADMIN', id='ADM-0001', phone='0711808286', email='lutancorpinfoteam@gmail.com', location='pipeline', password=generate_password_hash('000000'), is_admin=True)

    db.session.add(bk1)
    db.session.add(bk2)
    db.session.add(admin)
    db.session.commit()

    return jsonify({'status': 200})


@app.route('/get_books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify({'rating': [b.to_sale_dict() for b in books if not b.is_deleted]})


@app.route('/get_subs', methods=['GET'])
@protected
def get_subs():
    subs = Submission.query.all()
    return jsonify({'subs': [s.to_dict() for s in subs]})


@app.route('/api/login/auth/0', methods=['POST'])
def login():
    data = request.get_json()
    exists = Book.query.filter_by(title='Favoured by Grace').first()
    
    if not exists:
        dummy()

    if not data:
        log_action("Login failed: no data received", 400)
        return jsonify({'error': 'Incomplete request'}), 400

    id = data.get('id')
    password = data.get('password')

    if not id or not password:
        log_action("Login failed: missing fields", 400)
        return jsonify({'error': 'All fields required'}), 400

    staff = Staff.query.filter_by(id=id).first()

    if not staff:
        log_action("Login failed: invalid id", 400)
        return jsonify({'error': 'Invalid credentials'}), 400

    if not check_password_hash(staff.password, password):
        log_action("Login failed: wrong password", 401, staff.id)
        return jsonify({'error': 'Invalid credentials'}), 401

    # log_action("Login success", 200, staff.id)

    return jsonify({
        'staff': {
            'token': generate_token(staff.id, generate_id('T', 6)),
            'id': staff.id,
            'msg':'Logged in successfully'
        }
    }), 200


@app.route('/admin/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Incomplete request'}), 400

    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    location = data.get('location')
    added_by = data.get('added_by')

    if Staff.query.filter_by(phone=phone).first():
        return jsonify({'error': 'Phone already exists'}), 400

    if email and Staff.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    admin = Staff.query.filter_by(id=added_by).first()

    if not admin or not admin.is_admin:
        return jsonify({'error': 'Unauthorized'}), 401

    new_staff = Staff(
        name=name,
        phone=phone,
        email=email,
        location=location,
        added_by=admin.id
    )

    db.session.add(new_staff)
    db.session.commit()

    log_action("Created staff", 200, admin.id)

    return jsonify({'msg': f'Staff {name} created'})

@app.route('/api/create_order', methods=['POST'])
def create_order():
    data = request.get_json()

    cart = data.get('cart', [])
    temp_id = data.get('temp_id')

    if not cart:
        return jsonify({
            'error': 'Cart is empty'
        }), 400

    try:
        order = Order(
            temp_id=temp_id,
            data=cart
        )

        db.session.add(order)
        db.session.commit()

        return jsonify({
            'success': True,
            'order_id': order.id
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

import requests
from flask import request, jsonify
from flask_mail import Message

def format_phone(phone):
    phone = str(phone).replace("+", "").strip()

    if phone.startswith("0"):
        phone = "254" + phone[1:]

    elif phone.startswith("7"):
        phone = "254" + phone

    return phone

def initiate_payment(phone, amount):
    print(phone, amount)
    try:
        response = requests.post(
            'https://app.tunupublishers.com/api/pay',
            json={
                'phone': format_phone(phone),
                'amount': amount
            },
            timeout=30
        )

        return response.json()

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
        
counties = [
    "Nairobi","Kiambu","Machakos","Kajiado","Murang'a",
    "Nakuru","Nyeri","Kirinyaga","Nyandarua","Embu","Tharaka Nithi","Meru","Laikipia","Narok","Bomet","Kericho","Makueni",
    "Mombasa","Kwale","Kilifi","Tana River","Lamu","Taita Taveta",
    "Garissa","Wajir","Mandera","Marsabit","Isiolo","Kitui",
    "Turkana","West Pokot","Samburu","Trans Nzoia","Uasin Gishu",
    "Elgeyo Marakwet","Nandi","Baringo","Kakamega","Vihiga",
    "Bungoma","Busia","Siaya","Kisumu","Homa Bay","Migori",
    "Kisii","Nyamira"
]

def shipping_fee(county):
    c = county.strip()

    near = {"Nairobi","Kiambu","Machakos","Kajiado","Murang'a"}

    if c in near:
        return 250

    if c in counties[:17]: 
        return 300

    return 400

@app.route('/api/checkout', methods=['POST'])
def checkout():
    try:
        payload = request.get_json()

        if not payload:
            return jsonify({"error": "Invalid payload"}), 400

        name = payload.get("name")
        email = payload.get("email")
        phone = payload.get("phone")
        county = payload.get("county")
        address = payload.get("addr")
        order_id = payload.get("order_id")

        if not all([name, email, phone, county, address, order_id]):
            return jsonify({"error": "Missing fields"}), 400

        # Fetch order
        ord = Order.query.filter_by(id=order_id).first()

        if not ord:
            return jsonify({"error": "Order not found"}), 404

        # Order data expected:
        # [{"id":"BK-98VH","qty":2}, {"id":"BK-E27D","qty":1}]
        items = ord.data

        subtotal = 0
        purchased_books = []

        for item in items:
            book = Book.query.filter_by(id=item["id"]).first()

            if not book:
                continue

            qty = int(item.get("qty", 1))
            line_total = book.newPrice * qty

            subtotal += line_total

            purchased_books.append({
                "id": book.id,
                "title": book.title,
                "price": book.newPrice,
                "qty": qty,
                "total": line_total
            })

        if subtotal <= 0:
            return jsonify({"error": "No valid books found"}), 400

        shipping = shipping_fee(county)
        grand_total = subtotal + shipping

        payment_res = initiate_payment(phone, grand_total)

        if payment_res.get("ResponseCode") != "0":
            return jsonify({
                "error": "STK push failed",
                "details": payment_res
            }), 400

        checkout_request_id = payment_res.get("CheckoutRequestID")

        checkout_order = Order(
            name=name,
            email=email,
            phone=phone,
            city=county,
            address=address,
            grand_total=grand_total,
            checkout_request_id=checkout_request_id,
            status="PENDING"
        )

        db.session.add(checkout_order)
        db.session.commit()

        return jsonify({
            "message": "STK push sent",
            "checkout_request_id": checkout_request_id,
            "subtotal": subtotal,
            "shipping": shipping,
            "amount": grand_total,
            "items": purchased_books
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/admin/api/get_books', methods=['GET'])
@protected
def get_admin_books(staff):
    if not check_admin(staff.id):
        return jsonify({'error':'Permission denied'}), 401
    books = Book.query.all()
    return jsonify({'books': [ b.to_admin_dict() for b in books if not b.is_deleted ]}), 200

@app.route('/admin/api/logs', methods=['GET'])
@protected
def get_logs(staff):
    if not check_admin(staff.id):
        return jsonify({'error':'Permission denied'}), 401
        
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return jsonify({'logs': [l.to_dict() for l in logs]})

@app.route('/api/books/add', methods=['POST'])
@protected
def add_book(staff):
    if not check_admin(staff.id):
        return jsonify({'error':'Permission denied'}), 401
    data = request.get_json()

    image = data.get("image")

    book = Book(
        title=data.get("title"),
        image=image or "https://i.ibb.co/CKRYPD4p/image.png",
        added_by="SYSTEM",
        oldPrice=data.get("oldPrice") or 0,
        newPrice=data.get("newPrice"),
        discounted=data.get("discounted"),
        grade = data.get('grade'),
        authors=data.get('authors')
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({"msg": "Book added"}), 200
# ========================
# RUN
# ========================

from flask import send_from_directory

@app.route('/api/book-cover/<path:filename>')
def book_cover(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/admin/api/edit', methods=['POST'])
def edit_book():

    raw = request.get_json()
    data = raw.get('data')


    book = Book.query.filter_by(id=data.get('id')).first()

    if not book:
        return jsonify({'error': 'Book to be edited not found'}), 404

    try:
        book.title = data.get("title")
        book.added_by = "SYSTEM"
        book.oldPrice = data.get("oldPrice") or 0
        book.newPrice = data.get("newPrice")
        book.discounted = data.get("discounted")
        book.grade = data.get("grade")
        book.image = data.get("image")
        book.authors = data.get("authors")

        db.session.commit()

        return jsonify({'msg': 'Edited successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to edit {str(e)}'}), 500

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join("resources", "books", "covers")

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image = request.files['image']

        if image.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        filename = secure_filename(image.filename)

        name, ext = os.path.splitext(filename)
        filename = f"{generate_id('IMG', 8)}{ext}"

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        image.save(filepath)

        

        return jsonify({
            'msg': 'Uploaded successfully',
            'path': filepath.replace("\\", "/")
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/delete_book', methods=['POST'])
@protected
def delete_book(staff):
    if not check_admin(staff.id):
        return jsonify({'error':'Permission denied'}), 401
    
    data = request.get_json()
    id = data.get('id')
    
    book = Book.query.filter_by(id=id).first()
    if not book:
        return jsonify({'error':'Book not found'}), 404
    try:
        book.is_deleted = True
        book.deleted_at = datetime.utcnow() + timedelta(hours=3)
        db.session.commit()
        return jsonify({'msg':'Book deleted successfully'}),200
    except Exception as e:
        return jsonify({'error':f'Database error: {str(e)}'}), 500

@app.route('/admin/api/authorize', methods=['POST'])
@protected
def authorize_admin(staff):
    if not check_admin(staff.id):
       return jsonify({'error':'Authorization failed'}), 401
    else:
        return jsonify({'msg':f'Welcome back {staff.name}'}), 200


# @app.route('/admin/api/add-staff', methods=['POST'])
# @protected
# def add_staff():
#     data = request.get_json()
    
#     if not data:
#         return jsonify({'error':'Incomplete request. Please try again'}), 404
#     new_staff = Staff(name=data.get(""))
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
    