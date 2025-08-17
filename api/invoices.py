# api/invoices.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.invoice import Invoice
from models.customer import Customer
from models.order import Order
from app import login_required
from decimal import Decimal

invoices_bp = Blueprint('invoices', __name__)
invoice_model = Invoice()
customer_model = Customer()
order_model = Order()

@invoices_bp.route('/')
@login_required
def view_invoices():
    invoices = invoice_model.get_all()
    return render_template('invoice/view_invoices.html', invoices=invoices)

@invoices_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    if request.method == 'POST':
        try:
            gst_rate = Decimal(request.form['gst_rate'])
            sub_total = Decimal(request.form['sub_total'])
            
            data = {
                'customer_id': request.form['customer_id'],
                'dc_number': request.form['dc_number'],
                'dc_date': request.form['dc_date'],
                'po_number': request.form['po_number'],
                'po_date': request.form.get('po_date') or None,
                'payment_terms': request.form['payment_terms'],
                'gst_rate': gst_rate,
                'sub_total': sub_total,
                'gst_amount': sub_total * (gst_rate / 100),
                'total_amount': sub_total * (1 + (gst_rate / 100)),
                'items': []
            }
            
            order_item_ids = request.form.getlist('order_item_id[]')
            if not order_item_ids:
                flash("Cannot create an invoice with no items.", "error")
                return redirect(request.url)

            for i in range(len(order_item_ids)):
                data['items'].append({
                    'order_item_id': order_item_ids[i],
                    'work_order_number': request.form.getlist('wo_number[]')[i],
                    'hsn_number': request.form.getlist('hsn_number[]')[i]
                })

            invoice_model.create_invoice_with_items(data)
            flash('Invoice created successfully!', 'success')
            return redirect(url_for('invoices.view_invoices'))
        except Exception as e:
            flash(f"Error creating invoice: {e}", "error")

    customers = customer_model.get_all()
    return render_template('invoice/create_invoice.html', customers=customers)

@invoices_bp.route('/<int:invoice_id>')
@login_required
def print_invoice(invoice_id):
    invoice, items = invoice_model.get_details_by_id(invoice_id)
    if not invoice:
        flash('Invoice not found.', 'error')
        return redirect(url_for('invoices.view_invoices'))
    return render_template('invoice/print_invoice.html', invoice=invoice, items=items)

# API endpoint for JavaScript
@invoices_bp.route('/api/get-completed-items/<int:customer_id>')
@login_required
def get_completed_items(customer_id):
    items = order_model.get_completed_items_for_customer(customer_id)
    # Convert Decimal types to string for JSON serialization
    for item in items:
        if 'unit_price' in item:
            item['unit_price'] = str(item['unit_price'])
        if 'total_price' in item:
            item['total_price'] = str(item['total_price'])
    return jsonify(items)