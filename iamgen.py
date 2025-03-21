import networkx as nx
import matplotlib.pyplot as plt

def crear_mapa_mental_rectangular():
    G = nx.DiGraph()
    
    # Nodos principales
    G.add_node("Transición al Mercado Laboral", subset=0)
    G.add_node("Desafíos", subset=1)
    G.add_node("Soluciones", subset=1)
    
    # Subcategorías de Desafíos
    desafios = ["Falta de Experiencia", "Manejo del Estrés", "Entrevistas Laborales", "Expectativas Irrealistas", "Redes de Contacto"]
    for d in desafios:
        G.add_node(d, subset=2)
    
    # Subcategorías de Soluciones
    soluciones = ["Habilidades de Liderazgo", "Gestión Emocional", "Preparación para Entrevistas"]
    for s in soluciones:
        G.add_node(s, subset=2)
    
    # Detalles de cada solución
    detalles = {
        "Habilidades de Liderazgo": ["Simulaciones de Dinámicas Grupales", "Aprendizaje Colaborativo", "Liderazgo Ético"],
        "Gestión Emocional": ["Talleres de Inteligencia Emocional", "Autorreflexión", "Manejo de Presión"],
        "Preparación para Entrevistas": ["Simulaciones de Entrevistas", "Estrategias de Comunicación", "Plan de Empleabilidad"]
    }

    for categoria, items in detalles.items():
        for item in items:
            G.add_node(item, subset=3)
            G.add_edge(categoria, item)

    # Conectar nodos
    G.add_edges_from([
        ("Transición al Mercado Laboral", "Desafíos"),
        ("Transición al Mercado Laboral", "Soluciones"),
    ])
    
    for d in desafios:
        G.add_edge("Desafíos", d)
    
    for s in soluciones:
        G.add_edge("Soluciones", s)

    # Dibujar el gráfico con un layout rectangular
    pos = nx.multipartite_layout(G, subset_key="subset")
    plt.figure(figsize=(14, 10))
    
    # Cambiar los colores de los nodos
    node_colors = ['lightblue' if G.nodes[n]["subset"] == 0 else 
                   'lightcoral' if G.nodes[n]["subset"] == 1 else 
                   'lightgreen' if G.nodes[n]["subset"] == 2 else 
                   'lightyellow' for n in G.nodes()]
    
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=4000, edge_color='gray', font_size=10, font_weight='bold', font_family='Arial')
    plt.title("Mapa Mental Rectangular: Transición al Mercado Laboral", fontsize=14)
    plt.show()

crear_mapa_mental_rectangular()