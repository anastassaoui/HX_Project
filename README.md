# 🔥 Suite de Conception d'Échangeur de Chaleur

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)](https://streamlit.io)
[![Heat Transfer](https://img.shields.io/badge/Library-ht-green)](https://github.com/CalebBell/ht)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange)](https://xgboost.readthedocs.io)

> **Application Streamlit pour la conception d'échangeurs tubulaires à calandre avec calculs géométriques, analyse thermique et prédiction d'encrassement par machine learning.**

## 🎯 Vue d'ensemble

Application web Streamlit dédiée à la conception et l'analyse d'échangeurs de chaleur tubulaires à calandre. L'interface en français propose 5 modules principaux pour calculer la géométrie, analyser les clearances, évaluer l'efficacité thermique, prédire l'encrassement et générer des rapports PDF.

### 🏭 Fonctionnalités principales
- **Calculs géométriques** avec corrélations Perry's, HEDH, Phadkeb, VDI
- **Analyse clearances** calandre-faisceau selon standards TEMA
- **Efficacité thermique** avec méthodes ε-NTU pour configurations TEMA
- **Prédiction ML** d'encrassement avec modèles XGBoost pré-entraînés
- **Rapports PDF** professionnels avec tous les résultats

## 🧪 Modules de l'application

### 1. 📐 Géométrie
**Calculs de dimensionnement de faisceau tubulaire**

Utilise la bibliothèque `ht` pour calculer les diamètres de faisceau selon différentes corrélations:

```python
from ht.hx import (
    size_bundle_from_tubecount,    # Perry's method
    DBundle_for_Ntubes_HEDH,       # HEDH correlation
    DBundle_for_Ntubes_Phadkeb,    # Phadkeb method
    D_for_Ntubes_VDI,              # VDI standards
    shell_clearance,               # TEMA clearances
    D_baffle_holes,                # Baffle hole diameter
    L_unsupported_max              # Max unsupported length
)
```

**Paramètres d'entrée:**
- Ø extérieur tubes: 5-100 mm
- Pas triangulaire: 10-100 mm
- Angle disposition: 30°, 45°, 60°, 90°
- Nombre de tubes: 1-2000
- Passes tubes: 1 ou 2
- Matériau: CS ou aluminium
- Longueur non supportée: 0.1-10 m

**Résultats calculés:**
- Diamètres faisceau (Perry's, HEDH, Phadkeb, VDI)
- Clearance automatique
- Diamètre trous chicanes
- Longueur max sans support

### 2. 🔧 Jeu Calandre
**Calcul clearance calandre-faisceau**

Module simple utilisant `shell_clearance()` de la bibliothèque `ht`:

```python
from ht.hx import shell_clearance

# Calcul basé sur diamètre faisceau
clearance = shell_clearance(DBundle=diameter_bundle)
# ou basé sur diamètre calandre
clearance = shell_clearance(DShell=diameter_shell)
```

**Interface:**
- Choix: "Diamètre faisceau" ou "Diamètre calandre"
- Slider: 0.1 à 3.0 m
- Résultat: Jeu recommandé en mètres

### 3. ⚡ Efficacité
**Calculs d'efficacité thermique avec méthodes ε-NTU**

8 onglets avec différentes méthodes de calcul:

```python
from ht.hx import (
    temperature_effectiveness_basic,      # Basique
    temperature_effectiveness_TEMA_E,     # TEMA E
    temperature_effectiveness_TEMA_G,     # TEMA G  
    temperature_effectiveness_TEMA_H,     # TEMA H
    temperature_effectiveness_TEMA_J,     # TEMA J
    temperature_effectiveness_air_cooler, # Air Cooler
    temperature_effectiveness_plate,      # Plaques
    P_NTU_method                         # Solveur P-NTU
)
```

**Solveur P-NTU (onglet principal):**
- Débits massiques m1, m2 [kg/s]
- Capacités thermiques Cp1, Cp2 [J/kg.K]
- Températures entrée T1, T2 [°C]
- UA [W/K]
- Configuration: E, G, H, J, crossflow
- Nombre passes tubes: 1 ou 2

**Autres onglets:** Calculs ε-NTU avec paramètres R1, NTU1, passes tubes

### 4. 🤖 Prédiction ML
**Prédiction d'encrassement avec XGBoost**

Charge deux modèles pré-entraînés avec `joblib`:
- `model_fouling.pkl`: Niveau d'encrassement
- `model_ttc.pkl`: Heures avant nettoyage

**11 paramètres d'entrée:**
1. Heures depuis dernier nettoyage (0 à 7 ans)
2. ΔT côté chaud (0-40°C)
3. ΔT côté froid (0-40°C)  
4. ΔP calandre (0-150 kPa)
5. T entrée chaud (80-180°C)
6. T entrée froid (5-70°C)
7. Débit chaud (5-30 kg/s)
8. Débit froid (5-30 kg/s)
9. Viscosité chaud (0.1-10 cP)
10. Viscosité froid (0.1-10 cP)
11. Solides suspension (0-300 ppm)

**Résultats:**
- Niveau encrassement (0-1)
- Heures avant nettoyage
- Status: OK / Attention / Critique

### 5. 📊 Résumé
**Tableau récapitulatif et export PDF**

Module de synthèse qui:
- Affiche tableau avec tous les paramètres et résultats
- Génère rapport PDF avec `reportlab`
- Inclut sections: Géométrie, Clearance, Efficacité, ML
- Bouton téléchargement: "📄 Télécharger le PDF du Résumé"

Nécessite d'avoir exécuté les calculs géométrie et efficacité (P-NTU).

## 🛠️ Stack technique

### Dépendances principales
```
streamlit>=1.32.0              # Interface web
numpy>=1.26.0                  # Calculs numériques  
pandas>=2.2.0                  # DataFrames
ht                             # Corrélations transfert thermique
xgboost                        # Machine learning
joblib>=1.3.2                 # Chargement modèles ML
plotly                         # Graphiques interactifs
reportlab>=4.1.0              # Génération PDF
streamlit-option-menu>=0.3.12  # Menu navigation
matplotlib>=3.7.0              # Graphiques
pillow                         # Images
python-dotenv>=1.0.0          # Variables environnement
gunicorn                       # Déploiement
```

### Structure du projet
```
HX_Project/
├── app.py                     # App Streamlit principale
├── ui/                        # Modules interface
│   ├── geometry.py           # Module géométrie
│   ├── clearance.py          # Module clearance
│   ├── effectiveness.py      # Module efficacité
│   ├── ml.py                 # Module ML
│   └── summary.py            # Module résumé
├── utils/                     # Utilitaires
│   ├── helpers.py            # Fonctions helper
│   ├── pdf_report.py         # Génération PDF
│   └── session.py            # État session
├── model_fouling.pkl         # Modèle XGBoost encrassement
├── model_ttc.pkl             # Modèle XGBoost TTC
├── logo.png                  # Logo application
└── .streamlit/config.toml    # Config thème
```

## 🚀 Installation et utilisation

```bash
# Installation
git clone https://github.com/your-repo/HX_Project.git
cd HX_Project
pip install -r requirements.txt

# Lancement
streamlit run app.py
```

Accès: `http://localhost:8501`

### Interface
- **Menu latéral**: Navigation entre les 5 modules
- **Bouton "🚀 Calculer tout"**: Exécute tous les calculs
- **Interface française**: Textes et aide en français
- **Thème personnalisé**: Dégradés et couleurs modernes
- **Responsive**: Adaptatif mobile/desktop

### Workflow typique
1. **Géométrie**: Saisir paramètres tubes → Calculer diamètres faisceau
2. **Clearance**: Choisir base calcul → Obtenir jeu recommandé  
3. **Efficacité**: Paramètres thermiques → Calculs ε-NTU ou P-NTU
4. **ML**: Conditions opération → Prédiction encrassement
5. **Résumé**: Visualiser tableau → Télécharger PDF

## 📚 Références techniques

### Bibliothèque `ht`
- **Perry's Chemical Engineers' Handbook**: Corrélations de référence
- **HEDH**: Heat Exchanger Design Handbook  
- **TEMA**: Standards industriels échangeurs
- **VDI Heat Atlas**: Méthodes allemandes

### Machine Learning
- **XGBoost**: Modèles gradient boosting pré-entraînés
- **11 features**: Paramètres opérationnels et performance
- **Joblib**: Chargement rapide des modèles

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

---

**Version 1.0.0** | **© 2025 HX_Project** | *Made with Streamlit*