# api/deleted.py
from flask import Blueprint, render_template
from app import login_required
from models.customer import Customer
from models.enquiry import Enquiry
from models.order import Order

deleted_bp = Blueprint('deleted', __name__)

# Initialize the models
customer_model = Customer()
enquiry_model = Enquiry()
order_model = Order()

@deleted_bp.route('/deleted-info')
@login_required
def deleted_info_page():
    # Fetch deactivated records from each model
    deactivated_customers = customer_model.get_deactivated()
    deactivated_enquiries = enquiry_model.get_deactivated()
    deactivated_orders = order_model.get_deactivated()

    # Pass the lists of deactivated items to the template
    return render_template(
        'deleted_info.html',
        customers=deactivated_customers,
        enquiries=deactivated_enquiries,
        orders=deactivated_orders
    )