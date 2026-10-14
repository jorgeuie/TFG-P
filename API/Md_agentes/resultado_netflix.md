# Resultado de consulta — netflix
> Generado: 2026-06-21 01:40:57

## Solicitud
Obten los nombres de los shows junto a su duración y su director

## Query SQL ejecutada
```sql
SELECT title, duration, director FROM netflix_shows;
```

## Datos obtenidos
Se obtuvieron 100+ registros de la tabla netflix_shows con las columnas title, duration y director. Los datos incluyen shows de Netflix con sus títulos, duraciones (en minutos o temporadas) y directores (algunos valores son NULL cuando no hay director registrado).

## Notas y observaciones
La consulta SELECT title, duration, director FROM netflix_shows devuelve todos los shows de Netflix con su nombre, duración y director. Algunos registros tienen NULL en la columna director cuando no se ha registrado un director para ese show. La duración se muestra en formato texto, indicando minutos (ej. '90 min') o temporadas (ej. '2 Seasons').
