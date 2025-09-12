# State Diagram for Authentication System

## Flow Description
This state diagram illustrates the authentication and menu management flow of an application.

## Mermaid Diagram Code

```mermaid
stateDiagram-v2
    [*] --> Connexion

    state Connexion {
        [*] --> SaisieIdentifiants
        SaisieIdentifiants --> Validation
        Validation --> Accueil : Identifiants corrects
        Validation --> SaisieIdentifiants : Identifiants incorrects
    }

    Accueil --> "Nouveau compte livreur"
    "Nouveau compte livreur" --> Accueil : Compte créé

    Accueil --> Menu

    state Menu {
        [*] --> GestionMenu
        GestionMenu --> "Ajouter un menu"
        "Ajouter un menu" --> GestionMenu : Menu ajouté
        GestionMenu --> "Supprimer un menu"
        "Supprimer un menu" --> GestionMenu : Menu supprimé
    }

    Menu --> Deconnexion
    Deconnexion --> [*] : Déconnexion réussie

    "Ajouter un menu" --> Accueil : Retour à l'accueil
    "Supprimer un menu" --> Accueil : Retour à l'accueil