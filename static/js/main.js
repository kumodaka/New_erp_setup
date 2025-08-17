// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {

    // For Enquiry Form: Add/Remove Item Entries
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            const itemList = document.getElementById('item-list');
            const itemIndex = itemList.getElementsByClassName('item-entry').length;
            const newItemEntry = `
                <div class="item-entry">
                    <button type="button" class="btn btn-danger btn-sm remove-item-btn" style="float: right;">Remove</button>
                    <h4>Item ${itemIndex + 1}</h4>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Drawing Number</label>
                            <input type="text" name="drawing_number[]" required>
                        </div>
                        <div class="form-group">
                            <label>Part Number</label>
                            <input type="text" name="part_number[]" required>
                        </div>
                        <div class="form-group">
                            <label>Part Revision Number</label>
                            <input type="text" name="part_revision_number[]">
                        </div>
                        <div class="form-group">
                            <label>Material Type</label>
                            <input type="text" name="material_type[]" required>
                        </div>
                        <div class="form-group">
                            <label>Material Specification</label>
                            <input type="text" name="material_specification[]">
                        </div>
                        <div class="form-group">
                            <label>With Material</label>
                            <select name="with_material[]">
                                <option value="yes">Yes</option>
                                <option value="no">No</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Unit Price (₹)</label>
                            <input type="number" name="unit_price[]" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" name="quantity[]" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Remarks</label>
                        <textarea name="remarks[]" rows="2"></textarea>
                    </div>
                </div>`;
            itemList.insertAdjacentHTML('beforeend', newItemEntry);
        });

        // Use event delegation for removing items
        document.getElementById('item-list').addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('remove-item-btn')) {
                e.target.closest('.item-entry').remove();
            }
        });
    }

    // For Order Form: Fetch Enquiry Items based on Customer Selection
    const customerSelectOrder = document.getElementById('customer-id-order');
    if (customerSelectOrder) {
        customerSelectOrder.addEventListener('change', function() {
            const customerId = this.value;
            const itemsContainer = document.getElementById('enquiry-items-container');
            const selectedItemsTable = document.getElementById('selected-items-table').getElementsByTagName('tbody')[0];
            const totalOrderAmountEl = document.getElementById('total-order-amount');
            
            itemsContainer.innerHTML = '<p>Loading items...</p>';
            selectedItemsTable.innerHTML = '';
            totalOrderAmountEl.textContent = '₹0.00';

            if (!customerId) {
                itemsContainer.innerHTML = '<p>Please select a customer to see available items.</p>';
                return;
            }

            fetch(`/orders/api/get-enquiry-items/${customerId}`)
                .then(response => response.json())
                .then(data => {
                    itemsContainer.innerHTML = '';
                    if (data.length === 0) {
                        itemsContainer.innerHTML = '<p>No accepted enquiry items found for this customer.</p>';
                        return;
                    }

                    const table = document.createElement('table');
                    table.innerHTML = `
                        <thead>
                            <tr>
                                <th>Select</th>
                                <th>Part Number</th>
                                <th>Drawing No</th>
                                <th>Qty</th>
                                <th>Unit Price</th>
                            </tr>
                        </thead>
                        <tbody></tbody>`;
                    const tbody = table.querySelector('tbody');
                    
                    data.forEach(item => {
                        const row = tbody.insertRow();
                        row.innerHTML = `
                            <td><input type="checkbox" class="enquiry-item-checkbox" value="${item.id}" data-price="${item.unit_price}" data-quantity="${item.quantity}"></td>
                            <td>${item.part_number}</td>
                            <td>${item.drawing_number}</td>
                            <td>${item.quantity}</td>
                            <td>₹${parseFloat(item.unit_price).toFixed(2)}</td>
                        `;
                    });

                    itemsContainer.appendChild(table);
                    attachCheckboxListeners();
                })
                .catch(error => {
                    console.error('Error fetching items:', error);
                    itemsContainer.innerHTML = '<p>Error loading items. Please try again.</p>';
                });
        });

        function attachCheckboxListeners() {
            document.querySelectorAll('.enquiry-item-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', updateSelectedItems);
            });
        }

        function updateSelectedItems() {
            const selectedItemsTable = document.getElementById('selected-items-table').getElementsByTagName('tbody')[0];
            const totalOrderAmountEl = document.getElementById('total-order-amount');
            selectedItemsTable.innerHTML = '';
            let totalAmount = 0;

            document.querySelectorAll('.enquiry-item-checkbox:checked').forEach(checkbox => {
                const row = checkbox.closest('tr');
                const cells = row.getElementsByTagName('td');
                const price = parseFloat(checkbox.dataset.price);
                const quantity = parseInt(checkbox.dataset.quantity, 10);
                
                const newRow = selectedItemsTable.insertRow();
                newRow.innerHTML = `
                    <td>${cells[1].textContent}</td>
                    <td>${cells[2].textContent}</td>
                    <td>${cells[3].textContent}</td>
                    <td>₹${price.toFixed(2)}</td>
                    <td>₹${(price * quantity).toFixed(2)}</td>
                    <input type="hidden" name="item_ids[]" value="${checkbox.value}">
                `;
                totalAmount += price * quantity;
            });

            totalOrderAmountEl.textContent = `₹${totalAmount.toFixed(2)}`;
        }
    }

    // For Invoice Form: Fetch Completed Order Items
    const customerSelectInvoice = document.getElementById('customer-id-invoice');
    if (customerSelectInvoice) {
        customerSelectInvoice.addEventListener('change', function() {
            const customerId = this.value;
            const itemsContainer = document.getElementById('completed-items-container');
            
            itemsContainer.innerHTML = '<p>Loading items...</p>';
            clearInvoiceForm();

            if (!customerId) {
                itemsContainer.innerHTML = '<p>Please select a customer.</p>';
                return;
            }

            fetch(`/invoices/api/get-completed-items/${customerId}`)
                .then(response => response.json())
                .then(data => {
                    itemsContainer.innerHTML = '';
                    if (data.length === 0) {
                        itemsContainer.innerHTML = '<p>No completed order items available for invoicing for this customer.</p>';
                        return;
                    }
                    
                    const table = document.createElement('table');
                    table.innerHTML = `<thead><tr><th>Select</th><th>WO Number</th><th>Part Number</th><th>PO Number</th><th>Price</th></tr></thead><tbody></tbody>`;
                    const tbody = table.querySelector('tbody');
                    data.forEach(item => {
                        const row = tbody.insertRow();
                        row.innerHTML = `
                            <td><input type="checkbox" class="completed-item-checkbox" value="${item.id}" data-item='${JSON.stringify(item)}'></td>
                            <td>${item.wo_number}</td>
                            <td>${item.part_number}</td>
                            <td>${item.po_number}</td>
                            <td>₹${parseFloat(item.total_price).toFixed(2)}</td>
                        `;
                    });
                    itemsContainer.appendChild(table);
                    attachInvoiceCheckboxListeners();
                });
        });

        function attachInvoiceCheckboxListeners() {
            document.querySelectorAll('.completed-item-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', updateInvoiceItems);
            });
        }
        
        document.getElementById('gst_rate')?.addEventListener('change', updateInvoiceItems);

        function updateInvoiceItems() {
            const invoiceTableBody = document.getElementById('invoice-item-list').getElementsByTagName('tbody')[0];
            invoiceTableBody.innerHTML = '';
            let subTotal = 0;
            const poNumbers = new Set();
            
            document.querySelectorAll('.completed-item-checkbox:checked').forEach(checkbox => {
                const item = JSON.parse(checkbox.dataset.item);
                poNumbers.add(item.po_number);
                
                const newRow = invoiceTableBody.insertRow();
                newRow.innerHTML = `
                    <td>${item.wo_number}<input type="hidden" name="wo_number[]" value="${item.wo_number}"></td>
                    <td>${item.part_number}</td>
                    <td><input type="text" name="hsn_number[]" class="form-control" style="width: 100px;"></td>
                    <td>${item.quantity}</td>
                    <td>₹${parseFloat(item.unit_price).toFixed(2)}</td>
                    <td>₹${parseFloat(item.total_price).toFixed(2)}</td>
                    <input type="hidden" name="order_item_id[]" value="${item.id}">
                `;
                subTotal += parseFloat(item.total_price);
            });

            document.getElementById('po_number').value = Array.from(poNumbers).join(', ');
            
            const gstRate = parseFloat(document.getElementById('gst_rate').value) || 0;
            const gstAmount = subTotal * (gstRate / 100);
            const totalAmount = subTotal + gstAmount;

            document.getElementById('sub_total_display').textContent = `₹${subTotal.toFixed(2)}`;
            document.getElementById('gst_amount_display').textContent = `₹${gstAmount.toFixed(2)}`;
            document.getElementById('total_amount_display').textContent = `₹${totalAmount.toFixed(2)}`;

            document.getElementById('sub_total_hidden').value = subTotal.toFixed(2);
        }

        function clearInvoiceForm() {
            document.getElementById('invoice-item-list').getElementsByTagName('tbody')[0].innerHTML = '';
            document.getElementById('po_number').value = '';
            document.getElementById('sub_total_display').textContent = '₹0.00';
            document.getElementById('gst_amount_display').textContent = '₹0.00';
            document.getElementById('total_amount_display').textContent = '₹0.00';
            document.getElementById('sub_total_hidden').value = '0.00';
        }
    }

});