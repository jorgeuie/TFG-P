import json
import threading
import urllib.request
import urllib.error
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os


#  CONFIGURACIÓN

BASE_URL = "http://localhost:8000"

def _request(method: str, path: str, payload: dict | None = None) -> dict:
    url = BASE_URL + path
    data = json.dumps(payload).encode() if payload else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=520) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return {"error": json.loads(body).get("detail", body)}
        except Exception:
            return {"error": body}
    except urllib.error.URLError as e:
        return {"error": f"No se pudo conectar: {e.reason}"}


def _download(path: str, dest_path: str) -> str:
    url = BASE_URL + path
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content_type = resp.headers.get("Content-Type", "")
            content = resp.read()
            if "application/pdf" in content_type:
                with open(dest_path, "wb") as f:
                    f.write(content)
                return f"PDF guardado en: {dest_path}"
            else:
                return resp.read().decode()
    except urllib.error.HTTPError as e:
        return f"Error HTTP {e.code}: {e.read().decode()}"
    except urllib.error.URLError as e:
        return f"No se pudo conectar: {e.reason}"



#  ESTILOS  (ttk)

DARK_BG    = "#1a1a2e"
PANEL_BG   = "#16213e"
ACCENT     = "#0f3460"
HIGHLIGHT  = "#e94560"
TEXT_FG    = "#eaeaea"
MUTED      = "#8892a4"
INPUT_BG   = "#0d1b2a"
BTN_BG     = "#e94560"
BTN_FG     = "#ffffff"
SUCCESS    = "#4ecca3"
WARNING    = "#ffd460"

FONT_TITLE  = ("Consolas", 15, "bold")
FONT_LABEL  = ("Consolas", 10)
FONT_MONO   = ("Consolas", 10)
FONT_BTN    = ("Consolas", 10, "bold")


def apply_styles(root: tk.Tk):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TNotebook",           background=DARK_BG,  borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=PANEL_BG,   foreground=MUTED,
                    padding=[14, 6],       font=FONT_LABEL)
    style.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", TEXT_FG)])

    style.configure("TFrame",    background=DARK_BG)
    style.configure("TLabel",    background=DARK_BG, foreground=TEXT_FG, font=FONT_LABEL)
    style.configure("TEntry",    fieldbackground=INPUT_BG, foreground=TEXT_FG,
                    insertcolor=TEXT_FG,   font=FONT_MONO, borderwidth=1, relief="flat")
    style.configure("TButton",   background=BTN_BG, foreground=BTN_FG,
                    font=FONT_BTN,         borderwidth=0, padding=[10, 5])
    style.map("TButton",
              background=[("active", "#c73652"), ("pressed", "#a02a40")])
    style.configure("Success.TLabel", foreground=SUCCESS, background=DARK_BG, font=FONT_LABEL)
    style.configure("Warning.TLabel", foreground=WARNING, background=DARK_BG, font=FONT_LABEL)
    style.configure("Muted.TLabel",   foreground=MUTED,   background=DARK_BG, font=FONT_LABEL)

    style.configure("Card.TFrame",  background=PANEL_BG, relief="flat")
    style.configure("Card.TLabel",  background=PANEL_BG, foreground=TEXT_FG, font=FONT_LABEL)
    style.configure("Card.TEntry",  fieldbackground=INPUT_BG, foreground=TEXT_FG,
                    font=FONT_MONO, borderwidth=1)
    style.configure("Card.TButton", background=BTN_BG, foreground=BTN_FG,
                    font=FONT_BTN, borderwidth=0, padding=[10, 5])
    style.map("Card.TButton",
              background=[("active", "#c73652")])



#  WIDGET AUXILIAR: cuadro de resultado

def make_result_box(parent, height=10):
    box = scrolledtext.ScrolledText(
        parent, height=height, font=FONT_MONO,
        bg=INPUT_BG, fg=TEXT_FG, insertbackground=TEXT_FG,
        relief="flat", borderwidth=6, wrap="word",
        state="disabled"
    )
    return box


def set_result(box: scrolledtext.ScrolledText, text: str, color: str = TEXT_FG):
    box.config(state="normal")
    box.delete("1.0", "end")
    box.insert("end", text)
    box.config(fg=color, state="disabled")



#  Pestaña 1 – BASES DE DATOS

class TabBD(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook, style="TFrame")
        self._build()

    def _build(self):
        # ── Título
        ttk.Label(self, text="⬡  Gestión de Bases de Datos", font=FONT_TITLE,
                  foreground=HIGHLIGHT).pack(anchor="w", padx=20, pady=(18, 4))
        ttk.Label(self, text="Registra, edita o elimina conexiones PostgreSQL.",
                  style="Muted.TLabel").pack(anchor="w", padx=20, pady=(0, 14))

        # ── Card de formulario
        card = ttk.Frame(self, style="Card.TFrame", padding=18)
        card.pack(fill="x", padx=20, pady=(0, 10))

        fields = [
            ("alias",    "Alias *"),
            ("host",     "Host *"),
            ("port",     "Puerto"),
            ("dbname",   "Nombre BD *"),
            ("user",     "Usuario *"),
            ("password", "Contraseña *"),
        ]
        self._vars = {}
        for col, (key, label) in enumerate(fields):
            var = tk.StringVar()
            self._vars[key] = var
            r = col // 2
            c = (col % 2) * 2
            ttk.Label(card, text=label, style="Card.TLabel").grid(
                row=r, column=c, sticky="w", padx=(0, 6), pady=4)
            show = "*" if key == "password" else ""
            e = ttk.Entry(card, textvariable=var, style="Card.TEntry", width=28, show=show)
            e.grid(row=r, column=c + 1, sticky="ew", padx=(0, 20), pady=4)

        self._vars["port"].set("5432")
        card.columnconfigure(1, weight=1)
        card.columnconfigure(3, weight=1)

        # ── Botones
        btn_row = ttk.Frame(self, style="TFrame")
        btn_row.pack(fill="x", padx=20, pady=6)
        for text, cmd in [
            ("Agregar",   self._agregar),
            ("Actualizar", self._actualizar),
            ("Eliminar",  self._eliminar),
            ("Listar",    self._listar),
        ]:
            ttk.Button(btn_row, text=text, command=cmd).pack(
                side="left", padx=(0, 8))

        # ── Resultado
        ttk.Label(self, text="Respuesta", foreground=MUTED,
                  background=DARK_BG, font=FONT_LABEL).pack(anchor="w", padx=20, pady=(10, 2))
        self._result = make_result_box(self, height=12)
        self._result.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _get(self):
        return {k: v.get().strip() for k, v in self._vars.items()}

    def _agregar(self):
        d = self._get()
        if not all([d["alias"], d["host"], d["dbname"], d["user"], d["password"]]):
            messagebox.showwarning("Faltan datos", "Completa todos los campos obligatorios (*).")
            return
        try:
            d["port"] = int(d["port"] or 5432)
        except ValueError:
            messagebox.showerror("Puerto inválido", "El puerto debe ser un número entero.")
            return
        self._async(_request, "POST", "/agregar_base_datos", d)

    def _actualizar(self):
        d = self._get()
        if not d["alias"]:
            messagebox.showwarning("Alias requerido", "Escribe el alias de la BD a actualizar.")
            return
        try:
            d["port"] = int(d["port"] or 5432)
        except ValueError:
            messagebox.showerror("Puerto inválido", "El puerto debe ser un número entero.")
            return
        self._async(_request, "PUT", f"/actualizar_base_datos/{d['alias']}", d)

    def _eliminar(self):
        alias = self._vars["alias"].get().strip()
        if not alias:
            messagebox.showwarning("Alias requerido", "Escribe el alias de la BD a eliminar.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{alias}'?"):
            return
        self._async(_request, "DELETE", f"/eliminar_base_datos/{alias}")

    def _listar(self):
        self._async(_request, "GET", "/listar_bases_datos")

    def _async(self, fn, *args):
        set_result(self._result, " Esperando respuesta…", MUTED)
        def _run():
            result = fn(*args)
            self.after(0, lambda: set_result(
                self._result,
                json.dumps(result, indent=2, ensure_ascii=False),
                SUCCESS if "error" not in result else HIGHLIGHT
            ))
        threading.Thread(target=_run, daemon=True).start()



#  Pestaña 2 – CONSULTA AL AGENTE

class TabPreguntar(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook, style="TFrame")
        self._build()

    def _build(self):
        ttk.Label(self, text="Consulta al Agente SQL", font=FONT_TITLE,
                  foreground=HIGHLIGHT).pack(anchor="w", padx=20, pady=(18, 4))
        ttk.Label(self, text="Formula una pregunta en lenguaje natural. El supervisor orquestará los agentes.",
                  style="Muted.TLabel").pack(anchor="w", padx=20, pady=(0, 14))

        # Input
        input_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        input_card.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(input_card, text="Pregunta:", style="Card.TLabel").pack(anchor="w")
        self._pregunta = scrolledtext.ScrolledText(
            input_card, height=4, font=FONT_MONO,
            bg=INPUT_BG, fg=TEXT_FG, insertbackground=TEXT_FG,
            relief="flat", wrap="word"
        )
        self._pregunta.pack(fill="x", pady=(6, 0))
        self._pregunta.bind("<Control-Return>", lambda e: self._preguntar())

        hint = ttk.Label(input_card,
                         text="Ctrl+Enter para enviar",
                         style="Card.TLabel", foreground=MUTED)
        hint.pack(anchor="e", pady=(2, 0))

        btn_row = ttk.Frame(self, style="TFrame")
        btn_row.pack(anchor="w", padx=20, pady=6)
        ttk.Button(btn_row, text="Enviar pregunta", command=self._preguntar).pack(side="left")
        ttk.Button(btn_row, text="Limpiar",         command=self._limpiar).pack(side="left", padx=(8, 0))

        self._status = ttk.Label(btn_row, text="", foreground=WARNING, background=DARK_BG, font=FONT_LABEL)
        self._status.pack(side="left", padx=(16, 0))

        ttk.Label(self, text="Respuesta del agente", foreground=MUTED,
                  background=DARK_BG, font=FONT_LABEL).pack(anchor="w", padx=20, pady=(10, 2))
        self._result = make_result_box(self, height=18)
        self._result.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _preguntar(self):
        pregunta = self._pregunta.get("1.0", "end").strip()
        if not pregunta:
            messagebox.showwarning("Campo vacío", "Escribe una pregunta antes de enviar.")
            return
        set_result(self._result, " El agente está procesando tu consulta…\n(puede tardar varios segundos)", MUTED)
        self._status.config(text=" Procesando…")
        def _run():
            result = _request("POST", "/preguntar", {"pregunta": pregunta})
            def _update():
                self._status.config(text="")
                if "error" in result:
                    set_result(self._result, f"Error:\n{result['error']}", HIGHLIGHT)
                else:
                    set_result(self._result, result.get("respuesta", json.dumps(result, indent=2)), SUCCESS)
            self.after(0, _update)
        threading.Thread(target=_run, daemon=True).start()

    def _limpiar(self):
        self._pregunta.delete("1.0", "end")
        set_result(self._result, "")
        self._status.config(text="")




#  Pestaña 3 – CONVERSIÓN MD → PDF


class TabConversion(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook, style="TFrame")
        self._build()

    def _build(self):
        ttk.Label(self, text="Conversión Markdown → PDF", font=FONT_TITLE,
                  foreground=HIGHLIGHT).pack(anchor="w", padx=20, pady=(18, 4))
        ttk.Label(self, text="Convierte un archivo .md del servidor y descárgalo en PDF.",
                  style="Muted.TLabel").pack(anchor="w", padx=20, pady=(0, 14))

        card = ttk.Frame(self, style="Card.TFrame", padding=16)
        card.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(card, text="Nombre del archivo (sin extensión):", style="Card.TLabel").pack(anchor="w")
        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x", pady=(6, 0))
        self._nombre = ttk.Entry(row, style="Card.TEntry", width=34)
        self._nombre.pack(side="left", padx=(0, 10))
        self._nombre.bind("<Return>", lambda e: self._convertir())

        ttk.Label(card, text="Guardar PDF en:", style="Card.TLabel").pack(anchor="w", pady=(12, 0))
        dest_row = ttk.Frame(card, style="Card.TFrame")
        dest_row.pack(fill="x", pady=(4, 0))
        self._dest = ttk.Entry(dest_row, style="Card.TEntry", width=34)
        self._dest.pack(side="left", padx=(0, 10))
        self._dest.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))
        ttk.Button(dest_row, text=" Explorar", command=self._elegir_destino).pack(side="left")

        btn_row = ttk.Frame(self, style="TFrame")
        btn_row.pack(anchor="w", padx=20, pady=8)
        ttk.Button(btn_row, text="⬇  Descargar PDF", command=self._convertir).pack(side="left")

        self._status = ttk.Label(btn_row, text="", foreground=WARNING, background=DARK_BG, font=FONT_LABEL)
        self._status.pack(side="left", padx=(16, 0))

        ttk.Label(self, text="Resultado", foreground=MUTED,
                  background=DARK_BG, font=FONT_LABEL).pack(anchor="w", padx=20, pady=(10, 2))
        self._result = make_result_box(self, height=8)
        self._result.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _elegir_destino(self):
        folder = filedialog.askdirectory(title="Selecciona carpeta de destino")
        if folder:
            self._dest.delete(0, "end")
            self._dest.insert(0, folder)

    def _convertir(self):
        nombre = self._nombre.get().strip()
        dest   = self._dest.get().strip()
        if not nombre:
            messagebox.showwarning("Campo vacío", "Escribe el nombre del archivo Markdown.")
            return
        pdf_path = os.path.join(dest, f"{nombre}.pdf")
        set_result(self._result, "Solicitando conversión al servidor…", MUTED)
        self._status.config(text="Convirtiendo…")
        def _run():
            msg = _download(f"/conversion/{nombre}", pdf_path)
            def _update():
                self._status.config(text="")
                color = SUCCESS if os.path.exists(pdf_path) else HIGHLIGHT
                set_result(self._result, msg, color)
            self.after(0, _update)
        threading.Thread(target=_run, daemon=True).start()



#  Pestaña 4 – CONFIGURACIÓN


class TabConfig(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook, style="TFrame")
        self._build()

    def _build(self):
        ttk.Label(self, text="Configuración", font=FONT_TITLE,
                  foreground=HIGHLIGHT).pack(anchor="w", padx=20, pady=(18, 4))

        card = ttk.Frame(self, style="Card.TFrame", padding=18)
        card.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(card, text="URL base de la API:", style="Card.TLabel").pack(anchor="w")
        self._url_var = tk.StringVar(value=BASE_URL)
        url_entry = ttk.Entry(card, textvariable=self._url_var, style="Card.TEntry", width=40)
        url_entry.pack(anchor="w", pady=(6, 14))

        ttk.Button(card, text="Guardar", command=self._guardar).pack(anchor="w")

        # ── Estado de la API
        sep = ttk.Frame(self, style="TFrame", height=1)
        sep.pack(fill="x", padx=20, pady=10)

        ttk.Label(self, text="⬡  Estado de la conexión", foreground=MUTED,
                  background=DARK_BG, font=FONT_LABEL).pack(anchor="w", padx=20, pady=(0, 6))

        ping_row = ttk.Frame(self, style="TFrame")
        ping_row.pack(anchor="w", padx=20)
        ttk.Button(ping_row, text="Probar conexión", command=self._ping).pack(side="left")
        self._ping_status = ttk.Label(ping_row, text="", background=DARK_BG, font=FONT_LABEL)
        self._ping_status.pack(side="left", padx=(14, 0))

    def _guardar(self):
        global BASE_URL
        BASE_URL = self._url_var.get().strip().rstrip("/")
        messagebox.showinfo("Guardado", f"URL actualizada a:\n{BASE_URL}")

    def _ping(self):
        self._ping_status.config(text=" Conectando…", foreground=WARNING)
        def _run():
            result = _request("GET", "/listar_bases_datos")
            ok = "error" not in result
            msg    = " Conectado correctamente" if ok else f"  {result.get('error','Error')}"
            color  = SUCCESS if ok else HIGHLIGHT
            self.after(0, lambda: self._ping_status.config(text=msg, foreground=color))
        threading.Thread(target=_run, daemon=True).start()



#  VENTANA PRINCIPAL


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agentes DB  —  Panel de Control")
        self.geometry("860x680")
        self.minsize(700, 520)
        self.configure(bg=DARK_BG)
        apply_styles(self)
        self._build()

    def _build(self):
        # ── Header
        header = tk.Frame(self, bg=PANEL_BG, pady=10)
        header.pack(fill="x")
        tk.Label(
            header,
            text="    AGENTES DB",
            font=("Consolas", 17, "bold"),
            bg=PANEL_BG,
            fg=HIGHLIGHT,
        ).pack(side="left", padx=20)
        tk.Label(
            header,
            text="Sistema Multi-Agente SQL",
            font=("Consolas", 10),
            bg=PANEL_BG,
            fg=MUTED,
        ).pack(side="left", padx=(0, 20))

        # ── Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        tabs = [
            ("  Bases de Datos",  TabBD),
            (" Preguntar",       TabPreguntar),
            ("  Conversión PDF",  TabConversion),
            ("  Config",         TabConfig),
        ]
        for label, cls in tabs:
            frame = cls(nb)
            nb.add(frame, text=label)

        # ── Footer
        footer = tk.Frame(self, bg=PANEL_BG, pady=4)
        footer.pack(fill="x", side="bottom")
        tk.Label(
            footer,
            text=f"  Conectado a: {BASE_URL}    |    FastAPI + LangChain + MCP",
            font=("Consolas", 8),
            bg=PANEL_BG,
            fg=MUTED,
        ).pack(side="left", padx=12)



#  Conexión de entrada

if __name__ == "__main__":
    app = App()
    app.mainloop()