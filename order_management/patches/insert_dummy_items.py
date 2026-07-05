import frappe
import requests


def execute():
    insert_customers()
    insert_items()
    frappe.db.commit()
    frappe.log("Dummy customers and items inserted successfully.")


    
# Insert Dummy Customers


def insert_customers():
    url = "https://dummyjson.com/users"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        users = response.json().get("users", [])
    except Exception as e:
        frappe.log_error(f"Failed fetching users: {str(e)}")
        return

    for user in users:
        full_name = f"{user.get('firstName')} {user.get('lastName')}"
        email = user.get("email")
        phone = user.get("phone")

        if frappe.db.exists("Customer", {"customer_name": full_name}):
            continue

        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": full_name,
            "email": email,
            "phone": phone,
            "status": "Active"
        }).insert()



# Insert  Dummy Items


def insert_items():
    url = "https://dummyjson.com/products"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        products = response.json().get("products", [])
    except Exception as e:
        frappe.log_error(f"Failed fetching products: {str(e)}")
        return

    for product in products:
        item_name = product.get("title")
        price = product.get("price")
        stock = product.get("stock", 50)
        image_url = product.get("thumbnail")
        description = product.get("description")

        if frappe.db.exists("Item", {"item_name": item_name}):
            continue
            # frappe.set_value("Item", item_name, {
            #     "custom_item_image": image_url,
            #     "custom_description": description
            # })
        frappe.get_doc({
            "doctype": "Item",
            "item_name": item_name,
            "price": price,
            "stock": stock,
            "custom_image": image_url,
            "custom_description": description
        }).insert()