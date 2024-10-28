import requests
import time
import networkx as nx
import matplotlib.pyplot as plt

def get_links(article_title, limit=50):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "links",
        "titles": article_title,
        "pllimit": "max"
    }
    links = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        page_id = next(iter(data['query']['pages']))
        
        if 'links' in data['query']['pages'][page_id]:
            for link in data['query']['pages'][page_id]['links']:
                links.append(link['title'])
                if len(links) >= limit:
                    return links
        
        if "continue" in data:
            params.update(data["continue"])
        else:
            break
        
        time.sleep(1)
    
    return links


def build_graph(start_article, depth=2, link_limit=50):
    graph = nx.DiGraph()
    to_visit = [(start_article, 0)]
    visited = set()
    
    while to_visit:
        current_article, current_depth = to_visit.pop(0)
        if current_article in visited or current_depth > depth:
            continue
        visited.add(current_article)
        
        links = get_links(current_article, limit=link_limit)
        for link in links:
            graph.add_edge(current_article, link)
            if link not in visited:
                to_visit.append((link, current_depth + 1))
    
    return graph


def visualize_graph(graph):
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(graph, k=0.1)
    nx.draw(graph, pos, with_labels=True, node_size=50, font_size=8, edge_color='gray')
    plt.show()


if __name__ == "__main__":
    start_article = "Goiaba"
    depth = 2
    link_limit = 10

    graph = build_graph(start_article, depth, link_limit)
    visualize_graph(graph)
