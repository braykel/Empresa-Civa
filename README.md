# 🚌 Sistema Logístico de Transporte Interprovincial

Sistema completo de gestión para empresas de transporte terrestre, desarrollado en Python con interfaz gráfica Tkinter. Permite administrar rutas, buses, choferes y asientos de manera eficiente.

---

## ✨ Características Principales

| Módulo | Funcionalidad |
|---|---|
| 🗺️ **Rutas** | Cálculo de ruta más corta con algoritmo de Dijkstra. Selección de origen y destino por lista desplegable. |
| 🚌 **Buses** | Registro, asignación y control de estado. Tipos de servicio: Económico y Premium. |
| 👨‍✈️ **Choferes** | Registro, asignación, control de descanso y liberación. Tipos de licencia: A1, A2, B1, B2. |
| 💺 **Asientos** | Visualización gráfica en cuadrícula, reserva, marcado de ocupado y liberación. Resumen automático. |
| 📊 **Reportes** | Conteo de recursos disponibles y operaciones realizadas. |
| 📜 **Historial** | Registro automático de todas las acciones con opción de borrar. |

---

## 🛠️ Requisitos

- **Python 3.8 o superior**
- Librería Pillow:
  ```bash
  pip install pillow