# Esquema: northwind
> Generado: 2026-06-21 01:20:07  
> Tablas: 8  

---

## Tabla: `categories`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `categoryid` | INTEGER | Si |  | No |
| `categoryname` | VARCHAR(25) |  |  | Sí |
| `description` | VARCHAR(255) |  |  | Sí |

---

## Tabla: `products`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `productid` | INTEGER | Si |  | No |
| `productname` | VARCHAR(50) |  |  | Sí |
| `supplierid` | INTEGER |  | suppliers.supplierid | Sí |
| `categoryid` | INTEGER |  | categories.categoryid | Sí |
| `unit` | VARCHAR(25) |  |  | Sí |
| `price` | NUMERIC |  |  | Sí |

**Relaciones FK:**
- `products.categoryid` → `categories.categoryid`
- `products.supplierid` → `suppliers.supplierid`

---

## Tabla: `suppliers`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `supplierid` | INTEGER | Si |  | No |
| `suppliername` | VARCHAR(50) |  |  | Sí |
| `contactname` | VARCHAR(50) |  |  | Sí |
| `address` | VARCHAR(50) |  |  | Sí |
| `city` | VARCHAR(20) |  |  | Sí |
| `postalcode` | VARCHAR(10) |  |  | Sí |
| `country` | VARCHAR(15) |  |  | Sí |
| `phone` | VARCHAR(15) |  |  | Sí |

---

## Tabla: `employees`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `employeeid` | INTEGER | Si |  | No |
| `lastname` | VARCHAR(15) |  |  | Sí |
| `firstname` | VARCHAR(15) |  |  | Sí |
| `birthdate` | TIMESTAMP |  |  | Sí |
| `photo` | VARCHAR(25) |  |  | Sí |
| `notes` | VARCHAR(1024) |  |  | Sí |

---

## Tabla: `orders`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `orderid` | INTEGER | Si |  | No |
| `customerid` | INTEGER |  | customers.customerid | Sí |
| `employeeid` | INTEGER |  | employees.employeeid | Sí |
| `orderdate` | TIMESTAMP |  |  | Sí |
| `shipperid` | INTEGER |  | shippers.shipperid | Sí |

**Relaciones FK:**
- `orders.customerid` → `customers.customerid`
- `orders.employeeid` → `employees.employeeid`
- `orders.shipperid` → `shippers.shipperid`

---

## Tabla: `customers`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `customerid` | INTEGER | Si |  | No |
| `customername` | VARCHAR(50) |  |  | Sí |
| `contactname` | VARCHAR(50) |  |  | Sí |
| `address` | VARCHAR(50) |  |  | Sí |
| `city` | VARCHAR(20) |  |  | Sí |
| `postalcode` | VARCHAR(10) |  |  | Sí |
| `country` | VARCHAR(15) |  |  | Sí |

---

## Tabla: `shippers`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `shipperid` | INTEGER | Si |  | No |
| `shippername` | VARCHAR(25) |  |  | Sí |
| `phone` | VARCHAR(15) |  |  | Sí |

---

## Tabla: `orderdetails`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `orderdetailid` | INTEGER | Si |  | No |
| `orderid` | INTEGER |  | orders.orderid | Sí |
| `productid` | INTEGER |  | products.productid | Sí |
| `quantity` | INTEGER |  |  | Sí |

**Relaciones FK:**
- `orderdetails.orderid` → `orders.orderid`
- `orderdetails.productid` → `products.productid`

---

