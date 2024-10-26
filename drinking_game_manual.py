import streamlit as st
import time
import requests

st.set_page_config(page_title="Les jeux d'alcool entre potes", page_icon="🍺")
SERVER_URL = "rowz0.pythonanywhere.com"

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

    def refresh_data(self):
        try:
            response = requests.post(f"{SERVER_URL}/api/refresh")
            response.raise_for_status()
            self.user_data = self.load_data()
            self.last_refresh = self.get_last_refresh()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to refresh data: {e}")
            return False

    def refresh_rules(self):
        try:
            response = requests.get(f"{SERVER_URL}/api/rules")
            response.raise_for_status()
            new_rules = response.json()
            if new_rules != self.rules:
                self.rules = new_rules
                return True
            return False
        except requests.RequestException as e:
            st.error(f"Failed to refresh rules: {e}")
            return False

    def check_for_updates(self):
        new_refresh = self.get_last_refresh()
        rules_updated = self.refresh_rules()
        if new_refresh > self.last_refresh or rules_updated:
            self.user_data = self.load_data()
            self.last_refresh = new_refresh
            return True
        return False

    def add_sip(self, username, count):
        try:
            response = requests.post(f"{SERVER_URL}/api/add-sip", json={"username": username, "count": count})
            response.raise_for_status()
            if username not in self.user_data:
                self.user_data[username] = {'sips': []}
            self.user_data[username]['sips'].append(count)
            return True
        except requests.RequestException as e:
            st.error(f"Failed to add sip: {e}")
            return False

    def add_rule(self, rule, sip_count):
        try:
            response = requests.post(f"{SERVER_URL}/api/add-rule", json={"rule": rule, "sip_count": sip_count})
            response.raise_for_status()
            self.refresh_rules()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to add rule: {e}")
            return False

    def delete_rule(self, index):
        try:
            response = requests.post(f"{SERVER_URL}/api/delete-rule", json={"index": index})
            response.raise_for_status()
            self.refresh_rules()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to delete rule: {e}")
            return False

    def reset_data(self):
        try:
            response = requests.post(f"{SERVER_URL}/api/reset-data")
            response.raise_for_status()
            self.refresh_data()
            self.refresh_rules()
            return True
        except requests.RequestException as e:
            st.error(f"Failed to reset data: {e}")
            return False

def main():
    st.title("Les jeux d'alcool entre potes")

    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = BeerSipDashboard()
    if 'success_message' not in st.session_state:
        st.session_state.success_message = None

    username = st.text_input('Entrez votre nom')
    if username:
        dashboard = st.session_state.dashboard

        # Drinking Rules
        st.subheader('Règlements')
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            new_rule = st.text_input('Ajouter une règle')
        with col2:
            rule_sip_count = st.number_input('Gorgée pour la règle', min_value=1, step=1)
        with col3:
            add_rule_button = st.button('Ajouter')
        
        if add_rule_button:
            if new_rule.strip():  # Check if the rule is not empty
                if dashboard.add_rule(new_rule, rule_sip_count):
                    st.success('Règle ajoutée!')
                    st.rerun()
            else:
                st.error('ENTREZ UNE RÈGLE SVP.')

        # Display rules with delete buttons and beer emoji buttons
        st.write('Règles mises en place:')
        for i, (rule, sip_count) in enumerate(dashboard.rules):
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                st.write(f"{i+1}. {rule} - {sip_count} sips")
            with col2:
                if st.button('🍺', key=f'add_sips_{i}'):
                    if dashboard.add_sip(username, sip_count):
                        st.session_state.success_message = f'{sip_count} gorgées ajoutées!'
                        st.rerun()
            with col3:
                if st.button('🗑️', key=f'delete_rule_{i}'):
                    if dashboard.delete_rule(i):
                        st.rerun()

        if st.session_state.success_message:
            st.success(st.session_state.success_message)
            st.session_state.success_message = None

        # Sip input
        st.subheader('Ajouter des gorgées')
        col1, col2 = st.columns(2)
        with col1:
            sip_count = st.number_input('Combien de gorgées?', min_value=1, step=1)
        with col2:
            if st.button('Add'):
                if dashboard.add_sip(username, sip_count):
                    st.session_state.success_message = f'{sip_count} gorgées ajoutées pour {username}!'
                    st.rerun()

        # Display sip data for all users
        st.subheader('Gorgées de tous les joueurs')
        for user, data in dashboard.user_data.items():
            st.write(f"{user}: {sum(data['sips'])} gorgées totales")

        # Reset data button
        if st.button('Reset Data'):
            if dashboard.reset_data():
                st.success('Toutes les données ont été réinitialisées!')
                st.rerun()

        # Manual refresh button for sip data
        if st.button('Refresh Sip Data'):
            if dashboard.refresh_data():
                st.success('Données de gorgées mises à jour pour tous les joueurs!')
                st.rerun()

    else:
        st.warning("ENTREZ VOTRE NOM SVP.")

if __name__ == "__main__":
    main()

    # Automatic refresh for rules and check for sip data updates
    while True:
        time.sleep(5)
        if 'dashboard' in st.session_state:
            dashboard = st.session_state.dashboard
            if dashboard.check_for_updates():
                st.rerun()