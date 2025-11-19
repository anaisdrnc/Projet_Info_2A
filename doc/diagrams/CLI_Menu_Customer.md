---
config:
  theme: forest
  look: classic
  layout: elk
---
flowchart BT
    A("Menu Customer View") --> B{"Choose :"}
    B -- Get menu --> C("Products view")
    B -- Place an order --> D("Place Order View")
    B -- Change password --> F("Change profil view")
    B -- Get orders history --> E("Orders history view")
    B -- Logout --> G("Opening view")
    C -- Gives all products with prices and ingredients --> A
    F --> H["Enter username, current password and new password"]
    H -- wrong password entry : error --> A
    H -- success : password changed --> A
    E --> I{"Select the orders date"}
    I -- Gives a summary of all orders placed by the customer on the choosen date --> A
    style A fill:#C8E6C9
    style C fill:#C8E6C9
    style D fill:#C8E6C9
    style F fill:#C8E6C9
    style E fill:#C8E6C9
    style G fill:#C8E6C9
