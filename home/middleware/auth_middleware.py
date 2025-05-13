from django.shortcuts import redirect


from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [
            '/home/homePage', 
            '/home/login/', 
            '/home/signup/', 
            '/admin/', 
            '/static/', 
            '/media/'  # Allow access to media files without login
        ]

        if not request.session.get('is_logged_in'):
            if not any(request.path.startswith(path) for path in allowed_paths):
                return redirect('/home/login/')

        response = self.get_response(request)
        return response
