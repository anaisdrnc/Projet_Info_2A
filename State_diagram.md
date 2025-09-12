```mermaid
stateDiagram-v2
    [*] --> Connexion

    Connexion --> Accueil : identifiants corrects
    Connexion --> Connexion : Identifiants incorrects

    Accueil --> "Nouveau compte livreur"
    "Nouveau compte livreur" --> Accueil

    Accueil --> Menu

    Menu --> "Ajouter un menu"
    "Ajouter un menu" --> Menu

    Menu --> "Supprimer un menu"
    "Supprimer un menu" --> Menu

    Menu --> Deconnexion
    Deconnexion --> [*]

    "Ajouter un menu" --> Accueil : Retour à l’accueil
