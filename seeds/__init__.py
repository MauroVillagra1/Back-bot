"""
Paquete de seeds para poblar la base de datos del Asistente UTN.

Orden de ejecución:
    seed_01_periodos_materias   → períodos académicos + catálogo de materias
    seed_02_usuarios_sistema    → cuentas de sistema (admin, jefes, etc.)
    seed_03_comisiones_1ano     → comisiones, cursadas y profesores de 1º año
    seed_04_alumnos_demo        → alumnos de prueba

Correr todo junto:
    python seeds/run_seeds.py
"""
