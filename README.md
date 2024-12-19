## Setup Instructions

1. Clone the repository:

2. Create and activate a virtual environment:

3. Install dependencies:
pip install -r req.txt

4. Run migrations:
python manage.py migrate



### 1. Complete the Purchase Order Views (30%)
In `purchase/views.py`, implement the following:

a) **PurchaseOrderListView**
- Add filtering by status, date range, and supplier
- Implement search functionality
- Add sorting options

b) **PurchaseOrderCreateView**
- Implement form handling for PO and PO lines (hint: use formsets)
- Add validation for:
  - Supplier active status
  - Product availability
  - Valid quantities

c) **PurchaseOrderUpdateView**
- Implement status transition logic
- Add validation rules for each status change
- Prevent modifications of completed orders

### 2. Enhance API Endpoints (30%)
In `purchase/apis.py`, implement the following ViewSet methods:

a) **SupplierViewSet**
- Complete the `destroy` method with proper validation
- Add a custom action to display supplier purchase history
- Implement filtering and search

b) **ProductViewSet**
- Add custom actions for:
  - Stock level updates
  - Low stock alerts
  - Price history

c) **PurchaseOrderViewSet**
- Complete the `change_status` action with:
  - Status transition validation
  - Stock updates on completion
  - Email notifications
- Add filtering by date range and status

### 3. Add Business Logic (25%)
In `purchase/models.py`, enhance the models with:

a) **PurchaseOrder Model**
- Add methods for:
  - Status transition validation
  - Total amount calculation
  - Order completion checks

b) **Product Model**
- Add methods for:
  - Stock level management
  - Low stock validation
  - Price history tracking

### 4. Write Tests (15%)
Create tests in `purchase/tests.py` for:
- Model methods
- API endpoints
- View functionality
- Business logic validation

## Requirements

- All code must follow PEP 8 guidelines
- Include docstrings for all methods
- Implement proper error handling
- Add appropriate logging
- Write unit tests for new functionality

## Bonus Points (10%)

- Implement caching for frequently accessed data
- Add async tasks for email notifications
- Create custom management commands
- Add API documentation using drf-spectacular or similar
- Implement real-time updates using WebSockets

## Submission Guidelines

1. Create a new branch:



git checkout -b assessment/<your-name>
