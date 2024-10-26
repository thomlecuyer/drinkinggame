import streamlit as st
import requests
import time
import json
import os

# Set page config
st.set_page_config(page_title="Les jeux d'alcool entre potes", page_icon="🍺")

# Use Streamlit's secrets management for the server URL
SERVER_URL = os.environ.get('SERVER_URL', 'http://localhost:5000')

class BeerSipDashboard:
    def __init__(self):
        self.user_data = self.load_data()
        self.rules = self.load_rules()
        self.last_refresh = self.get_last_refresh()
        self.last_rules_refresh = 0

    def load_data(self):
        try:
            response = requests.get(f"{SERVER_URL}/api/sip-data")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to load sip data: {e}")
            return {}

    def load_rules(self):
        try:
            response = requests.get(f"{SERVER_URL}/api/rules")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to load rules: {e}")
            return []

    def get_last_refresh(self):
        try:
            response = requests.get(f"{SERVER_URL}/api/last-refresh")
            response.raise_for_status()
            return response.json()['timestamp']
        except requests.RequestException as e:
            st.error(f"Failed to get last refresh time: {e}")
            return 0

    def add_sip(self, username, count):
        try:
            response = requests.post(f"{SERVER_URL}/api/add-sip", json={"username": username, "count": count})
            response.raise_for_status()
            self.user_data = self.load_data()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to add sip: {e}")
            return False

    def add_rule(self, rule, sip_count):
        try:
            response = requests.post(f"{SERVER_URL}/api/add-rule", json={"rule": rule, "sip_count": sip_count})
            response.raise_for_status()
            self.rules = self.load_rules()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to add rule: {e}")
            return False

    def delete_rule(self, index):
        try:
            response = requests.post(f"{SERVER_URL}/api/delete-rule", json={"index": index})
            response.raise_for_status()
            self.rules = self.load_rules()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to delete rule: {e}")
            return False

    def reset_data(self):
        try:
            response = requests.post(f"{SERVER_URL}/api/reset-data")
            response.raise_for_status()
            self.user_data = {}
            self.rules = []
            self.last_refresh = time.time()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to reset data: {e}")
            return False

    def refresh(self):
        try:
            response = requests.post(f"{SERVER_URL}/api/refresh")
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to refresh: {e}")
            return False

    def check_for_updates(self):
        current_refresh = self.get_last_refresh()
        if current_refresh > self.last_refresh:
            self.last_refresh = current_refresh
            self.user_data = self.load_data()
            self.rules = self.load_rules()
            return True
        return False

def main():
    st.title("🍺 Les jeux d'alcool entre potes")

    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = BeerSipDashboard()

    dashboard = st.session_state.dashboard

    # Display user data
    st.header("Nombre de gorgées par joueur")
    for username, data in dashboard.user_data.items():
        total_sips = sum(data['sips'])
        st.write(f"{username}: {total_sips} gorgées")

    # Add sips form
    st.header("Ajouter des gorgées")
    username = st.text_input("Nom du joueur")
    sip_count = st.number_input("Nombre de gorgées", min_value=1, value=1)
    if st.button("Ajouter des gorgées"):
        if username:
            if dashboard.add_sip(username, sip_count):
                st.success('Gorgées ajoutées!')
                st.experimental_rerun()
        else:
            st.warning("ENTREZ VOTRE NOM SVP.")

    # Display rules
    st.header("Règles du jeu")
    for i, (rule, sip_count) in enumerate(dashboard.rules):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"{rule}")
        col2.write(f"{sip_count} gorgées")
        if col3.button("Supprimer", key=f"delete_{i}"):
            if dashboard.delete_rule(i):
                st.experimental_rerun()

    # Add rule form
    st.header("Ajouter une règle")
    new_rule = st.text_input("Nouvelle règle")
    rule_sip_count = st.number_input("Nombre de gorgées pour cette règle", min_value=1, value=1)
    if st.button("Ajouter la règle"):
        if new_rule.strip():
            if dashboard.add_rule(new_rule, rule_sip_count):
                st.success('Règle ajoutée!')
                st.experimental_rerun()
        else:
            st.error('ENTREZ UNE RÈGLE SVP.')

    # Reset button
    if st.button("Réinitialiser les données"):
        if dashboard.reset_data():
            st.success('Données réinitialisées!')
            st.experimental_rerun()

    # Refresh button
    if st.button("Rafraîchir"):
        if dashboard.refresh():
            st.experimental_rerun()

if __name__ == "__main__":
    main()
