
import sys
import random
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QInputDialog, 
                             QMessageBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import GraphItem
import numpy as np

class GraphColoringApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coloration de Graphes - Welsh-Powell (PyQt)")
        self.setGeometry(100, 100, 800, 600)
        
        # Données du graphe
        self.graph = {'nodes': set(), 'edges': set()}
        self.colors = {}
        self.node_positions = {}
        
        # Initialisation de l'interface
        self.init_ui()
        
    def init_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Zone de visualisation du graphe
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.setAspectLocked(True)
        self.graph_plot = None
        main_layout.addWidget(self.graph_widget)
        
        # Contrôles
        controls_layout = QHBoxLayout()
        
        # Boutons
        self.add_node_btn = QPushButton("Ajouter Sommet")
        self.add_node_btn.clicked.connect(self.add_node)
        controls_layout.addWidget(self.add_node_btn)
        
        self.add_edge_btn = QPushButton("Ajouter Arête")
        self.add_edge_btn.clicked.connect(self.add_edge)
        controls_layout.addWidget(self.add_edge_btn)
        
        self.color_btn = QPushButton("Colorier Graphe")
        self.color_btn.clicked.connect(self.color_graph)
        controls_layout.addWidget(self.color_btn)
        
        self.clear_btn = QPushButton("Effacer Graphe")
        self.clear_btn.clicked.connect(self.clear_graph)
        controls_layout.addWidget(self.clear_btn)
        
        # Options pour le graphe aléatoire
        random_layout = QHBoxLayout()
        random_layout.addWidget(QLabel("Graphe aléatoire:"))
        
        self.node_count = QSpinBox()
        self.node_count.setRange(3, 50)
        self.node_count.setValue(10)
        random_layout.addWidget(self.node_count)
        
        self.edge_prob = QDoubleSpinBox()
        self.edge_prob.setRange(0.1, 1.0)
        self.edge_prob.setSingleStep(0.1)
        self.edge_prob.setValue(0.3)
        random_layout.addWidget(self.edge_prob)
        
        self.random_btn = QPushButton("Générer")
        self.random_btn.clicked.connect(self.generate_random_graph)
        random_layout.addWidget(self.random_btn)
        
        # Ajout des layouts
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(random_layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.update_status()
        
        # Dessiner le graphe vide
        self.draw_graph()
    
    def add_node(self):
        node, ok = QInputDialog.getInt(self, "Ajouter Sommet", "Numéro du sommet:", 0, 0, 1000)
        if ok:
            if node in self.graph['nodes']:
                QMessageBox.warning(self, "Attention", f"Le sommet {node} existe déjà!")
            else:
                self.graph['nodes'].add(node)
                # Augmentation de l'espace possible pour les positions
                self.node_positions[node] = (random.uniform(-50, 50), random.uniform(-50, 50))
                self.draw_graph()
                self.update_status()
    
    def add_edge(self):
        edge, ok = QInputDialog.getText(self, "Ajouter Arête", "Sommets (ex: 1,2):")
        if ok and edge:
            try:
                u, v = map(int, edge.split(','))
                if u == v:
                    QMessageBox.warning(self, "Attention", "Un sommet ne peut pas être connecté à lui-même!")
                elif (u, v) in self.graph['edges'] or (v, u) in self.graph['edges']:
                    QMessageBox.warning(self, "Attention", f"L'arête ({u},{v}) existe déjà!")
                elif u not in self.graph['nodes'] or v not in self.graph['nodes']:
                    QMessageBox.warning(self, "Attention", "Un des sommets n'existe pas!")
                else:
                    self.graph['edges'].add((u, v))
                    self.draw_graph()
                    self.update_status()
            except ValueError:
                QMessageBox.critical(self, "Erreur", "Format invalide! Utilisez: numéro,numéro")
    
    def color_graph(self):
        if not self.graph['nodes']:
            QMessageBox.warning(self, "Attention", "Le graphe est vide!")
            return
        
        # Implémentation de Welsh-Powell
        nodes = list(self.graph['nodes'])
        edges = list(self.graph['edges'])
        
        # Calcul des degrés
        degrees = defaultdict(int)
        for u, v in edges:
            degrees[u] += 1
            degrees[v] += 1
        
        # Tri décroissant par degré
        nodes.sort(key=lambda x: degrees[x], reverse=True)
        
        # Coloration
        color_map = {}
        available_colors = []
        color_count = 0
        
        for node in nodes:
            # Couleurs des voisins
            neighbor_colors = set()
            for u, v in edges:
                if u == node and v in color_map:
                    neighbor_colors.add(color_map[v])
                elif v == node and u in color_map:
                    neighbor_colors.add(color_map[u])
            
            # Trouver la première couleur disponible
            color = 0
            while color in neighbor_colors:
                color += 1
            
            color_map[node] = color
            if color >= color_count:
                color_count = color + 1
        
        self.colors = color_map
        self.draw_graph(colored=True)
        
        QMessageBox.information(self, "Résultat", 
                               f"Coloration terminée avec {color_count} couleurs.")
        self.update_status()
    
    def clear_graph(self):
        self.graph = {'nodes': set(), 'edges': set()}
        self.colors = {}
        self.node_positions = {}
        self.draw_graph()
        self.update_status()
    
    def generate_random_graph(self):
        n = self.node_count.value()
        p = self.edge_prob.value()
        
        self.graph = {'nodes': set(), 'edges': set()}
        self.colors = {}
        self.node_positions = {}
        
        # Ajout des nœuds avec plus d'espace
        for node in range(n):
            self.graph['nodes'].add(node)
            self.node_positions[node] = (random.uniform(-50, 50), random.uniform(-50, 50))
        
        # Ajout des arêtes aléatoires
        for u in range(n):
            for v in range(u+1, n):
                if random.random() < p:
                    self.graph['edges'].add((u, v))
        
        self.draw_graph()
        self.update_status()
    
    def draw_graph(self, colored=False):
        self.graph_widget.clear()
        
        if not self.graph['nodes']:
            text = pg.TextItem("Graphe vide\nAjoutez des sommets et des arêtes", 
                             color='k', anchor=(0.5, 0.5))
            self.graph_widget.addItem(text)
            text.setPos(0, 0)
            return
        
        nodes = list(self.graph['nodes'])
        edges = list(self.graph['edges'])
        
        # Positions des nœuds avec plus d'espace
        pos = np.array([self.node_positions[node] for node in nodes])
        if len(nodes) > 1:
            # Normalisation et augmentation de l'espacement
            pos = (pos - pos.mean(axis=0)) * 2
        
        # Couleurs des nœuds
        if colored and self.colors:
            palette = [
                (31, 119, 180),(0, 255, 255),(255, 0, 255),(174, 199, 232), (255, 127, 14), (255, 187, 120),
                (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)
            ]
            node_colors = [palette[self.colors[node] % 20] for node in nodes]
        else:
            node_colors = [(100, 100, 255) for _ in nodes]
        
        # Création de la matrice d'adjacence
        edge_pairs = []
        for u, v in edges:
            ui = nodes.index(u)
            vi = nodes.index(v)
            edge_pairs.append([ui, vi])
        
        adj = np.array(edge_pairs, dtype=int)
        
        # Création du graphe avec des nœuds plus grands
        self.graph_plot = pg.GraphItem()
        self.graph_widget.addItem(self.graph_plot)
        
        self.graph_plot.setData(
            pos=pos,
            adj=adj,
            pen=pg.mkPen(width=2, color='k'),
            symbolBrush=node_colors,
            symbolPen='k',
            size=30,  # Taille augmentée des nœuds
            pxMode=True
        )
        
        # Ajout des labels avec police plus grande
        for node, (x, y) in zip(nodes, pos):
            text = pg.TextItem(str(node), color='k', anchor=(0.5, 0.5))
            text.setFont(pg.Qt.QtGui.QFont('Arial', 14))
            self.graph_widget.addItem(text)
            text.setPos(x, y)
    
    def update_status(self):
        status = f"Sommets: {len(self.graph['nodes'])} | Arêtes: {len(self.graph['edges'])}"
        if self.colors:
            status += f" | Couleurs: {max(self.colors.values())+1 if self.colors else 0}"
        self.status_bar.showMessage(status)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphColoringApp()
    window.show()
    sys.exit(app.exec_())
    
