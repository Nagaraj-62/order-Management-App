# 🧾 Order Management App

A production-ready **Order Management System** built using the **Frappe Framework** as a technical assessment. The application demonstrates end-to-end business process implementation, including inventory management, workflow automation, role-based security, reporting, and REST API integration.

---

# ✨ Features

### 📦 Order Management

* Create and manage customer orders.
* Server-side validation to prevent invalid submissions.
* Mandatory item validation before saving orders.

### 📊 Inventory Management

* Automatic stock validation before confirmation.
* Inventory is reduced automatically when an order is confirmed.
* Prevents confirmation when sufficient stock is unavailable.

### 🔄 Workflow

* Order lifecycle managed through a workflow:

  * **Draft**
  * **Confirmed**
  * **Cancelled**
* Workflow actions are controlled through user roles.

### 👥 Role-Based Access Control

* Separate permissions for **User** and **Manager**.
* Managers control workflow approvals and cancellations.
* Users can create and manage their own orders.

### ⚡ Client-Side Enhancements

* Automatic total amount calculation.
* Real-time stock availability warnings.
* Improved user experience through instant field updates.

### 📈 Reports & Dashboard

* SQL-based Script Reports.
* Dashboard Chart showing order statistics by status.

### 🌐 REST API

* Whitelisted API for fetching confirmed orders.
* Supports optional date filters for integrations.

---

# 🚀 Installation

## 1. Create a Bench

Follow the official Frappe installation guide and create a bench.

Start the development server:

```bash
bench start
```

Open another terminal.

---

## 2. Create a Site

```bash
bench new-site testsite.localhost
```

---

## 3. Get the Application

```bash
bench get-app https://github.com/Nagaraj-62/order-Management-App
```

---

## 4. Install the App

```bash
bench --site testsite.localhost install-app order_management
```

---

## 5. Run Database Migration

The application includes a migration patch that automatically downloads sample data from **DummyJSON** and populates the following DocTypes:

* Customer
* Item

Run:

```bash
bench --site testsite.localhost migrate
```

---

## 6. Build Assets

```bash
bench build
```

---

## 7. Open the Application

```
http://testsite.localhost:8000
```

Login with your Administrator credentials.

---

# 🌐 REST API

## Endpoint

```
GET /api/method/order_management.api.get_orders
```

### Description

Returns all **Confirmed** orders along with customer information and order items.

---

## Optional Parameters

| Parameter | Description             |
| --------- | ----------------------- |
| from_date | Start date (YYYY-MM-DD) |
| to_date   | End date (YYYY-MM-DD)   |

Example:

```
GET /api/method/order_management.api.get_orders?from_date=2026-03-01&to_date=2026-03-31
```

---

## Sample Response

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
    ]
  }
}
```

---

# 🧪 Running Unit Tests

Execute the test suite using:

```bash
bench --site testsite.localhost run-tests --app order_management
```

The tests validate the application's core business logic and ensure reliable functionality.

---

# 📸 Screenshots

## Sales Order

<img width="1767" height="727" alt="Sales Order" src="https://github.com/user-attachments/assets/28d4ac5f-38dc-4415-84bb-dec210fe1316" />

---

## Workflow Configuration

<img width="1364" height="387" alt="Workflow 1" src="https://github.com/user-attachments/assets/5ce8a91e-c381-4e9f-8d4d-dc37689939d8" />

<img width="1388" height="348" alt="Workflow 2" src="https://github.com/user-attachments/assets/23fc5f35-7cf1-429b-ad85-a1e8efd382a8" />

---

## Role Permissions

<img width="1828" height="743" alt="Role Permissions" src="https://github.com/user-attachments/assets/f93b8616-f955-4483-90aa-8644a0847022" />

---

## Dashboard

<img width="1377" height="701" alt="Dashboard" src="https://github.com/user-attachments/assets/70aeb177-ad0c-48f2-80b4-5ccf6df3c5da" />

---

# 🛠️ Technology Stack

* Frappe Framework
* Python
* JavaScript
* MariaDB
* SQL
* HTML
* CSS

---
