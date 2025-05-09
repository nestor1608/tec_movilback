import requests
import certifi
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

class ProductListGraphQLView(APIView):
    def get(self, request):
        SHOP_NAME = settings.SHOPIFY_DOMAIN
        ACCESS_TOKEN = settings.SHOPIFY_ADMIN_API_TOKEN
        API_VERSION = settings.SHOPIFY_API_VERSION  # Usa la versión de settings

        url = f"https://{SHOP_NAME}.myshopify.com/api/{API_VERSION}/graphql.json"
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": ACCESS_TOKEN
        }
        

        query = """
        {
          products(first: 100) {
            edges {
              node {
                id
                title
                description
                featuredImage {
                  url
                  altText
                }
                variants(first: 10) {
                  edges {
                    node {
                      id
                      title
                      price {
                        amount
                        currencyCode
                      }
                    }
                  }
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """
            # Configura la ruta del certificado CA
        session = requests.Session()
        session.verify = certifi.where()

        try:
            response = session.post(url, json={"query": query}, headers=headers)
            data = response.json().get("data", {}).get("products", {}).get("edges", [])

            products = []
            for edge in data:
                node = edge["node"]
                variant = node["variants"]["edges"][0]["node"]

                products.append({
                    "id": node["id"],
                    "title": node["title"].replace("Modulo", "Reparación de módulo"),
                    "description": node["description"] or "Reparación profesional de módulo de pantalla",
                    "imageUrl": node.get("featuredImage", {}).get("url", ""),
                    "price": float(variant["price"]["amount"]),
                    "currency": variant["price"]["currencyCode"],
                    "inStock": float(variant["price"]["amount"]) > 0
                })

            return Response(products)

        except Exception as e:
            print("Shopify fetch error:", e)
            return Response({"error": "Error fetching products"}, status=500)
