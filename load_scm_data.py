import random
import uuid
from datetime import datetime, timedelta
from neo4j import GraphDatabase, basic_auth
import streamlit as st
from langchain_community.graphs import Neo4jGraph

graph = Neo4jGraph(
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    database="supplychaindb"
)


def random_date(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# Sample data for more realistic examples
brands = ["Nike", "Adidas", "Apple", "Samsung", "Sony", "Toyota", "Honda", "Puma", "Dell", "HP"]
categories = ["Electronics", "Clothing", "Automotive", "Footwear", "Home Appliances", "Sports Equipment"]
products = [
    "iPhone 13", "Galaxy S21", "PlayStation 5", "MacBook Pro", "Nike Air Max", "Adidas Ultraboost",
    "Toyota Corolla", "Honda Civic", "Dell XPS 13", "HP Spectre x360"
]
first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hannah"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Martinez", "Lee"]
cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
countries = ["USA", "Canada", "UK", "Germany", "France", "Australia", "Japan", "South Korea", "China", "India"]

def create_brands(count=500):
    for i in range(count):
        brand_name = random.choice(brands)
        query = f"""
        CREATE (:Brand {{
            id: {i},
            title: '{brand_name}',
            summary: 'Summary for {brand_name}',
            createdAt: '{random_date(datetime(2021, 1, 1), datetime(2023, 1, 1))}',
            updatedAt: '{random_date(datetime(2023, 1, 2), datetime(2024, 1, 1))}',
            content: 'Content about {brand_name}'
        }})
        """
        execute_query(query)

def create_categories(count=500):
    for i in range(count):
        category_name = random.choice(categories)
        query = f"""
        CREATE (:Category {{
            id: {i},
            title: '{category_name}',
            parentId: {random.randint(0, 499)},
            metaTitle: 'Meta Title for {category_name}',
            slug: '{category_name.lower().replace(" ", "-")}',
            content: 'Content about {category_name}'
        }})
        """
        execute_query(query)

def create_products(count=500):
    for i in range(count):
        product_name = random.choice(products)
        query = f"""
        CREATE (:Product {{
            id: {i},
            title: '{product_name}',
            summary: 'Summary for {product_name}',
            type: {random.randint(1, 3)},
            createdAt: '{random_date(datetime(2021, 1, 1), datetime(2023, 1, 1))}',
            updatedAt: '{random_date(datetime(2023, 1, 2), datetime(2024, 1, 1))}',
            content: 'Content about {product_name}'
        }})
        """
        execute_query(query)

def create_users(count=500):
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        query = f"""
        CREATE (:User {{
            id: {i},
            firstName: '{first_name}',
            lastName: '{last_name}',
            username: '{first_name.lower()}.{last_name.lower()}',
            email: '{first_name.lower()}.{last_name.lower()}@example.com',
            mobile: '555-{i:04}',
            registeredAt: '{random_date(datetime(2021, 1, 1), datetime(2022, 1, 1))}',
            lastLogin: '{random_date(datetime(2022, 1, 2), datetime(2024, 1, 1))}'
        }})
        """
        execute_query(query)

def create_orders(count=500):
    for i in range(count):
        status = random.choice(['Pending', 'In Progress', 'Delivered'])
        query = f"""
        CREATE (:Order {{
            id: {i},
            userId: {random.randint(0, 499)},
            type: {random.randint(1, 3)},
            status: '{status}',
            subTotal: {random.uniform(50, 500)},
            discount: {random.uniform(0, 50)},
            grandTotal: {random.uniform(50, 500)},
            createdAt: '{random_date(datetime(2021, 1, 1), datetime(2023, 1, 1))}',
            updatedAt: '{random_date(datetime(2023, 1, 2), datetime(2024, 1, 1))}'
        }})
        """
        execute_query(query)

def create_items(count=500):
    for i in range(count):
        product_name = random.choice(products)
        brand_name = random.choice(brands)
        query = f"""
        CREATE (:Item {{
            id: {i},
            productId: {random.randint(0, 499)},
            brandId: {random.randint(0, 499)},
            sku: '{brand_name[:3].upper()}-{product_name[:3].upper()}-{i:04}',
            price: {random.uniform(5, 100)},
            quantity: {random.randint(1, 100)},
            available: {random.randint(1, 100)},
            createdAt: '{random_date(datetime(2021, 1, 1), datetime(2023, 1, 1))}',
            updatedAt: '{random_date(datetime(2023, 1, 2), datetime(2024, 1, 1))}'
        }})
        """
        execute_query(query)

def create_transactions(count=500):
    for i in range(count):
        query = f"""
        CREATE (:Transaction {{
            id: {i},
            userId: {random.randint(0, 499)},
            orderId: {random.randint(0, 499)},
            type: {random.randint(1, 3)},
            amount: {random.uniform(50, 500)},
            createdAt: '{random_date(datetime(2021, 1, 1), datetime(2023, 1, 1))}',
            updatedAt: '{random_date(datetime(2023, 1, 2), datetime(2024, 1, 1))}'
        }})
        """
        execute_query(query)

def create_addresses(count=500):
    for i in range(count):
        city = random.choice(cities)
        country = random.choice(countries)
        query = f"""
        CREATE (:Address {{
            id: {i},
            userId: {random.randint(0, 499)},
            line1: 'Address Line 1 - {i}',
            line2: 'Address Line 2 - {i}',
            city: '{city}',
            province: '{city} Province',
            country: '{country}',
            createdAt: '{random_date(datetime(2021, 1, 1), datetime(2023, 1, 1))}',
            updatedAt: '{random_date(datetime(2023, 1, 2), datetime(2024, 1, 1))}'
        }})
        """
        execute_query(query)

def create_relationships(count=500):
    for i in range(count):
        # Relationship between Order and Item
        query = f"""
        MATCH (o:Order {{id: {random.randint(0, 499)}}}), (i:Item {{id: {random.randint(0, 499)}}})
        CREATE (o)-[:CONTAINS]->(i)
        """
        execute_query(query)

        # Relationship between Product and Item
        query = f"""
        MATCH (p:Product {{id: {random.randint(0, 499)}}}), (i:Item {{id: {random.randint(0, 499)}}})
        CREATE (p)-[:INCLUDES]->(i)
        """
        execute_query(query)

        # Relationship between User and Order
        query = f"""
        MATCH (u:User {{id: {random.randint(0, 499)}}}), (o:Order {{id: {random.randint(0, 499)}}})
        CREATE (u)-[:PLACED]->(o)
        """
        execute_query(query)

        # Relationship between Transaction and User
        query = f"""
        MATCH (t:Transaction {{id: {random.randint(0, 499)}}}), (u:User {{id: {random.randint(0, 499)}}})
        CREATE (u)-[:MADE]->(t)
        """
        execute_query(query)

        # Relationship between Transaction and Order
        query = f"""
        MATCH (t:Transaction {{id: {random.randint(0, 499)}}}), (o:Order {{id: {random.randint(0, 499)}}})
        CREATE (t)-[:FOR]->(o)
        """
        execute_query(query)

        # Relationship between Product and Category
        query = f"""
        MATCH (p:Product {{id: {random.randint(0, 499)}}}), (c:Category {{id: {random.randint(0, 499)}}})
        CREATE (p)-[:BELONGS_TO]->(c)
        """
        execute_query(query)

        # Relationship between Product and Brand
        query = f"""
        MATCH (p:Product {{id: {random.randint(0, 499)}}}), (b:Brand {{id: {random.randint(0, 499)}}})
        CREATE (p)-[:MADE_BY]->(b)
        """
        execute_query(query)

        # Relationship between User and Address
        query = f"""
        MATCH (u:User {{id: {random.randint(0, 499)}}}), (a:Address {{id: {random.randint(0, 499)}}})
        CREATE (u)-[:LIVES_AT]->(a)
        """
        execute_query(query)

        # Relationship between Order and Address (shipping address)
        query = f"""
        MATCH (o:Order {{id: {random.randint(0, 499)}}}), (a:Address {{id: {random.randint(0, 499)}}})
        CREATE (o)-[:SHIPPED_TO]->(a)
        """
        execute_query(query)

def execute_query(query):
    graph.query(query)

def main():
    # Create nodes
    create_brands()
    create_categories()
    create_products()
    create_users()
    create_orders()
    create_items()
    create_transactions()
    create_addresses()

    # Create relationships
    create_relationships()

if __name__ == "__main__":
    main()
