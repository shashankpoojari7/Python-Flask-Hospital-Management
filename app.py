import cloudinary.uploader
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload
from sqlalchemy import Date, String, ForeignKey
from datetime import date, datetime
import re
import secrets
import cloudinary
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = secrets.token_hex(32)

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)  
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date(), nullable=False)
    image_filename: Mapped[str] = mapped_column(String(100)) 
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    
    blood_group: Mapped[str] = mapped_column(String(5), nullable=False)
    emergency_contact: Mapped[str] = mapped_column(String(20), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False)  
    
    doctor_profile: Mapped["Doctor"] = relationship("Doctor", back_populates="user", uselist=False)

class Appointment(db.Model):
    __tablename__ = "appointments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    patient_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_details:Mapped[str] = mapped_column(String(200), nullable=False)
    status:Mapped[str] = mapped_column(String(200), nullable=False)
    
    patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id], backref="patient_appointments")
    doctor: Mapped["User"] = relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")

class Prescription(db.Model):
    __tablename__ = "prescriptions"
    
    id: Mapped[int] = mapped_column(primary_key = True)
    
    appointment_id: Mapped[int] = mapped_column(ForeignKey('appointments.id'), nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    prescriptions :Mapped[str] = mapped_column(String(200),nullable = True)
    
    patient: Mapped["User"] = relationship("User", foreign_keys=[patient_id], backref="patient_prescriptions")
    doctor: Mapped["User"] = relationship("User", foreign_keys=[doctor_id], backref="doctor_prescriptions")
    
    def __repr__(self):
        return f"<User {self.id}: {self.fullname}>"

class Doctor(db.Model):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[str] = mapped_column(String(100), nullable=False)
    experience: Mapped[str] = mapped_column(String(10), nullable=False)
    license_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hospital_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str] = mapped_column(String(300), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="doctor_profile")

with app.app_context():
    db.create_all()


@app.route('/')
def main():
    return render_template('Home.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        dob_str = request.form['dob']
        gender = request.form.get('gender')
        address = request.form['address']
        blood_group = request.form['blood_group']
        emergency_contact = request.form['emergency_contact']
        image = request.files['image']

        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

        emailCheck = User.query.filter_by(email=email).first()
        phoneCheck = User.query.filter_by(phone=phone).first()

        errors = {}
        if len(fullname) < 3:
            errors['fullname'] = "Name must contain more than 3 characters."
        if emailCheck:
            errors['email'] = "This email is already linked to another account. Try a different one!"
        if not phone.isdigit() or len(phone) != 10:
            errors['phone'] = "Please enter a valid 10-digit phone number."
        if phoneCheck:
            errors['phone'] = "This phone number is already in use."
        if not re.fullmatch(r'^(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$', password):
            errors['password'] = "Password must contain at least 8 characters with a digit & special character."
        if not (date(1900, 1, 1) <= dob <= date.today()):
            errors['dob'] = "Please enter a valid date of birth."
        if not gender:
            errors['gender'] = "Select a gender."
        if not blood_group:
            errors['blood_group'] = "Select your blood group."
        if not emergency_contact or not emergency_contact.isdigit() or len(emergency_contact) != 10:
            errors['emergency_contact'] = "Enter a valid 10-digit emergency contact."

        if not errors:
            image_url = ''
            if image:
                res = cloudinary.uploader.upload(image)
                image_url = res['secure_url']
            user = User(
                fullname=fullname,
                email=email,
                password=password,
                phone=phone,
                date_of_birth=dob,
                gender=gender,
                address=address,
                blood_group=blood_group,
                emergency_contact=emergency_contact,
                image_filename=image_url,
                role="Patient"
            )
            db.session.add(user)
            db.session.commit()

            session.permanent = True
            session['id'] = user.id
            session['name'] = user.fullname
            session['role'] = "Patient"
            flash("Registration successful! Please log in to continue.", "success")
            return redirect(url_for('login'))
        return render_template('register.html', errors=errors, form=request.form)
    return render_template('register.html', form={})


@app.route('/doctor-register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        fullname = request.form['fullname'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        password = request.form['password'].strip()
        dob_str = request.form['dob'].strip()
        gender = request.form.get('gender').strip()
        address = request.form['address'].strip()
        blood_group = request.form['blood_group']
        emergency_contact = request.form['emergency_contact'].strip()
        image = request.files['image']

        specialization = request.form['specialization'].strip()
        qualification = request.form['qualification'].strip()
        experience = request.form['experience'].strip()
        license_number = request.form['license_number'].strip()
        hospital_name = request.form['hospital_name'].strip()
        bio = request.form.get('bio', '').strip()

        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        emailCheck = User.query.filter_by(email=email).first()
        phoneCheck = User.query.filter_by(phone=phone).first()
        licenseCheck = Doctor.query.filter_by(license_number=license_number).first()

        errors = {}

        if len(fullname) < 3:
            errors['fullname'] = "Name must contain more than 3 characters."
        if emailCheck:
            errors['email'] = "This email is already linked to another account. Try a different one!"
        if not phone.isdigit() or len(phone) != 10:
            errors['phone'] = "Please enter a valid 10-digit phone number."
        if phoneCheck:
            errors['phone'] = "This phone number is already in use."
        if not re.fullmatch(r'^(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$', password):
            errors['password'] = "Password must contain at least 8 characters with a digit & special character."
        if not (date(1900, 1, 1) <= dob <= date.today()):
            errors['dob'] = "Please enter a valid date of birth."
        if not gender:
            errors['gender'] = "Select a gender."
        if not blood_group:
            errors['blood_group'] = "Select your blood group."
        if not emergency_contact or not emergency_contact.isdigit() or len(emergency_contact) != 10:
            errors['emergency_contact'] = "Enter a valid 10-digit emergency contact."

        if not specialization:
            errors['specialization'] = "Please enter specialization."
        if not qualification:
            errors['qualification'] = "Please enter qualification."
        if not experience or not experience.isdigit():
            errors['experience'] = "Please enter years of experience as a number."
        if not license_number:
            errors['license_number'] = "License number is required."
        if licenseCheck:
            errors['license_number'] = "This license number is already registered."
        if not hospital_name:
            errors['hospital_name'] = "Please enter hospital or clinic name."

        if not errors:
            image_url = ''
            if image:
                res = cloudinary.uploader.upload(image)
                image_url = res['secure_url']
            user = User(
                fullname=fullname,
                email=email,
                password=password,
                phone=phone,
                date_of_birth=dob,
                gender=gender,
                address=address,
                blood_group=blood_group,
                emergency_contact=emergency_contact,
                image_filename=image_url,
                role="Doctor"
            )
            db.session.add(user)
            db.session.commit()

            doctor = Doctor(
                user_id=user.id,
                specialization=specialization,
                qualification=qualification,
                experience=experience,
                license_number=license_number,
                hospital_name=hospital_name,
                bio=bio
            )
            db.session.add(doctor)
            db.session.commit()

            session.permanent = True
            session['id'] = user.id
            session['name'] = user.fullname
            flash("Registration successful, Doctor! Please log in to access your dashboard.", "success")
            return redirect(url_for('login'))
        return render_template('doctor-register.html', errors=errors, form=request.form)
    return render_template('doctor-register.html', form={})


@app.route('/login',methods =['POST','GET'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'].strip()
        password = request.form['password'].strip()

        user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

        if user and user.password == password:
            session.permanent = True
            session['id'] = user.id
            session['name'] = user.fullname
            session['role'] = user.role
            flash("Logged in successfully.","success")
            if user.role == 'Patient':
                return redirect(url_for('patient', page_name='your-appointments'))
            if user.role == 'Doctor':
                return redirect(url_for('doctor',page_name='your-appointments'))
        else:
            flash("Invalid login credentials.","error")
            return render_template('login.html', identifier = identifier)
    return render_template('login.html', identifier='', form = {})


@app.route('/patient/dashboard/<page_name>')
def patient(page_name):
    user_id = session.get('id')
    if not user_id:
        flash("Session expired. Please log in again.", "warning")
        return redirect('/login')
    user = User.query.filter_by(id=user_id).first()
    doctor = User.query.filter_by(role = "doctor").all()
    appointments = Appointment.query.filter_by(patient_id=user_id).order_by(Appointment.appointment_date.asc()).all()
    
    pages = {
        'your-appointments': 'your-appointments.html',
        'book-appointments': 'book-appointments.html',
        'profile': 'profile.html'
    }
    if page_name not in pages:
        return "<h1>404 - Page Not Found</h1>", 404

    return render_template(pages[page_name],
                            user=user,
                            doctor=doctor,
                            appointments=appointments)


@app.route('/patient/dashboard/create-appointment',methods = ['POST','GET'])
def create_appointment():
    if request.method == "POST":
        doctor = request.form['doctor']
        appointment_date = request.form['appointment_date']
        appointment_details = request.form['appointment_details']
        patient = user_id = session.get('id')
        if not user_id:
            flash("Session expired. Please log in again.", "warning")
            return redirect('/login')
        selected_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        if selected_date < date.today():
            flash(" Appointments cannot be scheduled for past dates. Please select today or a future date.", "error")
            return redirect(url_for('patient', page_name='book-appointments'))
        count = Appointment.query.filter_by(doctor_id=doctor, appointment_date=appointment_date).count()
        if count>=10:
            flash("Cannot place appointment. Doctor already has 10 appointments on this date.","warning")
            return redirect(url_for('patient', page_name='book-appointments'))
        
        appointment = Appointment(
        patient_id=patient,
        doctor_id=doctor,
        appointment_date=appointment_date,
        appointment_details = appointment_details,
        status = "Scheduled"
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Appoinmet booked succesfully.","success")
        return redirect(url_for('patient', page_name='book-appointments'))


@app.route('/doctor/dashboard/<page_name>')
def doctor(page_name):
    user_id = session.get('id')
    if not user_id:
        flash("Session expired. Please log in again.", "warning")
        return redirect('/login')
    user = User.query.options(joinedload(User.doctor_profile)).get(user_id)
    
    today = date.today()
    appointments = Appointment.query.filter(
    Appointment.status == 'Scheduled',
    Appointment.appointment_date == today).all()
    
    pages = {
        'your-appointments': 'your-appointments.html',
        'book-appointments': 'book-appointments.html',
        'profile': 'profile.html'
    }

    if page_name not in pages:
        return "<h1>404 - Page Not Found</h1>", 404

    return render_template(pages[page_name],
                            user=user,
                            appointments=appointments)


@app.route('/appointment_details/<int:id>')
def appointment_details(id):
    if 'id' not in session:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('login'))
    appointment = Appointment.query.filter_by(id=id, ).first()
    prescriptions = Prescription.query.filter_by(appointment_id=id).all()

    return render_template('appointment-details.html',
                            appointment=appointment,
                            prescription=prescriptions)


@app.route('/app-prescriptions/<int:id>',methods = ['POST','GET'])
def add_prescription(id):
    if request.method == 'POST':
        if 'id' not in session:
            flash("Session expired. Please log in again.", "warning")
            return redirect(url_for('login'))
        prescription_details = request.form['prescription']
        appointment = Appointment.query.filter_by(id= id).first()
        doctor_id = appointment.doctor_id
        patient_id = appointment.patient_id
    
        prescription = Prescription(
            appointment_id = id,
            patient_id =patient_id,
            doctor_id = doctor_id,
            prescriptions = prescription_details
        )
        
        db.session.add(prescription)
        db.session.commit()
        flash("Thank you, Doctor! Prescription submitted successfully.", "success")
        return redirect(url_for('appointment_details',id =id))


@app.route('/upload',methods =['POST'])
def upload():
    if request.method == 'POST':
        method = request.form.get('_method')
        user_id = session.get('id')
        role = session.get('role')
        if not user_id or not role:
            flash("Session expired. Please log in again.", "warning")
            return redirect('/login')
        if method == 'PUT':
            image_url = request.form['url']
            image =request.files['profile_picture']
            public_id = image_url.split('/')[-1].split('.')[0].strip()
            res = cloudinary.uploader.destroy(public_id)
            if res["result"] == "ok":
                res = cloudinary.uploader.upload(image)
                if res:
                    user = User.query.filter_by(id=user_id).first()
                    user.image_filename = res["secure_url"].strip()
                    db.session.commit()
                    flash("Profile picture updated.","success")
                    if role == "Patient":
                        return redirect(url_for("patient",page_name ="profile"))
                    else:
                        return redirect(url_for("doctor", page_name ="profile"))
                else:
                    flash("Could not upload image. Something went wrong. Please try again.", "error")
            else:
                flash("Could not upload image. Something went wrong. Please try again.", "error")
        else:
            image =request.files.get('profile_picture')
            res = cloudinary.uploader.upload(image)
            if res:
                user = User.query.filter_by(id=user_id).first()
                user.image_filename = res["secure_url"]
                db.session.commit()
                flash("Image uploaded successfully.","success")
            else:
                flash("Could not upload image. Something went wrong. Please try again.", "error")
        return redirect(url_for("patient" if role == "Patient" else "doctor", page_name="profile"))


@app.route('/mark-completed/<int:id>',methods = ['POST','GET'])
def mark_completed(id):
    if request.method == "POST":
        role = session.get('role')
        if not  role:
            flash("Session expired. Please log in again.", "warning")
            return redirect('/login')
        appointment = Appointment.query.filter_by(id=id).first()
        if app:
            appointment.status = "Completed"
            db.session.commit()
            flash(" Marked as completed. Thank you, Doctor!","success")
        else:
            flash("No such Appointment!!","error")
        if role == "Patient":
            return redirect(url_for("patient",page_name ="your-appointments"))
        else:
            return redirect(url_for("doctor", page_name ="your-appointments"))


@app.route('/cancel-appointment/<int:id>',methods = ['POST','GET'])
def cancel_appointment(id):
    if request.method == 'POST':
        role = session.get('role')
        if not  role:
            flash("Session expired. Please log in again.", "warning")
            return redirect('/login')
        appointment = Appointment.query.filter_by(id = id).first()
        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            flash("Your Appointment is cancelled succesfully!!","warning")
        else:
            flash("Appointment not found or already deleted.","error")
        if role == "Patient":
            return redirect(url_for("patient",page_name ="your-appointments"))
        else:
            return redirect(url_for("doctor", page_name ="your-appointments"))


@app.route('/delete-appointment/<int:id>',methods = ['POST','GET'])
def delete_appointment(id):
    if request.method == 'POST':
        role = session.get('role')
        if not  role:
            flash("Session expired. Please log in again.", "warning")
            return redirect('/login')
        try:
            appointment = Appointment.query.filter_by(id=id).first()
            if not appointment:
                flash("Appointment not found or already deleted.", "error")
                return redirect(url_for("patient",page_name ="your-appointments"))

            prescription = Prescription.query.filter_by(appointment_id=id).first()
            if prescription:
                db.session.delete(prescription)
                db.session.commit()

            db.session.delete(appointment)
            db.session.commit()

            flash("Your appointment has been deleted successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("An error occurred while cancelling the appointment.", "error")
        return redirect(url_for("patient",page_name ="your-appointments"))


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == "POST":
        session.clear()
        flash("You have been logged out successfully.", "success")
        return redirect('/login')

if __name__ == "__main__":
    app.run(debug = True)