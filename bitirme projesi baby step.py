#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 18:14:41 2025

@author: irmaksklmz
"""

import tkinter as tk
import matplotlib.pyplot as plt
import json
import os
import math

# -----------------------------
# Veri Yapıları
# -----------------------------

nodes = []   # tüm noktalar burada tutulur
roads = []   # yollar burada tutulur

selection_mode = "dumping"
road_select_temp = []   # iki node.id biriktirmek için

# -----------------------------
# Yardımcı Fonksiyonlar
# -----------------------------

def find_closest_node(x, y, threshold=10):
    """Tıklanan noktaya en yakın gerçek node'u bulur"""
    best = None
    best_dist = 99999

    for node in nodes:
        nx, ny = node["x"], node["y"]
        d = math.dist((x, y), (nx, ny))

        if d < best_dist:
            best_dist = d
            best = node

    if best_dist <= threshold:
        return best

    return None


def add_node(x, y, node_type):
    """Yeni bir düğüm oluşturur ve ID verir"""
    node_id = f"{node_type}_{sum(n['type']==node_type for n in nodes) + 1}"

    nodes.append({
        "id": node_id,
        "type": node_type,
        "x": x,
        "y": y
    })

    return node_id


# -----------------------------
# Tkinter Callback Fonksiyonları
# -----------------------------

def on_click(event):
    global selection_mode, road_select_temp

    x, y = event.x, event.y

    # ROAD MODE
    if selection_mode == "road":
        clicked_node = find_closest_node(x, y)

        if clicked_node is None:
            info_label.config(text="❌ Yol oluşturmak için bir noktaya tıklamalısın.")
            return

        road_select_temp.append(clicked_node["id"])
        canvas.create_oval(clicked_node["x"]-5, clicked_node["y"]-5,
                           clicked_node["x"]+5, clicked_node["y"]+5, fill="black")

        if len(road_select_temp) == 2:
            start_id = road_select_temp[0]
            end_id = road_select_temp[1]

            # Çizgi çiz
            n1 = next(n for n in nodes if n["id"] == start_id)
            n2 = next(n for n in nodes if n["id"] == end_id)
            canvas.create_line(n1["x"], n1["y"], n2["x"], n2["y"], width=3, fill="grey")

            # Kaydet
            road_id = len(roads) + 1
            roads.append({
                "id": road_id,
                "start": start_id,
                "end": end_id
            })

            info_label.config(text=f"Road {road_id} eklendi")
            road_select_temp = []

        return

    # -----------------------------
    # NORMAL POINT EKLEME MODLARI
    # -----------------------------

    c = "#000"
    if selection_mode == "dumping":     c="red"
    elif selection_mode == "loading":   c="blue"
    elif selection_mode == "fuel":      c="green"
    elif selection_mode == "electric":  c="purple"

    node_id = add_node(x, y, selection_mode)
    canvas.create_oval(x-4, y-4, x+4, y+4, fill=c)
    info_label.config(text=f"{selection_mode} → {node_id} eklendi")


def set_mode(mode):
    global selection_mode
    selection_mode = mode
    info_label.config(text=f"{mode.upper()} modundasın")


# -----------------------------
# JSON EXPORT
# -----------------------------

def export_json():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop", "map_data.json")

    data = {
        "nodes": nodes,
        "roads": roads
    }

    with open(desktop, "w") as f:
        json.dump(data, f, indent=4)

    info_label.config(text=f"JSON kaydedildi → Desktop/map_data.json")
    print("JSON saved:", desktop)


# -----------------------------
# Map Plot
# -----------------------------

def show_map():
    root.destroy()

    plt.figure(figsize=(7,7))

    # Noktaları çiz
    for n in nodes:
        color = {"dumping":"red", "loading":"blue", "fuel":"green", "electric":"purple"}[n["type"]]
        plt.scatter(n["x"], n["y"], c=color)
        plt.text(n["x"]+5, n["y"]-5, n["id"])

    # Yolları çiz
    for r in roads:
        n1 = next(n for n in nodes if n["id"] == r["start"])
        n2 = next(n for n in nodes if n["id"] == r["end"])
        plt.plot([n1["x"], n2["x"]], [n1["y"], n2["y"]], c="grey")

    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.title("Harita")
    plt.show()


# -----------------------------
# TKINTER GUI
# -----------------------------

root = tk.Tk()
root.title("Harita Oluşturma")

info_label = tk.Label(root, text="Dumping noktalarını seç", font=("Arial", 14))
info_label.pack()

canvas = tk.Canvas(root, width=700, height=700, bg="white")
canvas.pack()
canvas.bind("<Button-1>", on_click)

tk.Button(root, text="Dumping", command=lambda: set_mode("dumping")).pack()
tk.Button(root, text="Loading", command=lambda: set_mode("loading")).pack()
tk.Button(root, text="Fuel", command=lambda: set_mode("fuel")).pack()
tk.Button(root, text="Electric", command=lambda: set_mode("electric")).pack()
tk.Button(root, text="Road Oluştur (2 Nokta)", command=lambda: set_mode("road")).pack()
tk.Button(root, text="JSON Kaydet", command=export_json).pack()
tk.Button(root, text="Haritayı Göster", command=show_map).pack()

root.mainloop()
