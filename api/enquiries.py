# api/enquiries.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.enquiry import Enquiry
from models.customer import Customer
from app import login_required

enquiries_bp = Blueprint('enquiries', __name__)
enquiry_model = Enquiry()
customer_model = Customer()

@enquiries_bp.route('/')
@login_required
def view_enquiries():
    enquiries = enquiry_model.get_all()
    return render_template('enquiry/view_enquiries.html', enquiries=enquiries)

@enquiries_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_enquiry():
    if request.method == 'POST':
        try:
            items = []
            drawing_numbers = request.form.getlist('drawing_number[]')
            if not drawing_numbers or not drawing_numbers[0]:
                 flash('Cannot create an enquiry with no items.', 'error')
                 return redirect(request.url)

            for i in range(len(drawing_numbers)):
                item = {
                    'drawing_number': drawing_numbers[i],
                    'part_number': request.form.getlist('part_number[]')[i],
                    'part_revision_number': request.form.getlist('part_revision_number[]')[i],
                    'material_type': request.form.getlist('material_type[]')[i],
                    'material_specification': request.form.getlist('material_specification[]')[i],
                    'with_material': request.form.getlist('with_material[]')[i],
                    'unit_price': request.form.getlist('unit_price[]')[i],
                    'quantity': request.form.getlist('quantity[]')[i],
                    'remarks': request.form.getlist('remarks[]')[i],
                }
                items.append(item)
            
            enquiry_model.create_enquiry_with_items(
                customer_id=request.form['customer_id'],
                enq_number=request.form['enq_number'],
                items=items
            )
            flash('Enquiry created successfully!', 'success')
            return redirect(url_for('enquiries.view_enquiries'))
        except Exception as e:
            flash(f'Error creating enquiry: {e}', 'error')

    customers = customer_model.get_all()
    return render_template('enquiry/create_enquiry.html', customers=customers)

@enquiries_bp.route('/<int:enquiry_id>')
@login_required
def details(enquiry_id):
    enquiry, items = enquiry_model.get_details_by_id(enquiry_id)
    if not enquiry:
        flash('Enquiry not found.', 'error')
        return redirect(url_for('enquiries.view_enquiries'))
    return render_template('enquiry/edit_enquiry.html', enquiry=enquiry, items=items)

@enquiries_bp.route('/<int:enquiry_id>/update-status', methods=['POST'])
@login_required
def update_enquiry_status(enquiry_id):
    status = request.form.get('status')
    if status in ['pending', 'accepted', 'rejected']:
        enquiry_model.update_status(enquiry_id, status)
        flash(f'Enquiry status updated to {status}.', 'success')
    else:
        flash('Invalid status.', 'error')
    return redirect(url_for('enquiries.details', enquiry_id=enquiry_id))

@enquiries_bp.route('/delete/<int:enquiry_id>')
@login_required
def delete(enquiry_id):
    enquiry_model.delete(enquiry_id)
    flash('Enquiry has been deactivated.', 'success')
    return redirect(url_for('enquiries.view_enquiries'))