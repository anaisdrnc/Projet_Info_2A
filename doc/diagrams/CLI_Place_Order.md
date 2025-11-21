```mermaid
---
config:
  theme: forest
  look: classic
  layout: elk
---
flowchart TB
    A("Place order view") --> B{"Choose :"}
    B -- Get product --> C{"Select product"}
    C --> D["Enter quantity"]
    B -- Get menu for 10% discount --> E{"Select lunch, drink and dessert"}
    E --> H{"Choose :"}
    D --> H
    H -- Add product --> I{"Select product"}
    I --> J["Enter quantity"]
    J --> H
    H -- Add a menu --> K{"Select lunch, drink and dessert"}
    K --> H
    H -- Finish order --> N["Enter address, city, postal code"]
    N -- Check if the address exists : if not --> P("Menu Customer View")
    N --> O{"Select payment method"}
    O -- Gives a summary of the order with each items, the menus, address to be delivered and amount to pay --> P
    style A fill:#C8E6C9
    style P fill:#C8E6C9
