import requests
import certifi
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ProductListGraphQLView(APIView):
    def get(self, request):
        SHOP_NAME = settings.SHOPIFY_DOMAIN
        ACCESS_TOKEN = settings.SHOPIFY_ADMIN_API_TOKEN
        API_VERSION = settings.SHOPIFY_API_VERSION  # Usa la versión de settings

        url = f"https://{SHOP_NAME}.myshopify.com/api/{API_VERSION}/graphql.json"
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": ACCESS_TOKEN  # Cambiado a Admin API Token
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
          }
        }
        """

        try:
            # Configura la sesión con certificados SSL
            session = requests.Session()
            session.verify = certifi.where()  # Usa los certificados de certifi
            
            response = session.post(url, json={"query": query}, headers=headers)
            
            if response.status_code != 200:
                return Response(
                    {"error": f"Shopify API error: {response.status_code}"},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            data = response.json()
            if 'errors' in data:
                return Response(
                    {"error": f"GraphQL error: {data['errors']}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            products = []
            for edge in data.get("data", {}).get("products", {}).get("edges", []):
                node = edge["node"]
                variants = node.get("variants", {}).get("edges", [])
                
                if variants:
                    variant = variants[0]["node"]
                    price_info = variant.get("price", {})
                    
                    products.append({
                        "id": node["id"],
                        "title": node["title"].replace("Modulo", "Reparación de módulo"),
                        "description": node.get("description") or "Reparación profesional de módulo de pantalla",
                        "imageUrl": node.get("featuredImage", {}).get("url", ""),
                        "price": float(price_info.get("amount", 0)),
                        "currency": price_info.get("currencyCode", "USD"),
                        "inStock": float(price_info.get("amount", 0)) > 0
                    })

            return Response(products)

        except Exception as e:
            print("Shopify fetch error:", str(e))
            return Response(
                {"error": "Error al conectar con Shopify"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )