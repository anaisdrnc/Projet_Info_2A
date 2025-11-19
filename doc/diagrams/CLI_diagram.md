---
config:
  theme: forest
  layout: elk
  look: classic
---
flowchart TB
    A["CLI"] --> B("Opening view")
    B --> C{"Choose"}
    C -- Create a customer account --> D("Inscription view")
    C -- Login --> E("Login view")
    C -- Exit --> F("Close the CLI")
    D --> G["Enter username, password, firstname, lastname, email"]
    G --> L{"Case :"}
    L -- username or email already used : error --> C
    L -- success : the account is created --> C
    E --> H["Enter username, password"]
    H --> I{"Case :"}
    I -- User doesnt exist : error --> C
    I -- User is a customer --> J("Menu Customer view")
    I -- User is a driver --> K("Menu Driver view")
    style B fill:#C8E6C9
    style D fill:#C8E6C9
    style E fill:#C8E6C9
    style J fill:#C8E6C9
    style K fill:#C8E6C9
