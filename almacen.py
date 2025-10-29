"""
Aplicación de escritorio (único archivo) para registro de productos e inventario
para un taller mecánico usando customtkinter y sqlite3.

Caracteristicas principales:
- Control estricto de Entradas y Salidas por vehículo y por técnico
- Base de datos de proveedores con historial de precios
- Inventario que permite dar fechas de entrega basadas en stock y lead time

Requisitos: pip install customtkinter
Ejecutar: python registro_taller.py
"""

import customtkinter as ctk
import sqlite3
from datetime import datetime, timedelta
import os
import threading

DB_FILE = "taller.db"

# ---------------------- Base de datos ----------------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Productos
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            unit TEXT,
            min_stock INTEGER DEFAULT 0,
            lead_time_days INTEGER DEFAULT 7,
            note TEXT
        )
    ''')

    # Proveedores
    c.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            lead_time_days INTEGER DEFAULT 7,
            note TEXT
        )
    ''')

    # Historial de precios de proveedor
    c.execute('''
        CREATE TABLE IF NOT EXISTS supplier_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER,
            product_id INTEGER,
            price REAL,
            currency TEXT DEFAULT 'BOB',
            date TEXT,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')

    # Vehiculos
    c.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT UNIQUE,
            owner TEXT
        )
    ''')

    # Tecnicos
    c.execute('''
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            note TEXT
        )
    ''')

    # Movimientos de inventario (entradas y salidas)
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            qty INTEGER,
            movement_type TEXT CHECK(movement_type IN ('IN','OUT')),
            date TEXT,
            vehicle_id INTEGER,
            technician_id INTEGER,
            reference TEXT,
            note TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
            FOREIGN KEY(technician_id) REFERENCES technicians(id)
        )
    ''')

    conn.commit()
    conn.close()

# DB helper
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()

    def query(self, sql, params=(), commit=False):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            if commit:
                self.conn.commit()
                return cur.lastrowid
            return cur.fetchall()

    def close(self):
        self.conn.close()

# ---------------------- Lógica de inventario ----------------------

def get_stock(db: DB, product_id: int):
    rows = db.query(
        "SELECT SUM(CASE WHEN movement_type='IN' THEN qty WHEN movement_type='OUT' THEN -qty ELSE 0 END) as stock FROM inventory_movements WHERE product_id = ?",
        (product_id,)
    )
    val = rows[0][0]
    return int(val or 0)

def estimate_delivery_date(db: DB, product_id: int, needed_qty: int):
    """Estimación simple:
    - Si stock >= needed_qty -> entrega inmediata (hoy)
    - Si stock < needed_qty -> buscar proveedores y usar su lead_time_days (promedio)
      y devolver la fecha estimada hoy + lead_time
    """
    stock = get_stock(db, product_id)
    if stock >= needed_qty:
        return datetime.now().date(), stock

    # buscar proveedores que vendan el producto (supplier_prices)
    rows = db.query(
        "SELECT s.lead_time_days FROM supplier_prices sp JOIN suppliers s ON sp.supplier_id = s.id WHERE sp.product_id = ?",
        (product_id,)
    )
    lead_times = [r[0] for r in rows if r[0] is not None]
    if not lead_times:
        # fallback: use product lead_time
        prod = db.query("SELECT lead_time_days FROM products WHERE id = ?", (product_id,))
        if prod:
            lt = prod[0][0] or 7
        else:
            lt = 7
        return datetime.now().date() + timedelta(days=lt), stock

    avg_lt = sum(lead_times) / len(lead_times)
    return datetime.now().date() + timedelta(days=int(round(avg_lt))), stock

# ---------------------- Interfaz Grafica ----------------------

class TallerApp(ctk.CTk):
    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.title("Registro Taller - Inventario y Control")
        self.geometry("1000x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame principal con tabs
        self.notebook = ctk.CTkTabview(self, width=980, height=660)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.notebook.add("Productos")
        self.notebook.add("Movimientos")
        self.notebook.add("Proveedores")
        self.notebook.add("Inventario")
        self.notebook.add("Reportes")

        self.build_product_tab()
        self.build_movements_tab()
        self.build_suppliers_tab()
        self.build_inventory_tab()
        self.build_reports_tab()

        self.refresh_all()

    # ----------------- Productos -----------------
    def build_product_tab(self):
        tab = self.notebook.tab("Productos")
        # Left: form
        form = ctk.CTkFrame(tab)
        form.place(x=10, y=10)

        ctk.CTkLabel(form, text="Registrar / Editar Producto", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)

        self.p_code = ctk.CTkEntry(form, placeholder_text="Código")
        self.p_code.pack(pady=6, fill='x', padx=12)
        self.p_name = ctk.CTkEntry(form, placeholder_text="Nombre")
        self.p_name.pack(pady=6, fill='x', padx=12)
        self.p_unit = ctk.CTkEntry(form, placeholder_text="Unidad (ej: unidad, caja)")
        self.p_unit.pack(pady=6, fill='x', padx=12)
        self.p_min = ctk.CTkEntry(form, placeholder_text="Stock mínimo (int)")
        self.p_min.pack(pady=6, fill='x', padx=12)
        self.p_lead = ctk.CTkEntry(form, placeholder_text="Lead time por defecto (días)")
        self.p_lead.pack(pady=6, fill='x', padx=12)
        self.p_note = ctk.CTkTextbox(form, height=100)
        self.p_note.pack(pady=6, fill='both', padx=12)

        btn_frame = ctk.CTkFrame(form)
        btn_frame.pack(pady=8)
        ctk.CTkButton(btn_frame, text="Agregar Producto", command=self.add_product).grid(row=0, column=0, padx=8)
        ctk.CTkButton(btn_frame, text="Limpiar", command=self.clear_product_form).grid(row=0, column=1, padx=8)

        # Right: lista productos
        list_frame = ctk.CTkFrame(tab)
        form.place(x=10, y=10)
        ctk.CTkLabel(list_frame, text="Productos", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        self.products_list = ctk.CTkScrollableFrame(list_frame)
        self.products_list.pack(fill='both', expand=True, padx=8, pady=6)

    def add_product(self):
        code = self.p_code.get().strip()
        name = self.p_name.get().strip()
        unit = self.p_unit.get().strip()
        try:
            min_stock = int(self.p_min.get().strip() or 0)
        except ValueError:
            min_stock = 0
        try:
            lead_time = int(self.p_lead.get().strip() or 7)
        except ValueError:
            lead_time = 7
        note = self.p_note.get(1.0, 'end').strip()

        if not code or not name:
            ctk.CTkLabel(self, text="Código y nombre obligatorios", text_color="red").place(x=10, y=670)
            self.after(3000, lambda: self.destroy_error_label())
            return

        # insert
        try:
            self.db.query(
                "INSERT INTO products (code, name, unit, min_stock, lead_time_days, note) VALUES (?,?,?,?,?,?)",
                (code, name, unit, min_stock, lead_time, note),
                commit=True
            )
        except Exception as e:
            ctk.CTkLabel(self, text=f"Error: {e}", text_color="red").place(x=10, y=670)
            self.after(3000, lambda: self.destroy_error_label())
            return

        self.clear_product_form()
        self.refresh_products()

    def clear_product_form(self):
        self.p_code.delete(0, 'end')
        self.p_name.delete(0, 'end')
        self.p_unit.delete(0, 'end')
        self.p_min.delete(0, 'end')
        self.p_lead.delete(0, 'end')
        self.p_note.delete(1.0, 'end')

    def destroy_error_label(self):
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkLabel) and getattr(w, 'text_color', None) == 'red':
                w.destroy()

    def refresh_products(self):
        for widget in self.products_list.winfo_children():
            widget.destroy()
        rows = self.db.query("SELECT * FROM products ORDER BY name")
        for r in rows:
            pid = r[0]
            name = r[2]
            code = r[1]
            unit = r[3]
            frame = ctk.CTkFrame(self.products_list)
            frame.pack(fill='x', padx=6, pady=4)
            ctk.CTkLabel(frame, text=f"{code} — {name} ({unit})").grid(row=0, column=0, sticky='w')
            ctk.CTkButton(frame, text="Editar", width=70, command=lambda pid=pid: self.load_product_into_form(pid)).grid(row=0, column=1, padx=6)
            ctk.CTkButton(frame, text="Eliminar", width=70, command=lambda pid=pid: self.delete_product(pid)).grid(row=0, column=2, padx=6)
            stock = get_stock(self.db, pid)
            ctk.CTkLabel(frame, text=f"Stock: {stock}").grid(row=1, column=0, sticky='w', pady=4)

    def load_product_into_form(self, product_id):
        row = self.db.query("SELECT * FROM products WHERE id = ?", (product_id,))
        if not row:
            return
        r = row[0]
        self.p_code.delete(0,'end'); self.p_code.insert(0, r['code'])
        self.p_name.delete(0,'end'); self.p_name.insert(0, r['name'])
        self.p_unit.delete(0,'end'); self.p_unit.insert(0, r['unit'] or '')
        self.p_min.delete(0,'end'); self.p_min.insert(0, str(r['min_stock'] or '0'))
        self.p_lead.delete(0,'end'); self.p_lead.insert(0, str(r['lead_time_days'] or '7'))
        self.p_note.delete(1.0,'end'); self.p_note.insert('end', r['note'] or '')

    def delete_product(self, product_id):
        # simple delete (could be soft-delete in production)
        try:
            self.db.query("DELETE FROM products WHERE id = ?", (product_id,), commit=True)
        except Exception as e:
            print("Error deleting product:", e)
        self.refresh_products()

    # ----------------- Movimientos -----------------
    def build_movements_tab(self):
        tab = self.notebook.tab("Movimientos")
        frame = ctk.CTkFrame(tab)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        left = ctk.CTkFrame(frame)
        left.pack(side='left', fill='y', padx=8, pady=8)
        ctk.CTkLabel(left, text="Registrar Movimiento", font=ctk.CTkFont(size=16, weight='bold')).pack(pady=6)

        self.m_product = ctk.CTkComboBox(left, values=[], width=300)
        self.m_product.pack(pady=6)
        self.m_type = ctk.CTkComboBox(left, values=['IN','OUT'], width=300)
        self.m_type.set('IN')
        self.m_type.pack(pady=6)
        self.m_qty = ctk.CTkEntry(left, placeholder_text='Cantidad (int)')
        self.m_qty.pack(pady=6)
        self.m_vehicle = ctk.CTkComboBox(left, values=[], width=300)
        self.m_vehicle.pack(pady=6)
        self.m_technician = ctk.CTkComboBox(left, values=[], width=300)
        self.m_technician.pack(pady=6)
        self.m_ref = ctk.CTkEntry(left, placeholder_text='Referencia (opcional)')
        self.m_ref.pack(pady=6)
        self.m_note = ctk.CTkTextbox(left, height=120)
        self.m_note.pack(pady=6)
        ctk.CTkButton(left, text='Registrar', command=self.add_movement).pack(pady=8)

        right = ctk.CTkFrame(frame)
        right.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        ctk.CTkLabel(right, text='Últimos Movimientos', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=6)
        self.movements_list = ctk.CTkScrollableFrame(right)
        self.movements_list.pack(fill='both', expand=True)

        # Short forms to add vehicles/technicians
        bottom = ctk.CTkFrame(frame)
        bottom.pack(side='bottom', fill='x', padx=10, pady=10)
        ctk.CTkLabel(bottom, text='Agregar vehículo / técnico (rápido)').pack(side='left', padx=8)
        self.quick_plate = ctk.CTkEntry(bottom, placeholder_text='Placa')
        self.quick_plate.pack(side='left', padx=4)
        self.quick_owner = ctk.CTkEntry(bottom, placeholder_text='Propietario')
        self.quick_owner.pack(side='left', padx=4)
        ctk.CTkButton(bottom, text='Agregar vehículo', command=self.add_vehicle_quick).pack(side='left', padx=4)

        self.quick_tech = ctk.CTkEntry(bottom, placeholder_text='Nombre técnico')
        self.quick_tech.pack(side='left', padx=8)
        ctk.CTkButton(bottom, text='Agregar técnico', command=self.add_technician_quick).pack(side='left', padx=4)

    def add_movement(self):
        prod_display = self.m_product.get()
        if not prod_display:
            return
        try:
            product_id = int(prod_display.split('|')[0])
        except Exception:
            # fallback: try mapping by code
            rows = self.db.query("SELECT id FROM products WHERE name = ?", (prod_display,))
            if not rows:
                return
            product_id = rows[0]['id']

        mtype = self.m_type.get()
        try:
            qty = int(self.m_qty.get().strip())
        except Exception:
            return
        vehicle_id = None
        if self.m_vehicle.get():
            try:
                vehicle_id = int(self.m_vehicle.get().split('|')[0])
            except Exception:
                vehicle_id = None
        tech_id = None
        if self.m_technician.get():
            try:
                tech_id = int(self.m_technician.get().split('|')[0])
            except Exception:
                tech_id = None
        ref = self.m_ref.get().strip()
        note = self.m_note.get(1.0, 'end').strip()

        # register movement
        self.db.query(
            "INSERT INTO inventory_movements (product_id, qty, movement_type, date, vehicle_id, technician_id, reference, note) VALUES (?,?,?,?,?,?,?,?)",
            (product_id, qty, mtype, datetime.now().isoformat(), vehicle_id, tech_id, ref, note),
            commit=True
        )

        # Refresh UI
        self.refresh_movements()
        self.refresh_products()
        self.refresh_inventory()

    def refresh_movements(self):
        for w in self.movements_list.winfo_children():
            w.destroy()
        rows = self.db.query("SELECT im.*, p.name as product, v.plate as plate, t.name as tech FROM inventory_movements im LEFT JOIN products p ON im.product_id=p.id LEFT JOIN vehicles v ON im.vehicle_id=v.id LEFT JOIN technicians t ON im.technician_id=t.id ORDER BY im.date DESC LIMIT 200")
        for r in rows:
            frame = ctk.CTkFrame(self.movements_list)
            frame.pack(fill='x', padx=6, pady=4)
            dt = r['date'][:19].replace('T',' ')
            ctk.CTkLabel(frame, text=f"[{dt}] {r['movement_type']} {r['qty']} x {r['product']} | Veh: {r['plate'] or '-'} | Tec: {r['tech'] or '-'}").pack(anchor='w')
            if r['reference']:
                ctk.CTkLabel(frame, text=f"Ref: {r['reference']} | Nota: {r['note'] or '-'}", font=ctk.CTkFont(size=12)).pack(anchor='w')

    def add_vehicle_quick(self):
        plate = self.quick_plate.get().strip()
        owner = self.quick_owner.get().strip()
        if not plate:
            return
        try:
            self.db.query("INSERT INTO vehicles (plate, owner) VALUES (?,?)", (plate, owner), commit=True)
        except Exception:
            pass
        self.quick_plate.delete(0,'end'); self.quick_owner.delete(0,'end')
        self.refresh_movements()
        self.refresh_movements_dropdowns()

    def add_technician_quick(self):
        name = self.quick_tech.get().strip()
        if not name:
            return
        try:
            self.db.query("INSERT INTO technicians (name) VALUES (?)", (name,), commit=True)
        except Exception:
            pass
        self.quick_tech.delete(0,'end')
        self.refresh_movements_dropdowns()

    # ----------------- Proveedores -----------------
    def build_suppliers_tab(self):
        tab = self.notebook.tab("Proveedores")
        left = ctk.CTkFrame(tab)
        left.place(x=10, y=10)
        ctk.CTkLabel(left, text='Registrar Proveedor', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=8)
        self.s_name = ctk.CTkEntry(left, placeholder_text='Nombre proveedor')
        self.s_name.pack(pady=6, fill='x', padx=12)
        self.s_contact = ctk.CTkEntry(left, placeholder_text='Contacto (tel/email)')
        self.s_contact.pack(pady=6, fill='x', padx=12)
        self.s_lead = ctk.CTkEntry(left, placeholder_text='Lead time (días)')
        self.s_lead.pack(pady=6, fill='x', padx=12)
        self.s_note = ctk.CTkTextbox(left, height=120)
        self.s_note.pack(pady=6, fill='both', padx=12)
        ctk.CTkButton(left, text='Agregar proveedor', command=self.add_supplier).pack(pady=8)

        # Right: proveedores y registrar precio
        right = ctk.CTkFrame(tab)
        right.place(x=480, y=10)
        ctk.CTkLabel(right, text='Proveedores y Precios', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=8)
        self.suppliers_list = ctk.CTkScrollableFrame(right)
        self.suppliers_list.pack(fill='both', expand=True, padx=8, pady=6)

        # Subform registrar precio
        self.sp_product = ctk.CTkComboBox(right, values=[], width=300)
        self.sp_product.pack(pady=6)
        self.sp_supplier = ctk.CTkComboBox(right, values=[], width=300)
        self.sp_supplier.pack(pady=6)
        self.sp_price = ctk.CTkEntry(right, placeholder_text='Precio')
        self.sp_price.pack(pady=6)
        ctk.CTkButton(right, text='Registrar precio (histórico)', command=self.add_supplier_price).pack(pady=6)

    def add_supplier(self):
        name = self.s_name.get().strip()
        contact = self.s_contact.get().strip()
        try:
            lead = int(self.s_lead.get().strip() or 7)
        except Exception:
            lead = 7
        note = self.s_note.get(1.0, 'end').strip()
        if not name:
            return
        try:
            self.db.query("INSERT INTO suppliers (name, contact, lead_time_days, note) VALUES (?,?,?,?)", (name, contact, lead, note), commit=True)
        except Exception:
            pass
        self.s_name.delete(0,'end'); self.s_contact.delete(0,'end'); self.s_lead.delete(0,'end'); self.s_note.delete(1.0,'end')
        self.refresh_suppliers()
        self.refresh_movements_dropdowns()

    def add_supplier_price(self):
        prod = self.sp_product.get()
        supp = self.sp_supplier.get()
        try:
            prod_id = int(prod.split('|')[0])
            supp_id = int(supp.split('|')[0])
            price = float(self.sp_price.get().strip())
        except Exception:
            return
        self.db.query("INSERT INTO supplier_prices (supplier_id, product_id, price, date) VALUES (?,?,?,?)", (supp_id, prod_id, price, datetime.now().isoformat()), commit=True)
        self.sp_price.delete(0,'end')
        self.refresh_suppliers()

    def refresh_suppliers(self):
        for w in self.suppliers_list.winfo_children():
            w.destroy()
        rows = self.db.query("SELECT * FROM suppliers ORDER BY name")
        for r in rows:
            sid = r['id']
            frame = ctk.CTkFrame(self.suppliers_list)
            frame.pack(fill='x', padx=6, pady=4)
            ctk.CTkLabel(frame, text=f"{r['name']} (lead {r['lead_time_days']} días)").grid(row=0, column=0, sticky='w')
            prices = self.db.query("SELECT sp.price, sp.date, p.name FROM supplier_prices sp JOIN products p ON sp.product_id=p.id WHERE sp.supplier_id=? ORDER BY sp.date DESC LIMIT 5", (sid,))
            for p in prices:
                ctk.CTkLabel(frame, text=f"{p['name']}: {p['price']} @ {p['date'][:10]}").grid(row=1, column=0, sticky='w')

    # ----------------- Inventario -----------------
    def build_inventory_tab(self):
        tab = self.notebook.tab('Inventario')
        ctk.CTkLabel(tab, text='Inventario Global', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=8)
        self.inventory_list = ctk.CTkScrollableFrame(tab)
        self.inventory_list.pack(fill='both', expand=True, padx=8, pady=8)

        bottom = ctk.CTkFrame(tab)
        bottom.pack(fill='x', padx=8, pady=8)
        ctk.CTkLabel(bottom, text='Simular entrega: elige producto y cantidad para estimar fecha').pack(anchor='w')
        self.inv_product = ctk.CTkComboBox(bottom, values=[], width=300)
        self.inv_product.pack(side='left', padx=6)
        self.inv_qty = ctk.CTkEntry(bottom, placeholder_text='Cantidad')
        self.inv_qty.pack(side='left', padx=6)
        ctk.CTkButton(bottom, text='Estimar fecha', command=self.estimate_date_ui).pack(side='left', padx=6)
        self.estimate_label = ctk.CTkLabel(bottom, text='')
        self.estimate_label.pack(side='left', padx=12)

    def refresh_inventory(self):
        for w in self.inventory_list.winfo_children():
            w.destroy()
        rows = self.db.query("SELECT * FROM products ORDER BY name")
        for r in rows:
            pid = r['id']
            name = r['name']
            unit = r['unit']
            stock = get_stock(self.db, pid)
            frame = ctk.CTkFrame(self.inventory_list)
            frame.pack(fill='x', padx=6, pady=4)
            txt = f"{name} ({unit}) — Stock: {stock} — Min: {r['min_stock'] or 0} — Lead default: {r['lead_time_days'] or 7}d"
            ctk.CTkLabel(frame, text=txt).pack(anchor='w')

    def estimate_date_ui(self):
        prod = self.inv_product.get()
        if not prod:
            return
        try:
            prod_id = int(prod.split('|')[0])
            qty = int(self.inv_qty.get().strip())
        except Exception:
            return
        date, stock = estimate_delivery_date(self.db, prod_id, qty)
        if stock >= qty:
            self.estimate_label.configure(text=f"En stock ({stock}) — entrega inmediata")
        else:
            self.estimate_label.configure(text=f"Stock actual {stock}. Fecha estimada llegada: {date}")

    # ----------------- Reportes -----------------
    def build_reports_tab(self):
        tab = self.notebook.tab('Reportes')
        ctk.CTkLabel(tab, text='Reportes básicos', font=ctk.CTkFont(size=16, weight='bold')).pack(pady=8)
        btns = ctk.CTkFrame(tab)
        btns.pack(pady=6)
        ctk.CTkButton(btns, text='Movimientos recientes', command=self.report_movements).grid(row=0, column=0, padx=8)
        ctk.CTkButton(btns, text='Productos por debajo de mínimo', command=self.report_low_stock).grid(row=0, column=1, padx=8)
        self.report_area = ctk.CTkTextbox(tab, height=400)
        self.report_area.pack(fill='both', expand=True, padx=8, pady=8)

    def report_movements(self):
        rows = self.db.query("SELECT im.*, p.name as product FROM inventory_movements im JOIN products p ON im.product_id=p.id ORDER BY im.date DESC LIMIT 500")
        self.report_area.delete(1.0, 'end')
        for r in rows:
            dt = r['date'][:19].replace('T',' ')
            self.report_area.insert('end', f"[{dt}] {r['movement_type']} {r['qty']} x {r['product']} | Ref: {r['reference'] or '-'}\n")

    def report_low_stock(self):
        rows = self.db.query("SELECT * FROM products")
        self.report_area.delete(1.0, 'end')
        for r in rows:
            pid = r['id']
            stock = get_stock(self.db, pid)
            if stock <= (r['min_stock'] or 0):
                self.report_area.insert('end', f"{r['code']} - {r['name']} : stock={stock} min={r['min_stock']}\n")

    # ----------------- Refresh helpers -----------------
    def refresh_movements_dropdowns(self):
        prods = []
        for r in self.db.query("SELECT id, code, name FROM products ORDER BY name"):
            prods.append(f"{r['id']}|{r['code']} - {r['name']}")
        self.m_product.configure(values=prods)
        self.sp_product.configure(values=prods)
        self.inv_product.configure(values=prods)

        vehicles = [f"{r['id']}|{r['plate']}" for r in self.db.query("SELECT id, plate FROM vehicles ORDER BY plate")]
        self.m_vehicle.configure(values=vehicles)

        techs = [f"{r['id']}|{r['name']}" for r in self.db.query("SELECT id, name FROM technicians ORDER BY name")]
        self.m_technician.configure(values=techs)

        suppliers = [f"{r['id']}|{r['name']}" for r in self.db.query("SELECT id, name FROM suppliers ORDER BY name")]
        self.sp_supplier.configure(values=suppliers)
        self.sp_supplier.set('')

    def refresh_all(self):
        self.refresh_products()
        self.refresh_movements()
        self.refresh_suppliers()
        self.refresh_inventory()
        self.refresh_movements_dropdowns()

# ---------------------- Inicio ----------------------

def main():
    if not os.path.exists(DB_FILE):
        init_db()
    db = DB()
    app = TallerApp(db)
    app.mainloop()
    db.close()

if __name__ == '__main__':
    main()
