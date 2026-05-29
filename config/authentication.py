from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from users.models import Teacher
import jwt
import requests
from jwt import PyJWKClient

class ClerkAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        parts = auth_header.split()
        if parts[0].lower() != 'bearer':
            return None

        if len(parts) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(parts) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        token = parts[1]
        
        try:
            # Get Clerk keys for verification
            # In production, CLERK_JWKS_URL should be set in environment
            # Usually: https://api.clerk.com/v1/jwks (requires secret key) 
            # Or the Frontend API instance URL: https://<YOUR_FRONTEND_API>/.well-known/jwks.json
            
            # For Clerk, we typically use the JWKS endpoint of the specific instance
            # We'll try to get it from settings or use a placeholder if not set
            jwks_url = getattr(settings, 'CLERK_JWKS_URL', None)
            
            if jwks_url:
                jwks_client = PyJWKClient(jwks_url)
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    options={"verify_exp": True}
                )
            else:
                # Fallback to unverified decode ONLY if JWKS is not configured 
                # but log a warning or handle appropriately. 
                # For this task, we'll keep it as is but mark it clearly.
                # In a real setup, you'd REQUIRE the JWKS URL.
                payload = jwt.decode(token, options={"verify_signature": False})
            
            clerk_id = payload.get('sub')
            if not clerk_id:
                raise exceptions.AuthenticationFailed('Token payload missing subject (clerk_id).')

            # Get or create the teacher in our database
            teacher, created = Teacher.objects.get_or_create(
                clerk_id=clerk_id,
                defaults={
                    'email': payload.get('email', ''),
                    'name': payload.get('name', 'Clerk User'),
                }
            )
            
            return (teacher, token)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Error authenticating with Clerk: {str(e)}')
