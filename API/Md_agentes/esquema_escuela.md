# Esquema: escuela
> Generado: 2026-06-21 01:42:33  
> Tablas: 7  

---

## Tabla: `persona`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `dni` | VARCHAR(15) | Si |  | No |
| `nombre` | VARCHAR(25) |  |  | No |
| `apellido` | VARCHAR(30) |  |  | No |
| `ciudad` | VARCHAR(25) |  |  | No |
| `direccioncalle` | VARCHAR(50) |  |  | No |
| `direccionum` | VARCHAR(5) |  |  | No |
| `telefono` | VARCHAR(15) |  |  | No |
| `fechanac` | DATE |  |  | No |
| `varon` | CHAR(1) |  |  | No |

---

## Tabla: `profesor`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `idprofesor` | VARCHAR(4) | Si |  | No |
| `dni` | VARCHAR(9) |  | persona.dni | No |
| `coddept` | VARCHAR(10) |  | departamento.iddept | Sí |

**Relaciones FK:**
- `profesor.coddept` → `departamento.iddept`
- `profesor.dni` → `persona.dni`

---

## Tabla: `departamento`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `iddept` | VARCHAR(10) | Si |  | No |
| `nombre` | VARCHAR(20) |  |  | Sí |
| `planta` | VARCHAR(6) |  |  | Sí |

---

## Tabla: `titulacion`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `idtitulacion` | VARCHAR(6) | Si |  | No |
| `nombre` | VARCHAR(20) |  |  | No |

---

## Tabla: `asignatura`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `idasignatura` | VARCHAR(6) | Si |  | No |
| `nombre` | VARCHAR(50) |  |  | No |
| `creditos` | NUMERIC |  |  | No |
| `cuatrimestre` | CHAR(1) |  |  | No |
| `costebasico` | NUMERIC |  |  | No |
| `idprofesor` | VARCHAR(4) |  | profesor.idprofesor | Sí |
| `idtitulacion` | VARCHAR(6) |  | titulacion.idtitulacion | Sí |
| `curso` | CHAR(1) |  |  | No |

**Relaciones FK:**
- `asignatura.idprofesor` → `profesor.idprofesor`
- `asignatura.idtitulacion` → `titulacion.idtitulacion`

---

## Tabla: `alumno`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `idalumno` | CHAR(7) | Si |  | No |
| `dni` | CHAR(9) |  | persona.dni | No |

**Relaciones FK:**
- `alumno.dni` → `persona.dni`

---

## Tabla: `alumno_asignatura`

| Columna | Tipo | PK | FK | Nulo |
|---------|------|----|----|------|
| `idalumno` | CHAR(7) | Si | alumno.idalumno | No |
| `idasignatura` | CHAR(6) | Si | asignatura.idasignatura | No |
| `numeromatricula` | NUMERIC |  |  | No |

**Relaciones FK:**
- `alumno_asignatura.idalumno` → `alumno.idalumno`
- `alumno_asignatura.idasignatura` → `asignatura.idasignatura`

---

