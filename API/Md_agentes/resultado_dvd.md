# Resultado de consulta — dvd
> Generado: 2026-06-21 14:15:55

## Solicitud
Dame el nombre de las primeras películas de la base de datos DVD por orden alfabético

## Query SQL ejecutada
```sql
SELECT title FROM film ORDER BY title ASC LIMIT 10;
```

## Datos obtenidos
1. Academy Dinosaur
2. Ace Goldfinger
3. Adaptation Holes
4. Affair Prejudice
5. African Egg
6. Agent Truman
7. Airplane Sierra
8. Airport Pollock
9. Alabama Devil
10. Aladdin Calendar

## Notas y observaciones
Se asume "primeras" como las 10 primeras películas ordenadas alfabéticamente (A-Z). Se puede ajustar el valor de LIMIT para mostrar más o menos resultados según necesidad.
