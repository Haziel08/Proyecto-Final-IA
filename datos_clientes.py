# --- BASE DE DATOS DE 100 PERSONAS PROPORCIONADA ---
datos_clientes = {
    "ID_Cliente": [f"CLI-{str(i).zfill(3)}" for i in range(1, 101)],
    "Nombre": [
        "Carlos García", "Ana Martínez", "Luis López", "María González", "Jorge Rodríguez", 
        "Sofía Pérez", "Pedro Sánchez", "Lucía Ramírez", "Miguel Flores", "Elena Gómez",
        "Alejandro Díaz", "Gabriela Cruz", "Roberto Hernández", "Fernanda Álvarez", "Ricardo Ruiz",
        "Daniela Vázquez", "Javier Castillo", "Camila Jiménez", "Manuel Moreno", "Beatriz Ortiz",
        "Carlos Martínez", "Ana López", "Luis González", "María Rodríguez", "Jorge Pérez",
        "Sofía Sánchez", "Pedro Ramírez", "Lucía Flores", "Miguel Gómez", "Elena Díaz",
        "Alejandro Cruz", "Gabriela Hernández", "Roberto Álvarez", "Fernanda Ruiz", "Ricardo Vázquez",
        "Daniela Castillo", "Javier Jiménez", "Camila Moreno", "Manuel Ortiz", "Beatriz García",
        "Arturo Mendoza", "Diana Herrera", "Hugo Castro", "Valeria Rios", "Oscar Arce",
        "Paulina Meza", "Héctor Lara", "Silvia Soto", "Eduardo Luna", "Adriana Vera",
        "Sergio Romero", "Tania Navarro", "Omar Delgado", "Natalia Vega", "Andrés ESP",
        "Claudia Ruiz", "Fernando Mora", "Patricia Rojas", "Raúl Solís", "Monica Luna",
        "Enrique Nava", "Lorena Soto", "Gustavo peña", "Irene Ortiz", "Felipe Guerra",
        "Karla Bravo", "Alfonso Rocha", "Natalia Valdés", "Salvador Trejo", "Guadalupe Mora",
        "César Franco", "Estela Durán", "Mario Rangel", "Rosa Montes", "Francisco Leyva",
        "Angelicá Benítez", "Rubén Nieto", "Miriam Cordero", "Alfredo Solares", "Blanca Pardo",
        "Guillermo Marín", "Josefina Rosas", "Jaime Becerril", "Lourdes Alanís", "Armando Olvera",
        "Yolanda Orozco", "Rodolfo Tejeda", "Leticia Briseño", "Ramón Lugo", "Verónica Galván",
        "Abelardo Chapa", "Sonia Covarrubias", "Ignacio Tovar", "Martha Casillas", "Agustín Barrera",
        "Elsa Palacios", "Adolfo Cedillo", "Alicia Villalobos", "Benjamín Godínez", "Consuelo Macías"
    ],
    "Ingreso_Mensual": [
        85000, 11200, 29500, 45000, 95000, 14000, 22000, 55000, 10500, 38000,
        72000, 16500, 31000, 52000, 12000, 26000, 48000, 115000, 13500, 34000,
        90000, 9500, 27000, 41000, 110000, 15000, 24000, 58000, 12000, 39000,
        68000, 16000, 33000, 49000, 13000, 28000, 50000, 125000, 14000, 36000,
        55000, 18500, 42000, 60000, 11000, 23000, 75000, 13000, 32000, 47000,
        88000, 15500, 29000, 51000, 12500, 27000, 53000, 118000, 14500, 35000,
        64000, 17000, 40000, 62000, 9000, 21000, 79000, 13800, 30000, 46000,
        92000, 16200, 28500, 54000, 11800, 25500, 49500, 130000, 15000, 37500,
        71000, 19000, 43500, 61000, 10000, 22500, 77000, 14200, 31500, 48500,
        86000, 14800, 29800, 50500, 12200, 26500, 52500, 122000, 13900, 34500
    ],
    "Buro_Credito_Score": [
        795, 510, 665, 0, 810, 490, 620, 760, 530, 680,
        780, 540, 640, 0, 520, 610, 750, 830, 500, 690,
        805, 480, 630, 590, 820, 515, 605, 775, 545, 675,
        790, 535, 655, 0, 495, 615, 740, 840, 525, 660,
        0, 575, 695, 765, 510, 645, 800, 550, 625, 715,
        815, 560, 635, 730, 505, 600, 755, 825, 535, 685,
        770, 585, 700, 745, 470, 615, 790, 540, 650, 710,
        825, 550, 620, 725, 515, 595, 765, 835, 520, 670,
        760, 590, 705, 750, 490, 610, 795, 545, 645, 720,
        810, 565, 615, 735, 530, 605, 745, 845, 510, 680
    ],
    "Factor_Certeza_CF": [
        96.4, 94.1, 93.8, 51.2, 98.1, 91.5, 92.0, 95.7, 89.4, 94.2,
        97.3, 90.1, 91.8, 48.5, 93.0, 92.4, 96.0, 98.5, 90.2, 93.1,
        97.0, 92.3, 91.5, 93.4, 99.0, 88.7, 90.6, 96.2, 91.1, 92.8,
        96.6, 89.9, 93.5, 53.0, 90.5, 91.2, 94.8, 97.9, 89.0, 92.1,
        47.9, 91.3, 94.0, 96.8, 88.5, 92.7, 97.5, 90.4, 91.9, 94.6,
        98.2, 91.0, 92.2, 95.1, 87.6, 93.3, 95.9, 98.7, 89.3, 93.7,
        96.1, 92.5, 94.4, 95.4, 86.9, 91.4, 97.2, 90.8, 92.9, 94.1,
        98.4, 89.7, 91.6, 94.9, 88.1, 92.0, 96.3, 98.9, 90.3, 93.2,
        95.8, 93.0, 94.7, 95.3, 87.2, 91.7, 97.6, 91.2, 92.6, 94.5,
        97.8, 90.5, 91.1, 95.0, 89.6, 92.4, 95.6, 98.3, 88.9, 93.9
    ],
    "Dictamen_Final": [
        "Aprobado", "Rechazado", "Sujeto a Aval", "Rechazado", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval",
        "Aprobado", "Rechazado", "Sujeto a Aval", "Rechazado", "Rechazado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval",
        "Aprobado", "Rechazado", "Sujeto a Aval", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval",
        "Aprobado", "Rechazado", "Sujeto a Aval", "Rechazado", "Rechazado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval",
        "Rechazado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado",
        "Aprobado", "Sujeto a Aval", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval",
        "Aprobado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado",
        "Aprobado", "Sujeto a Aval", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval",
        "Aprobado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado",
        "Aprobado", "Sujeto a Aval", "Sujeto a Aval", "Aprobado", "Rechazado", "Sujeto a Aval", "Aprobado", "Aprobado", "Rechazado", "Sujeto a Aval"
    ]
}