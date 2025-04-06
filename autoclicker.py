# streamlit_autoclicker.py

import streamlit as st
import pyautogui
import threading
import time

# Global control flag
clicking = False
targets = [(0, 0)] * 4

# Session state setup
if 'coords' not in st.session_state:
    st.session_state.coords = [{'x': 0, 'y': 0} for _ in range(4)]

def update_targets():
    for i in range(4):
        x = st.session_state.coords[i]['x']
        y = st.session_state.coords[i]['y']
        targets[i] = (x, y)

# Clicking loop
def click_loop():
    global clicking
    while clicking:
        for x, y in targets:
            if not clicking:
                break
            pyautogui.moveTo(x, y)
            pyautogui.click()
            time.sleep(0.01)

# Start clicking
def start_clicking():
    global clicking
    if not clicking:
        update_targets()
        clicking = True
        threading.Thread(target=click_loop, daemon=True).start()

# Stop clicking
def stop_clicking():
    global clicking
    clicking = False

# Capture mouse position for a specific index
def capture_position(i):
    x, y = pyautogui.position()
    st.session_state.coords[i]['x'] = x
    st.session_state.coords[i]['y'] = y
    st.experimental_rerun()  # Refresh the UI to show updated values

# UI
st.title("🖱️ 4-Target AutoClicker (with Position Picker)")

for i in range(4):
    st.subheader(f"🎯 Target {i + 1}")
    col1, col2, col3 = st.columns([1, 1, 2])
    st.session_state.coords[i]['x'] = col1.number_input(f"X{i+1}", value=st.session_state.coords[i]['x'], step=1, key=f"x{i}")
    st.session_state.coords[i]['y'] = col2.number_input(f"Y{i+1}", value=st.session_state.coords[i]['y'], step=1, key=f"y{i}")
    col3.button(f"📍 Pick Current Position", key=f"btn{i}", on_click=capture_position, args=(i,))

st.markdown("---")
col_start, col_stop = st.columns(2)
if col_start.button("✅ Start Clicking"):
    start_clicking()
    st.success("Clicking started!")

if col_stop.button("🛑 Stop Clicking"):
    stop_clicking()
    st.warning("Clicking stopped.")
