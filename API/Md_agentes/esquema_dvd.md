# Esquema: dvd
> Generado: 2026-06-21 00:14:11  
> Tablas: 15  

---

## Tabla: `actor`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `actor_id` | INTEGER | Si |  | No |
| `first_name` | VARCHAR(45) |  |  | No |
| `last_name` | VARCHAR(45) |  |  | No |
| `last_update` | TIMESTAMP |  |  | No |

---

## Tabla: `store`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `store_id` | INTEGER | Si |  | No |
| `manager_staff_id` | SMALLINT |  | staff.staff_id | No |
| `address_id` | SMALLINT |  | address.address_id | No |
| `last_update` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `store.address_id` → `address.address_id`
- `store.manager_staff_id` → `staff.staff_id`

---

## Tabla: `address`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `address_id` | INTEGER | Si |  | No |
| `address` | VARCHAR(50) |  |  | No |
| `address2` | VARCHAR(50) |  |  | Sí |
| `district` | VARCHAR(20) |  |  | No |
| `city_id` | SMALLINT |  | city.city_id | No |
| `postal_code` | VARCHAR(10) |  |  | Sí |
| `phone` | VARCHAR(20) |  |  | No |
| `last_update` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `address.city_id` → `city.city_id`

---

## Tabla: `category`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `category_id` | INTEGER | Si |  | No |
| `name` | VARCHAR(25) |  |  | No |
| `last_update` | TIMESTAMP |  |  | No |

---

## Tabla: `city`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `city_id` | INTEGER | Si |  | No |
| `city` | VARCHAR(50) |  |  | No |
| `country_id` | SMALLINT |  | country.country_id | No |
| `last_update` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `city.country_id` → `country.country_id`

---

## Tabla: `country`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `country_id` | INTEGER | Si |  | No |
| `country` | VARCHAR(50) |  |  | No |
| `last_update` | TIMESTAMP |  |  | No |

---

## Tabla: `customer`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `customer_id` | INTEGER | Si |  | No |
| `store_id` | SMALLINT |  |  | No |
| `first_name` | VARCHAR(45) |  |  | No |
| `last_name` | VARCHAR(45) |  |  | No |
| `email` | VARCHAR(50) |  |  | Sí |
| `address_id` | SMALLINT |  | address.address_id | No |
| `activebool` | BOOLEAN |  |  | No |
| `create_date` | DATE |  |  | No |
| `last_update` | TIMESTAMP |  |  | Sí |
| `active` | INTEGER |  |  | Sí |

**Relaciones FK:**
- `customer.address_id` → `address.address_id`

---

## Tabla: `film_actor`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `actor_id` | SMALLINT | Si | actor.actor_id | No |
| `film_id` | SMALLINT | Si | film.film_id | No |
| `last_update` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `film_actor.actor_id` → `actor.actor_id`
- `film_actor.film_id` → `film.film_id`

---

## Tabla: `film_category`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `film_id` | SMALLINT | Si | film.film_id | No |
| `category_id` | SMALLINT | Si | category.category_id | No |
| `last_update` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `film_category.category_id` → `category.category_id`
- `film_category.film_id` → `film.film_id`

---

## Tabla: `inventory`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `inventory_id` | INTEGER | Si |  | No |
| `film_id` | SMALLINT |  | film.film_id | No |
| `store_id` | SMALLINT |  |  | No |
| `last_update` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `inventory.film_id` → `film.film_id`

---

## Tabla: `language`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `language_id` | INTEGER | Si |  | No |
| `name` | CHAR(20) |  |  | No |
| `last_update` | TIMESTAMP |  |  | No |

---

## Tabla: `rental`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `rental_id` | INTEGER | Si |  | No |
| `rental_date` | TIMESTAMP |  |  | No |
| `inventory_id` | INTEGER |  | inventory.inventory_id | No |
| `customer_id` | SMALLINT |  | customer.customer_id | No |
| `return_date` | TIMESTAMP |  |  | Sí |
| `staff_id` | SMALLINT |  | staff.staff_id | No |
| `last_update` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `rental.customer_id` → `customer.customer_id`
- `rental.inventory_id` → `inventory.inventory_id`
- `rental.staff_id` → `staff.staff_id`

---

## Tabla: `staff`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `staff_id` | INTEGER | Si |  | No |
| `first_name` | VARCHAR(45) |  |  | No |
| `last_name` | VARCHAR(45) |  |  | No |
| `address_id` | SMALLINT |  | address.address_id | No |
| `email` | VARCHAR(50) |  |  | Sí |
| `store_id` | SMALLINT |  |  | No |
| `active` | BOOLEAN |  |  | No |
| `username` | VARCHAR(16) |  |  | No |
| `password` | VARCHAR(40) |  |  | Sí |
| `last_update` | TIMESTAMP |  |  | No |
| `picture` | BYTEA |  |  | Sí |

**Relaciones FK:**
- `staff.address_id` → `address.address_id`

---

## Tabla: `payment`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `payment_id` | INTEGER | Si |  | No |
| `customer_id` | SMALLINT |  | customer.customer_id | No |
| `staff_id` | SMALLINT |  | staff.staff_id | No |
| `rental_id` | INTEGER |  | rental.rental_id | No |
| `amount` | NUMERIC(5, 2) |  |  | No |
| `payment_date` | TIMESTAMP |  |  | No |

**Relaciones FK:**
- `payment.customer_id` → `customer.customer_id`
- `payment.rental_id` → `rental.rental_id`
- `payment.staff_id` → `staff.staff_id`

---

## Tabla: `film`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `film_id` | INTEGER | Si |  | No |
| `title` | VARCHAR(255) |  |  | No |
| `description` | TEXT |  |  | Sí |
| `release_year` | DOMAIN |  |  | Sí |
| `language_id` | SMALLINT |  | language.language_id | No |
| `rental_duration` | SMALLINT |  |  | No |
| `rental_rate` | NUMERIC(4, 2) |  |  | No |
| `length` | SMALLINT |  |  | Sí |
| `replacement_cost` | NUMERIC(5, 2) |  |  | No |
| `rating` | VARCHAR(5) |  |  | Sí |
| `last_update` | TIMESTAMP |  |  | No |
| `special_features` | ARRAY |  |  | Sí |
| `fulltext` | TSVECTOR |  |  | No |

**Relaciones FK:**
- `film.language_id` → `language.language_id`

---

