---

# 🧾 Order Management App (Frappe Custom App)

This application is a production-ready internal order tracking system built as a technical assessment. It demonstrates a full-stack implementation using the Frappe Framework, focusing on inventory integrity, automated workflows, and RESTful integration.

## 🚀 Installation Steps

To install and set up this app on your local Frappe environment:

1. **install the App:**
```bash
bench new-app order_management

```


2. **Install to Site:**
```bash
bench --site mysite.local install-app order_management

```


3. **Database Migration & Seeding:**
This command will run the patch that automatically fetches sample data from **DummyJSON** and seeds the Item and Customer DocTypes.
```bash
bench migrate

```


4. **Build Assets:**
```bash
bench build

```



---

## ✨ Features Implemented

The app covers  technical requirements from the project brief:

* **Logic:** Server-side validation for stock availability and mandatory item checks.
* **Inventory:** Automated stock reduction logic upon "Confirmed" status.
* **UX:** Client-side scripts for real-time total calculations and stock warnings.
* **Workflow:** Managed state transitions from `Draft` ➔ `Confirmed` ➔ `Cancelled`.
* **Security:** Role-based access control (RBAC) separating `User` and `Manager` capabilities.
* **Analytics:** SQL-based Script Reports and a Dashboard chart for order status.

---

## 🌐 API Endpoint Details

The app exposes a whitelisted REST API for third-party integration.

* **Endpoint:** `GET /api/method/order_management.api.get_orders`
* **Description:** Fetches all orders with a status of "Confirmed," including customer details and child table items.
* **Parameters:**
* `from_date` (Optional): Start date filter (YYYY-MM-DD).
* `to_date` (Optional): End date filter (YYYY-MM-DD).


* **Response Format:**
```json
{
  "message": {
    "status": "success",
    "data": [
      {
        "name": "SAL-ORD-0011",
        "customer": "Henry Hill",
        "order_date": "2026-03-02",
        "total_amount": 198,
        "items": [
          {
            "item": "Ice Cream",
            "quantity": 2,
            "rate": 99,
            "amount": 198
          }
        ]
     }
}

```



---

## 📸 Screenshots


1. **Sales Order UI:**
   <img width="1767" height="727" alt="Screenshot 2026-03-02 111655" src="https://github.com/user-attachments/assets/28d4ac5f-38dc-4415-84bb-dec210fe1316" />

3. **Workflow Configuration:**
   <img width="1364" height="387" alt="Screenshot 2026-03-02 111756" src="https://github.com/user-attachments/assets/5ce8a91e-c381-4e9f-8d4d-dc37689939d8" />
   <img width="1388" height="348" alt="Screenshot 2026-03-02 111819" src="https://github.com/user-attachments/assets/23fc5f35-7cf1-429b-ad85-a1e8efd382a8" />

5. **Role Permissions:**
   <img width="1828" height="743" alt="Screenshot 2026-03-02 104911" src="https://github.com/user-attachments/assets/f93b8616-f955-4483-90aa-8644a0847022" />

6. **Custom Dashboard:**
   <img width="1377" height="701" alt="image" src="https://github.com/user-attachments/assets/70aeb177-ad0c-48f2-80b4-5ccf6df3c5da" />


---

## 🧪 Unit Testing

I have included a unit test suite to verify the core business logic.

```bash
bench --site mysite.local run-tests --app order_management

```

---
