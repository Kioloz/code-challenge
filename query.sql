SELECT e.name,
         e.department,
         e.salary
FROM employee AS e
INNER JOIN 
    (SELECT department,
         max(salary) AS salary
    FROM employee
    GROUP BY  department) AS o
    ON e.department = o.department
        AND e.salary = o.salary
ORDER BY  department ASC