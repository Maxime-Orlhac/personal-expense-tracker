import os
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta


st.title("💰 Gestion de Dépenses")

# ========================================
# Configuration du dossier
# ========================================
#dossier = r"C:\Users\maxim\OneDrive\Bureau\developpement\Python\Projet\depense"
dossier = os.path.join(os.path.dirname(__file__), "data")

# ========================================
# Initialisation de la navigation
# ========================================
if 'page' not in st.session_state:
    st.session_state.page = 'accueil'
if 'portefeuille_selectionne' not in st.session_state:
    st.session_state.portefeuille_selectionne = None
# Initialisation du mois sélectionné (mois actuel par défaut)
if 'mois_selectionne' not in st.session_state:
    st.session_state.mois_selectionne = datetime.now().strftime('%Y-%m')
# Initialisation pour la suppression
if 'transaction_a_supprimer' not in st.session_state:
    st.session_state.transaction_a_supprimer = None

# ========================================
# Fonctions de navigation
# ========================================
def aller_vers_detail(fichier):
    st.session_state.page = 'detail'
    st.session_state.portefeuille_selectionne = fichier
    # Réinitialiser au mois actuel quand on ouvre un portefeuille
    st.session_state.mois_selectionne = datetime.now().strftime('%Y-%m')
    st.rerun()

def retour_accueil():
    st.session_state.page = 'accueil'
    st.session_state.portefeuille_selectionne = None
    st.rerun()

def mois_precedent():
    # Convertir le mois actuel en date
    date_actuelle = datetime.strptime(st.session_state.mois_selectionne, '%Y-%m')
    # Soustraire un mois (aller au premier du mois précédent)
    if date_actuelle.month == 1:
        nouvelle_date = date_actuelle.replace(year=date_actuelle.year - 1, month=12)
    else:
        nouvelle_date = date_actuelle.replace(month=date_actuelle.month - 1)
    st.session_state.mois_selectionne = nouvelle_date.strftime('%Y-%m')
    st.rerun()

def mois_suivant():
    # Convertir le mois actuel en date
    date_actuelle = datetime.strptime(st.session_state.mois_selectionne, '%Y-%m')
    # Ajouter un mois
    if date_actuelle.month == 12:
        nouvelle_date = date_actuelle.replace(year=date_actuelle.year + 1, month=1)
    else:
        nouvelle_date = date_actuelle.replace(month=date_actuelle.month + 1)
    st.session_state.mois_selectionne = nouvelle_date.strftime('%Y-%m')
    st.rerun()

# ========================================
# Vérification du dossier
# ========================================
if not os.path.exists(dossier):
    st.error(f"❌ Le dossier n'existe pas : {dossier}")
    st.stop()

# ========================================
# Liste des fichiers CSV
# ========================================
fichiers_csv = [f for f in os.listdir(dossier) if f.endswith(".csv")]

# ========================================
# PAGE ACCUEIL
# ========================================
if st.session_state.page == 'accueil':
    st.write("📂 Fichiers disponibles dans le dossier :")
    
    if fichiers_csv:
        for i, fichier in enumerate(fichiers_csv, 1):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{i}. {fichier}**")
            
            with col2:
                if st.button("Voir détails", key=f"btn_{fichier}"):
                    aller_vers_detail(fichier)
            
            st.write("---")
    else:
        st.warning("⚠️ Aucun fichier CSV trouvé dans le dossier.")

# ========================================
# PAGE DETAIL
# ========================================
elif st.session_state.page == 'detail':
    if st.button("⬅️ Retour à l'accueil"):
        retour_accueil()
    
    fichier = st.session_state.portefeuille_selectionne
    st.header(f"📊 Statistiques pour : {fichier}")
    
    chemin_fichier = os.path.join(dossier, fichier)
    
    # ========================================
    # Boutons pour ajouter dépense/revenu + Solde
    # ========================================
    col_btn1, col_btn2, col_solde = st.columns([1, 1, 1])
    
    with col_btn1:
        if st.button("➕ Ajouter une dépense", use_container_width=True):
            st.session_state.show_form_depense = True
            st.session_state.show_form_revenu = False
    
    with col_btn2:
        if st.button("💰 Ajouter un revenu", use_container_width=True):
            st.session_state.show_form_revenu = True
            st.session_state.show_form_depense = False
    
    # Initialiser les états des formulaires
    if 'show_form_depense' not in st.session_state:
        st.session_state.show_form_depense = False
    if 'show_form_revenu' not in st.session_state:
        st.session_state.show_form_revenu = False
    
    # ========================================
    # CALCUL DU SOLDE (CB et Cash)
    # ========================================
    try:
        df_temp = pd.read_csv(chemin_fichier)
        df_temp['date'] = pd.to_datetime(df_temp['date'], format='%d/%m/%y')
        
        # Calculer les soldes
        solde_cb = df_temp[df_temp['cash ou CB'].str.lower() == 'cb']['montant'].sum()
        solde_cash = df_temp[df_temp['cash ou CB'].str.lower() == 'cash']['montant'].sum()
        
        with col_solde:
            st.metric("💳 Solde CB", f"{solde_cb:.2f} €")
            st.caption(f"💵 Solde Cash: {solde_cash:.2f} €")
    except:
        with col_solde:
            st.metric("💳 Solde CB", "0.00 €")
            st.caption("💵 Solde Cash: 0.00 €")
    
    # ========================================
    # FORMULAIRE AJOUTER UNE DÉPENSE
    # ========================================
    if st.session_state.show_form_depense:
        with st.form("form_depense"):
            st.subheader("➕ Ajouter une dépense")
            
            col1, col2 = st.columns(2)
            
            with col1:
                date_depense = st.date_input("Date", value=datetime.now())
                montant_depense = st.number_input("Montant (€)", min_value=0.0, step=0.01)
                type_depense = st.text_input("Type de dépense", placeholder="Ex: Restaurant, Course...")
            
            with col2:
                utile_depense = st.selectbox("Utile ?", ["oui", "non"])
                mode_paiement = st.selectbox("Mode de paiement", ["CB", "cash"])
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button("✅ Enregistrer", use_container_width=True)
            
            with col_cancel:
                cancel = st.form_submit_button("❌ Annuler", use_container_width=True)
            
            if submitted:
                # Ajouter la nouvelle dépense au CSV (montant NÉGATIF)
                nouvelle_ligne = {
                    'date': date_depense.strftime('%d/%m/%y'),
                    'montant': -montant_depense,  # NÉGATIF pour dépense
                    'type de depense': type_depense,
                    'utile (yes/no)': utile_depense,
                    'cash ou CB': mode_paiement
                }
                
                # Lire le CSV existant
                df_existant = pd.read_csv(chemin_fichier)
                # Ajouter la nouvelle ligne
                df_nouveau = pd.concat([df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
                # Sauvegarder
                df_nouveau.to_csv(chemin_fichier, index=False)
                
                st.success(f"✅ Dépense de {montant_depense:.2f} € ajoutée avec succès !")
                st.session_state.show_form_depense = False
                st.rerun()
            
            if cancel:
                st.session_state.show_form_depense = False
                st.rerun()
    
    # ========================================
    # FORMULAIRE AJOUTER UN REVENU
    # ========================================
    if st.session_state.show_form_revenu:
        with st.form("form_revenu"):
            st.subheader("💰 Ajouter un revenu")
            
            col1, col2 = st.columns(2)
            
            with col1:
                date_revenu = st.date_input("Date", value=datetime.now())
                montant_revenu = st.number_input("Montant (€)", min_value=0.0, step=0.01)
                type_revenu = st.text_input("Type de revenu", placeholder="Ex: Salaire, Prime...")
            
            with col2:
                mode_paiement_revenu = st.selectbox("Mode de paiement", ["CB", "cash"])
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button("✅ Enregistrer", use_container_width=True)
            
            with col_cancel:
                cancel = st.form_submit_button("❌ Annuler", use_container_width=True)
            
            if submitted:
                # Ajouter le nouveau revenu au CSV (montant POSITIF)
                nouvelle_ligne = {
                    'date': date_revenu.strftime('%d/%m/%y'),
                    'montant': montant_revenu,  # POSITIF pour revenu
                    'type de depense': type_revenu,
                    'utile (yes/no)': 'oui',  # Un revenu est toujours "utile"
                    'cash ou CB': mode_paiement_revenu
                }
                
                # Lire le CSV existant
                df_existant = pd.read_csv(chemin_fichier)
                # Ajouter la nouvelle ligne
                df_nouveau = pd.concat([df_existant, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
                # Sauvegarder
                df_nouveau.to_csv(chemin_fichier, index=False)
                
                st.success(f"✅ Revenu de {montant_revenu:.2f} € ajouté avec succès !")
                st.session_state.show_form_revenu = False
                st.rerun()
            
            if cancel:
                st.session_state.show_form_revenu = False
                st.rerun()
    
    st.write("---")
    
    try:
        # lecture du fichier CSV
        df = pd.read_csv(chemin_fichier)
        
        # Conversion de la colonne date en datetime (format jour/mois/année)
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%y')
        
        # Ajouter une colonne année-mois pour faciliter le filtrage
        df['annee_mois'] = df['date'].dt.strftime('%Y-%m')
        
        # ========================================
        # Navigation par mois
        # ========================================
        st.subheader("📋 Aperçu des données")
        
        # Créer 3 colonnes : flèche gauche, mois affiché, flèche droite
        col_gauche, col_centre, col_droite = st.columns([1, 3, 1])
        
        with col_gauche:
            st.button("◀️", key="btn_mois_prec", on_click=mois_precedent)
        
        with col_centre:
            # Convertir le mois sélectionné en format lisible
            date_affichage = datetime.strptime(st.session_state.mois_selectionne, '%Y-%m')
            mois_francais = {
                1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
                5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
                9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
            }
            mois_nom = mois_francais[date_affichage.month]
            st.markdown(f"<h3 style='text-align: center;'>{mois_nom} {date_affichage.year}</h3>", 
                       unsafe_allow_html=True)
        
        with col_droite:
            st.button("▶️", key="btn_mois_suiv", on_click=mois_suivant)
        
        # Filtrer les données pour le mois sélectionné
        df_mois = df[df['annee_mois'] == st.session_state.mois_selectionne].copy()
        
        # Afficher les données du mois AVEC NUMÉROTATION ET BOUTON SUPPRIMER
        if len(df_mois) > 0:
            # Trier par date
            df_mois = df_mois.sort_values('date').reset_index(drop=True)
            
            # Créer un conteneur avec hauteur fixe pour 8 lignes (scrollable)
            with st.container(height=400):
                # En-têtes des colonnes
                col_num, col_date, col_montant, col_type, col_utile, col_mode, col_del = st.columns([0.5, 1.5, 1, 2, 1, 1, 0.5])
                
                with col_num:
                    st.write("**N°**")
                with col_date:
                    st.write("**Date**")
                with col_montant:
                    st.write("**Montant**")
                with col_type:
                    st.write("**Type**")
                with col_utile:
                    st.write("**Utile**")
                with col_mode:
                    st.write("**Paiement**")
                with col_del:
                    st.write("")
                
                st.write("---")
                
                # Afficher chaque transaction
                for idx, row in df_mois.iterrows():
                    col_num, col_date, col_montant, col_type, col_utile, col_mode, col_del = st.columns([0.5, 1.5, 1, 2, 1, 1, 0.5])
                    
                    with col_num:
                        st.write(f"**{idx + 1}**")  # Numéro repart à 1 pour chaque mois
                    
                    with col_date:
                        st.write(row['date'].strftime('%d/%m/%Y'))
                    
                    with col_montant:
                        montant_affiche = abs(row['montant'])
                        couleur = "green" if row['montant'] > 0 else "red"
                        st.markdown(f"<span style='color:{couleur}'>{montant_affiche:.2f} €</span>", unsafe_allow_html=True)
                    
                    with col_type:
                        st.write(row['type de depense'])
                    
                    with col_utile:
                        st.write(row['utile (yes/no)'])
                    
                    with col_mode:
                        st.write(row['cash ou CB'])
                    
                    with col_del:
                        # Trouver l'index original dans le DataFrame complet
                        index_original = df[(df['date'] == row['date']) & 
                                           (df['montant'] == row['montant']) & 
                                           (df['type de depense'] == row['type de depense'])].index[0]
                        
                        if st.button("❌", key=f"del_{index_original}"):
                            st.session_state.transaction_a_supprimer = index_original
                            st.rerun()
            
            st.info(f"📊 {len(df_mois)} transaction(s) en {mois_nom} {date_affichage.year}")
        else:
            st.warning(f"Aucune transaction pour {mois_nom} {date_affichage.year}")
        
        # ========================================
        # CONFIRMATION DE SUPPRESSION
        # ========================================
        if st.session_state.transaction_a_supprimer is not None:
            idx_suppr = st.session_state.transaction_a_supprimer
            transaction = df.loc[idx_suppr]
            
            st.warning(f"⚠️ Voulez-vous vraiment supprimer cette transaction ?")
            st.write(f"**Date:** {transaction['date'].strftime('%d/%m/%Y')}")
            st.write(f"**Montant:** {abs(transaction['montant']):.2f} €")
            st.write(f"**Type:** {transaction['type de depense']}")
            
            col_conf, col_ann = st.columns(2)
            
            with col_conf:
                if st.button("✅ Confirmer la suppression", use_container_width=True):
                    # Supprimer la ligne
                    df_nouveau = df.drop(idx_suppr).reset_index(drop=True)
                    df_nouveau['date'] = df_nouveau['date'].dt.strftime('%d/%m/%y')
                    df_nouveau = df_nouveau[['date', 'montant', 'type de depense', 'utile (yes/no)', 'cash ou CB']]
                    df_nouveau.to_csv(chemin_fichier, index=False)
                    
                    st.success("✅ Transaction supprimée avec succès !")
                    st.session_state.transaction_a_supprimer = None
                    st.rerun()
            
            with col_ann:
                if st.button("❌ Annuler", use_container_width=True):
                    st.session_state.transaction_a_supprimer = None
                    st.rerun()
        
        # ========================================
        # STATISTIQUES (30 DERNIERS JOURS)
        # ========================================
        st.write("---")
        st.write("### 📈 Statistiques des 30 derniers jours")
        
        # Filtrer les 30 derniers jours
        date_limite = datetime.now() - timedelta(days=30)
        df_30j = df[df['date'] >= date_limite].copy()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nombre de transactions", len(df_30j))
        
        with col2:
            # Total dépensé (montants négatifs seulement)
            total_depenses = df_30j[df_30j['montant'] < 0]['montant'].sum()
            st.metric("Total dépensé", f"{abs(total_depenses):.2f} €")
        
        with col3:
            # Total revenus (montants positifs seulement)
            total_revenus = df_30j[df_30j['montant'] > 0]['montant'].sum()
            st.metric("Total revenus", f"{total_revenus:.2f} €")
        
        with col4:
            # Compter les dépenses NON utiles (non)
            nb_non_utiles = (df_30j['utile (yes/no)'].str.lower() == 'non').sum()
            st.metric("Dépenses non utiles", int(nb_non_utiles))


        # Répartition par type de dépense (seulement les dépenses négatives)
        st.subheader("🍕 Répartition par type de dépense")
        df_depenses_only = df_30j[df_30j['montant'] < 0].copy()
        df_depenses_only['montant_abs'] = df_depenses_only['montant'].abs()
        repartition = df_depenses_only.groupby('type de depense')['montant_abs'].sum().sort_values(ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Dépenses par catégorie")

            # Création d'un dictionnaire pour savoir si la catégorie est utile ou non
            couleurs = {}
            for categorie in repartition.index:
                df_cat = df_depenses_only[df_depenses_only['type de depense'] == categorie]
                # Si toutes les dépenses sont utiles, vert, sinon rouge
                if (df_cat['utile (yes/no)'].str.lower() == 'oui').all():
                    couleurs[categorie] = "green"
                else:
                    couleurs[categorie] = "red"

            # Zone scrollable 5 lignes environ
            list_container = st.container(height=200)

            with list_container:
                for categorie, montant in repartition.items():
                    couleur = couleurs.get(categorie, "black")
                    st.markdown(f"- {categorie}: <span style='color:{couleur}'>{montant:.2f} €</span>", unsafe_allow_html=True)


        with col2:
            st.write("### Dépenses utiles vs non utiles")

            # Calcul des totaux utiles / non utiles (seulement dépenses)
            df_utile = df_depenses_only['montant_abs'].groupby(df_depenses_only['utile (yes/no)'].str.lower()).sum()
            utile_values = [df_utile.get('oui', 0), df_utile.get('non', 0)]

            fig, ax = plt.subplots(figsize=(6, 6))
            ax.bar(['Utile', 'Non utile'], utile_values, color=['green', 'red'])
            ax.set_ylabel("Montant (€)")
            ax.set_title("Dépenses utiles vs non utiles")
            
            # Affichage des montants sur chaque barre
            for i, v in enumerate(utile_values):
                if v > 0:
                    ax.text(i, v + max(utile_values)*0.01, f"{v:.2f} €", ha='center', va='bottom')

            st.pyplot(fig)

        
        # Cash vs CB
        st.subheader("💳 Répartition par mode de paiement")
        
        # Séparer dépenses et revenus
        df_depenses_cb = df_30j[df_30j['montant'] < 0].copy()
        df_depenses_cb['montant_abs'] = df_depenses_cb['montant'].abs()
        cash_cb = df_depenses_cb.groupby('cash ou CB')['montant_abs'].sum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Montant par mode de paiement :**")
            for mode, montant in cash_cb.items():
                st.write(f"- {mode}: {montant:.2f} €")
        
        with col2:
            # Graphique en barres
            fig, ax = plt.subplots(figsize=(8, 6))
            if len(cash_cb) > 0:
                cash_cb.plot(kind='bar', ax=ax, color=['green', 'blue'])
                ax.set_title("CB vs Cash")
                ax.set_ylabel("Montant (€)")
                ax.set_xlabel("Mode de paiement")
                plt.xticks(rotation=0)
            st.pyplot(fig)
        
        
        # Évolution dans le temps
        st.subheader("📅 Évolution des dépenses — 30 derniers jours.")
        
        # Grouper par date (valeurs absolues pour dépenses)
        df_evolution = df_30j.copy()
        df_evolution['montant_abs'] = df_evolution['montant'].apply(lambda x: abs(x) if x < 0 else 0)
        evolution = df_evolution.groupby(df_evolution['date'].dt.date)['montant_abs'].sum().sort_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        if len(evolution) > 0:
            evolution.plot(kind='line', ax=ax, marker='o', color='steelblue')
            ax.set_title("Évolution des dépenses")
            ax.set_ylabel("Montant (€)")
            ax.set_xlabel("Date")
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        st.pyplot(fig)
        
        
        # Analyse des dépenses non utiles
        st.subheader("⚠️ Analyse des dépenses non utiles (30 derniers jours)")
        
        # Filtrer les lignes où utile = "non"
        df_non_utiles = df_30j[(df_30j['utile (yes/no)'].str.lower() == 'non') & (df_30j['montant'] < 0)].copy()
        df_non_utiles['montant_abs'] = df_non_utiles['montant'].abs()
        
        if len(df_non_utiles) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Nombre de dépenses non utiles :** {len(df_non_utiles)}")
                st.write(f"**Montant total non utile :** {df_non_utiles['montant_abs'].sum():.2f} €")
                total_depenses_30j = df_30j[df_30j['montant'] < 0]['montant'].abs().sum()
                if total_depenses_30j > 0:
                    st.write(f"**Pourcentage du total :** {(df_non_utiles['montant_abs'].sum() / total_depenses_30j * 100):.1f}%")
            
            with col2:
                st.write("**Liste des dépenses non utiles :**")
                df_non_utiles_display = df_non_utiles.copy()
                df_non_utiles_display['date'] = df_non_utiles_display['date'].dt.strftime('%d/%m/%Y')
                st.dataframe(df_non_utiles_display[['date', 'montant_abs', 'type de depense']].rename(columns={'montant_abs': 'montant'}))
        else:
            st.success("✅ Toutes vos dépenses sont utiles !")
        
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.write("Vérifiez que votre CSV contient bien les colonnes : date, montant, type de depense, utile (yes/no), cash ou CB")