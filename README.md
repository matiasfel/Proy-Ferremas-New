# 🛠️ Ferremas - Sistema de Gestión y E-commerce

**Ferremas** es una plataforma desarrollada con **Django** que combina un sistema de ventas online con un completo panel administrativo.  
La aplicación permite a los clientes comprar productos, y a los administradores gestionar pedidos, productos, usuarios, marcas, categorías y mensajes de contacto.

> 🧑‍💻 Este proyecto fue realizado de forma individual por mi, [@matiasfel](https://github.com/matiasfel) como trabajo universitario.

---
### 🛍️ Sitio público (Landing)
- Visualización de productos por categoría y marca.
- Filtro de productos, precios y búsqueda.
- Carrito de compras persistente para usuarios autenticados y anónimos.
- Sistema de checkout con Webpay Plus (Transbank).
- Página de contacto con almacenamiento de mensajes.

### 🔐 Autenticación
- Registro e inicio de sesión personalizados.
- Roles de usuario con permisos diferenciados:
  - `CLIENTE`
  - `VENDEDOR`
  - `BODEGUERO`
  - `CONTADOR`
  - `ADMINISTRADOR`

### 🖥️ Panel de administración (admin_panel)
- Dashboard con resumen general.
- Gestión CRUD de:
  - Productos
  - Categorías
  - Marcas
  - Usuarios (con roles, estado y staff)
- Vista de pedidos y detalle por orden.
- Visualización de mensajes de contacto (no editable).
- Módulo de configuración (placeholder "Próximamente").

## ⚙️ Tecnologías usadas

- 🐍 Python 3.13
- 🌐 Django 5.x
- 💳 Webpay Plus (Transbank SDK)
- 🧠 SQLite (en desarrollo)
- 🎨 Bootstrap 5 + Tailwind CSS para estilos
- 🧪 Django Messages, Humanize, Widget Tweaks

---

## 🚀 Instalación

- **Clona el repositorio**

```bash
git clone https://github.com/matiasfel/Proy-Ferremas-New.git
```

- **Crea y activa un entorno virtual**

```bash
python3 -m venv venv
MacOS: source venv/bin/activate
Windows: cd venv/scripts/.activate
```

- **Instala dependecias que estan en instructions.txt**

- **Aplica las migraciones**

```bash
python manage.py migrate
```

- **Crea un super usuario**

```bash
python manage.py createsuperuser
```

- **Ejecuta el servidor**

```bash
python manage.py runserver**
```

## 👥 Usuarios y Roles

La aplicación utiliza un modelo de usuario personalizado (`CustomUser`) que hereda de `AbstractUser` y permite la asignación de diferentes roles con permisos específicos. Los roles disponibles son:

- `ADMINISTRADOR`
- `VENDEDOR`
- `BODEGUERO`
- `CONTADOR`
- `CLIENTE` (por defecto)

Cada usuario puede tener además:

- Nombre de usuario
- Email
- Teléfono
- Dirección
- Estado de actividad (`is_active`)
- Permiso de acceso al panel (`is_staff`)

## 🛡️ Acceso al Panel Administrativo

Solo los usuarios con roles **ADMINISTRADOR**, **VENDEDOR**, **BODEGUERO** o **CONTADOR** tienen acceso al panel administrativo.

La app redirige automáticamente al usuario al panel o a la página principal según su rol **solo una vez al ingresar**.

```python
# En la vista `landing/index`
if user.role in ['ADMINISTRADOR', 'VENDEDOR', 'BODEGUERO', 'CONTADOR']:
    return redirect('admin_panel:dashboard')