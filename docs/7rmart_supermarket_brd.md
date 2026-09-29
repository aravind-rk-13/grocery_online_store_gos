**BUSINESS REQUIREMENTS DOCUMENT**

**7rmart Supermarket — Online Grocery Ordering & Delivery Platform**

_Prepared from analysis of the live administration console at_

_groceryapp.uniqassosiates.com/admin_

| **Document Title** | Business Requirements Document (BRD) — 7rmart Supermarket Online Grocery Platform |
| --- | --- |
| **Prepared By** | Aravind, Reizend Pvt. Limited |
| **Organisation** | Reizend Pvt. Limited |
| **Document Date** | 24 August 2026 |
| **Document Status** | Draft v1.0 — For Stakeholder Review |
| **Source of Analysis** | Live walkthrough of the production admin console (all accessible modules) |

# Document Control

## Version History

| **Version** | **Date** | **Author** | **Description of Change** |
| --- | --- | --- | --- |
| 0.1 | 24-Aug-2026 | Aravind | Initial draft compiled from structured walkthrough of the live admin console. |
| 1.0 | 24-Aug-2026 | Aravind | First version circulated for stakeholder review. |

## Distribution / Review List

| **Name / Role** | **Organisation** | **Purpose** |
| --- | --- | --- |
| Product Owner / Business Sponsor | Reizend Pvt. Limited | Review & sign-off |
| Project Manager | Reizend Pvt. Limited | Planning & scheduling |
| Technical Lead / Development Team | Implementation Partner | Solution design & build |
| QA Lead | Implementation Partner | Test planning |

# 1. Introduction

## 1.1 Purpose of the Document

This Business Requirements Document (BRD) defines the business objectives, functional scope, and operating rules of the 7rmart Supermarket platform — an online grocery ordering and delivery system currently live in production. The document has been compiled by directly and systematically exploring the platform's administration console, module by module, rather than from a specification handed down in advance. Its purpose is to give business and technical stakeholders a single, agreed reference of what the system does today, so that it can be used as the baseline for a subsequent phase of enhancement, re-platforming, audit, or handover.

The BRD captures the system strictly as observed at the time of analysis (24 August 2026). Where the analysis surfaced ambiguities, defects, or features that exist in the data model but are not exposed or working end-to-end, these are called out explicitly in Section 8 (Known Issues and Gaps) rather than silently smoothed over, since an accurate baseline is more useful to the business than an idealised one.

## 1.2 Scope of This Document

This document covers the back-office administration console of the 7rmart Supermarket application, which is the operational control centre for the business: catalogue management, order processing, delivery operations, customer administration, promotions, content, payments, financial reconciliation, and platform administration. The customer-facing storefront and mobile applications were not part of the URL provided for analysis and are therefore referenced only indirectly, through the data and configuration screens that drive them (for example, sliders, push notifications, and CMS pages that are clearly intended for the shopper-facing app or website).

## 1.3 Intended Audience

* Business stakeholders and sponsors at Reizend Pvt. Limited who need a clear picture of current platform capability before approving further investment.
* Project and product managers who will scope the next phase of work (enhancement, re-platform, or integration).
* Business analysts and solution architects who will translate these business requirements into technical/functional specifications.
* Development and QA teams who need an authoritative list of existing modules and behaviours to avoid regressions.

## 1.4 Methodology

Requirements in this document were derived using a structured, hands-on walkthrough of the live admin console rather than by interviewing stakeholders or reading a prior specification. The approach was as follows:

* Authenticated to the admin console at the URL provided (groceryapp.uniqassosiates.com/admin) using administrator credentials.
* Enumerated every navigation entry in the console, including entries nested inside collapsible sub-menus (Manage Expense, Report, Manage Content, Manage Category, Settings), by inspecting the underlying page structure rather than relying on visual scrolling alone.
* Opened every list/module screen, recorded the data fields and columns displayed, the record counts, the available actions (create, edit, delete, status change, and workflow actions such as 'Assign Delivery Boy'), and captured representative data.
* Opened the corresponding 'Add/Create' forms for the core business entities (Product, Category, Location, and others) to capture field-level validation and data-entry requirements, not just what is shown in list views.
* Opened a sample transactional record (an order) end-to-end to confirm the order data model (customer, delivery address, line items, pricing, and totals).
* Noted every module that returned a server error instead of a working screen, and recorded it as a gap rather than guessing at intended behaviour.

## 1.5 Definitions, Acronyms and Abbreviations

| **Term** | **Definition** |
| --- | --- |
| BRD | Business Requirements Document |
| Admin Console | The password-protected back-office web application used by staff to operate the platform (the subject of this document) |
| COD | Cash on Delivery — a payment method settled in cash at the point of delivery |
| SKU / Product Code | The unique product identifier used in the catalogue (e.g. P4310691) |
| DB (in Admin Users context) | 'Delivery Boy' user type — an admin-console login used by delivery personnel |
| Offer Code | A promotional discount code, expressed as a percentage or a flat amount, applied to qualifying orders |
| CMS | Content Management System — the set of screens used to maintain customer-facing text pages, footer details, and news |
| RBAC | Role-Based Access Control |
| Combo Pack | A product flag indicating the item is sold as a bundled/combo unit rather than a single item |

# 2. Business Overview

## 2.1 Business Context

7rmart Supermarket operates an online grocery ordering and home-delivery business. Customers order groceries through a customer-facing application (mobile app and/or website, inferred from the admin console's app-facing configuration screens such as sliders, mobile sliders, and push notifications). Orders are fulfilled from a catalogue of packaged and fresh grocery items, priced by weight, piece, litre, or serving, and delivered by a distributed pool of delivery personnel. The business operates across multiple towns/postal areas in the United Kingdom, with delivery charges varying by registered delivery location, and settles payment either electronically or by cash on delivery, which is then reconciled centrally through an internal expense/cash ledger.

## 2.2 Business Objectives

* Provide customers with an online ordering channel for everyday grocery and household items, organised into a structured category and sub-category catalogue.
* Operate a reliable, trackable delivery workflow from order placement through to 'Delivered' status, with a delivery boy assigned per order and a delivery time-window recorded.
* Support two payment models — Cash on Delivery and card/bank payment — while capping COD exposure through a configurable per-order pay limit.
* Grow order volume and customer retention through promotions (percentage or flat-amount offer codes) and marketing surfaces (homepage sliders, push notifications, featured products).
* Give the business visibility into cash collected by delivery staff versus cash/bank settled centrally, to keep COD collections reconciled and reduce cash-handling risk.
* Allow non-technical staff to maintain the public-facing content (About Us, Terms & Conditions, Privacy Policy, Refund Policy, contact details, and news) without requiring a developer.
* Maintain a controlled, role-based staff access model so that different classes of internal user (administrators, staff, delivery-boy accounts) have appropriately scoped access to the console.

## 2.3 Stakeholders

| **Stakeholder** | **Interest in the System** |
| --- | --- |
| Business Owner / Management (Reizend Pvt. Limited) | Overall commercial performance, order volume, margin, and expansion into new delivery locations. |
| Store / Catalogue Operations Staff | Maintaining accurate product, pricing, stock, and category data ("Admin" and "staff" user types). |
| Delivery Operations / Dispatch Staff | Assigning orders to delivery personnel, managing delivery time slots, and tracking order status. |
| Delivery Personnel ("Delivery Boy") | Receiving assigned orders, collecting COD cash, updating delivery status. |
| Finance / Accounts Staff | Reconciling cash and bank credits/debits per order against the expense ledger; managing expense categories such as salaries, fuel, and loan repayments. |
| Customers (App/Web Shoppers) | Placing orders, tracking delivery, using offer codes, contacting support — served indirectly via the console's content and configuration screens. |
| Platform Administrator | Managing admin user accounts, roles, passwords, and the dynamic menu/navigation configuration. |
| Customer Support Staff | Verifying new user registrations and responding to customer feedback. |

## 2.4 In Scope and Out of Scope

### In Scope of This Document

* All administration console modules reachable from the authenticated admin session, as enumerated in the Appendix (Section 10).
* Business rules and data structures inferred from list screens, create/edit forms, and one transactional record (order) opened in full.

### Out of Scope of This Document

* The customer-facing mobile application and website UI/UX were not supplied for review and are therefore not documented directly — only the admin-side configuration that feeds them is covered.
* Underlying technical architecture, database schema, and source code were not reviewed; all findings are based on observed application behaviour only.
* Payment gateway integration details, SMS/e-mail provider integration, and push-notification delivery infrastructure were not testable from the console and are not documented beyond the presence of the relevant admin screens.

# 3. Current System Overview (As-Is)

## 3.1 Platform Snapshot at Time of Analysis

The admin console's dashboard exposes the following live record counts, which give a sense of the platform's current operating scale:

| **Metric** | **Count at Time of Review** | **Notes** |
| --- | --- | --- |
| Registered App Users | 20 (16 pending verification) | 'Manage Users' vs. 'Verify Users' screens |
| Admin Console Users | 1,146 | Includes admin, staff, and delivery-boy login types |
| Product Categories | 209 | Includes many duplicate/test entries — see Section 8 |
| Catalogue Products | 652 | Spread across categories such as Dairy, Dry Fruits & Nuts, Vegetables, etc. |
| Orders | 181 (20 shown on default order list filter) | Statuses include COD, UNPAID, PAID, OUT FOR DELIVERY, DELIVERED |
| Delivery Locations | 237 | UK towns/postal areas, each with its own delivery charge |
| Delivery Personnel | 306 | 'Manage Delivery Boy' module |
| Offer Codes | 10 | Mostly 0% today, i.e. inactive discount value, plus a small number of live percentage/flat offers |
| Homepage Sliders / Mobile Sliders | 1 / 14 | Marketing banners for web and mobile channels respectively |
| CMS Pages | 13 | About Us, Terms & Conditions, Privacy Policy, Refund Policy, product-launch announcements, etc. |
| News Items | ≈60 (33 pages) | Many appear to be test/placeholder entries |

## 3.2 Technology Indicators Observed

While a source-code review was out of scope, the following technical characteristics were evident from the application's own error output and behaviour, and are recorded here because they materially affect delivery risk and should inform the next phase of technical due diligence:

* The application is built on the CodeIgniter PHP framework (visible in unhandled exception traces) and is deployed on a standard LAMP-style hosting stack.
* The admin UI is built on the AdminLTE (Bootstrap) admin theme, giving a responsive, desktop-oriented layout with a collapsible left-hand navigation.
* Currency is displayed in Pounds Sterling (£) throughout orders, offers, and payments, and delivery locations are drawn from a fixed list of UK counties/regions, indicating the platform's current live market is the United Kingdom.
* Several navigation entries point to routes that return unhandled server errors (HTTP 500 / 404 exceptions) rather than a working screen — see Section 8.
* Site navigation itself is data-driven: the 'Menu Management' module stores every sidebar entry, its icon, its display order, and an Active/Inactive flag, meaning menu items can be shown or hidden without a code deployment. Two entries — 'Purchased Packages' and 'Manage Package' — exist in this configuration but are currently marked Inactive, indicating a subscription/package feature was built (or scaffolded) but is not currently switched on.

## 3.3 User Roles Identified

| **Role** | **Observed In** | **Apparent Purpose** |
| --- | --- | --- |
| admin | Admin Users list ('Usertype' column) | Full back-office access; can manage catalogue, orders, users, and other admins. |
| staff | Admin Users list | Operational staff account, likely scoped to day-to-day catalogue/order tasks. |
| db (delivery boy) | Admin Users list | A console-level login associated with a delivery person, distinct from the 'Manage Delivery Boy' operational record. |
| App Customer | Manage Users / Verify Users | Shopper who registers via the customer-facing app; accounts start 'Unverified' and require manual admin verification before becoming fully Active. |

_Note: the console does not expose a visible screen for defining custom roles or granular permissions per user type; access appears to be governed by the fixed usertype value (admin / staff / db) rather than a configurable permission matrix. This should be confirmed with the technical team during the next phase, as it is a common area where BRDs later uncover hidden complexity._

# 4. Functional Requirements

This section documents the functional capability of each module observed in the admin console. Requirements are grouped by business capability and each is assigned an identifier for traceability. Priority reflects the module's apparent centrality to daily operation, not a business-confirmed ranking — it should be validated with stakeholders before being used to plan a build.

## 4.1 Dashboard & Operational Summary

On login, the system presents a dashboard of colour-coded summary tiles, each showing a live count for a business entity (Pages, Admin Users, Category, Product, Offer Code, COD, Slider, Delivery Boy, Users, Orders, Location, Mobile Slider, News, Expense) with a 'More Info' link that navigates directly to the corresponding management screen.

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-DASH-01 | The system shall display, immediately after login, a single-screen dashboard of count tiles for at least: Pages, Admin Users, Categories, Products, Offer Codes, COD setting, Sliders, Delivery Boys, App Users, Orders, Locations, Mobile Sliders, News, and Expenses. | High |
| FR-DASH-02 | Each dashboard tile shall provide a direct navigation link ('More Info') to the full management screen for that entity. | High |
| FR-DASH-03 | Dashboard counts shall reflect live data at the time the dashboard is loaded (no manual refresh/report generation step observed). | Medium |

## 4.2 Customer (App User) Management

Customer accounts created through the shopper-facing app appear first under 'Verify Users' in an Unverified state and must be manually reviewed before becoming fully Active in 'Manage Users'. Once active, an administrator can Block/Unblock or permanently delete an account.

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-USR-01 | The system shall list all customer self-registrations pending verification, showing name, phone, e-mail, masked password, registration date, and User ID. | High |
| FR-USR-02 | The system shall allow an administrator to verify (approve) or delete a pending customer registration. | High |
| FR-USR-03 | The system shall maintain a separate, searchable list of all verified customer accounts, showing name, contact details, registration date, and current status (Active/Inactive). | High |
| FR-USR-04 | The system shall allow an administrator to Block (deactivate) or Unblock (reactivate) a verified customer account without deleting it. | High |
| FR-USR-05 | The system shall allow an administrator to permanently delete a customer account. | Medium |
| FR-USR-06 | The system shall provide a search facility to locate customer accounts (and a Reset control to clear search filters), on both the pending and verified user lists. | Medium |
| FR-USR-07 | The system shall provide a 'Details' drill-through for each customer record, and shall mask stored passwords behind a reveal control rather than displaying them in plain text by default. | Medium |

## 4.3 Catalogue Management (Category, Sub-Category, Group, Product)

The catalogue is organised as a three-tier hierarchy — Category, then Sub-Category, then Product — with an orthogonal, optional 'Group' tag (Organic, Vegan, Gluten Free, Goodness) that can be attached to a category for merchandising purposes.

### 4.3.1 Category & Sub-Category

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-CAT-01 | The system shall allow creation and maintenance of top-level product Categories, each with a name, an image (300×300 px), an Active/Inactive status, and zero or more associated Groups. | High |
| FR-CAT-02 | The system shall allow a Category to be flagged, independently, for display on the storefront's top navigation menu and/or its left-hand navigation menu ('Show on Top Menu' / 'Show on Left Menu'). | Medium |
| FR-CAT-03 | The system shall allow creation and maintenance of Sub-Categories, each linked to exactly one parent Category, with its own name, optional image, and Active/Inactive status. | High |
| FR-CAT-04 | The system shall allow creation and maintenance of merchandising Groups (e.g. Organic, Vegan, Gluten Free, Goodness) that can be attached to one or more Categories. | Low |
| FR-CAT-05 | The system shall support Edit and Delete actions on Categories and Sub-Categories, with a confirmation step before deletion. | High |

### 4.3.2 Product

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-PROD-01 | The system shall allow creation of a Product with, at minimum: Title, Product Type (Veg / Non-Veg / Others), Category, Sub-Category, optional free-text Tag, and optional Group. | High |
| FR-PROD-02 | The system shall allow a Product's Price Type to be set to Weight, Piece, Litre, or Serves, and shall capture the corresponding Weight Value and Weight Unit (grams/kilograms) when Price Type is Weight. | High |
| FR-PROD-03 | The system shall capture, per Product: Selling Price, MRP, Purchase Price, Stock Availability (in kg or units), a maximum orderable quantity, and an 'Unlimited Stock' override flag. | High |
| FR-PROD-04 | The system shall capture a rich-text Description per Product, a primary display Image (285×164 px), and multiple secondary/gallery images (900×900 px). | Medium |
| FR-PROD-05 | The system shall allow a Product to be independently flagged as Active/Inactive (Status), In-Stock/Out-of-Stock (Stock), Featured (Yes/No), and Combo Pack (Yes/No). | High |
| FR-PROD-06 | The system shall auto-generate and display a unique product code (e.g. 'P4310691') for every Product, for use in operations and reconciliation. | Medium |
| FR-PROD-07 | The system shall present the full Product catalogue in a searchable, paginated list showing Title, Type, Category >> Sub-Category, Image, Min–Max order quantity, Stock, Status, and Featured flag, and shall support Edit and Delete per Product. | High |

## 4.4 Order Management

Each order is placed by a registered customer against a delivery address, and carries a payment mode (COD or Bank), a fulfilment status, and a set of line items priced from the catalogue. Administrators manage the order lifecycle from this module.

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-ORD-01 | The system shall present a searchable, paginated list of all orders, showing Order ID, customer name/phone/e-mail, order date, order amount, payment mode, and current status. | High |
| FR-ORD-02 | The system shall allow an administrator to open a full Order Detail view showing the customer's delivery address, an itemised list of products ordered (image, description, unit price, quantity, and line subtotal), the order subtotal, delivery charge, and grand total, with a Print action. | High |
| FR-ORD-03 | The system shall allow an administrator to change an order's status (observed values include COD, UNPAID, PAID, OUT FOR DELIVERY, DELIVERED) as it progresses through fulfilment. | High |
| FR-ORD-04 | The system shall allow an administrator to set or change the delivery date and a delivery time window for an order. | High |
| FR-ORD-05 | The system shall allow an administrator to assign (or re-assign) a named Delivery Boy to an order, and shall display the currently assigned delivery person on the order list. | High |
| FR-ORD-06 | The system shall allow an administrator to delete an order record. | Medium |
| FR-ORD-07 | The system shall provide a 'Create New Order' capability for staff to place an order on a customer's behalf (e.g. for phone orders); at the time of review this function's screen returned a server error and could not be functionally verified — see Section 8. | High |
| FR-ORD-08 | The system shall provide Consolidated and Order-level reporting views under a 'Report' menu; at the time of review both screens returned a server error and could not be functionally verified — see Section 8. | High |

## 4.5 Delivery & Logistics Management

### 4.5.1 Delivery Personnel

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-DEL-01 | The system shall maintain a directory of delivery personnel with Name, e-mail, phone number, address, a system Username, a masked Password, and an Active/Inactive status. | High |
| FR-DEL-02 | The system shall allow creation, editing, and deletion of delivery-personnel records, and a 'Details' drill-through per record. | High |
| FR-DEL-03 | The system shall make active delivery personnel selectable from the Order Management screen for assignment to individual orders (see FR-ORD-05). | High |

### 4.5.2 Delivery Locations & Charges

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-LOC-01 | The system shall maintain a list of serviceable delivery locations, each associated with a Country and State/County, a free-text location/area name, a delivery charge, and an Active/Inactive status. | High |
| FR-LOC-02 | The system shall allow the delivery charge to be set independently per location, so that delivery cost can vary by area. | High |
| FR-LOC-03 | The system shall support Create, Edit, Delete, and Search operations on delivery locations. | High |
| FR-LOC-04 | The Country/State selection shall be presented as a dependent dropdown pair; at the time of review the State list was populated exclusively with United Kingdom counties/regions. | Medium |

## 4.6 Payments

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-PAY-01 | The system shall maintain a list of accepted payment methods (observed: 'Cash on Delivery' and 'Banking/Debit/Credit Card'), each with an editable name, a pay limit, and an Active/Inactive status. | High |
| FR-PAY-02 | The system shall provide a global Cash-on-Delivery toggle (Yes/No) that can enable or disable COD as an accepted payment mode platform-wide. | High |
| FR-PAY-03 | The system shall enforce (or at minimum record) a maximum order value eligible for Cash on Delivery, via the configured COD pay limit. | Medium |

## 4.7 Promotions & Merchandising

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-PROMO-01 | The system shall allow creation of Offer Codes, each with a code/name, a discount expressed as a Percentage or a flat Amount, a promotional image, and an Active/Inactive status. | High |
| FR-PROMO-02 | The system shall support Create, Edit, Delete, and Search operations on Offer Codes. | High |
| FR-PROMO-03 | The system shall allow management of homepage banner Sliders (image plus destination link) and a separate set of Mobile Sliders for the app's home screen, each with Active/Inactive status. | Medium |
| FR-PROMO-04 | The system shall allow individual Products to be flagged as 'Featured' for prioritised display on the storefront. | Medium |
| FR-PROMO-05 | The system shall allow individual Products to be flagged as 'Combo Pack' to denote bundled items. | Low |

## 4.8 Content Management & Customer Communication

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-CMS-01 | The system shall provide a CMS for standalone content pages (e.g. About Us, Terms & Conditions, Privacy Policy, Cancellation & Refund Policy, promotional landing pages), each with a Title, rich Description, Image, and a unique page slug; supporting Create, Edit, and Delete. | High |
| FR-CMS-02 | The system shall provide a single editable record for footer contact details (Address, e-mail, Phone) shown on the customer-facing site/app. | Medium |
| FR-CMS-03 | The system shall provide a single editable record for general contact and delivery configuration: support Phone, e-mail, Address, a delivery-time value, and a delivery-charge threshold/limit. | Medium |
| FR-CMS-04 | The system shall provide a News module supporting Create, Edit, Delete, and paginated listing of announcements shown to customers. | Medium |
| FR-CMS-05 | The system shall allow administrators to compose and send Push Notifications (Title and Description) to the customer-facing app. | High |

## 4.9 Financial Management (Expense & Cash Reconciliation)

Beyond order revenue, the platform maintains an internal ledger reconciling cash collected by delivery personnel against bank settlement, alongside general business expense tracking.

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-FIN-01 | The system shall maintain a list of Expense Categories (observed: Salaries, Loan Amount, Fuel Expense) supporting Create, Edit, and Delete. | Medium |
| FR-FIN-02 | The system shall record individual Expense/ledger entries, each with a Title, Date, and five monetary movement fields — Credit Bank, Debit Bank, Credit Cash, Debit Cash, and Cash With Delivery-Boy — to reconcile order-level cash and bank settlement. | High |
| FR-FIN-03 | The system shall allow ledger entries to be traced back to the originating Order and, where relevant, the Staff/Delivery-Boy who collected the cash (as seen in entry titles such as 'Order-177(Staff-DB)'). | Medium |
| FR-FIN-04 | The system shall provide a 'Create Merchant' capability for onboarding merchant/vendor records associated with expenses; at the time of review this screen returned a server error and could not be functionally verified — see Section 8. | Medium |

## 4.10 Platform Administration & Access Control

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-ADM-01 | The system shall maintain a directory of Admin Console user accounts, each with a Username, a Usertype (admin / staff / db), a masked Password, and an Active/Inactive status. | High |
| FR-ADM-02 | The system shall allow an authorised administrator to create, edit, block/unblock, and delete Admin Console user accounts. | High |
| FR-ADM-03 | The system shall allow the logged-in administrator to change their own password by providing their current password plus a new password and confirmation. | High |
| FR-ADM-04 | The system shall provide a 'Menu Management' screen allowing an administrator to add, edit, re-order, and enable/disable entries in the console's own navigation menu, including nested (parent/child) entries, without requiring a code change. | Medium |
| FR-ADM-05 | The system shall allow individual menu entries to be marked Inactive to hide a feature from the navigation while retaining its configuration (as currently done for 'Purchased Packages' and 'Manage Package'). | Low |

## 4.11 Customer Feedback

| **ID** | **Requirement** | **Priority** |
| --- | --- | --- |
| FR-FDBK-01 | The system shall provide a screen for administrators to review customer feedback submitted through the app; at the time of review this screen returned a server error and could not be functionally verified — see Section 8. | Medium |

# 5. Non-Functional Requirements

The items below describe qualities the system should exhibit. Several are stated as recommendations rather than confirmed requirements, because they could not be conclusively verified from the admin console alone (e.g. true response time under load, or backup policy) and should be validated with the hosting/technical team.

## 5.1 Usability

* The admin console shall remain usable on standard desktop browser widths (observed layout is a fixed left-hand navigation with a fluid content area, consistent with the AdminLTE framework).
* List screens holding large record counts (e.g. 652 products, 1,146 admin users, 209 categories) shall be paginated (20 records/page observed) with visible page-number navigation, Search, and Reset controls, so staff are not forced to scroll an unbounded list.

## 5.2 Security & Access Control

* Access to the admin console shall require authentication (username/password) with a session that expires and returns unauthenticated users to the login screen.
* Stored passwords shall not be shown in plain text by default in list views; a masked/reveal control was observed for user, delivery-boy, and admin passwords and this behaviour should be preserved and, ideally, strengthened (e.g. remove plain-text reveal entirely in favour of a reset flow).
* Distinct account types (admin / staff / db) exist and should be backed by an explicit, documented permission model rather than convention, since none was visibly configurable in the console — see the open question in Section 3.3.
* Self-registered customer accounts shall remain Unverified/inactive until an administrator explicitly verifies them, preventing unmoderated accounts from transacting immediately.

## 5.3 Performance & Scalability

* The catalogue and admin-user lists already run into the hundreds/low-thousands of records; list queries, search, and pagination shall continue to perform acceptably as these volumes grow with business expansion into new locations.
* Dashboard tile counts shall load without noticeably degrading initial page load time as record volumes increase.

## 5.4 Reliability & Availability

* Core transactional flows (placing/viewing orders, changing order status, assigning delivery personnel) shall be available with high uptime, given that delivery operations depend on them in real time.
* Server-side errors (see Section 8) shall be resolved so that no primary navigation entry leads to an unhandled exception page in production.

## 5.5 Data Integrity & Auditability

* Financial ledger entries (Section 4.9) shall be traceable to the order and staff/delivery-boy involved, to support audit of cash handling.
* Status-changing actions on orders (status, delivery date, delivery-boy assignment) and on user accounts (verify, block/unblock, delete) shall be auditable — the current console does not visibly expose an audit trail of who made a change and when, which should be reviewed with the technical team.

## 5.6 Localisation

* Currency is currently rendered in Pounds Sterling (£) and delivery locations are drawn from UK counties; any expansion to additional currencies/countries will require these to become configurable rather than fixed lists.

## 5.7 Compatibility

* The console shall continue to support current major desktop browsers (Chrome verified during this review); mobile-browser support for the admin console itself was not assessed and should be scoped separately from the customer-facing mobile app.

# 6. Business Rules

The following rules were inferred from observed field constraints, workflow states, and configuration screens. They should be validated with the business owner, since a rule inferred from a form is not always the complete rule the business intends.

| **Rule ID** | **Business Rule** |
| --- | --- |
| BR-01 | A customer account created via self-registration is not usable in an 'Active/verified' sense until an administrator manually verifies it via the Verify Users screen. |
| BR-02 | An order's payment mode is either Cash on Delivery or Bank; COD availability is controlled by a single platform-wide Yes/No switch, and by a configured pay-limit ceiling. |
| BR-03 | Every Product must belong to exactly one Category and one Sub-Category, and pricing must follow one of four defined models: Weight, Piece, Litre, or Serves. |
| BR-04 | A Product may be marked with unlimited stock, in which case its numeric stock quantity is not the binding constraint on orderability. |
| BR-05 | Delivery charges are determined by the customer's registered delivery Location, not by order value or weight — each Location carries its own flat delivery charge. |
| BR-06 | An Offer Code grants a discount as either a percentage or a flat amount, but the data model records both fields, implying only one is expected to be non-zero/active per code at a time. |
| BR-07 | Orders progress through a defined status sequence — observed values are COD/UNPAID/PAID (payment-oriented), OUT FOR DELIVERY, and DELIVERED (fulfilment-oriented) — and a Delivery Boy must be assigned before an order can meaningfully move through the delivery-oriented statuses. |
| BR-08 | Cash collected by a Delivery Boy against a COD order is tracked centrally in the expense ledger against that order, distinguishing cash held by the delivery boy from cash/bank already settled to the business. |
| BR-09 | Menu items (features) can be switched off platform-wide by setting their Menu Management status to Inactive without removing the underlying configuration — used today for the Purchased Packages / Manage Package features. |

# 7. Assumptions and Constraints

## 7.1 Assumptions

* The admin console reviewed is the same production system used to operate the live 7rmart Supermarket business, and the data observed (orders, users, products) is real operational data rather than a disconnected test copy — although the volume of obviously placeholder entries (see Section 8) suggests the environment also doubles as a staging/QA/demo system.
* The customer-facing storefront/app referenced throughout this document (sliders, push notifications, CMS pages, offer codes) exists and consumes the data maintained in this admin console, even though it was not directly reviewed.
* The three observed account types (admin, staff, db) map to a real, if currently implicit, permission model that the business intends to keep, rather than being an accidental artefact of the build.

## 7.2 Constraints

* This document is based solely on what is reachable and renderable through the admin console's user interface; no source code, database schema, or API contract was reviewed.
* Several navigation paths were not functionally verifiable because the underlying screen returned a server error during this review (see Section 8); requirements for those areas are therefore based on the menu label and, where available, related evidence (e.g. the expense ledger's references to orders/staff), and must be confirmed with the development team.
* The review was conducted against the URL and credentials supplied by the business ([REDACTED - demo credentials, see known-risks.md]) and reflects the state of the system on 24 August 2026; the system may change before requirements based on this document are actioned.
* No load testing, security testing, or accessibility testing was performed; all Non-Functional Requirements in Section 5 are advisory and should be independently verified.

# 8. Known Issues and Gaps Identified During Analysis

The table below lists every navigation entry that, at the time of this review, led to an unhandled application error (a CodeIgniter 'PageNotFoundException' and/or generic ErrorException) instead of a working screen. These are recorded as findings for the business and technical team to triage — each may be a genuine defect, a permissions/configuration issue specific to the reviewed account, or a module that is mid-development. They are called out here rather than omitted, because an accurate baseline must show what does not currently work, not only what does.

| **Menu Entry** | **Underlying Route** | **Observed Result** |
| --- | --- | --- |
| Create New Order | /admin/add-order | Unhandled server error (404/500 exception trace) |
| Report > Consolidated Report | /admin/list-report | Unhandled server error |
| Report > Order Report | /admin/list-order-report | Unhandled server error |
| Manage Expense > Create Merchant | /admin/list-merchant | Unhandled server error |
| Feedbacks | /admin/list-feedback | Unhandled server error |

Additional observations from the walkthrough that the business should be aware of when planning subsequent work:

* Test/placeholder data is pervasive in several modules — for example, product Categories include entries such as 'Test123', 'n qw', and randomly-suffixed names (e.g. 'Health1784619306525'), and the News module contains dozens of entries with titles like 'Hello I am test data'. If this is a shared staging/demo environment, a data-cleanup pass is recommended before this catalogue is treated as production-ready; if it is genuinely production, this represents a data-quality risk that should be remediated.
* The Manage Location list contains multiple exact duplicate entries (e.g. several identical 'Aberdeen / Sark / £150' rows), suggesting no uniqueness constraint currently prevents duplicate delivery-location records.
* The Admin Users list (1,146 records) is very large relative to the number of genuine staff a grocery operation would typically employ, and includes many auto-generated-looking usernames (e.g. 'haleigh.dach', 'janiya.rutherford') — this warrants a review of whether these are legitimate staff/delivery accounts or leftover test accounts before any access-control tightening is planned.
* Two navigation entries — 'Purchased Packages' and 'Manage Package' — exist in the Menu Management configuration but are marked Inactive, and were not otherwise reachable from the visible menu. This suggests a subscription/package-based feature was built, or partially built, but never launched; the business should confirm whether this is a deliberately shelved feature or one intended for a future release, so it can be either scoped into this BRD's future phase or formally retired.
* No dedicated screen for defining role permissions (as distinct from listing users by role) was found; access control appears to rely on the fixed 'Usertype' value alone.

# 9. Key Data Entities (Business Glossary)

The table below summarises the principal business entities maintained by the platform, to support a shared vocabulary between business and technical teams during subsequent design work.

| **Entity** | **Key Attributes Observed** | **Related Entities** |
| --- | --- | --- |
| Product | Title, product code, type, weight/price type, price, MRP, purchase price, stock, images, status, featured flag, combo-pack flag | Category, Sub-Category, Group |
| Category | Name, image, status, top/left menu flags | Group, Sub-Category, Product |
| Sub-Category | Name, image, status | Category, Product |
| Group | Name (Organic, Vegan, Gluten Free, Goodness) | Category, Product |
| Order | Order ID, order date, amount, payment mode, status, delivery date/time window, line items | Customer, Delivery Location, Delivery Boy, Product |
| Customer (App User) | Name, phone, e-mail, password, registration date, verification status, active status | Order, Delivery Location |
| Delivery Boy | Name, e-mail, phone, address, username, password, status | Order |
| Delivery Location | Location name, country, state/county, delivery charge, status | Order, Customer |
| Offer Code | Code/name, percentage, flat amount, image, status | Order |
| Admin User | Username, usertype (admin/staff/db), password, status | n/a |
| Expense / Ledger Entry | Title, date, credit bank, debit bank, credit cash, debit cash, cash with delivery boy | Order, Delivery Boy, Expense Category |
| CMS Page | Title, description, image, page slug | n/a |
| Payment Method | Title, pay limit, status | Order |
| Menu Item | Menu name, icon, linked table, display order, status, parent/child relationship | n/a |

# 10. Appendix — Admin Console Module Inventory

This appendix lists every navigation entry discovered in the admin console during this review, for direct traceability back to the functional requirements in Section 4.

| **#** | **Menu Path** | **Screen Purpose** | **Verified Working?** |
| --- | --- | --- | --- |
| 1 | Dashboard | Operational summary tiles with drill-through links | Yes |
| 2 | Manage Expense > Expense Category | Maintain expense categories (Salaries, Loan Amount, Fuel Expense) | Yes |
| 3 | Manage Expense > Manage Expense | Cash/bank ledger entries reconciling COD collections | Yes |
| 4 | Manage Expense > Create Merchant | Merchant/vendor onboarding for expenses | No — server error |
| 5 | Manage Orders | Order list, status change, delivery date, delivery-boy assignment, order detail/print | Yes |
| 6 | Create New Order | Manual order entry by staff | No — server error |
| 7 | Verify Users | Review/verify pending customer registrations | Yes |
| 8 | Report > Consolidated Report | Business-wide reporting | No — server error |
| 9 | Report > Order Report | Order-focused reporting | No — server error |
| 10 | Manage Content > Manage Pages | CMS pages (About Us, T&Cs, Privacy Policy, Refund Policy, etc.) | Yes |
| 11 | Manage Content > Manage Footer Text | Footer address/e-mail/phone | Yes |
| 12 | Manage Content > Manage Contact | Support contact + delivery time/charge threshold config | Yes |
| 13 | Manage Content > Manage News | Customer-facing news/announcements | Yes |
| 14 | Manage Product | Product catalogue list, create, edit, delete | Yes |
| 15 | Manage Users | Verified customer account list, block/unblock, delete | Yes |
| 16 | Manage Location | Delivery-location and per-location delivery-charge management | Yes |
| 17 | Push Notifications | Compose/send app push notifications | Yes |
| 18 | Manage Slider | Homepage banner sliders | Yes |
| 19 | Mobile Slider | App home-screen banner sliders | Yes |
| 20 | Manage Category > Category | Top-level catalogue categories | Yes |
| 21 | Manage Category > Sub Category | Catalogue sub-categories | Yes |
| 22 | Manage Groups | Merchandising tags (Organic, Vegan, Gluten Free, Goodness) | Yes |
| 23 | Manage Offer Code | Promotional discount codes | Yes |
| 24 | Manage COD | Global Cash-on-Delivery on/off switch | Yes |
| 25 | Manage Delivery Boy | Delivery-personnel directory | Yes |
| 26 | Manage Payment Methods | Accepted payment methods and pay limits | Yes |
| 27 | Feedbacks | Customer feedback review | No — server error |
| 28 | Admin Users | Admin/staff/delivery-boy console account directory | Yes |
| 29 | Settings > Change Password | Self-service password change for the logged-in admin | Yes |
| 30 | Settings > Manage Menu | Data-driven configuration of the console's own navigation menu | Yes |
| 31 | (Inactive) Purchased Packages | Not reachable from the visible menu; configured but disabled | Not applicable |
| 32 | (Inactive) Manage Package | Not reachable from the visible menu; configured but disabled | Not applicable |

# 11. Sign-Off

This document represents the current-state (as-is) understanding of the 7rmart Supermarket admin console as at 24 August 2026, compiled through direct system walkthrough. It is intended as a discussion baseline: sections 6 (Business Rules), 7 (Assumptions and Constraints), and 8 (Known Issues) in particular should be reviewed and corrected by business and technical stakeholders before this document is used to scope a build, since several statements in those sections are inferred from observed behaviour rather than confirmed by a system owner.

| **Reviewed By (Business)** |  |
| --- | --- |
| **Signature / Date** |  |
| **Reviewed By (Technical)** |  |
| **Signature / Date** |  |
