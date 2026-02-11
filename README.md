# Urbantrends dev Backend API's

## Introduction
welcome to the urbantrends development backend website. The following project handles different operations, for solving developer, business and client needs.
Also it's widely used to stage projects and make sure everything is on point before be shipped to production.

## Features

The following backend project contains API's, which are responsible for handling urbantrends logic tasks. The feature include:

- Users Authentication
- Display Services
- Display top Developers Projects
- Display Clients projects on developers portal
- Dashboard for clients to create their own data and decide which to share

## Url Structure for services

- Public (read-only):

```GET /api/services/ → list categories with services + tiers```

```GET /api/service-items/ → all services```

```GET /api/tiers/ → all tiers```

- User (authenticated):

``` GET /api/user/orders/ → list own orders```

```POST /api/user/orders/ → create order with multiple services/tier```

```GET/PUT/PATCH/DELETE /api/user/order-items/ → manage individual items (optional)```

- Admin (staff-only):

```GET/POST/PUT/PATCH/DELETE /api/admin/services/ → CRUD categories```

```GET/POST/PUT/PATCH/DELETE /api/admin/service-items/ → CRUD services```

```GET/POST/PUT/PATCH/DELETE /api/admin/tiers/ → CRUD tiers```

```GET /api/admin/orders/ → view all orders```


