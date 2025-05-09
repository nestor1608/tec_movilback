import requests
import certifi
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ProductListGraphQLView(APIView):
    def get(self, request):
        # Configuración para Storefront API
        SHOP_NAME = settings.SHOPIFY_DOMAIN
        STOREFRONT_TOKEN = settings.SHOPIFY_ADMIN_API_TOKEN
        API_VERSION = settings.SHOPIFY_API_VERSION
        
        # URL correcta para Storefront API
        url = f"https://{SHOP_NAME}.myshopify.com/api/{API_VERSION}/graphql.json"
        
        # Headers específicos para Storefront API
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Storefront-Access-Token": STOREFRONT_TOKEN,  # Header correcto para Storefront
            "Accept": "application/json"
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
                }
                variants(first: 1) {
                  edges {
                    node {
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
            # Configuración de sesión segura
            session = requests.Session()
            session.verify = certifi.where()
            
            response = session.post(
                url,
                json={'query': query},
                headers=headers,
                timeout=10
            )
            
            # Verificación de respuesta
            if response.status_code != 200:
                return Response(
                    {"error": f"API returned {response.status_code}"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            json_response = response.json()
            
            # Manejo de errores GraphQL
            if 'errors' in json_response:
                return Response(
                    {"error": json_response['errors']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Procesamiento de datos seguro
            products = []
            for edge in json_response.get('data', {}).get('products', {}).get('edges', []):
                node = edge.get('node', {})
                variant = node.get('variants', {}).get('edges', [{}])[0].get('node', {})
                price = variant.get('price', {})
                
                products.append({
                    "id": node.get('id'),
                    "title": node.get('title', '').replace("Modulo", "Reparación de módulo"),
                    "description": node.get('description') or "Reparación profesional",
                    "imageUrl": node.get('featuredImage', {}).get('url', ''),
                    "price": float(price.get('amount', 0)),
                    "currency": price.get('currencyCode', 'USD'),
                    "inStock": True  # Storefront API no indica stock directamente
                })
            
            return Response(products)
            
        except requests.exceptions.SSLError as e:
            return Response(
                {"error": "SSL verification failed"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )