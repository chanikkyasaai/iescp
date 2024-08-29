import base64
from flask import Flask, render_template, request,flash, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import secrets
import string
from datetime import datetime
from fpdf import FPDF
import io, csv, json

def generate_secret_key(length=24):
    alphabet = string.ascii_letters + string.digits + '-+_!@#$%^&*()'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Hp/OneDrive/Desktop/IESCP/iescp_db/iescp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = generate_secret_key()

db = SQLAlchemy(app)


class Auth(db.Model):
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)  

class Influencer(db.Model):
    __tablename__ = 'influencers'
    auth_id = db.Column(db.Integer, db.ForeignKey('auth.id'), primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    social_url = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    verification_status = db.Column(db.Integer, nullable=False)  
    niche = db.Column(db.String(100), nullable=False)
    doj = db.Column(db.DateTime, default=func.current_timestamp())
    image = db.Column(db.LargeBinary) 
    reach = db.Column(db.Integer)
    bio = db.Column(db.String(100), nullable=False)
    

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    auth_id = db.Column(db.Integer, db.ForeignKey('auth.id'), primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    doj = db.Column(db.DateTime, default=func.current_timestamp())
    flag = db.Column(db.Integer, nullable = False)
    
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    goals = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    visibility = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.auth_id'))
    flag = db.Column(db.Integer, nullable = False)

    sponsor = db.relationship('Sponsor', backref='campaigns')
    requests = db.relationship('Request', cascade='all, delete-orphan', backref='campaign')

    __table_args__ = (
        db.CheckConstraint(visibility.in_(['public', 'private']), name='visibility_check'),
        db.CheckConstraint(status.in_(['open', 'closed']), name='status_check'),
    )
class Request(db.Model):
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.auth_id'), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  
    quote = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)  

    campaign = db.relationship('Campaign', backref=db.backref('requests', cascade='all, delete-orphan'))
    influencer = db.relationship('Influencer', backref=db.backref('requests', cascade='all, delete-orphan'))
  
  
 

class Status(db.Model):
    __tablename__ = 'status'
    
    id = db.Column(db.Integer, db.ForeignKey('requests.id'), primary_key=True)
    influencer_status = db.Column(db.String, nullable=False)
    sponsor_status = db.Column(db.String, nullable=True)
    payment_status = db.Column(db.String, nullable=True)

    request = db.relationship('Request', backref=db.backref('status_info', uselist=False))


def create_database():
    with app.app_context():
        db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        user = Auth.query.filter_by(email=email, user_type=user_type).first()

        if not user:
            return render_template('auth.html', error_message='User not found.')

        if user.password != password:
            return render_template('auth.html', error_message='Invalid password.')

        session['user_id'] = user.id
        session['user_type'] = user.user_type
        if user.user_type == 'influencer':
            return redirect(url_for('influencer_dashboard'))
        elif user.user_type == 'sponsor':
            session['sponsor_id'] = user.id
            return redirect(url_for('sponsor_dashboard'))
        elif user.user_type == 'admin':
            return redirect(url_for('admin_dashboard'))

        return "User type not implemented", 501

    return render_template('auth.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    
    influencer_count = Auth.query.filter_by(user_type='influencer').count()
    sponsor_count = Auth.query.filter_by(user_type='sponsor').count()

    
    campaign_completion_data = {
        "open": Campaign.query.filter_by(status='open').count(),
        "closed": Campaign.query.filter_by(status='closed').count(),
    }

    
    influencer_niche_data = db.session.query(Influencer.niche, func.count(Influencer.niche)) \
                                      .group_by(Influencer.niche).all()

    
    campaign_budget_data = {
        "0-1k": Campaign.query.filter(Campaign.budget <= 1000).count(),
        "1k-5k": Campaign.query.filter(Campaign.budget > 1000, Campaign.budget <= 5000).count(),
        "5k-10k": Campaign.query.filter(Campaign.budget > 5000, Campaign.budget <= 10000).count(),
        "10k+": Campaign.query.filter(Campaign.budget > 10000).count(),
    }

    
    influencer_registration_data = db.session.query(func.date(Influencer.doj), func.count(Influencer.auth_id)) \
                                             .group_by(func.date(Influencer.doj)).all()

    sponsor_registration_data = db.session.query(func.date(Sponsor.doj), func.count(Sponsor.auth_id)) \
                                          .group_by(func.date(Sponsor.doj)).all()

    
    user_registration_data = influencer_registration_data + sponsor_registration_data

    
    influencer_requests = Request.query.filter_by(request_type='to_sponsor').count()
    sponsor_requests = Request.query.filter_by(request_type='to_influencer').count()

    return render_template('admin/dashboard.html',
                           influencer_count=influencer_count,
                           sponsor_count=sponsor_count,
                           campaign_completion_data=campaign_completion_data,
                           influencer_niche_data=influencer_niche_data,
                           campaign_budget_data=campaign_budget_data,
                           user_registration_data=user_registration_data,
                           influencer_requests=influencer_requests,
                           sponsor_requests=sponsor_requests)

@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    
    influencer_status = request.args.get('influencer_status')
    sponsor_flag = request.args.get('sponsor_flag')
    campaign_flag = request.args.get('campaign_flag')
    influencer_search_query = request.args.get('influencer_search_query')
    sponsor_search_query = request.args.get('sponsor_search_query')
    campaign_search_query = request.args.get('campaign_search_query')

    
    auth_emails = db.session.query(Auth.id, Auth.email).all()
    email_map = {auth_id: email for auth_id, email in auth_emails}

    
    influencers_query = db.session.query(Influencer).filter(Influencer.auth_id.in_(email_map.keys()))
    if influencer_status:
        influencers_query = influencers_query.filter(Influencer.verification_status == int(influencer_status))
    if influencer_search_query:
        influencers_query = influencers_query.filter(
            (Influencer.fname.like(f'%{influencer_search_query}%')) |
            (Influencer.lname.like(f'%{influencer_search_query}%')) |
            (Auth.email.like(f'%{influencer_search_query}%'))
        )
    influencers = influencers_query.all()

    
    sponsors_query = db.session.query(Sponsor).filter(Sponsor.auth_id.in_(email_map.keys()))
    if sponsor_flag:
        sponsors_query = sponsors_query.filter(Sponsor.flag == int(sponsor_flag))
    if sponsor_search_query:
        sponsors_query = sponsors_query.filter(
            (Sponsor.fname.like(f'%{sponsor_search_query}%')) |
            (Sponsor.lname.like(f'%{sponsor_search_query}%')) |
            (Sponsor.company_name.like(f'%{sponsor_search_query}%')) |
            (Auth.email.like(f'%{sponsor_search_query}%'))
        )
    sponsors = sponsors_query.all()

    
    campaigns_query = Campaign.query
    if campaign_flag:
        campaigns_query = campaigns_query.filter_by(flag=int(campaign_flag))
    if campaign_search_query:
        campaigns_query = campaigns_query.filter(Campaign.name.like(f'%{campaign_search_query}%'))
    campaigns = campaigns_query.all()

    
    influencer_emails = {influencer.auth_id: email_map.get(influencer.auth_id, '') for influencer in influencers}
    sponsor_emails = {sponsor.auth_id: email_map.get(sponsor.auth_id, '') for sponsor in sponsors}

    return render_template('admin/users.html',
                           influencers=influencers,
                           influencer_emails=influencer_emails,
                           sponsors=sponsors,
                           sponsor_emails=sponsor_emails,
                           campaigns=campaigns)



@app.route('/admin/toggle_flag_sponsor/<int:sponsor_id>', methods=['POST'])
def toggle_flag_sponsor(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    sponsor.flag = 0 if sponsor.flag == 1 else 1
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/toggle_flag_campaign/<int:campaign_id>', methods=['POST'])
def toggle_flag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flag = 0 if campaign.flag == 1 else 1
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/update_influencer_status/<int:influencer_id>', methods=['POST'])
def update_influencer_status(influencer_id):
    
    new_status = request.form.get('verification_status')
    
    
    influencer = Influencer.query.get(influencer_id)
    if influencer:
        influencer.verification_status = int(new_status)  
        db.session.commit()
    
    return redirect(url_for('admin_users'))


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    user_type = request.form['user_type']

    
    existing_user = Auth.query.filter((Auth.email == email) | (Auth.phone == phone)).first()
    if existing_user:
        return render_template('auth.html', error_message='Email or phone number already in use.')

    
    new_user = Auth(email=email, phone=phone, password=password, user_type=user_type)
    db.session.add(new_user)
    db.session.commit()

    user_id = new_user.id

    if user_type == 'influencer':
        return redirect(url_for('complete_profile_influencer', auth_id=user_id))
    elif user_type == 'sponsor':
        return redirect(url_for('complete_profile_sponsor', auth_id=user_id))
    else:
        return redirect(url_for('auth'))


@app.route('/complete_profile_influencer/<int:auth_id>', methods=['GET', 'POST'])
def complete_profile_influencer(auth_id):
    if request.method == 'POST':
        
        fname = request.form['fname']
        lname = request.form['lname']
        bio = request.form['bio']
        address_line1 = request.form['address_line1']
        address_line2 = request.form.get('address_line2', '')
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        postal_code = request.form['postal_code']
        social_url = request.form['social_url']
        birth_date_str = request.form['birth_date']
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        gender = request.form['gender']
        niche = request.form['niche']
        reach = int(request.form['reach'])
        verification_status = 0  
        image = request.files['image'].read()

        
        new_influencer = Influencer(
            auth_id=auth_id,
            fname=fname,
            lname=lname,
            bio=bio,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            social_url=social_url,
            birth_date=birth_date,
            gender=gender,
            niche=niche,
            verification_status=verification_status,
            image=image,
            reach=reach
        )
        
        
        db.session.add(new_influencer)
        db.session.commit()

        
        return redirect(url_for('influencer_dashboard'))

    return render_template('complete_profile_influencer.html', auth_id=auth_id)

@app.route('/complete_profile_sponsor/<int:auth_id>', methods=['GET', 'POST'])
def complete_profile_sponsor(auth_id):
    if request.method == 'POST':
        
        fname = request.form['fname']
        lname = request.form['lname']
        company_name = request.form['company_name']
        contact_number = request.form['contact_number']
        address_line1 = request.form['address_line1']
        address_line2 = request.form.get('address_line2', '')
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        postal_code = request.form['postal_code']

        
        new_sponsor = Sponsor(
            auth_id=auth_id,
            fname=fname,
            lname=lname,
            company_name=company_name,
            contact_number=contact_number,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code
        )

        
        db.session.add(new_sponsor)
        db.session.commit()

        
        return redirect(url_for('sponsor_dashboard'))

    return render_template('complete_profile_sponsor.html', auth_id=auth_id)


@app.route('/influencer/dashboard')
def influencer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'influencer':
        return redirect(url_for('auth'))

    influencer = Influencer.query.filter_by(auth_id=session['user_id']).first()

    
    print(f"Session user_id: {session['user_id']}")
    print(f"Influencer found: {influencer}")

    if not influencer:
        return "Influencer profile not found", 404

    
    if influencer.verification_status == -1:
        return redirect(url_for('flagged'))

    
    public_campaigns = db.session.query(Campaign, Sponsor.company_name).join(Sponsor, Campaign.sponsor_id == Sponsor.auth_id).filter(
        Campaign.visibility == 'public',
        Campaign.status == 'open' , 
        Campaign.flag == 0
    ).all()

    
    in_requests = db.session.query(Request, Campaign).join(Campaign, Request.campaign_id == Campaign.id).filter(
        Request.influencer_id == influencer.auth_id,
        Request.request_type == 'to_influencer',
        Request.status == 'pending'
    ).all()

    if influencer.image:
        image_base64 = base64.b64encode(influencer.image).decode('utf-8')
    else:
        image_base64 = None

    return render_template('influencer/dashboard.html', influencer=influencer, image_base64=image_base64, campaigns=public_campaigns, in_requests=in_requests)


@app.route('/sponsor/dashboard')
def sponsor_dashboard():
    if 'user_id' not in session or session['user_type'] != 'sponsor':
        return redirect(url_for('auth'))
    
    sponsor = Sponsor.query.filter_by(auth_id=session['user_id']).first()

    if not sponsor:
        return "Sponsor profile not found", 404

        
    if sponsor.flag == 1:
        return redirect(url_for('flagged'))

    
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.auth_id).all()

    all_influencers = Influencer.query.filter_by(verification_status=1).all()

     
    for influencer in all_influencers:
        if influencer.image:  
            influencer.image_url = f"data:image/jpeg;base64,{base64.b64encode(influencer.image).decode('utf-8')}"
        else:
            influencer.image_url = "/static/default-avatar.jpg"  

    niches = ['Technology', 'Fashion', 'Food', 'Travel', 'Fitness', 'Lifestyle']
    

    return render_template('sponsor/dashboard.html', sponsor=sponsor, campaigns=campaigns, influencers=all_influencers, niches=niches)

@app.route('/flagged')
def flagged():
    return render_template('flagged.html')


@app.route('/campaigns')
def campaigns():
    all_campaigns = Campaign.query.all()  
    return render_template('campaigns.html', campaigns=all_campaigns)

@app.route('/details/<entity_type>/<int:id>', methods=['GET'])
def details(entity_type, id):
    if entity_type == 'influencer':
        entity = db.session.query(Influencer, Auth).join(Auth, Influencer.auth_id == Auth.id).filter(Influencer.auth_id == id).first_or_404()
    elif entity_type == 'sponsor':
        entity = db.session.query(Sponsor, Auth).join(Auth, Sponsor.auth_id == Auth.id).filter(Sponsor.auth_id == id).first_or_404()
    elif entity_type == 'campaign':
        entity = Campaign.query.get_or_404(id)
    else:
        return "Invalid entity type", 404

    return render_template('admin/details.html', entity_type=entity_type, entity=entity)


@app.route('/create_campaign', methods=['POST'])
def create_campaign():
    if 'user_id' not in session or session['user_type'] != 'sponsor':
        return redirect(url_for('auth'))

    
    name = request.form['campaignName']
    description = request.form['campaignDescription']
    budget = float(request.form['campaignBudget'])
    goals = request.form['campaignGoals']
    start_date = datetime.strptime(request.form['startDate'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['endDate'], '%Y-%m-%d').date()
    visibility = request.form.get('campaignVisibility', 'public')  

    
    sponsor_id = session['user_id']

    
    new_campaign = Campaign(
        name=name,
        description=description,
        budget=budget,
        goals=goals,
        start_date=start_date,
        end_date=end_date,
        visibility=visibility,
        status='open',  
        sponsor_id=sponsor_id,
        flag = 0
    )

    
    db.session.add(new_campaign)
    db.session.commit()

    return redirect(url_for('sponsor_dashboard'))


@app.route('/influencer/profile', methods=['GET', 'POST'])
def influencer_profile():
    if 'user_id' not in session or session['user_type'] != 'influencer':
        return redirect(url_for('auth'))

    influencer = Influencer.query.filter_by(auth_id=session['user_id']).first()

    if influencer.image:  
        influencer.image_url = f"data:image/jpeg;base64,{base64.b64encode(influencer.image).decode('utf-8')}"
    else:
        influencer.image_url = url_for('static', filename='default-avatar.jpg')  

    if request.method == 'POST':
        
        influencer.fname = request.form['fname']
        influencer.lname = request.form['lname']
        influencer.bio = request.form['bio']
        influencer.address_line1 = request.form['address_line1']
        influencer.address_line2 = request.form['address_line2']
        influencer.city = request.form['city']
        influencer.state = request.form['state']
        influencer.country = request.form['country']
        influencer.postal_code = request.form['postal_code']
        influencer.social_url = request.form['social_url']
        influencer.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        influencer.gender = request.form['gender']
        influencer.niche = request.form['niche']

        
        if 'profile_image' in request.files and request.files['profile_image'].filename != '':
            profile_image = request.files['profile_image']
            image_data = profile_image.read()  
            influencer.image = image_data  
            

        db.session.commit()

    return render_template('influencer/profile.html', influencer=influencer)

@app.route('/sponsor/profile', methods=['GET', 'POST'])
def sponsor_profile():
    if 'user_id' not in session or session['user_type'] != 'sponsor':
        return redirect(url_for('auth'))

    sponsor = Sponsor.query.filter_by(auth_id=session['user_id']).first()

    if request.method == 'POST':
        
        sponsor.fname = request.form['fname']
        sponsor.lname = request.form['lname']
        sponsor.company_name = request.form['company_name']
        sponsor.contact_number = request.form['contact_number']
        sponsor.address_line1 = request.form['address_line1']
        sponsor.address_line2 = request.form['address_line2']
        sponsor.city = request.form['city']
        sponsor.state = request.form['state']
        sponsor.country = request.form['country']
        sponsor.postal_code = request.form['postal_code']

        db.session.commit()

        return redirect(url_for('sponsor_dashboard'))

    return render_template('sponsor/sponsor_profile.html', sponsor=sponsor)

from flask import session, request, redirect, url_for

@app.route('/influencer/<int:influencer_id>', methods=['GET'])
def influencer_details(influencer_id):
    
    influencer = Influencer.query.get_or_404(influencer_id)
    if influencer.image:  
        influencer.image_url = f"data:image/jpeg;base64,{base64.b64encode(influencer.image).decode('utf-8')}"
    else:
        influencer.image_url = url_for('static', filename='default-avatar.jpg')
    
    
    sponsor_id = session.get('sponsor_id')
    
    print(f"Sponsor ID from session: {sponsor_id}")
    if not sponsor_id:
        
        return redirect(url_for('auth'))  
    
    
    active_campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id, status='open').all()

    
    
    return render_template('sponsor/influencer.html', influencer=influencer, sponsor_id=sponsor_id, active_campaigns=active_campaigns)


@app.route('/make_request', methods=['POST'])
def make_request():
    campaign_id = request.form.get('campaign_id')
    influencer_id = request.form.get('influencer_id')
    quote_amount = request.form.get('quote')

    
    print(f"Influencer ID: {influencer_id}")

    if not influencer_id:
        return "Influencer ID is missing", 400

    new_request = Request(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        request_type='to_influencer',
        quote=quote_amount,
        status='pending'
    )

    db.session.add(new_request)
    db.session.commit()

    
    flash('Request submitted successfully!', 'success')

    
    return redirect(url_for('sponsor_dashboard'))

@app.route('/campaign/<int:campaign_id>/<int:auth_id>', methods=['GET', 'POST'])
def campaign_detail(campaign_id, auth_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer = Influencer.query.get_or_404(auth_id)

    
    sponsor = Sponsor.query.filter_by(auth_id=campaign.sponsor_id).first()
    company_name = sponsor.company_name if sponsor else 'Unknown'

    
    existing_request = Request.query.filter_by(campaign_id=campaign_id, influencer_id=auth_id).first()

    
    if existing_request:
        status = Status.query.get(existing_request.id)
    else:
        status = None

    if request.method == 'POST':
        quote = float(request.form.get('quote'))

        if quote <= campaign.budget:
            new_request = Request(
                campaign_id=campaign_id,
                influencer_id=influencer.auth_id,
                request_type='to_sponsor',
                quote=quote,
                status='pending'
            )
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for('campaign_detail', campaign_id=campaign_id, auth_id=auth_id))
        else:
            return "Quote exceeds campaign budget", 400

    return render_template('influencer/campaign_detail.html', campaign=campaign, influencer=influencer, request=existing_request, status=status, company_name=company_name)


@app.route('/campaign/<int:campaign_id>/<int:auth_id>/request', methods=['POST'])
def request_campaign(campaign_id, auth_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer = Influencer.query.get_or_404(auth_id)
    quote = float(request.form.get('quote'))
    
    if quote <= campaign.budget:
        new_request = Request(
            campaign_id=campaign_id,
            influencer_id=influencer.auth_id,
            request_type='to_sponsor',
            quote=quote,
            status='pending'
        )
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('campaign_detail', campaign_id=campaign_id, auth_id=auth_id))
    else:
        return "Quote exceeds campaign budget", 400
    
@app.route('/campaign/<int:campaign_id>')
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    requests = Request.query.filter_by(campaign_id=campaign_id).all()
    
    
    for req in requests:
        req.influencer_name = Influencer.query.get(req.influencer_id).fname
        req.status_info = Status.query.filter_by(id=req.id).first()
        req.payment_status = req.status_info.payment_status if req.status_info else None
    
    return render_template('sponsor/campaign_details.html', campaign=campaign, requests=requests)



@app.route('/update_sponsor_status/<int:request_id>', methods=['POST'])
def update_sponsor_status(request_id):
    
    request_obj = Request.query.get_or_404(request_id)
    
    
    status_obj = Status.query.filter_by(id=request_id).first()
    if request_obj.status == 'accept' and status_obj and status_obj.influencer_status == 'completed':
        
        status_obj.sponsor_status = 'accepted'
        db.session.commit()
        
        return redirect(url_for('campaign_details', campaign_id=request_obj.campaign_id))
    else:
        return "Invalid request or status", 400



@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    
    req = Request.query.get_or_404(request_id)
    
    
    req.status = 'accept'
    
    
    new_status = Status(
        id=req.id,
        influencer_status='ongoing',  
        sponsor_status=None,          
        payment_status=None          
    )
    
    
    db.session.add(new_status)
    
    
    db.session.commit()
    
    
    return redirect(url_for('campaign_details', campaign_id=req.campaign_id))


@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    req = Request.query.get_or_404(request_id)
    req.status = 'reject'
    db.session.commit()
    return redirect(url_for('campaign_details', campaign_id=req.campaign_id))

@app.route('/handle_response/<int:request_id>', methods=['POST'])
def handle_response(request_id):
    
    req = Request.query.get_or_404(request_id)
    
    
    action = request.form.get('action')
    if action == 'accept':
        req.status = 'accept'
        
        new_status = Status(
            id=req.id,
            influencer_status='ongoing',  
            sponsor_status=None,          
            payment_status=None          
        )
        db.session.add(new_status)
    elif action == 'reject':
        req.status = 'reject'
    else:
        return "Invalid action", 400

    
    db.session.commit()
    
    
    return redirect(url_for('influencer_dashboard'))

@app.route('/campaigns4me')
def campaigns4me():
    if 'user_id' not in session or session['user_type'] != 'influencer':
        return redirect(url_for('auth'))

    
    influencer = Influencer.query.filter_by(auth_id=session['user_id']).first()
    
    if not influencer:
        return "Influencer profile not found", 404

    
    campaigns_with_status = (
        db.session.query(Campaign, Request, Status)
        .join(Request, Campaign.id == Request.campaign_id)
        .join(Status, Request.id == Status.id)
        .filter(Request.influencer_id == influencer.auth_id)
        .all()
    )
    
    print("Campaigns with status:", campaigns_with_status)

    return render_template('influencer/campaigns4me.html', campaigns=campaigns_with_status, influencer=influencer)



@app.route('/mark_completed/<int:request_id>', methods=['POST'])
def mark_completed(request_id):
    
    req = Request.query.get_or_404(request_id)
    
    status_record = Status.query.get_or_404(request_id)
    
    
    status_record.influencer_status = 'completed'
    
    
    db.session.commit()

    
    return redirect(url_for('campaign_detail', campaign_id=req.campaign_id, auth_id=req.influencer_id))

@app.route('/update_status/<int:request_id>', methods=['POST'])
def update_status(request_id):
    
    status = Status.query.get_or_404(request_id)
    
    
    status.influencer_status = 'completed'
    
    
    db.session.commit()
    
    
    return redirect(url_for('campaigns4me'))


@app.route('/make_payment/<int:request_id>', methods=['POST'])
def make_payment(request_id):
    
    request_obj = Request.query.get_or_404(request_id)

    
    status_obj = Status.query.get(request_id)

    if status_obj is None:
        
        status_obj = Status(id=request_id, 
                            campaign_id=request_obj.campaign_id, 
                            payment_status='done')
        db.session.add(status_obj)
    else:
        
        status_obj.payment_status = 'done'
    
    db.session.commit()
    
    return redirect(url_for('campaign_details', campaign_id=request_obj.campaign_id))


@app.route('/payments/<int:request_id>')
def show_payment_page(request_id):
    
    request_obj = Request.query.get_or_404(request_id)
    campaign_obj = Campaign.query.get_or_404(request_obj.campaign_id)
    
    return render_template('sponsor/payment.html', request=request_obj, campaign=campaign_obj)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth'))


@app.route('/influencer/profile_image/<int:auth_id>')
def influencer_profile_image(auth_id):
    influencer = Influencer.query.filter_by(auth_id=auth_id).first()
    if influencer and influencer.image:
        return app.response_class(influencer.image, content_type='image/jpeg')
    else:
        return "No image found", 404
@app.route('/search_influencers', methods=['POST'])
def search_influencers():
    search_input = request.form.get('searchInput')
    reach_filter = request.form.get('reachFilter')
    niche_filter = request.form.get('nicheFilter')

    query = Influencer.query

    if search_input:
        query = query.filter(Influencer.fname.like(f'%{search_input}%') | Influencer.lname.like(f'%{search_input}%'))

    if reach_filter:
        
        query = query.filter(Influencer.reach >= int(reach_filter))

    if niche_filter:
        query = query.filter(Influencer.niche == niche_filter)

    influencers = query.all()

    
    return render_template('sponsor_dashboard.html', search_results=influencers)


def get_verification_status(status_code):
    if status_code == 1:
        return "Verified"
    elif status_code == 0:
        return "Pending Verification"
    elif status_code == -1:
        return "Verification Failed"
    else:
        return "Unknown"

@app.route('/update_campaign_status/<int:campaign_id>/<new_status>', methods=['POST'])
def update_campaign_status(campaign_id, new_status):
    
    if new_status not in ['open', 'closed']:
        return "Invalid status", 400

    
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    
     
    campaign.status = new_status
    db.session.commit()

    return redirect(url_for('campaign_details', campaign_id=campaign_id))

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    try:
        
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting campaign. Please try again.', 'danger')
    
    
    return redirect(url_for('sponsor_dashboard'))

@app.route('/download_receipt/<int:request_id>')
def download_receipt(request_id):
    
    request_data = Request.query.get(request_id)
    campaign = request_data.campaign
    influencer = request_data.influencer

    
    sponsor = Sponsor.query.filter_by(auth_id=campaign.sponsor_id).first()
    company_name = sponsor.company_name if sponsor else 'Unknown'

    
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 24)

    
    pdf.cell(0, 10, txt="IGNITASE", ln=False, align="L")

    
    now = datetime.now()
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=now.strftime("%Y-%m-%d %H:%M:%S"), ln=True, align="R")

    
    pdf.line(10, 30, 200, 30)  

    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)  
    pdf.cell(200, 10, txt=f"Campaign Name: {campaign.name}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Company Name: {company_name}", ln=True, align="L")  
    pdf.cell(200, 10, txt=f"End Date: {campaign.end_date.strftime('%Y-%m-%d')}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Description: {campaign.description}", ln=True, align="L")

    
    pdf.ln(10)  
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  

    
    pdf.ln(10)  
    pdf.cell(200, 10, txt=f"Influencer Name: {influencer.fname} {influencer.lname}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Amount Paid: ${request_data.quote}", ln=True, align="L")

    
    pdf.ln(20)  
    pdf.set_y(-30)  
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="This is a system-generated receipt. No signature required.", ln=True, align="C")

    
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    
    return send_file(buffer, as_attachment=True, download_name="receipt.pdf", mimetype='application/pdf')

@app.route('/download_campaign/<int:campaign_id>/<file_type>')
def download_campaign(campaign_id, file_type):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    
    requests = db.session.query(Request, Status).outerjoin(Status, Request.id == Status.id).filter(Request.campaign_id == campaign_id).all()
    
    if file_type == 'csv':
        return generate_csv(campaign, requests)
    elif file_type == 'pdf':
        return generate_pdf(campaign, requests)
    else:
        return "Invalid file type", 400

def generate_pdf(campaign, requests):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    
    pdf.cell(200, 10, txt=f"Campaign Name: {campaign.name}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Description: {campaign.description}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Budget: ${campaign.budget}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Goals: {campaign.goals}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Start Date: {campaign.start_date}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"End Date: {campaign.end_date}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Visibility: {campaign.visibility}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Status: {campaign.status}", ln=True, align="L")

    pdf.ln(10)  

    
    pdf.cell(200, 10, txt="Requests", ln=True, align="L")
    pdf.cell(200, 10, txt="Influencer Name, Quote Amount, Status, Payment Status", ln=True, align="L")

    for req, status in requests:
        
        payment_status = status.payment_status if status else 'unknown'
        if payment_status == 'done':
            pdf.cell(200, 10, txt=f"{req.influencer.fname}, {req.influencer.lname}, ${req.quote}, {req.status}, {payment_status}", ln=True, align="L")

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="campaign_details.pdf", mimetype='application/pdf')

def generate_csv(campaign, requests):
    output = io.StringIO()  
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    
    writer.writerow([f'Campaign Name: {campaign.name}'])
    writer.writerow([])  

    
    writer.writerow(['Request_Id','Influencer Name', 'Request type', 'Quote Amount'])

    
    if not requests:
        writer.writerow(['No data available'])
    else:
        for req, status in requests:
           
            
            payment_status = status.payment_status if status else 'unknown'
            
            if payment_status == 'done':
                influencer_name = f"{req.influencer.fname} {req.influencer.lname}"
                writer.writerow([req.id,influencer_name,req.request_type, req.quote])
            else:
                print(f"Skipping Request: {req} due to payment status: {payment_status}")

    
    output.seek(0)
    
    
    buffer_content = output.getvalue()
    print(f"Buffer content: {buffer_content}")

    
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), as_attachment=True, download_name="campaign_details.csv", mimetype='text/csv')

if __name__ == '__main__':
    create_database()  
    app.run(debug=True)
