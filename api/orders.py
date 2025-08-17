# api/orders.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.order import Order
from models.customer import Customer
from models.enquiry import Enquiry
from app import login_required

orders_bp = Blueprint('orders', __name__)
order_model = Order()
customer_model = Customer()
enquiry_model = Enquiry()

@orders_bp.route('/')
@login_required
def view_orders():
    # Use the function to only get active orders
    orders_summary = order_model.get_all_active_orders_summary()
    
    for order in orders_summary:
        # This function fetches the items for each order
        _ , item_list = order_model.get_order_details_with_items(order['id'])
        order['order_items'] = item_list
        
    return render_template('order/view_orders.html', orders=orders_summary)

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    if request.method == 'POST':
        try:
            item_ids = request.form.getlist('item_ids[]')
            if not item_ids:
                flash('You must select at least one item.', 'error')
                return redirect(request.url)
            
            order_model.create_order_with_items(
                customer_id=request.form['customer_id'],
                po_number=request.form['po_number'],
                item_ids=item_ids
            )
            flash('Order created successfully!', 'success')
            return redirect(url_for('orders.view_orders'))
        except Exception as e:
            flash(f"Error creating order: {e}", 'error')

    customers = customer_model.get_all()
    return render_template('order/create_order.html', customers=customers)

@orders_bp.route('/api/get-enquiry-items/<int:customer_id>')
@login_required
def get_enquiry_items(customer_id):
    items = enquiry_model.get_accepted_enquiries_for_customer(customer_id)
    for item in items:
        if 'unit_price' in item:
            item['unit_price'] = str(item['unit_price'])
    return jsonify(items)

@orders_bp.route('/item/<int:item_id>/update-status', methods=['POST'])
@login_required
def update_item_status(item_id):
    status = request.form.get('status')
    order_model.update_item_status(item_id, status)
    flash(f"Item status updated successfully.", 'success')
    return redirect(url_for('orders.view_orders'))

@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    try:
        order_model.delete(order_id)
        flash('Order has been moved to deactivated records.', 'success')
    except Exception as e:
        flash(f"Error deactivating order: {e}", 'error')
    return redirect(url_for('orders.view_orders'))