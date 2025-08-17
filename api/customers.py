# api/customers.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.customer import Customer
from app import login_required

customers_bp = Blueprint('customers', __name__)
customer_model = Customer()

@customers_bp.route('/')
@login_required
def view_customers():
    customers = customer_model.get_all()
    return render_template('customer/view_customers.html', customers=customers)

@customers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        customer_model.create(
            name=request.form['name'],
            address=request.form['address'],
            phone=request.form['phone'],
            gst=request.form['gst'],
            pan=request.form['pan']
        )
        flash('Customer Added Successfully!', 'success')
        return redirect(url_for('customers.view_customers'))
    return render_template('customer/add_customer.html')

@customers_bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = customer_model.get_by_id(customer_id)
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('customers.view_customers'))

    if request.method == 'POST':
        customer_model.update(
            customer_id,
            request.form['name'],
            request.form['address'],
            request.form['phone'],
            request.form['gst'],
            request.form['pan']
        )
        flash('Customer Updated Successfully!', 'success')
        return redirect(url_for('customers.view_customers'))
        
    return render_template('customer/edit_customer.html', customer=customer)

@customers_bp.route('/delete/<int:customer_id>')
@login_required
def delete_customer(customer_id):
    customer_model.delete(customer_id)
    flash('Customer Deactivated Successfully.', 'success')
    return redirect(url_for('customers.view_customers'))