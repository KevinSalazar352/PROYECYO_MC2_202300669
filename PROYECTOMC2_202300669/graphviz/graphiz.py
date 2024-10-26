import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import os
from collections import deque

class GraphApp:
    def __init__(self, master):
        self.master = master
        master.title("Generador de Gráficos No Dirigidos con Pesos")

        # Apartado para dibujar el gráfico original
        self.canvas = tk.Canvas(master, width=400, height=400, bg='white')
        self.canvas.pack(side=tk.LEFT)

        # Apartados para ver otros gráficos
        self.canvas_bfs = tk.Canvas(master, width=400, height=400, bg='lightblue')
        self.canvas_bfs.pack(side=tk.LEFT)

        self.canvas_dfs = tk.Canvas(master, width=400, height=400, bg='lightgreen')
        self.canvas_dfs.pack(side=tk.LEFT)

        # Apartado para funcionalidades
        self.func_frame = tk.Frame(master)
        self.func_frame.pack(side=tk.RIGHT, padx=10)

        # Campos y botones para agregar vértices
        self.vertex_label = tk.Label(self.func_frame, text="Agregar Vértice (letra):")
        self.vertex_label.pack()
        self.vertex_entry = tk.Entry(self.func_frame)
        self.vertex_entry.pack()
        self.add_vertex_button = tk.Button(self.func_frame, text="Agregar Vértice", command=self.add_vertex)
        self.add_vertex_button.pack()

        # Campos y botones para crear aristas
        self.edge_label = tk.Label(self.func_frame, text="Crear Arista (ej. a-b):")
        self.edge_label.pack()
        self.edge_entry = tk.Entry(self.func_frame)
        self.edge_entry.pack()
        self.add_edge_button = tk.Button(self.func_frame, text="Crear Arista", command=self.add_edge)
        self.add_edge_button.pack()

        # Listas para vértices y aristas
        self.vertices = []
        self.edges = []
        self.vertex_weights = {}  # Diccionario para almacenar pesos

        # Apartado para mostrar vértices y aristas
        self.vertex_list_label = tk.Label(self.func_frame, text="Vértices Creados:")
        self.vertex_list_label.pack()
        self.vertex_listbox = tk.Listbox(self.func_frame)
        self.vertex_listbox.pack()

        self.edge_list_label = tk.Label(self.func_frame, text="Aristas Creadas:")
        self.edge_list_label.pack()
        self.edge_listbox = tk.Listbox(self.func_frame)
        self.edge_listbox.pack()

        # Botón para generar gráfico
        self.generate_button = tk.Button(self.func_frame, text="Generar Gráfico", command=self.generate_graph)
        self.generate_button.pack()

        # Botones para BFS y DFS
        self.bfs_button = tk.Button(self.func_frame, text="Algoritmo de búsqueda en anchura", command=self.bfs)
        self.bfs_button.pack()

        self.dfs_button = tk.Button(self.func_frame, text="Algoritmo de búsqueda en profundidad", command=self.dfs)
        self.dfs_button.pack()

        # Botones para limpiar y borrar
        self.clear_button = tk.Button(self.func_frame, text="Limpiar Todo", command=self.clear_all)
        self.clear_button.pack()

        self.remove_vertex_button = tk.Button(self.func_frame, text="Borrar Vértice", command=self.remove_vertex)
        self.remove_vertex_button.pack()

        self.remove_edge_button = tk.Button(self.func_frame, text="Borrar Arista", command=self.remove_edge)
        self.remove_edge_button.pack()

    def add_vertex(self):
        vertex = self.vertex_entry.get().strip().lower()
        if vertex and vertex not in self.vertices and vertex.isalpha() and len(vertex) == 1:
            self.vertices.append(vertex)
            # Asignar peso al vértice basado en su posición en el abecedario
            weight = ord(vertex) - ord('a') + 1
            self.vertex_weights[vertex] = weight
            self.vertex_listbox.insert(tk.END, f"{vertex} (peso: {weight})")
            self.vertex_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Vértice inválido o ya existe.")

    def add_edge(self):
        edge = self.edge_entry.get().strip().lower()
        if edge and all(v in self.vertices for v in edge.split('-')) and len(edge.split('-')) == 2:
            v1, v2 = edge.split('-')
            if f"{v1}-{v2}" not in self.edges and f"{v2}-{v1}" not in self.edges:
                self.edges.append(f"{v1}-{v2}")
                self.edge_listbox.insert(tk.END, edge)
                self.edge_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Arista ya existe.")
        else:
            messagebox.showerror("Error", "Arista inválida o vértices no existen.")

    def remove_vertex(self):
        selected_vertex_index = self.vertex_listbox.curselection()
        if selected_vertex_index:
            vertex_to_remove = self.vertex_listbox.get(selected_vertex_index).split()[0]
            self.vertices.remove(vertex_to_remove)
            del self.vertex_weights[vertex_to_remove]
            self.vertex_listbox.delete(selected_vertex_index)

            # También eliminar aristas asociadas a este vértice
            self.edges = [edge for edge in self.edges if vertex_to_remove not in edge]
            self.update_edge_listbox()
        else:
            messagebox.showerror("Error", "Seleccione un vértice para borrar.")

    def remove_edge(self):
        selected_edge_index = self.edge_listbox.curselection()
        if selected_edge_index:
            edge_to_remove = self.edge_listbox.get(selected_edge_index)
            self.edges.remove(edge_to_remove)
            self.edge_listbox.delete(selected_edge_index)
        else:
            messagebox.showerror("Error", "Seleccione una arista para borrar.")

    def update_edge_listbox(self):
        self.edge_listbox.delete(0, tk.END)
        for edge in self.edges:
            self.edge_listbox.insert(tk.END, edge)

    def clear_all(self):
        self.vertices.clear()
        self.edges.clear()
        self.vertex_weights.clear()
        self.vertex_listbox.delete(0, tk.END)
        self.edge_listbox.delete(0, tk.END)
        self.canvas.delete("all")
        self.canvas_bfs.delete("all")
        self.canvas_dfs.delete("all")

    def generate_graph(self):
        dot_content = "graph G {\n"  # Usar 'graph' para grafos no dirigidos
        for vertex in self.vertices:
            weight = self.vertex_weights[vertex]
            dot_content += f"    {vertex} [label=\"{vertex} (peso: {weight})\"];\n"
        for edge in self.edges:
            v1, v2 = edge.split('-')
            dot_content += f"    {v1} -- {v2};\n"  # ' -- ' para grafos no dirigidos
        dot_content += "}"

        with open("graph.dot", "w") as dot_file:
            dot_file.write(dot_content)

        comando = '"C:\\Program Files\\Graphviz\\bin\\dot.exe" -Tpng graph.dot -o graph.png'
        result = subprocess.run(comando, shell=True)

        if result.returncode == 0:
            messagebox.showinfo("Éxito", "Gráfico generado correctamente.")
            self.draw_graph()
        else:
            messagebox.showerror("Error", "Error al generar el gráfico.")

    def draw_graph(self):
        self.canvas.delete("all")
        if os.path.exists("graph.png"):
            img = Image.open("graph.png")
            img = img.resize((400, 400), Image.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

    def bfs(self):
        if not self.vertices:
            messagebox.showerror("Error", "No hay vértices para realizar BFS.")
            return

        graph = self.create_adjacency_list()
        start_vertex = self.vertices[0]
        visited = set()
        queue = deque([start_vertex])
        bfs_order = []

        while queue:
            vertex = queue.popleft()
            if vertex not in visited:
                visited.add(vertex)
                bfs_order.append(vertex)
                for neighbor in graph[vertex]:
                    if neighbor not in visited:
                        queue.append(neighbor)

        self.draw_bfs_graph(bfs_order)

    def dfs(self):
        if not self.vertices:
            messagebox.showerror("Error", "No hay vértices para realizar DFS.")
            return

        graph = self.create_adjacency_list()
        start_vertex = self.vertices[0]
        visited = set()
        dfs_order = []

        self.dfs_util(start_vertex, visited, dfs_order, graph)

        self.draw_dfs_graph(dfs_order)

    def create_adjacency_list(self):
        graph = {v: [] for v in self.vertices}
        for edge in self.edges:
            v1, v2 = edge.split('-')
            graph[v1].append(v2)
            graph[v2].append(v1)
        return graph

    def dfs_util(self, vertex, visited, dfs_order, graph):
        visited.add(vertex)
        dfs_order.append(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                self.dfs_util(neighbor, visited, dfs_order, graph)

    def draw_bfs_graph(self, bfs_order):
        self.canvas_bfs.delete("all")
        dot_content = "graph G {\n"
        for edge in self.edges:
            v1, v2 = edge.split('-')
            dot_content += f"    {v1} -- {v2};\n"
        for i in range(len(bfs_order) - 1):
            dot_content += f"    {bfs_order[i]} -- {bfs_order[i+1]} [color=red,penwidth=2.0];\n"
        dot_content += "}"

        with open("bfs.dot", "w") as dot_file:
            dot_file.write(dot_content)

        comando = '"C:\\Program Files\\Graphviz\\bin\\dot.exe" -Tpng bfs.dot -o bfs.png'
        subprocess.run(comando, shell=True)

        if os.path.exists("bfs.png"):
            img = Image.open("bfs.png")
            img = img.resize((400, 400), Image.LANCZOS)
            self.img_bfs_tk = ImageTk.PhotoImage(img)
            self.canvas_bfs.create_image(0, 0, anchor=tk.NW, image=self.img_bfs_tk)

    def draw_dfs_graph(self, dfs_order):
        self.canvas_dfs.delete("all")
        dot_content = "graph G {\n"
        for edge in self.edges:
            v1, v2 = edge.split('-')
            dot_content += f"    {v1} -- {v2};\n"
        for i in range(len(dfs_order) - 1):
            dot_content += f"    {dfs_order[i]} -- {dfs_order[i+1]} [color=blue,penwidth=2.0];\n"
        dot_content += "}"

        with open("dfs.dot", "w") as dot_file:
            dot_file.write(dot_content)

        comando = '"C:\\Program Files\\Graphviz\\bin\\dot.exe" -Tpng dfs.dot -o dfs.png'
        subprocess.run(comando, shell=True)

        if os.path.exists("dfs.png"):
            img = Image.open("dfs.png")
            img = img.resize((400, 400), Image.LANCZOS)
            self.img_dfs_tk = ImageTk.PhotoImage(img)
            self.canvas_dfs.create_image(0, 0, anchor=tk.NW, image=self.img_dfs_tk)
# ... (todo el código anterior) ...

    def bfs(self):
        if not self.vertices:
            messagebox.showerror("Error", "No hay vértices para realizar BFS.")
            return

        graph = self.create_adjacency_list()
        start_vertex = self.vertices[0]  # Se empieza desde el primer vértice
        visited = set()
        queue = deque([start_vertex])
        bfs_order = []

        while queue:
            vertex = queue.popleft()
            if vertex not in visited:
                visited.add(vertex)
                bfs_order.append(vertex)
                for neighbor in graph[vertex]:
                    if neighbor not in visited:
                        queue.append(neighbor)

        self.draw_bfs_graph(bfs_order)
        self.show_steps("BFS", bfs_order)

    def dfs(self):
        if not self.vertices:
            messagebox.showerror("Error", "No hay vértices para realizar DFS.")
            return

        graph = self.create_adjacency_list()
        start_vertex = self.vertices[0]  # Se empieza desde el primer vértice
        visited = set()
        dfs_order = []

        self.dfs_util(start_vertex, visited, dfs_order, graph)

        self.draw_dfs_graph(dfs_order)
        self.show_steps("DFS", dfs_order)

    def show_steps(self, search_type, order):
        steps_window = tk.Toplevel(self.master)
        steps_window.title(f"Pasos de búsqueda: {search_type}")

        steps_label = tk.Label(steps_window, text=f"Pasos de búsqueda {search_type}:", font=("Arial", 14))
        steps_label.pack(pady=10)

        steps_text = " -> ".join(order)
        steps_display = tk.Label(steps_window, text=steps_text, font=("Arial", 12))
        steps_display.pack(pady=10)

        close_button = tk.Button(steps_window, text="Cerrar", command=steps_window.destroy)
        close_button.pack(pady=10)

# ... (todo el código posterior) ...

root = tk.Tk()
app = GraphApp(root)
root.mainloop()
