from django.shortcuts import redirect


class AdminOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_urls = [
            'home/adminDashboard/',
            'home/addBooks/',
        ]

        user_type = request.session.get('userType')
        if request.path in admin_urls and user_type != 'Admin':
            return redirect('/unauthorized/')
        return self.get_response(request)
