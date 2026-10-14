# Resultado de consulta — Escuela
> Generado: 2026-06-22 18:20:35

## Solicitud
Obten los nombres de los alumnos asignados a las asignaturas y el nombre de los profesores que las imparten junto a su número de créditos

## Query SQL ejecutada
```sql
SELECT 
    pa.nombre AS nombre_alumno,
    a.nombre AS nombre_asignatura,
    a.creditos,
    pp.nombre AS nombre_profesor
FROM alumno_asignatura aa
INNER JOIN alumno al ON aa.idalumno = al.idalumno
INNER JOIN persona pa ON al.dni = pa.dni
INNER JOIN asignatura a ON aa.idasignatura = a.idasignatura
LEFT JOIN profesor p ON a.idprofesor = p.idprofesor
LEFT JOIN persona pp ON p.dni = pp.dni
ORDER BY pa.nombre, a.nombre
```

## Datos obtenidos
| nombre_alumno | nombre_asignatura | creditos | nombre_profesor |
|---------------|-------------------|----------|----------------|
| Laura         | Contabilidad      | 6        | null           |
| Manoli        | Analisis II       | 9        | Jorge          |
| Maria         | Analisis II       | 9        | Jorge          |
| Martina       | Quimica Fisica    | 4        | Maria          |
| Pepe          | Quimica Fisica    | 4        | Maria          |

## Notas y observaciones
Se utilizó LEFT JOIN para la relación con profesor porque la asignatura "Contabilidad" no tiene profesor asignado (idprofesor es NULL), por lo que se muestra NULL en nombre_profesor para Laura.
