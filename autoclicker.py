# streamlit_autoclicker.py

import streamlit as st
import pyautogui
import threading
import time

clicking = False
targets = [(0, 0)] * 4

# Function to update target coordinates
def update_targets(coords):
    for i in range(4):
        try:
            x = int(coords[f'x{i}'])
            y = int(coords[f'y{i}'])
            targets[i] = (x, y)
        except ValueError:
            targets[i] = (0, 0)

# Click loop running in background
def click_loop():
    global clicking
    while clicking:
        for x, y in targets:
            if not clicking:
                break
            pyautogui.moveTo(x, y)
            pyautogui.click()
            time.sleep(0.01)

# Start clicking thread
def start_clicking(coords):
    global clicking
    if not clicking:
        update_targets(coords)
        clicking = True
        thread = threading.Thread(target=click_loop, daemon=True)
        thread.start()

# Stop clicking
def stop_clicking():
    global clicking
    clicking = False

# Streamlit GUI
st.title("4-Target AutoClicker (Streamlit Version)")

coords = {}
for i in range(4):
    st.subheader(f"Target {i+1}")
    col1, col2 = st.columns(2)
    coords[f'x{i}'] = col1.number_input(f"X{i+1}", value=0, step=1, key=f'x{i}')
    coords[f'y{i}'] = col2.number_input(f"Y{i+1}", value=0, step=1, key=f'y{i}')

# Start/Stop buttons
start = st.button("Start Clicking")
stop = st.button("Stop Clicking")

if start:
    start_clicking(coords)
    st.success("Clicking started!")

if stop:
    stop_clicking()
    st.warning("Clicking stopped.")
