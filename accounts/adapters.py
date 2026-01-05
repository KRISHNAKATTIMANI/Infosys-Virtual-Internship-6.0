# accounts/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social provider data.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Ensure username is set
        if not user.username:
            # Generate username from email or use provider's user ID
            if user.email:
                base_username = user.email.split('@')[0]
            else:
                base_username = f"{sociallogin.account.provider}_{sociallogin.account.uid}"
            
            # Make sure username is unique
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
        
        # Set full name from Google
        if not user.full_name:
            first_name = data.get('given_name', '')
            last_name = data.get('family_name', '')
            user.full_name = f"{first_name} {last_name}".strip()
            if not user.full_name:
                user.full_name = data.get('name', '')
        
        return user
