import frappe
from frappe.utils import getdate

@frappe.whitelist(allow_guest=True)
def products():
    """
    Fetches active inventory items for the open public shop storefront layout.
    allow_guest=True ensures guest visitors can browse without authentication.
    """
    try:
        # Pull products using standard fields present in your frontend JS template mapping
        products = frappe.get_all(
        "Item",
        fields=["name", "item_name", "price", "stock", "custom_item_image", "item_group"],
        limit_page_length=100
        )
        return products
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), title="Storefront Catalog Fetch Failure")
        return []

@frappe.whitelist()
def get_orders(from_date=None, to_date=None):
    try:
        filters = {"status": "Confirmed"}

        if from_date and to_date:
            filters["order_date"] = ["between", [from_date, to_date]]

        orders = frappe.get_all(
            "Sales Order",
            filters=filters,
            fields=["name", "customer", "order_date", "total_amount"]
        )

        for order in orders:
            order["items"] = frappe.get_all(
                "Sales Order Item",
                filters={"parent": order.name},
                fields=["item", "quantity", "rate", "amount"]
            )

        return {"status": "success", "data": orders}

    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        return {"status": "error", "message": str(e)}



@frappe.whitelist(allow_guest=True)
def register_customer(full_name, email, password):
    if not full_name or not email or not password:
        frappe.throw("Full name, email and password are all required.")

    if len(password) < 6:
        frappe.throw("Password must be at least 6 characters.")

    if frappe.db.exists("User", email):
        frappe.throw("An account with this email already exists.")

    try:
        # 1. Create the Website User account
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "enabled": 1,
            "send_welcome_email": 0,
            "user_type": "Website User"
        })
        user.insert(ignore_permissions=True)
        user.new_password = password
        user.save(ignore_permissions=True)
        user.add_roles("Customer")

        # 2. Create the Customer record, linked via custom_user
        #    (custom_user is the single source of truth this app uses everywhere
        #    else — place_storefront_order, get_user_orders, get_order_timeline —
        #    so this MUST match or checkout/order-history lookups will fail)
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": full_name,
            "customer_type": "Individual",
            "email_id": email,
            "custom_user": email
        })
        customer.insert(ignore_permissions=True)

        frappe.db.commit()

        # 3. Log the new user straight in so they land on the shop already signed in
        logged_in = False
        try:
            frappe.local.login_manager.login_as(email)
            logged_in = True
        except Exception:
            frappe.log_error(frappe.get_traceback(), title="Auto-login after signup failed")

        return {
            "status": "success",
            "customer": customer.name,
            "logged_in": logged_in
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), title="Customer signup failed")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_dashboard_stats():
    total_orders = frappe.db.count("Sales Order")

    confirmed_orders = frappe.db.count(
        "Sales Order",
        {"status": "Confirmed"}
    )

    draft_orders = frappe.db.count(
        "Sales Order",
        {"status": "Draft"}
    )

    total_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM `tabSales Order`
        WHERE status = 'Confirmed'
    """)[0][0]

    low_stock_count = frappe.db.count(
        "Item",
        {
            "stock": ["<", 10]
        }
    )
    
    low_stock_items = frappe.get_all(
        "Item",
        filters={"stock": ["<=", 10]},
        fields=["item_name", "stock"]
    )

    recent_orders = frappe.get_all(
        "Sales Order",
        fields=[
            "name",
            "customer",
            "status",
            "total_amount",
            "creation"
        ],
        order_by="creation desc",
        limit=5
    )
    
    status_data = frappe.db.sql("""
        SELECT
            status,
            COUNT(*) as count
        FROM `tabSales Order`
        GROUP BY status
    """, as_dict=True)

    top_customers = frappe.db.sql("""
        SELECT
            customer,
            SUM(total_amount) as revenue
        FROM `tabSales Order`
        WHERE status = 'Confirmed'
        GROUP BY customer
        ORDER BY revenue DESC
        LIMIT 5
    """, as_dict=True)

    return {
        "total_orders": total_orders,
        "confirmed_orders": confirmed_orders,
        "draft_orders": draft_orders,
        "revenue": total_revenue,
        "low_stock_count": low_stock_count,
        "recent_orders": recent_orders,
        "status_data": status_data,
        "top_customers": top_customers,
        "low_stock_items": low_stock_items
    }


@frappe.whitelist()
def update_items(item_name, price, stock, image_url):
    """Updates stock and rate attributes inside custom Item master entries"""
    try:
        if frappe.db.exists("Item", item_name):
            item = frappe.get_doc("Item", item_name)
            item.standard_rate = price
            item.stock = stock
            item.image = image_url
            item.save(ignore_permissions=True)
            return {"status": "success", "message": "Item properties updated successfully"}
        else:
            return {"status": "error", "message": "Target Item key records missing"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), title="Item Property Form Push Failure")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def get_current_user_info():
    """
    Checks if the visitor has an active logged-in session.
    Returns guest information or the logged-in User's first name.
    """
    current_user = frappe.session.user
    
    if current_user and current_user != "Guest":
        user_doc = frappe.get_doc("User", current_user)
        return {
            "logged_in": True,
            "first_name": user_doc.first_name,
            "email": user_doc.email
        }
    
    return {
        "logged_in": False,
        "first_name": "Guest"
    }

@frappe.whitelist()
def place_storefront_order(cart_json):
    """
    Accepts a JSON string representing the cart items from the frontend,
    resolves the active logged-in customer user, and creates a Sales Order.
    """
    import json
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required. Please sign in to place your order.")

    try:
        cart = json.loads(cart_json)
        if not cart:
            return {"status": "error", "message": "Cart is completely empty."}

        # 1. Resolve Customer link mapping using active session user email
        customer_name = frappe.db.get_value("Customer", {"custom_user": frappe.session.user}, "name")
        if not customer_name:
            # Fallback helper if Customer mapping isn't fully linked yet
            customer_name = frappe.db.get_value("Customer", {"email": frappe.session.user}, "name")
        
        if not customer_name:
            user=frappe.get_doc("User",frappe.session.user)
            new_customer=frappe.get_doc({
                "doctype":"Customer",
                "customer_name": user.full_name or user.first_name,
                "email": user.email,
                "custom_user": user.name
            })
            new_customer.insert(ignore_permissions=True)
            customer_name=new_customer.name
            # frappe.throw(f"No customer account record found linked to user profile: {frappe.session.user}")

        # 2. Structure child item table lines array
        order_items = []
        for item, quantity in cart.items():
            if quantity <= 0:
                continue
                
            # Fetch active standard rate price records directly from the database to prevent fraud
            rate = frappe.db.get_value("Item", item, "price") or 0
            stock = frappe.db.get_value("Item", item, "stock") or 0
            remaining_stock= stock - quantity
            frappe.db.set_value("Item", item, "stock", remaining_stock)

            
            order_items.append({
                "item": item,
                "quantity": quantity,
                "rate": rate
            })

        if not order_items:
            return {"status": "error", "message": "No valid items to place an order."}

        # 3. Assemble and insert the Sales Order master record
        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer_name,
            "order_date": frappe.utils.today(),
            # "delivery_date": frappe.utils.today(), # Zepto 10 min style delivery targets today
            "items": order_items,
            "status": "Draft" # Saves it as Draft so your admin desk dashboard console picks it up!
        })
        
        # Bypass permission walls safely for the checkout user profile context
        sales_order.insert(ignore_permissions=True)
        
        return {
            "status": "success",
            "message": "Order placed successfully!",
            "order_id": sales_order.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), title="Storefront Checkout Submission Failure")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def get_user_orders():
    """Order history for the logged-in customer, most recent first."""
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to view your orders.")

    customer_name = frappe.db.get_value("Customer", {"custom_user": frappe.session.user}, "name") \
        or frappe.db.get_value("Customer", {"email": frappe.session.user}, "name")

    if not customer_name:
        return []

    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer_name},
        fields=["name", "order_date", "status", "total_amount", "creation", "modified"],
        order_by="creation desc"
    )

    for order in orders:
        order["items"] = frappe.get_all(
            "Sales Order Item",
            filters={"parent": order.name},
            fields=["item", "quantity", "rate", "amount"]
        )

    return orders


@frappe.whitelist()
def get_order_timeline(order_name):
    """Status change history for one order, built from the Version log.
    Requires 'Track Changes' enabled on the Sales Order doctype."""
    if frappe.session.user == "Guest":
        frappe.throw("Please log in.")

    order = frappe.get_doc("Sales Order", order_name)

    customer_name = frappe.db.get_value("Customer", {"custom_user": frappe.session.user}, "name") \
        or frappe.db.get_value("Customer", {"email": frappe.session.user}, "name")

    if order.customer != customer_name and "Manager" not in frappe.get_roles():
        frappe.throw("You don't have permission to view this order.", frappe.PermissionError)

    import json
    events = [{"status": "Draft", "time": str(order.creation)}]

    versions = frappe.get_all(
        "Version",
        filters={"ref_doctype": "Sales Order", "docname": order_name},
        fields=["data", "creation"],
        order_by="creation asc"
    )

    for v in versions:
        try:
            changed = json.loads(v.data).get("changed", [])
            for field, old_val, new_val in changed:
                if field == "status":
                    events.append({"status": new_val, "time": str(v.creation)})
        except Exception:
            continue

    if not any(e["status"] == order.status for e in events):
        events.append({"status": order.status, "time": str(order.modified)})

    return {"order": order.name, "current_status": order.status, "events": events}