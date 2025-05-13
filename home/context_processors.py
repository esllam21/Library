from .models import Members


def member_context(request):
    member = None
    member_id = request.session.get('userID')
    if member_id:
        try:
            member = Members.objects.get(id=member_id)
        except Members.DoesNotExist:
            pass
    return {'current_member': member}
