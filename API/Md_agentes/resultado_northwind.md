# Resultado de consulta — northwind
> Generado: 2026-06-21 01:50:26

## Solicitud
Dame el nombre de los proveedores con los productos más vendidos de menor a mayor el mes de septiembre

## Query SQL ejecutada
```sql
SELECT 
    s.suppliername AS proveedor,
    SUM(od.quantity) AS cantidad_vendida
FROM 
    suppliers s
    INNER JOIN products p ON s.supplierid = p.supplierid
    INNER JOIN orderdetails od ON p.productid = od.productid
    INNER JOIN orders o ON od.orderid = o.orderid
WHERE 
    EXTRACT(MONTH FROM o.orderdate) = 9
GROUP BY 
    s.suppliername
ORDER BY 
    cantidad_vendida ASC;
```

## Datos obtenidos
[{"proveedor":"Ma Maison","cantidad_vendida":5},{"proveedor":"Nord-Ost-Fisch Handelsgesellschaft mbH","cantidad_vendida":10},{"proveedor":"Cooperativa de Quesos 'Las Cabras'","cantidad_vendida":12},{"proveedor":"Bigfoot Breweries","cantidad_vendida":14},{"proveedor":"Pasta Buttini s.r.l.","cantidad_vendida":24},{"proveedor":"Norske Meierier","cantidad_vendida":28},{"proveedor":"G'day, Mate","cantidad_vendida":30},{"proveedor":"Grandma Kelly's Homestead","cantidad_vendida":30},{"proveedor":"Karkki Oy","cantidad_vendida":30},{"proveedor":"Escargots Nouveaux","cantidad_vendida":30},{"proveedor":"Gai pâturage","cantidad_vendida":40},{"proveedor":"Svensk Sjöföda AB","cantidad_vendida":52},{"proveedor":"Specialty Biscuits, Ltd.","cantidad_vendida":53},{"proveedor":"New England Seafood Cannery","cantidad_vendida":60},{"proveedor":"Exotic Liquid","cantidad_vendida":60},{"proveedor":"Formaggi Fortini s.r.l.","cantidad_vendida":60},{"proveedor":"Leka Trading","cantidad_vendida":64},{"proveedor":"Plutzer Lebensmittelgroßmärkte AG","cantidad_vendida":67},{"proveedor":"New Orleans Cajun Delights","cantidad_vendida":80},{"proveedor":"Aux joyeux ecclésiastiques","cantidad_vendida":90},{"proveedor":"Forêts d'érables","cantidad_vendida":125},{"proveedor":"Pavlova, Ltd.","cantidad_vendida":160}]

## Notas y observaciones
Se consultaron las ventas del mes de septiembre (mes 9) de todos los años disponibles en la base de datos. Se utilizó INNER JOIN para asegurar que solo se incluyan proveedores con ventas reales. Los resultados están ordenados de menor a mayor según la cantidad total de productos vendidos. El proveedor con menos ventas fue "Ma Maison" con 5 unidades, y el más exitoso fue "Pavlova, Ltd." con 160 unidades.
