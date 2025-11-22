from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from src.utils.log_decorator import log


class ProductService:
    """Class containing service methods for managing products."""

    def __init__(self, productdao: ProductDAO | None = None):
        """
        Initialize the ProductService with a DAO.

        Parameters
        ----------
        productdao : ProductDAO, optional
            The DAO to use for database operations. If None, a default ProductDAO is created.
        """
        self.productdao = productdao or ProductDAO(DBConnector())

    @log
    def create(self, name: str, price: float, production_cost: float, product_type: str, description: str,
        stock: int ) -> Product | None:
        """
        Create a new product and store it via the DAO.

        Parameters
        ----------
        name : str
            The product's name.
        price : float
            The selling price of the product.
        production_cost : float
            The cost to produce the product.
        product_type : str
            The type of the product (e.g., lunch, drink, dessert).
        description : str
            A short description of the product.
        stock : int
            Initial stock quantity.

        Returns
        -------
        Product or None
            The created Product object if successful, otherwise None.
        """
        new_product = Product(
            name=name,
            price=price,
            production_cost=production_cost,
            product_type=product_type,
            description=description,
            stock=stock,
        )

        return self.productdao.create_product(new_product)

    @log
    def delete(self, product_id: int) -> bool:
        """
        Delete a product by its ID.

        Parameters
        ----------
        product_id : int
            The ID of the product to delete.

        Returns
        -------
        bool
            True if deletion succeeded, False otherwise.
        """
        return self.productdao.deleting_product(product_id)

    @log
    def get_list_products_names(self) -> list[dict]:
        """
        Retrieve the list of all products' names and IDs.

        Returns
        -------
        list of dict
            Each dict contains 'id' and 'name' keys.
        """
        return self.productdao.get_all_product_names()

    @log
    def get_list_products_descriptions(self) -> list[dict]:
        """
        Retrieve the list of products' names and descriptions.

        Returns
        -------
        list of dict
            Each dict contains 'name' and 'description' keys.
        """
        return self.productdao.get_all_product_names_descriptions()

    @log
    def get_available_products(self) -> list[dict]:
        """
        Retrieve products with stock greater than zero.

        Returns
        -------
        list of dict
            Each dict contains product details.
        """
        return self.productdao.get_available_products()

    @log
    def decrement_stock(self, product_id: int, quantity: int = 1) -> bool:
        """
        Decrease the stock of a product.

        Parameters
        ----------
        product_id : int
            ID of the product.
        quantity : int, optional
            Amount to decrement (default is 1).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        return self.productdao.decrement_stock(product_id, quantity)

    @log
    def increment_stock(self, product_id: int, quantity: int = 1) -> bool:
        """
        Increase the stock of a product (e.g., after order cancellation).

        Parameters
        ----------
        product_id : int
            ID of the product.
        quantity : int, optional
            Amount to increment (default is 1).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        return self.productdao.increment_stock(product_id, quantity)

    @log
    def get_id_by_name(self, product_name: str) -> int:
        """
        Get a product's ID using its name.

        Parameters
        ----------
        product_name : str
            The name of the product.

        Returns
        -------
        int
            The corresponding product ID.
        """
        return self.productdao.get_id_by_productname(product_name)

    @log
    def update_product(self, product_id: int, name: str, price: float, production_cost: float,
                       product_type: str, description: str, stock: int) -> Product | None:
        """
        Update an existing product.

        Parameters
        ----------
        product_id : int
            ID of the product to update.
        name : str
            Updated name.
        price : float
            Updated selling price.
        production_cost : float
            Updated production cost.
        product_type : str
            Updated type of product.
        description : str
            Updated description.
        stock : int
            Updated stock quantity.

        Returns
        -------
        Product or None
            Updated Product object if successful, else None.
        """
        updated_product = Product(
            id_product=product_id,
            name=name,
            price=price,
            production_cost=production_cost,
            product_type=product_type,
            description=description,
            stock=stock,
        )

        return self.productdao.update_product(product_id, updated_product)

